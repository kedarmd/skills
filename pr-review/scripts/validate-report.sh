#!/usr/bin/env bash
# Validate a generated pr-review HTML report. No dependencies beyond python3.
set -euo pipefail
REPORT="${1:?usage: validate-report.sh <report.html>}"
python3 - "$REPORT" <<'PY'
import json, re, sys
path = sys.argv[1]
html = open(path, encoding='utf-8').read()
errs = []
for token in ['id="review-data"', 'id="view"', 'id="tab-overview"', 'id="tab-changes"', 'related-findings']:
    if token not in html: errs.append(f'missing {token}')
for token in ['__pr_review_action', 'data-action', 'data-compose-comment', 'comment-body', 'flow-svg', 'theme-toggle', 'code-line', 'data-location']:
    if token not in html: errs.append(f'missing action/diagram hook: {token}')
m = re.search(r'<script type="application/json" id="review-data">(.*?)</script>', html, re.S)
if not m:
    errs.append('review-data JSON block not found')
else:
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        errs.append(f'review-data is not valid JSON: {e}'); data = {}
    else:
        for k in ('schema_version', 'review', 'summary', 'flow', 'findings', 'changes'):
            if k not in data: errs.append(f'review JSON missing key: {k}')
        if not isinstance(data.get('overview'), dict) or not data['overview'].get('summary'):
            errs.append('review JSON needs overview.summary for the opening report summary')
        for c in data.get('changes', []):
            for k in ('path', 'status', 'additions', 'deletions', 'patch'):
                if k not in c: errs.append(f"change {c.get('path', '?')} missing {k}")
        for f in data.get('findings', []):
            for k in ('id', 'severity', 'title', 'summary', 'locations', 'reason', 'impact', 'evidence', 'confidence', 'suggestions'):
                if k not in f: errs.append(f"{f.get('id', '?')} missing {k}")
            if f.get('severity') not in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'):
                errs.append(f"{f.get('id', '?')} bad severity")
            for loc in f.get('locations', []):
                if not loc.get('file') or not loc.get('start_line'):
                    errs.append(f"{f.get('id', '?')} bad location {loc}")
for bad in ('cdn.', 'unpkg.com', 'jsdelivr', 'fonts.googleapis', 'http://', 'https://'):
    # https? allowed only inside JSON evidence strings is noisy; flag src/href refs
    if re.search(r'(src|href)=["\']https?://', html):
        errs.append('external src/href reference found (must be self-contained)'); break
if errs:
    print('INVALID:'); [print(' -', e) for e in errs]; sys.exit(1)
print(f'OK: {path} ({len(data.get("findings", []))} findings)')
PY
