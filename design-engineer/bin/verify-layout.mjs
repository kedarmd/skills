#!/usr/bin/env node
/**
 * Design Engineer: standalone, dependency-free geometry and token verifier.
 * Written for this skill's own normalized evidence format. No legacy inputs.
 */
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const near = (a, b, tolerance) => Math.abs(a - b) <= tolerance;
const finite = value => typeof value === 'number' && Number.isFinite(value);
const isRecord = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const normalize = value => typeof value === 'string' && /^#[0-9a-f]{3,8}$/i.test(value)
  ? value.toLowerCase()
  : value;

export function verifyLayout(system, scene, tolerance = 0.5) {
  const errors = [];
  const warnings = [];
  const unverifiable = [];
  const fail = (rule, node, detail) => errors.push({ rule, node, detail });
  const missing = (area, detail) => unverifiable.push({ area, detail });
  if (!isRecord(system) || !isRecord(scene)) {
    fail('FORMAT', null, 'Both system and scene must be JSON objects.');
    return { verdict: 'FAIL', errors, warnings, unverifiable };
  }
  if (system.version !== 1 || scene.version !== 1) fail('VERSION', null, 'Unsupported contract or scene version.');
  if (system.approval?.status !== 'approved' || !system.approval?.reference) {
    fail('APPROVAL', null, 'An explicit approved system revision and decision reference are required.');
  }
  if (!system.revision || scene.systemRevision !== system.revision) {
    fail('SYSTEM_REVISION', null, 'Screen must name its currently approved system revision.');
  }
  const tokens = isRecord(system.tokens) ? system.tokens : {};
  const components = isRecord(system.components) ? system.components : {};
  const evidence = isRecord(scene.evidence) ? scene.evidence : {};
  if (!evidence.source || typeof evidence.source !== 'string') {
    fail('PROVENANCE', null, 'State exactly where and when live document measurements were read.');
  }
  for (const key of ['geometry', 'styles', 'componentLinkage', 'textMeasurement']) {
    if (evidence[key] !== true) missing(key, 'Design adapter did not confirm this read-back capability.');
  }
  missing('visual', 'Rendered hierarchy, optical balance and accessibility require separate visual inspection.');

  if (!Array.isArray(scene.nodes) || scene.nodes.length === 0) {
    fail('SCENE', null, 'Expected at least one measured node.');
    return { verdict: 'FAIL', errors, warnings, unverifiable };
  }
  const nodes = new Map();
  for (const node of scene.nodes) {
    if (!isRecord(node) || typeof node.id !== 'string' || !node.id) {
      fail('NODE_ID', null, 'Every node requires a unique nonempty id.');
      continue;
    }
    if (nodes.has(node.id)) fail('DUPLICATE_NODE', node.id, 'Duplicate node ID.');
    else nodes.set(node.id, node);
  }
  for (const node of nodes.values()) {
    if (node.parentId != null && !nodes.has(node.parentId)) {
      fail('PARENT', node.id, `Unknown parent ${node.parentId}.`);
    }
    const seen = new Set([node.id]);
    let cursor = node;
    while (cursor.parentId != null && nodes.has(cursor.parentId)) {
      if (seen.has(cursor.parentId)) {
        fail('CYCLE', node.id, 'Parent hierarchy contains a cycle.');
        break;
      }
      seen.add(cursor.parentId);
      cursor = nodes.get(cursor.parentId);
    }
  }

  const hasGeometry = evidence.geometry === true;
  const rectangleOk = node => [node.x, node.y, node.width, node.height].every(finite)
    && node.width > 0 && node.height > 0;
  if (hasGeometry) {
    const canvas = scene.canvas;
    if (!isRecord(canvas) || !finite(canvas.width) || !finite(canvas.height)
      || canvas.width <= 0 || canvas.height <= 0) fail('CANVAS', null, 'Invalid canvas dimensions.');
    for (const node of nodes.values()) {
      if (!rectangleOk(node)) {
        fail('BOUNDS', node.id, 'Invalid or missing live geometry.');
        continue;
      }
      const parent = node.parentId == null ? null : nodes.get(node.parentId);
      const r = parent && rectangleOk(parent) ? {
        x: parent.x, y: parent.y, width: parent.width, height: parent.height
      } : !parent && canvas?.width && canvas?.height ? {
        x: 0, y: 0, width: canvas.width, height: canvas.height
      } : null;
      if (r && !node.allowOverflow && (node.x < r.x - tolerance
        || node.y < r.y - tolerance || node.x + node.width > r.x + r.width + tolerance
        || node.y + node.height > r.y + r.height + tolerance)) {
        fail('OVERFLOW', node.id, 'Bounds extend outside the parent/canvas.');
      }
    }
    for (const parent of nodes.values()) {
      const siblings = [...nodes.values()].filter(n => n.parentId === parent.id && rectangleOk(n));
      for (let i = 0; i < siblings.length; i++) {
        for (let j = i + 1; j < siblings.length; j++) {
          const a = siblings[i], b = siblings[j];
          if (a.allowOverlap || b.allowOverlap) continue;
          const overlapWidth = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x);
          const overlapHeight = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
          if (overlapWidth > tolerance && overlapHeight > tolerance) {
            fail('OVERLAP', `${a.id},${b.id}`, 'Overlapping peer bounds without an explicit exception.');
          }
        }
      }
      if (parent.layout?.type !== 'stack') continue;
      if (!rectangleOk(parent)) continue;
      const { axis, children, padding, gap, crossAlign } = parent.layout;
      if (!['x', 'y'].includes(axis) || !Array.isArray(children)
        || !isRecord(padding) || !['start', 'end', 'center', 'stretch'].includes(crossAlign)
        || !finite(gap) || gap < 0 || ['top', 'bottom', 'left', 'right'].some(k => !finite(padding[k]) || padding[k] < 0)) {
        fail('STACK_CONTRACT', parent.id, 'Stack requires axis, ordered children, nonnegative padding and gap, and crossAlign.');
        continue;
      }
      const ids = siblings.map(n => n.id).sort();
      const specified = children.slice().sort();
      if (ids.join('\0') !== specified.join('\0')) {
        fail('STACK_CHILDREN', parent.id, 'Declared order must include every immediate child exactly once.');
        continue;
      }
      const ordered = children.map(id => nodes.get(id));
      if (!ordered.every(rectangleOk)) continue;
      const vertical = axis === 'y';
      const lead = vertical ? 'top' : 'left';
      const crossLead = vertical ? 'left' : 'top';
      const crossEnd = vertical ? 'right' : 'bottom';
      const mainPos = n => vertical ? n.y : n.x;
      const mainSize = n => vertical ? n.height : n.width;
      const crossPos = n => vertical ? n.x : n.y;
      const crossSize = n => vertical ? n.width : n.height;
      const mainStart = mainPos(parent) + padding[lead];
      const crossStart = crossPos(parent) + padding[crossLead];
      const crossAvailable = crossSize(parent) - padding[crossLead] - padding[crossEnd];
      if (ordered.length && !near(mainPos(ordered[0]), mainStart, tolerance)) {
        fail('LEADING_PADDING', ordered[0].id, `Expected leading ${lead} offset ${mainStart}.`);
      }
      for (let i = 0; i < ordered.length; i++) {
        const child = ordered[i];
        if (i > 0) {
          const previous = ordered[i - 1];
          const actualGap = mainPos(child) - (mainPos(previous) + mainSize(previous));
          if (!near(actualGap, gap, tolerance)) {
            fail('GAP', child.id, `Expected ${gap}, measured ${actualGap}.`);
          }
        }
        if (crossAlign === 'start' || crossAlign === 'stretch') {
          if (!near(crossPos(child), crossStart, tolerance)) {
            fail('CROSS_ALIGNMENT', child.id, `Expected cross-axis start ${crossStart}.`);
          }
        } else if (crossAlign === 'end') {
          const desired = crossStart + crossAvailable - crossSize(child);
          if (!near(crossPos(child), desired, tolerance)) fail('CROSS_ALIGNMENT', child.id, `Expected cross-axis end ${desired}.`);
        } else {
          const desired = crossStart + (crossAvailable - crossSize(child)) / 2;
          if (!near(crossPos(child), desired, tolerance)) fail('CROSS_ALIGNMENT', child.id, `Expected cross-axis center ${desired}.`);
        }
        if (crossAlign === 'stretch' && !near(crossSize(child), crossAvailable, tolerance)) {
          fail('CROSS_STRETCH', child.id, `Expected cross size ${crossAvailable}, measured ${crossSize(child)}.`);
        }
      }
    }
    for (const group of scene.alignmentGroups ?? []) {
      if (!Array.isArray(group.nodeIds) || !group.nodeIds.every(id => nodes.has(id))) {
        fail('ALIGNMENT_GROUP', null, 'Alignment group references unknown nodes.');
        continue;
      }
      const projection = node => ({
        left: node.x, right: node.x + node.width,
        top: node.y, bottom: node.y + node.height,
        'center-x': node.x + node.width / 2,
        'center-y': node.y + node.height / 2
      })[group.axis];
      const members = group.nodeIds.map(id => nodes.get(id));
      if (!['left', 'right', 'top', 'bottom', 'center-x', 'center-y'].includes(group.axis)) {
        fail('ALIGNMENT_GROUP', null, 'Unknown alignment axis.');
      } else if (members.every(rectangleOk)) {
        const baseline = projection(members[0]);
        for (const member of members.slice(1)) {
          if (!near(projection(member), baseline, tolerance)) {
            fail('PEER_ALIGNMENT', member.id, `Not aligned at ${group.axis} with ${members[0].id}.`);
          }
        }
      }
    }
  }

  if (evidence.styles === true) {
    for (const node of nodes.values()) {
      for (const [property, tokenName] of Object.entries(node.styles ?? {})) {
        if (typeof tokenName !== 'string' || !Object.hasOwn(tokens, tokenName)) {
          fail('UNAPPROVED_TOKEN', node.id, `${property}: ${JSON.stringify(tokenName)} not registered.`);
          continue;
        }
        if (node.resolvedStyles && Object.hasOwn(node.resolvedStyles, property)
          && normalize(node.resolvedStyles[property]) !== normalize(tokens[tokenName])) {
          fail('TOKEN_VALUE', node.id, `${property}: actual value does not match ${tokenName}.`);
        }
        if (!node.resolvedStyles || !Object.hasOwn(node.resolvedStyles, property)) {
          missing('resolved-style', `Cannot verify actual ${property} value on ${node.id}.`);
        }
      }
      if (isRecord(node.rawStyles) && Object.keys(node.rawStyles).length) {
        fail('RAW_STYLE', node.id, 'Untracked local styling bypasses the approved token registry.');
      }
    }
  }
  if (evidence.componentLinkage === true) {
    for (const node of nodes.values()) {
      if (!node.component) continue;
      const component = components[node.component.name];
      if (!component) { fail('UNAPPROVED_COMPONENT', node.id, 'Component not registered in the approved system.'); continue; }
      if (!component.variants?.includes(node.component.variant)) fail('VARIANT', node.id, 'Variant is not approved.');
      if (node.component.detached !== false) fail('DETACHED', node.id, 'Instance must remain linked to its canonical definition.');
      if (hasGeometry && rectangleOk(node)) {
        if (finite(component.fixedHeight) && !near(node.height, component.fixedHeight, tolerance)) {
          fail('COMPONENT_HEIGHT', node.id, `Expected height ${component.fixedHeight}.`);
        }
        if (finite(component.minWidth) && node.width + tolerance < component.minWidth) {
          fail('COMPONENT_MIN_WIDTH', node.id, `Minimum width ${component.minWidth}.`);
        }
      }
      for (const [property, tokenName] of Object.entries(component.styles ?? {})) {
        if (evidence.styles === true && node.styles?.[property] !== tokenName) {
          fail('COMPONENT_STYLE', node.id, `${property} must use ${tokenName}.`);
        }
      }
      for (const override of node.overrides ?? []) {
        if (!component.permittedOverrides?.includes(override)) {
          fail('OVERRIDE', node.id, `Forbidden component override: ${override}.`);
        }
      }
    }
  }
  if (evidence.textMeasurement === true) {
    for (const node of nodes.values()) {
      if (node.textMetrics?.overflow === true) fail('TEXT_OVERFLOW', node.id, 'Measured text is clipped or unexpectedly truncated.');
    }
  }
  const verdict = errors.length ? 'FAIL' : unverifiable.length ? 'PARTIAL' : 'PASS';
  return { verdict, errors, warnings, unverifiable, checks: { nodeCount: nodes.size, tolerance } };
}

const ownPath = process.argv[1] ? path.resolve(process.argv[1]) : null;
if (ownPath && fileURLToPath(import.meta.url) === ownPath) {
  const [systemFile, sceneFile] = process.argv.slice(2);
  if (!systemFile || !sceneFile) {
    process.stderr.write('Usage: node bin/verify-layout.mjs system.json scene.json\n');
    process.exitCode = 2;
  } else {
    try {
      const result = verifyLayout(JSON.parse(readFileSync(systemFile, 'utf8')), JSON.parse(readFileSync(sceneFile, 'utf8')));
      process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
      if (result.errors.length) process.exitCode = 1;
    } catch (error) {
      process.stderr.write(`Cannot verify: ${error.message}\n`);
      process.exitCode = 2;
    }
  }
}
