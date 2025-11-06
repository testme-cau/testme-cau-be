#!/bin/bash

# test.me 초기 설정 스크립트
# 백엔드와 프론트엔드의 의존성을 설치합니다

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/web-frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  test.me 초기 설정${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Python 버전 체크
echo -e "${YELLOW}🐍 Python 버전 확인 중...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3가 설치되어 있지 않습니다${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"

# Node.js 버전 체크
echo -e "${YELLOW}📦 Node.js 버전 확인 중...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Backend 설정${NC}"
echo -e "${BLUE}========================================${NC}"

# Python venv 생성
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Python virtual environment 생성 중...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ venv 생성 완료${NC}"
else
    echo -e "${GREEN}✓ venv가 이미 존재합니다${NC}"
fi

# Backend 의존성 설치
echo -e "${YELLOW}📦 Backend 의존성 설치 중...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Backend 의존성 설치 완료${NC}"

# .env 파일 체크
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}   .env.example을 복사하여 .env를 생성하세요${NC}"
        echo -e "${YELLOW}   cp .env.example .env${NC}"
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Frontend 설정${NC}"
echo -e "${BLUE}========================================${NC}"

# Frontend 의존성 설치
cd "$FRONTEND_DIR"
echo -e "${YELLOW}📦 Frontend 의존성 설치 중...${NC}"
npm install
echo -e "${GREEN}✓ Frontend 의존성 설치 완료${NC}"

# .env.local 파일 체크
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  .env.local 파일이 없습니다${NC}"
    echo -e "${YELLOW}   필요한 환경 변수를 설정하세요${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ 설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}다음 단계:${NC}"
echo ""
echo -e "1. Backend 환경 변수 설정:"
echo -e "   ${YELLOW}cd backend && cp .env.example .env${NC}"
echo -e "   ${YELLOW}# .env 파일을 편집하여 필요한 값 입력${NC}"
echo ""
echo -e "2. Firebase 서비스 계정 키 설정:"
echo -e "   ${YELLOW}# serviceAccountKey.json을 backend/ 디렉토리에 복사${NC}"
echo ""
echo -e "3. Frontend 환경 변수 설정:"
echo -e "   ${YELLOW}cd web-frontend${NC}"
echo -e "   ${YELLOW}# .env.local 파일 생성 및 Firebase 설정 추가${NC}"
echo ""
echo -e "4. 개발 서버 실행:"
echo -e "   ${GREEN}./scripts/dev.sh${NC}"
echo ""

