"""Human-controlled offline desktop UI; never contacts a remote server.

Tkinter is imported only when launch() runs; core logic is headless-testable.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4
from .core import BidLedger, KST, validate_profile
from .workflow import build_report, due_alerts, write_new_report, read_local_json


class LocalController:
    def __init__(self, database: str | Path):
        self.database = Path(database)
        self.profile: dict | None = None
        self.last_report: dict | None = None

    def load_profile(self, path: str | Path) -> dict:
        loaded = read_local_json(path)
        self.profile = validate_profile(loaded)
        self.last_report = None
        return self.profile

    def save_current_profile(self) -> dict:
        if self.profile is None:
            raise ValueError("먼저 기업 프로필 JSON을 불러오세요")
        with BidLedger(self.database) as ledger:
            return ledger.save_profile(self.profile)

    def stored_profiles(self) -> list[dict]:
        with BidLedger(self.database) as ledger:
            return ledger.list_profiles()

    def use_stored_profile(self, company: str) -> dict:
        with BidLedger(self.database) as ledger:
            self.profile = ledger.get_profile(company)
        self.last_report = None
        return self.profile

    def import_notices(self, path: str | Path) -> dict:
        records = read_local_json(path)
        with BidLedger(self.database) as ledger:
            result = ledger.ingest(records)
        self.last_report = None
        return result

    def import_onbid(self, path: str | Path) -> dict:
        from .onbid import OnbidStore
        with OnbidStore(self.database) as store:
            return store.import_snapshot(read_local_json(path))

    def onbid_report(self) -> dict:
        from .onbid import OnbidStore
        with OnbidStore(self.database) as store:
            return store.report()

    def import_court(self, path: str | Path, case_id: str, source_note: str, *, consent: bool) -> dict:
        from .court import CourtStore
        with CourtStore(self.database) as store:
            return store.import_document(path, case_id=case_id, source_note=source_note, user_consent=consent)

    def court_report(self, case_id: str) -> dict:
        from .court import CourtStore
        with CourtStore(self.database) as store:
            return store.case_report(case_id)

    def screen(self) -> dict:
        if self.profile is None:
            raise ValueError("기업 프로필을 먼저 선택하세요")
        with BidLedger(self.database) as ledger:
            self.last_report = build_report(ledger, self.profile)
        return self.last_report

    def history(self, notice_no: str) -> dict:
        with BidLedger(self.database) as ledger:
            return {"changes": ledger.changes(notice_no), "reviews": ledger.review_history(notice_no)}

    def alerts(self) -> list[dict]:
        with BidLedger(self.database) as ledger:
            return due_alerts(ledger)

    def poll_alerts(self) -> dict:
        from .reminders import poll_due
        with BidLedger(self.database) as ledger:
            return poll_due(ledger)

    def review(self, notice_no: str, fingerprint: str, reviewer: str, decision: str, note: str) -> dict:
        with BidLedger(self.database) as ledger:
            return ledger.record_review(notice_no, fingerprint, reviewer, decision, note,
                                        request_id=uuid4().hex)

    def export(self, path: str | Path, fmt: str) -> None:
        if self.last_report is None:
            raise ValueError("검토 결과를 먼저 생성하세요")
        write_new_report(path, self.last_report, fmt)

    def backup(self, target: str | Path) -> None:
        with BidLedger(self.database) as ledger:
            ledger.backup(target)


def launch(database: str | Path) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
    from .core import restore_backup

    controller = LocalController(database)
    root = tk.Tk()
    root.title("BID AX — 입찰 준비 로컬 사전검토")
    root.geometry("1120x720")
    root.minsize(850, 580)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)
    selected: dict[str, dict] = {}
    state = tk.StringVar(value="오프라인 모드 · 법적 자격 보장 불가 · 실시간 공고 미연동")
    ttk.Label(root, text="BID AX | 원문 확인 전 잠정 검토", font=("Malgun Gothic", 16, "bold")).grid(row=0, column=0, sticky="w", padx=14, pady=10)
    tools = ttk.Frame(root)
    tools.grid(row=1, column=0, sticky="ew", padx=12)

    columns = ("notice_no", "title", "status", "deadline")
    tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse")
    for key, heading, width in zip(columns, ("공고번호", "제목", "잠정 판정", "마감"), (180, 430, 135, 250)):
        tree.heading(key, text=heading)
        tree.column(key, width=width, anchor="w")
    tree.grid(row=2, column=0, sticky="nsew", padx=12, pady=10)
    details = tk.Text(root, height=9, wrap="word")
    details.grid(row=3, column=0, sticky="nsew", padx=12)
    details.configure(state="disabled")
    ttk.Label(root, textvariable=state).grid(row=4, column=0, sticky="w", padx=14, pady=12)

    def show(detail: object):
        details.configure(state="normal")
        details.delete("1.0", "end")
        details.insert("end", json.dumps(detail, ensure_ascii=False, indent=2))
        details.configure(state="disabled")

    def chosen():
        ids = tree.selection()
        if not ids or ids[0] not in selected:
            raise ValueError("공고 한 건을 선택하세요")
        return selected[ids[0]]

    def handle(fn):
        try:
            result = fn()
            if result is not None:
                show(result)
        except Exception as exc:
            messagebox.showerror("BID AX 작업 실패", str(exc))

    def choose_profile():
        path = filedialog.askopenfilename(title="기업 프로필 JSON", filetypes=[("JSON", "*.json")])
        if path:
            profile = controller.load_profile(path)
            state.set("기업 프로필: " + profile["company"])
            return {"company": profile["company"], "mode": "local-only"}

    def save_profile():
        return controller.save_current_profile()

    def choose_stored():
        profiles = controller.stored_profiles()
        if not profiles:
            raise ValueError("저장된 회사 프로필이 없습니다")
        company = simpledialog.askstring("저장된 기업", "기업명을 정확히 입력하세요:\n" +
                                         "\n".join(x["company"] for x in profiles), parent=root)
        if not company:
            return
        loaded = controller.use_stored_profile(company)
        state.set("저장된 기업 프로필: " + loaded["company"])
        return {"company": loaded["company"], "mode": "local-database"}

    def import_file():
        path = filedialog.askopenfilename(title="권한 있는 정규화 공고 JSON", filetypes=[("JSON", "*.json")])
        if path:
            result = controller.import_notices(path)
            state.set(f"입력 {result['received']}건 · 신규 버전 {result['added_versions']}건")
            return result

    def run_screen():
        report = controller.screen()
        tree.delete(*tree.get_children())
        selected.clear()
        for row in report["results"]:
            rid = tree.insert("", "end", values=(row["notice_no"], row.get("title", ""), row["status"], row["deadline"]))
            selected[rid] = row
        state.set(f"사전검토 {report['count']}건 · 적합 {report['summary']['적합']} / 추가확인 {report['summary']['추가 확인 필요']} / 부적합 {report['summary']['부적합']}")
        return report

    def on_select(_event):
        try:
            show(chosen())
        except ValueError:
            return

    tree.bind("<<TreeviewSelect>>", on_select)

    def show_history():
        return controller.history(chosen()["notice_no"])

    def save_report():
        fmt = simpledialog.askstring("보고서 형식", "형식: json / csv / html / pdf", initialvalue="html", parent=root)
        if fmt is None:
            return
        fmt = fmt.lower().strip()
        if fmt not in ("json", "csv", "html", "pdf"):
            raise ValueError("json, csv, html 또는 pdf만 지원")
        filename = filedialog.asksaveasfilename(title="새 보고서 경로", defaultextension="." + fmt,
                                                filetypes=[(fmt.upper(), "*." + fmt)])
        if filename:
            controller.export(filename, fmt)
            return {"saved": filename, "mode": "local-only"}

    def save_backup():
        filename = filedialog.asksaveasfilename(title="새 DB 백업 경로", defaultextension=".db")
        if filename:
            controller.backup(filename)
            return {"backup_created": filename}

    def restore():
        src = filedialog.askopenfilename(title="SQLite 백업 DB 선택", filetypes=[("SQLite DB", "*.db"), ("All", "*")])
        if not src:
            return
        dest = filedialog.asksaveasfilename(title="복원할 새 경로 (기존 DB 덮어쓰기 불가)", defaultextension=".db")
        if dest:
            restore_backup(src, dest)
            return {"restored_to_new_path": dest, "active_database_unchanged": str(controller.database)}

    def poll_reminders():
        result = controller.poll_alerts()
        state.set(f"PC 실행 중 조회: 신규 마감 알림 {result['new_count']}건 · 저장된 중복 알림 제외")
        return result

    def manual_review():
        record = chosen()
        reviewer = simpledialog.askstring("검토자", "담당자 식별명(로컬 기록):", parent=root)
        if not reviewer:
            return
        decision = simpledialog.askstring("수동 검토 결과", "확인 / 보류 / 반려 (법적 입찰 자격 승인 아님)", initialvalue="보류", parent=root)
        if not decision:
            return
        note = simpledialog.askstring("검토 사유", "원문 대조 내역/검토 의견:", parent=root)
        if not note or not messagebox.askyesno("검토 기록 확인", "공고와 원문을 직접 확인했습니까?\n검토 기록은 별도로 남으며 자동 제출하지 않습니다."):
            return
        return controller.review(record["notice_no"], record["source_fingerprint"], reviewer, decision.strip(), note)

    def onbid_import():
        path = filedialog.askopenfilename(title="권한 있는 온비드 정규화 JSON",filetypes=[("JSON", "*.json")])
        return controller.import_onbid(path) if path else None

    def onbid_show():
        return controller.onbid_report()

    def court_import():
        path = filedialog.askopenfilename(title="적법 보유 법원 문서", filetypes=[("Documents", "*.txt *.pdf")])
        if not path:
            return
        case_id = simpledialog.askstring("사건번호", "공식 사건번호를 입력하세요", parent=root)
        if not case_id:
            return
        note = simpledialog.askstring("자료 취득 근거", "문서를 적법하게 입수한 경위를 입력하세요",parent=root)
        if not note:
            return
        consent = messagebox.askyesno("법원 자료 로컬 취급 동의", "자료를 로컬 DB에 해시와 체크리스트로만 저장합니다. 원문을 네트워크 전송하지 않으며 법률판단이 아닙니다. 진행합니까?")
        return controller.import_court(path, case_id, note, consent=consent)

    def court_show():
        case_id = simpledialog.askstring("사건번호", "저장된 사건번호", parent=root)
        return controller.court_report(case_id) if case_id else None

    actions = [("공고 가져오기", import_file), ("기업 프로필", choose_profile), ("프로필 저장", save_profile), ("저장 프로필", choose_stored), ("사전검토", run_screen),
               ("변경·검토 이력", show_history), ("마감 알림 확인", poll_reminders),
               ("수동 검토 기록", manual_review), ("보고서 저장", save_report),
               ("온비드 가져오기", onbid_import), ("온비드 현황", onbid_show), ("법원 문서", court_import), ("법원 체크리스트", court_show),
               ("DB 백업", save_backup), ("새 DB로 복원", restore)]
    for label, action in actions:
        ttk.Button(tools, text=label, command=lambda fn=action: handle(fn)).pack(side="left", padx=3, pady=4)
    root.mainloop()
