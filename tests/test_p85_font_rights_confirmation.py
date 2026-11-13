"""Explicit commercial PDF font-use consent before writing a file."""
from unittest import TestCase
from unittest.mock import patch

from worknova_desk.core import DeskError
from worknova_desk.gui import WorknovaGUI


class FontRightsTests(TestCase):
    def test_pdf_rights_gate_denial_does_not_export(self):
        class FakeUI:
            root = None
            desk = None
            def selected(self, kind):
                return 'synthetic-id'
            def confirmed(self, prompt):
                assert '상업용' in prompt
                raise DeskError('권리 미확인')
        with patch('worknova_desk.gui.filedialog.asksaveasfilename', return_value='/tmp/unused.pdf'), \
             patch('worknova_desk.gui.filedialog.askopenfilename', return_value='/tmp/rights-unknown.ttf'), \
             patch('worknova_desk.gui.export_document') as exporter:
            with self.assertRaisesRegex(DeskError,'권리'):
                WorknovaGUI._export_selected(FakeUI(),'quote','pdf')
            exporter.assert_not_called()

    def test_pdf_rights_gate_accepted_calls_generator(self):
        prompts=[]
        class FakeUI:
            root = None
            desk = None
            def selected(self, kind):
                return 'synthetic-id'
            def confirmed(self, prompt):
                prompts.append(prompt)
        with patch('worknova_desk.gui.filedialog.asksaveasfilename', return_value='/tmp/unused.pdf'), \
             patch('worknova_desk.gui.filedialog.askopenfilename', return_value='/tmp/licensed.ttf'), \
             patch('worknova_desk.gui.export_document', return_value={'ok':True}) as exporter:
            result=WorknovaGUI._export_selected(FakeUI(),'quote','pdf')
            self.assertEqual(result,{'ok':True})
            self.assertTrue(prompts)
            exporter.assert_called_once()

    def test_docx_has_no_pdf_font_rights_gate(self):
        class FakeUI:
            root = None
            desk = None
            def selected(self,kind):
                return 'synthetic-id'
            def confirmed(self,prompt):
                self.fail('DOCX must not ask PDF font rights question')
        with patch('worknova_desk.gui.filedialog.asksaveasfilename', return_value='/tmp/unused.docx'), \
             patch('worknova_desk.gui.export_document', return_value={'ok':True}) as exporter:
            WorknovaGUI._export_selected(FakeUI(),'quote','docx')
            exporter.assert_called_once()
