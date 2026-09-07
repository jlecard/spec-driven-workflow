"use strict";

const readline = require("readline");

/** Prompts the user with a question and a set of accepted-shorthand choices. */
function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function select(question, choices, defaultChoice) {
  const label = choices.map((c) => (c === defaultChoice ? `[${c}]` : c)).join(" / ");
  const answer = await ask(`${question} (${label}): `);
  if (!answer) return defaultChoice;
  const match = choices.find((c) => c.toLowerCase().startsWith(answer.toLowerCase()));
  return match || defaultChoice;
}

async function confirm(question, defaultValue) {
  const suffix = defaultValue ? "Y/n" : "y/N";
  const answer = (await ask(`${question} (${suffix}): `)).toLowerCase();
  if (!answer) return defaultValue;
  return answer.startsWith("y");
}

module.exports = { ask, select, confirm };
