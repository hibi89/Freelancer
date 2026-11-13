"""Real Tk Widget construction smoke through Xvfb; not equivalent to customer Windows acceptance."""
import tempfile
from pathlib import Path
from worknova_desk.core import Desk
from worknova_desk.gui import WorknovaGUI
with tempfile.TemporaryDirectory() as folder:
    desk=Desk(Path(folder)/'window.sqlite')
    id=desk.add_customer('테스트 고객')
    app=WorknovaGUI(desk)
    app.root.update_idletasks()
    customers=app.views['customers']
    assert len(customers.get_children())==1
    customers.selection_set(id)
    app.root.event_generate('<<TreeviewSelect>>',when='tail')
    app.root.update()
    assert not app.views['quotes'].get_children()
    q=desk.new_quote(id,[{'description':'오프라인 견적','quantity':1,'unit_krw':10000}])
    app.refresh_children('customers')
    assert q in app.views['quotes'].get_children()
    app.close()
print('Tk 8.6 widget lifecycle, customer selection and quote display PASS')
