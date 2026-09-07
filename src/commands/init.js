"use strict";

const fs = require("fs");
const path = require("path");

const { select, ask } = require("../lib/prompt");
const { copyDir, writeFile, ensureDir, replacePathPrefixInTree } = require("../lib/fsUtils");
const { detectMode, alreadyInitialized } = require("../lib/detect");

const TEMPLATES_DIR = path.join(__dirname, "..", "..", "templates");
const ALL_SKILLS = [
  "spec-location-setup",
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

  // Where specs live: a folder in this repo (single repo or monorepo -- same
  // answer either way, just a directory name), or a separate, dedicated repo
  // for a multi-repo/polyrepo workspace. The latter needs `gh`/git judgment
  // calls (existing vs. new repo, submodule wiring) better done by the agent
  // in-chat -- see the spec-location-setup skill -- so this only collects the
  // simple in-repo case here and defers the rest.
  let specsLocation = args["specs-location"];
  let specsDir = args["specs-dir"];
  if (!specsLocation) {
    if (nonInteractive) {
      specsLocation = "in-repo";
    } else {
      specsLocation = await select(
        "Where should specs live? in-repo (a folder here) or external (a separate, dedicated repo)?",
        ["in-repo", "external"],
        "in-repo"
      );
    }
  }
  if (specsLocation === "in-repo" && !specsDir) {
    if (nonInteractive) {
      specsDir = "specs";
    } else {
      const answer = await ask('What should the specs directory be called? (default "specs"): ');
      specsDir = answer || "specs";
    }
  }

  return {
    dir,
    mode,
    agents,
    specsLocation,
    specsDir: specsLocation === "in-repo" ? specsDir : null,
    force: Boolean(args.force),
  };
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

function scaffoldSpecsFolders(dir, specsDir, force, log) {
  const specsPath = path.join(dir, specsDir);
  copyDir(path.join(TEMPLATES_DIR, "specs"), specsPath, { force, log });

  for (const type of ["product", "requirements", "design", "validation", "lightweight"]) {
    ensureDir(path.join(specsPath, type));
  }
}

function writeConfig(dir, options, log) {
  const configPath = path.join(dir, ".spec-workflow.json");
  const config = {
    version: 1,
    mode: options.mode,
    agents: options.agents,
    specsLocation: options.specsLocation,
    specsDir: options.specsDir,
    createdAt: new Date().toISOString(),
  };
  writeFile(configPath, JSON.stringify(config, null, 2) + "\n", { force: true, log });
}

async function init(args) {
  const options = await resolveOptions(args);
  const { dir, mode, agents, specsLocation, specsDir, force } = options;

  if (alreadyInitialized(dir) && !force) {
    process.stdout.write(
      `.spec-workflow.json already exists in ${dir} -- re-run with --force to overwrite files.\n`
    );
  }

  const log = [];
  const targetDirs = skillTargetDirs(dir, agents);
  for (const skillName of ALL_SKILLS) {
    installSkill(skillName, targetDirs, force, log);
  }

  if (specsLocation === "in-repo") {
    scaffoldSpecsFolders(dir, specsDir, force, log);
    if (specsDir !== "specs") {
      // Retarget every "specs/..." reference in the skills + specs templates
      // we just installed to the custom folder name -- see fsUtils' own docs.
      for (const targetRoot of targetDirs) replacePathPrefixInTree(targetRoot, "specs", specsDir);
      replacePathPrefixInTree(path.join(dir, specsDir), "specs", specsDir);
    }
  }
  // specsLocation === "external": nothing scaffolded locally yet -- the
  // spec-location-setup skill picks an existing/new dedicated repo, mounts
  // it as a submodule, and does this same retargeting once that path is known.

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
  process.stdout.write("Mode: " + mode + "\n");
  process.stdout.write(
    "Specs location: " +
      (specsLocation === "in-repo" ? `${specsDir}/ (this repo)` : "external (not yet configured)") +
      "\n\n"
  );

  if (specsLocation === "external") {
    process.stdout.write(
      "Next step: open this project in Claude or GitHub Copilot Chat and say\n" +
        '  "set up the specs repository"\n' +
        "to run the spec-location-setup skill -- it picks an existing or new dedicated\n" +
        "GitHub repo, mounts it as a submodule, and finishes wiring every skill to it.\n" +
        "Run spec-new-project/spec-discovery after that, once specs/ actually exists.\n"
    );
    return;
  }

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
      `in ${specsDir}/QUALITY_GATES.md so every spec and spec-driven-implementation enforce them.\n`
  );
}

module.exports = init;
