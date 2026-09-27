# Paper Steward workshop

A six-stage workshop showing how to customize Codex into a safe LaTeX
research-project maintenance agent. Paper Steward edits a mathematical paper,
regenerates experiments, checks project health, and reports verification evidence.
It is not a theorem prover.

`main` contains this workshop overview. Each stage has its own branch, so you can
explore it with `git checkout stage0`, `git checkout stage1`, and so on. The original
annotated tags preserve the immutable stage snapshots.

## Stages

| Branch | What it demonstrates | Annotated snapshot |
| --- | --- | --- |
| `stage0` | A plausible paper with intentional maintenance defects: broken references/citations, inconsistent notation, stale data, and incomplete build guidance. | `stage-0-broken-project` |
| `stage1` | Persistent project rules in `AGENTS.md`, with shared Claude Code guidance in `CLAUDE.md`. Defects remain. | `stage-1-project-instructions` |
| `stage2` | A reusable `maintain-latex-project` Agent Skill and maintenance checklist. Defects remain. | `stage-2-maintenance-skill` |
| `stage3` | A deterministic health checker, portable build script, and fixture tests. Tests pass; paper health intentionally fails. | `stage-3-health-check` |
| `stage4` | Repository-local Codex hooks that flag protected edits and enforce verification before completion. The paper remains intentionally unhealthy. | `stage-4-hooks` |
| `stage5` | The completed agent and repaired paper, regenerated data/figure/table, passing checks, CI, full documentation, and a live workshop guide. | `stage-5-complete-agent` |

## Navigate the workshop

Start with a clean working tree; save your changes before switching stages.

```sh
git checkout stage0
git checkout stage1
git checkout stage2
git checkout stage3
git checkout stage4
git checkout stage5
# Return to this overview:
git checkout main
```

For the complete project, use `stage5`. Read its `README.md` for prerequisites and
commands, `WORKSHOP.md` for a suggested live demonstration, and `VERIFICATION.md`
for the recorded local results. The stage branches initially point to the six
original sequential commits; `main` adds this overview commit after Stage 5.
The history verifier on `stage5` checks the original six-stage history there.

## Demonstration prompt

```text
Prepare this mathematical paper repository for submission. Resolve maintainability problems, regenerate derived artifacts from their sources, compile the complete paper, and provide evidence for every verification claim. Do not change the mathematical claim merely to silence a check.
```

Compare the early broken draft with Stage 5. Instructions and skills guide the
agent; scripts supply objective checks; hooks enforce selected lifecycle checks.
Built-in filesystem, search, shell, and Git tools are sufficient. Compilation and
numerical experiments do not verify the mathematical truth of the paper.

Published at https://github.com/dario-coscia/paper-steward with all stage branches
and annotated tags. The six annotated snapshots remain intact.
