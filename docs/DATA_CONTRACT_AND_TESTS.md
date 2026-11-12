# ONTOINSIGHT AX 데이터 의미/품질/ML 독립 검증 카탈로그

## A. 고객 사전 확인 카드
- 원본 파일 사용 권한·일반/민감/개인정보 포함 여부·보관 기간·외부 AI 허용·차트/파생파일의 재배포 범위.
- 필드 의미: 주문일 vs 결제일 vs 취소일, 거래 취소/환불 처리, 금액 통화(원/달러), VAT 포함, 중복 판매 주문, 고객 identifier 의미.
- 분석 목적: 기술통계/고객군 분할/재고 경향/매출추이/예측 중 어떤 문제인지, 예측 시점과 사용 가능한 feature.
- 권한 없는 주민등록번호/건강정보·불법 취득 고객 개인정보는 수령하지 않음. 보고서 가명/집계/임계 소집단 마스킹 정책.

## B. 지표 계약 예시
`gross_sales`: 승인된 판매 event의 세전/세후/할인/쿠폰 여부 포함 기준. 
`refund_amount`: 승인된 환불 event(원 결제 연결/환불 발생일 구분).
`net_sales`: 고객 승인 회계 정의에 따라 gross minus refund/discount 등 산식 고정; 임의 회계공식 보증 금지.
`order_count`: 주문별 1건, orderline duplicate JOIN로 중복 증가 차단.
`AOV`: 승인된 매출 분자/주문 건수 분모, 0분모면 null/NOT_DEFINED.
`repeat_customer_rate`: 고객 identifier + 고객 데이터 사용권 + 분석 기간/활동 고객 분모를 고정.
`conversion_rate`: 방문자/세션 등 모수가 없으면 계산 불가; 주문 CSV만으로 추정 금지.
`ROAS`: 유효 매출 attribution 기준/paid-channel 광고비·시점 매핑 모두 있어야 계산; 비용 빠지면 계산 불가.
- 모든 수치는 보고서에서 `formula_version + source_ids + source_digest + exact unit` 표시.

## C. 필수 테스트 케이스 36개 (신규 구현 대상)
1. UTF-8 CSV 정상 2. EUC-KR/CP949 표시 3. UTF-8 BOM 4. 잘못된 인코딩 5. 빈 파일 6. 누락 헤더 7. 중복 헤더 8. 한글·공백 경로 9. 특수문자 CSV formula 10. 원본 디렉터리 symlink.
11. XLSX 정상 시트 12. 암호화 XLSX 13. Excel 외부 링크/매크로 14. 엑셀 일련번호 날짜/타임존 15. 숫자 문자열/콤마 통화 16. 부가세 포함/제외 혼용 17. 주문 중복키 18. 한 고객 다주문 19. 1:N 주문라인 JOIN 폭증 20. 외래키 매핑 불일치.
21. 데이터 집계 행수 일치 22. 모든 금액 decimal rounding 23. 환불 이벤트/주문 취소 이중 차감 24. 근거 없는 conversion/ROAS null 25. 원본 SHA 변경/승인 무효화 26. 오프라인 외부 송신 deny 27. PII 필드·소집단 마스킹 28. ML target leakage derived column 29. time-based test split 30. group leakage customer.
31. dummy baseline보다 나쁜 모델 32. 작은/불균형 클래스 불가 판정 33. train만 fit되는 scaling/encoding 34. heldout 중복 평가 금지 35. 보고서 변조/ZIP SHA 거부 36. Windows10/11 고객형 파일 저장/열기·수치독립 재계산.
- 이 36개는 **작성된 검증 계획**이지 실행 완료된 테스트가 아니다.
- 추가 수용: 3개 합성 업종(shop/order/refund/ads) × 최소 2개 기간, 누락/음수/중복/비밀 컬럼, 매핑 변경 재승인, 보고서 수치가 데이터 행 집계와 정확 일치.
- HAE/DBVORA/SMAX 등 연동을 넣을 때 모두 optional/contract test 사용, 기존 95% 제품 점수를 재활용해 신규 100%로 합산 금지.

## D. 명시 데이터 계약(가상)
```json
{
 "contract":"ontoinsight.run.v1",
 "sources":[{"id":"orders","sha256":"<sha256>","rows":1200,"permission":"REVIEW_HOLD"}],
 "mapping":{"version":1,"role":"order_id","status":"PENDING","source_digest":"<sha256>"},
 "metrics":[{"metric":"net_sales","formula_version":"v1","status":"NEEDS_APPROVAL"}],
 "ml":{"target":null,"decision":"ML_NOT_SUITABLE","reason":"No approved target"},
 "report":{"export_allowed":false,"verified":false,"sha256":null}
}
```
모든 상태 머신은 고객 승인 `PENDING→REVIEWED→APPROVED→GENERATED→VALIDATED→DELIVERED`, 오류는 `HOLD/FAILED/CANCELED/REVIEW_REQUIRED`. GitHub 소스에 고객 실 데이터·매출액/신원·키 저장 금지.
