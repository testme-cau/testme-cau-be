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
    
    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "gemini"
    
    def generate_exam_from_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        num_questions: int = 10,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate exam questions from PDF file using Gemini
        
        Args:
            pdf_bytes: PDF file content as bytes
            original_filename: Original filename
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            Dict with success status and exam data
        """
        try:
            # Upload PDF to Gemini
            pdf_file = io.BytesIO(pdf_bytes)
            uploaded_file = genai.upload_file(pdf_file, mime_type='application/pdf')
            
            self.logger.info(f"Uploaded PDF to Gemini: {uploaded_file.name}")
            
            # Create prompt for exam generation
            prompt = f"""
You are an expert exam creator. Analyze the provided PDF lecture material and generate {num_questions} exam questions.
Difficulty level: {difficulty}.

Create a mix of:
- 40% multiple choice questions (with 4 options each)
- 40% short answer questions
- 20% essay questions

Return ONLY valid JSON with this exact structure (no markdown, no code blocks, just raw JSON):
{{
    "questions": [
        {{
            "id": 1,
            "question": "question text here",
            "type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "points": 10
        }},
        {{
            "id": 2,
            "question": "question text here",
            "type": "short_answer",
            "options": null,
            "points": 10
        }},
        {{
            "id": 3,
            "question": "question text here",
            "type": "essay",
            "options": null,
            "points": 20
        }}
    ],
    "total_points": 100,
    "estimated_time": 60
}}

Generate the questions now:
"""
            
            # Generate exam
            response = self.model.generate_content([uploaded_file, prompt])
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
You are an expert exam grader. Grade the following exam answers based on the lecture PDF content.
Be objective and provide constructive feedback.

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
    "percentage": 85.5
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

