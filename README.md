# spec-driven-workflow

Portable spec-driven development workflow. Scaffolds a `specs/` folder
plus agent skill files (for Claude and/or GitHub Copilot) into a new or
existing project, so that "requirements -> design -> validation ->
implementation" is followed consistently by whichever coding agent you
use.

## Usage

```bash
npx spec-driven-workflow init
```

Run it inside the project you want to set up (new, empty, or an
existing codebase). It will ask:

- **New project or existing codebase?** (auto-detected, confirm or
  override)
- **Which agent(s)?** Claude, GitHub Copilot, or both
- **Where should specs live?** A folder in this repo (single repo or
  monorepo -- you pick the folder name, default `specs`), or a separate,
  dedicated repository for a multi-repo/polyrepo workspace (finished via
  the `spec-location-setup` skill after install, since picking an
  existing/new GitHub repo needs a live `gh` conversation).

Non-interactive / scripted use:

```bash
npx spec-driven-workflow init --mode=new --agents=both --yes
npx spec-driven-workflow init --mode=existing --agents=copilot --yes
npx spec-driven-workflow init --specs-dir=documentation --yes
npx spec-driven-workflow init --specs-location=external --yes
```

| Flag                      | Meaning                                              |
| ------------------------- | ---------------------------------------------------- |
| `--dir <path>`          | Target directory (default: current directory)        |
| `--mode <new\|existing>` | Skip auto-detection                                  |
| `--agents <list>`       | `claude`, `copilot`, or `both` (default: both) |
| `--specs-location <in-repo\|external>` | Where specs live (default: `in-repo`) |
| `--specs-dir <name>`    | Specs folder name when in-repo (default: `specs`) |
| `--yes` / `-y`        | Non-interactive: accept detected/default values      |
| `--force`               | Overwrite files that already exist                   |

## What gets created

```text
<specs-dir>/                 # "specs" by default -- your chosen name otherwise
  CONSTITUTION.md            # the rules: folder structure, spec types, status flow
  QUALITY_GATES.md           # lint/coverage/security/test commands per language (spec-quality-tooling-setup fills this in)
  _templates/                # product / requirements / design / validation / lightweight
  product/  requirements/  design/  validation/  lightweight/

.spec-workflow.json           # repo root -- records the choices made at init time
.claude/skills/<name>/SKILL.md   # if Claude was selected
.github/skills/<name>/SKILL.md   # if Copilot was selected (same SKILL.md format)
```

Every installed skill's own `specs/...` references are automatically
retargeted at install time if you picked a non-default folder name --
there's nothing to fix up by hand.

Skills installed:

- **`spec-location-setup`** -- determines whether this workspace is a
  single repo, a monorepo, or part of a multi-repo/polyrepo setup, and
  finishes configuring where specs live accordingly: a named folder
  here, or a dedicated separate GitHub repository (existing or new)
  mounted as a git submodule. Runs first if `init` deferred this choice
  (specs location: external), or any time you want to rename the folder
  or move specs to/from a dedicated repo later.
- **`spec-driven-development`** -- gates new feature/behavior-change/
  bug-fix work on an approved spec existing first.
- **`spec-driven-implementation`** -- takes one approved requirement
  through branch -> implementation -> verification -> PR -> merge.
- **`spec-new-project`** -- interviews you to produce the first
  product spec + baseline requirements on a brand-new project.
- **`spec-discovery`** -- reconstructs a baseline product/requirements
  spec from an existing codebase (structure, deps, README, tests).
- **`spec-project-customization`** -- surveys skills/tooling already in
  the project, spots gaps a project-specific skill would close (a
  distinctive framework, deploy process, review checklist, ...), and
  recommends them for approval.
- **`spec-skill-builder`** -- writes a well-formed `SKILL.md` (correct
  frontmatter, a description written as an actual discovery trigger,
  focused steps) and installs it to whichever agent skill directories
  this project uses. Used by `spec-project-customization`, or directly
  any time you want a new skill ("create a skill for X").
- **`spec-issue-tracking-setup`** -- interviews you about which issue
  tracker this project uses (GitHub, GitLab, or none) and, via
  `spec-skill-builder`, drafts and installs a project-specific
  `spec-issue-tracking` skill tailored to that system's actual
  mechanics (issues/labels plus GitHub Projects v2 fields or GitLab
  Milestones/Iterations, whichever applies) -- built at setup time, not
  shipped generically for one system.
- **`spec-quality-tooling-setup`** -- discovers this project's
  language(s) and what's already configured for lint/format, coverage,
  security scanning, and unit testing; recommends what's missing plus
  relevant MCP servers, with install instructions for this project's
  agent(s); and records the agreed commands in `specs/QUALITY_GATES.md`
  -- the file every validation/lightweight spec and
  `spec-driven-implementation` enforce against.

## Getting started after `init`

Open the project in Claude Code or VS Code (GitHub Copilot Chat) and
say:

- New project: **"let's start this project"** (runs `spec-new-project`)
- Existing codebase: **"discover specs for this codebase"** (runs
  `spec-discovery`)

If you chose a separate specs repository, say **"set up the specs
repository"** first to run `spec-location-setup` -- it picks an
existing or new dedicated GitHub repo, mounts it as a submodule, and
retargets every skill to it before the two steps above have anything
to work with.

Then say **"customize the spec workflow for this project"** to run
`spec-project-customization` -- a one-time-ish pass that looks at what
the project actually needs (beyond the generic skills above) and offers
to build project-specific skills for it via `spec-skill-builder`. Worth
re-running later as the project grows.

Say **"set up issue tracking"** to run `spec-issue-tracking-setup` if
this project tracks specs as GitHub or GitLab issues -- it asks which
system and the relevant specifics, then generates a tailored
`spec-issue-tracking` skill for exactly that setup.

Say **"set up quality tooling"** to run `spec-quality-tooling-setup` --
it checks what lint/coverage/security/testing tooling (and MCP servers)
this project already has, recommends what's missing, and records the
agreed gates in `specs/QUALITY_GATES.md` so every spec and
`spec-driven-implementation` enforce them consistently.

From there, new feature work and bug fixes naturally trigger
`spec-driven-development`, and "implement `requirements/<slug>.md`"
triggers `spec-driven-implementation`.

## Why both Claude and Copilot work from the same files

Both Claude Code and VS Code's GitHub Copilot Chat discover skills from
a `SKILL.md` file under `.claude/skills/<name>/` or
`.github/skills/<name>/` (Copilot also checks `.agents/skills/<name>/`).
This package writes the identical skill content to whichever
directories match the agent(s) you choose -- there's no separate
"Copilot version" to keep in sync.
