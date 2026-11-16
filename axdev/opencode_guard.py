"""Pure, conservative validator of OpenCode V2's resolved debug config.

Never prints merged configuration; it can contain user configuration secrets.
A matching config is a STATIC check, not a proof that tools obey policy.
"""
from __future__ import annotations
import json
import re

MINIMUM_RELEASE = (2, 2, 6)


def supported_release(output: str) -> bool:
    release = re.fullmatch(r"(?:opencode\s+)?v?(\d{1,4})\.(\d{1,4})\.(\d{1,4})", output.strip(), re.I)
    return release is not None and tuple(map(int, release.groups())) >= MINIMUM_RELEASE


def validate_effective(output: str, expected: dict) -> bool:
    if not isinstance(output, str) or not output or len(output) > 65536:
        return False
    try:
        effective = json.loads(output)
    except (ValueError, TypeError):
        return False
    if not isinstance(effective, dict):
        return False
    if effective.get("model") != expected.get("model"):
        return False
    providers = effective.get("providers")
    if not isinstance(providers, dict):
        return False
    ollama = providers.get("ollama")
    if not isinstance(ollama, dict):
        return False
    if ollama.get("settings", {}).get("baseURL") != "http://127.0.0.1:11434/v1":
        return False
    # Hard policies (unlike prompt text) must survive configuration merging.
    effective_policies = effective.get("policies")
    required_policies = expected.get("policies")
    if (not isinstance(effective_policies, list)
            or not isinstance(required_policies, list)):
        return False
    if effective_policies != required_policies:
        return False
    expected_rules = expected.get("permissions")
    actual_rules = effective.get("permissions")
    if not isinstance(expected_rules, list) or actual_rules != expected_rules:
        return False
    if not expected_rules or expected_rules[0] != {
            "action": "*", "resource": "*", "effect": "deny"}:
        return False
    allowed_edits = [p for p in expected_rules
                     if isinstance(p, dict) and p.get("action") == "edit"
                     and p.get("effect") == "allow"]
    if not allowed_edits:
        return False
    if any(not isinstance(p.get("resource"), str)
           or p["resource"].startswith("/")
           or ".." in p["resource"].split("/")
           for p in allowed_edits):
        return False
    hard_required = [
        {"action": "provider.use", "resource": "*", "effect": "deny"},
        {"action": "provider.use", "resource": "ollama", "effect": "allow"},
        {"action": "tool.use", "resource": "shell:*", "effect": "deny"},
        {"action": "tool.use", "resource": "webfetch:*", "effect": "deny"},
        {"action": "tool.use", "resource": "websearch:*", "effect": "deny"},
        {"action": "tool.use", "resource": "external_directory:*", "effect": "deny"},
        {"action": "mcp.use", "resource": "*", "effect": "deny"},
        {"action": "plugin.use", "resource": "*", "effect": "deny"},
        {"action": "plugin.use", "resource": "opencode.provider.ollama", "effect": "allow"},
    ]
    return all(rule in required_policies for rule in hard_required)
