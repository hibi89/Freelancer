# WORKNOVA Desk — 상용화 권리 및 개인정보 사전 검토

검토일: 2026-11-14 KST. 사전 조사이며 법률 자문, 재배포 권리 확정 또는 판매 승인이 아님.

| 구성품 | 적용 | 공식 라이선스 근거 | 출고 전 할 일 |
|---|---|---|---|
| Python 3.11+ / Tkinter / SQLite / 표준 OOXML | 필수 Python 런타임 | PSF v2: https://docs.python.org/3/license.html | ZIP에는 Python 없음. 향후 EXE 번들 시 Python과 포함 구성의 라이선스·NOTICE 확인 |
| cryptography | 선택적 AES-GCM 암호화 백업 | Apache-2.0 OR BSD-3-Clause: https://pypi.org/project/cryptography/ | 실제 포함 wheel과 종속성 라이선스 전문 점검. 사용 중인 SQLite DB는 평문 |
| ReportLab 오픈소스 | 선택적 PDF 생성 | BSD: https://docs.reportlab.com/developerfaqs/ | 재배포 버전의 license.txt·포함 의존성 검토 |
| 한국어 TTF | 사용자가 로컬에서 선택 | 파일별 독립 라이선스 | 번들 없음, 상용 PDF 임베딩 권리 별도 확인. OS 글꼴 재배포권 추정 금지 |
| 고객·수금 자료 | 로컬 SQLite | 개인정보·사용자 자료 | 접근통제/보존·삭제/지원정책·사용자 확인 필요 |

## 반드시 남는 출시 조건
- 제품 자체 라이선스/실제 고객 계약/환불·지원 정책 미승인.
- 감사 해시는 공인 전자서명이 아니고 수금은 은행/PayPal 입금 보증이 아님.
- 상용 PDF 폰트 UI 동의만으로 그 글꼴의 실사용권을 법적으로 증명하지 못함.
- 독립 Windows EXE/한글 인쇄/권한 설정/고객 검수/법무 최종 승인 미완.
- 외부 고객 데이터나 비밀자료를 GitHub·공개 서비스로 전송하지 않음.

따라서 WD-12/14 정식 완료 아님. [작업중], RELEASE HOLD.
