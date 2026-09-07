---
name: spec-driven-implementation
description: Use whenever the user asks to implement, pick up, work on, or start a spec (a `requirements/<slug>.md`, `lightweight/<slug>.md`, or a GitHub issue filed from one) — including phrases like "implement requirements/foo.md", "let's pick up the next requirement for flexible-scheduling", or "implement issue #58". Takes exactly one requirement (or one requirement-level issue) from an approved spec through to a verified, reviewed change: creates a branch, implements strictly within the requirement's own scope, runs this repo's own verification commands and checks off acceptance criteria, opens a PR (running whatever code-review skills are available, iterating on findings), and — only once the user explicitly says to merge — merges. Does not apply to a spec still in `draft`, or to work with no matching spec at all (that's `spec-driven-development`'s job first).
---

# Spec-driven implementation

## Why this exists

Getting a spec from `draft` to `approved` is only half the loop —
someone still has to remember the branch-naming convention, which
acceptance criteria a given piece of work actually covers, which review
steps to run, and not to merge until a human has actually looked at it.
This skill is that missing link: it picks up exactly one requirement
and carries it through to a reviewed, verified change, then stops —
"proceed to the next requirement" means running this skill again, not
looping unattended through a whole spec.

## When this applies

- The user names a spec or requirement directly ("implement
  `requirements/foo.md`", "do flexible-scheduling requirement 3"), or
  an issue filed from one, if a project-specific `spec-issue-tracking`
  skill is in use (see `spec-issue-tracking-setup`).
- The user says something like "let's start implementing" right after
  a spec was approved.

**Does not apply to:**
- A spec (or the specific requirement) still `draft` — that's
  `spec-driven-development`'s gate; stop and say so rather than
  designing-while-implementing.
- A requirement whose `design/<slug>.md` doesn't exist yet or is still
  `draft`, when the full four-type split is in use for that spec.
- Work with no matching spec at all — run `spec-driven-development`
  first.

## Step 1: Read the requirement and its spec context

- `specs/requirements/<slug>.md` (or `specs/lightweight/<slug>.md`) —
  the full requirement in context, including ones adjacent to yours
  that explain *why* a constraint exists.
- `specs/design/<slug>.md` — the "how": which files to touch, the
  approach, anything already flagged as a risk (full-split specs only).
- `specs/validation/<slug>.md` (or the lightweight file's own
  Acceptance Criteria section) — this requirement's specific acceptance
  criterion and the Test Plan section's commands for checking it.

If picking this up from a tracker issue (GitHub or GitLab), the issue's
Given/When/Then, Acceptance Criteria, and In/Out of Scope are a
*summary* of the above — trustworthy for what to build, but the spec
files are what explain constraints and sibling behavior the issue body
doesn't repeat. Read both; implement to the requirement's own scope
boundary specifically, not the whole spec (that's what the other
requirements are for — resist the pull to "fix" or implement a
neighboring requirement while you're in there, even when it looks easy
from where you're standing).

If a project-specific `spec-issue-tracking` skill is installed and this
repo also tracks work on a board (GitHub Projects, GitLab
Milestones/Iterations, ...), mark the issue in-progress and assign it
per that skill's own field-setting guidance before continuing — that's
board bookkeeping, not a prerequisite the implementation itself depends
on, so a blocked write there shouldn't stall this workflow (note it and
move on).

## Step 2: Create the branch

```
<prefix>/<slug>-<short-description>
```

`<prefix>` from the kind of change: `feature/` for new capability,
`fix/` for a bug fix, `enhancement/` for extending something that
exists. Branch from the up-to-date default branch (`git fetch`, base
off `origin/<default-branch>`), not off whatever the working tree
happens to be on.

If you need to `git stash` anything to get a clean branch (e.g.
someone else's uncommitted work sitting in the working tree when you
start), **put it back before you finish** — checkout back to the
branch it came from and `git stash pop` there, or if you can't for some
reason, say exactly what's stashed and where in your final report.

## Step 3: Implement, strictly within scope

Follow the design doc's Approach/Key Files (if this spec uses the full
split) for the pieces this requirement touches. The requirement's own
**In Scope**/Out of Scope boundary — from the issue if one exists, or
from the requirements file's Out of scope section otherwise — is
authoritative, not a starting point to expand from.

Before writing code, check whatever skills or project conventions are
available for the surface this requirement touches (frontend
frameworks, backend language, security-sensitive areas like auth or
secrets) and use the ones actually relevant to this specific change —
don't invoke every installed skill "just in case."

