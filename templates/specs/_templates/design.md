<!--
The "how." Depends on the matching requirements/ file being approved.
This is where implementation actually starts from -- specific enough
that "implement design/<slug>.md" doesn't require re-deciding
architecture along the way, but without repeating the requirements
file's content.

For a correction to the current baseline architecture: amend
specs/design/initial_design.md in place. For a new capability with its
own requirements/<slug>.md: copy this file to specs/design/<slug>.md
using the *same slug* as the requirements file it implements.
-->

# <feature name> — Design

**Depends on:** `requirements/<slug>.md`
**Status:** draft | approved

## Approach

The chosen technical approach, in enough detail to start from. Name
specific files/functions that get touched or added. If there was a real
alternative considered and rejected, say so in one sentence and why --
don't write a survey of options nobody's taking.

## Data / API changes

Only if applicable -- delete if this is UI-only with no contract
changes. Spell out the exact new/changed shape of whatever contract
(API endpoint, schema, file format) this touches.

## Key files

- `path/to/file.ts` -- what changes and why

## Risks / open technical questions

Delete if none. Things that could make the chosen approach wrong, or
decisions still needed before/during implementation.
