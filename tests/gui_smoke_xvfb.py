"""Real Tk 8.6 widget + synthetic end-to-end desktop button actions under Xvfb.

No customer data or external services. Real physical Windows and manual click UX not tested.
"""
import tempfile
from pathlib import Path
from worknova_desk.core import Desk
from worknova_desk.gui import WorknovaGUI

with tempfile.TemporaryDirectory() as folder:
    desk=Desk(Path(folder)/'window.sqlite')
    cid=desk.add_customer('테스트 고객')
    app=WorknovaGUI(desk)
    app.root.update_idletasks()
    assert len(app.views['customers'].get_children())==1

    def select_customer():
        app.views['customers'].selection_set(cid)
        app.refresh_children('customers')
    select_customer()
    # Local-only GUI command execution using real widgets, deterministic scripted responses.
    app.question=lambda *args,**kwargs: '로고|1|100'
    app.vat=lambda: True
    app.action(app.new_quote)
    quote=desk.list_quotes(cid)[0]['id']
    select_customer()
    app.views['quotes'].selection_set(quote)
    app.confirmed=lambda *args,**kwargs: None
    app.question=lambda *args,**kwargs: 'owner'
    app.action(app.approve_quote)
    assert desk._fetch('quotes', quote)['status']=='APPROVED'

    select_customer()
    app.views['quotes'].selection_set(quote)
    answers=iter(('디자인 범위', '초안|110'))
    app.question=lambda *args,**kwargs: next(answers)
    app.action(app.new_contract)
    contract=desk.list_contracts(cid)[0]['id']
    select_customer()
    app.views['contracts'].selection_set(contract)
    app.question=lambda *args,**kwargs: 'owner'
    app.action(app.activate)
    assert desk._fetch('contracts',contract)['status']=='ACTIVE'
    select_customer()
    app.views['contracts'].selection_set(contract)
    app.refresh_children('contracts')
    mid=desk.list_milestones(contract)[0]['id']
    app.views['milestones'].selection_set(mid)
    answers=iter(('owner','초안 납품 테스트'))
    app.question=lambda *args,**kwargs: next(answers)
    app.action(app.deliver)
    assert desk._fetch('milestones',mid)['status']=='DELIVERED'

    select_customer();app.views['contracts'].selection_set(contract)
    app.refresh_children('contracts');app.views['milestones'].selection_set(mid)
    app.question=lambda *args,**kwargs:'client'
    app.action(app.accept)
    assert desk._fetch('milestones',mid)['status']=='ACCEPTED'

    select_customer();app.views['contracts'].selection_set(contract)
    app.refresh_children('contracts');app.views['milestones'].selection_set(mid)
    answers=iter(('50','receipt-001','owner'))
    app.question=lambda *args,**kwargs:next(answers)
    app.action(app.collect)
    assert desk.report(contract)['paid_krw']==50
    assert desk.report(contract)['outstanding_krw']==60
    assert desk.verify_audit()>=8
    app.close()
print('Tk8.6 real widget scripted E2E PASS: customer selection -> quote -> approval -> contract -> activate -> deliver -> accept -> manual collection; 0 network')
