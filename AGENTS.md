# Paper Steward project rules

Maintain the paper safely; never claim to prove mathematical truth through compilation.
Read the relevant skill before paper maintenance. Inspect the initial Git status.

Sources: `paper/main.tex`, `paper/sections/*.tex`, `paper/macros.tex`,
`paper/references.bib`, and `experiments/generate_convergence.py` are authoritative.
Use shared `\rtwo` and `\err` notation, theorem environments, descriptive labels,
and `\eqref` for equations. Update every reference when renaming a label.
Keep citation keys in the bibliography and figure paths relative to `paper/`.
Include every intended section. Resolve TODO/FIXME comments or report them.
Never silently alter original research claims; explain proposed claim changes.

Derived CSV, table and figure are intentionally tracked. Regenerate them from
Python; never hand-edit generated PDFs, tables, CSVs, .aux, .log or other build
artifacts. Build output belongs in ignored `build/`. Existing tracked auxiliary
files may be removed as maintenance. Preserve source/generated boundaries.
Protect `.git/`, licenses, agent guidance, hooks, and CI from incidental edits;
change policy files only when explicitly requested. Never commit credentials.
Do not publish, push, install system packages or change machine configuration.

Commands from the root (some become available at later workshop stages):
- `python experiments/generate_convergence.py`
- `sh scripts/build.sh`
- `python scripts/project_health.py --strict`
- `python -m unittest discover -s evals -v`

After LaTeX changes compile the complete paper, inspect errors and relevant
warnings, run strict health and tests, then review `git diff --check` and the diff.
After experiment changes regenerate all outputs first. Report modified files,
commands, exit results, unresolved warnings and unavailable executables honestly.
Successful compilation verifies document construction, not mathematical validity.
Early stages are intentionally unhealthy: preserve defects unless repair is requested.
