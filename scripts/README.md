# 개발 스크립트

개발 환경 설정 및 서버 실행을 위한 스크립트 모음

## 스크립트 목록

### `setup-dev.sh`
초기 개발 환경 설정 스크립트

**실행 방법:**
```bash
./scripts/setup-dev.sh
```

**기능:**
- Python virtual environment 생성
- Backend 의존성 설치
- Frontend 의존성 설치
- 환경 변수 파일 확인 및 안내

**최초 1회만 실행하면 됩니다.**

---

### `dev.sh` / `dev.bat`
개발 서버 실행 스크립트 (macOS/Linux, Windows)

**실행 방법:**
```bash
# macOS/Linux
./scripts/dev.sh

# Windows
scripts\dev.bat
```

**기능:**
- Backend (FastAPI) 서버 실행: http://localhost:5000
- Frontend (Next.js) 서버 실행: http://localhost:3000
- 양쪽 서버의 로그를 실시간으로 표시
- Ctrl+C로 모든 서버 종료

---

### `stop-dev.sh`
실행 중인 개발 서버 강제 종료 스크립트

**실행 방법:**
```bash
./scripts/stop-dev.sh
```

**기능:**
- 포트 5000에서 실행 중인 Backend 서버 종료
- 포트 3000에서 실행 중인 Frontend 서버 종료
- 관련된 모든 프로세스 정리

---

## 사용 순서

### 1. 최초 설정

```bash
# 1. 초기 환경 설정
./scripts/setup-dev.sh

# 2. Backend 환경 변수 설정
cd backend
cp .env.example .env
# .env 파일 편집 (SECRET_KEY, FIREBASE_STORAGE_BUCKET, OPENAI_API_KEY 등)

# 3. Firebase 서비스 계정 키 복사
# serviceAccountKey.json을 backend/ 디렉토리에 복사

# 4. Frontend 환경 변수 설정
cd ../web-frontend
# .env.local 파일 생성 및 Firebase 설정 추가
```

### 2. 개발 서버 실행

```bash
# 프로젝트 루트에서
./scripts/dev.sh
```

### 3. 서버 접속

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API 문서**: http://localhost:5000/docs

### 4. 서버 종료

**방법 1**: `Ctrl+C` (권장)
- dev.sh 실행 중인 터미널에서 Ctrl+C 누르기
- 모든 서버가 자동으로 종료됨

**방법 2**: 강제 종료 스크립트
```bash
./scripts/stop-dev.sh
```

---

## 로그 확인

개발 서버 실행 중에는 양쪽 서버의 로그가 실시간으로 표시됩니다.

별도로 로그를 확인하려면:

```bash
# Backend 로그
tail -f /tmp/backend.log

# Frontend 로그
tail -f /tmp/frontend.log
```

---

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# 실행 중인 서버 종료
./scripts/stop-dev.sh

# 또는 수동으로 포트 확인 및 종료
lsof -ti:5000  # Backend 포트
lsof -ti:3000  # Frontend 포트
```

### 의존성 오류가 발생하는 경우

```bash
# 다시 설정 스크립트 실행
./scripts/setup-dev.sh
```

### Python venv 문제

```bash
# venv 삭제 후 재생성
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node modules 문제

```bash
# node_modules 삭제 후 재설치
cd web-frontend
rm -rf node_modules
npm install
```

---

## Windows 사용자

Windows에서는 `dev.bat`을 사용하세요:

```cmd
REM 개발 서버 실행
scripts\dev.bat
```

**참고**: 
- Windows에서는 Backend와 Frontend가 각각 별도의 CMD 창에서 실행됩니다
- 각 창을 닫거나 Ctrl+C로 개별 종료할 수 있습니다

