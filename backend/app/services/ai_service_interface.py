"""
AI Service Interface - Abstract base class for AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AIServiceInterface(ABC):
    """
    Abstract interface for AI services (GPT, Gemini, etc.)
    All AI providers must implement these methods
    """
    
    @abstractmethod
    def generate_exam_from_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        num_questions: int = 10,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate exam questions from PDF file
        
        Args:
            pdf_bytes: PDF file content as bytes
            original_filename: Original filename (for AI upload)
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            Dict with structure:
            {
                'success': bool,
                'exam': {
                    'questions': [
                        {
                            'id': int,
                            'question': str,
                            'type': str,  # multiple_choice, short_answer, essay
                            'options': List[str] or None,
                            'points': int
                        },
                        ...
                    ],
                    'total_points': int,
                    'estimated_time': int
                },
                'model': str,  # Model name used
                'error': str (if success=False)
            }
        """
        pass
    
    @abstractmethod
    def grade_exam_with_pdf(
        self,
        pdf_bytes: bytes,
        original_filename: str,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Grade exam answers by referencing the original PDF
        
        Args:
            pdf_bytes: Original PDF file content as bytes
            original_filename: Original filename
            questions: List of exam questions
            answers: List of student answers with structure:
                [{'question_id': int, 'answer': str}, ...]
        
        Returns:
            Dict with structure:
            {
                'success': bool,
                'result': {
                    'total_score': float,
                    'max_score': float,
                    'percentage': float,
                    'question_results': [
                        {
                            'question_id': int,
                            'score': float,
                            'max_points': int,
                            'feedback': str,
                            'is_correct': bool
                        },
                        ...
                    ]
                },
                'error': str (if success=False)
            }
        """
        pass
    
    @abstractmethod
    def grade_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str | None = None
    ) -> Dict[str, Any]:
        """
        Grade a single answer (legacy method without PDF reference)
        
        Args:
            question: The question text
            student_answer: Student's answer
            correct_answer: Optional correct answer for reference
        
        Returns:
            Dict with structure:
            {
                'success': bool,
                'grade': {
                    'score': int (0-100),
                    'feedback': str,
                    'is_correct': bool
                },
                'model': str,
                'error': str (if success=False)
            }
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the provider name (e.g., 'gpt', 'gemini')
        """
        pass

