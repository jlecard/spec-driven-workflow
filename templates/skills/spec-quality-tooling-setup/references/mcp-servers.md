# MCP servers for quality tooling -- reference

MCP servers add value here where a *tool call* can give an agent
context or capability a plain shell command can't (live documentation,
a hosted scanning/analysis service, browser automation) -- not as a
replacement for running the project's own linter/test/coverage/security
commands directly, which is almost always simpler and faster than
routing through an MCP server. Recommend an MCP server only where it
adds something a direct CLI call doesn't.

## How to discover what's already available

1. **This session's own tool list** -- the agent running this skill
   already knows which MCP-provided tools it currently has loaded (and,
   in editors that support it, which ones are installed but deferred).
   Check that first; it's the ground truth for "what works right now,"
   more reliable than any config file.
2. **Workspace config**: `.vscode/mcp.json` (VS Code, workspace-scoped)
   and `.mcp.json` at the repo root (Claude Code, project-scoped).
3. **User-level config**: VS Code's user `mcp.json` (via Command
   Palette -> "MCP: Open User Configuration"), and Claude Code's
   `~/.claude.json` or `claude mcp list` -- these apply across all of a
   user's projects, so a server might already be available without any
   project-level file at all.

Don't assume a server is missing just because no project file mentions
it -- check user-level config or just ask the agent to list its own
tools before recommending an install.

## Categories relevant to quality gates

- **Up-to-date library/framework docs** (e.g. a server like Context7):
  useful so lint/test-framework recommendations and their config
  examples are checked against current docs rather than the model's
  training-time knowledge, which is especially prone to drift for
  fast-moving JS tooling (ESLint flat config, Vitest, etc.).
- **Community Q&A search** (e.g. a Stack Overflow-search server): useful
  when a specific lint rule/error message needs a real-world fix
  pattern, not just general advice.
- **Browser automation / E2E testing** (e.g. a Playwright or
  Chrome DevTools server): relevant to the "unit testing" category only
  insofar as the project also needs UI-level testing -- don't
  recommend this for a project with no UI.
- **SAST / dependency scanning as a hosted service** (e.g. Semgrep,
  Snyk, or a SonarQube/SonarCloud server, if the project already uses
  or is willing to adopt one of these platforms): gives an agent the
  ability to query scan results or trigger a scan directly, rather than
  only running a local CLI. Only worth adding if the project already
  has (or wants) an account on that platform -- these are hosted
  products, not free local tools.
- **Git hosting platform** (GitHub or GitLab MCP servers): already
  covered by `spec-issue-tracking-setup` if the project uses one for
  issue tracking -- don't recommend a second, separate install here if
  that skill already set one up; just note it's available for quality
  workflows too (e.g. reading CI check results on a PR).

## Deciding what to actually recommend

Ask, don't assume:

- Does the project (or the user personally) already have an account on
  a hosted scanning platform (SonarQube/SonarCloud, Snyk, Semgrep App)?
  An MCP server for a platform nobody has access to isn't useful yet --
  note it as "worth adding once you have an account" instead of
  recommending an install that will fail.
- Is there a UI to test at all? Skip browser-automation servers
  entirely for a pure backend/CLI project.
- What's the project's agent target (`specs/.spec-workflow.json`'s
  `agents` field)? Install instructions differ (see below) --
  don't give VS Code steps to a Claude-Code-only project or vice versa.

## Installation instructions

### VS Code (GitHub Copilot Chat)

Add an entry to `.vscode/mcp.json` (workspace-scoped, shareable via
version control) or the user-level `mcp.json`:

```jsonc
{
  "servers": {
    "<server-name>": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "<package-name>"]
    }
  }
}
```

Or, for a server published with a one-line install command, use the
Command Palette: **MCP: Add Server** (or `code --add-mcp '{"name":"<n>","command":"npx","args":["-y","<package>"]}'`
from a terminal). After adding, reload the MCP server (Command Palette
-> **MCP: List Servers** -> Restart) so it's picked up.

### Claude Code

```bash
claude mcp add <server-name> --transport stdio -- npx -y <package-name>
```

Add `--scope project` to write it to the repo's own `.mcp.json` (shared
with the team via version control) or `--scope user` for a personal,
cross-project install. Verify with `claude mcp list`.

### Either way

- Confirm the exact package/command name from the server's own
  published instructions at install time -- don't guess a package name
  from memory; search the relevant marketplace (VS Code's MCP
  extension gallery, or Claude Code's MCP directory) or ask the user
  for the link they have in mind.
- Some servers need an API key or token (hosted scanning platforms
  especially) -- get that from the user and store it the way the
  server's own docs specify (usually an environment variable referenced
  from the `mcp.json`/`claude mcp add` command, never hardcoded into a
  committed config file).

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Recommending an MCP server as a replacement for just running the linter/test command | MCP servers feel like the "modern" way to do everything | Only recommend one where it adds real capability (hosted service, live docs, browser automation) -- direct CLI is simpler for local lint/test/coverage |
| Guessing a package name instead of confirming it | Familiar-sounding names are easy to misremember | Search the actual marketplace/directory or ask the user before writing an install command |
| Recommending a hosted-platform server before confirming the user has an account | The server itself doesn't gate on this | Ask first -- note it as "later, once you have an account" otherwise |
| Committing an API key into `.mcp.json`/`mcp.json` | Fastest path to "it works" | Reference an environment variable per the server's own docs instead |
