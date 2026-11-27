#!/usr/bin/env python3
"""Capture immutable Git/gh facts for a review, including local worktree changes."""
import argparse
import datetime
import difflib
import json
import subprocess
from pathlib import Path


def collect(repo, mode, base, head, pr=None, include=()):
    repo = Path(repo).resolve()
    def run(*args, binary=False):
        return subprocess.check_output(args, cwd=repo, text=not binary)
    def git(*args, **kwargs):
        return run('git', *args, **kwargs)
    metadata = None
    if mode == 'pull_request':
        if not pr:
            raise ValueError('--pr is required in pull_request mode')
        metadata = json.loads(run('gh', 'pr', 'view', str(pr), '--json', 'number,url,title,body,author,baseRefName,headRefName,baseRefOid,headRefOid'))
        base, head = metadata['baseRefOid'], metadata['headRefOid']
        repository = json.loads(run('gh', 'repo', 'view', '--json', 'nameWithOwner'))['nameWithOwner']
    else:
        repository = repo.name
    if not base:
        raise ValueError('--base must identify the explicitly selected review baseline')
    base_sha = git('rev-parse', '--verify', base + '^{commit}').strip()
    head_sha = git('rev-parse', '--verify', (head or 'HEAD') + '^{commit}').strip()
    review = {'mode': mode, 'repository': repository, 'base_sha': base_sha, 'head_sha': head_sha, 'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if metadata:
        review.update(pull_request=metadata['number'], pr_url=metadata['url'], pr_title=metadata['title'], pr_author=metadata['author']['login'], base_ref=metadata['baseRefName'], head_ref=metadata['headRefName'])
    target = [] if mode == 'local' else [head_sha]
    names = git('diff', '--no-renames', '--name-status', '-z', base_sha, *target, '--', binary=True).decode().split('\0')
    entries = [(names[i], names[i + 1]) for i in range(0, len(names) - 1, 2)]
    if mode == 'local':
        entries += [('A', p) for p in git('ls-files', '--others', '--exclude-standard', '-z').split('\0') if p]
    changes, sources = [], {}
    def source(revision, path):
        result = subprocess.run(['git', 'show', revision + ':' + path], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout if result.returncode == 0 else b''
    for status, path in sorted(set(entries), key=lambda item: item[1]):
        left = source(base_sha, path)
        if mode == 'local':
            candidate = repo / path
            right = candidate.read_bytes() if candidate.is_file() and not candidate.is_symlink() else (candidate.readlink().as_posix().encode() if candidate.is_symlink() else b'')
        else:
            right = source(head_sha, path)
        binary = b'\0' in left or b'\0' in right
        left_text, right_text = left.decode('utf-8', errors='replace'), right.decode('utf-8', errors='replace')
        # Git patches retain hunk coordinates and special metadata for tracked files.
        if mode == 'local' and status == 'A':
            patch = ''.join(difflib.unified_diff([line + '\n' for line in left_text.splitlines()], [line + '\n' for line in right_text.splitlines()], fromfile='a/' + path, tofile='b/' + path)) if not binary else ''
        else:
            patch = git('diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--unified=3', base_sha, *target, '--', path)
        additions = sum(line.startswith('+') and not line.startswith('+++') for line in patch.splitlines())
        deletions = sum(line.startswith('-') and not line.startswith('---') for line in patch.splitlines())
        changes.append({'path': path, 'status': {'A':'added','D':'deleted','M':'modified','T':'modified'}.get(status, status), 'additions': additions, 'deletions': deletions, 'patch': patch, 'binary': binary})
        sources[path] = {'LEFT': left_text, 'RIGHT': right_text}
    for path in include:
        candidate = (repo / path).resolve()
        if not candidate.is_relative_to(repo):
            raise ValueError('--include paths must stay inside the repository')
        if path not in sources:
            right = candidate.read_bytes() if mode == 'local' and candidate.is_file() else source(head_sha, path)
            sources[path] = {'LEFT': source(base_sha, path).decode('utf-8', errors='replace'), 'RIGHT': right.decode('utf-8', errors='replace')}
    if metadata:
        latest = json.loads(run('gh', 'pr', 'view', str(metadata['number']), '--json', 'headRefOid'))
        if latest['headRefOid'] != head_sha:
            raise ValueError('PR head changed during collection; recollect before reviewing')
    return {'schema_version': '2.0', 'review': review, 'changes': changes, 'sources': sources, 'commits': int(git('rev-list', '--count', base_sha + '..' + head_sha)), 'pr_context': None, 'pr_description': metadata['body'] if metadata else ''}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='.')
    parser.add_argument('--mode', choices=['pull_request','commit_range','local'], required=True)
    parser.add_argument('--base')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--pr')
    parser.add_argument('--output', required=True)
    parser.add_argument('--include', action='append', default=[], help='Additional supporting source path to capture')
    args = parser.parse_args()
    try:
        data = collect(args.repo, args.mode, args.base, args.head, args.pr, args.include)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(data, indent=2) + '\n')
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Context collection failed: {error}\n')


if __name__ == '__main__':
    main()
