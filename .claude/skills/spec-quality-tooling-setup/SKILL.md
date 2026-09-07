---
name: spec-quality-tooling-setup
description: Use once, typically alongside spec-project-customization and spec-issue-tracking-setup right after a baseline spec exists, or whenever the user asks to "set up quality tooling", "check code quality tools", "recommend MCP servers", or "what linting/testing/security tools should this project use". Discovers what's already configured (linters, formatters, test runners, coverage, security scanners, MCP servers) for this project's language(s), recommends what's missing per category, gives environment-specific installation instructions (VS Code/Copilot, Claude Code), and records the agreed gates in specs/QUALITY_GATES.md so spec-driven-implementation and every validation/lightweight spec enforce them consistently. Does not itself install packages or MCP servers without the user's confirmation of each one.
---

# Spec quality tooling setup

## Why this exists

"Write tests" and "keep the code clean" are easy to say and easy to
skip under time pressure unless something concrete enforces them. Left
implicit, quality expectations drift into whatever each contributor (or
each agent session) happens to remember to check. This skill makes that
explicit and durable: it surveys what's already in place, closes gaps
across four categories (lint/style, coverage, security scanning, unit
testing) plus language-specific best-practice tooling, and writes the
result to `specs/QUALITY_GATES.md` — a single file every other skill in
this project can point at instead of re-deciding "what counts as
passing" each time.

## When this applies

- Right after `spec-new-project` or `spec-discovery` hands off, same
  moment as `spec-project-customization`/`spec-issue-tracking-setup`.
- Whenever the user asks to review, set up, or recommend quality
  tooling or MCP servers for the project.

**Does not apply to:** recommending project-specific *workflow* skills
(that's `spec-project-customization`) or issue-tracker setup (that's
`spec-issue-tracking-setup`) — this skill is scoped to code-quality
enforcement and the tools/MCP servers that support it.

## Step 1: Detect the project's language(s)

Reuse whatever `spec-discovery` already found if it just ran; otherwise
look at manifest files (`package.json`, `pyproject.toml`, `go.mod`,
`Cargo.toml`, `*.csproj`/`*.sln`, `Gemfile`, `composer.json`) and the
top-level layout. A project can be polyglot (e.g. a Python API + a
TypeScript frontend) — handle each language found, don't force a single
answer.

## Step 2: Discover what's already configured

For each language found, look for:

- **Lint/format**: config files (`.eslintrc*`, `.prettierrc*`,
  `ruff.toml`/`pyproject.toml`'s `[tool.ruff]`, `.golangci.yml`,
  `rustfmt.toml`, `.rubocop.yml`, `.editorconfig`) and the matching
  dependency/devDependency entries.
- **Coverage**: config or dependency for a coverage tool (`nyc`, `c8`,
  `coverage.py`/`pytest-cov`, `go test -cover` usage in CI, etc.) and
  whether a threshold is enforced anywhere (CI workflow, `pyproject.toml`,
  `package.json`).
- **Security scanning**: CI workflow files referencing CodeQL,
  Dependabot config (`.github/dependabot.yml`), `npm audit`/`pip-audit`/
  `cargo audit` steps, Semgrep/Snyk config, secret-scanning settings.
- **Unit testing**: the test runner already in use and whether it's
  wired into CI (don't recommend a second, competing framework just
  because it's popular).
- **MCP servers already available**: check for `.vscode/mcp.json`,
  `.mcp.json` at the repo root, and note (from the current session's
  own tool list) which MCP-provided tools are already loaded — this
  skill runs *inside* an agent session, so "what's already available to
  me right now" is directly observable, not something to guess at.

Read `references/language-tooling.md` (bundled with this skill) for the
common tool per category per language, and `references/mcp-servers.md`
for how to discover/install MCP servers and which ones are relevant to
each quality category. Treat both as a menu to select from with the
user, not a checklist to apply blindly — a project already using a
perfectly good tool doesn't need a replacement.

## Step 3: Present gaps and recommendations

For each language, one short block per category that's missing or
weak:

```
### <language> — <category>
Currently: <what's there today, or "nothing configured">
Recommend: <specific tool>, because <one-line reason>
Install: <the exact command(s), from references/language-tooling.md>
```

Do the same for MCP servers worth adding (from
`references/mcp-servers.md`), tailored to which agent(s) this project
targets (`specs/.spec-workflow.json`'s `agents` field) and to whatever
the user says about their local environment (OS, whether Docker/network
access is available for a server that needs it) — ask rather than
assume when a server's install path depends on it.

## Step 4: Confirm before changing anything

Show the full recommendation list and only install/configure what the
user explicitly approves — per item, not as an all-or-nothing batch.
Installing a dependency, writing a config file, or adding an MCP server
entry are all real changes to the project; drafting first is cheap and
lets the user say no to any one of them without blocking the rest.

For approved package/tool installs, run the project's own package
manager (`npm install -D`, `pip install`/add to `pyproject.toml`, etc.)
rather than editing manifests by hand. For approved MCP servers, follow
`references/mcp-servers.md`'s install instructions for this project's
agent(s) — typically writing an entry to `.vscode/mcp.json` (Copilot)
and/or running `claude mcp add` or editing `.mcp.json` (Claude Code).

## Step 5: Record the gates in specs/QUALITY_GATES.md

Rewrite `specs/QUALITY_GATES.md` (created as a placeholder at `init`
time) to state, per language actually present in the project:

```markdown
## <language>

- **Lint/format**: `<command>`
- **Coverage**: `<command>`, threshold: <e.g. 80% lines>
- **Security scanning**: `<command>`
- **Unit tests**: `<command>`
```

Plus a short "MCP servers configured" list (name, purpose, where it's
registered) if any were added in Step 4. This file is what
`spec-driven-implementation` and every `validation/`/`lightweight` spec
now point at instead of re-discovering commands each time — keep it
accurate as tooling changes, don't let it silently go stale.

## Step 6: Confirm the constitution references it

`specs/CONSTITUTION.md`'s "Quality gates" section should already point
at `specs/QUALITY_GATES.md` (installed that way by default) — if an
older version of this file predates that section, add it rather than
assuming it's there.

## Step 7: Report and note this can be redone

Say what was configured, what was declined, and that adding a new
language, changing a tool, or revisiting MCP servers later just means
running this skill again — it's not a one-way decision.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Recommending a second linter/test framework alongside one already in use | Treating the reference catalog as mandatory rather than a gap-filler | Step 2's discovery comes first — only recommend what's actually missing or clearly inadequate |
| Installing tools/MCP servers without per-item confirmation | Batch approval feels more efficient | Step 4 requires per-item confirmation — some recommendations will be legitimately declined |
| Writing `specs/QUALITY_GATES.md` with vague commands ("run the linter") | Copying the reference catalog's generic examples directly | Use this project's actual resolved command, the same way Step 2's discovery found it |
| Assuming an MCP server needs no extra setup (API keys, Docker, network access) | The reference catalog can't know every environment | Ask about the user's actual environment before recommending a server that needs something they may not have |
