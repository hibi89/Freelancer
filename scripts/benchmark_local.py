"""Bounded model throughput sample against Ollama's *loopback* API only.

Never reads source files, sends customer data, downloads models, or publishes
reports. Actual local inference requires explicit --execute opt-in.
"""
from __future__ import annotations
import argparse
import ctypes
import os
import threading
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

MODEL = re.compile(r"^ollama/[a-zA-Z0-9_.:/-]{2,100}$")
PROMPT = "Return exactly one word: OK."


def _sample_gpu():
    if not shutil.which("nvidia-smi"):
        return None
    try:
        p = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5,
                           check=False, shell=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout.strip()[:250] if p.returncode == 0 else None


def _windows_ram_snapshot():
    """Physical RAM only; process peak memory needs separate host proof."""
    if os.name != "nt":
        return None
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    info = MemoryStatus()
    info.dwLength = ctypes.sizeof(MemoryStatus)
    try:
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
            return None
    except (AttributeError, OSError):
        return None
    return {"total_mib": info.ullTotalPhys // (1024 * 1024),
            "available_mib": info.ullAvailPhys // (1024 * 1024)}


def _gpu_memory_used(raw):
    if not isinstance(raw, str):
        return None
    row = raw.splitlines()[0].split(",") if raw.strip() else []
    if len(row) != 3:
        return None
    try:
        used, total = int(row[1].strip()), int(row[2].strip())
    except ValueError:
        return None
    if 0 <= used <= total and total > 0:
        return used
    return None


class _GpuPeakSampler:
    def __init__(self):
        self._stop = threading.Event()
        self.highest = None
        self._thread = threading.Thread(target=self._poll, daemon=True)

    def _poll(self):
        while not self._stop.is_set():
            value = _gpu_memory_used(_sample_gpu())
            if value is not None:
                self.highest = value if self.highest is None else max(self.highest, value)
            self._stop.wait(0.25)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *_):
        self._stop.set()
        self._thread.join(timeout=6)


def _ollama_generate(model_id):
    payload = json.dumps({
        "model": model_id, "prompt": PROMPT, "stream": False,
        "options": {"num_predict": 16, "temperature": 0.0},
    }).encode("utf-8")
    request = Request("http://127.0.0.1:11434/api/generate",
                      data=payload, method="POST",
                      headers={"Content-Type": "application/json"})
    opener = build_opener(ProxyHandler({}))
    with opener.open(request, timeout=120) as response:
        if response.status != 200:
            raise RuntimeError("Ollama localhost generation returned non-200")
        raw = response.read(65537)
    if len(raw) > 65536:
        raise RuntimeError("Ollama generation response too large")
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("done") is not True:
        raise RuntimeError("Ollama did not complete bounded generation")
    return data


def benchmark(model, execute=False, sender=None, clock=None, gpu_reader=None):
    if not MODEL.fullmatch(model):
        raise ValueError("only explicit local ollama/<model> identifiers are allowed")
    model_id = model.removeprefix("ollama/")
    result = {"model": model, "localhost_only": True,
              "prompt_kind": "fixed_public_synthetic_text",
              "execution_requested": bool(execute), "model_e2e_verified": False}
    if not execute:
        return dict(result, status="DRY_RUN", note="add --execute for local inference")
    sender = sender or _ollama_generate
    clock = clock or time.perf_counter
    real_gpu_sampler = gpu_reader is None
    gpu_reader = gpu_reader or _sample_gpu
    before = gpu_reader()
    ram_before = _windows_ram_snapshot()
    began = clock()
    peak = None
    if real_gpu_sampler:
        with _GpuPeakSampler() as monitor:
            response = sender(model_id)
        peak = monitor.highest
    else:
        response = sender(model_id)
    elapsed = max(0.0, clock() - began)
    after = gpu_reader()
    ram_after = _windows_ram_snapshot()
    duration = response.get("eval_duration")
    count = response.get("eval_count")
    if (not isinstance(duration, int) or not isinstance(count, int)
            or duration <= 0 or count < 0 or response.get("done") is not True):
        raise RuntimeError("Ollama response missing completed generation counters")
    tok_per_sec = round((count * 1_000_000_000) / duration, 2)
    return dict(result, status="LOCAL_INFERENCE_COMPLETE", model_e2e_verified=True,
                elapsed_seconds=round(elapsed, 2), generated_tokens=count,
                eval_tokens_per_second=tok_per_sec,
                prompt_tokens=response.get("prompt_eval_count"),
                response_text_saved=False, gpu_snapshot_before=before,
                gpu_snapshot_after=after, gpu_peak_vram_used_mib=peak,
                gpu_peak_vram_measured=peak is not None,
                windows_ram_before=ram_before, windows_ram_after=ram_after,
                opencode_tool_permissions_verified=False)


def main(argv=None):
    p = argparse.ArgumentParser(description="Local synthetic Ollama speed probe")
    p.add_argument("--model", default="ollama/qwen3:4b-instruct")
    p.add_argument("--execute", action="store_true",
                   help="run bounded synthetic inference on local 127.0.0.1 Ollama")
    p.add_argument("--output", type=Path, help="optional NEW private JSON evidence file")
    args = p.parse_args(argv)
    report = benchmark(args.model, args.execute)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        output = args.output.expanduser().absolute()
        if output.is_symlink():
            raise ValueError("output symlink forbidden")
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    print(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, TimeoutError) as exc:
        print("AXDEV_BENCHMARK_ERROR:", str(exc))
        raise SystemExit(2)
