"""
GPT Service for exam generation and grading
Uses OpenAI API v1.x+ (new client-based structure)
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from flask import current_app, has_app_context


class GPTService:
    """
    Service class for GPT interactions with model fallback.
    Primary model is driven by OPENAI_MODEL (default: gpt-5), with fallbacks.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        # Initialize OpenAI client (v1.x+ structure)
        self.client = OpenAI(api_key=self.api_key)

        # Model configuration with fallback chain
        env_model = os.getenv('OPENAI_MODEL', 'gpt-5')
        self.model_candidates: List[str] = [
            env_model,
            'gpt-5',
            'gpt-4.1',
            'gpt-4o',
            'gpt-4o-mini',
        ]
        self.active_model: Optional[str] = None

    @property
    def model(self) -> str:
        """Expose a model name for diagnostics (first candidate until resolved)."""
        return self.active_model or self.model_candidates[0]

    # ---------- internal logging helpers ----------
    def _log_warn(self, message: str) -> None:
        try:
            if has_app_context():
                current_app.logger.warning(message)
                return
        except Exception:
            pass
        logging.getLogger(__name__).warning(message)

    def _log_error(self, message: str) -> None:
        try:
            if has_app_context():
                current_app.logger.error(message)
                return
        except Exception:
            pass
        logging.getLogger(__name__).error(message)

    # ---------- internal chat helper ----------
    def _create_chat_completion(self, *, model: str, messages, temperature: float, max_tokens: int, response_format):
        """
        Create a chat completion. Handle gpt-5 parameter compatibility:
        - Prefer max_tokens (per latest sample)
        - If model rejects max_tokens, retry with max_completion_tokens
        - If model rejects temperature, retry without temperature
        - For gpt-5, avoid response_format unless required by prompt
        """
        def call(kwargs: Dict[str, Any]):
            return self.client.chat.completions.create(**kwargs)

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
            return call(kwargs)
        except Exception as e:
            msg = str(e)
            # Retry: if max_tokens unsupported → switch to max_completion_tokens
            if "Unsupported parameter: 'max_tokens'" in msg:
                self._log_warn(f"Model '{model}' rejected max_tokens; retrying with max_completion_tokens")
                kwargs.pop('max_tokens', None)
                kwargs['max_completion_tokens'] = max_tokens
                try:
                    return call(kwargs)
                except Exception as e2:
                    msg2 = str(e2)
                    # If temperature unsupported → drop it and retry
                    if "Unsupported value: 'temperature'" in msg2:
                        self._log_warn(f"Model '{model}' rejected temperature; retrying without temperature")
                        kwargs.pop('temperature', None)
                        return call(kwargs)
                    raise
            # Retry: temperature unsupported → drop it and retry
            if "Unsupported value: 'temperature'" in msg:
                self._log_warn(f"Model '{model}' rejected temperature; retrying without temperature")
                kwargs.pop('temperature', None)
                return call(kwargs)
            raise

    # ---------- internal chat helper with fallback ----------
    def _chat_with_fallback(
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
                resp = self._create_chat_completion(
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
    def generate_exam_from_text(self, pdf_text: str, num_questions: int = 10, difficulty: str = "medium") -> Dict[str, Any]:
        try:
            system_prompt = (
                f"You are an expert exam creator.\n"
                f"Generate {num_questions} exam questions based on the provided lecture material.\n"
                f"Difficulty level: {difficulty}\n\n"
                "Create a mix of:\n"
                "- Multiple choice questions (40%)\n"
                "- Short answer questions (40%)\n"
                "- Essay questions (20%)\n\n"
                "For each question, provide:\n"
                "1. Question text\n"
                "2. Question type\n"
                "3. Options (if multiple choice)\n"
                "4. Points value\n\n"
                "Return only valid JSON with this structure:\n"
                "{\n"
                "    \"questions\": [\n"
                "        {\n"
                "            \"id\": 1,\n"
                "            \"question\": \"...\",\n"
                "            \"type\": \"multiple_choice|short_answer|essay\",\n"
                "            \"options\": [\"A\", \"B\", \"C\", \"D\"],\n"
                "            \"points\": 10\n"
                "        }\n"
                "    ],\n"
                "    \"total_points\": 100,\n"
                "    \"estimated_time\": 60\n"
                "}"
            )
            user_prompt = f"Lecture material:\n\n{pdf_text[:15000]}"

            # For gpt-5, do not force response_format to reduce incompat issues
            response = self._chat_with_fallback(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content or "{}"
            try:
                exam_data = json.loads(result)
            except Exception:
                # Try to rescue JSON from content if model returned extra text
                import re
                match = re.search(r"\{[\s\S]*\}\s*$", result)
                if match:
                    exam_data = json.loads(match.group(0))
                else:
                    raise

            return {
                'success': True,
                'exam': exam_data,
                'model': self.model,
            }
        except Exception as e:
            self._log_error(f'GPT exam generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
            }

    def grade_answer(self, question: str, student_answer: str, correct_answer: Optional[str] = None) -> Dict[str, Any]:
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

            response = self._chat_with_fallback(
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

    def grade_exam(self, questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
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

                grade_result = self.grade_answer(
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

