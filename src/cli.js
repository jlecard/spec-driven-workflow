"use strict";

const init = require("./commands/init");

const USAGE = `spec-driven-workflow <command> [options]

Commands:
  init          Scaffold specs/ and agent skills into a project (default)
  help          Show this message

Options for "init":
  --dir <path>            Target project directory (default: current directory)
  --mode <new|existing>   Skip auto-detection of new vs. existing project
  --agents <list>         Comma-separated: claude,copilot (default: both)
  --yes, -y               Non-interactive: accept defaults / detected values
  --force                 Overwrite files that already exist

Examples:
  npx spec-driven-workflow init
  npx spec-driven-workflow init --agents=copilot --mode=existing
  npx spec-driven-workflow init --yes
`;

function parseArgs(argv) {
  const args = { _: [] };
  for (const raw of argv) {
    if (raw === "-y") {
      args.yes = true;
      continue;
    }
    if (!raw.startsWith("--")) {
      args._.push(raw);
      continue;
    }
    const eq = raw.indexOf("=");
    if (eq === -1) {
      args[raw.slice(2)] = true;
    } else {
      args[raw.slice(2, eq)] = raw.slice(eq + 1);
    }
  }
  return args;
}

async function run(argv) {
  const args = parseArgs(argv);
  const command = args._[0] || "init";

  switch (command) {
    case "init":
      await init(args);
      return;
    case "help":
    case "--help":
    case "-h":
      process.stdout.write(USAGE);
      return;
    default:
      process.stderr.write(`Unknown command: ${command}\n\n${USAGE}`);
      process.exitCode = 1;
  }
}

module.exports = { run, parseArgs, USAGE };
