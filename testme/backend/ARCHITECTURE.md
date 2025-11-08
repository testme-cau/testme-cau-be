# Backend Architecture

## Overview

test.me 백엔드는 **Repository-Service-Controller** 패턴을 사용하여 계층화된 아키텍처를 구현합니다.

## Architecture Layers

```
┌─────────────────────────────────────┐
│         Routes (Controllers)        │  ← HTTP 요청/응답 처리
├─────────────────────────────────────┤
│          Services Layer             │  ← 비즈니스 로직
├─────────────────────────────────────┤
│        Repositories Layer           │  ← 데이터 접근 추상화
├─────────────────────────────────────┤
│     Firebase / External APIs        │  ← 외부 서비스
└─────────────────────────────────────┘
```

## Directory Structure

```
backend/app/
├── dependencies/          # FastAPI 의존성 주입
│   ├── auth.py           # 인증 의존성
│   └── service.py        # 서비스 의존성
│
├── middleware/           # 미들웨어
│   └── logging.py        # 요청/응답 로깅
│
├── models/               # Pydantic 모델
│   ├── domain.py         # 도메인 모델
│   ├── requests.py       # 요청 스키마
│   └── responses.py      # 응답 스키마
│
├── repositories/         # 데이터 접근 계층
│   ├── base.py           # BaseRepository (공통 CRUD)
│   ├── subject.py        # SubjectRepository
│   ├── pdf.py            # PDFRepository
│   ├── exam.py           # ExamRepository
│   └── group.py          # GroupRepository
│
├── routes/               # API 라우트 (컨트롤러)
│   ├── subject.py        # 과목 엔드포인트
│   ├── pdf.py            # PDF 엔드포인트
│   ├── exam.py           # 시험 엔드포인트
│   └── ...
│
├── services/             # 비즈니스 로직 계층
│   ├── subject_service.py    # 과목 비즈니스 로직
│   ├── pdf_service.py        # PDF 비즈니스 로직
│   ├── exam_service.py       # 시험 비즈니스 로직
│   ├── ai_service_interface.py  # AI 서비스 인터페이스
│   ├── gpt_service.py        # GPT 구현
│   └── gemini_service.py     # Gemini 구현
│
└── utils/                # 유틸리티
    ├── exam_validator.py  # 시험 검증
    └── file_utils.py      # 파일 유틸리티
```

## Layer Responsibilities

### 1. Routes Layer (Controllers)

**책임**:
- HTTP 요청 파라미터 추출
- 의존성 주입을 통한 서비스 획득
- 서비스 메서드 호출
- HTTP 응답 반환

**예시**:
```python
@router.post("", response_model=SubjectResponse)
async def create_subject(
    request: SubjectCreateRequest,
    user: Dict = Depends(get_current_user),
    subject_service: SubjectService = Depends(get_subject_service)
):
    subject = subject_service.create_subject(user['uid'], request)
    return SubjectResponse(success=True, subject=subject)
```

### 2. Services Layer

**책임**:
- 비즈니스 로직 구현
- 여러 Repository 조율
- 데이터 검증 및 변환
- 트랜잭션 관리

**예시**:
```python
class SubjectService:
    def __init__(self, subject_repo: SubjectRepository = None):
        self.repo = subject_repo or SubjectRepository()
    
    def create_subject(self, user_id: str, request: SubjectCreateRequest) -> Subject:
        # 비즈니스 로직: 데이터 검증, 변환, 저장
        subject_data = {...}
        created_data = self.repo.create(subject_data, user_id)
        return Subject(**created_data)
```

### 3. Repositories Layer

**책임**:
- Firestore 데이터 접근 추상화
- CRUD 작업 구현
- 쿼리 로직
- 데이터베이스 에러 처리

**Base Repository**:
```python
class BaseRepository(ABC, Generic[T]):
    def get_by_id(self, doc_id: str, user_id: Optional[str] = None)
    def get_by_id_with_ownership(self, doc_id: str, user_id: str)
    def list_by_user(self, user_id: str, ...)
    def create(self, data: Dict, user_id: Optional[str] = None)
    def update(self, doc_id: str, data: Dict, ...)
    def delete(self, doc_id: str, user_id: Optional[str] = None)
```

## Key Design Patterns

### 1. Repository Pattern

모든 데이터 접근 로직을 Repository 계층에 캡슐화:

- **장점**: 데이터 소스 변경 시 Repository만 수정
- **테스트**: Repository 를 Mock하여 Service 테스트 용이

### 2. Dependency Injection

FastAPI의 `Depends()`를 사용한 의존성 주입:

```python
# dependencies/service.py
def get_subject_service() -> SubjectService:
    return SubjectService()

# routes/subject.py
@router.post("...")
async def create_subject(
    subject_service: SubjectService = Depends(get_subject_service)
):
    ...
```

### 3. Strategy Pattern (AI Services)

여러 AI 제공자를 동일한 인터페이스로 추상화:

```python
class AIServiceInterface(ABC):
    @abstractmethod
    def generate_exam_from_pdf(...)
    
    @property
    @abstractmethod
    def provider_name(self) -> str
```

## Data Flow Example

### Subject 생성 플로우

```
1. Client Request
   POST /api/subjects
   Body: {name: "수학", ...}
   Header: Authorization: Bearer <token>
   
2. Route (subject.py)
   ├─ get_current_user() → 사용자 인증
   ├─ get_subject_service() → 서비스 주입
   └─ create_subject() 호출
   
3. Service (subject_service.py)
   ├─ 데이터 검증 및 변환
   ├─ SubjectRepository.create() 호출
   └─ Subject 도메인 모델 반환
   
4. Repository (subject.py)
   ├─ BaseRepository.create() 사용
   ├─ Firestore에 저장
   └─ 생성된 데이터 반환
   
5. Response
   SubjectResponse(success=True, subject=...)
```

## Error Handling

### 계층별 에러 처리

- **Repository**: Firestore 에러 → HTTPException으로 변환
- **Service**: 비즈니스 로직 에러 → HTTPException
- **Route**: HTTPException 자동 처리 (FastAPI)

## Authentication & Authorization

1. **인증**: `get_current_user()` 의존성이 Firebase ID 토큰 검증
2. **권한**: Repository의 `get_by_id_with_ownership()` 메서드로 소유권 확인

## Logging

- **Middleware**: 모든 요청/응답 로깅
- **Format**: `timestamp - name - level - message`
- **Services**: 중요 비즈니스 로직 이벤트 로깅

## Testing Strategy

### 단위 테스트
- Repository: Firestore mock
- Service: Repository mock  
- AI Service: API mock

### 통합 테스트
- E2E 테스트: TestClient 사용
- Firebase Emulator 활용

## Performance Considerations

1. **Firestore 최적화**:
   - 필요한 필드만 쿼리
   - 적절한 인덱스 사용

2. **캐싱**: 향후 Redis 도입 고려

3. **비동기 처리**: FastAPI async/await 활용

## Future Improvements

1. **캐싱 레이어**: Redis 도입
2. **이벤트 시스템**: 도메인 이벤트 발행/구독
3. **CQRS**: 읽기/쓰기 분리
4. **배치 작업**: Celery 또는 Cloud Tasks

## Migration Guide

### 기존 코드를 새 아키텍처로 마이그레이션

1. **Repository 생성**: 데이터 접근 로직을 Repository로 이동
2. **Service 생성**: 비즈니스 로직을 Service로 이동
3. **Route 단순화**: Service 호출만 남기기
4. **테스트 작성**: 각 계층 테스트 추가

## References

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

