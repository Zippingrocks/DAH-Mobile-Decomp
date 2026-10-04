"""Public tooling tests use authored fixtures, not original or recovered game code."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from tools import collection_recovery as cr
from tools.component_recovery import RecoveryError, sha
from tools.subsystem_recovery import normalized_inventory, alias_test_fields

ROOT=Path(__file__).resolve().parents[1]
GOOD='successful=5 expected-or-recorded-exceptions=1 fixture_calls=2\nMETHOD\tn.a()I\t3\t1\n'

class CollectionRecoveryTests(unittest.TestCase):
    def test_outcome_accounting_excludes_fixtures(self):
        result=cr.outcome_counts(GOOD,4)
        self.assertEqual(result,{'fixture_calls_excluded':2,'methods':{'n.a()I':{'returned':3,'threw':1}}})

    def test_outcome_counts_cannot_disagree(self):
        for text,count in ((GOOD,5),(GOOD.replace('fixture_calls=2','fixture_calls=3'),4)):
            with self.subTest(text=text,count=count),self.assertRaises(RecoveryError):cr.outcome_counts(text,count)

    def test_outcome_duplicate_cannot_inflate_results(self):
        with self.assertRaises(RecoveryError):cr.outcome_counts(GOOD+'METHOD\tn.a()I\t3\t1\n',8)

    def test_outcome_wrong_target_cannot_count_as_recovery(self):
        with self.assertRaises(RecoveryError):cr.outcome_counts(GOOD.replace('n.a()I','j.a()I'),4)

    def test_outcome_bad_or_zero_counts_rejected(self):
        for text in ('','nope',GOOD.replace('\t3\t1','\t-1\t5'),GOOD.replace('\t3\t1','\t0\t0')):
            with self.subTest(text=text),self.assertRaises(RecoveryError):cr.outcome_counts(text,4)

    def test_alias_records_preserve_owner_and_descriptor(self):
        cfg={'field_renames':[dict(owner='n',original='a',descriptor='I',source_name='originX'),dict(owner='n',original='a',descriptor='Z',source_name='needsSort')],'method_renames':[]}
        old=deepcopy(cfg);lines=cr.alias_lines(cfg)
        self.assertIn('field\tn\ta\tI\toriginX\n',lines);self.assertIn('field\tn\ta\tZ\tneedsSort\n',lines)
        self.assertEqual(cfg,old)

    def test_alias_duplicate_or_injected_record_rejected(self):
        row=dict(owner='n',original='a',descriptor='I',source_name='originX')
        with self.assertRaises(RecoveryError):cr.alias_lines({'field_renames':[row,row],'method_renames':[]})
        row['source_name']='bad\nfield'
        with self.assertRaises(RecoveryError):cr.alias_lines({'field_renames':[row],'method_renames':[]})

    def test_three_return_only_overloads_stay_distinct(self):
        cfg=json.loads((ROOT/cr.CONFIG).read_text())
        text='  public void a(o);\n    descriptor: (Lo;)V\n  public static boolean isVisible(o);\n    descriptor: (Lo;)Z\n  public o nearby(o);\n    descriptor: (Lo;)Lo;\n'
        self.assertEqual(normalized_inventory(text,'n',cfg['method_renames'],True),[('a','(Lo;)V'),('a','(Lo;)Z'),('a','(Lo;)Lo;')])

    def test_all_prior_source_snapshots_are_unchanged(self):
        old=json.loads((ROOT/'config/entity_recovery.json').read_text());new=json.loads((ROOT/cr.CONFIG).read_text())
        rows={r['original']:r for r in new['components']}
        for row in old['components']:self.assertEqual(row,rows[row['original']])
        self.assertEqual(set(rows),cr.CLASSES);self.assertEqual(len(rows),14)
        self.assertEqual(sum(r['method_entries'] for r in rows.values()),124)
        self.assertEqual(set(rows)-{r['original'] for r in old['components']},{'n','d','r'})

    def test_support_roster_excludes_every_recovered_class(self):
        cfg=json.loads((ROOT/cr.CONFIG).read_text());names=cfg['support_classes']
        self.assertEqual(len(names),len(set(names)))
        self.assertFalse(set(names)&{n+'.class' for n in cr.CLASSES})
        self.assertIn('ProbeEntity.class',names);self.assertIn('BuildingsResourceOwner.class',names)
        for p in cfg['support_sources']:self.assertTrue(p.startswith('tests/java/'));self.assertTrue((ROOT/p).is_file())
        for n in cfg['test_aliases']:self.assertNotIn(n,{x+'.class' for x in cr.CLASSES})

    def test_public_resource_metadata_contains_only_hashes(self):
        cfg=json.loads((ROOT/cr.CONFIG).read_text())
        for name in ('data/HousePieces.dat','data/HouseParts.dat','data/Houses.dat','pics/house.png','pics/barn.png'):
            self.assertRegex(cfg['resource_hashes'][name],r'^[a-f0-9]{64}$')
        for row in cfg['components']:self.assertRegex(row['source_sha256'],r'^[a-f0-9]{64}$')

    def test_split_excludes_probe_and_actor_test_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);c=r/'c';s=r/'s';c.mkdir();s.mkdir()
            for n in ('n','d','r','ProbeEntity','j'):(c/(n+'.class')).write_bytes(('authored '+n).encode())
            output=cr.split_outputs(c,s,{'n.class','d.class','r.class'})
            self.assertEqual(set(output),{'n.class','d.class','r.class'});self.assertTrue((s/'j.class').exists())
            self.assertFalse((s/'n.class').exists())

    def test_existing_support_cannot_shadow_recovered_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);(r/'c').mkdir();(r/'s').mkdir()
            for folder in ('c','s'):(r/folder/'n.class').write_bytes(b'authored fixture')
            with self.assertRaises(RecoveryError):cr.split_outputs(r/'c',r/'s',{'n.class'})

    def test_missing_private_sources_stop_before_run_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);(r/'config').mkdir();(r/'inputs/original').mkdir(parents=True)
            data=b'authored';(r/'inputs/original/input.jar').write_bytes(data)
            (r/'config/target.json').write_text(json.dumps(dict(id='fixture',filename='input.jar',size_bytes=len(data),sha256=sha(data))))
            (r/cr.CONFIG).write_text(json.dumps(dict(target_id='fixture',components=[dict(original='n',source_sha256='0'*64)])))
            with self.assertRaises(RecoveryError):cr.run(r,r/'results')
            self.assertFalse((r/'results').exists())

    @unittest.skipUnless(shutil.which('javac') and shutil.which('java'),'Optional JDK test')
    def test_authored_probe_compiles_and_selects_declared_shadowed_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=Path(tmp);(r/'empty').mkdir()
            # This temporary o is solely a signature fixture, never recovered source.
            (r/'o.java').write_text('class o {public int k,l; public boolean g; public o(int x,int y,int type){} public void a(){} public void f(){} public void g(){}}')
            paths=[ROOT/'tests/java/CollectionProbe.java',ROOT/'tests/java/entity_support/javax/microedition/lcdui/Graphics.java',ROOT/'tests/java/subsystem_support/javax/microedition/lcdui/Image.java']+sorted((ROOT/'tests/java/subsystem_support/javax/microedition/media').glob('*.java'))
            p=subprocess.run(['javac','--release','8','-g:none','-implicit:none','-sourcepath',str(r/'empty'),'-classpath',str(r/'empty'),'-d',str(r),str(r/'o.java'),*map(str,paths)],capture_output=True,text=True,timeout=30)
            self.assertEqual(p.returncode,0,p.stderr)
            for n in cr.CLASSES-{'o'}:self.assertFalse((r/(n+'.class')).exists())
            (r/'ShadowCheck.java').write_text('class Parent {public int k=1234;} class Child extends Parent {public byte k=2;} public class ShadowCheck {public static void main(String[]args)throws Exception {Child x=new Child();if(CollectionProbe.F("Parent","k","I").getInt(x)!=1234 || CollectionProbe.F("Child","k","B").getByte(x)!=2)throw new AssertionError();System.out.println("ok");}}')
            p=subprocess.run(['javac','--release','8','-classpath',str(r),'-d',str(r),str(r/'ShadowCheck.java')],capture_output=True,text=True,timeout=20);self.assertEqual(p.returncode,0,p.stderr)
            p=subprocess.run(['java','-cp',str(r),'ShadowCheck'],capture_output=True,text=True,timeout=10);self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(p.stdout.strip(),'ok')

if __name__=='__main__':unittest.main()
