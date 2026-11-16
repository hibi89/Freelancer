import json
import unittest
from axdev.opencode_guard import validate_effective

class EffectiveConfigTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "model": "ollama/qwen3:4b-instruct",
            "enabled_providers": ["ollama"],
            "providers": {"ollama": {"settings": {"baseURL": "http://127.0.0.1:11434/v1"}}},
            "permissions": [
                {"action": "*", "resource": "*", "effect": "deny"},
                {"action": "edit", "resource": "src/hello.py", "effect": "allow"},
            ],
            "policies": [
                {"action": "provider.use", "resource": "*", "effect": "deny"},
                {"action": "provider.use", "resource": "ollama", "effect": "allow"},
                {"action": "tool.use", "resource": "shell:*", "effect": "deny"},
                {"action": "tool.use", "resource": "webfetch:*", "effect": "deny"},
                {"action": "tool.use", "resource": "websearch:*", "effect": "deny"},
                {"action": "tool.use", "resource": "external_directory:*", "effect": "deny"},
                {"action": "mcp.use", "resource": "*", "effect": "deny"},
                {"action": "plugin.use", "resource": "*", "effect": "deny"},
            ],
        }

    def test_exact_safe_resolved_config(self):
        self.assertTrue(validate_effective(json.dumps(self.expected), self.expected))

    def test_strictly_fail_on_provider_or_policy_merge(self):
        for key, value in (
            ("enabled_providers", ["ollama", "openai"]),
            ("model", "openai/gpt"),
            ("permissions", [{"action": "*", "resource": "*", "effect": "allow"}]),
            ("policies", []),
        ):
            with self.subTest(key=key):
                tampered = dict(self.expected, **{key: value})
                self.assertFalse(validate_effective(json.dumps(tampered), self.expected))

    def test_reject_malformed_or_truncated_debug_stdout(self):
        self.assertFalse(validate_effective("Not JSON", self.expected))
        self.assertFalse(validate_effective('{"model":', self.expected))
        self.assertFalse(validate_effective("x" * 65537, self.expected))

    def test_missing_tool_hard_denies_are_not_accepted(self):
        expected = dict(self.expected)
        expected["policies"] = [p for p in self.expected["policies"]
                                if p.get("resource") != "shell:*"]
        self.assertFalse(validate_effective(json.dumps(expected), expected))


if __name__ == "__main__":
    unittest.main()
