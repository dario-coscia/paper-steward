# Evaluator verification

Checked locally on 2026-09-27 with Python from the existing Anaconda environment,
Matplotlib 3.7.0, and installed latexmk/pdflatex. No packages were installed.

- `python -m unittest discover -s benchmark -p 'test_*.py' -v`: six tests pass.
- Matched candidates have identical paper, experiment, tools and tests; only agent
  customization differs. Workshop branch/tag refs remain unchanged by preparation.
- Untouched broken fixture scores zero of ten repairs and fails readiness.
- A mechanically repaired fixture scores ten of ten and passes an actual trusted
  LaTeX build. It is an evaluator fixture, not a measured agent run.
- Incorrect report claims are detected. Changed candidate check scripts are flagged
  without executing those scripts. Modified external oracle scripts are rejected.
- Deleted intended sections do not count as repaired inclusion.
- CLI prepare/start/finish/score/summarize smoke test produces result.json, a real
  failed compilation log for the broken fixture, and results.csv. Expected score
  exit is 1; unavailable metrics stay null/blank.
- `git diff --check`: no whitespace errors.

No real Codex sessions were benchmarked. Mathematical claim preservation and
whether outputs were produced through the generator require a transcript/diff
review. Tool calls, tokens and human interventions are recorded manually; only
elapsed time is automatic. Exact artifact bytes require the same plotting environment.
