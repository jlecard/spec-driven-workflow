---
name: spec-issue-tracking-setup
description: Use once, typically alongside spec-project-customization, or whenever the user asks to "track specs as issues", "set up issue tracking", "connect this to GitHub/GitLab issues", or asks whether specs are filed as issues yet. Interviews the user about which issue tracker this project uses (GitHub, GitLab, or none), then drafts and installs a project-specific `spec-issue-tracking` skill tailored to that system's actual mechanics (issues, labels, milestones, iterations, project boards) via spec-skill-builder, and records the choice in specs/CONSTITUTION.md. Does not itself file any issues -- that's the generated skill's job, once it exists.
---

# Spec issue tracking setup

## Why this exists

GitHub and GitLab track work in genuinely different ways -- GitHub has
Issues + optional Projects v2 boards with typed custom fields; GitLab
has Issues + Milestones + (tier-gated) Iterations and Epics, and a
different CLI (`glab` vs `gh`). Shipping one hardcoded "file a GitHub
issue" skill either doesn't work for a GitLab project or quietly
assumes GitHub for everyone. This skill is the one guided conversation
that figures out which system (if any) a given project actually uses,
then produces a real, working, project-specific skill for exactly that
system -- built at setup time, once, rather than guessed at generically
up front.

## When this applies

- Right after `spec-new-project` or `spec-discovery` hands off, as part
  of (or alongside) `spec-project-customization`.
- Whenever the user asks directly to wire specs up to an issue tracker.

**Does not apply to:** actually filing issues once the tailored skill
exists -- that's the generated `spec-issue-tracking` skill's job from
then on, triggered the same way `spec-driven-development` already
describes (right after a spec's `**Status:**` flips to `approved`).

## Step 1: Ask which system, if any

Ask directly rather than guessing from the git remote alone (a
`gitlab.com` or self-managed remote is a strong hint, but confirm --
some teams mirror a repo across both, or use neither and want plain
spec files only):

- **GitHub** (Issues, optionally Projects v2)
- **GitLab** (Issues, optionally Milestones/Iterations/Epics)
- **None / skip** -- specs stay plain files with no issue-filing skill;
  this is a completely valid answer, not a fallback to apologize for.

If "none," stop here: note in `specs/CONSTITUTION.md` (Step 5) that
issue tracking isn't in use, and end the conversation. Nothing else in
this skill applies.

## Step 2: Read the matching reference

Read this skill's own bundled reference file for the chosen system --
`references/github/ISSUE_TRACKING.md` or
`references/gitlab/ISSUE_TRACKING.md` -- in full before asking anything
else. It covers the real mechanics (what a board/milestone/iteration
actually is, what the CLI can and can't do natively, the filing
pattern to adapt) and a bundled reference script
(`references/<system>/scripts/*.py`) that the generated skill can copy
and reuse rather than reinventing.

## Step 3: Ask the system-specific follow-up questions

Each reference file ends with a "What to ask the user" section -- work
through it as a short conversation, not a form. In particular:

- **GitHub**: is there a Projects v2 board in use? If so, owner, project
  number, and what fields/options actually exist (run the bundled
  `project_fields.py fields` together if `gh` is available and
  authenticated).
- **GitLab**: self-managed or gitlab.com; tier (does Iterations/Epics
  actually apply); scoped labels or plain; native issue links or a
  checklist for "sub-issue of a spec."
- Either system: branch-naming convention and merge method, so the
  generated skill's guidance matches this project's actual house style
  rather than inventing one.

Skip questions whose answer is already obvious from the repo (e.g.
don't ask "what's your git host" if the remote is unambiguous) --
confirm briefly instead of re-asking from scratch.

## Step 4: Draft and install the tailored skill via spec-skill-builder

Invoke `spec-skill-builder` to produce `spec-issue-tracking` (this
exact name, regardless of system, so `spec-driven-development`'s
existing references to "if an issue-tracking skill is installed" keep
working without needing to know which system is behind it). Give it as
input:

- The chosen system's reference content from Step 2, adapted with the
  Step 3 answers baked in as concrete values (real project number/owner,
  real tier-appropriate feature set, real branch convention) -- not left
  as placeholders for a future run to fill in.
- The matching bundled script, copied into the new skill's own
  `scripts/` folder and referenced by relative path, with any
  project-specific defaults (e.g. `--project-number`) adjusted to match
  what Step 3 confirmed.
- The same body shape every skill in this project uses (Why this
  exists / When this applies+doesn't / numbered steps / common mistakes
  table) -- `spec-skill-builder` already enforces this.

## Step 5: Record the choice in the constitution

Edit `specs/CONSTITUTION.md`'s "Optional: tracking specs as issues"
section (or add it, if an older version of this file predates it) to
state plainly which system is in use and name the generated skill:

```markdown
## Optional: tracking specs as issues

This project tracks approved specs as <GitHub | GitLab> issues -- see
the `spec-issue-tracking` skill for the exact mechanics
(labels/board fields/milestones used here).
```

If the user chose "none" in Step 1, write instead that issue tracking
isn't in use and specs are plain files only -- explicit, not silent.

## Step 6: Report and note this can be redone

Tell the user what was created (or that nothing was, for "none") and
that switching systems later, or reconfiguring fields/tiers, means
running this skill again -- it isn't a one-way decision.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Assuming the system from the git remote without confirming | Feels obvious from the URL | Ask anyway -- some repos mirror across hosts or want neither wired up |
| Generating a skill still full of placeholder values ("your project number here") | Treating the reference file as the finished product | The reference is raw material; Step 3's real answers must be baked into the generated skill, not left as fill-in-the-blank |
| Assuming GitLab Iterations/Epics exist without checking tier | They're prominent in GitLab's marketing/docs | Confirm tier, or run the bundled `gitlab_fields.py fields` and see if anything comes back |
| Naming the generated skill after the system (e.g. `spec-github-tracking`) | Seems more descriptive | Keep the name `spec-issue-tracking` regardless of system, so other skills' generic references to it keep resolving |
