# AGENTS — MYRADIO AI 작업 규칙

1. 새 채팅 또는 사용자 'ㄱ': HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → docs/FINAL_BLUEPRINT.md → 소스/테스트 순서.
2. 공식 최종완성률 분모 = docs/FINAL_BLUEPRINT.md 최종 확정 R01~R15 전체 100%. 미구현/미검증/코드·정확 SHA·수용 근거가 없으면 UNASSESSED. 설계/시험 PASS만으로 50/70/85/95/100 주장 금지.
3. 이 브랜치 product/myradio-ai-dj만 수정. Freelancer/main과 다른 상품 branch 및 원본/고객 자료 보존. force push/이력 수정 금지. 변경 전 HEAD와 복구 경로 확인.
4. 두 가지 이상 아키텍처의 성능·비용·법적 권리·데이터 안전성을 비교하고 선택. 외부 API/유료 모델·음악 서비스/공개 배포/고객 자료 전송은 사전 승인.
5. 오픈 라이선스 ≠ 저작권 부재 ≠ 임의 스트리밍/다운로드 재배포 허가. 개별 음원 원본·실연/원반권·사이트 ToS 확인, CC BY attribution 준수, NCS/NC/권리 미확인은 보류.
6. DJ 말투 템플릿 다섯 가지는 다섯 음색이 아니며 Windows SAPI는 자연 음성 모델이 아니다. Qwen3-TTS/CosyVoice 등은 검증 전 후보일 뿐. 코드/가중치/데이터셋 배포 및 상업용 허가 검토 후 내장.
7. GitHub에는 코드, 문서, tests, 메타데이터 예시만. 음악 실파일·원본 음성·비밀 키·.env·개인정보·대형 모델 weights 금지. 읽기 전용 파일과 경로검증 유지.
8. 상품 개발 착수/상태 갱신 시 해총 kmong-productization 상품 원장과 [작업중] 정책 연동. 목표 달성 전 임의 해제 금지, 실제 등록 증거 없이는 크몽 '등록완료' 표기 금지.
9. 개발/수정 시 로컬 단위·실 Windows GUI/음성·외부 API 권한·보안/실 청취·복구 검증 분리, 테스트/CI 사용료 및 권한 확인. 오류 반복 시 STOP/PIVOT.
10. 주요 작업 종료 시 STATUS.md, HANDOFF.md 10항, GitHub 실제 commit SHA 및 원격 파일 readback, 해총 상품 색인 최신화; 실 서비스 미배포/미검증은 명시.
