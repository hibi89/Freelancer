# CITEVAULT AX — Offline snapshot/restore evidence (2026-11-14 KST)

Scope: opt-in, offline, SYNTHETIC vault only. The service must be stopped and SQLite handles closed before use. This is not a production customer backup service.

Architecture choice: A) plain copy/overwrite risks inconsistent SQLite and data loss (rejected); B) SQLite backup API + SHA-256 per-file manifest + create-only atomic directory publication (selected; 0 external API fees); C) managed online/cloud backup requires separate customer authorization and infrastructure.

Safety contract: absolute paths; new destination only; source-root cannot contain destination; no network calls; no symlink/hardlink/unsupported file; no Windows-reserved names, traversal, case-collision, overbudget files, or extra files at restore. SHA and SQLite quick_check + state generation revalidated before restoration. Failure does not leave a target directory.

Budget: maximum 512 files, 32MiB total, 10MiB/file, path depth 8. Supports synthetic .txt/.md/.pdf/.docx/.csv/.json and the fixed SQLite state file. Not all production datasets.

Commands (offline only):
  node scripts/p85-offline-ops.mjs snapshot --source ABSOLUTE_VAULT_ROOT --dest NEW_ABSOLUTE_BACKUP_DIR
  node scripts/p85-offline-ops.mjs restore --source ABSOLUTE_BACKUP_DIR --dest NEW_ABSOLUTE_RESTORE_DIR

Local verification: Linux Node22.16, node --test tests/p85-offline-backup.test.mjs = 9 PASS / 0 FAIL / 0 SKIP. Synthetic bytes only.
Windows/Ubuntu GitHub Actions: matrix test added in citevault-p50.yml; exact-SHA hosted outcome PENDING at commit creation. CI success later must be separately checked.
Not verified: live concurrent multi-process source consistency, customer IdP, real source rights, actual Korean local model, physical Win10/11 deployment, customer Gold100.
Official final-blueprint 24 requirement score UNASSESSED; 85% unverified; [작업중] / RELEASE HOLD / SALE NO-GO; original upstream and customer data unchanged.
