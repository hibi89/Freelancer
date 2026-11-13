"""Run: python -m myradio --help"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import CatalogError, PERSONAS, dj_script, load_catalog, make_example_catalog, select_playlist


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MYRADIO AI: 권한 확인형 로컬 DJ 시제품")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="폴더 WAV를 미승인 목록에 등록")
    init.add_argument("folder", type=Path)
    init.add_argument("--output", type=Path, required=True)
    for name in ("plan", "play"):
        cmd = commands.add_parser(name, help="DJ 선곡·멘트 출력" if name == "plan" else "Windows DJ 멘트 + WAV 실제 재생")
        cmd.add_argument("--catalog", type=Path, required=True)
        cmd.add_argument("--mood", default="")
        cmd.add_argument("--genre", default="")
        cmd.add_argument("--count", type=int, default=5)
        cmd.add_argument("--seed", type=int, default=7)
        cmd.add_argument("--persona", choices=sorted(PERSONAS), default="night")
        cmd.add_argument("--rate", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            n = make_example_catalog(args.folder, args.output)
            print(f"미승인 WAV {n}곡 등록: {args.output} (허가 확인 후 각 항목 approved=true로 변경)")
            return 0
        tracks = select_playlist(load_catalog(args.catalog), mood=args.mood, genre=args.genre, count=args.count, seed=args.seed)
        if not tracks:
            print("재생 가능하다고 확인된 곡이 없습니다. 출처/권한/필터를 검토하세요.", file=sys.stderr)
            return 2
        for n, track in enumerate(tracks, 1):
            line = dj_script(track, args.persona)
            print(f"[{n}] {line}\n    출처/권한: {track.attribution}")
            if args.command == "play":
                from .playback import play_wav_windows, speak_windows
                speak_windows(line, rate=args.rate)
                play_wav_windows(track.path)
        return 0
    except (CatalogError, ValueError, OSError, RuntimeError, TimeoutError) as exc:
        print(f"MYRADIO 오류: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
