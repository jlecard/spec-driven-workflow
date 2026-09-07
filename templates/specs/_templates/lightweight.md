<!--
For small changes only -- see specs/CONSTITUTION.md for when this is
appropriate versus the full product/requirements/design/validation
split. One file combining all four concerns at reduced depth.

Copy this file to specs/lightweight/<short-slug>.md (kebab-case,
descriptive, no number needed) and fill it in. Delete this comment
block and any section you genuinely have nothing to say for -- don't
leave placeholder text.

Write it before asking the agent to build the thing, not after. The
goal is that "implement specs/lightweight/<slug>.md" is a complete,
unambiguous instruction on its own, without needing the surrounding
chat context to fill gaps.
-->

# <short, specific title>

**Status:** draft | approved | implemented | abandoned

## Goal

One or two sentences: what should be true once this is done, and why it
matters. Not a feature list -- the underlying problem or outcome.

## Requirements

Numbered, each one independently checkable:

1. ...
2. ...
3. ...

## Non-goals

Explicitly out of scope for this spec -- things a reader might otherwise
assume are included. Prevents scope creep during implementation and
tells a future reader why something adjacent *wasn't* done.

## Acceptance criteria

How to verify this is actually done, concretely enough that "is this
finished?" isn't a judgment call. Use this repo's own real test/lint
commands rather than "code looks right."

- [ ] ...
- [ ] ...
- [ ] Passes the quality gates in `specs/QUALITY_GATES.md` (lint,
      coverage, security scan) for every language this change touches
      -- not optional, part of "done" for every change.

## Open questions

Anything left unresolved that implementation will need to decide, or
that should come back to the user before/during the work. Delete this
section if there are none.
