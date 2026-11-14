"""CI-only frozen-EXE business and backup/restore proof on fake local records.

No real LOCALAPPDATA, customer data, network, credentials or financial APIs.
The test writes only a temporary synthetic SQLite and one NEW caller-specified
JSON report; all synthetic SQLite/backup files are deleted before returning.
A passing result is engineering evidence, not commercial buyer sign-off.
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from .core import Desk, DeskError, restore_new


def _must_reject(fn, reason: str) -> None:
    try:
        fn()
    except DeskError:
        return
    raise AssertionError(reason)


def run(output: str | Path) -> dict:
    target = Path(output)
    if (target.suffix.lower() != '.json' or target.exists() or target.is_symlink()
            or not target.parent.is_dir() or target.parent.is_symlink()):
        raise DeskError('Synthetic report must be a NEW .json in an existing plain directory')

    with tempfile.TemporaryDirectory(prefix='worknova-frozen-qa-') as temp:
        work = Path(temp)
        db_path = work / 'fake.sqlite'
        desk = Desk(db_path, allow_create=True)
        try:
            customer = desk.add_customer('WORKNOVA_SYNTHETIC_ONLY')
            quote = desk.new_quote(customer, [
                {'description': 'Synthetic service', 'quantity': 2, 'unit_krw': 500}
            ], taxable=True)
            quotes = desk.list_quotes(customer)
            if len(quotes) != 1 or quotes[0]['total_krw'] != 1100:
                raise AssertionError('KRW/VAT calculated incorrectly')
            steps = [{'title': 'Synthetic delivery', 'amount_krw': 1100}]
            _must_reject(lambda: desk.new_contract(quote, 'synthetic scope', steps),
                         'Unapproved quote was allowed to create contract')
            desk.approve_quote(quote, 'qa-owner')
            contract = desk.new_contract(quote, 'synthetic scope', steps)
            desk.activate_contract(contract, 'qa-owner')
            milestone = desk.list_milestones(contract)[0]['id']
            _must_reject(lambda: desk.record_collection(milestone, 1100, 'QA-BEFORE', 'qa-owner'),
                         'Payment record accepted before delivery acceptance')
            desk.deliver(milestone, 'qa-owner', 'synthetic file delivered')
            desk.accept(milestone, 'qa-customer')
            first = desk.record_collection(milestone, 700, 'QA-PARTIAL', 'qa-owner')
            if desk.record_collection(milestone, 700, 'QA-PARTIAL', 'qa-owner') != first:
                raise AssertionError('Duplicate receipt reference changed id')
            desk.record_collection(milestone, 400, 'QA-REMAINDER', 'qa-owner')
            _must_reject(lambda: desk.record_collection(milestone, 1, 'QA-OVERPAY', 'qa-owner'),
                         'Overpayment was accepted')
            initial_events = desk.verify_audit()
            if initial_events < 8:
                raise AssertionError('Audit events missing')
            backup_path = work / 'fake-backup.sqlite'
            backup_digest = desk.backup(backup_path)
        finally:
            desk.close()

        restored_path = work / 'restored.sqlite'
        restore_new(backup_path, restored_path, backup_digest)
        recovered = Desk(restored_path, allow_create=False)
        try:
            if recovered.schema_version != 2:
                raise AssertionError('Restored SQLite schema differs')
            if recovered.list_customers('WORKNOVA_SYNTHETIC_ONLY')[0]['id'] != customer:
                raise AssertionError('Restored customer differs')
            if recovered.list_quotes(customer)[0]['total_krw'] != 1100:
                raise AssertionError('Restored quote or VAT differs')
            if recovered.list_contracts(customer)[0]['status'] != 'ACTIVE':
                raise AssertionError('Restored contract differs')
            if recovered.list_milestones(contract)[0]['status'] != 'ACCEPTED':
                raise AssertionError('Restored acceptance differs')
            with closing(sqlite3.connect(restored_path.resolve().as_uri() + '?mode=ro',
                                         uri=True)) as readonly:
                if readonly.execute('SELECT COUNT(*) FROM receipts').fetchone()[0] != 2:
                    raise AssertionError('Restored receipts count differs')
                if readonly.execute('SELECT SUM(amount_krw) FROM receipts').fetchone()[0] != 1100:
                    raise AssertionError('Restored KRW receipts differ')
                if readonly.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise AssertionError('Restored SQLite integrity differs')
            restored_events = recovered.verify_audit()
            if restored_events != initial_events:
                raise AssertionError('Restored audit digest chain differs')
        finally:
            recovered.close()

    result = {
        'ok': True,
        'synthetic_only': True,
        'scope': 'frozen EXE quote/VAT/approval/contract/delivery/acceptance/receipts/backup/restore',
        'verified_receipts': 2,
        'verified_total_krw': 1100,
        'verified_restored_events': restored_events,
        'sqlite_integrity': 'ok',
        'real_customer_test': False,
        'release': 'HOLD',
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0)
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(target, flags, 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return result
