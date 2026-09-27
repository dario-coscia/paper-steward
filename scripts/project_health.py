"""Static checks for this project's literal LaTeX conventions; not a TeX parser."""
from pathlib import Path
import argparse
from collections import Counter
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

REQUIRED = ("paper/main.tex", "paper/macros.tex", "paper/references.bib",
            "experiments/generate_convergence.py", "scripts/build.sh")
ARTIFACTS = {".aux", ".log", ".out", ".toc", ".bbl", ".blg", ".fls", ".fdb_latexmk", ".synctex.gz"}
OUTPUTS = ("paper/generated/convergence.csv", "paper/figures/convergence.pdf", "paper/generated/table.tex")

def clean(text):
    return re.sub(r"(?<!\\)%[^\n]*", "", text)

def commands(text, name):
    return re.findall(r"\\(?:" + name + r")\*?(?:\s*\[[^\]]*\])*\s*\{([^{}]+)\}", text)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(root, compile_paper=True):
    root = Path(root).resolve()
    failures, warnings = [], []
    def fail(code, message): failures.append(f"{code}: {message}")
    for name in REQUIRED:
        if not (root / name).is_file(): fail("missing-file", name)
    paper = root / "paper"
    active = {}
    def visit(path):
        path = path.resolve()
        if path in active: return
        if not path.is_relative_to(paper.resolve()):
            fail("include-path", str(path)); return
        if not path.is_file():
            fail("missing-input", str(path.relative_to(root))); return
        text = path.read_text()
        active[path] = clean(text)
        for target in commands(clean(text), "input|include"):
            visit(paper / (target if Path(target).suffix else target + ".tex"))
    visit(paper / "main.tex")
    for p in sorted((paper / "sections").glob("*.tex")):
        if p.resolve() not in active: fail("omitted-section", str(p.relative_to(root)))
    text = "\n".join(active.values())
    labels = commands(text, "label")
    counts = Counter(labels)
    for label, count in counts.items():
        if count > 1: fail("duplicate-label", label)
    for value in commands(text, "ref|eqref|autoref|pageref|cref|Cref"):
        for key in value.split(","):
            if key.strip() not in counts: fail("undefined-reference", key.strip())
    bib = "\n".join(p.read_text() for p in paper.glob("*.bib"))
    keys = set(re.findall(r"@(?!(?:comment|string|preamble)\b)\w+\s*\{\s*([^,\s]+)", bib, re.I))
    for value in commands(text, "cite|citep|citet|nocite"):
        for key in value.split(","):
            if key.strip() != "*" and key.strip() not in keys: fail("undefined-citation", key.strip())
    for target in commands(text, "includegraphics"):
        p = paper / target
        options = [p] if p.suffix else [p.with_suffix(s) for s in (".pdf", ".png", ".jpg", ".eps")]
        if not any(p.is_file() for p in options): fail("missing-figure", target)
    for p in sorted(paper.rglob("*")):
        if p.is_file() and p.suffix in {".tex", ".bib"}:
            for line, content in enumerate(p.read_text().splitlines(), 1):
                if re.search(r"\b(?:TODO|FIXME)\b", content): fail("pending-marker", f"{p.relative_to(root)}:{line}")
            if p.parent.name == "sections" and r"\sqrt{2}" in clean(p.read_text()):
                fail("shared-macro", f"{p.relative_to(root)}: use \\rtwo")
    def artifact(p): return any(str(p).endswith(s) for s in ARTIFACTS)
    for p in paper.rglob("*"):
        if p.is_file() and artifact(p): fail("present-artifact", str(p.relative_to(root)))
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True)
    if tracked.returncode == 0:
        for name in tracked.stdout.split("\0"):
            if artifact(name): fail("tracked-artifact", name)
    experiment = root / "experiments/generate_convergence.py"
    for name in OUTPUTS:
        p = root / name
        if not p.is_file(): fail("missing-generated", name)
        elif experiment.exists() and p.stat().st_mtime < experiment.stat().st_mtime:
            warnings.append(f"timestamp-stale: {name}; regenerate (Git checkout timestamps are not provenance)")
    manifest = root / "paper/generated/provenance.json"
    if manifest.exists():
        try:
            hashes = json.loads(manifest.read_text())
            for name in ("experiments/generate_convergence.py", *OUTPUTS):
                p = root / name
                if not p.exists() or hashes.get(name) != digest(p): fail("provenance", name)
        except (ValueError, OSError) as e: fail("provenance", str(e))
    else:
        warnings.append("provenance: no source/output hash manifest; freshness relies on timestamps")
    if compile_paper:
        if shutil.which("pdflatex") and (shutil.which("latexmk") or shutil.which("bibtex")):
            with tempfile.TemporaryDirectory(prefix="paper-steward-build-") as out:
                import os
                env = dict(os.environ, PAPER_BUILD_DIR=out)
                try:
                    proc = subprocess.run(["sh", str(root / "scripts/build.sh")], cwd=root, env=env,
                                          capture_output=True, text=True, timeout=90)
                    if proc.returncode: fail("compilation", proc.stdout[-1800:] + proc.stderr[-600:])
                    log = Path(out) / "main.log"
                    if log.exists():
                        for line in log.read_text(errors="replace").splitlines():
                            if "Warning:" in line or "Overfull" in line: warnings.append("latex: " + line)
                except (OSError, subprocess.TimeoutExpired) as e: fail("compilation", str(e))
        else:
            warnings.append("compiler-unavailable: need pdflatex and latexmk or bibtex; compilation unverified")
    return failures, warnings

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--strict", action="store_true", help="Treat warnings, including skipped compilation, as failure")
    parser.add_argument("--no-build", action="store_true", help="Static checks only; does not verify compilation")
    args = parser.parse_args(argv)
    failures, warnings = check(args.root, not args.no_build)
    for item in failures: print("FAIL " + item)
    for item in warnings: print("WARN " + item)
    result = bool(failures or (args.strict and warnings))
    print(f"Health: {len(failures)} failures, {len(warnings)} warnings; " + ("FAIL" if result else "PASS") + (" (static only)" if args.no_build else ""))
    return int(result)
if __name__ == "__main__":
    raise SystemExit(main())
