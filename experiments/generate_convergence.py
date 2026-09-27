"""Deterministic binary64 iterates; errors measured against an 80-digit root."""
from pathlib import Path
import csv
from decimal import Decimal, localcontext
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "paper-steward-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ("paper/generated/convergence.csv", "paper/figures/convergence.pdf", "paper/generated/table.tex")

def rows():
    with localcontext() as ctx:
        ctx.prec = 80
        root = Decimal(2).sqrt()
        x, a, b = 2.0, 1.0, 2.0
        result = []
        for n in range(21):
            midpoint = (a + b) / 2
            error = lambda v: float(abs(Decimal.from_float(v) - root))
            result.append((n, x, error(x), midpoint, error(midpoint)))
            x = (x + 2 / x) / 2
            if midpoint * midpoint < 2:
                a = midpoint
            else:
                b = midpoint
        return result

def table(data):
    lines = [r"\begin{tabular}{rrrrr}", r"\toprule", r"$n$ & Newton & Newton error & Bisection & Bisection error \\", r"\midrule"]
    for n, x, e, b, be in data[:6]:
        lines.append(f"{n} & {x:.10f} & {e:.3e} & {b:.10f} & {be:.3e} " + r"\\")
    return "\n".join(lines + [r"\bottomrule", r"\end{tabular}"]) + "\n"

def main():
    data = rows()
    for name in OUTPUTS:
        (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / OUTPUTS[0]).open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "newton", "newton_error", "bisection", "bisection_error"])
        writer.writerows(data)
    (ROOT / OUTPUTS[2]).write_text(table(data))
    plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(6.2, 2.9), layout="constrained")
    for index, label, marker in [(2, "Newton (binary64)", "o"), (4, "Bisection (binary64)", "s")]:
        ax.semilogy([r[0] for r in data], [max(r[index], 1e-18) for r in data], marker=marker, markersize=3, label=label)
    ax.set(xlabel="Iteration index n", ylabel="Absolute error", xlim=(0, 20))
    ax.grid(True, which="major", alpha=.25)
    ax.legend()
    fig.savefig(ROOT / OUTPUTS[1], metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)
    print("Generated CSV, table, and PDF from 21 deterministic rows.")
if __name__ == "__main__":
    main()
