"""Source-map tooling checks; no original game or third-party packages required."""
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import source_map as sm


class SourceMapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = {"id": "fixture", "sha256": "a" * 64, "size_bytes": 10,
                       "entry_class": "Sample",
                       "expected_static_counts": {"class_count": 1, "method_entries": 2}}
        self.data = {
            "schema_version": 1, "target_id": "fixture", "input_sha256": "a" * 64,
            "files": [{"path": "report.md", "kind": "docs", "purpose": "Synthetic evidence."}],
            "classes": [{"original": "Sample", "method_entries": 2, "source_path": None,
                         "recovery": {"state": "not_started", "evidence": []},
                         "build": {"state": "not_tested", "evidence": []},
                         "behavior": {"state": "not_tested", "evidence": []}}],
            "planned": [{"area": "Native build", "state": "not_started", "purpose": "Future work."}],
        }
        (self.root / "report.md").write_text("Synthetic fixture, not game evidence.\n")
        self.tracked = ["report.md"]

    def validate(self, audit=None):
        sm.validate(self.data, self.target, self.root, self.tracked, audit)

    def record(self):
        return [{"path": "report.md", "scope": "Synthetic stage-transition fixture only."}]

    def test_valid_empty_progress(self):
        self.validate()
        output = sm.render(self.data)
        self.assertIn("0 / 1", output)
        self.assertIn("Not recovered", output)
        self.assertIn("not a percentage complete", output)

    def test_duplicate_file_rejected(self):
        self.data["files"] *= 2
        with self.assertRaises(sm.MapError):
            self.validate()

    def test_missing_tracked_metadata_rejected(self):
        self.tracked.append("extra.py")
        with self.assertRaisesRegex(sm.MapError, "Unmapped"):
            self.validate()

    def test_untracked_map_entry_rejected(self):
        self.tracked.clear()
        with self.assertRaisesRegex(sm.MapError, "not tracked"):
            self.validate()

    def test_missing_file_rejected(self):
        (self.root / "report.md").unlink()
        with self.assertRaisesRegex(sm.MapError, "Missing"):
            self.validate()

    def test_unsafe_paths_rejected(self):
        for p in ("", ".", "../private", "/etc/passwd", "C:/secret", "a\\b", "a//b", ".git/config", "a/./b", "x|y"):
            with self.subTest(p=p):
                self.assertFalse(sm.safe_path(p))

    def test_wrong_target_and_hash_rejected(self):
        for field in ("target_id", "input_sha256"):
            with self.subTest(field=field):
                original = self.data[field]
                self.data[field] = "wrong"
                with self.assertRaises(sm.MapError):
                    self.validate()
                self.data[field] = original

    def test_method_and_class_totals_rejected(self):
        self.data["classes"][0]["method_entries"] = 3
        with self.assertRaisesRegex(sm.MapError, "Method total"):
            self.validate()
        self.data["classes"].clear()
        with self.assertRaisesRegex(sm.MapError, "Class count"):
            self.validate()

    def test_duplicate_original_class_rejected(self):
        self.data["classes"] *= 2
        self.target["expected_static_counts"] = {"class_count": 2, "method_entries": 4}
        with self.assertRaisesRegex(sm.MapError, "Duplicate original"):
            self.validate()

    def test_unknown_state_rejected(self):
        self.data["classes"][0]["behavior"]["state"] = "100_percent_accurate"
        with self.assertRaisesRegex(sm.MapError, "Unknown behavior"):
            self.validate()

    def test_claim_requires_evidence(self):
        for stage, state in (("recovery", "raw_output"), ("build", "failed"), ("behavior", "passed_scoped")):
            with self.subTest(stage=stage):
                old = self.data["classes"][0][stage]["state"]
                self.data["classes"][0][stage]["state"] = state
                with self.assertRaisesRegex(sm.MapError, "needs scoped evidence"):
                    self.validate()
                self.data["classes"][0][stage]["state"] = old

    def test_recovery_requires_source_pointer(self):
        c = self.data["classes"][0]
        c["recovery"] = {"state": "raw_output", "evidence": self.record()}
        with self.assertRaisesRegex(sm.MapError, "source-path"):
            self.validate()

    def test_evidence_requires_scope_and_existing_report(self):
        c = self.data["classes"][0]
        c["source_path"] = "recovered/Sample.java"
        for e in ({"path": "report.md", "scope": ""}, {"path": "missing.md", "scope": "test"}):
            c["recovery"] = {"state": "raw_output", "evidence": [e]}
            with self.assertRaisesRegex(sm.MapError, "Evidence"):
                self.validate()

    def test_build_cannot_skip_repair(self):
        c = self.data["classes"][0]
        c["source_path"] = "recovered/Sample.java"
        c["recovery"] = {"state": "raw_output", "evidence": self.record()}
        c["build"] = {"state": "passed", "evidence": self.record()}
        with self.assertRaisesRegex(sm.MapError, "repaired source"):
            self.validate()

    def test_behavior_cannot_skip_build(self):
        c = self.data["classes"][0]
        c["behavior"] = {"state": "passed_scoped", "evidence": self.record()}
        with self.assertRaisesRegex(sm.MapError, "source-only build"):
            self.validate()

    def test_scoped_progress_is_supported_without_publishing_source(self):
        c = self.data["classes"][0]
        c["source_path"] = "src/game/Sample.java"
        for stage, state in (("recovery", "repaired"), ("build", "passed"), ("behavior", "passed_scoped")):
            c[stage] = {"state": state, "evidence": self.record()}
        self.validate()
        self.assertIn("1 / 1", sm.render(self.data))
        self.assertIn("Synthetic stage-transition", sm.render(self.data))
        self.assertFalse((self.root / c["source_path"]).exists())

    def test_planned_area_cannot_claim_implementation(self):
        self.data["planned"][0]["state"] = "implemented"
        with self.assertRaisesRegex(sm.MapError, "planned-only"):
            self.validate()

    def test_audit_crosscheck(self):
        audit = {"input_sha256": "a" * 64, "input_size_bytes": 10,
                 "classes": [{"class": "Sample", "method_entries": 2}]}
        self.validate(audit)
        for key, bad in (("input_sha256", "b" * 64), ("input_size_bytes", 11),
                         ("classes", [{"class": "Other", "method_entries": 2}])):
            with self.subTest(key=key):
                changed = deepcopy(audit); changed[key] = bad
                with self.assertRaises(sm.MapError):
                    self.validate(changed)

    def test_duplicate_json_keys_rejected(self):
        p = self.root / "duplicate.json"
        p.write_text('{"status":1,"status":2}')
        with self.assertRaisesRegex(sm.MapError, "Duplicate JSON"):
            sm.read_json(p)

    def test_render_is_deterministic_and_does_not_mutate(self):
        before = deepcopy(self.data)
        self.assertEqual(sm.render(self.data), sm.render(self.data))
        self.assertEqual(self.data, before)

    def test_tree_groups_directories_and_keeps_plans_out(self):
        entries = [{"path": "tools/x.py", "kind": "tool", "purpose": "x"},
                   {"path": "docs/x.md", "kind": "docs", "purpose": "x"}]
        lines = "\n".join(sm.tree_lines(entries))
        self.assertIn("docs/", lines)
        self.assertIn("x.py [TOOL]", lines)
        self.assertNotIn("Native", lines)
        self.assertEqual(sm.tree_lines(entries), sm.tree_lines(list(reversed(entries))))

    def test_cli_check_catches_stale_output_without_writing(self):
        (self.root / "config").mkdir(); (self.root / "docs").mkdir()
        paths = ["config/target.json", sm.MANIFEST, sm.OUTPUT]
        for p in paths:
            self.data["files"].append({"path": p, "kind": "docs", "purpose": "Fixture."})
        (self.root / "config/target.json").write_text(json.dumps(self.target))
        (self.root / sm.MANIFEST).write_text(json.dumps(self.data))
        output = self.root / sm.OUTPUT; output.write_text("stale")
        with patch.object(sm, "ROOT", self.root), patch.object(sm, "tracked_files", return_value=self.tracked+paths):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(sm.main(["--check"]), 1)
                self.assertEqual(output.read_text(), "stale")
                self.assertEqual(sm.main([]), 0)
                self.assertEqual(sm.main(["--check"]), 0)

    def test_real_git_index_excludes_ignored_and_untracked(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("private/\n")
        (self.root / "private").mkdir(); (self.root / "private/game.jar").write_text("fixture")
        (self.root / "extra.py").write_text("# untracked")
        subprocess.run(["git", "-C", str(self.root), "add", "report.md", ".gitignore"], check=True)
        self.assertEqual(sm.tracked_files(self.root), [".gitignore", "report.md"])

    def test_repository_map_is_current(self):
        data = sm.read_json(sm.ROOT / sm.MANIFEST)
        target = sm.read_json(sm.ROOT / "config/target.json")
        sm.validate(data, target, sm.ROOT, sm.tracked_files(sm.ROOT))
        self.assertEqual(sm.render(data), (sm.ROOT / sm.OUTPUT).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
