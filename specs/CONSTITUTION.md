# Specs constitution

How specs work in this repo. Read this once; individual specs shouldn't
need to repeat it.

## Structure: grouped by concern, not by feature

```text
specs/
  CONSTITUTION.md
  .spec-workflow.json                # written by the CLI, records setup choices
  product/
    <slug>.md                        # normally just one, the whole product
  requirements/
    initial_requirements.md          # current baseline, amended in place
    <slug>.md                        # new capabilities, one file each
  design/
    initial_design.md
    <slug>.md
  validation/
    initial_validation.md
    <slug>.md
  lightweight/
    <slug>.md                        # small changes -- see below
  _templates/
    product.md
    requirements.md
    design.md
    validation.md
    lightweight.md
```

Each type has its own folder. Within a type, there's one **baseline**
document (`initial_*.md`) representing the app as it currently exists,
plus **delta** documents for capabilities added since -- one file per
capability, not one per feature-times-four-folders bundle.

On a brand-new project the baseline starts empty and gets filled in
through an interview (see the `spec-new-project` skill). On an existing
codebase with no specs yet, the baseline is reconstructed from the code
itself (see the `spec-discovery` skill) rather than invented from
scratch.

## The four spec types

1. **`product/`** -- the *why*. There is normally **one** product spec
   for the whole app -- it changes rarely, only when the actual product
   vision shifts (new user segment, a fundamentally different problem
   being solved). A new feature's rationale is a sentence or two at the
   top of its `requirements/` file, not a new product doc.
2. **`requirements/`** -- the *what*. Numbered, testable functional
   requirements. `initial_requirements.md` is the living baseline;
   amend it in place for small corrections to already-documented
   behavior. When a new capability doesn't fit into it, add
   `requirements/<slug>.md` instead of bloating the baseline
   indefinitely.
3. **`design/`** -- the *how*. Depends on the matching requirements file
   being approved. `design/<slug>.md` uses the **same slug** as
   `requirements/<slug>.md` -- that shared filename is what links them;
   there's no separate cross-reference mechanism.
4. **`validation/`** -- the *how do we know*. Same slug-matching rule.
   Acceptance criteria map 1:1 to the requirements file's numbered
   list.

Templates for all four (plus `lightweight.md`) are in
`specs/_templates/`. Copy the template, don't start from a blank file.

## Slugs, not numbers

Files are named by descriptive kebab-case slug (`new-button-cross.md`),
not a sequence number -- the type folder plus filename is enough to
find things; a shared incrementing counter across four folders doesn't
add anything. Pick a slug specific enough that it won't collide with a
future unrelated feature.

## When to use the full four-type split vs. `lightweight/`

Use the full split (new files in `requirements/`, `design/`,
`validation/`, all sharing a slug) for anything that changes behavior a
user or API consumer would notice, spans more than one major layer of
the codebase (e.g. both a backend and a frontend, or a service and its
data model), or where getting the requirements wrong would be expensive
to unwind (auth, a public contract, anything touching money or data
integrity).

For small, contained changes -- a copy tweak, a new field on an
already-editable record, a CSS fix -- use
`specs/_templates/lightweight.md` instead: one file at
`specs/lightweight/<slug>.md`, all four concerns folded into
Goal / Requirements / Non-goals / Acceptance criteria at reduced depth.

If you're not sure which to use, default to lightweight and split it
out into the full structure later if it turns out bigger than
expected -- that's cheaper than over-specifying something that didn't
need it.

## Status and dependency order

- Each document has its own `Status`: `draft` -> `approved` ->
  (`requirements`/`design`: stays `approved` once implemented;
  `validation`: -> `verified`). A document can also end at `abandoned`
  -- leave it in place with that status rather than deleting it; it's a
  record of a decision not to do something.
- Don't write a `design/<slug>.md` against a `requirements/<slug>.md`
  still marked `draft`. This is what keeps a spec from drifting into
  "we designed the solution and then wrote requirements to match it."
- When asked to "implement `<type>/<slug>.md`", treat the full set of
  matching-slug documents across `requirements/`/`design/`/`validation/`
  as the complete, authoritative requirements. Implement exactly what
  they say. Flag ambiguity rather than guessing. Don't expand scope
  without checking first.

## Verification

`validation/` files' test plans should point at whatever this
repo's own real verification tooling is (its test runner, lint/type
checks, a manual smoke-test script) -- discover and name the actual
commands (e.g. from `package.json` scripts, a `Makefile`, or CI
workflow files) rather than inventing generic steps like "test
thoroughly." If a spec needs a new kind of check that doesn't exist
yet, adding it is part of that spec's implementation, not a separate
task.

## Quality gates

`specs/QUALITY_GATES.md` is the authoritative source for this
project's lint/format, coverage, security-scanning, and unit-test
commands, per language -- run `spec-quality-tooling-setup` to fill it
in (and to get recommendations for missing tooling and relevant MCP
servers). Every `validation/`/`lightweight` spec's acceptance criteria
must include these gates passing, not just the spec's own
requirement-specific tests -- a requirement isn't done if it breaks
lint, drops coverage, or fails a security scan, even when its own
functional test passes. `spec-driven-implementation` enforces this at
verification time; see that skill for the exact mechanics.

## Optional: tracking specs as issues

Not yet configured. Run the `spec-issue-tracking-setup` skill to pick
an issue tracker (GitHub, GitLab, or none) and generate a
project-specific `spec-issue-tracking` skill for it -- once that's
done, this section is rewritten to say which system is in use and
where to find the details. Specs are fully usable as plain files
without this; it's purely optional automation.
