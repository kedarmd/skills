# Implementation validation results

Results are recorded for the working-tree refactor of baseline c212d2e, using Node.js v24.22.1 on 2026-11-13. No live design-tool or comparative agent-performance PASS is claimed.

## Changes

Added six routed workflows, a construction reference, ten behavioral cases, a rubric/manual execution protocol, a structural validator, this report and the audit/invariant map. Reworked the entry point and skill README; updated the repository layout documentation and existing system/tool/evidence protocols. Retained change-control and inspiration policy, version-1 verifier inputs/CLI/exports, fixtures and installer. Removed the redundant sample result JSON. No dependencies added and no unrelated skill changes.

## Observed checks

- `node design-engineer/tests/verify-layout.test.mjs`: 13/13 tests passed after the fix. Before the fix, the newly added padding regression failed (12/13 passed), confirming the defect. Tests cover both axes, spare space and explicit overflow exceptions in addition to the original checks.
- `node design-engineer/tests/validate-package.mjs`: passed, one discoverable entry point, six workflow routes, ten complete case definitions and 56 existing local links in repository mode. The first run caught the results document before it was created; the final run passes. This is structural coverage, not behavioral scoring.
- Sample verifier CLI: exit 0, verdict PARTIAL, no numeric errors, visual inspection UNVERIFIABLE. This preserves prior semantics.
- CLI invocations with a five-unit gap violation, no arguments, malformed JSON and a missing file returned expected exits 1, 2, 2 and 2 respectively. Checks used temporary fixtures and asserted return codes.
- `bash install.sh --local --dir <temporary-directory>`: installed both existing top-level skills; all 32 design-engineer files copied byte-for-byte. Package checks also passed from the installed copy (54 local links; repository-only README checks excluded) to check standalone portability.
- `git diff --check`: passed. No unrelated skill files changed; no commit or push performed.

A direct numeric comparison used `git show HEAD:design-engineer/bin/verify-layout.mjs` as the original module and the current module on the same simulated scene with root height 115. Original errors: `[]`; current errors: `CONTENT_BOUNDS` on submit. This establishes improvement for that specific verifier defect, not improved agent behavior.

Reproduce the comparison by taking examples/valid-scene.json, setting nodes[0].height to 115, and calling each module's exported verifyLayout with examples/approved-system.json. Temporary CLI fixtures use nodes[2].y increased by five for a violation and a single opening brace for malformed JSON.

## Behavioral evaluation status

All ten cases are NOT RUN as isolated agent/design-tool sessions: approved-screen, local-spacing, missing-component, undocumented-baseline, approved-canonical-change, screenshot-only, scoped-feedback, adapt-inspiration, migration-preserves-behavior, layout-regression. There is no connected design-document adapter or disposable product fixture supplying live mutation/read-back/render evidence. A Codex CLI exists, but no isolated behavioral runner was invoked; Markdown inspection and numeric fixtures cannot substitute for agent transcripts. Claude Code, OpenCode and Pi executables were not found on PATH.

Numeric fixture tests exercise local gap/alignment correction, detached-instance detection, token checks, unsupported geometry disclosure, and an introduced layout regression. These are verifier-level simulations, not evaluations of agent decisions or visual quality. Behavioral adherence, approval pauses, scope preservation in actual tools, responsive/interaction states and inspiration quality remain untested. No original-versus-refactored agent comparison exists.

## Limitations and next iterations

The checker cannot authenticate authority/freshness or discover all omitted component/text metadata. Coverage rules now require external assessment. Provider/runtime compatibility is structural only; no claim is made that all named agents were exercised. Start live evaluations with local-spacing, missing-component, screenshot-only and layout-regression; then test migration states and human visual assessment. Use matched original/refactored runs before claiming improved reliability. Treat remaining improvements as hypotheses until supported by those runs.
