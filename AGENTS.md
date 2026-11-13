# AGENTS — AXNODE 제품 브랜치
> 전체 공통 [OWNER-FINAL-BLUEPRINT-100](https://github.com/hibi89/hackathon-command-center-2026/blob/kmong-productization/docs/strategy/FINAL_BLUEPRINT_COMPLETION_STANDARD_20261113.md) 준수. 최종완성률의 분모는 사용자 확정 제품 설계 전체 100%; 합성 POC/19 PASS=공식 상품 퍼센트 아님. 현재 `UNASSESSED`.

1. 담당 범위: `hibi89/Freelancer@product/axnode-sector-runtime` 독자 섹터 파일+런타임, 사용자 선택 A안. 다른 product/* 및 HAE/LA/기존32종 소스는 임의 변경 금지.
2. 채팅 복구: HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/FINAL_BLUEPRINT.md → 실제 source/tests 순.
3. 설계 변경 시 A(독자 바이트 포맷) vs B(기성 컨테이너) 성능·비용·보안·유지보수 비교. A를 ZIP 이름 변경으로 대체하거나 최종 범위를 줄이려면 사용자 승인 필요.
4. `.axnode`의 서명·검사·정책·고객 승인이 검증되기 전 임의 원격 Python/쉘 다운로드 실행 금지. 네트워크 기본 차단, 좁은 allowlist, 최소 권한·상한·샌드박스·복구·무결성/공급망 보안 적용.
5. GitHub에 고객 파일/키/.env/개인정보/대형 모델 업로드 금지. 외부 송신/유료 CI/계정권한·보안변경/원본 수정/상용 출고는 사전 승인. 무료 Actions 무제한 자원 보장 금지.
6. 제품 구현 시작 전 본 브랜치 최신 SHA와 해총 원장 등록 상태 확인. 테스트·실 OS·GitHub Actions·원격 실행·고객 인수·Production을 독립 판정하고 기능 검증 SHA 기록. 실패 무진전 2회 STOP/PIVOT.
7. `docs/FINAL_BLUEPRINT.md` R01~R29 요구/가중치(소유자 확정)/코드/정확 SHA 테스트 증거를 추적해야 공식 완성률 산정 가능. 기존 제품 진척률·등록이력 복제 금지.
8. 신규 브랜치/변경 후 해총 `kmong-productization/docs/audits/FREELANCER_BRANCH_COMPLETION_REGISTRY_20261113.md`에 AXNODE 영구 등재. 별도 무인 동기화는 미구현.
9. 기존 `[작업중]`/HOLD/미등록 상태 보존, 실제 크몽 게시 증거 없이는 `등록완료` 금지.
10. 주요 변경 후 STATUS와 10항 HANDOFF 최신화, GitHub commit SHA/파일 readback, 미검증 명시. Vercel 등 배포 비대상은 미적용.
