"""Windows built-in sound demo. NOT a natural neural DJ voice model."""
from __future__ import annotations

import subprocess
import sys
import wave
from pathlib import Path


def speak_windows(text: str, rate: int = 0) -> None:
    """Use Windows SAPI through PowerShell; feed untrusted text on stdin (not shell code)."""
    if sys.platform != "win32":
        raise RuntimeError("음성 시연은 Windows에 설치된 SAPI 음성이 필요합니다")
    if not -5 <= rate <= 5:
        raise ValueError("속도 범위는 -5~5")
    script = (
        "[Console]::InputEncoding=[System.Text.Encoding]::UTF8; "
        "Add-Type -AssemblyName System.Speech; "
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Rate={rate}; "
        "$s.Speak([Console]::In.ReadToEnd()); $s.Dispose()"
    )
    process = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        input=text, text=True, encoding="utf-8", capture_output=True, timeout=120, check=False,
    )
    if process.returncode:
        raise RuntimeError("Windows TTS 실행 실패. 한국어 음성팩 설치를 확인하세요")


def play_wav_windows(path: str | Path) -> None:
    if sys.platform != "win32":
        raise RuntimeError("음악 재생 시연은 Windows용입니다")
    path = Path(path)
    # Check header before passing data to the OS playback API.
    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() not in (1, 2) or wav.getsampwidth() not in (1, 2, 3, 4):
            raise ValueError("지원하지 않는 WAV 채널·샘플 크기")
    import winsound
    winsound.PlaySound(str(path), winsound.SND_FILENAME)
