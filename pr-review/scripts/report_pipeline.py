"""Deterministic report assembly; only the Python standard library is required."""
import datetime
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(value, schema, path='$'):
    """Validate the JSON Schema subset used by this package, failing at exact paths."""
    if '$ref' in schema:
        schema = json.loads((ROOT / 'schemas' / schema['$ref']).read_text())
    if 'oneOf' in schema:
        matches = 0
        for variant in schema['oneOf']:
            try:
                validate(value, variant, path)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(f'{path}: expected exactly one supported shape')
        return
    kinds = {'object': dict, 'array': list, 'string': str, 'integer': int, 'number': (int, float), 'boolean': bool, 'null': type(None)}
    expected = schema.get('type')
    if expected:
        choices = expected if isinstance(expected, list) else [expected]
        if not any(isinstance(value, kinds[k]) and not (k in ('integer', 'number') and isinstance(value, bool)) for k in choices):
            raise ValueError(f'{path}: expected {expected}')
    if 'const' in schema and value != schema['const']:
        raise ValueError(f'{path}: expected {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: unsupported value {value!r}')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                raise ValueError(f'{path}.{key}: required')
        for key, item in value.items():
            if key in schema.get('properties', {}):
                validate(item, schema['properties'][key], path + '.' + key)
            elif isinstance(schema.get('additionalProperties'), dict):
                validate(item, schema['additionalProperties'], path + '.' + key)
            elif schema.get('additionalProperties') is False:
                raise ValueError(f'{path}.{key}: unexpected field')
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise ValueError(f'{path}: too few items')
        for i, item in enumerate(value):
            validate(item, schema.get('items', {}), f'{path}[{i}]')
    elif isinstance(value, str):
        if schema.get('format') == 'date-time':
            try:
                stamp = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
                if stamp.tzinfo is None: raise ValueError()
            except ValueError:
                raise ValueError(f'{path}: expected timezone-qualified date-time')
        if len(value.strip()) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            raise ValueError(f'{path}: invalid string length')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValueError(f'{path}: invalid format')
    elif isinstance(value, (float, int)):
        if value < schema.get('minimum', -float('inf')) or value > schema.get('maximum', float('inf')):
            raise ValueError(f'{path}: out of range')


def check(data, name):
    validate(data, json.loads((ROOT / 'schemas' / (name + '.schema.json')).read_text()))
    context = data.get('pr_context')
    if context:
        if context['lifecycle'] != 'open' and not context['closed_at']:
            raise ValueError('pr_context.closed_at: required for closed/merged PR')
        if context['lifecycle'] == 'merged' and not context['merged_at']:
            raise ValueError('pr_context.merged_at: required for merged PR')
        if context['lifecycle'] == 'open' and (context['closed_at'] or context['merged_at']):
            raise ValueError('pr_context: open PR cannot have lifecycle end dates')


def prepare(data):
    check(data, 'analysis')
    result = copy.deepcopy(data)
    for i, finding in enumerate(result['findings'], 1):
        finding['id'] = f'F-{i:03d}'
        for loc in finding['locations']:
            if loc['end_line'] < loc['start_line']:
                raise ValueError(f'{finding["id"]}: end_line precedes start_line')
    check(result, 'accepted')
    return result


def anchors(patch):
    result = {'LEFT': set(), 'RIGHT': set()}
    old = new = None
    for line in patch.splitlines():
        match = re.match(r'@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
        if match:
            old, new = map(int, match.groups())
        elif old is not None:
            if line.startswith(' '):
                result['LEFT'].add(old); result['RIGHT'].add(new)
                old += 1; new += 1
            elif line.startswith('-'):
                result['LEFT'].add(old); old += 1
            elif line.startswith('+'):
                result['RIGHT'].add(new); new += 1
    return result


def assemble(context, accepted, comments):
    check(context, 'context'); check(accepted, 'accepted'); check(comments, 'comments')
    ids = [f['id'] for f in accepted['findings']]
    if len(set(ids)) != len(ids):
        raise ValueError('accepted findings contain duplicate IDs')
    translated = {}
    for item in comments['comments']:
        fid = item['finding_id']
        if fid not in ids or fid in translated:
            raise ValueError(f'comments: unknown or duplicate finding ID {fid}')
        translated[fid] = item
    if set(ids) != set(translated):
        raise ValueError('comments: provide one comment for every accepted finding')
    changes = copy.deepcopy(context['changes'])
    files = {c['path']: c for c in changes}
    review = copy.deepcopy(context['review'])
    findings = []
    for f in accepted['findings']:
        item = {k: copy.deepcopy(v) for k, v in f.items() if k != 'recommendation'}
        item['summary'] = f['reason']
        comment = translated[f['id']]
        suggestion = {'id': 'S-' + f['id'][2:], 'title': 'Suggested comment', 'comment': comment['comment']}
        if 'code' in comment:
            suggestion['code'] = comment['code']
        item['suggestions'] = [suggestion]
        for loc in item['locations']:
            if loc['file'] not in context['sources']:
                raise ValueError(f'{f["id"]}: source not captured: {loc["file"]}; recollect with --include')
            lines = context['sources'][loc['file']][loc['side']].splitlines()
            if loc['end_line'] < loc['start_line'] or loc['end_line'] > len(lines):
                raise ValueError(f'{f["id"]}: source range is outside the reviewed snapshot')
            start = max(1, loc['start_line'] - 3)
            loc['code_excerpt_start_line'] = start
            loc['code_excerpt'] = '\n'.join(lines[start - 1:min(len(lines), loc['end_line'] + 3)])
            loc['commit_sha'] = review['head_sha']
            loc['commentable'] = loc['end_line'] in anchors(files.get(loc['file'], {}).get('patch', ''))[loc['side']]
        findings.append(item)
    for change in changes:
        change['finding_ids'] = [f['id'] for f in findings if any(l['file'] == change['path'] for l in f['locations'])]
    overview = copy.deepcopy(accepted['overview'])
    overview['stats'] = {'files': len(changes), 'additions': sum(c['additions'] for c in changes), 'deletions': sum(c['deletions'] for c in changes), 'commits': context.get('commits', 0)}
    result = {'schema_version': '2.0', 'review': review, 'overview': overview, 'findings': findings, 'changes': changes, 'pr_context': context.get('pr_context'), 'summary': {s.lower(): sum(f['severity'] == s for f in findings) for s in ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')}}
    check(result, 'review')
    return result


def render(data):
    check(data, 'review')
    replacements = {'{{REPORT_CSS}}': (ROOT / 'assets/report.css').read_text(), '{{REPORT_JS}}': (ROOT / 'assets/report.js').read_text(), '{{REVIEW_DATA}}': json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')}
    template = (ROOT / 'templates/report.html').read_text()
    for marker in replacements:
        if template.count(marker) != 1:
            raise ValueError(f'template must contain exactly one {marker}')
    return re.sub(r'\{\{(?:REPORT_CSS|REPORT_JS|REVIEW_DATA)\}\}', lambda match: replacements[match[0]], template)
