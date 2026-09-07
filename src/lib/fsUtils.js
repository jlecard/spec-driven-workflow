"use strict";

const fs = require("fs");
const path = require("path");

/** Recursively copies a directory. Existing files are skipped unless force=true. */
function copyDir(srcDir, destDir, { force = false, log = [] } = {}) {
  fs.mkdirSync(destDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath, { force, log });
    } else {
      writeFile(destPath, fs.readFileSync(srcPath, "utf8"), { force, log });
    }
  }
  return log;
}

function writeFile(destPath, content, { force = false, log = [] } = {}) {
  const exists = fs.existsSync(destPath);
  if (exists && !force) {
    log.push({ path: destPath, action: "skipped (already exists)" });
    return log;
  }
  fs.mkdirSync(path.dirname(destPath), { recursive: true });
  fs.writeFileSync(destPath, content, "utf8");
  log.push({ path: destPath, action: exists ? "overwritten" : "created" });
  return log;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

/**
 * Rewrites every text file under `rootDir` (recursively), replacing
 * whole-path-segment occurrences of `oldName/` with `newName/` -- used to
 * retarget every "specs/..." reference in installed skills/templates when
 * the user picks a non-default specs directory name.
 */
function replacePathPrefixInTree(rootDir, oldName, newName) {
  if (oldName === newName) return;
  const pattern = new RegExp(`\\b${oldName}/`, "g");
  const replacement = `${newName}/`;
  for (const entry of fs.readdirSync(rootDir, { withFileTypes: true })) {
    const entryPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      replacePathPrefixInTree(entryPath, oldName, newName);
      continue;
    }
    if (!/\.(md|json|py)$/.test(entry.name)) continue;
    const content = fs.readFileSync(entryPath, "utf8");
    const updated = content.replace(pattern, replacement);
    if (updated !== content) fs.writeFileSync(entryPath, updated, "utf8");
  }
}

module.exports = { copyDir, writeFile, ensureDir, replacePathPrefixInTree };
