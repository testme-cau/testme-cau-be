"""
GPT Service for exam generation and grading
Uses OpenAI API v1.x+ (new client-based structure)
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.services.ai_service_interface import AIServiceInterface

from config import settings


class GPTService(AIServiceInterface):
    """
    Service class for GPT interactions with model fallback.
    Primary model is driven by OPENAI_MODEL (default: gpt-5), with fallbacks.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Initialize OpenAI client (async)
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Model configuration with fallback chain
        # TODO: Change back to gpt-5 when it's supported in Assistants API
        env_model = model or os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.model_candidates: List[str] = [
            env_model,
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo',
        ]
        self.active_model: Optional[str] = None
        self.logger = logging.getLogger(__name__)
        
        # JSON Schema for structured exam generation
        self.exam_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Brief descriptive title summarizing main topics covered (max 50 chars)"
                },
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "question": {"type": "string"},
                            "type": {"type": "string", "enum": ["multiple_choice", "short_answer", "essay"]},
                            "options": {"type": ["array", "null"], "items": {"type": "string"}},
                            "points": {"type": "integer"},
                            "topic": {"type": "string"},
                            "correct_answer": {"type": ["string", "null"]},
                            "model_answer": {"type": "string"},
                            "keywords": {"type": ["array", "null"], "items": {"type": "string"}},
                            "scoring_rubric": {
                                "type": ["array", "null"],
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "criterion": {"type": "string"},
                                        "points": {"type": "number"},
                                        "example": {"type": ["string", "null"]}
                                    },
                                    "required": ["criterion", "points"]
                                }
                            }
                        },
                        "required": ["id", "question", "type", "points", "model_answer"]
                    }
                },
                "total_points": {"type": "integer"},
                "estimated_time": {"type": "integer"}
            },
            "required": ["title", "questions", "total_points", "estimated_time"]
        }

    @property
    def model(self) -> str:
        """Expose a model name for diagnostics (first candidate until resolved)."""
        return self.active_model or self.model_candidates[0]
    
    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "gpt"

    # ---------- internal logging helpers ----------
    def _log_warn(self, message: str) -> None:
        self.logger.warning(message)

    def _log_error(self, message: str) -> None:
        self.logger.error(message)
    
    def _remove_citations(self, data: Any) -> Any:
        """
        Remove citation markers like [4:0†source] from all text fields in the data structure.
        """
        import re
        
        # Pattern to match citation markers: [number:number†source]
        citation_pattern = r'\[\d+:\d+†source\]'
        
        def clean_text(text: str) -> str:
            if isinstance(text, str):
                return re.sub(citation_pattern, '', text).strip()
            return text
        
        if isinstance(data, dict):
            return {key: self._remove_citations(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._remove_citations(item) for item in data]
        elif isinstance(data, str):
            return clean_text(data)
        else:
            return data

    # ---------- internal chat helper ----------
    async def _create_chat_completion(self, *, model: str, messages, temperature: float, max_tokens: int, response_format):
        """
        Create a chat completion. Handle gpt-5 parameter compatibility:
        - Prefer max_tokens (per latest sample)
        - If model rejects max_tokens, retry with max_completion_tokens
        - If model rejects temperature, retry without temperature
        - For gpt-5, avoid response_format unless required by prompt
        """
        # Base kwargs
        kwargs: Dict[str, Any] = {
            'model': model,
            'messages': messages,
        }

        # gpt-5 specific: avoid response_format by default
        is_gpt5 = 'gpt-5' in model
        if not is_gpt5 and response_format is not None:
            kwargs['response_format'] = response_format

        # tokens & temperature handling
        kwargs['max_tokens'] = max_tokens
        if temperature is not None:
            kwargs['temperature'] = temperature

        # Try 1: as-is
        try:
            return await self.client.chat.completions.create(**kwargs)
        except Exception as e:
            msg = str(e)
            # Retry: if max_tokens unsupported → switch to max_completion_tokens
            if "Unsupported parameter: 'max_tokens'" in msg:
                self._log_warn(f"Model '{model}' rejected max_tokens; retrying with max_completion_tokens")
                kwargs.pop('max_tokens', None)
                kwargs['max_completion_tokens'] = max_tokens
                try:
                    return await self.client.chat.completions.create(**kwargs)
                except Exception as e2:
                    msg2 = str(e2)
                    # If temperature unsupported → drop it and retry
                    if "Unsupported value: 'temperature'" in msg2:
                        self._log_warn(f"Model '{model}' rejected temperature; retrying without temperature")
                        kwargs.pop('temperature', None)
                        return await self.client.chat.completions.create(**kwargs)
                    raise
            # Retry: temperature unsupported → drop it and retry
            if "Unsupported value: 'temperature'" in msg:
                self._log_warn(f"Model '{model}' rejected temperature; retrying without temperature")
                kwargs.pop('temperature', None)
                return await self.client.chat.completions.create(**kwargs)
            raise

    # ---------- internal chat helper with fallback ----------
    async def _chat_with_fallback(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        response_format: Optional[Dict[str, Any]] = None,
    ):
        last_error = None
        for model in self.model_candidates:
            try:
                resp = await self._create_chat_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
                self.active_model = model  # cache success
                return resp
            except Exception as e:
                last_error = e
                self._log_warn(f"GPT model '{model}' failed, trying next fallback. Error: {e}")
                continue
        # All candidates failed
        raise last_error  # type: ignore[misc]

    # ---------- public methods ----------
    async def generate_exam_from_pdf(self, pdf_bytes: bytes, original_filename: str, num_questions: int = 10, difficulty: str = "medium", language: str = "ko", previous_context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate exam from PDF file using OpenAI File API.
        
        Args:
            pdf_bytes: PDF file content as bytes
            original_filename: Original filename (for OpenAI file upload)
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            language: Language code (ISO 639-1: ko, en, ja, zh, etc.)
        
        Returns:
            Dict with success status and exam data
        """
        try:
            # Upload PDF to OpenAI
            import io
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_file.name = original_filename
            
            file_response = await self.client.files.create(
                file=pdf_file,
                purpose='assistants'
            )
            file_id = file_response.id
            
            self._log_warn(f"Uploaded PDF to OpenAI: {file_id}")
            
            # Get language name
            from app.utils.language_utils import get_language_name
            lang_name = get_language_name(language)
            
            # Create assistant for exam generation with improved instructions
            instructions = (
                "You are an expert university exam creator.\n\n"
                
                f"LANGUAGE REQUIREMENT:\n"
                f"ALL questions, options, and answers MUST be in {lang_name}.\n"
                f"Generate questions and answers entirely in {lang_name}.\n\n"
                
                "QUALITY REQUIREMENTS:\n"
                "1. Test UNDERSTANDING and APPLICATION, not just memorization\n"
                "2. Questions must cover different topics from the PDF\n"
                "3. Clear, unambiguous wording\n"
                "4. Professional academic language\n\n"
                
                f"TASK: Generate {num_questions} questions at {difficulty} difficulty.\n\n"
                
                "TITLE GENERATION:\n"
                "Create a concise, descriptive title that summarizes the main topics/subjects covered in the PDF.\n"
                f"Title should be clear, specific, and in {lang_name} (max 50 characters).\n"
                f"STRICT PROHIBITION: If {lang_name} is English, the title MUST NOT contain any Korean characters (Hangul) or the character '및'. Use 'and' for conjunctions.\n"
                "Example: 'Introduction to Kotlin and Android Components'\n\n"
                
                "DIFFICULTY LEVELS:\n"
                "- easy: Direct recall from material\n"
                "- medium: Apply concepts to new situations\n"
                "- hard: Analyze, synthesize, evaluate\n\n"
                
                "QUESTION DISTRIBUTION:\n"
                "- Multiple choice: ~40% (exactly 4 options)\n"
                "- Short answer: ~40% (2-3 sentences expected)\n"
                "- Essay: ~20% (paragraph-length)\n\n"
                
                "⚠️ SCORING REQUIREMENT:\n"
                "The TOTAL points across all questions MUST equal exactly 100.\n"
                "Distribute points appropriately across questions:\n"
                "- Multiple choice: typically 5-10 points each\n"
                "- Short answer: typically 10-15 points each\n"
                "- Essay: typically 15-25 points each\n"
                "Adjust individual question points so the sum equals 100.\n\n"
                
                "IMPORTANT - INCLUDE ANSWERS AND RUBRICS:\n"
                "For MULTIPLE CHOICE:\n"
                "  - correct_answer: The correct option text\n"
                "  - model_answer: Explanation why this is correct\n\n"
                
                "For SHORT ANSWER:\n"
                "  - model_answer: Complete ideal answer (2-3 sentences)\n"
                "  - keywords: List of essential terms that must appear\n"
                "  - scoring_rubric: Breakdown by points\n\n"
                
                "For ESSAY:\n"
                "  - model_answer: Comprehensive ideal answer\n"
                "  - scoring_rubric: Detailed criteria with point allocation\n\n"
                
                "Each question must include:\n"
                "- id: sequential number\n"
                "- question: the question text\n"
                "- type: multiple_choice, short_answer, or essay\n"
                "- options: array of 4 choices for multiple_choice, null otherwise\n"
                "- points: integer score value\n"
                "- topic: brief topic this question covers\n"
                "- correct_answer: for multiple_choice (the correct option text)\n"
                "- model_answer: complete ideal answer for all types\n"
                "- keywords: for short_answer (list of key terms)\n"
                "- scoring_rubric: for short_answer and essay (array of criterion objects)\n\n"
                
                "Scoring rubric format:\n"
                '[{"criterion": "description", "points": number, "example": "optional example"}]\n'
                "The points in rubric items should sum to the question's total points.\n"
            )
            
            # Add previous context if available
            if previous_context and len(previous_context) > 0:
                instructions += "\n\n⚠️ PREVIOUS EXAM HISTORY:\n"
                instructions += "The student has taken this exam before. Here are their previous attempts:\n\n"
                
                context_limit = settings.exam_history_prompt_limit
                context_slice = previous_context if context_limit <= 0 else previous_context[:context_limit]
                
                for i, ctx in enumerate(context_slice, 1):
                    score_pct = (ctx['score'] / ctx['max_points'] * 100) if ctx['max_points'] > 0 else 0
                    instructions += f"{i}. Q: {ctx['question'][:100]}...\n"
                    instructions += f"   Topic: {ctx.get('topic', 'N/A')}\n"
                    instructions += f"   Student Answer: {ctx['answer'][:80]}...\n"
                    instructions += f"   Score: {ctx['score']}/{ctx['max_points']} ({score_pct:.0f}%)\n\n"
                
                instructions += (
                    "NEW EXAM STRATEGY:\n"
                    "- AVOID generating similar questions to those scored >80% (student mastered)\n"
                    "- FOCUS more on topics where student scored <60% (weak areas)\n"
                    "- Ensure broad coverage across ALL sections of the PDF\n"
                    "- Create NEW questions, not just rephrasing old ones\n"
                )
            
            assistant = await self.client.beta.assistants.create(
                name="Exam Generator",
                instructions=instructions,
                model='gpt-4o',  # TODO: Use self.model_candidates[0] when gpt-5 is supported
                tools=[{"type": "file_search"}],
                response_format={"type": "json_schema", "json_schema": {"name": "exam_response", "schema": self.exam_schema}}
            )
            
            # Create thread and attach file
            thread = await self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate {num_questions} exam questions from this lecture PDF at {difficulty} difficulty level.",
                        "attachments": [
                            {"file_id": file_id, "tools": [{"type": "file_search"}]}
                        ]
                    }
                ]
            )
            
            # Run assistant
            run = await self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )
            
            if run.status == 'completed':
                messages = await self.client.beta.threads.messages.list(thread_id=thread.id)
                response_content = messages.data[0].content[0].text.value
                
                # Parse JSON from response
                try:
                    exam_data = json.loads(response_content)
                except Exception:
                    # Try to extract JSON from response
                    import re
                    match = re.search(r'\{[\s\S]*\}', response_content)
                    if match:
                        exam_data = json.loads(match.group(0))
                    else:
                        raise ValueError(f"Could not parse JSON from response: {response_content[:200]}")
                
                # Post-processing: Fix common translation issues (unconditional removal of '및' as requested)
                if 'title' in exam_data:
                    exam_data['title'] = exam_data['title'].replace(" 및 ", ", ").replace(" 및", ", ").replace("및", ", ")
                
                # Cleanup
                await self.client.files.delete(file_id)
                await self.client.beta.assistants.delete(assistant.id)
                
                return {
                    'success': True,
                    'exam': exam_data,
                    'model': self.model,
                }
            else:
                # Cleanup on failure
                await self.client.files.delete(file_id)
                await self.client.beta.assistants.delete(assistant.id)
                
                raise Exception(f"Assistant run failed with status: {run.status}")
                
        except Exception as e:
            self._log_error(f'GPT exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }
    
    async def generate_exam_from_multiple_pdfs(
        self,
        pdf_bytes_list: List[tuple[bytes, str]],
        num_questions: int = 10,
        difficulty: str = "medium",
        language: str = "ko",
        previous_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate exam from multiple PDF files using OpenAI File API.
        
        Args:
            pdf_bytes_list: List of tuples (pdf_bytes, original_filename)
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            language: Language code (ISO 639-1: ko, en, ja, zh, etc.)
        
        Returns:
            Dict with success status and exam data
        """
        try:
            import io
            
            # Upload all PDFs to OpenAI
            file_ids = []
            for pdf_bytes, original_filename in pdf_bytes_list:
                pdf_file = io.BytesIO(pdf_bytes)
                pdf_file.name = original_filename
                
                file_response = await self.client.files.create(
                    file=pdf_file,
                    purpose='assistants'
                )
                file_ids.append(file_response.id)
                self._log_warn(f"Uploaded PDF to OpenAI: {file_response.id} ({original_filename})")
            
            # Get language name
            from app.utils.language_utils import get_language_name
            lang_name = get_language_name(language)
            
            # Create assistant for exam generation with improved instructions
            instructions = (
                "You are an expert university exam creator.\n\n"
                
                f"LANGUAGE REQUIREMENT:\n"
                f"ALL questions, options, and answers MUST be in {lang_name}.\n"
                f"Generate questions and answers entirely in {lang_name}.\n\n"
                
                "QUALITY REQUIREMENTS:\n"
                "1. Test UNDERSTANDING and APPLICATION, not just memorization\n"
                "2. Questions must cover different topics from ALL the provided PDFs\n"
                "3. Distribute questions across all materials\n"
                "4. Clear, unambiguous wording\n"
                "5. Professional academic language\n\n"
                
                f"TASK: Generate {num_questions} questions at {difficulty} difficulty from ALL PROVIDED MATERIALS.\n\n"
                
                "TITLE GENERATION:\n"
                f"Create a comprehensive title that synthesizes the main topics from ALL {len(pdf_bytes_list)} PDFs.\n"
                f"Title should reflect the combined scope of all materials and be in {lang_name} (max 50 characters).\n"
                f"STRICT PROHIBITION: If {lang_name} is English, the title MUST NOT contain any Korean characters (Hangul) or the character '및'. Use 'and' for conjunctions.\n"
                "Example: 'Comprehensive Kotlin and Android Grammar'\n\n"
                
                "DIFFICULTY LEVELS:\n"
                "- easy: Direct recall from material\n"
                "- medium: Apply concepts to new situations\n"
                "- hard: Analyze, synthesize, evaluate\n\n"
                
                "QUESTION DISTRIBUTION:\n"
                "- Multiple choice: ~40% (exactly 4 options)\n"
                "- Short answer: ~40% (2-3 sentences expected)\n"
                "- Essay: ~20% (paragraph-length)\n\n"
                
                "⚠️ SCORING REQUIREMENT:\n"
                "The TOTAL points across all questions MUST equal exactly 100.\n"
                "Distribute points appropriately across questions:\n"
                "- Multiple choice: typically 5-10 points each\n"
                "- Short answer: typically 10-15 points each\n"
                "- Essay: typically 15-25 points each\n"
                "Adjust individual question points so the sum equals 100.\n\n"
                
                "IMPORTANT - INCLUDE ANSWERS AND RUBRICS:\n"
                "For MULTIPLE CHOICE:\n"
                "  - correct_answer: The correct option text\n"
                "  - model_answer: Explanation why this is correct\n\n"
                
                "For SHORT ANSWER:\n"
                "  - model_answer: Complete ideal answer (2-3 sentences)\n"
                "  - keywords: List of essential terms that must appear\n"
                "  - scoring_rubric: Breakdown by points\n\n"
                
                "For ESSAY:\n"
                "  - model_answer: Comprehensive ideal answer\n"
                "  - scoring_rubric: Detailed criteria with point allocation\n\n"
                
                "Each question must include:\n"
                "- id: sequential number\n"
                "- question: the question text\n"
                "- type: multiple_choice, short_answer, or essay\n"
                "- options: array of 4 choices for multiple_choice, null otherwise\n"
                "- points: integer score value\n"
                "- topic: brief topic this question covers\n"
                "- correct_answer: for multiple_choice (the correct option text)\n"
                "- model_answer: complete ideal answer for all types\n"
                "- keywords: for short_answer (list of key terms)\n"
                "- scoring_rubric: for short_answer and essay (array of criterion objects)\n\n"
                
                "Scoring rubric format:\n"
                '[{"criterion": "description", "points": number, "example": "optional example"}]\n'
                "The points in rubric items should sum to the question's total points.\n"
            )
            
            # Add previous context if available
            if previous_context and len(previous_context) > 0:
                instructions += "\n\n⚠️ PREVIOUS EXAM HISTORY:\n"
                instructions += "The student has taken this exam before. Here are their previous attempts:\n\n"
                
                context_limit = settings.exam_history_prompt_limit
                context_slice = previous_context if context_limit <= 0 else previous_context[:context_limit]
                
                for i, ctx in enumerate(context_slice, 1):
                    score_pct = (ctx['score'] / ctx['max_points'] * 100) if ctx['max_points'] > 0 else 0
                    instructions += f"{i}. Q: {ctx['question'][:100]}...\n"
                    instructions += f"   Topic: {ctx.get('topic', 'N/A')}\n"
                    instructions += f"   Student Answer: {ctx['answer'][:80]}...\n"
                    instructions += f"   Score: {ctx['score']}/{ctx['max_points']} ({score_pct:.0f}%)\n\n"
                
                instructions += (
                    "NEW EXAM STRATEGY:\n"
                    "- AVOID generating similar questions to those scored >80% (student mastered)\n"
                    "- FOCUS more on topics where student scored <60% (weak areas)\n"
                    "- Ensure broad coverage across ALL sections of the PDFs\n"
                    "- Create NEW questions, not just rephrasing old ones\n"
                )
            
            assistant = await self.client.beta.assistants.create(
                name="Multi-PDF Exam Generator",
                instructions=instructions,
                model='gpt-4o',  # TODO: Use self.model_candidates[0] when gpt-5 is supported
                tools=[{"type": "file_search"}],
                response_format={"type": "json_schema", "json_schema": {"name": "exam_response", "schema": self.exam_schema}}
            )
            
            # Create thread with all files attached
            attachments = [{"file_id": fid, "tools": [{"type": "file_search"}]} for fid in file_ids]
            thread = await self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate {num_questions} exam questions from ALL {len(pdf_bytes_list)} provided lecture PDFs at {difficulty} difficulty level. Make sure to cover topics from all the materials.",
                        "attachments": attachments
                    }
                ]
            )
            
            # Run assistant
            run = await self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )
            
            if run.status == 'completed':
                messages = await self.client.beta.threads.messages.list(thread_id=thread.id)
                response_content = messages.data[0].content[0].text.value
                
                # Parse JSON from response
                try:
                    exam_data = json.loads(response_content)
                except Exception:
                    # Try to extract JSON from response
                    import re
                    match = re.search(r'\{[\s\S]*\}', response_content)
                    if match:
                        exam_data = json.loads(match.group(0))
                    else:
                        raise ValueError(f"Could not parse JSON from response: {response_content[:200]}")
                
                # Post-processing: Fix common translation issues (unconditional removal of '및' as requested)
                if 'title' in exam_data:
                    exam_data['title'] = exam_data['title'].replace(" 및 ", ", ").replace(" 및", ", ").replace("및", ", ")
                
                # Cleanup - delete all uploaded files
                for file_id in file_ids:
                    try:
                        await self.client.files.delete(file_id)
                    except Exception as e:
                        self._log_warn(f"Failed to delete file {file_id}: {e}")
                
                await self.client.beta.assistants.delete(assistant.id)
                
                return {
                    'success': True,
                    'exam': exam_data,
                    'model': self.model,
                }
            else:
                # Cleanup on failure
                for file_id in file_ids:
                    try:
                        await self.client.files.delete(file_id)
                    except Exception as e:
                        self._log_warn(f"Failed to delete file {file_id}: {e}")
                
                await self.client.beta.assistants.delete(assistant.id)
                
                raise Exception(f"Assistant run failed with status: {run.status}")
                
        except Exception as e:
            self._log_error(f'GPT multi-PDF exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    async def grade_exam_with_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        language: str = "ko"
    ) -> Dict[str, Any]:
        """
        Grade exam answers by referencing the original PDF.
        
        Args:
            pdf_bytes: Original PDF file content as bytes
            original_filename: Original filename
            questions: List of exam questions
            answers: List of student answers
        
        Returns:
            Dict with success status and grading results
        """
        try:
            from app.utils.language_utils import get_language_name
            lang_name = get_language_name(language)

            # Upload PDF to OpenAI
            import io
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_file.name = original_filename
            
            file_response = await self.client.files.create(
                file=pdf_file,
                purpose='assistants'
            )
            file_id = file_response.id
            
            self._log_warn(f"Uploaded PDF for grading to OpenAI: {file_id}")
            
            # Create assistant for grading
            assistant = await self.client.beta.assistants.create(
                name="Exam Grader",
                instructions=(
                    "You are an expert exam grader and learning advisor.\n\n"
                    
                    "GRADING TASK:\n"
                    "1. Grade each answer based on the lecture PDF content\n"
                    "2. Provide a model answer (ideal answer) for each question\n"
                    "3. Be objective and provide constructive feedback\n"
                    "4. Provide an overall assessment of student performance\n\n"
                    
                    "MODEL ANSWER REQUIREMENTS:\n"
                    "- For each question, provide a complete, ideal answer based on the PDF content\n"
                    "- Model answers should be comprehensive yet concise\n"
                    "- Include key concepts, terminology, and examples from the lecture material\n"
                    "- For multiple choice, explain why the correct option is right\n"
                    "- For math/formula questions, use LaTeX notation wrapped in $ or $$\n"
                    "  Example: The formula is $E = mc^2$ or display mode: $$\\int_{a}^{b} f(x)dx$$\n\n"
                    
                    "OVERALL ASSESSMENT:\n"
                    "After grading all questions, provide:\n"
                    "- overall_feedback: 2-3 sentences summarizing performance\n"
                    "- strengths: 2-3 specific achievements (what student did well)\n"
                    "- weaknesses: 2-3 areas needing improvement (specific topics)\n"
                    "- study_recommendations: 2-3 actionable study suggestions\n\n"
                    
                    "LANGUAGE REQUIREMENT:\n"
                    f"- All feedback, model answers, and textual output must be written in {lang_name} (language code: {language}).\n\n"
                    
                    "Return ONLY valid JSON with this structure:\n"
                    "{\n"
                    '  "question_results": [\n'
                    '    {\n'
                    '      "question_id": 1,\n'
                    '      "score": 8.5,\n'
                    '      "max_points": 10,\n'
                    '      "feedback": "Good explanation, but missing X...",\n'
                    '      "model_answer": "The ideal answer based on the PDF is...",\n'
                    '      "is_correct": true\n'
                    '    },\n'
                    '    ...\n'
                    '  ],\n'
                    '  "total_score": 85.5,\n'
                    '  "max_score": 100,\n'
                    '  "percentage": 85.5,\n'
                    '  "overall_feedback": "You demonstrated solid understanding...",\n'
                    '  "strengths": ["Clear explanation of X", "Good use of examples"],\n'
                    '  "weaknesses": ["Weak understanding of Y", "Missing key concepts in Z"],\n'
                    '  "study_recommendations": ["Review chapter 3", "Practice more problems on Y"]\n'
                    "}"
                ),
                model=self.model_candidates[0],
                tools=[{"type": "file_search"}],
            )
            
            # Prepare grading prompt
            grading_text = (
                f"Grade the following exam answers based on the lecture PDF. "
                f"Respond entirely in {lang_name} (language code: {language}).\n\n"
            )
            for question in questions:
                q_id = question['id']
                answer = next((a for a in answers if a['question_id'] == q_id), None)
                
                grading_text += f"Question {q_id} ({question['points']} points):\n"
                grading_text += f"{question['question']}\n"
                if answer:
                    grading_text += f"Student's Answer: {answer['answer']}\n\n"
                else:
                    grading_text += "Student's Answer: [No answer provided]\n\n"
            
            # Create thread and attach file
            thread = await self.client.beta.threads.create(
                messages=[
                    {
                        "role": "user",
                        "content": grading_text,
                        "attachments": [
                            {"file_id": file_id, "tools": [{"type": "file_search"}]}
                        ]
                    }
                ]
            )
            
            # Run assistant
            run = await self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
            )
            
            if run.status == 'completed':
                messages = await self.client.beta.threads.messages.list(thread_id=thread.id)
                response_content = messages.data[0].content[0].text.value
                
                # Parse JSON from response
                try:
                    result_data = json.loads(response_content)
                except Exception:
                    # Try to extract JSON from response
                    import re
                    match = re.search(r'\{[\s\S]*\}', response_content)
                    if match:
                        result_data = json.loads(match.group(0))
                    else:
                        raise ValueError(f"Could not parse JSON from grading response: {response_content[:200]}")
                
                # Remove citation markers from all text fields
                result_data = self._remove_citations(result_data)
                
                # Cleanup
                await self.client.files.delete(file_id)
                await self.client.beta.assistants.delete(assistant.id)
                
                return {
                    'success': True,
                    'result': result_data,
                }
            else:
                # Cleanup on failure
                await self.client.files.delete(file_id)
                await self.client.beta.assistants.delete(assistant.id)
                
                raise Exception(f"Assistant run failed with status: {run.status}")
                
        except Exception as e:
            self._log_error(f'Exam grading with PDF failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }
    
    async def grade_answer(self, question: str, student_answer: str, correct_answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Legacy method: Grade single answer without PDF reference.
        Note: Consider using grade_exam_with_pdf() for more accurate grading.
        """
        try:
            system_prompt = (
                "You are an expert exam grader.\n"
                "Grade the student's answer objectively and provide constructive feedback.\n\n"
                "Provide your response as valid JSON:\n"
                "{\n"
                "    \"score\": 0-100,\n"
                "    \"feedback\": \"detailed feedback\",\n"
                "    \"is_correct\": true/false\n"
                "}"
            )

            user_parts = [f"Question: {question}", f"\nStudent's Answer: {student_answer}"]
            if correct_answer:
                user_parts.append(f"\nCorrect Answer (for reference): {correct_answer}")
            user_prompt = "".join(user_parts)

            response = await self._chat_with_fallback(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content or "{}"
            raw = json.loads(result)

            # Normalize fields to guarantee score/feedback/is_correct
            def pick(*keys, default=None):
                for k in keys:
                    if k in raw and raw[k] is not None:
                        return raw[k]
                return default

            score = pick('score', 'grade', 'score_percent', default=0)
            try:
                score = float(score)
            except Exception:
                score = 0.0

            feedback = pick('feedback', 'explanation', 'comment', default="")

            is_correct = pick('is_correct', 'correct', default=None)
            if isinstance(is_correct, str):
                is_correct = is_correct.lower() in ('true', 'yes', '1')
            if is_correct is None:
                # Derive correctness if not provided
                is_correct = bool(score >= 99)

            grade_data = {
                'score': int(round(score)),
                'feedback': feedback,
                'is_correct': bool(is_correct),
            }

            return {
                'success': True,
                'grade': grade_data,
                'model': self.model,
            }
        except Exception as e:
            self._log_error(f'GPT grading failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    async def grade_exam(self, questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            results = []
            total_score = 0.0
            max_score = 0.0

            for question in questions:
                q_id = question['id']
                answer = next((a for a in answers if a['question_id'] == q_id), None)

                if not answer:
                    results.append({
                        'question_id': q_id,
                        'score': 0,
                        'max_points': question['points'],
                        'feedback': 'No answer provided',
                    })
                    max_score += float(question['points'])
                    continue

                grade_result = await self.grade_answer(
                    question['question'],
                    answer['answer'],
                )

                if grade_result['success']:
                    grade = grade_result['grade']
                    score = (float(grade['score']) / 100.0) * float(question['points'])
                    results.append({
                        'question_id': q_id,
                        'score': score,
                        'max_points': question['points'],
                        'feedback': grade['feedback'],
                        'is_correct': grade['is_correct'],
                    })
                    total_score += score
                else:
                    results.append({
                        'question_id': q_id,
                        'score': 0,
                        'max_points': question['points'],
                        'feedback': 'Grading error',
                    })
                max_score += float(question['points'])

            percentage = (total_score / max_score * 100.0) if max_score > 0 else 0.0

            return {
                'success': True,
                'result': {
                    'total_score': round(total_score, 2),
                    'max_score': max_score,
                    'percentage': round(percentage, 2),
                    'question_results': results,
                },
            }
        except Exception as e:
            self._log_error(f'Exam grading failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

