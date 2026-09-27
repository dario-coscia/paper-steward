# Paper Steward

Turn an existing coding agent into a careful LaTeX research-project maintainer.
Six sequential commits demonstrate persistent instructions, a reusable skill,
deterministic checks, lifecycle hooks, and objective evals. The example paper,
*Quadratic Convergence of Newton’s Method for the Square Root of Two*, proves
monotone convergence and the exact quadratic error identity for Newton's method
starting at two, then illustrates the result with a reproducible comparison.

Paper Steward maintains project conventions, edits sources, regenerates derived
artifacts, compiles the document and reports evidence. It is not a theorem prover.

## Quick start

Prerequisites: Python 3.10+, Matplotlib 3.7–3.x, Git, a POSIX shell, and a LaTeX
installation with `latexmk` and `pdflatex` (or `pdflatex` and `bibtex`). Packages
used by the paper: geometry, amsmath, amssymb, amsthm, graphicx, booktabs, hyperref.
A normal TeX Live or MacTeX installation supplies them. No LLM API key is needed
for the scripts or evals; use your existing Codex or Claude Code account for agent work.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python experiments/generate_convergence.py
python -m unittest discover -s evals -v
sh scripts/build.sh
python scripts/project_health.py --strict
```

Read `build/main.pdf` and `build/main.log`. Commands work from the repository
root; the experiment and build resolve paths relative to their own source.
`python scripts/verify_stages.py` verifies the annotated stage history.
Health exits 1 on errors; `--strict` also rejects warnings, including an unavailable
compiler. `--no-build` performs static checks only. The default checker compiles
in a temporary directory, leaving source files untouched. No supported compiler
means compilation is explicitly unverified, not passed.

## Architecture

| Component | Role |
| --- | --- |
| `AGENTS.md` | Persistent conventions, scope boundaries and reporting rules |
| `.agents/skills/maintain-latex-project/` | Discoverable reusable maintenance workflow and checklist |
| Built-in filesystem, search, shell and Git tools | Inspect and change the project |
| `scripts/project_health.py` | Deterministic source, provenance and compilation checks |
| `scripts/build.sh` | Complete LaTeX build in ignored `build/` |
| `.codex/hooks.json` | Event-driven checks and protected-file guardrails |
| `evals/` | Objective healthy/unhealthy fixtures and exit-behavior tests |
| `.github/workflows/ci.yml` | Regeneration, evals, build and strict health in CI |

No separate agent runtime, RAG, web application or orchestration framework is
needed. Built-in filesystem and shell tools suffice. MCP could later connect an
external bibliography service or submission system, but adds no value to this local prototype.

## Sources and derived outputs

`paper/main.tex` includes the section sources (including a separate quadratic-error
section), shared macros and bibliography. `experiments/generate_convergence.py`
is the source for the CSV, generated table and convergence PDF. Those three outputs
and `paper/generated/provenance.json` are intentionally tracked to make the example
readable immediately. Never edit them by hand. The manifest hashes source and outputs;
regeneration refreshes all four. A timestamp warning also detects an older output,
but hashes provide durable change detection across Git checkouts. After switching
stages, regenerate before strict verification because Git timestamps are not provenance.
The full compiled paper, logs, auxiliaries and build receipt are ignored.

The experiment uses 21 binary64 iterates. Bisection index zero is the first midpoint
of [1,2]; Newton index zero is 2. Errors use an 80-digit decimal reference and exact
conversion of binary64 values. Plot clipping below 1e-18 affects only plotting;
CSV values remain unchanged. The table is generated from its first six rows.
Equal indices do not imply equal computational cost. The finite experiment cannot
establish mathematical convergence. Cross-version PDF rendering may vary slightly;
CI regenerates the outputs rather than requiring byte-identical PDFs across platforms.

## Use with Codex and Claude Code

Start Codex in the repository and ask for a maintenance task. The repository skill
is available for discovery; explicitly invoke `$maintain-latex-project` for a demonstration.
Inspect `.codex/README.md`, the scripts and hook definitions before trusting project
hooks. Use `/hooks` to review/trust definitions or disable them for teaching. Local
config requests workspace-write and on-request approvals; user or managed settings
may take precedence. Hooks are guardrails, not a replacement for the permission sandbox.

| Concept | Codex | Claude Code |
| --- | --- | --- |
| Persistent guidance | `AGENTS.md` | `CLAUDE.md` points to the shared rules |
| Workflow | `.agents/skills/.../SKILL.md` | Read the same workflow explicitly; no native discovery claim |
| Tools and verification | Built-in shell/filesystem + scripts | Same source files and shell commands |
| Lifecycle enforcement | Reviewed `.codex/hooks.json` | Requires separate client-specific configuration; run scripts manually here |

Guidance tells the agent what good work looks like. Hooks execute checks at tool/stop
boundaries. The stop hook checks strict static health and existing complete-build
evidence without modifying files. It allows one corrective continuation and then
requires honest reporting if verification remains incomplete. See `.codex/README.md`.

## Workshop stages

Start with a clean working tree. These commands inspect immutable tags in detached
HEAD mode; use a new branch for a live repair (`git switch -c workshop-repair`).

```sh
git switch --detach stage-0-broken-project
git switch --detach stage-1-project-instructions
git switch --detach stage-2-maintenance-skill
git switch --detach stage-3-health-check
git switch --detach stage-4-hooks
git switch --detach stage-5-complete-agent
# Return to the completed publication branch:
git switch main
```

| Stage | Learning outcome |
| --- | --- |
| 0 | A plausible, deliberately broken draft |
| 1 | Persistent project rules; defects retained |
| 2 | Reusable skill workflow; defects retained |
| 3 | Objective checks fail on the broken project; checker tests pass |
| 4 | Hook enforcement correctly reports the same unhealthy state |
| 5 | Repaired sources, regenerated outputs, tests and full build |

Never force a checkout over uncommitted work. Use a separate worktree for experiments
or commit the demo repair on its own branch. Earlier stages intentionally lack later
checks. See `WORKSHOP.md` for the live sequence and `STAGE_0_NOTES.md` for the
instructor's historical defect inventory; it does not describe the final state.

## Maintenance prompts

```text
Prepare this mathematical paper repository for submission. Resolve maintainability problems, regenerate derived artifacts from their sources, compile the complete paper, and provide evidence for every verification claim. Do not change the mathematical claim merely to silence a check.
```

```text
Rename the main convergence theorem and update all references safely.
```

```text
Regenerate the numerical experiment and explain any changed values.
```

```text
Audit the paper for unresolved citations, references, TODOs, and stale figures.
```

## Limits and verification

The checker implements this repository's literal LaTeX conventions, not arbitrary
TeX expansion. See `evals/README.md` for supported syntax and limitations. Build
receipts demonstrate source/PDF/log consistency, not scientific correctness or a
security attestation. Hook coverage cannot prevent arbitrary shell writes. No live
model eval, external submission or remote publishing is performed. CI is supplied
but local verification cannot claim a GitHub-hosted run. Human mathematical review
remains necessary. This repository is MIT licensed, has no remote, and is ready
for you to publish. Local verification evidence is recorded in `VERIFICATION.md`.
