# MYRADIO AI 검증 계획 및 증거 (2026-11-13 KST)

| 테스트/수용 | 상태 | 다음 기준 |
|---|---|---|
| 미승인 catalog 생성·덮어쓰기 거부 | 로컬 Python PASS | Windows 디렉터리/권한 |
| 동일 시드/장르/기분 선택 | 로컬 Python PASS | 큰 실제 라이브러리/시간 |
| 라이선스 미승인/NC/NCS 보류, CC BY 출처 필수 | 로컬 Python PASS(형식만) | 실제 원본 권리/웹 정책 |
| 절대·상대 path traversal/URL 거부 | 로컬 Python PASS | 악성 파일/symlink/대용량 |
| DJ 문장 스타일 5개 | 로컬 Python PASS | 서로 다른 신경망 TTS 화자·감정 |
| Windows 기본 SAPI 실제 한국어 청취 | 코드만 / NOT_RUN | Windows 10/11 GUI/오디오 |
| tkinter GUI 실제 입력/재생/중지 | 구문 검사만 / NOT_RUN | Windows E2E/접근성 |
| Openverse/ccMixter 검색·재생/ToS | NOT_IMPLEMENTED | 공식 API·상업적 허용 증거 |
| 한국어 다중 DJ 자연 음성 | NOT_IMPLEMENTED | 모델 code+weights 라이선스·청취 품질 |
| 로컬 LLM/STT/방송/취향·큐 | NOT_IMPLEMENTED | 실 마이크/대화/복구 |
| 상용 EXE/고객수용/크몽 심사 | NOT_IMPLEMENTED | 최종 사용자 승인 |

실행 명령:
- python -m compileall -q myradio
- python -m unittest discover -s tests -v
- python -m myradio --help

이번 샌드박스 Python 검사: 7 PASS / 0 FAIL / 0 SKIP, compile PASS. CI·Windows 실재생·실 API/상용 모델 검증 0. 테스트 결과를 판매 가능이나 공식 최종완성율로 환산하지 않는다.

권장 다음 작업: Windows 실 장치 → 다중 화자 TTS 재배포/성능 검사 → 원본 ToS 확인 뒤 음악 검색 API → 대화/취향/큐 → 고객형 패키지.
