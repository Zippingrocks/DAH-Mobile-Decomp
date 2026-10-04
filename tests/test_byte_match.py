"""Independently authored fixtures test comparisons, never DAH game fidelity."""
from copy import deepcopy
from pathlib import Path
import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.classfile import ClassFile, Unsupported
from tools.dah1 import AuditError
from tools import byte_match as bm
from test_dah1 import archive


def fixture(padding=False, literal="hello", debug=False, unknown=False, value=1):
    """Two methods, including an ldc with a constant-pool-dependent operand."""
    pool = []
    def utf(s):
        b = s.encode('utf-8');pool.append(b'\x01'+struct.pack('>H',len(b))+b);return len(pool)
    def cp(tag, index):
        pool.append(bytes([tag])+struct.pack('>H',index));return len(pool)
    if padding:
        utf('unused pool entry')
    this = cp(7, utf('Sample')); parent = cp(7, utf('java/lang/Object'))
    name1, desc1 = utf('number'), utf('()I')
    name2, desc2 = utf('text'), utf('()Ljava/lang/String;')
    code_name, string = utf('Code'), cp(8, utf(literal))
    dbg_name, dbg_value = utf('SourceFile'), utf('Sample.java')
    unknown_name = utf('FutureAttribute')
    u2 = lambda n: struct.pack('>H',n)
    u4 = lambda n: struct.pack('>I',n)
    def code(data):
        payload = u2(1)+u2(0)+u4(len(data))+data+u2(0)+u2(0)
        return u2(code_name)+u4(len(payload))+payload
    m1 = u2(9)+u2(name1)+u2(desc1)+u2(1)+code(bytes([0x10,value,0xac]))
    m2 = u2(9)+u2(name2)+u2(desc2)+u2(1)+code(bytes([0x12,string,0xb0]))
    attrs=[]
    if debug: attrs.append(u2(dbg_name)+u4(2)+u2(dbg_value))
    if unknown: attrs.append(u2(unknown_name)+u4(1)+b'?')
    return (b'\xca\xfe\xba\xbe'+u2(0)+u2(49)+u2(len(pool)+1)+b''.join(pool)+
            u2(0x21)+u2(this)+u2(parent)+u2(0)+u2(0)+u2(2)+m1+m2+u2(len(attrs))+b''.join(attrs))


