# test.me - AI 시험 생성 플랫폼 - 에이전트 문서

> AI 에이전트와 개발자를 위한 아키텍처 가이드

## 프로젝트 개요

**test.me**는 AI 기반 시험 생성 및 채점 플랫폼입니다. PDF 강의 자료를 분석하여 시험 문제를 자동 생성하고 답안을 채점합니다.

### 시스템 아키텍처

```
Web/Mobile Client ──► FastAPI Backend ──► Firebase (Auth/DB/Storage)
                                      └──► AI Services (GPT/Gemini)
```

### 핵심 워크플로우

1. **인증**: Firebase OAuth 2.0
2. **업로드**: PDF를 Firebase Storage에 저장
3. **AI 처리**: PDF를 AI 서비스로 전송
4. **문제 생성**: AI가 PDF 분석 후 문제 생성
5. **자동 채점**: AI가 원본 PDF 참조하여 채점

## 기술 스택

### 백엔드

- FastAPI (Python)
- Firebase (Auth, Firestore, Storage)
- OpenAI / Google Generative AI

### 프론트엔드

- Next.js (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui

## 프로젝트 구조

```
testme/
├── backend/           # FastAPI 백엔드
│   ├── app/
│   │   ├── models/        # Pydantic 모델 (domain, requests, responses)
│   │   ├── routes/        # API 엔드포인트 (pdf, exam)
│   │   ├── services/      # 비즈니스 로직 (AI, Firebase)
│   │   ├── dependencies/  # FastAPI 의존성 주입
│   │   └── utils/         # 유틸리티
│   └── tests/         # pytest 테스트
│
├── web-frontend/      # Next.js 프론트엔드
│   └── src/
│       ├── app/           # App Router 페이지
│       ├── components/    # React 컴포넌트
│       └── lib/           # 유틸리티
│
└── scripts/           # 개발 스크립트
```

## 핵심 아키텍처

### Strategy Pattern for AI Services

AI 서비스는 Strategy Pattern으로 추상화되어 여러 제공자(GPT, Gemini 등)를 자유롭게 전환할 수 있습니다.

```python
class AIServiceInterface(ABC):
    @abstractmethod
    def generate_exam_from_pdf(...)

    @abstractmethod
    def grade_exam_with_pdf(...)

# 구현체: GPTService, GeminiService
# 팩토리로 선택: get_ai_service(provider)
```

### API 설계 원칙

- Firebase ID 토큰 기반 인증
- RESTful 엔드포인트: `/api/pdf/*`, `/api/exam/*`
- Pydantic 모델로 요청/응답 검증
- FastAPI 의존성 주입 패턴

### 프론트엔드 패턴

- Next.js App Router
- Server-Side Rendering
- shadcn/ui 컴포넌트 기반

## 개발 원칙

### 환경 설정

환경 변수, 개발 서버 실행 등 구체적인 설정은 `README.md`를 참조하세요.

**핵심 원칙**:

- 민감 정보는 `.env`에 저장 (절대 커밋 금지)
- Firebase 인증 키는 `serviceAccountKey.json` 사용
- AI 제공자는 환경 변수로 선택 가능

### 코드 작성 패턴

**백엔드 (FastAPI)**:

- Pydantic 모델로 데이터 검증
- 의존성 주입으로 인증/AI 서비스 제공
- 라우터 → 서비스 → 모델 계층 구조

**프론트엔드 (Next.js)**:

- App Router 기반 라우팅
- 컴포넌트 기반 개발
- TypeScript 필수

### 확장 가이드

**새 AI 제공자 추가**:

1. `AIServiceInterface` 구현
2. 팩토리에 등록
3. 환경 변수 추가

**새 API 추가**:

1. Pydantic 모델 정의
2. 라우터 작성
3. 테스트 추가

## 보안 원칙

**절대 커밋 금지**:

- `.env` 파일
- `serviceAccountKey.json`
- 모든 API 키

**핵심 보안 전략**:

- Firebase Admin SDK 토큰 검증
- Pydantic 입력 검증
- 프로덕션: HTTPS 필수
- 클라이언트: API 키 노출 금지

## 배포

- **백엔드**: Docker 컨테이너 (FastAPI + Uvicorn)
- **프론트엔드**: Vercel (Next.js SSR)
- **데이터베이스**: Firebase (Firestore + Storage)

## 테스팅

백엔드는 pytest 사용. 구체적인 테스트 명령어는 `backend/README.md` 참조.

## 참고 문서

- **설정 및 실행**: `README.md`
- **백엔드 상세**: `backend/README.md`, `backend/AGENTS.md`
- **API 문서**: FastAPI Swagger UI (`/docs`)

**최종 업데이트**: 2025-11-07
