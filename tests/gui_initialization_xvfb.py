"""GUI first-run consent smoke; actual Tk widgets under Xvfb, not Windows QA."""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from worknova_desk.gui import WorknovaGUI, main

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / 'owner.sqlite'
    with patch('worknova_desk.gui.messagebox.askyesno', return_value=False):
        try:
            main(['--db', str(database)])
        except SystemExit as exc:
            assert '취소' in str(exc)
        else:
            raise AssertionError('new ledger without consent was not stopped')
    assert not database.exists(), 'declined new DB must not be created'
    with patch('worknova_desk.gui.messagebox.askyesno', return_value=True), \
         patch.object(WorknovaGUI, 'run', lambda self: self.close()):
        main(['--db', str(database)])
    assert database.exists(), 'explicitly accepted first-run DB expected'
    with patch('worknova_desk.gui.messagebox.askyesno', side_effect=AssertionError('should not prompt')):
        with patch.object(WorknovaGUI, 'run', lambda self: self.close()):
            main(['--db', str(database)])
print('GUI first-run refusal/confirmation/existing DB PASS (Linux Tk/Xvfb; not Windows)')
