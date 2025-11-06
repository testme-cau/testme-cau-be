#!/bin/bash

# test.me 개발 서버 실행 스크립트
# 백엔드(FastAPI) + 프론트엔드(Next.js)를 동시에 실행합니다

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/web-frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  test.me Development Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 백엔드 체크
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend 디렉토리를 찾을 수 없습니다: $BACKEND_DIR${NC}"
    exit 1
fi

# 프론트엔드 체크
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend 디렉토리를 찾을 수 없습니다: $FRONTEND_DIR${NC}"
    exit 1
fi

# Python venv 체크
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Python venv가 없습니다. 생성 중...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv venv
    echo -e "${GREEN}✓ Python venv 생성 완료${NC}"
fi

# Backend 의존성 체크
echo -e "${YELLOW}📦 Backend 의존성 확인 중...${NC}"
cd "$BACKEND_DIR"
if [ -f "requirements.txt" ]; then
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Backend 의존성 설치 완료${NC}"
else
    echo -e "${RED}❌ requirements.txt를 찾을 수 없습니다${NC}"
    exit 1
fi

# Frontend 의존성 체크
echo -e "${YELLOW}📦 Frontend 의존성 확인 중...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   npm install 실행 중...${NC}"
    npm install
    echo -e "${GREEN}✓ Frontend 의존성 설치 완료${NC}"
else
    echo -e "${GREEN}✓ Frontend 의존성 이미 설치됨${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🚀 서버 시작 중...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Backend:${NC}  http://localhost:5000"
echo -e "${GREEN}API Docs:${NC} http://localhost:5000/docs"
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo ""
echo -e "${YELLOW}⚠️  서버를 종료하려면 Ctrl+C를 누르세요${NC}"
echo ""

# trap을 사용하여 Ctrl+C 시 모든 프로세스 종료
trap 'kill 0' SIGINT

# 백엔드 실행 (백그라운드)
cd "$BACKEND_DIR"
echo -e "${BLUE}[Backend]${NC} FastAPI 서버 시작..."
source venv/bin/activate
python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# 백엔드 시작 대기
sleep 2

# 프론트엔드 실행 (백그라운드)
cd "$FRONTEND_DIR"
echo -e "${BLUE}[Frontend]${NC} Next.js 서버 시작..."
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# 프론트엔드 시작 대기
sleep 3

echo ""
echo -e "${GREEN}✓ 모든 서버가 시작되었습니다!${NC}"
echo ""
echo -e "${YELLOW}📝 로그 확인:${NC}"
echo -e "   Backend:  tail -f /tmp/backend.log"
echo -e "   Frontend: tail -f /tmp/frontend.log"
echo ""

# 로그 실시간 출력 (양쪽 모두)
tail -f /tmp/backend.log -f /tmp/frontend.log &

# 프로세스 대기
wait

