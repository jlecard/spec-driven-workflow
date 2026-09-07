# GitHub issue tracking -- reference

Background knowledge for drafting a project-specific `spec-issue-tracking`
skill when the user's project tracks specs as **GitHub Issues** (optionally
with a GitHub Projects v2 board). This file is read by
`spec-issue-tracking-setup`, not used directly as a skill -- adapt it to
the specifics the user actually confirms (do they use a Projects v2 board
at all? what fields does it have? what's their branch/merge convention?)
rather than copying it verbatim.

## Mechanics this system provides

- **Issues** -- one per unit of trackable work. Support parent/child via
  `parent_issue_number` (sub-issues), which is how "one tracking issue per
  spec, one sub-issue per requirement" is naturally modeled.
- **Labels** -- arbitrary tags with a name + colour. Good fit for a
  `<slug>` grouping label plus one `<slug>-R<n>` label per requirement, so
  a person can filter to "everything for this spec" or "this exact line."
- **Projects v2 board (optional)** -- a separate system from labels/issues,
  with its own typed fields (single-select, iteration, date, number,
  text). Common fields: `Status`, `Team`, `Iteration`, `Start date`,
  `Target date`. Reading/writing these requires GraphQL (`gh api graphql`)
  -- there is no higher-level `gh` subcommand for custom board fields.
- **CLI**: `gh` (GitHub CLI), already authenticated in most environments
  this skill runs in. `gh issue`, `gh label`, `gh pr` cover the REST-ish
  surface; `gh api graphql` is needed for Projects v2 fields.

## Filing one issue per requirement (the pattern to adapt)

1. Confirm the spec doesn't already have a `**GitHub Issue:** #<n>` line
   -- that line, not a live search, is the source of truth for "already
   filed."
2. Resolve `owner/repo` from `git remote get-url origin`.
3. Assign a stable ID to every functional requirement (`<slug>-R<n>`),
   non-functional requirement (`<slug>-NFR<n>`), and open question
   (`<slug>-Q<n>`), plus one spec-wide grouping label (`<slug>`). Create
   every label (`gh label create ... --force`) *before* creating any
   issue that references it -- `gh issue create --parent-issue-number`
   fails outright on an unrecognized label name.
4. Create one tracking issue for the spec (links to the spec file(s),
   non-functional requirements, notes that functional requirements are
   sub-issues). Then one issue per functional requirement
   (`parent_issue_number` = tracking issue), each with Given/When/Then,
   Acceptance Criteria (pulled from the matching validation file),
   In Scope / Out of Scope. Then one issue per open question, left open
   regardless of the rest of the spec's shipped status.
5. If the capability is already shipped (validation file `verified`),
   create issues pre-closed (create, then close) rather than open --
   they're a retrospective record, not pending work.
6. Show every drafted title/body before calling the API, unless the user
   already said to go ahead.
7. Record `**GitHub Issue:** #<tracking-issue-number>` back on the spec
   file once real issues exist -- never write that line after a failed
   create (it would make a future run believe this spec is already
   filed).

## Projects v2 board fields (optional)

If the user's repo tracks issues on a Projects v2 board, `gh` has no
native command for custom fields -- everything goes through
`gh api graphql`. `scripts/project_fields.py` (bundled alongside this
reference) already implements the generic version of this: resolving
field/option/iteration ids fresh every call (never hardcoded, since an
Iteration's id changes every rollover), and applying a value by field
*name* rather than hand-writing GraphQL per field:

```bash
python scripts/project_fields.py fields                       # list fields/options/iterations
python scripts/project_fields.py set --issue 51 --issue 52 \
  --field "Status=In progress" --field "Start date=today" \
  --field "Target date=+3bd"
```

`--owner`/`--project-number` default to the repo's own owner and project
number 1 -- confirm the real project number with the user and bake it
into the generated skill's example commands rather than leaving it as a
guess.

Setting a field requires the `gh` token to carry the `project` scope,
which many pre-existing tokens don't have:

```bash
gh auth refresh -s project -s read:project
```

This opens a browser consent step only the user can complete.

## What to ask the user before drafting the tailored skill

- Do they use a Projects v2 board at all, or just plain issues/labels?
- If yes: project owner (user or org) and project number; which fields
  actually exist (run `scripts/project_fields.py fields` together, or
  ask them to check the board); what "Status" options exist and what
  the in-progress/done ones are called.
- Preferred branch-naming convention (`feature/<n>-<slug>`, etc.) and
  merge method (merge commit / squash / rebase), so
  `spec-driven-implementation`-driven work matches house style.
- Whether non-functional requirements and open questions should really
  become separate issues here, or if this repo's convention is lighter
  weight.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Creating labels and issues in the same pass | Feels like one step | Pre-create every label the batch needs first -- `create` with an unrecognized label fails and creates nothing |
| Hardcoding a field/option/iteration id from a previous run's output | Tempting once you've seen it in a transcript | Always call through the script, which re-resolves every id live |
| Writing `**GitHub Issue:**` after a failed create | Wanting the spec to reflect "handled" | Only write it once issues genuinely exist |
| Bundling two requirements into one issue | They feel closely related | One issue per requirement, always |
