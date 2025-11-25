#!/bin/bash

# LaunchAgent 기반 스테이징 백엔드 제어 스크립트

set -euo pipefail

LABEL="com.testme.backend.staging"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
LOG_DIR="$HOME/Library/Logs/testme"
COMBINED_LOG="$LOG_DIR/testme-staging.log"
STDOUT_LOG="$LOG_DIR/testme-staging.out.log"
STDERR_LOG="$LOG_DIR/testme-staging.err.log"

usage() {
  cat <<USAGE
사용법: $(basename "$0") <command>

지원 명령:
  start      LaunchAgent를 즉시 시작 (kickstart)
  stop       LaunchAgent를 언로드하고 중지 (bootout)
  reload     plist 재적용 (bootout → bootstrap → start)
  status     LaunchAgent 상태 출력
  logs       종합 로그 tail -f
  out        stdout 로그 tail -f
  err        stderr 로그 tail -f
USAGE
  exit 1
}

require_plist() {
  if [ ! -f "$PLIST" ]; then
    echo "❌ LaunchAgent plist를 찾을 수 없습니다: $PLIST"
    exit 1
  fi
}

cmd="${1:-}"
if [ -z "$cmd" ]; then
  usage
fi

case "$cmd" in
  start)
    require_plist
    launchctl bootstrap "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl kickstart -k "gui/$(id -u)/${LABEL}"
    echo "✅ ${LABEL} kickstart 완료"
    ;;
  stop)
    require_plist
    if launchctl print "gui/$(id -u)/${LABEL}" >/dev/null 2>&1; then
      launchctl bootout "gui/$(id -u)" "$PLIST"
      echo "🛑 ${LABEL} 중지 완료"
    else
      echo "ℹ️  ${LABEL} 는 이미 중지 상태입니다."
    fi
    ;;
  reload)
    require_plist
    launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    launchctl kickstart -k "gui/$(id -u)/${LABEL}"
    echo "🔁 ${LABEL} 재적용 완료"
    ;;
  status)
    require_plist
    launchctl print "gui/$(id -u)/${LABEL}"
    ;;
  logs)
    tail -f "$COMBINED_LOG"
    ;;
  out)
    tail -f "$STDOUT_LOG"
    ;;
  err)
    tail -f "$STDERR_LOG"
    ;;
  *)
    usage
    ;;
esac

