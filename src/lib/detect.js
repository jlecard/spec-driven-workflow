"use strict";

const fs = require("fs");
const path = require("path");

/**
 * Heuristically decides whether `dir` looks like a brand-new project or an
 * existing codebase, so init can default the new-vs-existing prompt sensibly.
 */
function detectMode(dir) {
  if (fs.existsSync(path.join(dir, "specs", "requirements", "initial_requirements.md"))) {
    return "existing"; // already has a baseline spec -- treat as an existing spec-driven project
  }

  const signals = [
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "requirements.txt",
    "src",
    "app",
    "api",
  ];
  const hasSignal = signals.some((name) => fs.existsSync(path.join(dir, name)));
  const hasGit = fs.existsSync(path.join(dir, ".git"));

  return hasSignal || hasGit ? "existing" : "new";
}

function alreadyInitialized(dir) {
  return fs.existsSync(path.join(dir, ".spec-workflow.json"));
}

module.exports = { detectMode, alreadyInitialized };
