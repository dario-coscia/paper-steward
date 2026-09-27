# Local verification evidence

Verified on 2026-09-27 using an existing environment; no packages were installed
and no system configuration was changed. Codex CLI is 0.157.0, Matplotlib 3.7.0,
LaTeX is TeX Live 2021 with latexmk 4.70b. The shell's default python3 lacks
Matplotlib, so experiment/eval commands used the existing interpreter
`/Users/dariocoscia/anaconda3/bin/python`. This path is local evidence only;
project scripts and documented usage do not depend on it.

| Command/check | Observed result |
| --- | --- |
| `python experiments/generate_convergence.py` | 21 deterministic rows; CSV, generated table, PDF and hash manifest regenerated |
| `python -m unittest discover -s evals -v` | All 17 tests pass: health fixtures, exits, compiler handling, numerical invariants, CSV/table consistency and hook contracts |
| `sh scripts/build.sh` | Exit 0, complete four-page PDF in build/main.pdf; final log has no LaTeX warnings or overfull boxes |
| `python scripts/project_health.py --strict` | Exit 0, zero failures and zero warnings; includes an independent fresh build |
| `python scripts/build_evidence.py check` | Exit 0; source, PDF and log hashes match the build receipt |
| Skill Creator `quick_validate.py` | Skill valid, using existing Python with PyYAML |
| `git diff --check` and `git diff --cached --check` | No whitespace errors |
| `python scripts/verify_stages.py` | Six distinct consecutive commits and exactly six annotated tags; final HEAD Stage 5 |
| Git status / remote / tracked auxiliaries | Clean main branch; no remote; no tracked LaTeX auxiliaries |

The first final-stage build exposed older BibTeX rejecting absolute output paths.
The build now uses latexmk's `-bibfudge` option and explicit bibliography search
path, with a portable C locale. Subsequent builds and fresh strict compilation
succeeded. The pdflatex/bibtex fallback is provided, but this verification used
latexmk; it does not claim a separate fallback execution.

Ghostscript rendered all four PDF pages at 90 dpi, and each page was visually
inspected: readable title and sections, complete proof, correct equation numbering,
consistent numerical table, log-scale convergence figure, conclusion and bibliography.
No clipped text, missing glyphs or unresolved reference placeholders were observed.
The full PDF and rendered pages are local build/temporary artifacts, not tracked.

Stages 3 and 4 were intentionally checked before repair. Eight checker tests passed
at Stage 3; strict health returned exit 1 with the planted source problems and a
real missing-figure compilation failure. Stage 4's Stop hook returned a block on
that unhealthy state. Final Stage 5 has repaired every historical inventory item.

The mathematical proof was reviewed algebraically: positivity and strict upper
invariance follow from the exact error identity; strict decrease follows from
(2-x_n^2)/(2x_n); bounded monotonicity and continuity identify the positive limit.
The error ratio tends to 1/(2 sqrt(2)). Tests illustrate selected numerical
invariants; neither tests nor compilation certify mathematical truth.

No required verification executable was missing. Hooks were checked by fixture and
stdin contracts, not through a live authenticated Codex session. Hook trust remains
an explicit user review step. GitHub Actions is configured but has not run remotely.
The checker supports the project's literal TeX conventions and is not a general
TeX interpreter or security boundary. Rendering may vary across library versions.
