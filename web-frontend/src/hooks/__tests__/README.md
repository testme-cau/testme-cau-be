# Custom Hooks Tests

이 디렉토리는 프로젝트의 커스텀 React Hooks에 대한 테스트를 포함합니다.

## 테스트 파일

현재 `.example.ts` 확장자로 제공되는 예제 테스트 파일들:

- `useApiRequest.test.example.ts` - API 요청 hook 테스트
- (추가 예정: useSubject, usePDFs, useGroups)

## 테스트 활성화 방법

### 1. 필요한 패키지 설치

```bash
npm install --save-dev \
  jest \
  @testing-library/react \
  @testing-library/react-hooks \
  @testing-library/jest-dom \
  @testing-library/user-event \
  jest-environment-jsdom \
  @types/jest
```

### 2. Jest 설정

프로젝트 루트에 `jest.config.js` 생성 (상세 내용은 `../../../TESTING.md` 참조)

### 3. 테스트 파일 활성화

예제 파일의 확장자를 변경:

```bash
# useApiRequest 테스트 활성화
mv useApiRequest.test.example.ts useApiRequest.test.ts
```

### 4. 테스트 실행

```bash
npm test
```

## 테스트 커버리지

각 hook별로 다음 사항들을 테스트합니다:

### useApiRequest
- ✅ 초기 상태
- ✅ 성공적인 API 호출
- ✅ 로딩 상태 관리
- ✅ 에러 처리
- ✅ 커스텀 에러 메시지
- ✅ 연속적인 요청 처리

### useSubject (예정)
- 컴포넌트 마운트 시 자동 fetch
- Subject 업데이트
- 에러 처리

### usePDFs (예정)
- PDF 목록 로딩
- PDF 업로드
- PDF 삭제
- PDF 다운로드

### useGroups (예정)
- 그룹 목록 로딩
- 그룹 생성
- 그룹 업데이트
- 그룹 삭제

## 추가 정보

자세한 테스트 작성 가이드는 프로젝트 루트의 `TESTING.md`를 참조하세요.

