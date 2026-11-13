"""Contract for the non-destructive Windows QA tool; no false platform PASS."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'tools/windows_acceptance.py'


class WindowsAcceptanceContract(unittest.TestCase):
    def test_script_parse_and_is_explicitly_platform_gated(self):
        compile(SCRIPT.read_text(encoding='utf-8'), str(SCRIPT), 'exec')
        source = SCRIPT.read_text(encoding='utf-8')
        self.assertIn("if sys.platform != 'win32'", source)
        self.assertIn("env['LOCALAPPDATA'] = str(profile)", source)
        self.assertIn("'-NonInteractive', '-File'", source)
        self.assertNotIn("'-ExecutionPolicy'", source)
        self.assertNotIn("os.system(", source)
        self.assertIn('TemporaryDirectory', source)

    @unittest.skipIf(sys.platform == 'win32', 'Windows full drill must run manually on target OS')
    def test_nonwindows_refuses_false_success_without_creating_files(self):
        p = subprocess.run([sys.executable, '-B', str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 3)
        self.assertIn('Windows acceptance NOT confirmed', p.stdout)
        self.assertNotIn('"ok": true', p.stdout)


if __name__ == '__main__':
    unittest.main()
