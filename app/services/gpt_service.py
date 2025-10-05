"""
GPT Service for exam generation and grading
Uses OpenAI API v1.x+ (new client-based structure)
"""
import os
from openai import OpenAI
from flask import current_app


class GPTService:
    """
    Service class for GPT interactions
    
    Note: Currently uses GPT-4 as GPT-5 is not yet released.
    Update model name when GPT-5 becomes available.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize GPT Service
        
        Args:
            api_key: OpenAI API key (optional, defaults to env variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        # Initialize OpenAI client (v1.x+ structure)
        self.client = OpenAI(api_key=self.api_key)
        
        # Model configuration
        # Note: GPT-5 not yet available as of 2025-10
        # Using gpt-4o (optimized) or gpt-4-turbo
        # Update model name when GPT-5 is released
        self.model = "gpt-4o"  # Most stable current model
    
    def generate_exam_from_text(self, pdf_text, num_questions=10, difficulty="medium"):
        """
        Generate exam questions from PDF text
        
        Args:
            pdf_text: Extracted text from PDF
            num_questions: Number of questions to generate
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        
        Returns:
            dict: {
                'questions': [
                    {
                        'id': 1,
                        'question': '...',
                        'type': 'multiple_choice' or 'short_answer' or 'essay',
                        'options': ['A', 'B', 'C', 'D'] (if multiple_choice),
                        'points': 10
                    },
                    ...
                ],
                'total_points': 100,
                'estimated_time': 60  # minutes
            }
        """
        try:
            # System prompt
            system_prompt = f"""You are an expert exam creator. 
Generate {num_questions} exam questions based on the provided lecture material.
Difficulty level: {difficulty}

Create a mix of:
- Multiple choice questions (40%)
- Short answer questions (40%)
- Essay questions (20%)

For each question, provide:
1. Question text
2. Question type
3. Options (if multiple choice)
4. Points value

Format your response as valid JSON with this structure:
{{
    "questions": [
        {{
            "id": 1,
            "question": "...",
            "type": "multiple_choice|short_answer|essay",
            "options": ["A", "B", "C", "D"],  // only for multiple_choice
            "points": 10
        }}
    ],
    "total_points": 100,
    "estimated_time": 60
}}"""

            # User prompt with PDF content
            user_prompt = f"Lecture material:\n\n{pdf_text[:15000]}"  # Limit to ~15k chars
            
            # Call GPT API (v1.x+ structure)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Extract response
            result = response.choices[0].message.content
            
            # Parse JSON
            import json
            exam_data = json.loads(result)
            
            return {
                'success': True,
                'exam': exam_data
            }
            
        except Exception as e:
            current_app.logger.error(f'GPT exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def grade_answer(self, question, student_answer, correct_answer=None):
        """
        Grade a student's answer using GPT
        
        Args:
            question: Question text
            student_answer: Student's submitted answer
            correct_answer: Correct answer (optional, for reference)
        
        Returns:
            dict: {
                'score': 0-100,
                'feedback': '...',
                'is_correct': True/False
            }
        """
        try:
            # System prompt
            system_prompt = """You are an expert exam grader.
Grade the student's answer objectively and provide constructive feedback.

Provide your response as valid JSON:
{
    "score": 0-100,
    "feedback": "detailed feedback",
    "is_correct": true/false
}"""
            
            # User prompt
            user_prompt = f"""Question: {question}

Student's Answer: {student_answer}
"""
            
            if correct_answer:
                user_prompt += f"\nCorrect Answer (for reference): {correct_answer}"
            
            # Call GPT API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Extract response
            result = response.choices[0].message.content
            
            # Parse JSON
            import json
            grade_data = json.loads(result)
            
            return {
                'success': True,
                'grade': grade_data
            }
            
        except Exception as e:
            current_app.logger.error(f'GPT grading failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def grade_exam(self, questions, answers):
        """
        Grade entire exam
        
        Args:
            questions: List of question objects
            answers: List of student answer objects
        
        Returns:
            dict: {
                'total_score': 85,
                'max_score': 100,
                'percentage': 85.0,
                'question_results': [...]
            }
        """
        try:
            results = []
            total_score = 0
            max_score = 0
            
            for question in questions:
                q_id = question['id']
                
                # Find corresponding answer
                answer = next((a for a in answers if a['question_id'] == q_id), None)
                
                if not answer:
                    results.append({
                        'question_id': q_id,
                        'score': 0,
                        'max_points': question['points'],
                        'feedback': 'No answer provided'
                    })
                    max_score += question['points']
                    continue
                
                # Grade the answer
                grade_result = self.grade_answer(
                    question['question'],
                    answer['answer']
                )
                
                if grade_result['success']:
                    grade = grade_result['grade']
                    score = (grade['score'] / 100) * question['points']
                    
                    results.append({
                        'question_id': q_id,
                        'score': score,
                        'max_points': question['points'],
                        'feedback': grade['feedback'],
                        'is_correct': grade['is_correct']
                    })
                    
                    total_score += score
                else:
                    results.append({
                        'question_id': q_id,
                        'score': 0,
                        'max_points': question['points'],
                        'feedback': 'Grading error'
                    })
                
                max_score += question['points']
            
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            return {
                'success': True,
                'result': {
                    'total_score': round(total_score, 2),
                    'max_score': max_score,
                    'percentage': round(percentage, 2),
                    'question_results': results
                }
            }
            
        except Exception as e:
            current_app.logger.error(f'Exam grading failed: {e}')
            return {
                'success': False,
                'error': str(e)
            }

