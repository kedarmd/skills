import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { verifyLayout } from '../bin/verify-layout.mjs';

const read = file => JSON.parse(readFileSync(new URL(`../examples/${file}`, import.meta.url)));
const base = () => ({ system: read('approved-system.json'), scene: read('valid-scene.json') });
const rules = result => result.errors.map(error => error.rule);

test('valid sample has no measurable violations (visual still unverified)', () => {
  const { system, scene } = base();
  const result = verifyLayout(system, scene);
  assert.equal(result.errors.length, 0);
  assert.equal(result.verdict, 'PARTIAL');
  assert.ok(result.unverifiable.some(issue => issue.area === 'visual'));
});

test('detect wrong stack gap', () => {
  const { system, scene } = base();
  scene.nodes[2].y += 5;
  assert.ok(rules(verifyLayout(system, scene)).includes('GAP'));
});

test('detect incorrect leading padding', () => {
  const { system, scene } = base();
  scene.nodes[1].y += 3;
  assert.ok(rules(verifyLayout(system, scene)).includes('LEADING_PADDING'));
});

test('detect overflow outside viewport or parent', () => {
  const { system, scene } = base();
  scene.nodes[2].width = 500;
  assert.ok(rules(verifyLayout(system, scene)).includes('OVERFLOW'));
});

test('detect detached instance and unapproved override', () => {
  const { system, scene } = base();
  scene.nodes[2].component.detached = true;
  scene.nodes[2].overrides.push('cornerRadius');
  const result = rules(verifyLayout(system, scene));
  assert.ok(result.includes('DETACHED'));
  assert.ok(result.includes('OVERRIDE'));
});

test('detect mismatched actual token value', () => {
  const { system, scene } = base();
  scene.nodes[2].resolvedStyles.fill = '#ff0000';
  assert.ok(rules(verifyLayout(system, scene)).includes('TOKEN_VALUE'));
});

test('detect semantic component style mismatch', () => {
  const { system, scene } = base();
  scene.nodes[2].styles.fill = 'color.background';
  const result = rules(verifyLayout(system, scene));
  assert.ok(result.includes('COMPONENT_STYLE'));
});

test('detect alignment-group drift', () => {
  const { system, scene } = base();
  scene.nodes[2].x = 26;
  assert.ok(rules(verifyLayout(system, scene)).includes('PEER_ALIGNMENT'));
});

test('unavailable geometry is disclosed, never falsely passed', () => {
  const { system, scene } = base();
  scene.evidence.geometry = false;
  const result = verifyLayout(system, scene);
  assert.equal(result.verdict, 'PARTIAL');
  assert.ok(result.unverifiable.some(issue => issue.area === 'geometry'));
});

test('unapproved registry blocks screen verification', () => {
  const { system, scene } = base();
  system.approval.status = 'draft';
  assert.ok(rules(verifyLayout(system, scene)).includes('APPROVAL'));
});

test('detect overlap without explicit exception', () => {
  const { system, scene } = base();
  scene.nodes[2].y = 40;
  assert.ok(rules(verifyLayout(system, scene)).includes('OVERLAP'));
});

test('stack respects trailing content padding on both axes', () => {
  for (const axis of ['y', 'x']) {
    const { system, scene } = base();
    scene.nodes[0].height = 115;
    if (axis === 'x') {
      for (const node of scene.nodes) {
        [node.x, node.y] = [node.y, node.x];
        [node.width, node.height] = [node.height, node.width];
        delete node.component;
      }
      scene.nodes[0].layout.axis = 'x';
      [scene.canvas.width, scene.canvas.height] = [scene.canvas.height, scene.canvas.width];
      scene.alignmentGroups = [];
    }
    assert.ok(rules(verifyLayout(system, scene)).includes('CONTENT_BOUNDS'));
  }
});

test('stack permits spare space and explicit overflow exceptions', () => {
  const { system, scene } = base();
  assert.ok(!rules(verifyLayout(system, scene)).includes('CONTENT_BOUNDS'));
  scene.nodes[0].height = 115;
  scene.nodes[2].allowOverflow = true;
  assert.ok(!rules(verifyLayout(system, scene)).includes('CONTENT_BOUNDS'));
});
