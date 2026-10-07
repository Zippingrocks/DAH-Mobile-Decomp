import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import workstation_check as wc


class WorkstationCheckTests(unittest.TestCase):
    def test_selected_snapshot_is_checked_instead_of_legacy_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / 'src/game/verification'
            folder.mkdir(parents=True)
            (folder / 'a.java').write_bytes(b'accepted')
            (root / 'src/game/a.java').write_bytes(b'legacy')
            rows = [{'class': 'a', 'sha256': hashlib.sha256(b'accepted').hexdigest()}]
            self.assertEqual(wc.source_inventory(root, rows, 'src/game/verification'), {'a': 'match'})

    def test_partial_or_changed_checkpoint_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / 'src/game'
            source.mkdir(parents=True)
            (source / 'a.java').write_bytes(b'accepted')
            (source / 'b.java').write_bytes(b'older snapshot')
            records = [{'class': name, 'sha256': hashlib.sha256(b'accepted').hexdigest()}
                       for name in ('a', 'b', 'c')]
            self.assertEqual(wc.source_inventory(root, records),
                             {'a': 'match', 'b': 'different_snapshot', 'c': 'missing'})

    def test_runtime_alone_does_not_supply_compiler(self):
        with patch.object(wc.shutil, 'which', return_value=None):
            self.assertFalse(wc.compiler_check()['passed'])

    def test_rejected_release_8_compilation_blocks_readiness(self):
        import subprocess
        with patch.object(wc.shutil, 'which', return_value='/fixture/javac'), \
             patch.object(wc.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'javac')):
            self.assertFalse(wc.compiler_check()['passed'])
