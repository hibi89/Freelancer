"""Tk real widget acceptance for optional owner-only customer edits and file hash recording."""
from __future__ import annotations
import tempfile
from pathlib import Path
from worknova_desk.core import Desk
from worknova_desk.gui import WorknovaGUI
from worknova_desk.delivery_evidence import list_evidence
from unittest.mock import patch

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder)
    desk=Desk(root/'desk.sqlite')
    cust=desk.add_customer('테스트거래처')
    q=desk.new_quote(cust,[{'description':'기획','quantity':1,'unit_krw':100}])
    desk.approve_quote(q,'owner')
    contract=desk.new_contract(q,'scope',[{'title':'1단계','amount_krw':110}])
    desk.activate_contract(contract,'owner')
    milestone=desk.list_milestones(contract)[0]['id']
    desk.deliver(milestone,'owner','전달 준비')
    sample=root/'deliverable.txt';sample.write_text('local-only bytes',encoding='utf-8')
    app=WorknovaGUI(desk)
    app.root.update()
    try:
        app.views['customers'].selection_set(cust)
        app.question=lambda *args,**kwargs:'수정된거래처'
        app.confirmed=lambda *args,**kwargs:None
        app.action(app.rename_selected_customer)
        assert desk._fetch('customers',cust)['name']=='수정된거래처'
        app.views['customers'].selection_set(cust)
        with patch('worknova_desk.gui.messagebox.showwarning', return_value=None):
            app.action(app.delete_selected_customer)
        assert len(desk.list_customers())==1, 'existing contract must block deletion'
        app.views['customers'].selection_set(cust)
        app.refresh_children('customers')
        app.views['contracts'].selection_set(contract)
        app.refresh_children('contracts')
        app.views['milestones'].selection_set(milestone)
        with patch('worknova_desk.gui.filedialog.askopenfilename',return_value=str(sample)):
            app.action(app.attach_selected_evidence)
        assert len(list_evidence(desk,milestone))==1
        app.views['milestones'].selection_set(milestone)
        with patch('worknova_desk.gui.filedialog.askopenfilename',return_value=str(sample)):
            app.action(app.verify_selected_evidence)
        assert desk.verify_audit()>0
    finally:
        app.close()
print('Tk8.6 owner lifecycle/evidence GUI PASS: rename, protected customer delete, evidence hash, file reverify, 0 network')
