# test.me - AI-Powered Exam Generation Platform

AI 기반 시험 생성 및 채점 플랫폼

## 프로젝트 구조

```
testme/
├── backend/          # FastAPI 백엔드
│   ├── main.py
│   ├── app/
│   ├── tests/
│   └── README.md
│
└── web-frontend/     # Next.js 웹 프론트엔드
    ├── src/
    ├── public/
    └── package.json
```

## Quick Start

### 🚀 한 번에 실행 (권장)

```bash
# 초기 설정 (최초 1회만)
./scripts/setup-dev.sh

# 개발 서버 실행
./scripts/dev.sh

# 서버 종료
./scripts/stop-dev.sh
```

### 개별 실행

#### 백엔드 (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

백엔드 API: http://localhost:5000  
API 문서: http://localhost:5000/docs

#### 웹 프론트엔드 (Next.js)

```bash
cd web-frontend
npm install
npm run dev
```

프론트엔드: http://localhost:3000

## 기술 스택

### 백엔드
- FastAPI 0.109.0
- Python 3.11+
- Firebase (Auth, Firestore, Storage)
- OpenAI GPT-5 / Google Gemini

### 프론트엔드
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Firebase Auth

## 주요 기능

- 🔐 Firebase OAuth 2.0 인증
- 📄 PDF 업로드 및 관리
- 🤖 AI 기반 시험 문제 생성 (GPT/Gemini 선택 가능)
- ✅ 자동 채점 및 피드백
- 📊 시험 결과 분석

## 개발 문서

- Backend: `backend/AGENTS.md`, `backend/README.md`
- Frontend: `web-frontend/README.md` (생성 예정)

## 라이선스

MIT License

