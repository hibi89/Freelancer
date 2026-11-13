# HANDOFF — MYRADIO AI (10항 / 2026-11-13 KST)

1. 목표·용도·확정기술: Windows 개인용 자동 AI 라디오. 감정/장르/시간/취향 선곡, 저작권·서비스 약관 허용 음악 검색·재생, 실제 여러 다른 한국어 DJ 음색/감정·속도·방송 멘트, 로컬/온라인 모드, 청취자 대화. 희망 판매가 30,000원; 작곡 모델은 후속 선택.
2. 완료 기능·변경·결정 근거: 새 product/myradio-ai-dj 브랜치, 최종설계와 권리·판매·검증 문서; 오프라인 WAV 카탈로그 초안/수동 rights 확인/seed 필터 선곡/다섯 DJ 대사 스타일/Windows SAPI·WAV 재생 코드 및 tkinter GUI. A local-first(선정) / B cloud(기본형 제외) / C 무단 크롤링(배제) 비교. 외부 API 호출 0.
3. 테스트 명령/성공·실패·미검증: python -m unittest discover -s tests -v 7 PASS/0 FAIL/0 SKIP, python -m compileall -q myradio PASS, python -m myradio --help PASS (로컬 샌드박스). 실 Windows GUI·PowerShell SAPI·음악 재생·API·실 자연 TTS NOT_RUN/NOT_IMPLEMENTED. 테스트 실행 기록과 GitHub 코드 일치 확인 전 원격 테스트 성공 보장 금지.
4. 완료/진행/대기/차단·중단 지점: 계획+초기 오프라인 기능만. DJ 자연음성, 실 사이트 검색·권리 자동검증/정식 스트리밍, 상용 EXE/크몽 등록 대기. 최종설계 기준 UNASSESSED/RELEASE HOLD.
5. 오류·근거·원인·시도·대안: 현 7 로컬 단위검사 실패 없음. 위험은 사이트별 상업 앱 플레이 허용과 2+ 실제 TTS 화자/저사양 성능. 허가 불명 음악 강제 재생/다운로드 금지→허가된 로컬 파일/대체 승인 소스. Windows SAPI 실제 품질 미검증→신경망 모델/기본 보이스 비교. 동일 실패 반복 무진전 중단.
6. 저장소·브랜치·SHA·경로: Private hibi89/Freelancer @ product/myradio-ai-dj, base main@fe4bbfea9b515d85b6e77b77c57e63851bd2964d. 문서 기준 GitHub SHA는 최종 원격 ref 확인 후 최종 작업 보고. 핵심 myradio/core.py, playback.py, gui.py, __main__.py, tests/test_radio.py, docs/FINAL_BLUEPRINT.md.
7. Production/Vercel/명령·환경: Production URL/Vercel 미적용. Python 3.11+ stdlib, Windows 10/11 목표. python -m myradio init PATH --output PATH/catalog.json → 승인/음악 메타 → python -m myradio plan --catalog PATH/catalog.json; Windows 실제 play/GUI는 각각 python -m myradio play --catalog PATH/catalog.json / python -m myradio.gui.
8. 원본/백업·인증 관리·수정금지: 기존 Freelancer main/other product 브랜치 미수정. 원본 구직 자료 Git 이력 d47239f961fc895592147c2afa969ecf64f2bd00 복구 가능. 고객 노래·가족 음성·개인정보·모델 weights·.env/API키 GitHub/클라우드 무단 전송 금지. 커밋/브랜치로 rollback.
9. 다음 작업 우선순위/승인/완료: Windows 실 재생·GUI 테스트 → 다중 DJ 자연음성 코드/weights commercial 라이선스/자원 실측 → Openverse/ccMixter 원본 ToS 및 음원별 허가 확인 → 공식 검색 API + 정상 플레이어 → LLM/STT/취향/큐 → 패키지/보안/고객 수용 → 사용자 판매 최종 승인. 신규 유료 호출·외부 원본 전송·권한·설치 원본 수정 사전 승인.
10. 갱신 KST/검증 범위/문서기준: 2026-11-13, 샌드박스 Python 단위·구문 검증 중심, 실제 Windows/외부 API/배포 미확인. 이 브랜치 최신 commit SHA와 blob readback을 본 작업 최종 보고로 교차확인. STATUS/REQUIREMENTS/FINAL_BLUEPRINT 동기화. 
