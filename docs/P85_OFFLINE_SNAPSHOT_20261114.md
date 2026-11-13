# CITEVAULT AX — Offline snapshot/restore evidence (2026-11-14 KST)

## [2026-11-14 KST] SQLite 스키마·현재 문서 원문 SHA 추가 검증 (최신)

- exact source `d32f530e2425da0129a4eb2e9a4a7aef6708dab8`, [CI #43527372030](https://github.com/hibi89/Freelancer/actions/runs/43527372030) **6/6 SUCCESS**, offline suite **Ubuntu12/12·Windows12/12 PASS**, 전체중복합산404PASS/0FAIL/0SKIP.
- Active document가 DB의 digest와 다른 파일을 가리키면 snapshot 단계에서도 거부. Restore 단계에서 위조된 SQLite DB/manifest 복구를 차단. `header`만 있는 DB는 더 이상 복구로 인정하지 않음.
- 오프라인 서비스 중지형 synthetic vault 전용. 동시운영 고객백업/카탈로그 승인신원/골든100 대체 아님. 별도 상세 `docs/P85_SNAPSHOT_CATALOG_INTEGRITY_20261114.md`.


Scope: opt-in, offline, SYNTHETIC vault only. The service must be stopped and SQLite handles closed before use. This is not a production customer backup service.

Architecture choice: A) plain copy/overwrite risks inconsistent SQLite and data loss (rejected); B) SQLite backup API + SHA-256 per-file manifest + create-only atomic directory publication (selected; 0 external API fees); C) managed online/cloud backup requires separate customer authorization and infrastructure.

Safety contract: absolute paths; new destination only; source-root cannot contain destination; no network calls; no symlink/hardlink/unsupported file; no Windows-reserved names, traversal, case-collision, overbudget files, or extra files at restore. SHA and SQLite quick_check + state generation revalidated before restoration. Failure does not leave a target directory.

Budget: maximum 512 files, 32MiB total, 10MiB/file, path depth 8. Supports synthetic .txt/.md/.pdf/.docx/.csv/.json and the fixed SQLite state file. Not all production datasets.

Commands (offline only):
  node scripts/p85-offline-ops.mjs snapshot --source ABSOLUTE_VAULT_ROOT --dest NEW_ABSOLUTE_BACKUP_DIR
  node scripts/p85-offline-ops.mjs restore --source ABSOLUTE_BACKUP_DIR --dest NEW_ABSOLUTE_RESTORE_DIR

Local verification: Linux Node22.16, node --test tests/p85-offline-backup.test.mjs = 9 PASS / 0 FAIL / 0 SKIP. Synthetic bytes only.
Windows/Ubuntu GitHub Actions: exact feature SHA 0cf969fb2908cca985f4655d2c713ad7e030d168 [#43525453183](https://github.com/hibi89/Freelancer/actions/runs/43525453183) 6/6 SUCCESS. Offline snapshot test 9 PASS/0 FAIL/0 SKIP on each OS; full hosted suite 398 PASS/0 FAIL/0 SKIP across Linux+Windows/RAG jobs. Physical Windows10/11 and live customer backup remain UNVERIFIED.
Not verified: live concurrent multi-process source consistency, customer IdP, real source rights, actual Korean local model, physical Win10/11 deployment, customer Gold100.
Official final-blueprint 24 requirement score UNASSESSED; 85% unverified; [작업중] / RELEASE HOLD / SALE NO-GO; original upstream and customer data unchanged.
