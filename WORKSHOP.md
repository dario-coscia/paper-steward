# Live workshop: specialize an existing agent

Allow 45–60 minutes. Prepare Python and LaTeX before the session, inspect hook
scripts, and keep a clean clone available. Save Stage 5 docs separately or read
this file on main before checkout. Stages are snapshots of customization, not a
record of six LLM conversations. Stage 0's proof is mathematically sound; its
maintenance defects are documented in the instructor notes.

## Primary request

```text
Prepare this mathematical paper repository for submission. Resolve maintainability problems, regenerate derived artifacts from their sources, compile the complete paper, and provide evidence for every verification claim. Do not change the mathematical claim merely to silence a check.
```

## Suggested sequence

1. **Stage 0 (8 minutes).** `git switch --detach stage-0-broken-project`.
   Inspect the tree and README. Create a repair branch with `git switch -c demo-baseline`
   and run the primary request. Observe how an uncustomized agent discovers conventions.
   Save its diff and report; do not imply all agents behave identically.
2. **Stage 1 (5 minutes).** In a clean separate worktree/clone inspect
   `stage-1-project-instructions`. Read AGENTS.md and CLAUDE.md. Repeat the request
   on a fresh branch. Discuss source boundaries and truthful reporting.
3. **Stage 2 (7 minutes).** Inspect `stage-2-maintenance-skill` and invoke
   `$maintain-latex-project` with the primary request. Show frontmatter discovery
   and the focused checklist. Instructions and skills guide; they do not execute checks.
4. **Stage 3 (8 minutes).** Inspect `stage-3-health-check`. Run
   `python -m unittest discover -s evals -v` (expected success), then
   `python scripts/project_health.py --strict` (expected exit 1). Trace findings to
   sources. A passing checker test suite does not mean the draft is healthy.
5. **Stage 4 (8 minutes).** Inspect `stage-4-hooks`. Review `.codex/README.md`,
   hooks.json and hook_guard.py, then use `/hooks` to trust the project definitions.
   Show a direct generated-file patch being denied, and the stop hook returning
   actionable failures. The hook intentionally blocks completion on this snapshot.
   Use `/hooks` or `codex -c features.hooks=false` when teaching without enforcement.
   Shell writes are not comprehensively blocked; demonstrate the scope honestly.
6. **Stage 5 (10 minutes).** Return to `main` or inspect `stage-5-complete-agent`.
   Regenerate, run tests, build and run strict health. Open build/main.pdf. Compare
   objective evidence and the Stage 0 diff with the final result. Ask which properties
   were actually checked and which still need a mathematical reviewer.

Use `git worktree add --detach ../paper-steward-stage3 stage-3-health-check` for
isolated stage comparisons. Give each live repair its own branch. Do not force
checkouts or discard participant edits. To return after a clean tag inspection,
use `git switch main`. Historical generated outputs may need regeneration due to
checkout timestamps. Early stages deliberately have incomplete build guidance.

## Smaller exercises

```text
Rename the main convergence theorem and update all references safely.
```

```text
Regenerate the numerical experiment and explain any changed values.
```

```text
Audit the paper for unresolved citations, references, TODOs, and stale figures.
```

## Discussion and scoring

Record baseline and final health exits, changed sources, regeneration commands,
full-build results, warnings and claims in each report. Award one point each for
reference/citation repair, source/output discipline, notation and section repair,
objective test/build evidence, and honest limits. Use checker fixtures as objective
evals; do not present this rubric as a measured agent benchmark. Compilation cannot
prove the theorem. MCP is a possible future integration for external services;
built-in files, search, shell and Git are sufficient for the prototype.
