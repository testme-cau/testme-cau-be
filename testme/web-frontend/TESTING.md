# Frontend Testing Guide

이 문서는 test.me 프론트엔드의 테스트 전략과 설정 가이드를 제공합니다.

## 테스트 스택

- **Jest**: JavaScript 테스트 프레임워크
- **React Testing Library**: React 컴포넌트 테스트
- **@testing-library/react-hooks**: React Hooks 테스트

## 설치

테스트를 실행하려면 다음 패키지들을 설치해야 합니다:

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event @testing-library/react-hooks jest-environment-jsdom
npm install --save-dev @types/jest
```

## Jest 설정

`jest.config.js` 파일을 프로젝트 루트에 생성:

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // next.config.js와 .env 파일의 경로 제공
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
  ],
}

module.exports = createJestConfig(customJestConfig)
```

## Jest Setup

`jest.setup.js` 파일 생성:

```javascript
import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
    }
  },
  useSearchParams() {
    return {
      get: jest.fn(),
    }
  },
  usePathname() {
    return ''
  },
}))

// Mock Firebase
jest.mock('firebase/app', () => ({
  initializeApp: jest.fn(),
  getApps: jest.fn(() => []),
  getApp: jest.fn(),
}))

jest.mock('firebase/auth', () => ({
  getAuth: jest.fn(),
  signInWithPopup: jest.fn(),
  GoogleAuthProvider: jest.fn(),
}))
```

## package.json에 스크립트 추가

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

## 테스트 파일 구조

```
src/
├── hooks/
│   ├── __tests__/
│   │   ├── useApiRequest.test.ts
│   │   ├── useSubject.test.ts
│   │   ├── usePDFs.test.ts
│   │   └── useGroups.test.ts
│   ├── useApiRequest.ts
│   ├── useSubject.ts
│   ├── usePDFs.ts
│   └── useGroups.ts
└── components/
    └── __tests__/
        └── ...
```

## Custom Hooks 테스트 예제

### useApiRequest 테스트

```typescript
import { renderHook, act } from '@testing-library/react-hooks'
import { useApiRequest } from '../useApiRequest'

describe('useApiRequest', () => {
  it('should handle successful API call', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockApiCall = jest.fn().mockResolvedValue({ data: 'test' })
    
    await act(async () => {
      await result.current.request(mockApiCall, 'Success message')
    })
    
    expect(result.current.data).toEqual({ data: 'test' })
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
  })
  
  it('should handle API error', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockApiCall = jest.fn().mockRejectedValue(new Error('API Error'))
    
    await act(async () => {
      await result.current.request(mockApiCall, undefined, 'Error message')
    })
    
    expect(result.current.data).toBe(null)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe('Error message')
  })
})
```

### useSubject 테스트

```typescript
import { renderHook, act } from '@testing-library/react-hooks'
import { useSubject } from '../useSubject'
import * as subjectsApi from '@/lib/api/subjects'

jest.mock('@/lib/api/subjects')

describe('useSubject', () => {
  it('should fetch subject on mount', async () => {
    const mockSubject = {
      subject_id: '123',
      name: 'Test Subject',
      user_id: 'user123',
      created_at: new Date().toISOString(),
    }
    
    ;(subjectsApi.getSubject as jest.Mock).mockResolvedValue(mockSubject)
    
    const { result, waitForNextUpdate } = renderHook(() => useSubject('123'))
    
    await waitForNextUpdate()
    
    expect(result.current.subject).toEqual(mockSubject)
    expect(result.current.loading).toBe(false)
  })
})
```

## 테스트 실행

```bash
# 모든 테스트 실행
npm test

# watch 모드로 실행
npm run test:watch

# 커버리지 리포트 생성
npm run test:coverage
```

## 테스트 작성 원칙

### 1. Arrange-Act-Assert (AAA) 패턴

```typescript
it('should do something', () => {
  // Arrange: 테스트 환경 설정
  const input = 'test'
  
  // Act: 동작 실행
  const result = doSomething(input)
  
  // Assert: 결과 검증
  expect(result).toBe('expected')
})
```

### 2. Mock 사용

- 외부 API 호출은 항상 mock
- Firebase 인증은 jest.setup.js에서 전역 mock
- 컴포넌트 테스트 시 하위 컴포넌트 mock 고려

### 3. 테스트 격리

- 각 테스트는 독립적으로 실행 가능해야 함
- `beforeEach`/`afterEach`로 상태 초기화

### 4. 의미있는 테스트 작성

- 구현이 아닌 동작을 테스트
- 사용자 관점에서 테스트
- Edge case 포함

## 현재 구현된 Hooks

1. **useApiRequest**: API 호출 및 상태 관리
   - 성공/실패 처리
   - 로딩 상태
   - 토스트 메시지

2. **useSubject**: Subject 데이터 관리
   - 자동 fetching
   - 업데이트 함수

3. **usePDFs**: PDF 목록 관리
   - 업로드, 다운로드, 삭제
   - 자동 새로고침

4. **useGroups**: 그룹 관리
   - CRUD 작업
   - 상태 동기화

## 참고 자료

- [Jest 문서](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Hooks](https://react-hooks-testing-library.com/)
- [Next.js Testing](https://nextjs.org/docs/testing)

