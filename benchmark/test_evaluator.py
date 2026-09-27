"""Fixture evaluations only: no model sessions or claimed agent results."""
import argparse
from contextlib import redirect_stdout
import io
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('evaluator', HERE / 'evaluate.py')
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)

class EvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='steward-eval-fixtures-')
        cls.template = Path(cls.temp.name) / 'template'
        cls.refs = evaluator.git('show-ref', '--heads', '--tags')
        with redirect_stdout(io.StringIO()):
            evaluator.prepare(argparse.Namespace(runs=cls.template, pairs=1))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.run_dir = Path(tempfile.mkdtemp(prefix='steward-eval-test-'))
        self.addCleanup(shutil.rmtree, self.run_dir)
        shutil.copytree(self.template, self.run_dir, dirs_exist_ok=True)
        self.case = self.run_dir / '01-baseline'

    def start(self):
        with redirect_stdout(io.StringIO()):
            evaluator.start(argparse.Namespace(case=self.case))

    def score(self):
        with redirect_stdout(io.StringIO()):
            code = evaluator.score(argparse.Namespace(case=self.case))
        return code, evaluator.read_json(self.case / 'result.json')

    def repair_fixture(self):
        self.start()
        work = self.case / 'workspace'
        trusted = self.run_dir / '_evaluator/complete'
        shutil.rmtree(work / 'paper')
        shutil.copytree(trusted / 'paper', work / 'paper')
        # Removing the intentionally tracked auxiliary is part of the fixture repair.
        evaluator.run(['git', 'rm', '--cached', 'paper/main.aux'], work)
        shutil.copy2(trusted / 'README.md', work / 'README.md')
        for name in evaluator.OUTPUTS:
            os.utime(work / name, None)
        report = evaluator.read_json(self.case / 'report.json')
        report['claims'] = {name: True for name in evaluator.CLAIMS}
        evaluator.write_json(self.case / 'report.json', report)
        evaluator.write_json(self.case / 'review.json', {'claims_preserved': True, 'generated_outputs_from_script': True,
                                                       'notes': 'Mechanically repaired test fixture; not an agent score.'})

    def test_matched_paper_and_tools(self):
        base = self.run_dir / '01-baseline/workspace'
        steward = self.run_dir / '01-steward/workspace'
        for folder in ('paper', 'experiments', 'scripts', 'evals'):
            for p in (base / folder).rglob('*'):
                if p.is_file():
                    self.assertEqual(p.read_bytes(), (steward / p.relative_to(base)).read_bytes())
        self.assertFalse((base / 'AGENTS.md').exists())
        self.assertTrue((steward / 'AGENTS.md').exists())
        self.assertEqual(evaluator.git('show-ref', '--heads', '--tags'), self.refs)

    def test_broken_fixture_fails(self):
        self.start()
        code, result = self.score()
        self.assertEqual(code, 1)
        self.assertEqual(result['repairs_resolved'], 0)
        self.assertFalse(result['objective_submission_ready'])
        self.assertIsNone(result['efficiency']['tokens'])

    def test_repaired_fixture_and_reporting_mismatch(self):
        self.repair_fixture()
        code, result = self.score()
        self.assertEqual(result['repairs_resolved'], 10)
        if result['facts']['compiled'] is None:
            self.assertEqual(code, 1)
        else:
            self.assertTrue(result['facts']['compiled'], (self.case / 'build.log').read_text()[-3000:])
            self.assertEqual(code, 0, result)
        report = evaluator.read_json(self.case / 'report.json')
        report['claims']['table_consistent'] = False
        evaluator.write_json(self.case / 'report.json', report)
        _, rescored = self.score()
        self.assertIn('table_consistent', rescored['reporting']['mismatches'])
        self.assertEqual(result['efficiency']['elapsed_seconds'], rescored['efficiency']['elapsed_seconds'])

    def test_modified_checks_are_flagged_not_executed(self):
        self.start()
        p = self.case / 'workspace/scripts/project_health.py'
        p.write_text('raise RuntimeError("candidate checker must not run")\n')
        _, result = self.score()
        self.assertIn('scripts/project_health.py', result['safety']['changed_checks_or_guidance'])

    def test_protected_oracle_tamper_rejected(self):
        (self.run_dir / '_evaluator/complete/scripts/build.sh').write_text('bad')
        with self.assertRaisesRegex(ValueError, 'External evaluator modified'):
            self.score()

    def test_missing_intended_section_is_not_repair(self):
        self.start()
        (self.case / 'workspace/paper/sections/conclusion.tex').unlink()
        _, result = self.score()
        self.assertFalse(result['repairs']['omitted_section'])
        self.assertIn('missing-intended-section: conclusion', result['failures'])

if __name__ == '__main__':
    unittest.main()
