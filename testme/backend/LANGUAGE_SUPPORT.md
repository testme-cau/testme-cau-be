# 다국어 지원 (Multi-Language Support)

## 개요

test.me는 이제 유저별/과목별 언어 설정을 지원합니다. AI가 지정된 언어로 시험 문제를 생성하여 글로벌 사용자를 위한 맞춤형 경험을 제공합니다.

**지원 버전**: 2.2.0  
**업데이트 날짜**: 2025-11-08

## 지원 언어

ISO 639-1 코드를 사용하여 14개 주요 언어를 지원합니다:

| 코드 | 언어 | English Name |
|------|------|--------------|
| ko | 한국어 | Korean |
| en | 영어 | English |
| ja | 일본어 | Japanese |
| zh | 중국어 | Chinese |
| es | 스페인어 | Spanish |
| fr | 프랑스어 | French |
| de | 독일어 | German |
| it | 이탈리아어 | Italian |
| pt | 포르투갈어 | Portuguese |
| ru | 러시아어 | Russian |
| ar | 아랍어 | Arabic |
| hi | 힌디어 | Hindi |
| vi | 베트남어 | Vietnamese |
| th | 태국어 | Thai |

## 언어 우선순위

시험 문제 생성 시 다음 순서로 언어를 결정합니다:

```
1. 과목(Subject)의 language_preference
2. 유저(User)의 language_preference
3. 기본값: 한국어(ko)
```

### 예시

```python
# 시나리오 1: 과목에 언어 설정이 있는 경우
User: language_preference = "ko"
Subject: language_preference = "en"
→ 결과: 영어(en)로 문제 생성

# 시나리오 2: 과목에 언어 설정이 없는 경우
User: language_preference = "ja"
Subject: language_preference = None
→ 결과: 일본어(ja)로 문제 생성

# 시나리오 3: 둘 다 설정이 없는 경우
User: language_preference = None (or "ko" by default)
Subject: language_preference = None
→ 결과: 한국어(ko)로 문제 생성
```

## API 사용법

### 0. 지원 언어 목록 조회 (공개)

```http
GET /api/user/languages
```

**인증 불필요** - 공개 엔드포인트

**응답 예시**:
```json
{
  "success": true,
  "languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "flag": "🇰🇷"
    },
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "flag": "🇺🇸"
    },
    {
      "code": "ja",
      "name": "Japanese",
      "native_name": "日本語",
      "flag": "🇯🇵"
    }
    // ... 11 more languages
  ],
  "count": 14
}
```

**사용 사례**: 프론트엔드 드롭다운, 언어 선택 UI

### 1. 유저 프로필 조회

```http
GET /api/user/profile
Authorization: Bearer <firebase-id-token>
```

**응답 예시**:
```json
{
  "success": true,
  "user": {
    "uid": "user123",
    "email": "user@example.com",
    "display_name": "홍길동",
    "language_preference": "ko",
    "created_at": "2025-11-08T00:00:00Z"
  }
}
```

### 2. 유저 언어 설정 업데이트

```http
PUT /api/user/profile
Authorization: Bearer <firebase-id-token>
Content-Type: application/json

{
  "language_preference": "en"
}
```

**응답**:
```json
{
  "success": true,
  "message": "User profile updated successfully"
}
```

### 3. 과목 생성 (언어 설정 포함)

```http
POST /api/subjects
Authorization: Bearer <firebase-id-token>
Content-Type: application/json

{
  "name": "Database Systems",
  "description": "Advanced database course",
  "semester": "2025-1",
  "year": 2025,
  "color": "#3498db",
  "language_preference": "en"
}
```

### 4. 과목 언어 설정 업데이트

```http
PUT /api/subjects/{subject_id}
Authorization: Bearer <firebase-id-token>
Content-Type: application/json

{
  "language_preference": "ja"
}
```

### 5. 시험 문제 생성 (자동 언어 적용)

```http
POST /api/subjects/{subject_id}/exams/generate
Authorization: Bearer <firebase-id-token>
Content-Type: application/json

{
  "pdf_id": "pdf_123",
  "num_questions": 10,
  "difficulty": "medium"
}
```

시스템이 자동으로 과목 또는 유저의 언어 설정을 적용하여 문제를 생성합니다.

## 데이터 모델

### User 모델

```python
class User(BaseModel):
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    language_preference: str = "ko"  # 기본값: 한국어
```

### Subject 모델

```python
class Subject(BaseModel):
    subject_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    semester: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    language_preference: Optional[str] = None  # 유저 설정 재정의
    created_at: datetime
    updated_at: Optional[datetime] = None
```

## AI 프롬프트 동작

언어가 설정되면 AI 서비스는 다음과 같이 동작합니다:

### GPT 및 Gemini 프롬프트

```
LANGUAGE REQUIREMENT:
ALL questions, options, and answers MUST be in {Language Name}.
Generate questions and answers entirely in {Language Name}.

QUALITY REQUIREMENTS:
1. Test UNDERSTANDING and APPLICATION, not just memorization
2. Questions must cover different topics from the PDF
3. Clear, unambiguous wording
4. Professional academic language
```

### 예시: 영어 시험 생성

**입력**:
- PDF: 한국어 데이터베이스 강의 자료
- language_preference: "en"

**AI 동작**:
- PDF 내용을 분석 (한국어)
- 질문, 선택지, 답변을 **영어**로 생성

**출력**:
```json
{
  "questions": [
    {
      "id": 1,
      "question": "What is the primary purpose of database normalization?",
      "type": "multiple_choice",
      "options": [
        "To increase data redundancy",
        "To reduce data redundancy",
        "To slow down queries",
        "To make database larger"
      ],
      "correct_answer": "To reduce data redundancy",
      "model_answer": "Database normalization aims to reduce data redundancy..."
    }
  ]
}
```

