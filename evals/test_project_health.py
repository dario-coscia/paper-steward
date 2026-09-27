from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("health", ROOT / "scripts/project_health.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

class HealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in health.REQUIRED + health.OUTPUTS:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("")
        shutil.copy(ROOT / "evals/fixtures/healthy/main.tex", self.root / "paper/main.tex")
        section = self.root / "paper/sections/body.tex"
        section.parent.mkdir()
        shutil.copy(ROOT / "evals/fixtures/healthy/body.tex", section)
        (self.root / "paper/references.bib").write_text("@book{example, title={Example}}")
        self.provenance()
    def provenance(self):
        (self.root / "paper/generated/provenance.json").write_text(json.dumps({n: health.digest(self.root / n) for n in ("experiments/generate_convergence.py", *health.OUTPUTS)}))
    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/project_health.py"), "--root", str(self.root), "--no-build", *args], capture_output=True, text=True)
    def test_healthy_exit(self):
        self.assertEqual(health.check(self.root, False), ([], []))
        self.assertEqual(self.cli("--strict").returncode, 0)
    def test_unhealthy_fixture(self):
        shutil.copy(ROOT / "evals/fixtures/unhealthy/body.tex", self.root / "paper/sections/body.tex")
        errors, _ = health.check(self.root, False)
        for code in ("duplicate-label", "undefined-reference", "undefined-citation", "missing-figure", "pending-marker"):
            self.assertTrue(any(e.startswith(code) for e in errors), code)
        self.assertEqual(self.cli().returncode, 1)
    def test_missing_and_omitted(self):
        (self.root / "paper/macros.tex").unlink()
        (self.root / "paper/sections/extra.tex").write_text("Extra")
        errors, _ = health.check(self.root, False)
        self.assertTrue(any(e.startswith("missing-file") for e in errors))
        self.assertTrue(any(e.startswith("omitted-section") for e in errors))
    def test_artifacts_present_and_tracked(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        p = self.root / "paper/main.aux"
        p.write_text("aux")
        subprocess.run(["git", "add", "paper/main.aux"], cwd=self.root, check=True)
        errors, _ = health.check(self.root, False)
        self.assertTrue(any(e.startswith("present-artifact") for e in errors))
        self.assertTrue(any(e.startswith("tracked-artifact") for e in errors))
    def test_stale_and_strict_exit(self):
        os.utime(self.root / health.OUTPUTS[0], (1, 1))
        self.assertEqual(self.cli().returncode, 0)
        self.assertEqual(self.cli("--strict").returncode, 1)
    def test_provenance_content_change(self):
        (self.root / health.OUTPUTS[0]).write_text("altered")
        errors, _ = health.check(self.root, False)
        self.assertTrue(any(e.startswith("provenance") for e in errors))
    def test_compiler_failure(self):
        from unittest.mock import patch
        fake = subprocess.CompletedProcess([], 1, "build failed", "")
        original = subprocess.run
        def run(args, **kwargs):
            return fake if args[0] == "sh" else original(args, **kwargs)
        with patch.object(health.shutil, "which", return_value="available"), patch.object(health.subprocess, "run", side_effect=run):
            errors, _ = health.check(self.root, True)
        self.assertTrue(any(e.startswith("compilation") for e in errors))
    def test_missing_compiler_warning(self):
        from unittest.mock import patch
        with patch.object(health.shutil, "which", return_value=None):
            _, warnings = health.check(self.root, True)
        self.assertTrue(any(w.startswith("compiler-unavailable") for w in warnings))
if __name__ == "__main__": unittest.main()
