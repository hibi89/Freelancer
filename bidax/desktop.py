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

    def portfolio_report(self) -> dict:
        from .portfolio import portfolio_report
        return portfolio_report(self.database)

    def onbid_filter(self, *, property_type: str | None = None,
                     max_bid_krw: int | None = None, min_failed_rounds: int | None = None) -> dict:
        from .portfolio import filter_onbid
        return filter_onbid(self.database, property_type=property_type,
                            max_bid_krw=max_bid_krw, min_failed_rounds=min_failed_rounds)

    def onbid_watchlist(self) -> dict:
        from .portfolio import watchlist
        return watchlist(self.database)

    def onbid_stage_page(self, batch_id: str, packet_file: str | Path, *, consent: bool) -> dict:
        """Record an already quarantined official page; no network or auto-import."""
        from .onbid_batch import stage_page
        return stage_page(self.database, batch_id, packet_file, consent=consent)

    def onbid_stage_status(self, batch_id: str) -> dict:
        """Reverify the saved local packets without changing the evidence database."""
        from .onbid_batch import batch_status
        return batch_status(self.database, batch_id)

    def onbid_watch(self, property_id: str, condition_id: str, state: str, note: str) -> dict:
        from .portfolio import watch_onbid
        return watch_onbid(self.database, property_id=property_id, condition_id=condition_id,
                            state=state, note=note, request_id=str(uuid4()))

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
    # A single horizontal row hid most commands on ordinary Windows displays.
    # Keep every local action visible without horizontal scrolling.
    for index, (label, action) in enumerate(actions):
        ttk.Button(tools, text=label, command=lambda fn=action: handle(fn)).grid(
            row=index // 5, column=index % 5, sticky="ew", padx=3, pady=3)
    for index in range(5):
        tools.columnconfigure(index, weight=1)
    def save_interest():
        prop = simpledialog.askstring("온비드 관심물건", "로컬 온비드 물건관리번호", parent=root)
        if not prop:
            return
        cond = simpledialog.askstring("온비드 공매조건", "공매조건번호", parent=root)
        if not cond:
            return
        state_text = simpledialog.askstring("사람의 관심 상태", "관심 / 검토 보류 / 관심 해제", parent=root)
        if not state_text:
            return
        memo = simpledialog.askstring("원문 확인 메모", "직접 검토 계획을 기록하세요", parent=root)
        if not memo:
            return
        if not messagebox.askyesno("기록 확인", "온비드 로컬 사본에 대한 관심 메모만 기록합니다. 실제 권리/가격/낙찰 상태를 보증하지 않습니다. 진행합니까?"):
            return
        return controller.onbid_watch(prop.strip(), cond.strip(), state_text.strip(), memo)

    def search_onbid():
        max_value = simpledialog.askstring("온비드 최소입찰가 필터", "검색할 최대 최저입찰가(원, 공란이면 전체)", parent=root)
        if max_value is None:
            return
        max_krw = int(max_value) if max_value.strip() else None
        return controller.onbid_filter(max_bid_krw=max_krw)

    def stage_onbid_page():
        identity = simpledialog.askstring(
            "온비드 오프라인 증빙",
            "새 배치는 표시된 UUID를 사용하세요. 중단 후 재개할 때는 기존 UUID를 입력하세요.",
            initialvalue=str(uuid4()), parent=root)
        if not identity:
            return
        path = filedialog.askopenfilename(
            title="이미 보유한 온비드 결과목록 격리 JSON", filetypes=[("JSON", "*.json")])
        if not path:
            return
        if not messagebox.askyesno(
            "오프라인 원본 경로 보관 동의",
            "고객 PC의 SQLite에 이 JSON의 로컬 절대경로, SHA-256, 건수만 기록합니다.\n"
            "원본 값이나 API 키는 DB에 넣지 않습니다. 네트워크 요청/공고 판정도 없습니다.\n"
            "해당 경로 저장에 동의합니까?"):
            return
        result = controller.onbid_stage_page(identity.strip(), path, consent=True)
        state.set(
            f"온비드 오프라인 증빙: {len(result['verified_local_pages'])}/{result['reported_total_pages']}페이지 확인 · "
            "원문 자동반영 금지")
        return result

    def show_onbid_stage_status():
        identity = simpledialog.askstring(
            "온비드 오프라인 증빙 조회", "기존 증빙 배치 UUID를 입력하세요.", parent=root)
        if not identity:
            return
        result = controller.onbid_stage_status(identity.strip())
        state.set(
            f"온비드 증빙 재검사: {len(result['verified_local_pages'])}/{result['reported_total_pages']}페이지 · "
            "공식 필드 매핑/법적 판정 미검증")
        return result

    menu = tk.Menu(root)
    auction_menu = tk.Menu(menu, tearoff=0)
    auction_menu.add_command(label="3개 출처 통합 현황", command=lambda: handle(controller.portfolio_report))
    auction_menu.add_command(label="온비드 관심목록", command=lambda: handle(controller.onbid_watchlist))
    auction_menu.add_command(label="온비드 관심 상태 기록", command=lambda: handle(save_interest))
    auction_menu.add_command(label="온비드 가격 필터", command=lambda: handle(search_onbid))
    auction_menu.add_separator()
    auction_menu.add_command(label="온비드 격리 페이지 등록(로컬)", command=lambda: handle(stage_onbid_page))
    auction_menu.add_command(label="온비드 증빙 배치 재검사", command=lambda: handle(show_onbid_stage_status))
    menu.add_cascade(label="공매·경매 로컬 관리", menu=auction_menu)
    root.config(menu=menu)
    root.mainloop()
