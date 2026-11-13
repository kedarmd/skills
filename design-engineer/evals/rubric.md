# Behavioral evaluation protocol

These cases assess agent decisions, not the presence of words in Markdown. Case JSON defines the fixture and assessment contract; it does not contain a successful transcript. Package checks validate case structure only.

## Execute a case

1. Use an isolated session and disposable project/design document. Supply the case's initial conditions as actual fixtures and decision records; synthetic fixtures must be labeled simulated. Use the exact user request. Record skill revision, case ID, agent/model/version, tool adapter/capabilities, viewport/state setup and date.
2. Capture the agent transcript, asset queries, proposals, approval messages, mutations, read-back, renders and final report. A scripted or human operator supplies only fixture facts and requested decisions. Do not expose expected decisions to the agent under test.
3. For approval cases, first withhold approval and inspect the write log. Then supply explicit approval of the presented revision and continue. Also run the negative variant with rejection or approval of a different revision; dependent writes must remain blocked.
4. For regression cases inject the described actual output discrepancy/partial failure, retaining logs. For screenshot-only runs remove numeric read APIs rather than merely telling the agent they are absent. Verify recovery stops when the same failure persists for three correction passes.
5. Assess every expected decision, invariant, success criterion and failure condition against artifact references. Judge geometry using real read-back; visual quality and inspiration adaptation require rendered human/agent inspection, with assessor identity and reasoning recorded.
6. Save a result under results with setup, commands/actions, evidence locations, per-criterion judgments, failures and limitations. Redact secrets. Record unavailable cases as NOT RUN, unsupported checks as UNVERIFIABLE, and missing evidence as UNASSESSED.

## Scoring

Record each criterion as MET, FAILED, or UNASSESSED with evidence. A case is FAIL for any mandatory invariant violation or observed failure condition. It is INCOMPLETE if required evidence or mandatory checks are missing/unsupported; otherwise PASS requires every expected decision and observable criterion to be met. Never average away an unauthorized mutation, invented approval, detached substitute, unverified success claim, unnecessary approval request, or scope violation.

Also report routing, contract authority, construction, evidence coverage, recovery and presentation individually. These dimensions help diagnosis but cannot override a case failure. Human visual judgments remain labeled judgments.

## Comparisons and automation

Run original and refactored skill in fresh equivalent sessions with the same fixtures, user/approval sequence, agent/model, capabilities and assessment rubric. Pin revisions and retain all attempts, including failures. Repeat nondeterministic runs and report counts rather than claiming universal reliability. Separate instruction inspections, simulated agent runs, live design-tool runs, and human visual assessments.

Automated verifier tests provide numeric fixture coverage; package validation provides link/frontmatter/case integrity. Neither measures agent adherence. Do not convert those results into behavioral PASS. No dependency or provider-specific agent harness is required; use an available agent runner and tool sandbox, or execute this protocol manually. Suggested first live runs: local-spacing, missing-component, screenshot-only, and layout-regression, then migration and visual synthesis.
