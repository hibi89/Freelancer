"""Exercise the GUI executable's fail-closed, disposable self-test entrypoint.

Native tkinter's widget lifecycle is checked separately by Windows CI.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from bidax.entrypoint import main


class GUIEntrypointTests(unittest.TestCase):
    def test_selftest_uses_temporary_db_without_touching_owner_path(self):
        with patch.object(sys, 'argv', ['BIDAX_GUI_CI_UNRELEASED.exe', '--selftest-gui']):
            with patch('bidax.entrypoint.launch') as gui:
                with patch('bidax.entrypoint.default_db_path') as customer:
                    main()
        customer.assert_not_called()
        gui.assert_called_once()
        args, kwargs = gui.call_args
        self.assertEqual(kwargs['auto_close_ms'], 700)
        self.assertEqual(Path(args[0]).name, 'test-gui.db')
        self.assertFalse(Path(args[0]).parent.exists())

    def test_regular_launch_uses_existing_default_behavior(self):
        with patch.object(sys, 'argv', ['run_bidax.py']):
            with patch('bidax.entrypoint.launch') as gui:
                with patch('bidax.entrypoint.default_db_path', return_value=Path('expected.db')) as p:
                    main()
        p.assert_called_once_with()
        gui.assert_called_once_with(Path('expected.db'))

    def test_unrecognized_gui_argument_fails_before_any_database_path(self):
        with patch.object(sys, 'argv', ['run_bidax.py', '--db', 'wrong.db']):
            with patch('bidax.entrypoint.launch') as gui:
                with patch('bidax.entrypoint.default_db_path') as customer:
                    with self.assertRaises(SystemExit):
                        main()
        gui.assert_not_called()
        customer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
