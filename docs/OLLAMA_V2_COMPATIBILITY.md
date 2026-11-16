# V2 built-in Ollama provider and capability preflight — 2026-11-16

The official OpenCode V2 docs describe **native Ollama model discovery** through
`http://127.0.0.1:11434` and `providers.ollama.settings.baseURL`. The old
manually attached OpenAI-compatible provider `package` was removed to avoid
overriding V2's built-in Ollama discovery. The legacy
`enabled_providers` allowlist was removed in favor of the V2
`provider.use` hard policy: deny `*`, allow `ollama`.

Plugins remain denied by default; only the built-in discovery plugin
`opencode.provider.ollama` is allowed. A matching **merged** OpenCode V2
configuration is still required before any model invocation. Plugin naming
and actual enforcement require a real installed V2 trial and remain unverified.

Local preflight now uses only `127.0.0.1:11434/api/tags` and
`127.0.0.1:11434/api/show` to check that the **exact selected model**
exists and advertises both `completion` and `tools` capabilities.
A model that can chat but lacks tool calling is **not** accepted for
autonomous coding. This check makes no remote connections, installs
no model and reads no source files. A matching capability report is
necessary but insufficient for a successful tool-calling E2E.

References:
- https://opencode.ai/docs/providers/#ollama
- https://opencode.ai/docs/policies/
- https://opencode.ai/docs/config/

No claim of Windows GTX1050Ti or OpenCode V2 tool enforcement has been made.
