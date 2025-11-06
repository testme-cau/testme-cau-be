# test.me Web Frontend

Next.js 14 기반 웹 프론트엔드

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
- Tailwind CSS
- React 18

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

