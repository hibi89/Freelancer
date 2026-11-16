# OpenCode V2 effective-config fail-closed guard

Before every live model call, AX Dev Factory now runs
\`opencode debug config\` in the **same Git worktree and environment** as
the coding call. It validates the merged, resolved JSON without writing
or echoing the returned configuration. The check expects:

- exactly the requested \`ollama/\` model and \`enabled_providers: ["ollama"]\`;
- provider endpoint \`http://127.0.0.1:11434/v1\`;
- the full ordered permissions including task-specific edit allowlist;
- hard V2 policies that deny other providers, shell commands, web tools,
  MCP tools, plugins and external-directory access.

If the installed CLI does not support \`debug config\`, the output is
invalid/truncated, or global/project/managed settings changed the
result, the controller returns a generic failure and **does not make
the model call**. This may block an otherwise working host; inspect
the installed OpenCode version and its documented V2 schema, rather
than disabling the gate or reducing the checks. The full merged output
is never saved because it may contain secrets.

Official V2 references:
https://opencode.ai/docs/cli/commands
https://opencode.ai/docs/policies/
https://opencode.ai/docs/permissions/

A matching resolved config is NOT an OS sandbox, network isolation,
file-system confinement or a runtime tool-enforcement proof. The first
trial must use a disposable checkout, no secrets, non-admin Windows
user and a locally installed Ollama model. Never auto-push/merge.
