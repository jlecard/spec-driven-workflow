"use strict";

const fs = require("fs");
const path = require("path");

const { select } = require("../lib/prompt");
const { copyDir, writeFile, ensureDir } = require("../lib/fsUtils");
const { detectMode, alreadyInitialized } = require("../lib/detect");

const TEMPLATES_DIR = path.join(__dirname, "..", "..", "templates");
const ALL_SKILLS = [
  "spec-driven-development",
  "spec-driven-implementation",
  "spec-new-project",
  "spec-discovery",
  "spec-project-customization",
  "spec-skill-builder",
  "spec-issue-tracking-setup",
  "spec-quality-tooling-setup",
];

function parseAgents(raw) {
  if (!raw) return ["claude", "copilot"];
  const tokens = String(raw)
    .split(",")
    .map((a) => a.trim().toLowerCase())
    .filter(Boolean);
  if (tokens.includes("both")) return ["claude", "copilot"];
  return tokens;
}

async function resolveOptions(args) {
  const dir = path.resolve(args.dir || process.cwd());
  const nonInteractive = Boolean(args.yes);

  let mode = args.mode;
  if (!mode) {
    const detected = detectMode(dir);
    mode = nonInteractive
      ? detected
      : await select(
          `Is this a new project or an existing codebase? (detected: ${detected})`,
          ["new", "existing"],
          detected
        );
  }

  let agents = args.agents ? parseAgents(args.agents) : null;
  if (!agents) {
    if (nonInteractive) {
      agents = ["claude", "copilot"];
    } else {
      const answer = await select(
        "Which agent(s) should get skill files installed?",
        ["both", "claude", "copilot"],
        "both"
      );
      agents = answer === "both" ? ["claude", "copilot"] : [answer];
    }
  }

  return { dir, mode, agents, force: Boolean(args.force) };
}

function skillTargetDirs(dir, agents) {
  const dirs = [];
  if (agents.includes("claude")) dirs.push(path.join(dir, ".claude", "skills"));
  if (agents.includes("copilot")) dirs.push(path.join(dir, ".github", "skills"));
  return dirs;
}

function installSkill(skillName, targetDirs, force, log) {
  const src = path.join(TEMPLATES_DIR, "skills", skillName);
  for (const targetRoot of targetDirs) {
    copyDir(src, path.join(targetRoot, skillName), { force, log });
  }
}

function scaffoldSpecsFolders(dir, mode, force, log) {
  const specsDir = path.join(dir, "specs");
  copyDir(path.join(TEMPLATES_DIR, "specs"), specsDir, { force, log });

  for (const type of ["product", "requirements", "design", "validation", "lightweight"]) {
    ensureDir(path.join(specsDir, type));
  }

  if (mode === "new") {
    // A brand-new project starts with no baseline at all -- spec-new-project
    // creates it through an interview. Nothing else to seed here.
    return;
  }
}

function writeConfig(dir, options, log) {
  const configPath = path.join(dir, "specs", ".spec-workflow.json");
  const config = {
    version: 1,
    mode: options.mode,
    agents: options.agents,
    createdAt: new Date().toISOString(),
  };
  writeFile(configPath, JSON.stringify(config, null, 2) + "\n", { force: true, log });
}

async function init(args) {
  const options = await resolveOptions(args);
  const { dir, mode, agents, force } = options;

  if (alreadyInitialized(dir) && !force) {
    process.stdout.write(
      `specs/.spec-workflow.json already exists in ${dir} -- re-run with --force to overwrite files.\n`
    );
  }

  const log = [];
  scaffoldSpecsFolders(dir, mode, force, log);

  const targetDirs = skillTargetDirs(dir, agents);
  for (const skillName of ALL_SKILLS) {
    installSkill(skillName, targetDirs, force, log);
  }

  writeConfig(dir, options, log);

  const created = log.filter((l) => l.action === "created").length;
  const skipped = log.filter((l) => l.action.startsWith("skipped")).length;
  const overwritten = log.filter((l) => l.action === "overwritten").length;

  process.stdout.write(
    `\nspec-driven-workflow: ${created} file(s) created` +
      (overwritten ? `, ${overwritten} overwritten` : "") +
      (skipped ? `, ${skipped} skipped (already existed)` : "") +
      ` in ${dir}\n\n`
  );

  process.stdout.write("Agents enabled: " + agents.join(", ") + "\n");
  process.stdout.write("Mode: " + mode + "\n\n");

  if (mode === "new") {
    process.stdout.write(
      "Next step: open this project in Claude or GitHub Copilot Chat and say\n" +
        '  "let\'s start this project"\n' +
        "to run the spec-new-project skill and draft your first product spec + baseline requirements.\n"
    );
  } else {
    process.stdout.write(
      "Next step: open this project in Claude or GitHub Copilot Chat and say\n" +
        '  "discover specs for this codebase"\n' +
        "to run the spec-discovery skill and reconstruct a baseline from the existing code.\n"
    );
  }
  process.stdout.write(
    "\nThen: say \"customize the spec workflow for this project\" to run\n" +
      "spec-project-customization -- it surveys what's already there and\n" +
      "recommends project-specific skills (built via spec-skill-builder) worth adding.\n" +
      "Say \"set up issue tracking\" to run spec-issue-tracking-setup and wire specs up to\n" +
      "GitHub or GitLab issues, if this project uses either.\n" +
      "Say \"set up quality tooling\" to run spec-quality-tooling-setup -- it recommends\n" +
      "lint/coverage/security/testing tools and MCP servers, and records the agreed gates\n" +
      "in specs/QUALITY_GATES.md so every spec and spec-driven-implementation enforce them.\n"
  );
}

module.exports = init;
