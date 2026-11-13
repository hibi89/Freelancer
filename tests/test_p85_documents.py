"""P85 offline DOCX/PDF/privacy/portable packaging regression (synthetic names only)."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from worknova_desk.core import Desk, DeskError
from worknova_desk.documents import export_document
from scripts.build_portable import bundle

ROOT = Path(__file__).resolve().parents[1]
TEST_FONT = Path('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')


class P85DocumentsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p = Path(self.tmp.name)
        self.desk = Desk(self.p / 'p85.sqlite')
        self.addCleanup(self.desk.close)
        self.customer = self.desk.add_customer('가상 홍길동 <script>alert(1)</script>')
        self.quote = self.desk.new_quote(self.customer,[
           {'description':'웹 디자인 <img src=x>', 'quantity':2,'unit_krw':101},
           {'description':'유지보수', 'quantity':1, 'unit_krw':103}])
        self.desk.approve_quote(self.quote,'owner')
        self.contract = self.desk.new_contract(self.quote, '가상 업무 범위: 웹 페이지 두 개',[
          {'title':'착수', 'amount_krw':222}, {'title':'검수','amount_krw':114}])
        self.desk.activate_contract(self.contract,'owner')

    def _docx_lines(self, location):
        import docx
        loaded=docx.Document(location)
        return '\n'.join(p.text for p in loaded.paragraphs)

    def test_docx_quote_redacted_price_and_korean_xml(self):
        out=self.p/'quote.docx'
        result=export_document(self.desk,'quote',self.quote,out)
        self.assertEqual(result['document_type'],'docx')
        self.assertEqual(result['sha256'],hashlib.sha256(out.read_bytes()).hexdigest())
        lines=self._docx_lines(out)
        self.assertIn('웹 디자인 <img src=x>',lines)  # user input is TEXT, not markup
        self.assertIn('견적 버전: 1',lines)
        self.assertIn('336원',lines)
        self.assertIn('고객명: [비공개]',lines)
        self.assertNotIn('가상 홍길동',lines)
        self.assertNotIn('세금계산서 발급 완료',lines)
        with zipfile.ZipFile(out) as z:
            self.assertEqual(z.testzip(),None)
            self.assertEqual(set(z.namelist()),{'[Content_Types].xml','_rels/.rels','word/document.xml'})

    def test_contract_docx_milestone_and_manual_not_verified(self):
        m=self.desk.list_milestones(self.contract)[0]['id']
        self.desk.deliver(m,'owner','전달 완료')
        self.desk.accept(m,'owner')
        self.desk.record_collection(m,100,'synthetic-collection-1','owner')
        out=self.p/'contract.docx'
        export_document(self.desk,'contract',self.contract,out)
        text=self._docx_lines(out)
        for x in ['수기 수금 기록: 100원','미수 잔액: 236원','가상 업무 범위','입금과 검증되지 않았습니다']:
            self.assertIn(x,text)
        self.assertNotIn('가상 홍길동',text)

    def test_opt_in_disclosure_both_flags_required(self):
        with self.assertRaises(DeskError):
            export_document(self.desk,'quote',self.quote,self.p/'bad.docx',include_customer=True)
        self.assertFalse((self.p/'bad.docx').exists())
        good=self.p/'opted.docx'
        export_document(self.desk,'quote',self.quote,good,include_customer=True,confirm_disclosure=True)
        self.assertIn('가상 홍길동',self._docx_lines(good))

    def test_existing_path_never_overwritten(self):
        out=self.p/'existing.docx'
        out.write_bytes(b'valuable owner document')
        with self.assertRaises(DeskError):
            export_document(self.desk,'quote',self.quote,out)
        self.assertEqual(out.read_bytes(),b'valuable owner document')

    def test_extension_rejected_and_no_output(self):
        with self.assertRaises(DeskError):
            export_document(self.desk,'quote',self.quote,self.p/'unsafe.html')
        self.assertEqual(list(self.p.glob('*.html')),[])

    def test_export_refuses_tampered_audit(self):
        self.desk.db.execute("UPDATE audit_events SET actor='tampered' WHERE seq=1")
        with self.assertRaises(DeskError):
            export_document(self.desk,'contract',self.contract,self.p/'no.docx')
        self.assertFalse((self.p/'no.docx').exists())

    def test_quote_revision_renders_separately(self):
        new_id=self.desk.revise_quote(self.quote,[{'description':'개정본','quantity':1,'unit_krw':999}])
        old=self.p/'v1.docx';new=self.p/'v2.docx'
        export_document(self.desk,'quote',self.quote,old)
        export_document(self.desk,'quote',new_id,new)
        self.assertIn('견적 버전: 1',self._docx_lines(old))
        self.assertIn('견적 버전: 2',self._docx_lines(new))
        self.assertIn('336원',self._docx_lines(old))
        self.assertIn('1,099원',self._docx_lines(new))

    def test_docx_deterministic_same_input(self):
        a=self.p/'a.docx'; b=self.p/'b.docx'
        export_document(self.desk,'quote',self.quote,a)
        export_document(self.desk,'quote',self.quote,b)
        self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_pdf_font_required_and_missing_reportlab_not_faked(self):
        with self.assertRaises(DeskError):
            export_document(self.desk,'quote',self.quote,self.p/'no.pdf',format='pdf')
        with self.assertRaises(DeskError):
            export_document(self.desk,'quote',self.quote,self.p/'no.pdf',format='pdf',pdf_font=self.p/'missing.ttf')
        self.assertFalse((self.p/'no.pdf').exists())

    @unittest.skipUnless(TEST_FONT.exists(),'No local test-only Nanum Korean TTF')
    def test_pdf_real_render_and_korean_text_extract(self):
        import fitz
        out=self.p/'quote.pdf'
        info=export_document(self.desk,'quote',self.quote,out,format='pdf',pdf_font=TEST_FONT)
        self.assertEqual(info['bytes'],out.stat().st_size)
        with fitz.open(out) as pdf:
            self.assertEqual(len(pdf),1)
            lines=' '.join(page.get_text() for page in pdf)
            self.assertIn('견적 검토서',lines)
            self.assertIn('336원',lines)
            self.assertNotIn('가상 홍길동',lines)
            self.assertNotIn('세금계산서 발급 완료',lines)

    def test_cli_docx_export(self):
        out=self.p/'cli.docx'
        args=[sys.executable,'-m','worknova_desk','--db',str(self.desk.path),
              'export-document','--type','quote','--id',self.quote,'--out',str(out),'--format','docx']
        env={**os.environ,'PYTHONPATH':str(ROOT)}
        result=subprocess.run(args,env=env,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(out.exists())
        self.assertEqual(json.loads(result.stdout)['result']['sha256'],hashlib.sha256(out.read_bytes()).hexdigest())

    def test_portable_zip_allowlist_hash_and_no_customer_sqlite(self):
        out=self.p/'portable.zip'
        info=bundle(ROOT,out)
        self.assertEqual(info['sha256'],hashlib.sha256(out.read_bytes()).hexdigest())
        with zipfile.ZipFile(out) as archive:
            self.assertIsNone(archive.testzip())
            contents=set(archive.namelist())
            self.assertNotIn('p85.sqlite',contents)
            self.assertFalse(any(x.endswith(('.ttf','.env','.db','.sqlite','.exe','.pem')) for x in contents))
            manifest=json.loads(archive.read('FILE_MANIFEST.json'))
            for item in manifest['files']:
                self.assertEqual(hashlib.sha256(archive.read(item['path'])).hexdigest(),item['sha256'])
            self.assertIn('install_local.ps1', contents)
            self.assertIn('launch.cmd', contents)

    def test_portable_reproducible_zip(self):
        a=self.p/'a.zip';b=self.p/'b.zip'
        bundle(ROOT,a);bundle(ROOT,b)
        self.assertEqual(a.read_bytes(),b.read_bytes())

    def test_portable_does_not_overwrite_existing(self):
        out=self.p/'already.zip';out.write_bytes(b'original')
        with self.assertRaises(DeskError):bundle(ROOT,out)
        self.assertEqual(out.read_bytes(),b'original')


class SyntheticIndustryCoverageTests(unittest.TestCase):
    def test_ten_synthetic_industries_not_customer_validation(self):
        cases=[('디자인',1001,True),('개발',5000,True),('번역',310,False),('영상',9999,True),
               ('문서편집',101,False),('로고',100,True),('사진',703,True),('상담',331,False),
               ('리서치',201,True),('컨텐츠',50,True)]
        with tempfile.TemporaryDirectory() as t:
            desk=Desk(Path(t)/'synthetic-only.sqlite')
            try:
                for idx,(category,unit,taxable) in enumerate(cases,1):
                    with self.subTest(case=category):
                        cid=desk.add_customer(f'{category} 분야 가상고객')
                        q=desk.new_quote(cid,[{'description':category,'quantity':1,'unit_krw':unit}],taxable=taxable)
                        desk.approve_quote(q,'owner')
                        total=unit+(unit+5)//10 if taxable else unit
                        c=desk.new_contract(q,'합성 테스트',[{'title':'납품','amount_krw':total}])
                        desk.activate_contract(c,'owner')
                        m=desk.list_milestones(c)[0]['id']
                        desk.deliver(m,'owner','가상 파일 전달'); desk.accept(m,'owner')
                        desk.record_collection(m,total,f'synthetic-{idx}','owner')
                        self.assertEqual(desk.report(c)['outstanding_krw'],0)
                self.assertGreaterEqual(desk.verify_audit(),70)
            finally:
                desk.close()
