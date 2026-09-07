---
name: spec-location-setup
description: Use once, before spec-new-project or spec-discovery, or whenever the user asks to "set up the specs repository", "move specs to their own repo", "change the specs folder name", or "where should specs live". Determines whether this workspace is a single repo, a monorepo, or part of a multi-repo/polyrepo setup, and configures specs/ accordingly -- a folder in this repo (asking for a name, default "specs"), or a dedicated separate GitHub repository (existing or newly created) mounted as a git submodule. Retargets every "specs/..." reference across installed skills and templates to the final path. Does not draft any spec content itself -- that's spec-new-project/spec-discovery's job, once this is done.
---

# Spec location setup

## Why this exists

Every other skill in this project reads and writes paths like
`specs/requirements/<slug>.md` -- that assumes specs live in a plain
folder called `specs` inside the current repo. That's true for a single
repository or a monorepo, but a workspace split across many separate
repositories often wants one shared, independently-versioned specs repo
instead (so a spec can outlive, or span, any one code repo). This skill
is the one place that decision gets made and every path reference gets
retargeted to match -- so nothing downstream has to guess or drift.

## When this applies

- Right after `init` scaffolds the project, if it deferred this (the
  CLI's own output says "specs location: external (not yet
  configured)") -- run this before `spec-new-project`/`spec-discovery`.
- Whenever the user wants to reconfigure later: rename the folder,
  or move specs into (or out of) a dedicated repository.

**Does not apply to:** drafting spec content -- that's
`spec-new-project` (new project) or `spec-discovery` (existing
codebase), run after this skill finishes.

## Step 1: Determine the workspace shape

Ask directly rather than guessing:

- **Single repository** -- one project, one repo.
- **Monorepo** -- multiple projects/packages, but still one repo.
- **Multiple separate repositories (polyrepo)** -- this workspace is
  one of several independent repos that share (or should share) a
  single source of truth for specs.

The first two get the same answer here (a folder inside *this* repo);
only the third genuinely needs a separate, dedicated repository.

## Step 2: Single repo / monorepo -- pick a folder name

Ask what the specs directory should be called (default `specs`). If
`init` already scaffolded a default `specs/` folder and the user now
wants a different name, or this is a rename of an already-in-use
folder:

1. `git mv <old-name> <new-name>` (preserves history) rather than a
   plain filesystem move, if the project is in a git repo already.
2. Retarget every reference (Step 4) from the old name to the new one.
3. Update `.spec-workflow.json` (repo root) -- `specsDir` and
   `specsLocation: "in-repo"`.

If this is fresh (nothing to rename yet), just scaffold going forward
with the chosen name -- there's nothing to move.

## Step 3: Polyrepo -- attach a dedicated specs repository

Ask whether to use an **existing** repository or **create a new one**:

- **Existing**: list candidates rather than asking the user to type a
  full URL from memory --
  ```bash
  gh repo list <owner-or-org> --limit 100
  ```
  Confirm the exact one they mean before proceeding.
- **New**: ask for a name (and visibility -- private/public; default to
  private unless told otherwise), then create it:
  ```bash
  gh repo create <owner-or-org>/<name> --private --confirm
  ```

Ask what local folder name to mount it at (default `specs`, same as
the in-repo case -- there's no requirement that it differ just because
it's a separate repo underneath). Then attach it as a **git
submodule** -- this is the correct mechanism for "a separate,
independently-versioned repo, nested at a path in this one," as
opposed to a plain nested folder (which git can't represent cleanly)
or copying files in (which loses the separate versioning entirely):

```bash
git submodule add <repo-url> <folder-name>
git submodule update --init --recursive
```

If the chosen folder already has real content in it (a rename-to-external
scenario, not a fresh setup), move that content into the freshly-cloned
submodule's working tree and commit it there (in the submodule's own
repo), rather than leaving it stranded outside the mounted path.

Update `.spec-workflow.json` (repo root): `specsLocation: "external"`,
`specsDir: "<folder-name>"`, and record the submodule's repo URL so a
future run of this skill (or a teammate) doesn't have to rediscover it.

## Step 4: Retarget every "specs/..." reference

Every installed skill (`.claude/skills/**/SKILL.md`,
`.github/skills/**/SKILL.md`, and any others this project's
`.spec-workflow.json` lists agents for) and the specs templates
themselves (`<folder>/CONSTITUTION.md`, `<folder>/QUALITY_GATES.md`,
`<folder>/_templates/*.md`) were written assuming the folder is
literally named `specs`. If the final folder name is anything else,
find and replace the **whole path-segment** `specs/` with
`<folder-name>/` across all of those files -- use your own
file-search/edit tools (search for the literal string `specs/` as a
path prefix, not just the word "specs" on its own, to avoid touching
unrelated prose) rather than assuming a particular shell's `sed`/`grep`
is available, since this skill runs across whatever OS the user's
agent happens to be on.

Skip this step entirely if the folder is still named `specs` (the
common case) -- there's nothing to retarget.

## Step 5: Confirm and report

Show what changed: the folder's final location (in-repo path, or
external repo URL + local mount path), and confirm `.spec-workflow.json`
reflects it accurately. If specs didn't exist yet (fresh `external`
setup deferred from `init`), tell the user to run `spec-new-project` or
`spec-discovery` next now that `specs/` genuinely exists.

## Common mistakes

| Mistake | Why it happens | Fix |
|---|---|---|
| Nesting a separate specs repo as a plain folder instead of a submodule | Feels simpler than learning submodule commands | A plain nested folder with its own `.git` confuses the parent repo's git (untracked/ambiguous state) -- always use `git submodule add` |
| Forgetting to retarget path references after a rename | Easy to treat the folder move as the whole job | Step 4 is not optional once the name differs from `specs` -- every skill's own instructions still say `specs/...` otherwise |
| Assuming a shell's `sed`/`grep -r` is available for Step 4 | Common Unix habit | Use your own file tools instead -- this skill runs on whatever OS the agent's host has |
| Creating a new specs repo without asking about visibility | Defaults matter less for code than for planning docs | Confirm private/public explicitly -- specs can contain product/business detail the team may not want public |
| Skipping `git mv`/history-preserving move on a rename | Plain filesystem move is one command | Use `git mv` when the project is already a git repo so file history survives |
