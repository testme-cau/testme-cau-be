"""
Domain model validation tests - Pure business logic without infrastructure
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.domain import Subject, PDF, Question, Exam, QuestionResult, GradingResult, ScoringCriterion
from app.models.requests import (
    SubjectCreateRequest,
    SubjectUpdateRequest,
    ExamGenerationRequest,
    ExamSubmissionRequest,
    AnswerSubmission
)
from app.models.responses import SubjectResponse, SubjectListResponse


class TestSubjectModel:
    """Test Subject domain model"""
    
    def test_subject_creation_valid(self):
        """Test creating a valid subject"""
        subject = Subject(
            subject_id="subj_123",
            user_id="user_123",
            name="데이터베이스",
            description="데이터베이스 설계",
            group_id="group_123",
            color="#FF5733",
            created_at=datetime.utcnow()
        )
        
        assert subject.subject_id == "subj_123"
        assert subject.name == "데이터베이스"
        assert subject.group_id == "group_123"
        assert subject.color == "#FF5733"
    
    def test_subject_minimal_required_fields(self):
        """Test subject with only required fields"""
        subject = Subject(
            subject_id="subj_123",
            user_id="user_123",
            name="알고리즘",
            created_at=datetime.utcnow()
        )
        
        assert subject.name == "알고리즘"
        assert subject.description is None
        assert subject.group_id is None
        assert subject.color is None


class TestSubjectRequestModels:
    """Test Subject request validation"""
    
    def test_create_request_valid(self):
        """Test valid subject creation request"""
        request = SubjectCreateRequest(
            name="운영체제",
            description="운영체제 이론과 실습",
            group_id="group_123",
            color="#3498db"
        )
        
        assert request.name == "운영체제"
        assert request.group_id == "group_123"
    
    def test_create_request_name_required(self):
        """Test that name is required"""
        with pytest.raises(ValidationError) as exc_info:
            SubjectCreateRequest(
                description="설명만 있음"
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
    
    def test_create_request_invalid_color_format(self):
        """Test invalid color format"""
        with pytest.raises(ValidationError) as exc_info:
            SubjectCreateRequest(
                name="과목",
                color="invalid_color"
            )
        
        errors = exc_info.value.errors()
        assert any('color' in str(error) for error in errors)
    
    def test_create_request_valid_color_formats(self):
        """Test various valid color formats"""
        valid_colors = ["#FF5733", "#abc123", "#000000", "#FFFFFF"]
        
        for color in valid_colors:
            request = SubjectCreateRequest(name="과목", color=color)
            assert request.color == color
    
    def test_create_request_year_range_validation(self):
        """Test group_id validation"""
        # Valid with group_id
        request = SubjectCreateRequest(name="과목", group_id="group_123")
        assert request.group_id == "group_123"
        
        # Valid without group_id
        request2 = SubjectCreateRequest(name="과목")
        assert request2.group_id is None
    
    def test_update_request_all_optional(self):
        """Test that all fields in update request are optional"""
        request = SubjectUpdateRequest()
        
        assert request.name is None
        assert request.description is None
        assert request.group_id is None
        assert request.color is None
    
    def test_update_request_partial_update(self):
        """Test partial update with some fields"""
        request = SubjectUpdateRequest(
            name="업데이트된 이름",
            color="#FF0000"
        )
        
        assert request.name == "업데이트된 이름"
        assert request.color == "#FF0000"
        assert request.description is None


class TestSubjectResponseModels:
    """Test Subject response models"""
    
    def test_subject_response(self):
        """Test subject response model"""
        subject = Subject(
            subject_id="subj_123",
            user_id="user_123",
            name="과목",
            created_at=datetime.utcnow()
        )
        
        response = SubjectResponse(success=True, subject=subject)
        
        assert response.success is True
        assert response.subject.subject_id == "subj_123"
    
    def test_subject_list_response(self):
        """Test subject list response model"""
        subjects = [
            Subject(
                subject_id=f"subj_{i}",
                user_id="user_123",
                name=f"과목 {i}",
                created_at=datetime.utcnow()
            )
            for i in range(3)
        ]
        
        response = SubjectListResponse(
            success=True,
            subjects=subjects,
            count=len(subjects)
        )
        
        assert response.success is True
        assert response.count == 3
        assert len(response.subjects) == 3


class TestPDFModel:
    """Test PDF domain model"""
    
    def test_pdf_creation(self):
        """Test creating a PDF model"""
        pdf = PDF(
            file_id="pdf_123",
            subject_id="subj_123",
            original_filename="lecture.pdf",
            unique_filename="pdf_123_lecture.pdf",
            storage_path="pdfs/user_123/pdf_123_lecture.pdf",
            size=1024000,
            user_id="user_123",
            uploaded_at=datetime.utcnow(),
            status="uploaded"
        )
        
        assert pdf.file_id == "pdf_123"
        assert pdf.subject_id == "subj_123"
        assert pdf.size == 1024000
        assert pdf.status == "uploaded"


class TestScoringCriterionModel:
    """Test ScoringCriterion domain model"""
    
    def test_scoring_criterion_creation(self):
        """Test creating a scoring criterion"""
        criterion = ScoringCriterion(
            criterion="핵심 개념 설명",
            points=8.0,
            example="예: 데이터베이스는..."
        )
        
        assert criterion.criterion == "핵심 개념 설명"
        assert criterion.points == 8.0
        assert criterion.example == "예: 데이터베이스는..."
    
    def test_scoring_criterion_without_example(self):
        """Test criterion without example"""
        criterion = ScoringCriterion(
            criterion="논리적 구조",
            points=5.0
        )
        
        assert criterion.example is None


class TestExamModels:
    """Test Exam domain models"""
    
    def test_question_creation(self):
        """Test creating a question"""
        question = Question(
            id=1,
            question="Python의 특징은?",
            type="multiple_choice",
            options=["동적 타입", "정적 타입", "컴파일 언어", "저수준 언어"],
            points=10
        )
        
        assert question.id == 1
        assert question.type == "multiple_choice"
        assert len(question.options) == 4
        assert question.points == 10
    
    def test_question_with_enhanced_fields(self):
        """Test question with new enhanced fields"""
        question = Question(
            id=1,
            question="Python의 주요 특징은?",
            type="multiple_choice",
            options=["동적 타입", "정적 타입", "컴파일 언어", "저수준 언어"],
            points=10,
            topic="Programming Languages",
            correct_answer="동적 타입",
            model_answer="Python은 동적 타입 언어입니다. 변수의 타입이 런타임에 결정됩니다.",
            keywords=None,
            scoring_rubric=None
        )
        
        assert question.topic == "Programming Languages"
        assert question.correct_answer == "동적 타입"
        assert question.model_answer is not None
        assert "동적 타입" in question.model_answer
    
    def test_short_answer_with_keywords_and_rubric(self):
        """Test short answer question with keywords and rubric"""
        rubric = [
            ScoringCriterion(criterion="핵심 개념", points=7.0),
            ScoringCriterion(criterion="예시 제시", points=5.0),
            ScoringCriterion(criterion="설명 명확성", points=3.0)
        ]
        
        question = Question(
            id=2,
            question="객체지향 프로그래밍의 주요 특징을 설명하시오.",
            type="short_answer",
            options=None,
            points=15,
            topic="OOP",
            correct_answer=None,
            model_answer="객체지향 프로그래밍은 캡슐화, 상속, 다형성을 핵심으로 하는 프로그래밍 패러다임입니다.",
            keywords=["캡슐화", "상속", "다형성"],
            scoring_rubric=rubric
        )
        
        assert question.type == "short_answer"
        assert len(question.keywords) == 3
        assert "캡슐화" in question.keywords
        assert len(question.scoring_rubric) == 3
        assert sum(c.points for c in question.scoring_rubric) == 15
    
    def test_essay_question_with_rubric(self):
        """Test essay question with detailed rubric"""
        rubric = [
            ScoringCriterion(
                criterion="주제 이해도",
                points=8.0,
                example="데이터베이스 정규화의 목적과 필요성 설명"
            ),
            ScoringCriterion(
                criterion="정규화 단계 설명",
                points=7.0,
                example="1NF, 2NF, 3NF 각각 설명"
            ),
            ScoringCriterion(
                criterion="예시 제시",
                points=5.0,
                example="구체적인 테이블 예시"
            )
        ]
        
        question = Question(
            id=3,
            question="데이터베이스 정규화에 대해 상세히 설명하시오.",
            type="essay",
            options=None,
            points=20,
            topic="Database Normalization",
            correct_answer=None,
            model_answer="데이터베이스 정규화는 중복을 제거하고 데이터 무결성을 보장하기 위한 프로세스입니다...",
            keywords=None,
            scoring_rubric=rubric
        )
        
        assert question.type == "essay"
        assert question.scoring_rubric is not None
        assert len(question.scoring_rubric) == 3
        assert question.scoring_rubric[0].example is not None
    
    def test_essay_question_no_options(self):
        """Test essay question without options"""
        question = Question(
            id=2,
            question="데이터베이스 정규화에 대해 설명하시오.",
            type="essay",
            options=None,
            points=20
        )
        
        assert question.type == "essay"
        assert question.options is None
    
    def test_exam_creation(self):
        """Test creating an exam"""
        questions = [
            Question(
                id=1,
                question="질문 1",
                type="multiple_choice",
                options=["A", "B", "C", "D"],
                points=10
            ),
            Question(
                id=2,
                question="질문 2",
                type="essay",
                options=None,
                points=20
            )
        ]
        
        exam = Exam(
            exam_id="exam_123",
            subject_id="subj_123",
            pdf_id="pdf_123",
            user_id="user_123",
            questions=questions,
            total_points=30,
            estimated_time=30,
            num_questions=2,
            difficulty="medium",
            created_at=datetime.utcnow(),
            ai_provider="gpt"
        )
        
        assert exam.exam_id == "exam_123"
        assert exam.subject_id == "subj_123"
        assert len(exam.questions) == 2
        assert exam.total_points == 30
        assert exam.difficulty == "medium"


class TestExamRequestModels:
    """Test Exam request validation"""
    
    def test_exam_generation_request_valid(self):
        """Test valid exam generation request"""
        request = ExamGenerationRequest(
            pdf_id="pdf_123",
            num_questions=5,
            difficulty="medium",
            ai_provider="gpt"
        )
        
        assert request.pdf_id == "pdf_123"
        assert request.num_questions == 5
        assert request.difficulty == "medium"
    
    def test_exam_generation_invalid_difficulty(self):
        """Test invalid difficulty value"""
        with pytest.raises(ValidationError):
            ExamGenerationRequest(
                pdf_id="pdf_123",
                num_questions=5,
                difficulty="super_hard"  # Invalid
            )
    
    def test_exam_generation_invalid_num_questions(self):
        """Test invalid number of questions"""
        # Too few
        with pytest.raises(ValidationError):
            ExamGenerationRequest(
                pdf_id="pdf_123",
                num_questions=0,
                difficulty="easy"
            )
        
        # Too many
        with pytest.raises(ValidationError):
            ExamGenerationRequest(
                pdf_id="pdf_123",
                num_questions=51,
                difficulty="easy"
            )
    
    def test_exam_generation_default_values(self):
        """Test default values for exam generation"""
        request = ExamGenerationRequest(
            pdf_id="pdf_123",
            num_questions=5
        )
        
        assert request.difficulty == "medium"  # default
        assert request.ai_provider is None  # default (set via query param or env)
    
    def test_exam_submission_request(self):
        """Test exam submission request"""
        answers = [
            AnswerSubmission(question_id=1, answer="A"),
            AnswerSubmission(question_id=2, answer="데이터베이스 정규화는...")
        ]
        
        request = ExamSubmissionRequest(
            exam_id="exam_123",
            answers=answers
        )
        
        assert request.exam_id == "exam_123"
        assert len(request.answers) == 2
        assert request.answers[0].question_id == 1


class TestGradingModels:
    """Test grading domain models"""
    
    def test_question_result_creation(self):
        """Test creating a question result"""
        result = QuestionResult(
            question_id=1,
            score=10.0,
            max_points=10,
            feedback="정답입니다."
        )
        
        assert result.question_id == 1
        assert result.score == 10.0
        assert result.max_points == 10
        assert result.feedback == "정답입니다."
    
    def test_grading_result_creation(self):
        """Test creating a grading result"""
        question_results = [
            QuestionResult(
                question_id=1,
                score=10.0,
                max_points=10,
                feedback="정답"
            ),
            QuestionResult(
                question_id=2,
                score=15.0,
                max_points=20,
                feedback="부분 정답"
            )
        ]
        
        grading = GradingResult(
            total_score=25.0,
            max_score=30.0,
            percentage=83.33,
            question_results=question_results
        )
        
        assert grading.total_score == 25.0
        assert grading.max_score == 30.0
        assert grading.percentage == 83.33
        assert len(grading.question_results) == 2


class TestBusinessRules:
    """Test business rules and constraints"""
    
    def test_subject_name_length_constraints(self):
        """Test subject name length constraints"""
        # Too short
        with pytest.raises(ValidationError):
            SubjectCreateRequest(name="")
        
        # Too long (over 100 chars)
        with pytest.raises(ValidationError):
            SubjectCreateRequest(name="A" * 101)
        
        # Valid length
        request = SubjectCreateRequest(name="A" * 50)
        assert len(request.name) == 50
    
    def test_subject_description_length(self):
        """Test subject description length constraint"""
        # Valid
        request = SubjectCreateRequest(
            name="과목",
            description="A" * 500
        )
        assert len(request.description) == 500
        
        # Too long
        with pytest.raises(ValidationError):
            SubjectCreateRequest(
                name="과목",
                description="A" * 501
            )
    
    def test_exam_points_consistency(self):
        """Test that exam total points match question points"""
        questions = [
            Question(id=1, question="Q1", type="multiple_choice", 
                    options=["A"], points=10),
            Question(id=2, question="Q2", type="essay", 
                    options=None, points=20)
        ]
        
        # Correct total
        exam = Exam(
            exam_id="exam_123",
            subject_id="subj_123",
            pdf_id="pdf_123",
            user_id="user_123",
            questions=questions,
            total_points=30,  # 10 + 20
            estimated_time=30,
            num_questions=2,
            difficulty="medium",
            created_at=datetime.utcnow()
        )
        
        # Verify
        calculated_total = sum(q.points for q in exam.questions)
        assert exam.total_points == calculated_total
    
    def test_grading_percentage_calculation(self):
        """Test grading percentage calculation"""
        result = GradingResult(
            total_score=85.0,
            max_score=100.0,
            percentage=85.0,
            question_results=[]
        )
        
        expected_percentage = (result.total_score / result.max_score) * 100
        assert result.percentage == expected_percentage

