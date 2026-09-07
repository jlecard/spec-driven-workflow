"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const os = require("os");

const init = require("../src/commands/init");

test("init scaffolds specs + both agent skill dirs for a new project", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sdw-test-"));
  try {
    await init({ dir, mode: "new", agents: "both", yes: true });

    assert.ok(fs.existsSync(path.join(dir, "specs", "CONSTITUTION.md")));
    assert.ok(fs.existsSync(path.join(dir, "specs", "QUALITY_GATES.md")));
    assert.ok(fs.existsSync(path.join(dir, "specs", ".spec-workflow.json")));
    assert.ok(
      fs.existsSync(path.join(dir, ".claude", "skills", "spec-driven-development", "SKILL.md"))
    );
    assert.ok(
      fs.existsSync(path.join(dir, ".github", "skills", "spec-driven-development", "SKILL.md"))
    );
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("init installs the quality-tooling-setup skill with both reference files bundled", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sdw-test-"));
  try {
    await init({ dir, mode: "existing", agents: "claude", yes: true });

    const skillDir = path.join(dir, ".claude", "skills", "spec-quality-tooling-setup");
    assert.ok(fs.existsSync(path.join(skillDir, "SKILL.md")));
    assert.ok(fs.existsSync(path.join(skillDir, "references", "language-tooling.md")));
    assert.ok(fs.existsSync(path.join(skillDir, "references", "mcp-servers.md")));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test("init installs the issue-tracking-setup skill with both system references bundled", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "sdw-test-"));
  try {
    await init({ dir, mode: "existing", agents: "claude", yes: true });

    const skillDir = path.join(dir, ".claude", "skills", "spec-issue-tracking-setup");
    assert.ok(fs.existsSync(path.join(skillDir, "SKILL.md")));
    assert.ok(
      fs.existsSync(path.join(skillDir, "references", "github", "scripts", "project_fields.py"))
    );
    assert.ok(
      fs.existsSync(path.join(skillDir, "references", "gitlab", "scripts", "gitlab_fields.py"))
    );
    assert.ok(!fs.existsSync(path.join(dir, ".github", "skills")));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
