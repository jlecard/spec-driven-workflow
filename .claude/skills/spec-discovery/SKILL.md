---
name: spec-discovery
description: Use on an existing codebase that has just had spec-driven-workflow scaffolded into it but has no specs yet (specs/requirements/initial_requirements.md doesn't exist or is empty) — including phrases like "discover specs for this codebase", "retro-engineer the specs", or "figure out what this app does". Explores the workspace (structure, dependencies, README, tests, existing behavior) and drafts the baseline product/requirements/design/validation docs from what it finds, then asks the user to review and approve them. Does not apply to a project that already has an approved baseline, or a brand-new empty project (use spec-new-project there instead).
---

# Spec discovery

## Why this exists

`spec-driven-development` and `spec-driven-implementation` both assume
an approved baseline exists. Dropping this workflow onto an existing,
already-built codebase means that baseline doesn't exist yet and can't
be written from an interview alone the way a new project's can — the
real behavior is already sitting in the code, and guessing at it from
a conversation would just produce a baseline that's wrong on day one.
This skill reconstructs the baseline from the codebase itself, then
lets the user correct it before it's treated as ground truth.

## When this applies

Right after `spec-driven-workflow init` scaffolds `specs/` into a
project that already has real code, and no baseline exists yet
(`specs/requirements/initial_requirements.md` is missing or still the
template placeholder). Runs once per project, typically. Re-running
later to refresh the baseline against a codebase that's drifted a lot
since is fine, but treat that as a deliberate, explicit ask, not
something to redo automatically.

## Step 1: Explore the workspace

Before drafting anything, build an actual picture of what exists:

- Read `README.md` and any top-level docs — the stated purpose is a
  strong signal for the product spec, even if it's stale in places.
- Identify the language(s)/framework(s) from manifest files
  (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.) and
  the top-level directory layout — this tells you where "requirements"
  live in the code (routes/controllers, UI components, CLI commands).
- Look for existing tests — they're often the closest thing to
  existing acceptance criteria; a test asserting a specific behavior is
  good evidence for a requirement, not just a nice-to-have to mention.
- Look for existing docs that already describe behavior (API docs,
  ADRs, a wiki, comments describing intent) and treat them as sources,
  citing them rather than re-deriving from raw code where they exist.
- Note anything that looks like a real, load-bearing constraint (an
  external API contract, a data format other systems depend on, an
  auth boundary) — these belong in the requirements file's Constraints
  section.

Don't guess at intent you can't find evidence for — if something is
genuinely ambiguous from the code alone (e.g. "is this behavior
intentional or an accident nobody's noticed"), flag it as an open
question rather than asserting it confidently either way.

## Step 2: Draft the product spec

From `specs/_templates/product.md`: what problem this project solves,
for whom, based on what Step 1 actually found — paraphrase, don't
invent framing beyond what the evidence supports. `**Status:** draft`.

## Step 3: Draft the initial requirements baseline

From `specs/_templates/requirements.md`, write
`specs/requirements/initial_requirements.md`: numbered functional
requirements describing what the app *actually does today*, grouped
sensibly (by area/feature, not forced into an artificial order). This
is a description of current behavior, not a wishlist — resist the urge
to write down what the code *should* do instead of what it *does*.
`**Status:** draft`.

## Step 4: Draft the initial design and validation baselines (optional, if useful)

If the codebase is large or architecturally non-obvious enough that a
design baseline would genuinely help future work, draft
`specs/design/initial_design.md` (architecture overview, key
files/modules per area) and `specs/validation/initial_validation.md`
(how each requirement area is actually verified today — pointing at
real existing tests/commands). Skip these for a small/simple codebase
where the requirements file alone is enough — don't pad for the sake
of filling out every template.

## Step 5: Report and get approval

Present the drafted files to the user with a short summary of what was
found and what's uncertain (the open questions from Step 1). Ask them
to review, correct anything wrong, and confirm before flipping
`**Status:**` to `approved` on each — a discovered baseline is a
starting hypothesis, not ground truth, until a human who actually knows
the project confirms it.

## Step 6: Hand off

Once approved, tell the user the baseline is in place, and suggest
running `spec-project-customization` and `spec-quality-tooling-setup`
next — the exploration this skill just did (framework, tooling,
conventions) is exactly what those skills use, respectively, to
recommend project-specific skills and to set up/record lint, test,
coverage, and security-scanning gates in `specs/QUALITY_GATES.md`.
From there, new work goes through `spec-driven-development` as normal.
