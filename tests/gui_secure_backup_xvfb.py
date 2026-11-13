"""Real Tk buttons and password dialogs on synthetic data; Linux Xvfb only."""
from pathlib import Path
import tempfile
from unittest.mock import patch

from worknova_desk.core import Desk
from worknova_desk.gui import WorknovaGUI
from worknova_desk.secure_backup import encrypted_restore_new

with tempfile.TemporaryDirectory(prefix='worknova-gui-enc-') as folder:
    root=Path(folder)
    desk=Desk(root/'original.sqlite')
    desk.add_customer('가상 표본 업체')
    gui=WorknovaGUI(desk)
    try:
        gui.root.update()
        destination=root/'backup.wndesk'
        with patch('worknova_desk.gui.filedialog.asksaveasfilename',return_value=str(destination)), \
             patch('worknova_desk.gui.simpledialog.askstring',side_effect=['test-passphrase-1234','test-passphrase-1234']), \
             patch('worknova_desk.gui.messagebox.askyesno',return_value=True):
            gui.action(gui.encrypted_backup)
        assert destination.is_file()
        restored=root/'restored.sqlite'
        with patch('worknova_desk.gui.filedialog.askopenfilename',return_value=str(destination)), \
             patch('worknova_desk.gui.filedialog.asksaveasfilename',return_value=str(restored)), \
             patch('worknova_desk.gui.simpledialog.askstring',return_value='test-passphrase-1234'), \
             patch('worknova_desk.gui.messagebox.askyesno',return_value=True):
            gui.action(gui.encrypted_restore)
        assert restored.is_file()
        reopened=Desk(restored,allow_create=False)
        try: assert reopened.list_customers()[0]['name']=='가상 표본 업체'
        finally:reopened.close()
        before=restored.read_bytes()
        with patch('worknova_desk.gui.filedialog.askopenfilename',return_value=str(destination)), \
             patch('worknova_desk.gui.filedialog.asksaveasfilename',return_value=str(restored)), \
             patch('worknova_desk.gui.simpledialog.askstring',return_value='test-passphrase-1234'), \
             patch('worknova_desk.gui.messagebox.askyesno',return_value=True), \
             patch('worknova_desk.gui.messagebox.showwarning',return_value=None):
            gui.action(gui.encrypted_restore)
        assert restored.read_bytes()==before
    finally:gui.close()
print('Tk backup, password prompt, NEW restore, no-overwrite PASS (Linux Xvfb)')
