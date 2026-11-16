"""Read-only F01-F20 source inventory; no completion percentage is inferred."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from axdev.core import ContractError

ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT = ROOT / "docs" / "FINAL_BLUEPRINT.md"
MATRIX = ROOT / "docs" / "REQ_IMPLEMENTATION_MATRIX.json"
IDS = {f"F{index:02d}" for index in range(1, 21)}
IMPLEMENTATION = {"IMPLEMENTED", "PARTIAL", "NOT_IMPLEMENTED"}
VERIFICATION = {"SYNTHETIC_PASS", "PARTIAL", "NOT_RUN"}


def read_status():
    """Check that all 20 original IDs are accounted for, not reweighted."""
    blueprint_ids = set(re.findall(r"^\|\s*(F\d{2})\s*\|",
                                   BLUEPRINT.read_text(encoding="utf-8"), re.M))
    if blueprint_ids != IDS:
        raise ContractError("blueprint F01-F20 IDs are missing or changed")
    data = json.loads(MATRIX.read_text(encoding="utf-8"))
    if (data.get("version") != 1 or
            data.get("official_final_blueprint_completion") != "UNASSESSED"):
        raise ContractError("unsupported or improperly scored requirement matrix")
    records = data.get("requirements")
    if not isinstance(records, list) or len(records) != 20:
        raise ContractError("exactly 20 F01-F20 records required")
    seen = set()
    for entry in records:
        if not isinstance(entry, dict) or entry.get("id") not in IDS:
            raise ContractError("invalid F01-F20 requirement ID")
        if entry["id"] in seen:
            raise ContractError("duplicate F01-F20 requirement ID")
        seen.add(entry["id"])
        if (entry.get("implementation") not in IMPLEMENTATION or
                entry.get("verification") not in VERIFICATION or
                not isinstance(entry.get("remaining_work"), str) or
                not entry["remaining_work"].strip()):
            raise ContractError("incomplete evidence for " + entry["id"])
        paths = entry.get("paths")
        if not isinstance(paths, list) or len(set(paths)) != len(paths):
            raise ContractError("invalid source paths in requirement matrix")
        for path in paths:
            if (not isinstance(path, str) or path.startswith(("/", "\\")) or
                    ".." in path.split("/") or not (ROOT / path).is_file()):
                raise ContractError("missing or unsafe evidence source for " + entry["id"])
        if entry["implementation"] == "NOT_IMPLEMENTED" and paths:
            raise ContractError("not implemented requirement must not claim code evidence")
    if seen != IDS:
        raise ContractError("F01-F20 matrix ID set differs")
    return {
        "official_final_blueprint_completion": "UNASSESSED",
        "implementation_counts": {
            state: sum(e["implementation"] == state for e in records)
            for state in sorted(IMPLEMENTATION)
        },
        "verification_counts": {
            state: sum(e["verification"] == state for e in records)
            for state in sorted(VERIFICATION)
        },
        "remaining_requirement_count": sum(e["implementation"] != "IMPLEMENTED"
                                           or e["verification"] != "SYNTHETIC_PASS"
                                           for e in records),
        "requirements": records,
        "note": "Counts are item counts, not official weighted completion or host proof.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only AXDEV requirement inventory")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    result = read_status()
    if args.summary:
        result.pop("requirements")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, ContractError) as exc:
        print("AXDEV_REQ_STATUS_ERROR:", exc)
        raise SystemExit(2)
