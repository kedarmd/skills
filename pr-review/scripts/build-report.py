#!/usr/bin/env python3
"""Prepare the agent handoff or build a fixed, self-contained report."""
import argparse
import json
from pathlib import Path
from report_pipeline import prepare, assemble, render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('--analysis', required=True)
    prep.add_argument('--output', required=True)
    build = commands.add_parser('build')
    for name in ('context', 'analysis', 'comments', 'output'):
        build.add_argument('--' + name, required=True)
    args = parser.parse_args()
    read = lambda path: json.loads(Path(path).read_text())
    try:
        if args.command == 'prepare':
            output = json.dumps(prepare(read(args.analysis)), indent=2) + '\n'
        else:
            output = render(assemble(read(args.context), read(args.analysis), read(args.comments)))
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'Invalid review input: {error}\n')


if __name__ == '__main__':
    main()
