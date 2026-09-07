<!--
The "how do we know it's actually done." Depends on the matching
requirements/ and design/ files. Written before or during
implementation, not after -- writing it after tends to produce criteria
that just describe whatever got built, rather than actually checking
the requirements.

For a correction to the current baseline: amend
specs/validation/initial_validation.md in place. For a new capability:
copy this file to specs/validation/<slug>.md using the *same slug* as
the requirements/design files it validates.
-->

# <feature name> — Validation

**Depends on:** `requirements/<slug>.md`, `design/<slug>.md`
**Status:** draft | approved | verified

## Acceptance criteria

One checkbox per functional requirement in the matching `requirements/`
file at minimum (link back by number) -- "is this finished?" should
never be a judgment call:

- [ ] Requirement 1: ...
- [ ] Requirement 2: ...

## Test plan

How this actually gets verified. Concrete commands/steps, not "test
thoroughly" -- use this repo's own real test/lint/build commands
(check `package.json` scripts, a `Makefile`, or CI workflow files
before inventing new ones):

- e.g. `npm test`, `pytest`, `go test ./...` -- whichever this repo
  actually uses for the layer this change touches.
- UI-facing change -> whatever this repo's own end-to-end/manual smoke
  process is, if it has one.
- Infra change -> plan-before-apply, plus whatever the change actually
  touches live.
- **Quality gates**: the lint/format, coverage, and security-scanning
  commands from `specs/QUALITY_GATES.md` for every language this
  change touches, in addition to the functional tests above -- these
  are not optional extras, they're part of what "done" means for every
  requirement, not just this spec's own numbered criteria.

## Open questions

Delete if none.
