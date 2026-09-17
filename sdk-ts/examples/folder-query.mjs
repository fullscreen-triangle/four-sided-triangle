// Manual integration smoke test (see plan §Verification).
//
// Usage:
//   npm run build
//   node examples/folder-query.mjs <folder-to-search> "<query>"
//
// Points a LocalFileSource at a real folder of .md/.txt/.pdf files and asks
// a query. Confirms ask() returns a status — never a bare passage dump.

import { createIndividuator, LocalFileSource } from "../dist/index.js";

const [, , folder, ...queryParts] = process.argv;
const query = queryParts.join(" ");

if (!folder || !query) {
  console.error('Usage: node folder-query.mjs <folder> "<query>"');
  process.exit(1);
}

const assistant = createIndividuator({
  receiverId: "smoke-test",
  sources: [new LocalFileSource({ root: folder, extensions: [".md", ".txt", ".tex"] })],
});

const answer = await assistant.ask(query);

console.log(`status: ${answer.status}`);
if (answer.status === "grounded" || answer.status === "single-sourced" || answer.status === "two-sourced") {
  console.log(`claim: ${answer.claim.slice(0, 300)}`);
  console.log(`floor: ${answer.floor}`);
  if ("warning" in answer) console.log(`warning: ${answer.warning}`);
} else if (answer.status === "contested") {
  console.log(`warning: ${answer.warning}`);
  for (const c of answer.classes) console.log(`  - class ${c.key}: ${c.representative.slice(0, 150)}`);
} else {
  console.log(`reason: ${answer.reason}`);
}
