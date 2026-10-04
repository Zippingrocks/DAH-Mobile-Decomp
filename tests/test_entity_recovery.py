"""Authored tooling tests. These do not require or validate the original game."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import entity_recovery as er
from tools.component_recovery import RecoveryError, sha

ROOT=Path(__file__).resolve().parents[1]
GOOD='successful=5 expected-or-recorded-exceptions=1 fixture_calls=2\nMETHOD\to.f()V\t3\t1\n'

class EntityRecoveryTests(unittest.TestCase):
    def test_outcomes_target_and_fixture_counts(self):
        r=er.outcome_counts(GOOD,4)
        self.assertEqual(r['fixture_calls_excluded'],2)
        self.assertEqual(r['methods']['o.f()V'],{'returned':3,'threw':1})

    def test_outcomes_reject_wrong_total(self):
        with self.assertRaises(RecoveryError):er.outcome_counts(GOOD,5)

    def test_outcomes_reject_fixture_total(self):
        with self.assertRaises(RecoveryError):er.outcome_counts(GOOD.replace('fixture_calls=2','fixture_calls=3'),4)

    def test_outcomes_reject_duplicate(self):
        with self.assertRaises(RecoveryError):er.outcome_counts(GOOD+'METHOD\to.f()V\t3\t1\n',8)

    def test_outcomes_reject_missing_or_malformed(self):
        for text in ('','nope',GOOD.replace('\t3\t1','\tx\t1'),GOOD.replace('o.f()V','j.f()V')):
            with self.subTest(text=text),self.assertRaises(RecoveryError):er.outcome_counts(text,4)

    def test_outcomes_reject_zero_member(self):
        with self.assertRaises(RecoveryError):er.outcome_counts('successful=0 expected-or-recorded-exceptions=0 fixture_calls=0\nMETHOD\to.f()V\t0\t0\n',0)

    def test_aliases_are_deterministic(self):
        c={'field_renames':[{'owner':'x','original':'a','descriptor':'I','source_name':'count'}],'method_renames':[]}
        saved=deepcopy(c)
        self.assertEqual(er.alias_lines(c),'field\tx\ta\tI\tcount\n')
        self.assertEqual(c,saved)

    def test_duplicate_alias_rejected(self):
        row={'owner':'x','original':'a','descriptor':'I','source_name':'count'}
        with self.assertRaises(RecoveryError):er.alias_lines({'field_renames':[row,row],'method_renames':[]})

    def test_unsafe_alias_rejected(self):
        for value in ('bad\nname','bad\tname',None):
            c={'field_renames':[{'owner':'x','original':'a','descriptor':'I','source_name':value}],'method_renames':[]}
            with self.subTest(value=value),self.assertRaises(RecoveryError):er.alias_lines(c)

    def test_split_keeps_test_code_out_of_game_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);classes=root/'classes';support=root/'support';classes.mkdir();support.mkdir()
            (classes/'Recovered.class').write_bytes(b'authored fixture');(classes/'Probe.class').write_bytes(b'probe fixture')
            out=er.split_outputs(classes,support,{'Recovered.class'})
            self.assertEqual(out,{'Recovered.class':b'authored fixture'})
            self.assertEqual((support/'Probe.class').read_bytes(),b'probe fixture')
            self.assertFalse((support/'Recovered.class').exists())

    def test_split_missing_game_class_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'support').mkdir();(root/'classes').mkdir()
            with self.assertRaises(RecoveryError):er.split_outputs(root/'classes',root/'support',{'Missing.class'})

    def test_split_shadowing_game_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'support').mkdir();(root/'classes').mkdir()
            for folder in ('classes','support'):(root/folder/'G.class').write_bytes(b'fixture')
            with self.assertRaises(RecoveryError):er.split_outputs(root/'classes',root/'support',{'G.class'})

    def test_manifest_old_sources_unchanged_and_new_scope(self):
        old=json.loads((ROOT/'config/subsystem_recovery.json').read_text())
        new=json.loads((ROOT/er.CONFIG).read_text());new_rows={r['original']:r for r in new['components']}
        self.assertEqual(set(new_rows),er.CLASSES)
        self.assertEqual(sum(r['method_entries'] for r in new_rows.values()),91)
        for r in old['components']:self.assertEqual(r,new_rows[r['original']])
        self.assertEqual(set(new['test_aliases']),{'b.class','c.class','j.class','k.class'})

    def test_runner_refuses_missing_private_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir();(root/'inputs/original').mkdir(parents=True)
            data=b'fixture input only';(root/'inputs/original/test.jar').write_bytes(data)
            (root/'config/target.json').write_text(json.dumps({'id':'test','filename':'test.jar','size_bytes':len(data),'sha256':sha(data)}))
            (root/er.CONFIG).write_text(json.dumps({'target_id':'test','components':[{'original':'a','source_sha256':'0'*64}]}))
            with self.assertRaises(RecoveryError):er.run(root,root/'run')
            self.assertFalse((root/'run').exists())

    @unittest.skipUnless(shutil.which('javac'),'Optional JDK compilation test')
    def test_probe_compiles_without_any_game_sources(self):
        names=['tests/java/EntityProbe.java','tests/java/entity_support/javax/microedition/lcdui/Graphics.java',
            'tests/java/subsystem_support/javax/microedition/lcdui/Image.java']
        names += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'tests/java/subsystem_support/javax/microedition/media').glob('*.java'))]
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);empty=out/'empty';empty.mkdir()
            p=subprocess.run(['javac','--release','8','-g:none','-implicit:none','-classpath',str(empty),'-sourcepath',str(empty),'-d',str(out),*[str(ROOT/n) for n in names]],capture_output=True,text=True,timeout=30)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue((out/'EntityProbe.class').exists())
            for name in er.CLASSES:self.assertFalse((out/(name+'.class')).exists())

if __name__=='__main__':unittest.main()
