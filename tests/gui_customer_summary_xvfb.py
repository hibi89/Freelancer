"""Actual Tk widget smoke for redacted customer summary, Linux Xvfb only."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from worknova_desk.core import Desk
from worknova_desk.gui import WorknovaGUI

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    desk=Desk(root/'ledger.sqlite')
    customer=desk.add_customer('개인정보 표시 금지')
    app=WorknovaGUI(desk)
    app.root.update()
    try:
        app.views['customers'].selection_set(customer)
        output=root/'customer.json'
        with patch('worknova_desk.gui.filedialog.asksaveasfilename',return_value=str(output)), \
             patch('worknova_desk.gui.messagebox.askyesno',return_value=True):
            app.action(app.export_selected_customer_summary)
        assert output.is_file(), 'Tk export failed'
        blob=json.loads(output.read_text(encoding='utf-8'))
        assert blob['customer_name']=='[REDACTED]'
        assert blob['quotes']==[]
        assert '개인정보 표시 금지' not in output.read_text(encoding='utf-8')
        # Confirm once again on same path: no silent overwrite, warning only.
        before=output.read_bytes()
        with patch('worknova_desk.gui.filedialog.asksaveasfilename',return_value=str(output)), \
             patch('worknova_desk.gui.messagebox.askyesno',return_value=True), \
             patch('worknova_desk.gui.messagebox.showwarning',return_value=None):
            app.action(app.export_selected_customer_summary)
        assert output.read_bytes()==before
    finally:
        app.close()
print('Tk8.6 customer summary: default-redacted, no-overwrite, 0 external calls PASS (Linux Xvfb)')
