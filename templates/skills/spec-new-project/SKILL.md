---
name: spec-new-project
description: Use on a brand-new, empty (or nearly empty) project that has just had spec-driven-workflow scaffolded into it, when the user wants to start building — including phrases like "let's start this project", "set up the product spec", or "walk me through getting started". Interviews the user to produce the initial product spec and baseline requirements before any code is written. Does not apply once specs/requirements/initial_requirements.md already exists and describes real content, or on an existing codebase with code but no specs (use spec-discovery there instead).
---

# Spec new project

## Why this exists

`spec-driven-development` assumes a baseline already exists to check
new work against. On a genuinely new project there's no code and no
baseline yet — this skill produces that baseline through a short
interview, so the very first feature built already has a spec behind
it instead of being the thing that "didn't need one because there was
nothing to check it against yet."

## When this applies

Right after `spec-driven-workflow init` has scaffolded `specs/` into an
empty or near-empty project, and the user is ready to start describing
what they're building. If `init`'s output said specs location is
"external (not yet configured)," run `spec-location-setup` first --
this skill needs `specs/` to actually exist. Don't run this on a
project that already has a filled-in `specs/product/` and
`specs/requirements/initial_requirements.md` — at that point just use
`spec-driven-development` for new work.

## Step 1: Interview for the product spec

Ask the user, one question at a time rather than as a wall of text:

1. What is this project, in one or two sentences? Who is it for?
2. What's the core problem it solves, or the outcome it should produce?
3. What does success look like — a few concrete, observable signals?
4. Anything explicitly out of scope at the product level (not
   implementation detail — genuine non-goals)?

Don't invent answers the user hasn't given you. If they want to skip
ahead and just describe a first feature, that's fine — capture what
they *have* said as the product spec's current best draft and note
that it can be refined later; don't block on completeness.

Write `specs/product/<slug>.md` from `specs/_templates/product.md`,
`**Status:** draft`.

## Step 2: Draft the initial requirements baseline

From the same conversation, and any first feature(s) the user describes,
draft `specs/requirements/initial_requirements.md` from
`specs/_templates/requirements.md`: numbered functional requirements
for whatever the user has described so far — this doesn't need to cover
the whole eventual product, just what's been discussed. It's fine for
this to be small; it grows over time as `spec-driven-development` adds
new capability files and, for corrections to what's already here,
amends this baseline in place.

## Step 3: Confirm and approve

Show the drafted product spec and initial requirements file to the
user before treating them as approved. Once they confirm, flip both
`**Status:**` lines to `approved` — this is the point the project has
a real baseline, and `spec-driven-development` can start doing its job
on the next feature request.

If the user wants to keep the specs in `draft` while they think it
over, that's fine — say plainly that implementation work should wait
for approval, per `spec-driven-development`'s own rule.

## Step 4: Hand off

Tell the user the baseline is in place, and suggest running
`spec-project-customization` and `spec-quality-tooling-setup` next —
the former looks for project-specific skills worth adding (framework
conventions, a deploy process, anything this new project already has
non-obvious rules for), the latter sets up lint/test/coverage/security
tooling and records it in `specs/QUALITY_GATES.md` before real feature
work starts. From there, new features or fixes go through
`spec-driven-development` as normal — no need to invoke this skill
again unless they want to revisit the product spec itself later.
