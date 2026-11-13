import json
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from myradio.core import CatalogError, PERSONAS, dj_script, load_catalog, make_example_catalog, select_playlist
from myradio.__main__ import main


class RadioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.music = self.root / "test.wav"
        with wave.open(str(self.music), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(8000)
            f.writeframes(struct.pack("<h", 0) * 16)
        self.catalog = self.root / "catalog.json"
        self.item = {"path": "test.wav", "title": "작은 음악", "artist": "본인", "genre": "jazz", "moods": ["calm"], "license": "LOCAL-USER", "approved": True}

    def write(self, items):
        self.catalog.write_text(json.dumps({"tracks": items}, ensure_ascii=False), encoding="utf-8")

    def test_init_is_unapproved(self):
        count = make_example_catalog(self.root, self.catalog)
        self.assertEqual(count, 1)
        self.assertEqual(load_catalog(self.catalog), [])
        with self.assertRaises(FileExistsError):
            make_example_catalog(self.root, self.catalog)

    def test_plan_deterministic_and_licenses(self):
        self.write([self.item])
        tracks = load_catalog(self.catalog)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(select_playlist(tracks, mood="calm", genre="jazz", seed=3), tracks)
        self.assertEqual(select_playlist(tracks, mood="energetic"), [])
        for name in PERSONAS:
            self.assertIn("작은 음악", dj_script(tracks[0], name))
        self.assertEqual(main(["plan", "--catalog", str(self.catalog), "--mood", "calm"]), 0)

    def test_unknown_or_noncommercial_is_blocked(self):
        for name in ("CC-BY-NC-4.0", "UNKNOWN", "NCS"):
            self.write([{**self.item, "license": name}])
            with self.assertRaises(CatalogError):
                load_catalog(self.catalog)

    def test_path_traversal_and_absolute_blocked(self):
        for path in ("../test.wav", "/tmp/music.wav", "https://example.com/song.wav"):
            self.write([{**self.item, "path": path}])
            with self.assertRaises(CatalogError):
                load_catalog(self.catalog)

    def test_not_approved_is_ignored(self):
        self.write([{**self.item, "approved": False}])
        self.assertEqual(load_catalog(self.catalog), [])
        self.assertEqual(main(["plan", "--catalog", str(self.catalog)]), 2)

    def test_cc_by_requires_proof_and_attribution(self):
        self.write([{**self.item, "license": "CC-BY-4.0"}])
        with self.assertRaises(CatalogError):
            load_catalog(self.catalog)
        self.write([{**self.item, "license": "CC-BY-4.0", "source_url": "https://example.org/audio", "license_url": "https://creativecommons.org/licenses/by/4.0/"}])
        self.assertIn("CC-BY-4.0", load_catalog(self.catalog)[0].attribution)

    def test_count_and_persona_rejected(self):
        self.write([self.item])
        tracks = load_catalog(self.catalog)
        with self.assertRaises(ValueError):
            select_playlist(tracks, count=0)
        with self.assertRaises(ValueError):
            dj_script(tracks[0], "fake")


if __name__ == "__main__":
    unittest.main()
