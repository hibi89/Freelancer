# MYRADIO AI — 나만의 AI 라디오 방송국

Private repository: hibi89/Freelancer
Branch: product/myradio-ai-dj

**상품 기획 목표:** 사용자의 기분·취향·시간에 맞춰 합법적으로 사용 가능한 음악을 자동 선곡하고, 자연스러운 한국어 AI DJ가 서로 다른 목소리와 말투로 진행하는 Windows 개인용 라디오. 희망 판매가 30,000원(수익성/판매 최종 승인 별도).

**현재는 0.1.0 오프라인 시제품**이다. 실제 다중 DJ 자연음성·Openverse/ccMixter 검색·온라인 자동 재생·LLM/STT는 미구현이며, 기존 Windows SAPI 기본 음성과 규칙 기반 멘트만 지원한다. 상용 제품, 완제품, 판매 가능 프로그램이 아니다. RELEASE HOLD / 크몽 미등록.

## 구현한 기능

- Python 3.11+ 표준 라이브러리로 실행; WAV 폴더를 미승인 catalog.json으로 등록, 수동 권리 확인 후 approved=true일 때만 선곡
- mood/genre 필터, 중복 없는 선택, 시드 기반 재현, 다섯 가지 DJ **멘트 스타일** (다섯 가지 실제 음색 아님)
- 출처 및 라이선스 메타 표시, CC0/CC BY 4.0/본인 소유 로컬 음원만 허용하는 기본 체크, NC/NCS/미승인 파일 차단
- 경로 이탈 방지/원본 변경 안 함, Windows SAPI 음성+WAV 시연 코드, tkinter 초기 GUI
- 외부 서버·유료 API·인터넷 크롤링·음원 자동 다운로드 없음

## 실행

Windows의 Python 환경에서 저장소 브랜치 파일을 내려받은 뒤 아래 명령을 실행한다.

    python -m myradio --help
    python -m myradio init C:\Music\Radio --output C:\Music\Radio\catalog.json
    # catalog.json을 직접 열어 실제 이용권한/저작자/출처/genre/moods 입력하고 approved=true로 변경
    python -m myradio plan --catalog C:\Music\Radio\catalog.json --persona night --mood calm --genre jazz
    python -m myradio play --catalog C:\Music\Radio\catalog.json --persona night
    python -m myradio.gui
    python -m unittest discover -s tests -v

plan은 음성/음악 재생 없이 목록·DJ 멘트 미리보기, play와 gui 실 음성은 Windows PowerShell의 System.Speech와 winsound에 의존한다. Windows 10/11에서 실제 작동/한국어 화자 설치 여부는 아직 검증하지 않았다. 음악은 고객 PC의 WAV를 직접 지정하며 앱에 함께 포함하거나 판매하지 않는다.

## 카탈로그 양식

    {"tracks":[{"path":"song.wav","title":"곡명","artist":"저작자","genre":"jazz","moods":["calm"],"license":"LOCAL-USER","license_url":"","source_url":"","approved":false}]}

CC0/CC-BY 항목은 실제 개별 파일의 정당한 출처와 라이선스 HTTPS 링크를 기입해야 한다. 단순 문자열·체크박스는 법률상 권리 검증이 아니므로 미확인 곡을 임의 승인하면 안 된다.

최종 상품 범위: docs/FINAL_BLUEPRINT.md
기능/시험: REQUIREMENTS.md, docs/ACCEPTANCE_AND_ROADMAP.md
권리/판매: docs/COMMERCIAL_AND_COPYRIGHT.md
진행/인수인계: STATUS.md, HANDOFF.md
