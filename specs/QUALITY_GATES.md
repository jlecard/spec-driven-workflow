# Quality gates

**Not yet configured.** Run the `spec-quality-tooling-setup` skill to
discover this project's language(s), recommend lint/coverage/security/
testing tools and relevant MCP servers, and record the agreed commands
here.

Once configured, this file lists -- per language actually used in this
project -- the exact lint/format, coverage, security-scanning, and unit
test commands, plus any MCP servers set up to support them. Every
`validation/`/`lightweight` spec's acceptance criteria, and
`spec-driven-implementation`'s own verification step, point at this
file rather than re-discovering or re-deciding commands each time.

This file is meant to be kept current by hand or by re-running
`spec-quality-tooling-setup` -- if a tool or command changes, update it
here so the rest of the workflow doesn't act on stale information.
