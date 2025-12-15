# Security Notes

## React2Shell (CVE-2025-55182) 영향 평가
- 현재 프런트엔드 버전: Next.js 14.2.33 / React 18.3.1 (`npm ls` 기준)
- React19 / Next15 이상을 사용하지 않으므로 React2Shell(RSC Flight 역직렬화) 직접 영향 범위에 해당하지 않음.
- 추후 React19 / Next15+ 업그레이드 시 즉시 패치 버전으로 이동 필요:
  - React ≥ 19.0.1 / 19.1.2 / 19.2.1
  - Next.js 15.0.5+ / 16.0.7+

## 상시 방어 권고
- WAF: RSC Flight 특유 패턴/비정상 긴 헤더·바디 차단 룰 적용.
- SSR/RSC 경로: rate limit, 허용 메서드/콘텐츠 타입 강제.
- 로깅/모니터링: `child_process` 실행 시도, 비정상 POST/헤더 스파이크 알림.
- 배포 시: 최신 LTS Node/npm, 정기 `npm audit --production`/`npm outdated` 점검.

## 운영 체크리스트
- 빌드 전 `npm run lint` / `npm run build`.
- 의존성 점검: `npm ls next react react-dom`으로 버전 기록.
- 이상 징후 발견 시 신규 인스턴스 롤링 및 자격 증명 로테이션 권장.

