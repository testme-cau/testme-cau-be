#!/bin/bash

# Next.js 프론트엔드 스테이징 서버 관리 스크립트
# start/stop/status/logs 명령을 지원합니다.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
RUN_SCRIPT="$SCRIPT_DIR/frontend-run.sh"
LOG_DIR="$HOME/Library/Logs/testme"
LOG_FILE="$LOG_DIR/frontend-staging.log"
PID_FILE="$LOG_DIR/frontend-staging.pid"

mkdir -p "$LOG_DIR"

usage() {
  cat <<USAGE
사용법: $(basename "$0") <start|stop|restart|status|logs>
USAGE
  exit 1
}

is_running() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if ps -p "$pid" >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

start() {
  if is_running; then
    echo "⚠️  이미 실행 중입니다 (pid $(cat "$PID_FILE"))."
    return
  fi
  echo "▶️  프론트엔드 스테이징 서버를 백그라운드에서 시작합니다..."
  nohup "$RUN_SCRIPT" >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  echo "✅ 시작 완료 (pid $(cat "$PID_FILE")). 로그: $LOG_FILE"
}

stop() {
  if ! is_running; then
    echo "ℹ️  실행 중인 프로세스가 없습니다."
    return
  fi
  local pid
  pid="$(cat "$PID_FILE")"
  echo "🛑 프로세스 종료 중... (pid $pid)"
  kill "$pid" >/dev/null 2>&1 || true
  rm -f "$PID_FILE"
  echo "✅ 중지 완료"
}

status() {
  if is_running; then
    echo "✅ 실행 중 (pid $(cat "$PID_FILE"))."
  else
    echo "🛑 실행 중이 아닙니다."
  fi
}

logs() {
  if [ ! -f "$LOG_FILE" ]; then
    echo "로그 파일이 아직 없습니다: $LOG_FILE"
    exit 0
  fi
  tail -f "$LOG_FILE"
}

cmd="${1:-}"
case "$cmd" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  logs) logs ;;
  *) usage ;;
esac

