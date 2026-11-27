#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 - "$SCRIPT_DIR" "${1:?usage: validate-report.sh <report.html>}" <<'PY'
import json, re, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from report_pipeline import check, render
try:
    html = Path(sys.argv[2]).read_text()
    match = re.search(r'<script type="application/json" id="review-data">(.*?)</script>', html, re.S)
    if not match: raise ValueError('review-data block missing')
    data = json.loads(match[1])
    check(data, 'review')
    if html != render(data): raise ValueError('report does not match the canonical template and assets; rebuild it')
    print(f'OK: {sys.argv[2]} ({len(data["findings"])} findings)')
except (ValueError, OSError) as error:
    sys.exit(f'INVALID: {error}')
PY
