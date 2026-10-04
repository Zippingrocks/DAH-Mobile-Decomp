"""Public tool/fixture checks, not DAH gameplay or recovered source publication."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import weapon_recovery as wr
from tools.component_recovery import RecoveryError, sha, source_files

ROOT=Path(__file__).resolve().parents[1]

class WeaponRecoveryTests(unittest.TestCase):
    def test_scope_is_exact_and_includes_prior_snapshots(self):
        old=json.loads((ROOT/'config/collection_recovery.json').read_text())
        new=json.loads((ROOT/wr.CONFIG).read_text())
        self.assertEqual({c['original'] for c in new['components']},wr.CLASSES)
        self.assertEqual(sum(c['method_entries'] for c in new['components']),151)
        indexed={r['original']:r for r in new['components']}
        for row in old['components']:self.assertEqual(row,indexed[row['original']])

    def test_only_four_game_classes_remain_outside_the_new_artifact(self):
        names={'GameMidlet',*list('abcdefghijklmnopqrst')}
        self.assertEqual(names-wr.CLASSES,{'b','j','k','p'})

    def test_test_support_cannot_supply_recovered_classes(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        self.assertFalse(set(c['support_classes']) & {n+'.class' for n in wr.CLASSES})
        self.assertEqual(set(c['test_aliases']),{'b.class','j.class','k.class'})
        self.assertNotIn('c.class',c['support_classes']);self.assertNotIn('f.class',c['support_classes'])

    def test_transform_alias_does_not_replace_final_base_predicate(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        aliases=c['method_renames']
        self.assertIn({'owner':'j','original':'a','descriptor':'(II)V','source_name':'transform'},aliases)
        self.assertNotIn({'owner':'o','original':'a','descriptor':'(II)Z','source_name':'transform'},aliases)
        self.assertEqual(c['test_aliases']['j.class']['transform'],'a')

    def test_distinct_weapon_field_descriptors_are_mapped(self):
        c=json.loads((ROOT/wr.CONFIG).read_text());rows=[r for r in c['field_renames'] if r['owner']=='c' and r['original']=='a']
        self.assertEqual({r['descriptor'] for r in rows},{'[B','I','Z','Ljavax/microedition/lcdui/Image;','Lj;','Lo;','La;','B'})
        self.assertEqual(len({r['source_name'] for r in rows}),len(rows))

    def test_lifecycle_controller_remains_unrecovered(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        self.assertIn('k.class',c['support_classes'])
        self.assertIn('tests/java/weapon_support/k.java',c['support_sources'])

    def test_aliases_are_repeatable(self):
        c=json.loads((ROOT/wr.CONFIG).read_text());before=deepcopy(c)
        self.assertEqual(wr.alias_lines(c),wr.alias_lines(c));self.assertEqual(c,before)

    def test_duplicate_or_injected_alias_rejected(self):
        for row in ({'owner':'x','original':'a','descriptor':'I','source_name':'safe'}, {'owner':'x','original':'a','descriptor':'I','source_name':'bad\tname'}):
            c={'field_renames':[row,row],'method_renames':[]}
            with self.assertRaises(RecoveryError):wr.alias_lines(c)

    def test_counts_allow_multicharacter_midlet_owner(self):
        text='successful=5 expected-or-recorded-exceptions=2 fixture_calls=3\nMETHOD\tGameMidlet.startApp()V\t1\t1\nMETHOD\tc.b()V\t1\t0\nMETHOD\tf.r()V\t1\t0\n'
        self.assertEqual(wr.outcome_counts(text,4)['fixture_calls_excluded'],3)

    def test_counts_exclude_fixture_and_nested_calls(self):
        text='successful=13 expected-or-recorded-exceptions=2 fixture_calls=10\nMETHOD\tc.b()V\t3\t2\n'
        out=wr.outcome_counts(text,5);self.assertEqual(out['methods']['c.b()V'],{'returned':3,'threw':2})
        with self.assertRaises(RecoveryError):wr.outcome_counts(text,15)

    def test_counts_reject_wrong_owner_zero_duplicate_malformed(self):
        rows=['METHOD\tj.g()V\t1\t0','METHOD\tf.g()V\t0\t0','METHOD\tc.a()V\t-1\t2','METHOD\tf.g()V\t1\t0\nMETHOD\tf.g()V\t1\t0']
        for row in rows:
            with self.subTest(row=row),self.assertRaises(RecoveryError):wr.outcome_counts('successful=1 expected-or-recorded-exceptions=0 fixture_calls=0\n'+row,1)

    def test_split_excludes_support_and_probes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=root/'compiled';b=root/'support';a.mkdir();b.mkdir()
            (a/'c.class').write_bytes(b'fixture candidate');(a/'WeaponProbe.class').write_bytes(b'fixture probe')
            actual=wr.split_outputs(a,b,{'c.class'});self.assertEqual(actual,{'c.class':b'fixture candidate'})
            self.assertFalse((b/'c.class').exists());self.assertTrue((b/'WeaponProbe.class').exists())

    def test_missing_source_cannot_be_replaced_with_original(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(RecoveryError):source_files(Path(tmp),c)

    def test_new_source_hashes_and_resource_metadata_not_bodies(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        for r in c['components']:
            self.assertRegex(r['source_sha256'],r'^[0-9a-f]{64}$');self.assertRegex(r['original_class_sha256'],r'^[0-9a-f]{64}$')
        for p,d in c['resource_hashes'].items():self.assertRegex(d,r'^[0-9a-f]{64}$')
        self.assertIn('pics/Alien_Weapon_Strip.png',c['resource_hashes'])

    @unittest.skipUnless(shutil.which('javac'),'JDK needed for independently authored probe compilation')
    def test_probe_compiles_without_any_game_source(self):
        c=json.loads((ROOT/wr.CONFIG).read_text())
        # Probe uses reflection; only public Java/phone test adapters are linked here.
        sources=[ROOT/p for p in c['support_sources'] if '/javax/' in p or p.endswith('/WeaponProbe.java')]
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);(out/'empty').mkdir()
            run=subprocess.run(['javac','--release','8','-g:none','-implicit:none','-sourcepath',str(out/'empty'),'-classpath',str(out/'empty'),'-d',str(out),*map(str,sources)],capture_output=True,text=True,timeout=40)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertTrue((out/'WeaponProbe.class').is_file())
            self.assertFalse(any((out/(n+'.class')).exists() for n in wr.CLASSES))

if __name__=='__main__':unittest.main()
