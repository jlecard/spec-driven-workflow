---
name: spec-project-customization
description: Use once, right after spec-new-project or spec-discovery finishes setting up a baseline, or whenever the user asks to "customize the spec workflow", "set up project-specific skills", "review what skills this project has", or "recommend skills for this project". Surveys the project's already-installed skills and its actual tooling/conventions, identifies gaps where a project-specific skill would materially help spec-driven-development or spec-driven-implementation, and — for each gap the user approves — hands off to spec-skill-builder to actually create it. Does not author skills itself; it's the discovery-and-recommendation step, not the writing step.
---

# Spec project customization

## Why this exists

The skills this package installs (`spec-driven-development`,
`spec-driven-implementation`, etc.) are deliberately generic — they
work on any project, but that means they know nothing about *this*
project's specific framework quirks, deploy process, review checklist,
or test harness. Left alone, that knowledge either never gets written
down or gets re-explained in chat every time. This skill is the one
deliberate pass, right after the baseline spec exists, that looks at
what's already there and proposes closing the gaps — rather than
leaving "should we have a skill for this?" as a question nobody
schedules time to ask.

## When this applies

- Right after `spec-new-project` or `spec-discovery` reports the
  baseline is approved and hands off.
- Whenever the user explicitly asks to review, set up, or recommend
  skills for the project.

**Does not apply to:** authoring the skill content itself — that's
`spec-skill-builder`'s job once a specific skill is approved here.
Also does not cover lint/test/coverage/security tooling or MCP servers
for quality enforcement — that's `spec-quality-tooling-setup`'s
dedicated job, or issue-tracker setup — that's `spec-issue-tracking-setup`'s.
This skill is for everything else a project might benefit from a
custom *workflow* skill for.

## Step 1: Inventory what's already installed

List every existing skill folder — `.claude/skills/*/`,
`.github/skills/*/`, `.agents/skills/*/` — and read each `SKILL.md`'s
`description` (not the whole body, unless something's ambiguous). Note
which ones came from this package (`spec-*`) versus ones already
present in the project before or after it. This is purely so Step 4
doesn't recommend something that already exists — every agent session
already sees the live skill listing on its own, so there's no file to
update just because a skill exists.

## Step 2: Survey the project's actual conventions

Look for load-bearing, non-obvious knowledge that isn't captured
anywhere a coding agent would find it on its own:

- **Test/lint/build tooling**: is there a distinctive way to run or
  interpret tests beyond a plain `npm test`/`pytest` (a custom harness,
  a required fixture setup, flaky-test handling)? (The base tools
  themselves — which linter, which coverage/security scanner — are
  `spec-quality-tooling-setup`'s job, not this skill's; only note
  project-specific *workflow* quirks around them here.)
- **Framework/architecture conventions**: a specific pattern this
  codebase always follows (state management approach, API layer
  conventions, a required file layout for new modules) that a generic
  agent would otherwise guess at inconsistently.
- **Review/release process**: CODEOWNERS, a PR template, required
  checks, a release/deploy runbook, anything with steps someone has to
  remember in the right order.
- **Domain-specific correctness rules**: anything where getting it
  wrong is expensive or hard to notice (money/rounding rules, a
  regulated-data boundary, an external contract other systems depend
  on) that isn't just "write a spec for it" but "here's how we always
  check this class of change."

If `spec-discovery` was just run, reuse what it already found rather
than re-exploring from scratch. On a new project with little code yet,
this step may turn up little or nothing — that's a fine outcome, say so
rather than inventing gaps.

## Step 3: Filter to what's actually worth a skill

Not every convention needs a dedicated skill — a one-line rule belongs
in an instructions file instead (see `spec-skill-builder`'s Step 1
table). Only propose a skill where there's a real, multi-step, on-demand
workflow: something with more than one step, that comes up repeatedly,
where getting it wrong or forgetting a step has a real cost.

## Step 4: Present recommendations

For each candidate, one short block — not a wall of prose:

```
### <candidate name>
Why: <one sentence — what gap this closes>
Trigger: <when it would fire, in plain language>
```

Also note, briefly, anything from Step 2 that's real but doesn't
warrant a full skill (suggest an instructions file instead, if so).

## Step 5: Hand off approved candidates

For each recommendation the user approves, invoke `spec-skill-builder`
with that candidate's name/why/trigger as the starting brief. Skip (and
say so) anything the user declines — don't create it "just in case."

## Step 6: Report and note this can be re-run later

Summarize what was created and what was skipped. Mention that as the
project grows, running this skill again — after a new integration, a
new subsystem, or a painful incident that revealed a missing process —
is a normal, expected thing to do, not a one-time setup step.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Recommending a skill for a one-off rule | Skills feel like the "official" way to capture knowledge | Check Step 3's bar first — a single always-true rule is an instructions file, not a skill |
| Re-recommending a skill that already exists | Skipped Step 1's inventory | Always list existing skills before proposing new ones |
| Creating skills the user didn't approve | Treating recommendations as a to-do list rather than options | Step 5 only acts on explicit approval, per-candidate |
| Doing this before a baseline spec exists | Jumping straight to customization | Run `spec-new-project`/`spec-discovery` first — this skill assumes that context exists |
