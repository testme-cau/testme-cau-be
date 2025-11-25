#!/bin/bash

# Next.js 프론트엔드 스테이징 서버 실행 스크립트
# - web-frontend/.env.staging 환경 파일을 로드합니다.
# - 기본 포트는 13001이며 PORT 환경 변수로 오버라이드할 수 있습니다.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
FRONTEND_DIR="$PROJECT_ROOT/web-frontend"
ENV_FILE="${ENV_FILE:-$FRONTEND_DIR/.env.staging}"
PORT="${PORT:-13001}"
API_URL="${NEXT_PUBLIC_API_URL:-https://testmeapi.jdn.kr}"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ web-frontend 디렉토리를 찾을 수 없습니다: $FRONTEND_DIR"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ 스테이징 환경 파일을 찾을 수 없습니다: $ENV_FILE"
  echo "   web-frontend/.env.example을 참고해 $ENV_FILE 를 작성한 뒤 다시 실행하세요."
  exit 1
fi

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "📦 node_modules가 없어 npm install을 실행합니다..."
  npm install --loglevel error
fi

export PORT="$PORT"
export NEXT_PUBLIC_API_URL="$API_URL"

echo "🚀 Next.js 스테이징 서버 시작 (port=$PORT, env=$ENV_FILE, api=$API_URL)"
echo "    중지: Ctrl+C"
echo ""

exec npm run dev:staging

