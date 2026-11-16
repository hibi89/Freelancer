import json
import unittest
from pathlib import Path
from unittest.mock import patch

from axdev.core import ContractError
from scripts.req_status import read_status, ROOT


class RequirementStatusTests(unittest.TestCase):
    def test_full_F01_F20_manifest_preserves_official_unassessed(self):
        result = read_status()
        self.assertEqual(len(result["requirements"]), 20)
        self.assertEqual(result["official_final_blueprint_completion"], "UNASSESSED")
        self.assertEqual(sum(result["implementation_counts"].values()), 20)
        self.assertEqual(sum(result["verification_counts"].values()), 20)
        self.assertEqual(result["verification_counts"]["NOT_RUN"], 4)

    def test_missing_requirement_source_refuses_completion_claim(self):
        from scripts import req_status
        data = json.loads(req_status.MATRIX.read_text(encoding="utf-8"))
        data["requirements"][0]["paths"] = ["missing/generated.py"]
        with patch("scripts.req_status.MATRIX") as manifest:
            manifest.read_text.return_value = json.dumps(data)
            with self.assertRaisesRegex(ContractError, "evidence source"):
                read_status()

    def test_duplicate_requirement_refused(self):
        from scripts import req_status
        data = json.loads(req_status.MATRIX.read_text(encoding="utf-8"))
        data["requirements"][1]["id"] = data["requirements"][0]["id"]
        with patch("scripts.req_status.MATRIX") as manifest:
            manifest.read_text.return_value = json.dumps(data)
            with self.assertRaisesRegex(ContractError, "duplicate"):
                read_status()


if __name__ == "__main__":
    unittest.main()
