<!--
The "what." Depends on the product spec (specs/product/<slug>.md) as
background, not a new one per feature -- see that file for the overall
why.

For a small correction to already-documented behavior: amend
specs/requirements/initial_requirements.md in place. For a new,
separately-shippable capability: copy this file to
specs/requirements/<slug>.md instead (kebab-case, descriptive, no
number needed -- e.g. new-button-cross.md).

Someone implementing from this file alone shouldn't need to guess at
behavior.
-->

# <feature name> — Requirements

**Depends on:** `product/<slug>.md`
**Status:** draft | approved

## Functional requirements

Numbered, each independently testable/checkable:

1. ...
2. ...

## Non-functional requirements

Only include categories that actually apply -- delete the rest, don't
pad with boilerplate ("must be secure," "must be fast"):

- **Performance:** ...
- **Accessibility:** ...
- **Cost:** flag anything that meaningfully changes the running cost
  of this project (new paid service, higher tier, etc.), if that's a
  concern for this project.

## Constraints

Real, pre-existing constraints that shape the solution space (technical
or otherwise) -- not requirements themselves, but things any valid
design must respect. Look for these in the codebase before guessing --
existing contracts, data-write boundaries, external dependencies.

- ...

## Out of scope

Things within the product goal that this iteration explicitly defers
(as opposed to the product spec's non-goals, which are never in scope).

- ...

## Open questions

Delete this section if there are none. Otherwise: what's unresolved,
and who/what resolves it before the corresponding `design/` file can be
written.
