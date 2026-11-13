// Structural checks only: these do not evaluate agent adherence.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry =>
    entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
}
const files = walk(root);
const skill = readFileSync(path.join(root, 'SKILL.md'), 'utf8');
assert.match(skill, /^---\nname: design-engineer\ndescription: >\n[\s\S]+?\n---\n/);
assert.equal(files.filter(file => path.basename(file) === 'SKILL.md').length, 1);
let links = 0;
const repositoryDocs = existsSync(path.join(root, '../install.sh')) ? [path.join(root, '../README.md')] : [];
for (const file of [...files.filter(file => file.endsWith('.md')), ...repositoryDocs]) {
  const source = readFileSync(file, 'utf8');
  for (const match of source.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
    const target = match[1];
    if (/^(https?:|#)/.test(target)) continue;
    const destination = path.resolve(path.dirname(file), target.split('#')[0]);
    assert.ok(existsSync(destination), `${file}: missing ${target}`);
    links++;
  }
}
const workflows = ['new-product', 'new-screen', 'refine-screen', 'design-system-change', 'audit', 'inspiration'];
for (const workflow of workflows) {
  assert.ok(skill.includes(`workflows/${workflow}.md`), `Unreachable route: ${workflow}`);
  const text = readFileSync(path.join(root, `workflows/${workflow}.md`), 'utf8');
  for (const label of ['Use when:', 'Inputs:', 'Complete when:', 'Recovery:']) assert.ok(text.includes(label), `${workflow}: ${label}`);
}
const cases = files.filter(file => file.includes(`${path.sep}cases${path.sep}`) && file.endsWith('.json'));
assert.equal(cases.length, 10);
const ids = new Set();
for (const file of cases) {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  assert.equal(typeof data.id, 'string');
  assert.ok(!ids.has(data.id)); ids.add(data.id);
  for (const key of ['initial_conditions', 'user_request']) assert.ok(typeof data[key] === 'string' && data[key].length);
  for (const key of ['workflows', 'expected_decisions', 'mandatory_invariants', 'observable_success', 'failure_conditions', 'evidence_required']) {
    assert.ok(Array.isArray(data[key]) && data[key].length && data[key].every(value => typeof value === 'string' && value.length), `${data.id}: ${key}`);
  }
  for (const workflow of data.workflows) assert.ok(workflows.includes(workflow), `${data.id}: unknown route`);
}
for (const file of files.filter(file => file.endsWith('.json') && !cases.includes(file))) JSON.parse(readFileSync(file, 'utf8'));
assert.ok(!existsSync(path.join(root, 'test-validation-result.json')), 'Obsolete result artifact');
console.log(`Package checks passed: 1 skill, ${workflows.length} routes, ${cases.length} cases, ${links} local links.`);
