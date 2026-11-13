# Pre-refactor audit and invariant map

Baseline: kedarmd/skills c212d2e30fda21b26c026e61c8bb40d32eff68d6. Checkout was clean; no user edits or applicable AGENTS.md were found. Read all 12 files under design-engineer, repository README, CONTEXT.md and installer. CONTEXT.md concerns PR reviews, not this skill. No package manifest or separate schema exists for this skill; the verifier implements the neutral input contract. Node.js is optional for numeric verification, not core workflow execution.

## Existing responsibilities and decisions

The entry point assesses product/baseline/tool capabilities, maps a system, then contains six working modes: new product, adoption/audit, new feature/screen, refinement, canonical evolution, and inspiration. It requires approved reuse, explicit canonical approval before dependent implementation, fresh numeric read-back and separate rendered QA. Screen acceptance is separate from system approval.

The five protocols own system modeling/reconciliation, scoped proposals and approval gates, adapter discovery, layout evidence/normalized snapshots, and reference synthesis. The entry point references all five, and each mode repeats portions of shared governance. The layout-evidence and system-model documents depend on the verifier's version-1 format; the adapter depends on layout-evidence. Examples are simulated; the root result JSON repeats sample output without run provenance. The installer copies complete skill directories and discovers only top-level SKILL.md directories.

## Confirmed issues

- Task instructions and shared safeguards are interleaved in the entry point. Reference-loading conditions are mostly generic rather than tied to specific decisions.
- Construction guidance is sparse relative to verification: no dedicated hierarchy/content/responsiveness construction procedure.
- Most phase completion and failure recovery are implicit. There is no correction-loop bound.
- Origin explanations appear in both entry point and README without governing current design behavior.
- Approval/reuse/scope rules repeat across entry point, change-control, system-model, tool-interface and README. No direct governance contradiction was found.
- Adoption language requests a normalized registry up front even when optional numeric tooling is unnecessary; this can add avoidable work.
- There are 11 verifier tests but no agent-behavior evaluation assets.
- A 115-high parent contains a child ending at 112, despite declared 24 trailing padding. Baseline checker reports no error: a confirmed missing content-area check.
- Removing all textMetrics or a component record produces no additional missing-evidence finding even with capability flags true. The format cannot infer all omitted metadata; coverage must be assessed externally.
- Approval/provenance are strings, not authenticated records. The checker cannot establish their truth. Sample success is correctly PARTIAL, with visual inspection unresolved.

## Hypotheses, not observed agent failures

Clear routing and measurable phase gates may reduce inconsistent execution. Conditional references may reduce irrelevant context. Construction-first relationships may prevent geometric errors. No captured agent sessions establish the current failure rate or improvement; document length alone is not evidence of ineffectiveness.

## Invariant preservation map

| Existing invariant | Refactored authoritative mechanism |
| --- | --- |
| Greenfield and existing-product support | Entry discovery/routing, new-product/new-screen/audit workflows |
| Identifiable prior approvals reused; no invented history | CONTRACT and system-model authority classification |
| Canonical scope/revision approval before dependent writes | change-control, design-system-change workflow |
| Screen-local repairs need no system reapproval | change-control classification, refine-screen workflow |
| Stable identities, live instances and approved tokens | EXECUTE, layout-construction, adapter boundary |
| Unrelated UI untouched; pre-existing drift separate | CONTRACT scope boundary, refinement/audit/migration routes |
| Actual fresh read-back, separate numeric/render review | VERIFY and layout-evidence coverage matrix |
| Unsupported checks UNVERIFIABLE | Capability discovery and evidence coverage rules |
| Independent inspiration synthesis | Inspiration workflow and synthesis protocol |
| System approval distinct from screen acceptance | PRESENT and change-control gates |
| Approved canonical changes verified before dependents | System-change workflow and recovery boundary |

## Reference principles applied

Read Matt Pocock's writing-for-agents/SKILL.md, SKILL-MECHANICS.md, diagnosing-bugs/SKILL.md, code-review/SKILL.md, and SCOPE.md at 5863806dd4e15c63174bee4e7515a4256792ecfa. Applied conditional context pointers, co-location/single policy ownership, observable completion gates, falsifiable feedback, distinct assessment axes and observed-failure discipline. Did not copy wording, harness-specific invocation rules, delegation requirements, or repository contribution policy.
