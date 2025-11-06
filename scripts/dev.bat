@echo off
REM test.me 개발 서버 실행 스크립트 (Windows)
REM 백엔드(FastAPI) + 프론트엔드(Next.js)를 동시에 실행합니다

setlocal enabledelayedexpansion

echo ========================================
echo   test.me Development Server
echo ========================================
echo.

REM 프로젝트 루트 디렉토리
set PROJECT_ROOT=%~dp0..
set BACKEND_DIR=%PROJECT_ROOT%\backend
set FRONTEND_DIR=%PROJECT_ROOT%\web-frontend

REM 백엔드 체크
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend 디렉토리를 찾을 수 없습니다
    exit /b 1
)

REM 프론트엔드 체크
if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend 디렉토리를 찾을 수 없습니다
    exit /b 1
)

REM Python venv 체크
if not exist "%BACKEND_DIR%\venv" (
    echo [INFO] Python venv 생성 중...
    cd /d "%BACKEND_DIR%"
    python -m venv venv
    echo [SUCCESS] Python venv 생성 완료
)

REM Backend 의존성 설치
echo [INFO] Backend 의존성 확인 중...
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo [SUCCESS] Backend 의존성 설치 완료

REM Frontend 의존성 설치
echo [INFO] Frontend 의존성 확인 중...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo [INFO] npm install 실행 중...
    call npm install
    echo [SUCCESS] Frontend 의존성 설치 완료
) else (
    echo [SUCCESS] Frontend 의존성 이미 설치됨
)

echo.
echo ========================================
echo   서버 시작 중...
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo API Docs: http://localhost:5000/docs
echo Frontend: http://localhost:3000
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요
echo.

REM 백엔드 실행 (새 창)
start "Backend - FastAPI" cmd /k "cd /d %BACKEND_DIR% && venv\Scripts\activate.bat && python main.py"

REM 잠시 대기
timeout /t 3 /nobreak > nul

REM 프론트엔드 실행 (새 창)
start "Frontend - Next.js" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo [SUCCESS] 모든 서버가 시작되었습니다!
echo.
echo 각 서버는 별도의 창에서 실행됩니다.
echo 서버를 종료하려면 각 창을 닫거나 Ctrl+C를 누르세요.
echo.

pause

