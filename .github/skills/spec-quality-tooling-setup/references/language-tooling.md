# Language quality tooling -- reference

A menu of common, well-established tools per category, per language.
Use this to spot gaps (Step 2/3 of `spec-quality-tooling-setup`), not as
a mandatory checklist -- a project already using an equivalent tool
doesn't need to switch. Versions/exact package names drift; confirm the
current recommended install command for the tool actually chosen rather
than trusting this file to stay current forever.

## JavaScript / TypeScript

| Category | Common tool | Install |
|---|---|---|
| Lint/format | ESLint + Prettier (or Biome as a single faster replacement for both) | `npm install -D eslint prettier` or `npm install -D @biomejs/biome` |
| Coverage | Built into Vitest/Jest (`--coverage`), or `c8`/`nyc` for other runners | `npm install -D @vitest/coverage-v8` (if using Vitest) |
| Security scanning | `npm audit` (dependency CVEs, built in), Semgrep for SAST, Snyk | `npm audit`; `pip install semgrep` (Semgrep's CLI, language-agnostic) |
| Unit testing | Vitest or Jest | `npm install -D vitest` |
| Clean code / complexity | ESLint's own complexity rules, or SonarLint/SonarQube for deeper metrics | ESLint config: `"complexity": ["warn", 10]`; SonarLint is an editor extension, SonarQube/SonarCloud is a server |

## Python

| Category | Common tool | Install |
|---|---|---|
| Lint/format | Ruff (lint + format in one, fast) | `pip install ruff` |
| Coverage | `coverage.py` via `pytest-cov` | `pip install pytest-cov` |
| Security scanning | `pip-audit` (dependency CVEs), Bandit (SAST for common Python pitfalls), Semgrep | `pip install pip-audit bandit` |
| Unit testing | pytest | `pip install pytest` |
| Clean code / complexity | Ruff's own complexity rules (`C901`), or `radon` for cyclomatic complexity reports | `pip install radon` |
| Type checking (often paired with lint) | mypy or basedpyright/pyright | `pip install mypy` |

## Go

| Category | Common tool | Install |
|---|---|---|
| Lint/format | `golangci-lint` (aggregates many linters) + `gofmt`/`goimports` | `go install github.com/golangci-lint/cmd/golangci-lint@latest` |
| Coverage | Built in: `go test -cover` / `go test -coverprofile=cover.out` | (no install needed) |
| Security scanning | `govulncheck` (official, dependency + stdlib vulnerabilities) | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| Unit testing | Built-in `testing` package via `go test ./...` | (no install needed) |
| Clean code / complexity | `gocyclo`, or `golangci-lint`'s `gocognit`/`cyclop` linters | `go install github.com/fzipp/gocyclo/cmd/gocyclo@latest` |

## Rust

| Category | Common tool | Install |
|---|---|---|
| Lint/format | `clippy` + `rustfmt` (both official, usually already present via rustup) | `rustup component add clippy rustfmt` |
| Coverage | `cargo-tarpaulin` or `cargo-llvm-cov` | `cargo install cargo-tarpaulin` |
| Security scanning | `cargo audit` (RustSec advisory database) | `cargo install cargo-audit` |
| Unit testing | Built-in: `cargo test` | (no install needed) |
| Clean code / complexity | `clippy`'s own complexity/cognitive-complexity lints (`clippy::cognitive_complexity`) | (included with clippy) |

## Java / Kotlin

| Category | Common tool | Install |
|---|---|---|
| Lint/format | Checkstyle/Spotless (Java), ktlint (Kotlin) | Gradle/Maven plugin -- see build tool docs |
| Coverage | JaCoCo | Gradle/Maven plugin |
| Security scanning | OWASP Dependency-Check, Snyk | Gradle/Maven plugin, or `snyk test` |
| Unit testing | JUnit 5 (Java), Kotest/JUnit (Kotlin) | Build tool dependency |
| Clean code / complexity | SonarQube/SonarLint, PMD | SonarLint is an editor extension; PMD via build plugin |

## C# / .NET

| Category | Common tool | Install |
|---|---|---|
| Lint/format | `dotnet format` (built in) + Roslyn analyzers | (built in); analyzers via NuGet |
| Coverage | Coverlet | `dotnet add package coverlet.collector` |
| Security scanning | `dotnet list package --vulnerable` (built in, .NET 6+), Snyk | (built in) |
| Unit testing | xUnit or NUnit | `dotnet add package xunit` |
| Clean code / complexity | SonarQube/SonarLint, Roslyn's own maintainability analyzers | SonarLint editor extension |

## Ruby

| Category | Common tool | Install |
|---|---|---|
| Lint/format | RuboCop | `gem install rubocop` |
| Coverage | SimpleCov | `gem install simplecov` |
| Security scanning | `bundler-audit`, Brakeman (Rails-specific SAST) | `gem install bundler-audit brakeman` |
| Unit testing | RSpec or Minitest | `gem install rspec` |
| Clean code / complexity | RuboCop's own complexity cops (`Metrics/CyclomaticComplexity`, `Metrics/PerceivedComplexity`) | (included with RuboCop) |

## Any language not listed here

- Ask what the ecosystem's own de facto standard tools are rather than
  guessing -- most languages have one clearly dominant linter/formatter
  and test framework the community has converged on.
- Semgrep and Trivy are both genuinely language-agnostic and worth
  considering for security scanning regardless of language (Semgrep for
  SAST pattern rules, Trivy for dependency/container/IaC vulnerability
  scanning).
- SonarQube/SonarCloud support most mainstream languages under one
  server for the "clean code / complexity" category, if the project
  wants one tool across a polyglot codebase rather than a
  language-specific one per language.

## Ready-made clean-code / refactoring skills (language-agnostic)

Beyond static-analysis *tools*, the "clean code / complexity" category
also has ready-made **agent skills** worth offering alongside (or
instead of) a linter plugin -- these teach the agent judgment
(cognitive load, responsibility boundaries, safe refactoring steps)
that a linter's fixed rule set can't express:

- **[ciembor/agent-rules-books](https://github.com/ciembor/agent-rules-books)**
  (MIT) -- rule sets distilled from *Clean Code*, *Refactoring*
  (Fowler), *Refactoring.Guru*'s smell catalog, *A Philosophy of
  Software Design* (deep modules, cognitive load -- the closest direct
  match to "clean code, best practices, cognitive load"), *Working
  Effectively with Legacy Code*, *Clean Architecture*, and others. Each
  ships in `nano`/`mini`/`full` sizes; plain Markdown, explicitly built
  for Claude Code/Cursor/Codex and adaptable to Copilot. Recommend the
  `mini` size for most projects -- fold the relevant book(s) into a
  project-specific skill via `spec-skill-builder` rather than copying
  the repo's files in wholesale, so it picks up this project's own
  naming/idioms instead of generic examples.
- **[anthropics/skills](https://github.com/anthropics/skills)**'s
  `skill-creator` -- not clean-code content itself, but the official
  reference for the `SKILL.md` format `spec-skill-builder` already
  follows; worth pointing to if the user wants to see Anthropic's own
  authoring conventions directly.

Offer these as optional, not mandatory -- a project with strong
existing conventions and a good linter may not need a books-derived
skill on top; ask before adding one, same as any other recommendation
in this file.
