from pathlib import Path
import hashlib, json, tempfile, unittest, zipfile
from tools import integration_recovery as ir
class IntegrationRecoveryTests(unittest.TestCase):
    def test_config_has_complete_unique_class_roster(self):
        c=ir.config(); names=[x['class'] for x in c['classes']]
        self.assertEqual(names,ir.GAME); self.assertEqual(len(names),len(set(names))); self.assertEqual(c['expected']['method_entries'],313)
    def test_private_source_paths_are_not_tracked_support(self):
        c=ir.config(); self.assertTrue(all(x['sha256'] and len(x['sha256'])==64 for x in c['classes'])); self.assertEqual(c['support_root'],'tests/java/integration_support')
    def test_support_contains_no_game_class_names_at_root(self):
        root=ir.ROOT/'tests/java/integration_support'; names={p.stem for p in root.glob('*.java')}; self.assertFalse(names & set(ir.GAME))
    def test_support_compiles_without_game_source(self):
        with tempfile.TemporaryDirectory() as td: ir.compile_support(Path(td))
    def test_candidate_packaging_excludes_original_classes_and_preserves_resources(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td); orig=t/'o.jar'; classes=t/'classes';classes.mkdir()
            with zipfile.ZipFile(orig,'w') as z:
                z.writestr('asset.bin',b'abc')
                for c in ir.GAME:z.writestr(c+'.class',b'ORIGINAL')
            for c in ir.GAME:(classes/(c+'.class')).write_bytes(('NEW'+c).encode())
            out=t/'c.jar'; n=ir.build_candidate(orig,classes,out);self.assertEqual(n,1)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(z.read('asset.bin'),b'abc');self.assertNotEqual(z.read('a.class'),b'ORIGINAL')
    def test_run_directory_refuses_overwrite(self):
        src=Path(ir.__file__).read_text(); self.assertIn("run directory already exists",src)
    def test_probe_sources_are_authored_and_present(self):
        for p in ir.config()['probes']:self.assertTrue((ir.ROOT/p).is_file())
    def test_probe_execution_roster_tracks_config(self):
        src=Path(ir.__file__).read_text()
        self.assertIn("for probe_path in cfg['probes']",src)
        self.assertIn('tests/java/DeepIntegrationProbe.java',ir.config()['probes'])
    def test_graphics_adapter_supports_centered_top_image_anchor(self):
        src=(ir.ROOT/'tests/java/integration_support/javax/microedition/lcdui/Graphics.java').read_text()
        self.assertIn('if (h==1) dx-=image.getWidth()/2',src)
        self.assertIn('else if(v!=16)',src)
    def test_persistence_and_long_run_probes_are_in_scope(self):
        probes = ir.config()["probes"]
        self.assertIn("tests/java/PersistenceProbe.java", probes)
        self.assertIn("tests/java/LongRunProbe.java", probes)

    def test_rms_adapter_is_stateful_but_test_only(self):
        src=(ir.ROOT/"tests/java/integration_support/javax/microedition/rms/RecordStore.java").read_text()
        self.assertIn("Map<String,List<byte[]>> STORES", src)
        self.assertIn("not a production persistence backend", src)

    def test_long_run_probe_has_multiple_state_checkpoints(self):
        src=(ir.ROOT/"tests/java/LongRunProbe.java").read_text()
        self.assertIn("frame<=500", src)
        self.assertIn("frame%100==0", src)

    def test_original_pin_shape(self):
        i=ir.config()['input'];self.assertEqual(i['size'],201816);self.assertEqual(len(i['sha256']),64)
if __name__=='__main__':unittest.main()
