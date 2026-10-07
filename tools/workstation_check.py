#!/usr/bin/env python3
"""Check local prerequisites; historical evidence is not a restored workstation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

try:
    from . import dah1
    from . import integration_recovery
except ImportError:
    import dah1
    import integration_recovery

ROOT = Path(__file__).resolve().parents[1]


def source_inventory(root, records, source_dir='src/game'):
    result = {}
    for row in records:
        path = root / source_dir / (row['class'] + '.java')
        result[row['class']] = (
            'missing' if not path.is_file() else
            'match' if hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
            else 'different_snapshot'
        )
    return result


def compiler_check():
    if not shutil.which('javac'):
        return {'passed': False, 'reason': 'javac unavailable'}
    try:
        version = subprocess.run(['javac', '-version'], capture_output=True,
                                 text=True, check=True, timeout=30)
        with tempfile.TemporaryDirectory(prefix='dah-compiler-check-') as td:
            source = Path(td) / 'CompilerCheck.java'
            source.write_text('class CompilerCheck {}\n')
            subprocess.run(['javac', '--release', '8', '-g:none', '-implicit:none',
                            '-d', td, str(source)], capture_output=True,
                           text=True, check=True, timeout=30)
        return {'passed': True, 'version': (version.stdout + version.stderr).strip()}
    except (OSError, subprocess.SubprocessError) as exc:
        return {'passed': False, 'reason': str(exc)}


def inspect(root=ROOT, manifest=None):
    target = dah1.load_target(root / 'config/target.json')
    original = root / 'inputs/original' / target['filename']
    try:
        audit = dah1.audit_jar(dah1.verify_input(original, target))
        dah1.check_baseline(audit, target)
        reference = {'passed': True, 'sha256': audit['input_sha256'],
                     'classes': audit['class_count'], 'totals': audit['totals']}
    except (OSError, ValueError) as exc:
        reference = {'passed': False, 'reason': str(exc)}
    config = integration_recovery.config(manifest or root / 'config/integration_recovery.json')
    sources = source_inventory(root, config['classes'], config.get('source_dir', 'src/game'))
    compiler = compiler_check()
    dependencies = {name: shutil.which(name) is not None
                    for name in ('java', 'javap', 'ffmpeg')}
    recon_ready = reference['passed'] and compiler['passed'] and dependencies['java'] and dependencies['javap']
    replay_ready = recon_ready and all(dependencies.values()) and all(v == 'match' for v in sources.values())
    return {'schema_version': 1, 'target_id': target['id'],
            'reference': reference, 'compiler': compiler, 'dependencies': dependencies,
            'private_source_snapshots': sources,
            'recon_prerequisites_ready': bool(recon_ready),
            'integration_replay_ready': bool(replay_ready),
            'behavior_replayed': False,
            'scope': 'Local prerequisites only; run public tests and actual integration comparisons separately.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--config', type=Path, help='Select an independently verified source manifest.')
    args = parser.parse_args(argv)
    result = inspect(manifest=args.config)
    text = json.dumps(result, indent=2) + '\n'
    if args.report:
        with args.report.open('x') as out:
            out.write(text)
    print(text, end='')
    return 0 if result['integration_replay_ready'] else 1


if __name__ == '__main__':
    sys.exit(main())
