"""Offline no-credential diagnostics for unknown Onbid response shapes."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bidax.api_gateway import create_plan, fetch_quarantined
from bidax.response_shape import diagnose_packet


class _Reply:
    status = 200
    headers = {"Content-Type": "application/json; charset=utf-8"}
    def __init__(self, b): self.b = b
    def read(self, size): return self.b[:size]
    def __enter__(self): return self
    def __exit__(self, *args): pass


class ResponseShapeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root/'response.json'
        self.plan = create_plan('onbid_result_list', {'parameters': {'cltrTypeCd':'0001','prptDivCd':'0002','opbdDtStart':'20261110','opbdDtEnd':'20261113'},'page':1,'rows':10})

    def save(self, raw):
        class Opener:
            def open(_,request,timeout=15): return _Reply(json.dumps(raw).encode('utf8'))
        fetch_quarantined(self.plan, service_key='TEST_PRIVATE_API_KEY_DO_NOT_PRINT',permission=True,
                          db_path=self.root/'budget.db',output_path=self.path,
                          opener=Opener(),now=datetime(2026,11,14,tzinfo=timezone.utc))
        return self.path

    def test_flat_onbid_shape_uses_no_values(self):
        path=self.save({'resultCode':'00','pageNo':1,'numOfRows':10,'totalCount':1,
                        'items':[{'onbidCltrNm':'CUSTOMER_PRIVATE_ASSET','addr':'CUSTOMER_ADDRESS'}]})
        report=diagnose_packet(path); dumped=json.dumps(report)
        self.assertEqual(report['inspection_reason'],'UNRECOGNIZED_ENVELOPE')
        self.assertEqual(report['status_classes'][0]['class'],'SUCCESS_CODE_CANDIDATE')
        self.assertIn('resultCode',report['nodes'][0]['known_keys'])
        self.assertNotIn('CUSTOMER_PRIVATE_ASSET',dumped)
        self.assertNotIn('CUSTOMER_ADDRESS',dumped)
        self.assertNotIn('TEST_PRIVATE_API_KEY_DO_NOT_PRINT',dumped)
        self.assertFalse(report['auto_import_allowed'])

    def test_unknown_envelope_key_not_echoed(self):
        data={'HIGHLY_PRIVATE_CUSTOMER_KEY':{'secret_value':'customer-secret'},'foo':1}
        r=diagnose_packet(self.save(data))
        s=json.dumps(r)
        self.assertEqual(r['nodes'][0]['other_key_count'],2)
        self.assertNotIn('HIGHLY_PRIVATE_CUSTOMER_KEY',s)
        self.assertNotIn('customer-secret',s)

    def test_error_code_classified_without_value(self):
        r=diagnose_packet(self.save({'resultCode':'REDACT_THIS_BAD_CODE','resultMsg':'PRIVATE_DETAIL'}))
        self.assertEqual(r['status_classes'][0]['class'],'UNUSUAL_CODE_REDACTED')
        self.assertNotIn('PRIVATE_DETAIL',json.dumps(r))

    def test_existing_standard_envelope(self):
        raw={'response':{'header':{'resultCode':'00'},'body':{'pageNo':1,'numOfRows':10,'totalCount':0,'items':{'item':[]}}}}
        r=diagnose_packet(self.save(raw))
        self.assertEqual(r['inspection_state'],'STRUCTURE_CANDIDATE_REVIEW_REQUIRED')
        self.assertEqual(r['status_classes'][0]['path'],'response.header.resultCode')

    def test_modified_or_sensitive_packet_rejected(self):
        p=self.save({'data':{'items':[]}})
        packet=json.loads(p.read_text(encoding='utf8'))
        packet['raw_response']['data']['items'].append({'private':'mutated'})
        p.write_text(json.dumps(packet),encoding='utf8')
        with self.assertRaises(ValueError): diagnose_packet(p)

    def test_standalone_script_uses_existing_packet_without_network(self):
        import importlib.util
        from pathlib import Path
        import bidax
        script=Path(bidax.__file__).resolve().parents[1]/'BID_AX_API_SHAPE_DIAG.py'
        spec=importlib.util.spec_from_file_location('bidax_offline_diag_test',script)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module._FILE=self.save({'resultCode':'00','items':[{'location':'SENSITIVE'}]})
        output=io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined',side_effect=AssertionError('unexpected network')):
            with contextlib.redirect_stdout(output):
                module.run()
        self.assertNotIn('SENSITIVE',output.getvalue())
        self.assertIn('OFFLINE_SCHEMA_ONLY',output.getvalue())

    def test_api_shape_cli_is_offline(self):
        self.save({'resultCode':'00','data':{'items':[{'note':'PRIVATE_DATA'}]}})
        from bidax.cli import main
        output=io.StringIO()
        with patch('bidax.api_gateway.fetch_quarantined',side_effect=AssertionError('should not call')):
            with contextlib.redirect_stdout(output):
                main(['--db',str(self.root/'local.db'),'api-shape',str(self.path)])
        self.assertIn('OFFLINE_PUBLIC_SCHEMA_NAMES_ONLY',output.getvalue())
        self.assertNotIn('PRIVATE_DATA',output.getvalue())

if __name__ == '__main__': unittest.main()
