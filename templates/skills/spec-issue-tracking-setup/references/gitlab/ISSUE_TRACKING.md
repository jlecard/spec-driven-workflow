# GitLab issue tracking -- reference

Background knowledge for drafting a project-specific `spec-issue-tracking`
skill when the user's project tracks specs as **GitLab issues**
(optionally with Milestones, Iterations, an Issue Board, or Epics). This
file is read by `spec-issue-tracking-setup`, not used directly as a
skill -- adapt it to what the user actually confirms (which of these
features their GitLab tier/instance actually has enabled) rather than
copying it verbatim.

## Mechanics this system provides

- **Issues** -- one per unit of trackable work, identified within a
  project by an `iid` (project-scoped) rather than a global id. Labels,
  assignees, weight, due date, milestone, and (if available) iteration
  all live directly on the issue.
- **Labels** -- same idea as GitHub: arbitrary tags with a name + colour.
  GitLab also supports **scoped labels** (`key::value`, e.g.
  `priority::1`), which is a good native fit for a `<slug>` grouping
  label plus `<slug>::r<n>` per-requirement labels, or just plain
  `<slug>` / `<slug>-r<n>` labels if the project doesn't use scoped
  labels elsewhere.
- **Milestones** -- a simple due-dated bucket (project- or
  group-level). The closest GitLab analog to "which release/sprint is
  this for" -- often what a GitHub Projects `Iteration` field would map
  to on a project that doesn't have GitLab Premium.
- **Iterations** -- **Premium/Ultimate only** (GitLab.com and
  self-managed EE). Time-boxed cadences, similar in spirit to GitHub
  Projects v2's Iteration field, but they're a first-class GitLab object
  (`Iteration`/`IterationCadence`), scoped to a group and inherited by
  its projects. Confirm the plan/tier before assuming these exist.
- **Epics** -- **Premium/Ultimate only**, group-level, roughly analogous
  to "one tracking issue per spec" if the user's tier has them; on a
  Free tier, use a plain tracking *issue* with task-list checkboxes
  linking to the per-requirement issues instead (GitLab issues support
  native "child issue" links since 15.x via the `Issue Links`/`Related
  issues` API, though not as deeply integrated in the UI as GitHub
  sub-issues).
- **Issue Boards** -- Kanban-style view over issues/labels, doesn't
  introduce new data beyond labels + (optionally) an assignee/milestone,
  so nothing special to script for it.
- **CLI**: `glab` (GitLab CLI), analogous to `gh`. `glab issue create`,
  `glab issue update`, `glab label create` cover most of the REST
  surface; `glab api <endpoint>` is a thin authenticated wrapper for
  anything the higher-level subcommands don't expose (e.g. iterations).

## Filing one issue per requirement (the pattern to adapt)

1. Confirm the spec doesn't already have a `**GitLab Issue:** #<iid>`
   line -- same "source of truth" principle as the GitHub reference.
2. Resolve the project path from `git remote get-url origin` (GitLab
   URLs are `https://gitlab.example.com/<group>/<subgroup>/<project>.git`
   or `git@gitlab.example.com:<group>/<project>.git` -- note self-hosted
   instances won't be `gitlab.com`, so don't hardcode the host).
3. Assign the same kind of stable IDs as the GitHub reference
   (`<slug>`, `<slug>-r<n>`, `<slug>-nfr<n>`, `<slug>-q<n>` -- GitLab
   label names are conventionally lowercase) and create every label
   first with `glab label create <name> --color <hex>` (or
   `--scoped` if using scoped labels), same idempotency concern as
   GitHub (check existing labels before assuming a colour).
4. Create one tracking issue for the spec, then one issue per functional
   requirement. Link them either via GitLab's native issue-link API
   (`glab api` against `POST /projects/:id/issues/:iid/links`, relation
   `is_child_of`/`relates_to` depending on GitLab version) or, if that
   feels heavier than the project wants, a plain checklist in the
   tracking issue's body referencing each requirement issue by `#iid` --
   confirm which the user prefers, since GitLab's UI support for this
   is less uniform than GitHub's sub-issues.
5. Same Given/When/Then + Acceptance Criteria + In/Out of Scope body
   shape as the GitHub reference -- the issue body convention doesn't
   need to change per system, only the linking/labeling mechanics do.
6. Already-shipped capability -> create then close immediately, same as
   GitHub.
7. Show every drafted title/body before calling anything, unless told
   to proceed.
8. Record `**GitLab Issue:** #<tracking-issue-iid>` back on the spec
   file once real issues exist.

## Milestones / Iterations (optional)

`scripts/gitlab_fields.py` (bundled alongside this reference) covers
the common project-board-ish fields via GitLab's REST API through
`glab api`:

```bash
python scripts/gitlab_fields.py fields                      # list open milestones + iterations
python scripts/gitlab_fields.py set --issue 51 --issue 52 \
  --field "milestone=Sprint 14" --field "iteration=current" \
  --field "labels=+bug,+priority::1" --field "weight=3" \
  --field "due_date=+3bd"
```

Iterations only resolve if the project's group actually has an
iteration cadence configured -- if `fields` comes back with none, the
tier/config doesn't have them, and the generated skill should fall back
to milestones only (or to whatever the user actually uses).

## What to ask the user before drafting the tailored skill

- Self-managed instance or gitlab.com? (affects nothing about the
  mechanics, but worth confirming the host isn't hardcoded anywhere)
- Free/Premium/Ultimate tier -- do Iterations and Epics actually exist
  here, or is Milestones + plain issues the real ceiling?
- Do they use scoped labels (`key::value`) elsewhere in the project, or
  plain labels?
- Preferred way of expressing "sub-issue of a spec": native issue
  links, or a checklist in the tracking issue's body?
- Branch-naming convention and merge method (merge commit / squash /
  fast-forward), so `spec-driven-implementation`-driven work matches
  house style. Note GitLab's own default merge-request-approval rules
  (required approvals, etc.) if this project uses them.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Assuming Iterations/Epics exist without checking the tier | They're prominent in GitLab's own docs | Run `scripts/gitlab_fields.py fields` (or ask the user) before relying on either |
| Hardcoding `gitlab.com` as the host | Most tutorials assume SaaS | Parse the actual host from `git remote get-url origin`; self-managed instances are common |
| Treating GitLab issue `iid` like GitHub's global issue number | Both look like a plain integer | `iid` is project-scoped -- always resolve issues via `glab api projects/:id/issues/:iid`, not a bare number across projects |
| Bundling two requirements into one issue | Same temptation as GitHub | One issue per requirement, always |
