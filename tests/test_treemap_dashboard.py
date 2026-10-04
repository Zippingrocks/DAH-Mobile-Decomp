"""Geometry, rendering, real-schema and evidence integration checks."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
import io
from tools import treemap_dashboard as td


ROWS=[{'original':'a','method_entries':8},{'original':'b','method_entries':46},{'original':'GameMidlet','method_entries':5}]


class TreemapTests(unittest.TestCase):
    def test_all_tiles_present_once(self):
        tiles=td.layout(ROWS)
        self.assertEqual(sorted(t[0]['original'] for t in tiles),['GameMidlet','a','b'])

    def test_area_proportions(self):
        total=sum(c['method_entries'] for c in ROWS);area=td.BOX[2]*td.BOX[3]
        for row,x,y,w,h in td.layout(ROWS):
            self.assertAlmostEqual(w*h/area,row['method_entries']/total,places=10)

    def test_tiles_inside_bounds_and_do_not_overlap(self):
        tiles=td.layout(ROWS);bx,by,bw,bh=td.BOX
        for row,x,y,w,h in tiles:
            self.assertGreaterEqual(x,bx);self.assertGreaterEqual(y,by)
            self.assertLessEqual(x+w,bx+bw+1e-9);self.assertLessEqual(y+h,by+bh+1e-9)
        for i,a in enumerate(tiles):
            for b in tiles[i+1:]:
                overlap_x=max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
                overlap_y=max(0,min(a[2]+a[4],b[2]+b[4])-max(a[2],b[2]))
                self.assertLess(overlap_x*overlap_y,1e-6)

    def test_layout_stable_across_input_order(self):
        self.assertEqual(td.layout(ROWS),td.layout(list(reversed(ROWS))))

    def test_invalid_weights(self):
        for v in (0,-1,True,1.1):
            with self.subTest(v=v),self.assertRaises(ValueError):td.layout([{'original':'x','method_entries':v}])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):td.layout([])

    def test_all_views_valid_svg_and_readable_legend(self):
        for view,(_,legend) in td.VIEWS.items():
            states={r['original']:legend[0][0] for r in ROWS}
            svg=td.svg(ROWS,view,states,'fixture')
            root=ET.fromstring(svg)
            groups=root.findall('.//{http://www.w3.org/2000/svg}g[@data-class]')
            self.assertEqual(len(groups),3)
            for label in (l for s,l,c in legend):self.assertIn(label,svg)
            self.assertGreater(td.BOX[1],209)  # Tiles must not cover summary cards/legend.

    def test_match_colors_are_distinct(self):
        self.assertEqual(len({color for s,l,color in td.VIEWS['byte_match'][1]}),4)

    def test_missing_or_unknown_status_rejected(self):
        for s in ({},{r['original']:'made_up' for r in ROWS}):
            with self.assertRaises(ValueError):td.svg(ROWS,'byte_match',s,'x')

    def test_does_not_mutate_input(self):
        old=deepcopy(ROWS);td.layout(ROWS);self.assertEqual(old,ROWS)

    def test_repository_outputs_are_fresh(self):
        for path,content in td.products(td.ROOT).items():
            self.assertEqual((td.ROOT/path).read_text(encoding='utf-8'),content,path)

    def test_check_mode_does_not_write_stale_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'x.svg').write_text('old')
            with patch.object(td,'ROOT',root),patch.object(td,'products',return_value={'x.svg':'new'}):
                with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                    self.assertEqual(td.main(['--check']),1)
                    self.assertEqual((root/'x.svg').read_text(),'old')
                    self.assertEqual(td.main([]),0)
                    self.assertEqual(td.main(['--check']),0)
