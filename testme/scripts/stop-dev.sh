#!/bin/bash

# test.me 개발 서버 중지 스크립트

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 서버 중지 중...${NC}"

# 포트로 프로세스 찾아서 종료
# Backend (port 5000)
BACKEND_PID=$(lsof -ti:5000)
if [ ! -z "$BACKEND_PID" ]; then
    echo -e "${YELLOW}   Backend 서버 종료 (PID: $BACKEND_PID)${NC}"
    kill -9 $BACKEND_PID 2>/dev/null
    echo -e "${GREEN}   ✓ Backend 종료 완료${NC}"
else
    echo -e "${YELLOW}   Backend 서버가 실행 중이 아닙니다${NC}"
fi

# Frontend (port 3000)
FRONTEND_PID=$(lsof -ti:3000)
if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${YELLOW}   Frontend 서버 종료 (PID: $FRONTEND_PID)${NC}"
    kill -9 $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}   ✓ Frontend 종료 완료${NC}"
else
    echo -e "${YELLOW}   Frontend 서버가 실행 중이 아닙니다${NC}"
fi

# Python 프로세스 정리
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "python main.py" 2>/dev/null || true

# Next.js 프로세스 정리
pkill -f "next dev" 2>/dev/null || true

echo -e "${GREEN}✓ 모든 서버가 종료되었습니다${NC}"

