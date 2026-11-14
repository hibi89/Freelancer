"""Independent console CLI entrypoint remains separate from GUI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CLIEntrypointTests(unittest.TestCase):
    def test_help_exits_without_gui_or_network(self):
        p = subprocess.run([sys.executable, str(ROOT/'run_bidax_cli.py'), '--help'],
                           capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('api-probe', p.stdout)
        self.assertIn('onbid-field-audit', p.stdout)

    def test_offline_onbid_plan_returns_without_gui(self):
        with tempfile.TemporaryDirectory() as td:
            p = subprocess.run([sys.executable, str(ROOT/'run_bidax_cli.py'),
                               '--db', str(Path(td)/'unused.sqlite'), 'api-probe',
                               'onbid_result_list', str(ROOT/'examples'/'onbid_result_list_plan_LOCAL_ONLY.json')],
                               capture_output=True, text=True, encoding='utf-8', timeout=15)
            self.assertEqual(p.returncode, 0, p.stderr)
            output = json.loads(p.stdout)
            self.assertEqual(output['dataset_id'],15157252)
            self.assertTrue(output['ready'])
            self.assertFalse((Path(td)/'unused.sqlite').exists())

if __name__ == '__main__': unittest.main()
