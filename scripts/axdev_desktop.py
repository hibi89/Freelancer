"""Windows desktop owner console. No HTTP server or cloud dependency.

The requested reference design is a dark three-column local orchestration
workstation. The command bar is an *inert draft inbox* until explicit owner
approval pins scope and independent test oracles.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

from scripts.configure_queue import default_file
from scripts.desktop_commands import (
    approve_draft, inspect_approval, launch_approved, save_draft,
)
from scripts.queue_control import control

NAV_ITEMS = ("현황", "자동화", "검수", "작업 로그", "모델 관리", "보안")
COLORS = {
    "root": "#090e1b", "side": "#101827", "panel": "#141e30",
    "panel2": "#18243a", "stroke": "#30405b", "text": "#e9f0ff",
    "sub": "#9baac4", "purple": "#a58bff", "blue": "#6aafff",
    "green": "#50dfb4", "red": "#ff879a", "amber": "#f4bb78",
    "log": "#0c1424",
}
STATES = ("QUEUED", "CODING", "IMPLEMENTED", "REVIEW", "PREPARED", "VERIFIED", "HOLD")
LABELS = {
    "QUEUED": "대기", "CODING": "코딩 중", "IMPLEMENTED": "구현 후보",
    "REVIEW": "독립 검증", "PREPARED": "커밋 준비",
    "VERIFIED": "검증 통과", "HOLD": "보류",
}


def _safe_events(settings_path: Path, limit: int = 40) -> list[str]:
    """Read only whitelisted event fields; never expose model output or secrets."""
    if not settings_path.is_file():
        return []
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        path = Path(settings["state"]).expanduser().absolute() / "run-events.jsonl"
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            return []
        if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
            return []
        records = path.read_text(encoding="utf-8").splitlines()[-limit:]
        result = []
        for line in records:
            try:
                data = json.loads(line)
            except (ValueError, TypeError):
                continue
            if not isinstance(data, dict):
                continue
            task, status = data.get("task_id"), data.get("status")
            if (isinstance(task, str) and re.fullmatch(r"[A-Z][A-Z0-9_-]{2,39}", task)
                    and status in ("IMPLEMENTED", "VERIFIED", "HOLD")):
                stamp = str(data.get("timestamp_utc", ""))[:19]
                seconds = data.get("duration_seconds", 0)
                duration = (" %.1fs" % seconds) if type(seconds) in (int, float) and 0 <= seconds <= 86400 else ""
                result.append("[%s]  %-13s  %-13s%s" % (stamp, task, status, duration))
        return result
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return []


def _safe_status(settings_path: Path) -> tuple[dict, str | None]:
    try:
        return control("status", settings_path), None
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        empty = {"counts": {s: 0 for s in STATES}, "tasks": {},
                 "stop_requested": False, "model_running": "UNKNOWN",
                 "events_recorded": 0}
        return empty, type(exc).__name__


def _model_label(settings_path: Path) -> str:
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        model = data.get("model")
        if isinstance(model, str) and re.fullmatch(r"ollama/[A-Za-z0-9_.:/-]{2,100}", model):
            return model.replace("ollama/", "")
    except (OSError, ValueError, TypeError):
        pass
    return "미설정"


def _sandbox_configuration(settings_path: Path) -> str:
    """Report only config readiness, never a live Windows Sandbox instance."""
    try:
        obj = json.loads(settings_path.read_text(encoding="utf-8"))
        config = obj.get("sandbox")
        if (isinstance(config, dict) and
                isinstance(config.get("bundle"), str) and
                isinstance(config.get("manifest_sha256"), str) and
                re.fullmatch(r"[a-f0-9]{64}", config["manifest_sha256"]) and
                Path(config["bundle"]).is_dir()):
            return "구성됨"
    except (OSError, ValueError, TypeError):
        return "미확인"
    return "미설정"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AX Dev Factory standalone owner GUI")
    parser.add_argument("--settings", type=Path, default=default_file())
    args = parser.parse_args(argv)
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk

    palette = COLORS
    text_font = ("Malgun Gothic", 10)
    bold_font = ("Malgun Gothic", 10, "bold")
    small_font = ("Malgun Gothic", 9)

    class OwnerApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("AX Dev Factory  |  오프라인 개발 오케스트레이터")
            self.configure(bg=palette["root"])
            self.geometry("1420x880")
            self.minsize(1100, 760)
            self.settings = Path(args.settings).expanduser().absolute()
            self.section = "현황"
            self.draft = None
            self.approved = None
            self._nav = {}
            self._make_widgets()
            self.refresh()
            self.after(5500, self._tick)

        def label(self, parent, title, *, fg=None, size=10, bold=False, bg=None, **opts):
            return tk.Label(parent, text=title, bg=bg or parent["bg"],
                            fg=fg or palette["text"],
                            font=("Malgun Gothic", size, "bold" if bold else "normal"),
                            **opts)

        def button(self, parent, title, action, *, color=None, fg=None, width=None):
            button = tk.Button(parent, text=title, command=action,
                               bg=color or palette["panel2"],
                               fg=fg or palette["text"],
                               activebackground=palette["purple"],
                               activeforeground="#0b1021",
                               relief="flat", bd=0, padx=12, pady=9,
                               font=bold_font, cursor="hand2")
            if width:
                button.configure(width=width)
            return button

        def panel(self, parent, *, bg=None):
            border = tk.Frame(parent, bg=palette["stroke"], padx=1, pady=1)
            content = tk.Frame(border, bg=bg or palette["panel"])
            content.pack(fill="both", expand=True)
            return border, content

        def _make_widgets(self):
            # Native Windows chrome: no browser, no loopback server.
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)
            side = tk.Frame(self, bg=palette["side"], width=200)
            side.grid(row=0, column=0, sticky="ns")
            side.grid_propagate(False)
            self.label(side, "◈  AX Dev Factory", size=16, bold=True).pack(anchor="w", padx=17, pady=(24, 4))
            self.label(side, "오프라인 개발 오케스트레이터", fg=palette["sub"], size=9).pack(anchor="w", padx=18, pady=(0, 28))
            for item in NAV_ITEMS:
                button = self.button(side, "  " + item, lambda x=item: self.set_section(x), width=17)
                button.configure(anchor="w", pady=12)
                button.pack(fill="x", padx=12, pady=3)
                self._nav[item] = button
            tk.Frame(side, bg=palette["side"]).pack(fill="both", expand=True)
            self.label(side, "●  로컬 PC 전용", fg=palette["green"], bold=True).pack(anchor="w", padx=19, pady=(0, 7))
            self.label(side, "클라우드 서버 없음\n실행 계약 변경은 승인 필요", fg=palette["sub"], size=9,
                       justify="left").pack(anchor="w", padx=19, pady=(0, 25))

            content = tk.Frame(self, bg=palette["root"])
            content.grid(row=0, column=1, sticky="nsew", padx=18, pady=14)
            content.grid_columnconfigure(0, weight=1)
            content.grid_rowconfigure(2, weight=1)

            header = tk.Frame(content, bg=palette["root"])
            header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
            self.label(header, "AX Dev Factory", size=18, bold=True).pack(side="left")
            self.label(header, "  |  개인용 로컬 자율개발 제어판",
                       fg=palette["sub"], size=10).pack(side="left")
            self.status_text = self.label(header, "상태 확인 중", fg=palette["amber"], size=10, bold=True)
            self.status_text.pack(side="right")
            self.button(header, "↻ 새로고침", self.refresh).pack(side="right", padx=10)

            top = tk.Frame(content, bg=palette["root"])
            top.grid(row=1, column=0, sticky="ew", pady=(0, 13))
            for i in range(4):
                top.grid_columnconfigure(i, weight=1, uniform="kpi")
            self.kpis = []
            for index, (title, accent) in enumerate((
                    ("작업 검증 통과", palette["green"]),
                    ("보류 · 검토 필요", palette["purple"]),
                    ("로컬 모델 설정", palette["blue"]),
                    ("Sandbox 격리", palette["green"]))):
                outer, card = self.panel(top)
                outer.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0))
                self.label(card, title, fg=palette["sub"], size=10).pack(anchor="w", padx=16, pady=(14, 5))
                value = self.label(card, "—", fg=accent, size=18, bold=True)
                value.pack(anchor="w", padx=16)
                sub = self.label(card, "확인 중", fg=palette["sub"], size=9)
                sub.pack(anchor="w", padx=16, pady=(3, 14))
                self.kpis.append((value, sub))

            middle = tk.Frame(content, bg=palette["root"])
            middle.grid(row=2, column=0, sticky="nsew", pady=(0, 13))
            middle.grid_columnconfigure(0, weight=6)
            middle.grid_columnconfigure(1, weight=5)
            middle.grid_rowconfigure(0, weight=1)

            outer, logs = self.panel(middle)
            outer.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            self.label(logs, "▣  작업 로그  |  로컬 체크포인트",
                       bold=True).pack(anchor="w", padx=15, pady=(13, 10))
            self.log = tk.Text(logs, bg=palette["log"], fg=palette["green"],
                               insertbackground=palette["text"], relief="flat",
                               font=("Consolas", 10), wrap="word", state="disabled",
                               padx=14, pady=12, height=16, selectbackground=palette["stroke"])
            self.log.pack(fill="both", expand=True, padx=11, pady=(0, 10))

            outer, details = self.panel(middle)
            outer.grid(row=0, column=1, sticky="nsew")
            self.detail_title = self.label(details, "◈  작업 상세 / 승인 상태", bold=True)
            self.detail_title.pack(anchor="w", padx=15, pady=(13, 10))
            style = ttk.Style(self)
            style.theme_use("clam")
            style.configure("AX.Treeview", background=palette["panel2"],
                            fieldbackground=palette["panel2"], foreground=palette["text"],
                            rowheight=30, borderwidth=0, font=small_font)
            style.configure("AX.Treeview.Heading", background=palette["stroke"],
                            foreground=palette["text"], relief="flat", font=bold_font)
            style.map("AX.Treeview", background=[("selected", "#39305e")])
            table = ttk.Treeview(details, columns=("id", "state"), show="headings",
                                 height=7, style="AX.Treeview", selectmode="browse")
            table.heading("id", text="작업 ID")
            table.heading("state", text="상태")
            table.column("id", width=160, stretch=True)
            table.column("state", width=110, stretch=False)
            table.pack(fill="both", expand=True, padx=13, pady=(0, 8))
            self.table = table
            self.detail_info = self.label(details, "작업을 선택하면 상태가 표시됩니다.",
                                          fg=palette["sub"], justify="left", anchor="w",
                                          wraplength=490, size=9)
            self.detail_info.pack(fill="x", padx=15, pady=(0, 7))
            table.bind("<<TreeviewSelect>>", self._selected)
            actions = tk.Frame(details, bg=palette["panel"])
            actions.pack(fill="x", padx=12, pady=(0, 12))
            for name, action, color in [
                ("안전 중지 요청", self._stop, "#593445"),
                ("중지 해제", self._resume, "#215c51"),
                ("검증 현황", self._verify_report, "#2b4771"),
            ]:
                self.button(actions, name, action, color=color).pack(
                    side="left", padx=(0, 5))

            footer = tk.Frame(content, bg=palette["root"])
            footer.grid(row=3, column=0, sticky="ew", pady=(0, 13))
            box, timeline = self.panel(footer)
            box.pack(fill="x")
            self.label(timeline, "보안 / 작업 흐름", bold=True).pack(anchor="w", padx=13, pady=(9, 4))
            flow = tk.Frame(timeline, bg=palette["panel"])
            flow.pack(fill="x", padx=13, pady=(0, 10))
            for i, text in enumerate(("승인 계약", "로컬 AI 코딩", "독립 검증", "Sandbox 격리", "Git + SQLite")):
                item = self.label(flow, text, fg=palette["blue"] if i % 2 else palette["green"],
                                  bold=True, size=9)
                item.pack(side="left", expand=True)
                if i < 4:
                    self.label(flow, "→", fg=palette["sub"]).pack(side="left")

            box, commands = self.panel(content)
            box.grid(row=4, column=0, sticky="ew")
            commands.grid_columnconfigure(0, weight=1)
            self.label(commands, "✦  AI 작업 명령 입력",
                       fg=palette["purple"], bold=True, size=12).grid(
                row=0, column=0, sticky="w", padx=14, pady=(10, 2))
            self.label(commands, "한국어로 작성 → 초안 저장 → 변경 범위·검증조건 승인 → 로컬 AI 실행",
                       fg=palette["sub"], size=9).grid(row=1, column=0, sticky="w", padx=14)
            self.command = tk.Text(commands, height=3, bg=palette["log"],
                                   fg=palette["text"], insertbackground=palette["text"],
                                   relief="flat", wrap="word", font=text_font,
                                   padx=12, pady=8, undo=True)
            self.command.grid(row=2, column=0, sticky="ew", padx=12, pady=(8, 9))
            controls = tk.Frame(commands, bg=palette["panel"])
            controls.grid(row=2, column=1, sticky="ns", padx=(0, 12), pady=(8, 9))
            self.button(controls, "1  명령 초안 저장", self._save, color="#45367a").pack(fill="x", pady=(0, 4))
            self.button(controls, "2  계약 검토·승인", self._approve, color="#244f75").pack(fill="x", pady=(0, 4))
            self.button(controls, "3  승인 작업 실행", self._launch, color="#205d51").pack(fill="x")
            self.label(content,
                       "정보는 PC에서만 처리 · 모델 호출은 승인 후 1개 작업만 · 이 화면의 상태는 증거 없는 100%를 표시하지 않습니다",
                       fg=palette["sub"], size=8).grid(row=5, column=0, sticky="w", pady=(7, 0))
            self.set_section("현황")

        def _tick(self):
            if self.winfo_exists():
                self.refresh()
                self.after(5500, self._tick)

        def set_section(self, section):
            self.section = section
            for name, button in self._nav.items():
                button.configure(bg="#443478" if name == section else palette["panel2"])
            self.detail_title.configure(text="◈  " + section + " / 작업 상태")
            if section == "자동화":
                self.command.focus_set()
                self.detail_info.configure(text="아래 명령 입력창에서 작업을 작성하세요. 승인 전에는 모델이 실행되지 않습니다.")
            elif section == "모델 관리":
                self.detail_info.configure(text="설정 모델: " + _model_label(self.settings) +
                                           " / 실제 메모리 상주 및 동작 여부는 별도 검증 대상")
            elif section == "보안":
                self.detail_info.configure(text="Windows Sandbox 네트워크 차단과 AppContainer 독립 검증은 기존 엔진에서 시행. 현재 실행 여부는 추정하지 않습니다.")
            elif section == "작업 로그":
                self.detail_info.configure(text="로컬 이벤트의 허용된 상태 필드만 표시합니다. 모델 원문·토큰은 표시하지 않습니다.")
            elif section == "검수":
                self.detail_info.configure(text="VERIFIED 상태는 로컬 작업별 독립 검증 통과 기록이며 공식 제품 검증 완료율과 다릅니다.")
            else:
                self.detail_info.configure(text="작업 행을 선택하면 상태를 볼 수 있습니다.")

        def refresh(self):
            state, error = _safe_status(self.settings)
            counts = state.get("counts", {})
            verified = max(0, int(counts.get("VERIFIED", 0)))
            held = max(0, int(counts.get("HOLD", 0)))
            total = sum(max(0, int(counts.get(s, 0))) for s in STATES)
            percent = str(round(100 * verified / total)) + "%" if total else "—"
            rows = [
                (percent, str(verified) + " / " + str(total) + " 작업 · 제품 공식 검증률 아님"),
                (str(held), "HOLD 작업 (승인 없이 재시도 안 함)"),
                (_model_label(self.settings), "선택된 Ollama 모델 · 실행 상태 미측정"),
                (_sandbox_configuration(self.settings), "격리 정책은 실행 때 검증 / 자동 성공 주장 금지"),
            ]
            for i, (value, hint) in enumerate(rows):
                self.kpis[i][0].configure(text=value)
                self.kpis[i][1].configure(text=hint)
            self.status_text.configure(
                text=("● 중지 요청됨" if state.get("stop_requested") else
                      "● 상태 연결됨") if error is None else "● 설정·DB 확인 필요",
                fg=palette["amber"] if error or state.get("stop_requested") else palette["green"])
            self.table.delete(*self.table.get_children())
            tasks = state.get("tasks", {})
            if isinstance(tasks, dict):
                for task_id, status in sorted(tasks.items())[:50]:
                    if isinstance(task_id, str) and status in STATES:
                        self.table.insert("", "end", values=(task_id[:40], LABELS[status]))
            events = _safe_events(self.settings)
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            if error:
                self.log.insert("end", "설정 또는 로컬 SQLite 상태를 확인하세요: " + error + "\n")
            self.log.insert("end", "\n".join(events[-40:]) if events
                            else "아직 저장된 로컬 실행 이벤트가 없습니다.\n명령은 아래 입력창에서 작성하세요.")
            self.log.configure(state="disabled")
            self.log.see("end")

        def _selected(self, _event=None):
            selected = self.table.selection()
            if selected:
                task, state = self.table.item(selected[0], "values")
                self.detail_info.configure(text="작업 ID: %s  |  체크포인트: %s\n로컬 SQLite 기록입니다. 실제 모델 호출 결과는 독립 검증 증거로 확인하세요." % (task, state))

        def _stop(self):
            if not messagebox.askyesno("안전 중지", "현재 코딩을 강제 종료하지 않고 다음 작업 경계에서 중지 신호를 설정할까요?"):
                return
            try:
                control("stop", self.settings)
                self.refresh()
            except (OSError, ValueError) as exc:
                messagebox.showerror("중지 실패", type(exc).__name__)

        def _resume(self):
            if not messagebox.askyesno("중지 해제", "중지 신호만 해제합니다. AI 작업은 바로 시작되지 않습니다. 진행할까요?"):
                return
            try:
                control("resume", self.settings, confirm=True)
                self.refresh()
            except (OSError, ValueError) as exc:
                messagebox.showerror("재개 실패", type(exc).__name__)

        def _verify_report(self):
            state, error = _safe_status(self.settings)
            if error:
                messagebox.showwarning("상태 미확인", "로컬 상태 확인 불가: " + error)
                return
            lines = ["로컬 작업 체크포인트 (공식 제품 검증 완료율 아님)"]
            lines += ["%s: %s" % (s, state.get("counts", {}).get(s, 0)) for s in STATES]
            messagebox.showinfo("검증 현황", "\n".join(lines))

        def _save(self):
            goal = self.command.get("1.0", "end-1c").strip()
            try:
                info = json.loads(self.settings.read_text(encoding="utf-8"))
                self.draft = save_draft(goal, Path(info["repo"]))
                self.approved = None
                messagebox.showinfo("초안 저장됨", "명령 ID: " + self.draft["id"] +
                                    "\n비공개 초안으로 저장했습니다. 모델 호출이나 코드 변경은 없습니다.")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                messagebox.showerror("초안 저장 실패", str(exc)[:300])

        def _approve(self):
            if not self.draft:
                messagebox.showwarning("초안 필요", "먼저 아래 입력창에서 명령 초안을 저장하세요.")
                self.command.focus_set()
                return
            files = simpledialog.askstring(
                "승인 범위", "AI가 변경해도 되는 정확한 상대 파일 경로를 쉼표로 구분하세요.\n예: src/hello.py",
                parent=self)
            if files is None:
                return
            paths = [x.strip() for x in files.split(",") if x.strip()]
            text = simpledialog.askstring(
                "독립 검증 계약", "기존 코드와 분리된 수용조건 JSON 배열을 입력하세요.\n"
                '예: [{"module":"src.hello","function":"greet","args":["AX"],"kwargs":{},"expected":"Hello, AX"}]',
                parent=self)
            if text is None:
                return
            try:
                acceptance = json.loads(text)
                if not messagebox.askyesno("작업계약 승인",
                        "명령: " + self.draft["goal"][:180] +
                        "\n변경 허용: " + ", ".join(paths)[:200] +
                        "\n독립 수용조건: " + str(len(acceptance)) +
                        "개\n\n이 내용을 SHA 고정 작업계약으로 승인해 저장할까요?\n아직 AI는 실행되지 않습니다."):
                    return
                self.approved = approve_draft(
                    self.draft["id"], paths, acceptance, source_settings=self.settings)
                messagebox.showinfo("계약 고정됨",
                    "SHA256: " + self.approved["plan_sha256"] +
                    "\n실행은 별도 버튼에서 승인해야 합니다.")
            except (OSError, ValueError, TypeError, KeyError) as exc:
                messagebox.showerror("승인 불가", str(exc)[:450])

        def _launch(self):
            if not self.approved:
                messagebox.showwarning("승인 계약 없음", "먼저 명령 초안을 저장하고 파일·수용조건을 승인하세요.")
                return
            try:
                proof = inspect_approval(Path(self.approved["settings"]))
                if not messagebox.askyesno(
                        "로컬 AI 작업 실행 승인",
                        "작업: " + proof["id"] + "\n모델: " + proof["model"] +
                        "\n변경 허용: " + ", ".join(proof["files"]) +
                        "\n독립 검증: " + str(proof["probe_count"]) + "개" +
                        "\n\nWindows Sandbox에서 승인된 작업 1개를 실행합니다.\n"
                        "무료 로컬 모델만 사용하고, 원본 코드는 분리 보존합니다. 실행할까요?"):
                    return
                root = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
                        else Path(__file__).resolve().parent.parent)
                result = launch_approved(Path(self.approved["settings"]), app_root=root,
                                         frozen=bool(getattr(sys, "frozen", False)))
                self.approved = None
                messagebox.showinfo("작업 프로세스 시작",
                    "PID: " + str(result["pid"]) +
                    "\n작업은 백그라운드에서 실행됩니다. 이 화면의 종료가 작업 성공을 뜻하지 않습니다.\n"
                    "VERIFIED 상태는 별도 확인이 필요합니다.")
            except (OSError, ValueError, TypeError, KeyError) as exc:
                messagebox.showerror("실행 거부", str(exc)[:400])

    app = OwnerApp()
    app.mainloop()
    return 0


def entrypoint() -> int:
    # An EXE can start its own separate worker process without a Python console.
    if len(sys.argv) >= 2 and sys.argv[1] == "--axdev-selfcheck":
        import tkinter
        from axdev.windows_sandbox_runtime import run_sandbox_queue
        from scripts.desktop_commands import inspect_approval
        print("AXDEV_DESKTOP_EXE_SELF_CHECK: PASS")
        return 0
    if len(sys.argv) >= 2 and sys.argv[1] == "--axdev-worker":
        from scripts.run_configured_queue import main as run_queue
        return run_queue(sys.argv[2:])
    return main()


if __name__ == "__main__":
    raise SystemExit(entrypoint())
