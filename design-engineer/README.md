# Design Engineer

One tool-neutral skill for greenfield products, existing-product design, screen refinement, design-system governance, audits, and inspiration research.

**Design against an explicit contract. Verify actual output, not intended changes.**

[SKILL.md](SKILL.md) routes tasks through DISCOVER → CONTRACT → PLAN → EXECUTE ↔ VERIFY → PRESENT. Workflows load only the relevant shared references. Existing approved definitions retain their authority; canonical revisions require scoped approval before dependent work. Ordinary corrections within approved rules proceed without system reapproval. Screen acceptance remains separate.

## Package

- [Workflows](workflows/new-screen.md): new product, new screen, refinement, canonical change, audit, and inspiration.
- [Contract model](protocol/system-model.md) and [change control](protocol/change-control.md): authority, approvals, scope, and migrations.
- [Layout construction](protocol/layout-construction.md): hierarchy, native constraints, tokens, realistic content, and intentional layering.
- [Tool boundary](protocol/tool-interface.md) and [verification](protocol/layout-evidence.md): capability discovery, fresh actual read-back, numeric and visual evidence, recovery and limitations.
- [Evaluation rubric](evals/rubric.md), cases, and [actual results](evals/results/implementation.md).

Install this whole directory through the repository installer or copy it to your agent's skill directory. Supporting files are internal documents, not separate skills. The entry point uses portable name/description frontmatter and no agent-specific commands.

## Optional verifier

Requires Node.js; no package installation or design-tool integration is included. From this directory:

```bash
node tests/verify-layout.test.mjs
node tests/validate-package.mjs
node bin/verify-layout.mjs examples/approved-system.json examples/valid-scene.json
```

Fixtures are simulations, not real approvals or tool exports. The sample returns PARTIAL with exit code 0: no reported numeric errors, visual inspection unresolved. The verifier cannot authenticate provenance, detect all omitted metadata, or certify rendered quality. See its [coverage limits](protocol/layout-evidence.md). Tool-independent policy does not imply every adapter supports every check; unsupported mandatory checks are UNVERIFIABLE.

No comparative agent-performance improvement is claimed. The [audit](evals/results/audit.md) separates observed implementation issues from behavioral hypotheses; the evaluation protocol explains how to collect comparable evidence across agents and tools.
