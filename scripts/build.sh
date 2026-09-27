#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=${PAPER_BUILD_DIR:-"$ROOT/build"}
mkdir -p "$OUT"
cd "$ROOT/paper"
if command -v latexmk >/dev/null 2>&1; then
    latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$OUT" main.tex
elif command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" main.tex
    (cd "$OUT" && BIBINPUTS="$ROOT/paper:" bibtex main)
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" main.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" main.tex
else
    echo 'Missing supported compiler: install latexmk + pdflatex, or pdflatex + bibtex. Build unverified.' >&2
    exit 2
fi
printf 'Built %s/main.pdf\n' "$OUT"

python3 "$ROOT/scripts/build_evidence.py" record "$OUT"
