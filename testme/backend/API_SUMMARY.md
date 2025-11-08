# API 엔드포인트 요약

## 인증 없이 접근 가능 (Public)

### GET `/`
웰컴 메시지

### GET `/health`
헬스 체크

### GET `/api/health`
API 헬스 체크

### GET `/api/user/languages`
**지원 언어 목록 조회**

**응답**:
```json
{
  "success": true,
  "languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "flag": "🇰🇷"
    }
    // ... 14개 언어
  ],
  "count": 14
}
```

---

## 인증 필요 (Firebase ID Token)

모든 하위 엔드포인트는 `Authorization: Bearer <token>` 헤더 필요

### 유저 관리 (`/api/user`)

#### GET `/api/user/profile`
유저 프로필 조회

#### PUT `/api/user/profile`
유저 프로필 업데이트 (언어 설정 포함)

**요청**:
```json
{
  "display_name": "홍길동",
  "language_preference": "ko"
}
```

---

### 과목 관리 (`/api/subjects`)

#### POST `/api/subjects`
과목 생성 (언어 설정 포함)

**요청**:
```json
{
  "name": "Database Systems",
  "description": "...",
  "semester": "2025-1",
  "year": 2025,
  "color": "#3498db",
  "language_preference": "en"
}
```

#### GET `/api/subjects`
과목 목록 조회

#### GET `/api/subjects/{subject_id}`
특정 과목 조회

#### PUT `/api/subjects/{subject_id}`
과목 업데이트 (언어 변경 가능)

#### DELETE `/api/subjects/{subject_id}`
과목 삭제 (연관된 PDF, 시험 모두 삭제)

---

### PDF 관리 (`/api/subjects/{subject_id}/pdfs`)

#### POST `/api/subjects/{subject_id}/pdfs/upload`
PDF 업로드

#### GET `/api/subjects/{subject_id}/pdfs`
과목별 PDF 목록

#### GET `/api/subjects/{subject_id}/pdfs/{pdf_id}/download`
PDF 다운로드 (signed URL로 리다이렉트)

#### DELETE `/api/subjects/{subject_id}/pdfs/{pdf_id}`
PDF 삭제

---

### 시험 관리 (`/api/subjects/{subject_id}/exams`)

#### POST `/api/subjects/{subject_id}/exams/generate`
**시험 문제 생성 (자동 언어 적용)**

**요청**:
```json
{
  "pdf_id": "pdf_123",
  "num_questions": 10,
  "difficulty": "medium"
}
```

**동작**:
- 과목의 `language_preference` 확인
- 없으면 유저의 `language_preference` 사용
- 둘 다 없으면 기본값(ko) 사용
- AI가 해당 언어로 문제 생성

**응답**:
```json
{
  "success": true,
  "exam": {
    "exam_id": "...",
    "questions": [
      {
        "id": 1,
        "question": "What is...?",
        "type": "multiple_choice",
        "options": [...],
        "correct_answer": "...",
        "model_answer": "...",
        "points": 10
      }
    ],
    "total_points": 100,
    "estimated_time": 60
  }
}
```

#### GET `/api/subjects/{subject_id}/exams`
과목별 시험 목록

#### GET `/api/subjects/{subject_id}/exams/{exam_id}`
특정 시험 조회

#### POST `/api/subjects/{subject_id}/exams/{exam_id}/grade`
시험 채점

---

## 언어 지원

### 지원 언어 (14개)
ko, en, ja, zh, es, fr, de, it, pt, ru, ar, hi, vi, th

### 언어 우선순위
1. 과목의 `language_preference`
2. 유저의 `language_preference`
3. 기본값 (ko)

### 예시

```javascript
// 시나리오 1: 과목별 언어 설정
User: language_preference = "ko"
Subject: language_preference = "en"
→ 영어로 시험 생성

// 시나리오 2: 유저 언어 사용
User: language_preference = "ja"
Subject: language_preference = null
→ 일본어로 시험 생성

// 시나리오 3: 기본값
User: language_preference = null
Subject: language_preference = null
→ 한국어로 시험 생성
```

---

## 에러 응답

모든 에러는 다음 형식:

```json
{
  "detail": "Error message"
}
```

### 주요 상태 코드
- 200: 성공
- 201: 생성 성공
- 400: 잘못된 요청
- 401: 인증 필요
- 403: 권한 없음
- 404: 리소스 없음
- 500: 서버 에러

---

**버전**: 2.2.0  
**최종 업데이트**: 2025-11-08