## 유효성 검증

언어 코드는 자동으로 검증됩니다:

```python
# 유효한 언어 코드
request = UserUpdateRequest(language_preference="en")  # ✅
request = UserUpdateRequest(language_preference="EN")  # ✅ (자동 소문자 변환)

# 유효하지 않은 언어 코드
request = UserUpdateRequest(language_preference="invalid")  # ❌ ValidationError
```

## Firestore 데이터 구조

### Users Collection

```
users/{user_id}
{
  "uid": "user123",
  "email": "user@example.com",
  "display_name": "John Doe",
  "language_preference": "en",
  "created_at": Timestamp,
  "updated_at": Timestamp
}
```

### Subjects Subcollection

```
users/{user_id}/subjects/{subject_id}
{
  "subject_id": "subj123",
  "user_id": "user123",
  "name": "Database Systems",
  "language_preference": "en",  // Override user's preference
  "created_at": Timestamp,
  "updated_at": Timestamp
}
```

## 테스트

언어 지원 기능은 포괄적인 테스트로 검증됩니다:

```bash
# 언어 지원 테스트 실행
pytest tests/test_language_support.py -v
```

**테스트 커버리지**:
- ✅ 언어 코드 검증
- ✅ 대소문자 무시
- ✅ 유효하지 않은 언어 거부
- ✅ 도메인 모델 기본값
- ✅ AI 서비스 인터페이스
- ✅ 14개 지원 언어

## 사용 사례

### 사례 1: 글로벌 대학

한국 대학에서 영어 강의를 운영하는 경우:

```javascript
// 과목 생성 시 영어로 설정
POST /api/subjects
{
  "name": "Advanced Database Systems",
  "language_preference": "en"
}

// 해당 과목의 모든 시험은 영어로 생성됨
```

### 사례 2: 유학생 지원

한국어를 모르는 일본인 유학생:

```javascript
// 유저 프로필에서 일본어로 설정
PUT /api/user/profile
{
  "language_preference": "ja"
}

// 모든 과목(별도 설정 없는 경우)의 시험이 일본어로 생성됨
```

### 사례 3: 다양한 언어 과목 관리

한 유저가 여러 언어로 공부하는 경우:

```javascript
// 유저 기본 언어: 한국어
User: language_preference = "ko"

// 과목별 언어 설정
Subject 1: "한국사" - language_preference = null → 한국어
Subject 2: "English Literature" - language_preference = "en" → 영어
Subject 3: "日本語" - language_preference = "ja" → 일본어
```

## 제한사항

1. **PDF 언어 자동 감지 없음**: PDF의 언어는 자동으로 감지되지 않습니다. 유저가 명시적으로 설정해야 합니다.

2. **번역 기능 없음**: 이미 생성된 시험을 다른 언어로 번역하는 기능은 없습니다. 언어를 변경하려면 시험을 다시 생성해야 합니다.

3. **혼합 언어 미지원**: 하나의 시험에서 여러 언어를 혼합할 수 없습니다.

## 향후 계획

- [ ] 자동 언어 감지 (PDF 내용 기반)
- [ ] 추가 언어 지원 확대
- [ ] 시험 번역 기능
- [ ] 언어별 난이도 조정
- [ ] 다국어 UI 지원

## 마이그레이션 가이드

기존 사용자를 위한 마이그레이션:

### 1. 기존 유저

기존 유저는 자동으로 `language_preference = "ko"` 기본값을 가집니다.

### 2. 기존 과목

기존 과목은 `language_preference = null`이며, 유저의 언어 설정을 따릅니다.

### 3. 업데이트 필요 없음

기존 시스템은 변경 없이 계속 작동합니다 (기본 한국어).

## 문제 해결

### 문제: 시험이 잘못된 언어로 생성됨

**해결책**:
1. 과목의 `language_preference` 확인
2. 유저의 `language_preference` 확인
3. 두 설정 모두 확인하여 우선순위 이해

### 문제: 언어 코드 검증 실패

**해결책**:
- 지원되는 14개 언어 코드 중 하나를 사용
- 대소문자는 상관없음 (자동 변환)

### 문제: AI가 요청한 언어로 생성하지 않음

**해결책**:
- AI 모델의 제약으로 인해 드물게 발생 가능
- 재생성 시도
- 다른 AI 제공자(GPT ↔ Gemini) 시도

## 기술 세부사항

### 구현된 파일

- `app/models/domain.py`: User, Subject 모델 확장
- `app/models/requests.py`: UserUpdateRequest, 언어 검증 추가
- `app/services/ai_service_interface.py`: language 파라미터 추가
- `app/services/gpt_service.py`: 언어별 프롬프트 구현
- `app/services/gemini_service.py`: 언어별 프롬프트 구현
- `app/routes/user.py`: 유저 프로필 및 언어 목록 엔드포인트 (신규)
- `app/routes/exam.py`: 언어 우선순위 로직
- `app/utils/language_utils.py`: 언어 상수 및 유틸리티 함수 (신규)
- `main.py`: user 라우터 등록
- `tests/test_language_support.py`: 포괄적 테스트 (신규)
- `tests/test_language_endpoints.py`: 언어 API 엔드포인트 테스트 (신규)

### 테스트 결과

```
105 passed, 5 skipped
26 new tests for language support (14 + 12)
- test_language_support.py: 14 tests
- test_language_endpoints.py: 12 tests
```

## 라이선스

MIT License

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-11-08  
**작성자**: test.me Development Team