class MatchTests(unittest.TestCase):
    def test_exact_is_entire_class_file(self):
        self.assertEqual(bm.compare_class(fixture(), fixture())['state'], 'exact_byte_match')

    def test_pool_reordering_is_normalized(self):
        a,b=fixture(),fixture(padding=True)
        self.assertNotEqual(a,b)
        result=bm.compare_class(a,b)
        self.assertEqual(result['state'],'normalized_match')
        self.assertTrue(all(m['state']=='normalized_match' for m in result['methods']))

    def test_different_constant_with_same_instruction_bytes_is_not_match(self):
        self.assertEqual(bm.compare_class(fixture(literal='one'), fixture(literal='two'))['state'],'differences')

    def test_debug_attributes_are_explicitly_ignored(self):
        self.assertEqual(bm.compare_class(fixture(),fixture(debug=True))['state'],'normalized_match')

    def test_literal_instruction_change_is_difference(self):
        self.assertEqual(bm.compare_class(fixture(value=1),fixture(value=2))['state'],'differences')

    def test_unknown_attributes_fail_closed(self):
        r=bm.compare_class(fixture(),fixture(unknown=True))
        self.assertEqual(r['state'],'unverified')
        self.assertIn('Unsupported',r['reason'])

    def test_unknown_identical_bytes_still_match_exactly(self):
        self.assertEqual(bm.compare_class(fixture(unknown=True),fixture(unknown=True))['state'],'exact_byte_match')

    def test_missing_is_unverified(self):
        self.assertEqual(bm.compare_class(fixture(),None)['state'],'unverified')

    def test_truncated_candidate_is_unverified(self):
        self.assertEqual(bm.compare_class(fixture(),fixture()[:-3])['state'],'unverified')

    def test_archive_scope_and_missing_classes(self):
        a=archive([('Sample.class',fixture()),('text.txt',b'one')])
        b=archive([('Sample.class',fixture()),('text.txt',b'two')])
        r=bm.compare_jars(a,b)
        self.assertFalse(r['whole_jar_exact'])
        self.assertEqual(r['class_counts']['exact_byte_match'],1)
        r=bm.compare_jars(a,archive([('text.txt',b'two')]))
        self.assertEqual(r['class_counts']['unverified'],1)

    def test_branch_width_normalization(self):
        c=ClassFile(fixture())
        a,_=c.instructions(bytes([0xa7,0,3,0xb1]))
        b,_=c.instructions(bytes([0xc8,0,0,0,5,0xb1]))
        self.assertEqual(a,b)

    def test_changed_branch_target_is_detected(self):
        c=ClassFile(fixture())
        a,_=c.instructions(bytes([0xa7,0,3,0x00,0xb1]))
        b,_=c.instructions(bytes([0xa7,0,4,0x00,0xb1]))
        self.assertNotEqual(a,b)

    def test_bad_branch_target_is_rejected(self):
        with self.assertRaises(Unsupported):
            ClassFile(fixture()).instructions(bytes([0xa7,0,2,0xb1]))

    def test_reserved_opcode_is_rejected(self):
        with self.assertRaises(Unsupported):
            ClassFile(fixture()).instructions(b'\xca')

    def test_ldc_width_normalization(self):
        c=ClassFile(fixture())
        index=next(i for i,p in enumerate(c.pool) if p is not None and p[0]==8)
        a,_=c.instructions(bytes([0x12,index,0xb0]))
        b,_=c.instructions(bytes([0x13,0,index,0xb0]))
        self.assertEqual(a,b)

    def test_truncations_never_normalize(self):
        a=fixture()
        for size in range(len(a)):
            with self.subTest(size=size):
                self.assertEqual(bm.compare_class(a,a[:size])['state'],'unverified')

    def test_report_hash_guard(self):
        jar=archive([('Sample.class',fixture())]);report=bm.compare_jars(jar,jar)
        target={'sha256':bm.digest(jar)};manifest={'classes':[{'original':'Sample','method_entries':2}]}
        report['context_sha256']='a'*64
        bm.validate_report(report,manifest,target)
        report['classes'][0]['rebuilt_sha256']='0'*64
        with self.assertRaises(AuditError):bm.validate_report(report,manifest,target)

    def test_context_and_source_evidence_gate(self):
        jar=archive([('Sample.class',fixture())]);report=bm.compare_jars(jar,jar)
        manifest={'files':[{'path':'report.json'}], 'classes':[{
            'original':'Sample','method_entries':2,'recovery':{'state':'not_started','evidence':[]},
            'build':{'state':'not_tested','evidence':[]},'behavior':{'state':'not_tested','evidence':[]}}]}
        target={'sha256':bm.digest(jar)}
        report['context_sha256']='a'*64
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir()
            (root/'config/byte_match.json').write_text(json.dumps({'schema_version':1,'report':'report.json'}))
            (root/'report.json').write_text(json.dumps(report))
            with patch.object(bm,'context',return_value='a'*64):
                states,note=bm.dashboard_states(root,manifest,target)
                self.assertEqual(states['Sample'],'unverified')
                self.assertIn('withheld',note)
                manifest['classes'][0]['recovery']['state']='repaired'
                manifest['classes'][0]['build']['state']='passed'
                self.assertEqual(bm.dashboard_states(root,manifest,target)[0]['Sample'],'exact_byte_match')
            with patch.object(bm,'context',return_value='b'*64):
                states,note=bm.dashboard_states(root,manifest,target)
                self.assertEqual(states['Sample'],'unverified');self.assertIn('STALE',note)

    @unittest.skipUnless(shutil.which('javac'), 'JDK not available; independent compiled fixture check skipped')
    def test_independently_compiled_debug_and_control_flow(self):
        source='''public class Sample {
          static final int MAGIC = 7;
          public static int f(int x) {
            try { switch(x) { case 0: return 3; case 1: return 4; case 2: return 5;
              default: return 8 / x; } } catch (ArithmeticException e) { return -1; }
          }
          public static int sparse(int x) {
            switch(x) { case 2: return 20; case 70: return 30; default: return 40; }
          }
        }'''
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'Sample.java';path.write_text(source)
            variants=[]
            for name,flag in [('debug','-g'),('nodebug','-g:none')]:
                out=root/name;out.mkdir()
                subprocess.run(['javac','--release','8',flag,'-d',str(out),str(path)],check=True,capture_output=True,timeout=30)
                variants.append((out/'Sample.class').read_bytes())
            self.assertEqual(bm.compare_class(*variants)['state'],'normalized_match')
            path.write_text(source.replace('MAGIC = 7','MAGIC = 8'))
            subprocess.run(['javac','--release','8','-g:none','-d',str(root/'changed'),str(path)],check=True,capture_output=True,timeout=30)
            self.assertEqual(bm.compare_class(variants[1],(root/'changed/Sample.class').read_bytes())['state'],'differences')
