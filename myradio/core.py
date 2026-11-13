"""Local rights-aware catalog, deterministic playlist, and script engine.

This module never makes a network request or downloads audio.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

ALLOWED_LICENSES = frozenset({"CC0-1.0", "CC-BY-4.0", "LOCAL-USER"})
PERSONAS = {
    "night": ("심야 감성", "차분히 쉬어 가는 밤입니다. 다음 곡은 {title}, {artist}의 음악이에요."),
    "morning": ("아침 활력", "좋은 아침입니다! {artist}의 {title}으로 기분 좋게 시작해 볼까요?"),
    "classic": ("클래식 FM", "잠시 음악에 귀를 기울여 보시죠. {artist}의 {title}입니다."),
    "friend": ("친근한 친구", "이번 곡 꽤 괜찮아. {artist}의 {title}, 같이 들어보자."),
    "jazz": ("재즈 바", "오늘의 분위기에 어울리는 한 곡, {artist}의 {title}입니다."),
}


class CatalogError(ValueError):
    """A local catalog item cannot safely be used."""


@dataclass(frozen=True)
class Track:
    path: Path
    title: str
    artist: str
    genre: str
    moods: tuple[str, ...]
    license: str
    license_url: str
    source_url: str
    approved: bool

    @property
    def attribution(self) -> str:
        if self.license == "CC-BY-4.0":
            return f"{self.title} — {self.artist} | {self.license} | {self.source_url}"
        if self.license == "CC0-1.0":
            return f"{self.title} — {self.artist} | CC0 | {self.source_url}"
        return f"{self.title} — {self.artist} | 개인 로컬 파일(재배포 권한 없음)"


def load_catalog(file: str | Path) -> list[Track]:
    """Require manual rights approval; reject traversal, remote URLs and non-WAV files.

    CC labels must also have a traceable track source URL and license URL.
    LOCAL-USER is for user-owned local playback; it is not a redistribution grant.
    """
    catalog_path = Path(file).resolve(strict=True)
    root = catalog_path.parent
    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise CatalogError(f"카탈로그 JSON 오류: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("tracks"), list):
        raise CatalogError("카탈로그에 tracks 배열이 필요합니다")
    result: list[Track] = []
    for index, data in enumerate(payload["tracks"], 1):
        if not isinstance(data, dict):
            raise CatalogError(f"{index}번 곡 형식 오류")
        if data.get("approved") is not True:
            continue
        license_name = str(data.get("license", ""))
        if license_name not in ALLOWED_LICENSES:
            raise CatalogError(f"{index}번 곡: 이용 권한이 확인되지 않았습니다")
        raw_path = data.get("path")
        if not isinstance(raw_path, str) or not raw_path or "://" in raw_path:
            raise CatalogError(f"{index}번 곡: 로컬 상대경로만 허용됩니다")
        relative_path = Path(raw_path)
        if relative_path.is_absolute():
            raise CatalogError(f"{index}번 곡: 절대경로는 금지됩니다")
        path = (root / relative_path).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.suffix.lower() != ".wav":
            raise CatalogError(f"{index}번 곡: 경로 이탈·미존재 또는 비지원 WAV")
        if path.stat().st_size > 200 * 1024 * 1024:
            raise CatalogError(f"{index}번 곡: 크기 제한 200MB 초과")
        title, artist = (str(data.get(k, "")).strip() for k in ("title", "artist"))
        if not title or not artist:
            raise CatalogError(f"{index}번 곡: 곡명·아티스트 누락")
        license_url = str(data.get("license_url", "")).strip()
        source_url = str(data.get("source_url", "")).strip()
        if license_name != "LOCAL-USER" and not (license_url.startswith("https://") and source_url.startswith("https://")):
            raise CatalogError(f"{index}번 곡: 추적 가능한 라이선스/출처 URL 필요")
        moods = data.get("moods", [])
        if not isinstance(moods, list) or not all(isinstance(m, str) for m in moods):
            raise CatalogError(f"{index}번 곡: moods는 문자열 배열이어야 합니다")
        result.append(Track(
            path=path, title=title, artist=artist,
            genre=str(data.get("genre", "other")).strip().lower(),
            moods=tuple(m.lower() for m in moods),
            license=license_name, license_url=license_url,
            source_url=source_url, approved=True,
        ))
    return result


def select_playlist(tracks: list[Track], *, mood: str = "", genre: str = "", count: int = 5, seed: int = 7) -> list[Track]:
    if not 1 <= count <= 100:
        raise ValueError("선곡 수는 1~100개")
    mood, genre = mood.strip().lower(), genre.strip().lower()
    candidates = [t for t in tracks if (not mood or mood in t.moods) and (not genre or genre == t.genre)]
    if not candidates:
        return []
    rng = random.Random(seed)
    rng.shuffle(candidates)
    return candidates[:count]


def dj_script(track: Track, persona: str = "night") -> str:
    if persona not in PERSONAS:
        raise ValueError("지원하지 않는 DJ 스타일")
    # No generated claims about the artist or track. Titles are local user metadata.
    return PERSONAS[persona][1].format(title=track.title, artist=track.artist)


def make_example_catalog(directory: str | Path, output: str | Path) -> int:
    """Stage local WAV tracks as unapproved. Never auto-grant music rights."""
    folder = Path(directory).resolve(strict=True)
    destination = Path(output)
    if destination.exists():
        raise FileExistsError("기존 카탈로그를 덮어쓸 수 없습니다")
    if not folder.is_dir():
        raise NotADirectoryError(folder)
    if destination.parent.resolve() != folder:
        raise ValueError("카탈로그는 음악 폴더 바로 아래에 생성하세요")
    tracks = []
    for path in sorted(folder.glob("*.wav")):
        if path.is_symlink() or not path.is_file():
            continue
        tracks.append({"path": path.name, "title": path.stem, "artist": "미입력", "genre": "other", "moods": [], "license": "", "license_url": "", "source_url": "", "approved": False})
    destination.write_text(json.dumps({"tracks": tracks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(tracks)
