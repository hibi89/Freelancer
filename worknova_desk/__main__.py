"""Local-only command line; the operator owns and protects the SQLite database."""
import argparse
import json
import sys
from pathlib import Path

from .core import Desk, DeskError, restore_new
from .documents import export_document


def main(argv=None):
    parser = argparse.ArgumentParser(prog="worknova_desk", description="Offline quote-to-collection ledger (not a payment provider)")
    parser.add_argument("--db", required=True, help="SQLite path in an existing local folder")
    sub = parser.add_subparsers(dest="command", required=True)

    def cmd(name, *fields):
        p = sub.add_parser(name)
        for field, required in fields:
            p.add_argument("--" + field.replace("_", "-"), required=required)
        return p

    sub.add_parser("init")
    cmd("customer", ("name", True))
    q = cmd("quote", ("customer_id", True), ("items_json", True)); q.add_argument("--no-vat", action="store_true")
    cmd("approve-quote", ("quote_id", True), ("actor", True))
    rev = cmd("revise-quote", ("quote_id", True), ("items_json", True), ("actor", True)); rev.add_argument("--no-vat", action="store_true")
    cmd("quote-history", ("quote_id", True))
    quote_preview = cmd("quote-preview", ("quote_id", True), ("out", True))
    cmd("list-customers", ("search", False))
    cmd("list-quotes", ("customer_id", True))
    cmd("list-contracts", ("customer_id", True))
    cmd("list-milestones", ("contract_id", True))
    cmd("contract", ("quote_id", True), ("scope", True), ("steps_json", True))
    cmd("activate", ("contract_id", True), ("actor", True))
    cmd("deliver", ("milestone_id", True), ("actor", True), ("note", True))
    cmd("revision", ("milestone_id", True), ("actor", True), ("reason", True))
    cmd("accept", ("milestone_id", True), ("actor", True))
    cmd("collect", ("milestone_id", True), ("actor", True), ("amount_krw", True), ("reference", True))
    r = cmd("report", ("contract_id", True)); r.add_argument("--html-out")
    document = sub.add_parser("export-document", help="Local redacted-by-default DOCX/PDF report; never sends data")
    document.add_argument("--type", required=True, choices=("quote", "contract"))
    document.add_argument("--id", required=True)
    document.add_argument("--out", required=True)
    document.add_argument("--format", choices=("docx", "pdf"), required=True)
    document.add_argument("--pdf-font", help="PDF only: user-supplied Korean TTF; font rights remain user's responsibility")
    document.add_argument("--include-customer", action="store_true", help="Include customer name in output; requires --confirm-disclosure")
    document.add_argument("--confirm-disclosure", action="store_true", help="Explicit permission to disclose customer name")
    sub.add_parser("verify")
    cmd("backup", ("out", True))
    cmd("migrate-v1", ("backup_out", True))
    cmd("restore-new", ("backup_file", True), ("new_db", True), ("sha256", True))
    args = parser.parse_args(argv)
    desk = None
    try:
        if args.command == "restore-new":
            result = restore_new(args.backup_file, args.new_db, args.sha256)
            print(json.dumps({"ok": True, "result": result}, ensure_ascii=False, sort_keys=True))
            return 0
        desk = Desk(args.db)
        c = args.command
        value = None
        if c == "init": value = {"schema_version": desk.schema_version}
        elif c == "customer": value = {"customer_id": desk.add_customer(args.name)}
        elif c == "quote": value = {"quote_id": desk.new_quote(args.customer_id, json.loads(args.items_json), taxable=not args.no_vat)}
        elif c == "approve-quote": desk.approve_quote(args.quote_id, args.actor)
        elif c == "revise-quote": value = {"quote_id": desk.revise_quote(args.quote_id, json.loads(args.items_json), taxable=not args.no_vat, actor=args.actor)}
        elif c == "quote-history": value = desk.quote_history(args.quote_id)
        elif c == "list-customers": value = desk.list_customers(args.search or "")
        elif c == "list-quotes": value = desk.list_quotes(args.customer_id)
        elif c == "list-contracts": value = desk.list_contracts(args.customer_id)
        elif c == "list-milestones": value = desk.list_milestones(args.contract_id)
        elif c == "quote-preview":
            path = Path(args.out)
            if path.exists() or path.is_symlink() or not path.parent.is_dir():
                raise DeskError("quote preview requires a new local output path")
            path.write_text(desk.export_quote_html(args.quote_id), encoding="utf-8")
            value = {"quote_preview_created": True}
        elif c == "contract": value = {"contract_id": desk.new_contract(args.quote_id, args.scope, json.loads(args.steps_json))}
        elif c == "activate": desk.activate_contract(args.contract_id, args.actor)
        elif c == "deliver": desk.deliver(args.milestone_id, args.actor, args.note)
        elif c == "revision": desk.request_revision(args.milestone_id, args.actor, args.reason)
        elif c == "accept": desk.accept(args.milestone_id, args.actor)
        elif c == "collect": value = {"receipt_id": desk.record_collection(args.milestone_id, int(args.amount_krw), args.reference, args.actor)}
        elif c == "report":
            value = desk.report(args.contract_id)
            if args.html_out:
                path = Path(args.html_out)
                if path.exists() or path.is_symlink() or not path.parent.is_dir():
                    raise DeskError("HTML export requires a new local output path")
                path.write_text(desk.export_html(args.contract_id), encoding="utf-8")
                value["html_created"] = True
        elif c == "export-document":
            value = export_document(desk, args.type, args.id, args.out,
                         format=args.format, pdf_font=args.pdf_font,
                         include_customer=args.include_customer,
                         confirm_disclosure=args.confirm_disclosure)
        elif c == "verify": value = {"verified_events": desk.verify_audit()}
        elif c == "backup": value = {"backup_sha256": desk.backup(args.out)}
        elif c == "migrate-v1": value = {"backup_sha256": desk.migrate_v1(args.backup_out), "schema_version": desk.schema_version}
        print(json.dumps({"ok": True, "result": value}, ensure_ascii=False, sort_keys=True))
        return 0
    except (DeskError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        if desk is not None:
            desk.close()


if __name__ == "__main__":
    raise SystemExit(main())
