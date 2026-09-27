from pathlib import Path
import csv
from decimal import Decimal, localcontext
import importlib.util
import math
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("experiment", ROOT / "experiments/generate_convergence.py")
experiment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(experiment)

class ExperimentTests(unittest.TestCase):
    def test_parameters_and_recurrence(self):
        data = experiment.rows()
        self.assertEqual(len(data), 21)
        self.assertEqual(data[0][1], 2)
        self.assertEqual(data[0][3], 1.5)
        self.assertEqual(data[1][1], 1.5)
        a, b = 1., 2.
        for i, row in enumerate(data):
            n, x, error, midpoint, be = row
            self.assertEqual(n, i)
            self.assertEqual(midpoint, (a+b)/2)
            self.assertLessEqual(be, 2**(-n-1) + 1e-15)
            if midpoint*midpoint < 2: a = midpoint
            else: b = midpoint
            if i: self.assertEqual(x, (data[i-1][1] + 2/data[i-1][1])/2)
            self.assertTrue(math.isfinite(error) and error > 0)
        self.assertLess(data[5][2], 2e-16)
    def test_exact_identity_and_monotonicity(self):
        with localcontext() as ctx:
            ctx.prec = 70
            alpha, x = Decimal(2).sqrt(), Decimal(2)
            for _ in range(6):
                nxt = (x + 2/x)/2
                self.assertGreater(nxt, alpha)
                self.assertLess(nxt, x)
                self.assertLess(abs((nxt-alpha) - (x-alpha)**2/(2*x)), Decimal('1e-68'))
                x = nxt
    def test_tracked_csv_and_table_match_generator(self):
        data = experiment.rows()
        with (ROOT / "paper/generated/convergence.csv").open() as f:
            reader = csv.reader(f)
            self.assertEqual(next(reader), ['n','newton','newton_error','bisection','bisection_error'])
            saved = [tuple(float(v) for v in row) for row in reader]
        self.assertEqual(saved, data)
        self.assertEqual((ROOT / "paper/generated/table.tex").read_text(), experiment.table(data))
if __name__ == "__main__": unittest.main()
