#!/bin/bash

# Staging FastAPI 서버 실행 스크립트 (macOS용)
# - backend/.env.staging 환경 파일을 로드합니다.
# - 기본 포트는 13000이며 PORT 환경 변수로 오버라이드할 수 있습니다.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
BACKEND_DIR="$PROJECT_ROOT/backend"
ENV_FILE="${ENV_FILE:-$BACKEND_DIR/.env.staging}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-13000}"
LOG_LEVEL="${LOG_LEVEL:-info}"
WORKERS="${WORKERS:-1}"

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  for candidate in /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3 /usr/local/bin/python3.11 /usr/local/bin/python3 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v "$candidate")"
      break
    fi
  done
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "❌ python3 실행 파일을 찾을 수 없습니다. PYTHON_BIN을 지정하세요."
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
  echo "❌ Python 3.11 이상이 필요합니다. 현재: $("$PYTHON_BIN" -V)"
  exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
  echo "❌ backend 디렉토리를 찾을 수 없습니다: $BACKEND_DIR"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ 스테이징 환경 파일을 찾을 수 없습니다: $ENV_FILE"
  echo "   backend/.env.example을 복사해 $ENV_FILE 를 생성한 뒤 다시 실행하세요."
  exit 1
fi

cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
  echo "⚙️  Python venv가 없어 새로 생성합니다... ($PYTHON_BIN)"
  "$PYTHON_BIN" -m venv venv
fi

source venv/bin/activate

if ! python -c "import uvicorn" >/dev/null 2>&1; then
  echo "📦 uvicorn이 없어 requirements.txt를 설치합니다..."
  pip install -q -r requirements.txt
fi

export PYTHONPATH="$BACKEND_DIR:${PYTHONPATH:-}"

echo "🚀 test.me Staging 서버 시작"
echo "   ENV_FILE : $ENV_FILE"
echo "   HOST     : $HOST"
echo "   PORT     : $PORT"
echo "   WORKERS  : $WORKERS"
echo ""
echo "로그는 stdout/stderr 로 출력됩니다. 중지는 Ctrl+C"

exec uvicorn main:app \
  --host "$HOST" \
  --port "$PORT" \
  --env-file "$ENV_FILE" \
  --workers "$WORKERS" \
  --log-level "$LOG_LEVEL"

