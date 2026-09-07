---
name: spec-skill-builder
description: Use when the user asks to create, add, write, scaffold, fix, or update a skill for this project's coding agent(s) — including phrases like "create a skill for X", "make a skill that handles Y", "turn this into a skill", or when spec-project-customization recommends a project-specific skill and the user approves it. Produces a well-formed SKILL.md (correct frontmatter, a description written as the actual discovery trigger, focused steps, a common-mistakes table) and installs it to whichever agent skill directories this project uses. Not for a one-off instruction that should apply to *every* task (that's an instructions file or AGENTS.md, not a skill) or a single parameterized task with no real multi-step workflow (that's a prompt file, not a skill).
---

# Spec skill builder

## Why this exists

A skill is only as good as its `description` (the discovery surface —
if the trigger phrases aren't in it, the agent never loads the skill)
and its focus (a skill that tries to cover everything ends up guiding
nothing well). This skill packages the format and pitfalls that this
project's own skills (`spec-driven-development`,
`spec-driven-implementation`, etc.) already follow, so a new
project-specific skill starts from the same bar instead of being
reinvented ad hoc each time.

## Step 1: Confirm a skill is actually the right primitive

| If the need is... | Use instead |
|---|---|
| A rule that should apply to *every* task, not just specific ones | An instructions file (`.github/instructions/*.instructions.md` with `applyTo`) or repo-wide `AGENTS.md`/`copilot-instructions.md`/`CLAUDE.md` |
| A single, parameterized, one-shot task ("summarize this file", "generate a changelog entry") with no real multi-step workflow | A prompt file (Copilot: `.github/prompts/*.prompt.md`) — skills are for on-demand *workflows*, not single commands |
| Something that needs its own isolated context or different tool restrictions per stage | A custom agent, not a skill |
| An on-demand, multi-step workflow triggered by specific phrasing, optionally with bundled scripts/templates | **A skill** — keep going |

If genuinely unsure, ask the user one question rather than guessing:
"does this apply to most work here, or only when X comes up?" — most
→ instructions, only-when-X → skill.

## Step 2: Pick the name and write the description first

The `name` is the folder name (kebab-case) and must match it exactly —
a mismatch silently breaks discovery in some agents. Pick something
specific enough not to collide with a skill this project already has
(check existing `.claude/skills/`, `.github/skills/`, `.agents/skills/`
folders first).

The `description` is the single most important line in the file — it's
all the agent sees when deciding whether to load the skill. Write it as
a **"Use when..." trigger list**, not a summary of what the skill does:

- Name the literal phrases a user would actually say ("implement issue
  #N", "add a migration for X", "run the release checklist").
- Name the situations that should trigger it even without those exact
  words (e.g. "any time a new API endpoint is added").
- Name what it does **not** apply to, if the boundary is easy to get
  wrong (mirrors this project's own skills, e.g.
  `spec-driven-development`'s "not for pure exploration...").
- Quote the whole description if it contains a colon — unescaped colons
  in YAML frontmatter fail silently.

## Step 3: Write the body

Follow the shape this project's own skills already use — a reader
switching between skills shouldn't have to relearn the structure each
time:

```markdown
---
name: <kebab-case, matches folder>
description: "Use when... [trigger phrases/situations]. Not for [explicit non-cases], if that's easy to get wrong."
---

# <Title>

## Why this exists
One paragraph: what gap this closes, and why it'd otherwise get
skipped or done inconsistently.

## When this applies
Bullet list of trigger situations, plus a **Does not apply to:** list
for the boundary cases.

## Step 1: ...
## Step 2: ...
(as many as the workflow genuinely needs — don't pad to look thorough)

## Common mistakes
| Mistake | Why it happens | Fix |
|---|---|---|
```

Keep steps concrete and checkable — name actual files, commands, or
questions to ask, not "verify everything works correctly." If the
skill needs a helper script (e.g. something like
`spec-issue-tracking-setup`'s bundled `scripts/project_fields.py` /
`scripts/gitlab_fields.py` reference scripts), put it under
`<skill-name>/scripts/` alongside the `SKILL.md` and reference it by
relative path.

## Step 4: Install to the right location(s)

Read `specs/.spec-workflow.json` for which agents this project is using
(`agents: ["claude", "copilot"]` or a subset) and write the **identical**
`SKILL.md` (and any bundled scripts) to each corresponding folder — the
same content works unmodified in every location:

| Agent | Location |
|---|---|
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| GitHub Copilot (VS Code) | `.github/skills/<name>/SKILL.md` |
| Other AGENTS.md-following agents | `.agents/skills/<name>/SKILL.md` |

If `.spec-workflow.json` isn't present or doesn't say, ask the user
rather than guessing, or just install to every location the project
already has a skills folder for.

## Step 5: Validate before calling it done

- Frontmatter parses as YAML — no unescaped colons in `description`,
  no tabs.
- `name` matches the folder name exactly.
- `description` actually contains the trigger words a user would say —
  read it back and ask "would this fire on the phrase that prompted
  creating it?"
- The skill doesn't duplicate an existing one (re-check Step 2's search)
  — extend the existing skill instead if the overlap is substantial.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Description summarizes what the skill does instead of when to trigger it | Feels natural to describe the skill like a feature | Rewrite as "Use when..." with literal trigger phrases — that's what the agent matches against |
| `applyTo: "**"` on an instructions file created instead of a skill | Easiest option that "always works" | If it truly applies to every file, fine — but that also burns context on every turn; a skill loaded only when needed is usually the better fit |
| One skill trying to cover several unrelated workflows | Feels efficient to bundle | Split into separate skills with their own descriptions — a vague, broad skill matches nothing precisely |
| Creating a near-duplicate of an existing skill | Didn't check what's already installed first | Step 2's search before writing anything new |
| Installing only to one agent's folder when the project supports both | Forgetting to check `.spec-workflow.json` | Always check which agents this project targets and mirror the file to all of them |
