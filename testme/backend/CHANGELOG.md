# Changelog

## [2.1.0] - 2025-11-08

### Added - Enhanced Exam Generation with Structured Answers and Grading Rubrics

#### Domain Models
- **ScoringCriterion**: New model for detailed grading rubrics
  - `criterion`: Description of grading criterion
  - `points`: Point allocation for this criterion
  - `example`: Optional example answer

- **Question Model Enhancement**: Extended with answer and grading fields
  - `topic`: Question topic classification
  - `correct_answer`: Correct option for multiple choice questions
  - `model_answer`: Complete ideal answer for all question types
  - `keywords`: Key terms for short answer questions
  - `scoring_rubric`: Detailed grading criteria with point breakdown

#### AI Services
- **Improved Prompts**: Comprehensive instructions for high-quality question generation
  - Clear quality requirements
  - Difficulty level definitions
  - Detailed answer and rubric requirements
  - Support for Korean educational context

- **Structured Outputs**:
  - GPTService: OpenAI Structured Outputs with JSON Schema
  - GeminiService: Gemini JSON mode with schema validation
  - Guaranteed consistent response format

#### Validation
- **exam_validator.py**: New utility for AI response validation
  - `validate_exam_response()`: Validates question count, types, and structure
  - `validate_scoring_rubric()`: Ensures rubric points match question points
  - Comprehensive error detection and logging

#### Route Integration
- exam.py: Integrated validation into exam generation workflow
  - Validates AI responses before storage
  - Logs validation issues as warnings
  - Ensures data consistency

#### Testing
- **test_exam_validator.py**: 14 comprehensive validator tests
- **test_domain_models.py**: Enhanced with new model tests
  - ScoringCriterion tests
  - Enhanced Question field tests
  - Short answer and essay question tests with rubrics
- All 54+ tests passing

### Technical Details

**JSON Schema Structure**:
```json
{
  "questions": [
    {
      "id": 1,
      "question": "...",
      "type": "multiple_choice|short_answer|essay",
      "options": ["A", "B", "C", "D"] or null,
      "points": 10,
      "topic": "...",
      "correct_answer": "...",
      "model_answer": "...",
      "keywords": [...],
      "scoring_rubric": [
        {"criterion": "...", "points": 5, "example": "..."}
      ]
    }
  ],
  "total_points": 100,
  "estimated_time": 60
}
```

**Question Type Requirements**:
- Multiple Choice: `correct_answer`, `model_answer` required
- Short Answer: `model_answer`, `keywords`, `scoring_rubric` recommended
- Essay: `model_answer`, `scoring_rubric` required

### Benefits
- Clear answer keys for all questions
- Structured grading criteria for consistent scoring
- Improved AI prompt quality for better question generation
- Automatic validation prevents malformed exam data
- Better support for Korean educational content

---

## [2.0.0] - 2025-11-07

### Changed
- Migrated to Subject-based structure
- Updated all routes to use `/subjects/{subject_id}/` prefix
- Enhanced Firebase integration

### Added
- Subject management endpoints
- Improved AI service architecture
- Strategy pattern for AI providers

---

## [1.0.0] - 2025-11-06

### Initial Release
- FastAPI-based REST API
- Firebase Authentication and Storage
- PDF upload and management
- AI-powered exam generation (GPT/Gemini)
- Automated grading system



