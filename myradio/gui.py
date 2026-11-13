"""Minimal offline Windows GUI prototype; no internet access or bundled music."""
from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .core import PERSONAS, dj_script, load_catalog, select_playlist
from .playback import play_wav_windows, speak_windows


class RadioWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MYRADIO AI — 로컬 DJ 시제품")
        self.root.geometry("740x550")
        self.catalog = tk.StringVar()
        self.persona = tk.StringVar(value="night")
        self.mood = tk.StringVar()
        self.genre = tk.StringVar()
        self.count = tk.IntVar(value=5)
        self.messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self.stop_event = threading.Event()
        self.working = False
        wrapper = ttk.Frame(root, padding=18)
        wrapper.pack(fill="both", expand=True)
        ttk.Label(wrapper, text="MYRADIO — 내 음악으로 만드는 개인 라디오", font=("Malgun Gothic", 16, "bold")).pack(anchor="w")
        ttk.Label(wrapper, text="로컬 WAV만 사용 · 라이선스 확인된 곡만 선택 · Windows 기본 TTS 시연").pack(anchor="w", pady=(4, 12))
        row = ttk.Frame(wrapper)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.catalog, state="readonly").pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="카탈로그 선택", command=self.choose).pack(side="left", padx=(8, 0))
        options = ttk.Frame(wrapper)
        options.pack(fill="x", pady=10)
        for label, variable, options_list in (
            ("DJ 목소리 스타일", self.persona, list(PERSONAS)),
            ("기분(예: calm)", self.mood, None),
            ("장르(예: jazz)", self.genre, None),
        ):
            box = ttk.Frame(options)
            box.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ttk.Label(box, text=label).pack(anchor="w")
            if options_list:
                ttk.Combobox(box, textvariable=variable, values=options_list, state="readonly", width=18).pack(fill="x")
            else:
                ttk.Entry(box, textvariable=variable, width=18).pack(fill="x")
        buttons = ttk.Frame(wrapper)
        buttons.pack(fill="x", pady=6)
        ttk.Button(buttons, text="선곡/멘트 미리보기", command=self.preview).pack(side="left")
        ttk.Button(buttons, text="방송 재생", command=self.play).pack(side="left", padx=8)
        ttk.Button(buttons, text="다음 곡부터 중지", command=self.stop).pack(side="left")
        ttk.Label(buttons, text="곡 수").pack(side="left", padx=(18, 5))
        ttk.Spinbox(buttons, from_=1, to=20, textvariable=self.count, width=4).pack(side="left")
        self.output = tk.Text(wrapper, height=18, wrap="word", state="disabled")
        self.output.pack(fill="both", expand=True, pady=(10, 4))
        ttk.Label(wrapper, text="※ 상용 TTS·자동 음원 검색·AI 생성 멘트는 아직 연결되지 않았습니다.").pack(anchor="w")
        self.root.after(100, self.poll)

    def choose(self):
        file = filedialog.askopenfilename(title="MYRADIO 카탈로그", filetypes=[("JSON", "*.json")])
        if file:
            self.catalog.set(file)

    def log(self, text: str):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def playlist(self):
        if not self.catalog.get():
            raise ValueError("카탈로그를 먼저 선택하세요")
        return select_playlist(load_catalog(Path(self.catalog.get())), mood=self.mood.get(), genre=self.genre.get(), count=self.count.get())

    def preview(self):
        try:
            tracks = self.playlist()
            self.log(f"선택된 곡: {len(tracks)}개")
            for track in tracks:
                self.log(f"DJ: {dj_script(track, self.persona.get())}\n출처: {track.attribution}\n")
        except (ValueError, OSError) as exc:
            messagebox.showerror("선곡 오류", str(exc))

    def play(self):
        if self.working:
            return
        try:
            tracks = self.playlist()
            if not tracks:
                raise ValueError("사용이 승인된 곡이 없습니다")
            persona = self.persona.get()
        except (ValueError, OSError) as exc:
            messagebox.showerror("재생 불가", str(exc))
            return
        self.stop_event.clear()
        self.working = True
        threading.Thread(target=self.play_worker, args=(tracks, persona), daemon=True).start()

    def play_worker(self, tracks, persona):
        try:
            for track in tracks:
                if self.stop_event.is_set():
                    break
                self.messages.put(("log", "방송: " + dj_script(track, persona)))
                speak_windows(dj_script(track, persona))
                if self.stop_event.is_set():
                    break
                play_wav_windows(track.path)
        except Exception as exc:
            self.messages.put(("error", str(exc)))
        finally:
            self.messages.put(("done", "방송 종료"))

    def stop(self):
        self.stop_event.set()
        self.log("중지 요청됨. 현재 재생 중인 곡이 끝나면 정지합니다.")

    def poll(self):
        try:
            while True:
                kind, message = self.messages.get_nowait()
                self.log(message)
                if kind == "error":
                    messagebox.showerror("재생 오류", message)
                elif kind == "done":
                    self.working = False
        except queue.Empty:
            pass
        self.root.after(100, self.poll)


def main():
    root = tk.Tk()
    RadioWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
