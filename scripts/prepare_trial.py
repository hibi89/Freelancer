"""Create an isolated, synthetic local Git repository and immutable review tests."""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path,
                        help="NEW directory for disposable trial; never overwritten")
    a = parser.parse_args()
    out = a.output.expanduser().resolve()
    if out.exists():
        raise SystemExit("REFUSING TO OVERWRITE: output directory exists")
    if not out.parent.is_dir():
        raise SystemExit("Parent directory must already exist")
    out.mkdir()
    repo = out / "trial-repo"
    repo.mkdir()
    (repo / "tests").mkdir()
    (repo / "README.md").write_text(
        "# AXDEV disposable trial\nSynthetic only. Do not put secrets here.\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text(
        "# Trial repo\nOnly implement approved src/hello.py; protected acceptance tests must remain unchanged.\n",
        encoding="utf-8")
    (repo / "tests" / "test_hello.py").write_text(
        "import unittest\n"
        "from src.hello import greet\n"
        "class TestHello(unittest.TestCase):\n"
        "    def test_greeting(self):\n"
        "        self.assertEqual(greet('AX'), 'Hello, AX')\n"
        "    def test_empty_name(self):\n"
        "        self.assertEqual(greet(''), 'Hello, ')\n",
        encoding="utf-8")
    def git(*args):
        subprocess.run(["git", *args], cwd=repo, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    git("init")
    git("config", "user.name", "AXDEV Local Trial")
    git("config", "user.email", "axdev-trial@example.invalid")
    git("add", ".")
    git("commit", "-m", "synthetic fixture")
    plan = {
        "version": 1,
        "tasks": [{
            "id": "TRIAL-001",
            "goal": "Create src/hello.py defining greet(name) returning 'Hello, ' + name. "
                    "Two pre-existing protected unittest cases must pass. "
                    "Do not edit tests or any other file.",
            "files": ["src/hello.py"],
            "depends_on": [],
            "checks": [["python", "-m", "unittest", "discover", "-s", "tests", "-q"]],
            "acceptance": [
                {"module": "src.hello", "function": "greet", "args": [name],
                 "kwargs": {}, "expected": "Hello, " + name}
                for name in ("", "Independent reviewer")
            ],
        }]
    }
    plan_file = out / "trial-plan.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    print("Synthetic repository created; original projects unchanged.")
    print("Dry run:")
    print(f'python -m axdev run --repo "{repo}" --plan "{plan_file}" '
          f'--state "{out / "state"}"')
    print("After local Ollama/OpenCode setup, add --execute to that command.")
    print("No GitHub push or customer data transfer is performed.")

if __name__ == "__main__":
    main()
