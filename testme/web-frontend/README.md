# test.me Web Frontend

Next.js 14 기반 웹 프론트엔드

## 환경 설정

`.env.local` 파일을 생성하고 다음 환경 변수를 설정하세요:

```env
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 실행 방법

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

개발 서버: http://localhost:3000

## 기술 스택

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- React 18
- Firebase (Authentication)
- Axios (API Client)
- React Hook Form + Zod (Form Validation)
- Zustand (State Management)

## 프로젝트 구조

```
src/
├── app/              # Next.js App Router
├── components/       # React 컴포넌트
│   ├── ui/          # UI 컴포넌트
│   ├── features/    # 기능별 컴포넌트
│   └── layouts/     # 레이아웃 컴포넌트
├── lib/             # 유틸리티
└── hooks/           # Custom Hooks
```

## TODO

- [ ] shadcn/ui 설치
- [ ] Firebase Auth 통합
- [ ] API 클라이언트 구현
- [ ] 페이지 구현 (로그인, 대시보드, PDF 관리, 시험)

