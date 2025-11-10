"""
Gemini Service for exam generation and grading
Uses Google Generative AI SDK
"""
import os
import json
import logging
import io
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.services.ai_service_interface import AIServiceInterface


class GeminiService(AIServiceInterface):
    """
    Service class for Gemini AI interactions
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Model configuration
        self.model_name = model or os.getenv('GOOGLE_MODEL', 'gemini-1.5-pro')
        self.model = genai.GenerativeModel(self.model_name)
        self.logger = logging.getLogger(__name__)
        
        # JSON Schema for structured exam generation
        self.exam_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Brief descriptive title summarizing main topics covered (max 50 chars)"},
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
    def provider_name(self) -> str:
        """Return provider name"""
        return "gemini"
    
    def generate_exam_from_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        num_questions: int = 10,
        difficulty: str = "medium",
        language: str = "ko",
        previous_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate exam questions from PDF file using Gemini
        
        Args:
            pdf_bytes: PDF file content as bytes
            original_filename: Original filename
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            language: Language code (ISO 639-1: ko, en, ja, zh, etc.)
        
        Returns:
            Dict with success status and exam data
        """
        try:
            # Upload PDF to Gemini
            pdf_file = io.BytesIO(pdf_bytes)
            uploaded_file = genai.upload_file(pdf_file, mime_type='application/pdf')
            
            self.logger.info(f"Uploaded PDF to Gemini: {uploaded_file.name}")
            
            # Get language name
            from app.utils.language_utils import get_language_name
            lang_name = get_language_name(language)
            
            # Create improved prompt for exam generation
            prompt = (
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
                "Example: 'Kotlin 기초 및 Android 컴포넌트'\n\n"
                
                "DIFFICULTY LEVELS:\n"
                "- easy: Direct recall from material\n"
                "- medium: Apply concepts to new situations\n"
                "- hard: Analyze, synthesize, evaluate\n\n"
                
                "QUESTION DISTRIBUTION:\n"
                "- Multiple choice: ~40% (exactly 4 options)\n"
                "- Short answer: ~40% (2-3 sentences expected)\n"
                "- Essay: ~20% (paragraph-length)\n\n"
                
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
                "The points in rubric items should sum to the question's total points.\n\n"
                
                "Generate the exam questions now based on the PDF content."
            )
            
            # Add previous context if available
            if previous_context and len(previous_context) > 0:
                prompt += "\n\n⚠️ PREVIOUS EXAM HISTORY:\n"
                prompt += "The student has taken this exam before. Here are their previous attempts:\n\n"
                
                for i, ctx in enumerate(previous_context[:15], 1):  # Limit to 15 for token management
                    score_pct = (ctx['score'] / ctx['max_points'] * 100) if ctx['max_points'] > 0 else 0
                    prompt += f"{i}. Q: {ctx['question'][:100]}...\n"
                    prompt += f"   Topic: {ctx.get('topic', 'N/A')}\n"
                    prompt += f"   Student Answer: {ctx['answer'][:80]}...\n"
                    prompt += f"   Score: {ctx['score']}/{ctx['max_points']} ({score_pct:.0f}%)\n\n"
                
                prompt += (
                    "NEW EXAM STRATEGY:\n"
                    "- AVOID generating similar questions to those scored >80% (student mastered)\n"
                    "- FOCUS more on topics where student scored <60% (weak areas)\n"
                    "- Ensure broad coverage across ALL sections of the PDF\n"
                    "- Create NEW questions, not just rephrasing old ones\n"
                )
            
            # Generate exam with JSON mode
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.exam_schema
            )
            
            response = self.model.generate_content(
                [uploaded_file, prompt],
                generation_config=generation_config
            )
            response_text = response.text
            
            # Parse JSON from response
            try:
                # Try direct parsing
                exam_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response (in case of markdown code blocks)
                import re
                # Remove markdown code blocks if present
                cleaned = re.sub(r'```json\s*', '', response_text)
                cleaned = re.sub(r'```\s*', '', cleaned)
                cleaned = cleaned.strip()
                
                # Try to find JSON object
                match = re.search(r'\{[\s\S]*\}', cleaned)
                if match:
                    exam_data = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
            
            # Delete uploaded file
            genai.delete_file(uploaded_file.name)
            
            return {
                'success': True,
                'exam': exam_data,
                'model': self.model_name,
            }
            
        except Exception as e:
            self.logger.error(f'Gemini exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }
    
    def generate_exam_from_multiple_pdfs(
        self,
        pdf_bytes_list: List[tuple[bytes, str]],
        num_questions: int = 10,
        difficulty: str = "medium",
        language: str = "ko",
        previous_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate exam questions from multiple PDF files using Gemini
        
        Args:
            pdf_bytes_list: List of tuples (pdf_bytes, original_filename)
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            language: Language code (ISO 639-1: ko, en, ja, zh, etc.)
        
        Returns:
            Dict with success status and exam data
        """
        try:
            # Upload all PDFs to Gemini
            uploaded_files = []
            for pdf_bytes, original_filename in pdf_bytes_list:
                pdf_file = io.BytesIO(pdf_bytes)
                uploaded_file = genai.upload_file(pdf_file, mime_type='application/pdf')
                uploaded_files.append(uploaded_file)
                self.logger.info(f"Uploaded PDF to Gemini: {uploaded_file.name} ({original_filename})")
            
            # Get language name
            from app.utils.language_utils import get_language_name
            lang_name = get_language_name(language)
            
            # Create improved prompt for multi-PDF exam generation
            prompt = (
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
                
                f"TASK: Generate {num_questions} questions at {difficulty} difficulty from ALL {len(pdf_bytes_list)} PROVIDED PDFS.\n\n"
                
                "TITLE GENERATION:\n"
                f"Create a comprehensive title that synthesizes the main topics from ALL {len(pdf_bytes_list)} PDFs.\n"
                f"Title should reflect the combined scope of all materials and be in {lang_name} (max 50 characters).\n"
                "Example: 'Kotlin 기초 및 Android Grammar 종합'\n\n"
                
                "DIFFICULTY LEVELS:\n"
                "- easy: Direct recall from material\n"
                "- medium: Apply concepts to new situations\n"
                "- hard: Analyze, synthesize, evaluate\n\n"
                
                "QUESTION DISTRIBUTION:\n"
                "- Multiple choice: ~40% (exactly 4 options)\n"
                "- Short answer: ~40% (2-3 sentences expected)\n"
                "- Essay: ~20% (paragraph-length)\n\n"
                
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
                "The points in rubric items should sum to the question's total points.\n\n"
                
                "Generate the exam questions now based on ALL the PDF contents. Make sure to cover topics from all materials."
            )
            
            # Add previous context if available
            if previous_context and len(previous_context) > 0:
                prompt += "\n\n⚠️ PREVIOUS EXAM HISTORY:\n"
                prompt += "The student has taken this exam before. Here are their previous attempts:\n\n"
                
                for i, ctx in enumerate(previous_context[:15], 1):  # Limit to 15 for token management
                    score_pct = (ctx['score'] / ctx['max_points'] * 100) if ctx['max_points'] > 0 else 0
                    prompt += f"{i}. Q: {ctx['question'][:100]}...\n"
                    prompt += f"   Topic: {ctx.get('topic', 'N/A')}\n"
                    prompt += f"   Student Answer: {ctx['answer'][:80]}...\n"
                    prompt += f"   Score: {ctx['score']}/{ctx['max_points']} ({score_pct:.0f}%)\n\n"
                
                prompt += (
                    "NEW EXAM STRATEGY:\n"
                    "- AVOID generating similar questions to those scored >80% (student mastered)\n"
                    "- FOCUS more on topics where student scored <60% (weak areas)\n"
                    "- Ensure broad coverage across ALL sections of the PDFs\n"
                    "- Create NEW questions, not just rephrasing old ones\n"
                )
            
            # Generate exam with JSON mode
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.exam_schema
            )
            
            # Combine all files and prompt for content generation
            content_parts = uploaded_files + [prompt]
            response = self.model.generate_content(
                content_parts,
                generation_config=generation_config
            )
            response_text = response.text
            
            # Parse JSON from response
            try:
                # Try direct parsing
                exam_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response (in case of markdown code blocks)
                import re
                # Remove markdown code blocks if present
                cleaned = re.sub(r'```json\s*', '', response_text)
                cleaned = re.sub(r'```\s*', '', cleaned)
                cleaned = cleaned.strip()
                
                # Try to find JSON object
                match = re.search(r'\{[\s\S]*\}', cleaned)
                if match:
                    exam_data = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
            
            # Delete all uploaded files
            for uploaded_file in uploaded_files:
                try:
                    genai.delete_file(uploaded_file.name)
                except Exception as e:
                    self.logger.warning(f"Failed to delete file {uploaded_file.name}: {e}")
            
            return {
                'success': True,
                'exam': exam_data,
                'model': self.model_name,
            }
            
        except Exception as e:
            self.logger.error(f'Gemini multi-PDF exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }
    
    def grade_exam_with_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Grade exam answers by referencing the original PDF using Gemini
        
        Args:
            pdf_bytes: Original PDF file content as bytes
            original_filename: Original filename
            questions: List of exam questions
            answers: List of student answers
        
        Returns:
            Dict with success status and grading results
        """
        try:
            # Upload PDF to Gemini
            pdf_file = io.BytesIO(pdf_bytes)
            uploaded_file = genai.upload_file(pdf_file, mime_type='application/pdf')
            
            self.logger.info(f"Uploaded PDF for grading to Gemini: {uploaded_file.name}")
            
            # Prepare grading prompt
            grading_text = """
You are an expert exam grader and learning advisor.

GRADING TASK:
1. Grade each answer based on the lecture PDF content
2. Be objective and provide constructive feedback
3. Provide an overall assessment of student performance

OVERALL ASSESSMENT:
After grading all questions, provide:
- overall_feedback: 2-3 sentences summarizing performance
- strengths: 2-3 specific achievements (what student did well)
- weaknesses: 2-3 areas needing improvement (specific topics)
- study_recommendations: 2-3 actionable study suggestions

Return ONLY valid JSON with this structure (no markdown, no code blocks):
{
    "question_results": [
        {
            "question_id": 1,
            "score": 8.5,
            "max_points": 10,
            "feedback": "Good answer, but could be more detailed",
            "is_correct": true
        }
    ],
    "total_score": 85.5,
    "max_score": 100,
    "percentage": 85.5,
    "overall_feedback": "You demonstrated solid understanding...",
    "strengths": ["Clear explanation of X", "Good use of examples"],
    "weaknesses": ["Weak understanding of Y", "Missing key concepts in Z"],
    "study_recommendations": ["Review chapter 3", "Practice more problems on Y"]
}

Here are the questions and answers to grade:

"""
            
            for question in questions:
                q_id = question['id']
                answer = next((a for a in answers if a['question_id'] == q_id), None)
                
                grading_text += f"\nQuestion {q_id} ({question['points']} points):\n"
                grading_text += f"{question['question']}\n"
                if answer:
                    grading_text += f"Student's Answer: {answer['answer']}\n"
                else:
                    grading_text += "Student's Answer: [No answer provided]\n"
            
            grading_text += "\nProvide your grading now:"
            
            # Grade with Gemini
            response = self.model.generate_content([uploaded_file, grading_text])
            response_text = response.text
            
            # Parse JSON from response
            try:
                result_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                cleaned = re.sub(r'```json\s*', '', response_text)
                cleaned = re.sub(r'```\s*', '', cleaned)
                cleaned = cleaned.strip()
                
                match = re.search(r'\{[\s\S]*\}', cleaned)
                if match:
                    result_data = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse JSON from grading response: {response_text[:200]}")
            
            # Delete uploaded file
            genai.delete_file(uploaded_file.name)
            
            return {
                'success': True,
                'result': result_data,
            }
            
        except Exception as e:
            self.logger.error(f'Gemini grading failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }
    
    def grade_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str | None = None
    ) -> Dict[str, Any]:
        """
        Grade a single answer using Gemini (legacy method without PDF)
        
        Args:
            question: The question text
            student_answer: Student's answer
            correct_answer: Optional correct answer for reference
        
        Returns:
            Dict with success status and grade data
        """
        try:
            prompt = f"""
You are an expert exam grader.
Grade the student's answer objectively and provide constructive feedback.

Question: {question}
Student's Answer: {student_answer}
"""
            if correct_answer:
                prompt += f"\nCorrect Answer (for reference): {correct_answer}"
            
            prompt += """

Return ONLY valid JSON with this structure (no markdown, no code blocks):
{
    "score": 85,
    "feedback": "detailed feedback here",
    "is_correct": true
}

Provide your grading now:
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse JSON
            try:
                grade_data = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                cleaned = re.sub(r'```json\s*', '', response_text)
                cleaned = re.sub(r'```\s*', '', cleaned)
                cleaned = cleaned.strip()
                
                match = re.search(r'\{[\s\S]*\}', cleaned)
                if match:
                    grade_data = json.loads(match.group(0))
                else:
                    raise ValueError(f"Could not parse JSON: {response_text[:200]}")
            
            # Normalize response
            if 'score' not in grade_data:
                grade_data['score'] = 0
            if 'feedback' not in grade_data:
                grade_data['feedback'] = ""
            if 'is_correct' not in grade_data:
                grade_data['is_correct'] = grade_data['score'] >= 90
            
            return {
                'success': True,
                'grade': grade_data,
                'model': self.model_name,
            }
            
        except Exception as e:
            self.logger.error(f'Gemini grading failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

