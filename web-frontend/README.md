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
- next-intl (Client i18n)

## 다국어(i18n)

- 사용자/과목의 `language_preference`를 기반으로 `next-intl` Provider가 UI 문자열을 전환합니다.
- 번역 리소스는 `src/i18n/locales/{ko,en,ja}.json`에 있으며, 동일한 키 구조를 유지해야 합니다.
- 새 언어를 추가하려면:
  1. `src/i18n/config.ts`의 `supportedLocales` 배열에 ISO 코드를 추가합니다.
  2. `src/i18n/locales/<code>.json` 파일을 생성하여 기존 키를 모두 번역합니다.
  3. `src/i18n/messages.ts`에서 새 JSON을 import하고 `messagesByLocale`에 등록합니다.
- UI에서 지구본 아이콘을 클릭하면 언어를 즉시 변경할 수 있으며, 백엔드 `PUT /api/user/profile`을 통해 사용자 설정이 저장됩니다.
- 시간대 일관성을 위해 `NEXT_PUBLIC_I18N_TIMEZONE`(기본값 `Asia/Seoul`) 환경 변수를 설정할 수 있습니다.

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
