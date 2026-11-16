"""Validate the configuration sources reported by OpenCode V2."""
from __future__ import annotations
import json
import re

MINIMUM_RELEASE = (2, 2, 6)


def supported_release(output: str) -> bool:
    release = re.fullmatch(r"(?:opencode\s+)?v?(\d{1,4})\.(\d{1,4})\.(\d{1,4})", output.strip(), re.I)
    return release is not None and tuple(map(int, release.groups())) >= MINIMUM_RELEASE


def validate_config_sources(output: str, expected: dict) -> bool:
    if not isinstance(output, str) or not output or len(output) > 65536:
        return False
    try:
        sources = json.loads(output)
    except (ValueError, TypeError):
        return False
    if not isinstance(sources, list):
        return False
    # debug config lists each source. Only the inline document is trusted.
    # Directory entries contain paths, while a file or remote source could
    # introduce agent permissions, providers or other configuration.
    documents = []
    for source in sources:
        if not isinstance(source, dict):
            return False
        if (source.keys() == {"type", "path"} and source["type"] == "directory"
                and isinstance(source["path"], str) and source["path"]):
            continue
        if source.keys() != {"type", "info"} or source["type"] != "document":
            return False
        documents.append(source["info"])
    model = expected.get("model")
    if not isinstance(model, str):
        return False
    provider, _, model_id = model.partition("/")
    if provider != "ollama" or not model_id:
        return False
    decoded = dict(expected, model={"providerID": provider, "model": model_id})
    if documents != [decoded]:
        return False
    if expected.get("providers") != {
        "ollama": {"settings": {"baseURL": "http://127.0.0.1:11434/v1"}},
    }:
        return False
    required_policies = expected.get("policies")
    if not isinstance(required_policies, list):
        return False
    expected_rules = expected.get("permissions")
    if not isinstance(expected_rules, list) or not expected_rules or expected_rules[0] != {
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
