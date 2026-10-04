"""Independent tooling tests; no DAH inputs, assets or recovered source needed."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from tools import subsystem_recovery as sr

ROOT = Path(__file__).resolve().parents[1]


def cp_fixture(names):
    pool = b"".join(b"\x01"+struct.pack(">H",len(n))+n for n in names)
    return b"\xca\xfe\xba\xbe\x00\x00\x00\x34"+struct.pack(">H",len(names)+1)+pool+b"unchanged-test-tail"


class SubsystemRecoveryTests(unittest.TestCase):
    def test_alias_b_names_only(self):
        data=cp_fixture([b"b",b"primary",b"fallback",b"Lj;",b"Lf;"])
        want=cp_fixture([b"b",b"a",b"a",b"Lj;",b"Lf;"])
        self.assertEqual(sr.alias_test_fields(data,sr.TEST_ALIASES["b.class"]),want)
        self.assertIn(b"primary",data)

    def test_alias_k_names_only(self):
        data=cp_fixture([b"k",b"width",b"height",b"rng",b"I",b"Ljava/util/Random;"])
        want=cp_fixture([b"k",b"a",b"b",b"a",b"I",b"Ljava/util/Random;"])
        self.assertEqual(sr.alias_test_fields(data,sr.TEST_ALIASES["k.class"]),want)

    def test_missing_alias_fails(self):
        with self.assertRaises(sr.RecoveryError):sr.alias_test_fields(cp_fixture([b"width"]),sr.TEST_ALIASES["k.class"])

    def test_duplicate_alias_fails(self):
        with self.assertRaises(sr.RecoveryError):sr.alias_test_fields(cp_fixture([b"primary",b"primary",b"fallback"]),sr.TEST_ALIASES["b.class"])

    def test_bad_test_class_fails(self):
        for data in (b"",b"not-a-class",b"\xca\xfe\xba\xbe"):
            with self.subTest(data=data),self.assertRaises(sr.RecoveryError):sr.alias_test_fields(data,{"x":"a"})

    def test_truncated_constant_pool_fails(self):
        data=cp_fixture([b"primary",b"fallback"])
        for cut in range(10,len(data)-len(b"unchanged-test-tail")):
            with self.subTest(cut=cut),self.assertRaises(sr.RecoveryError):sr.alias_test_fields(data[:cut],sr.TEST_ALIASES["b.class"])

    def test_unknown_constant_fails(self):
        data=bytearray(cp_fixture([b"primary",b"fallback"]));data[10]=255
        with self.assertRaises(sr.RecoveryError):sr.alias_test_fields(bytes(data),sr.TEST_ALIASES["b.class"])

    def test_method_return_alias_is_explicit(self):
        source='  public final byte encodedByte(int, int);\n    descriptor: (II)B\n  public final int a(int, int);\n    descriptor: (II)I\n'
        aliases=[dict(owner="l",source_name="encodedByte",original="a",descriptor="(II)B")]
        self.assertEqual(sr.normalized_inventory(source,"l",aliases,True),[("a","(II)B"),("a","(II)I")])
        self.assertEqual(sr.normalized_inventory(source,"l",aliases,False)[0],("encodedByte","(II)B"))

    def test_other_owner_not_renamed(self):
        source='  public final byte encodedByte(int, int);\n    descriptor: (II)B\n'
        aliases=[dict(owner="l",source_name="encodedByte",original="a",descriptor="(II)B")]
        self.assertEqual(sr.normalized_inventory(source,"g",aliases,True)[0][0],"encodedByte")

    def test_resources_are_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(sr.RecoveryError):sr.resource_fixtures(Path(tmp),{"../oops":b"x"})

    def test_resource_fixture_short_font_rejected(self):
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(sr.RecoveryError):
            sr.resource_fixtures(Path(tmp),{k:b"" for k in sr.RESOURCES})

    def test_fixture_determinism_and_no_game_bytes(self):
        data={n:b"authored" for n in sr.RESOURCES};data["fnt1.font"]=bytes(range(256))+bytes(range(100));data["en.bin"]=bytes(range(70))
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"a",Path(tmp)/"b";sr.resource_fixtures(a,data);sr.resource_fixtures(b,data)
            files=[p.relative_to(a)for p in a.rglob('*')if p.is_file()]
            self.assertGreater(len(files),400)
            for p in files:self.assertEqual((a/p).read_bytes(),(b/p).read_bytes())
            self.assertEqual((a/"audio/empty.mid").read_bytes(),b"")
            self.assertEqual((a/"font-cuts/355").read_bytes(),data["fnt1.font"][:355])

    def test_manifest_scope_and_private_snapshot_hashes(self):
        config=json.loads((ROOT/sr.CONFIG).read_text())
        self.assertEqual({c['original']for c in config['components']},{'e','s','t','g','l','q'})
        self.assertEqual(sum(c['method_entries']for c in config['components']),58)
        for c in config['components']:
            self.assertRegex(c['source_sha256'],r'^[0-9a-f]{64}$')
        self.assertEqual(set(config['resource_hashes']),set(sr.RESOURCES))
        for name in config['support_sources']:
            self.assertTrue(name.startswith('tests/java/'))
            self.assertTrue((ROOT/name).is_file())

    @unittest.skipUnless(shutil.which('javac') and shutil.which('java') and shutil.which('javap'),'JDK required')
    def test_probes_compile_without_game_and_double_aliases_resolve(self):
        config=json.loads((ROOT/sr.CONFIG).read_text())
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            result=subprocess.run(['javac','--release','8','-g:none','-d',str(out),*[str(ROOT/p)for p in config['support_sources']]],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            for name in ('e','s','t','g','l','q'):self.assertFalse((out/(name+'.class')).exists())
            for name,aliases in sr.TEST_ALIASES.items():
                p=out/name;p.write_bytes(sr.alias_test_fields(p.read_bytes(),aliases))
            java='''import java.lang.reflect.*; public class AliasSmoke {public static void main(String[]x)throws Exception{
              Class<?> b=Class.forName("b"),k=Class.forName("k");int count=0;
              for(Field f:b.getDeclaredFields())if(f.getName().equals("a"))count++;
              for(Field f:k.getDeclaredFields())if(f.getName().equals("a"))count++;
              if(count!=4)throw new AssertionError(count); System.out.println("ok");}}'''
            p=out/'AliasSmoke.java';p.write_text(java)
            subprocess.run(['javac','--release','8','-d',str(out),str(p)],capture_output=True,check=True,timeout=20)
            result=subprocess.run(['java','-cp',str(out),'AliasSmoke'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'ok')

    def test_runner_refuses_missing_private_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir()
            cfg=json.loads((ROOT/sr.CONFIG).read_text())
            target={'id':cfg['target_id'],'filename':'authored.jar','size_bytes':1,'sha256':sr.sha(b'x')}
            (root/'config/target.json').write_text(json.dumps(target));(root/sr.CONFIG).write_text(json.dumps(cfg))
            (root/'inputs/original').mkdir(parents=True);(root/'inputs/original/authored.jar').write_bytes(b'x')
            with self.assertRaises(sr.RecoveryError):sr.run(root,root/'results')
            self.assertFalse((root/'results').exists())

if __name__=='__main__':unittest.main()
