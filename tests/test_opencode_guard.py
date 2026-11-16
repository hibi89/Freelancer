import json
import unittest
from axdev.opencode_guard import validate_config_sources

class ConfigSourceTests(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "model": "ollama/qwen3:4b-instruct",
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
                {"action": "plugin.use", "resource": "opencode.provider.ollama", "effect": "allow"},
            ],
        }

    def inline_document(self, expected=None):
        config = dict(self.expected if expected is None else expected)
        provider, model = config["model"].split("/", 1)
        config["model"] = {"providerID": provider, "model": model}
        return {"type": "document", "info": config}

    def test_accepts_the_exact_inline_document_from_opencode(self):
        sources = [{"type": "directory", "path": "/tmp/home/.config/opencode"},
                   self.inline_document()]
        self.assertTrue(validate_config_sources(json.dumps(sources), self.expected))

    def test_rejects_altered_document(self):
        for key, value in (
            ("model", {"providerID": "openai", "model": "gpt"}),
            ("permissions", [{"action": "*", "resource": "*", "effect": "allow"}]),
            ("policies", []),
            ("providers", {"ollama": {"settings": {"baseURL": "https://example.com/v1"}}}),
            ("agents", {"build": {"permissions": [{"action": "*", "resource": "*",
                                                     "effect": "allow"}]}}),
        ):
            with self.subTest(key=key):
                document = self.inline_document()
                document["info"][key] = value
                self.assertFalse(validate_config_sources(json.dumps([document]), self.expected))

    def test_rejects_additional_or_unexpected_sources(self):
        approved = self.inline_document()
        for sources in (
            [],
            [approved, approved],
            [dict(approved, path="/repo/opencode.json")],
            [approved, {"type": "document", "path": "/repo/opencode.json",
                        "info": {"permissions": []}}],
            [approved, {"type": "other"}],
        ):
            with self.subTest(sources=sources):
                self.assertFalse(validate_config_sources(json.dumps(sources), self.expected))

    def test_reject_malformed_or_truncated_debug_stdout(self):
        for output in ("Not JSON", '[{"model":', json.dumps(self.expected), "x" * 65537):
            self.assertFalse(validate_config_sources(output, self.expected))

    def test_missing_tool_hard_denies_are_not_accepted(self):
        expected = dict(self.expected)
        expected["policies"] = [p for p in self.expected["policies"]
                                if p.get("resource") != "shell:*"]
        output = json.dumps([self.inline_document(expected)])
        self.assertFalse(validate_config_sources(output, expected))


if __name__ == "__main__":
    unittest.main()