If something in the requirement turns out ambiguous, or the design
doc's approach doesn't quite fit what you find in the actual code, stop
and say so rather than guessing past it — same principle
`spec-driven-development` applies before code is written also applies
mid-implementation.

## Step 4: Verify against the validation spec and the quality gates

Run the command(s) from the matching validation file's (or lightweight
file's) Test Plan/Acceptance criteria section that actually exercise
*this* requirement's change — not "tests pass in general." If a
requirement's own test doesn't exist yet, write it rather than skip
this step — a requirement isn't verified by an absent test. If it
fails, fix and rerun — don't move on to Step 5 on a red check, and
don't loosen the criterion to make it pass.

Then run every command listed for this change's language(s) in
`specs/QUALITY_GATES.md` — lint/format, coverage, and security
scanning, not just the functional test above. These are blocking gates,
same as the functional test: a red lint check, a coverage drop, or a
security-scan finding means this requirement isn't done yet, even if
its own acceptance criterion passed. If `specs/QUALITY_GATES.md` still
says "not yet configured," say so plainly and suggest running
`spec-quality-tooling-setup` — don't silently skip this half of
verification just because it hasn't been set up.

Once green, check off:

1. The requirement's line in `specs/validation/<slug>.md` (or the
   lightweight file), `- [ ]` → `- [x]`.
2. If tracked as an issue, its own Acceptance Criteria checklist, same
   edit applied to the issue body text.

If this was the *last* unchecked box in that validation file, say so
explicitly and suggest the user flip the spec's own `**Status:**` line
to `verified` — don't flip it yourself; that's the user's call, same as
approving a spec in the first place.

## Step 5: Open the pull request

Search for a PR template and use it if one exists. Push the branch,
then create the PR:

- **Title**: short, references the requirement.
- **Body**: what changed and why (cite the spec file(s)), how it was
  verified (Step 4's commands and their result), and, if there's a
  linked issue, `Closes #<issue-number>`.

## Step 6: Review and iterate

Run whatever code-review (and, for security-sensitive changes,
security-review) skills or tooling this repo has configured against
the diff. Fix what's surfaced, push the update, and note in a PR
comment what changed and why. Repeat until nothing's left to fix.

## Step 7: Wait for a human, then merge

Tell the user the PR is up and ready, with a link. **Never merge
without the user explicitly telling you to** in this conversation —
not inferred from a GitHub approval appearing, not because review
found nothing left to fix. A real human approval on the PR is a good
sign to report, not a substitute for the user's own go-ahead here.

Once told to proceed: merge (respect this repo's usual merge method —
check a few recent merged PRs if unsure), and close out any linked
issue/board status per `spec-issue-tracking` if that skill is in use.

## Step 8: Report and stop

Say what's done, link the PR (and closed issue, if any), and — if there
are other open requirements in the same spec — name them as what's
next. Don't start on one yourself; "proceed to next requirement" means
the user invokes this skill again, deliberately, not that this run
keeps going.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Implementing a sibling requirement "while you're in there" | The design doc's Approach section covers the whole spec, not just this requirement | This requirement's own In Scope/Out of Scope is the boundary for *this* run — a sibling requirement is separate work |
| Marking the validation checkbox from a manual "looks right" check | Running the exact test plan command feels like extra ceremony when the change is small | Step 4's criterion is the actual command from the validation file, not a judgment call |
| Merging because a GitHub review approval appeared | It looks like the human-approval gate this skill is waiting for | The gate is the user telling *you*, in this conversation, to merge — a PR approval is evidence to report, not the trigger itself |
| Flipping the spec's `Status` to `verified` after checking the last box | Feels like the natural next step once every requirement is done | That's the user's call, same as approving a spec in the first place — say it's ready, don't do it silently |
| Branching off a stale local default branch instead of `origin/<default>` | Habit | Always `git fetch` first |
| Treating the functional test as the whole of "verified" | Quality gates feel separate from "does this requirement work" | Step 4 runs `specs/QUALITY_GATES.md`'s commands too — lint/coverage/security are part of done, not a separate later concern |
| Skipping quality gates because `specs/QUALITY_GATES.md` isn't configured yet | Easiest path forward when the file just says "not yet configured" | Say so explicitly and suggest `spec-quality-tooling-setup` — don't silently treat missing config as "nothing to check" |
