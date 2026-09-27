---
name: maintain-latex-project
description: Maintain a mathematical LaTeX project when editing sections, renaming labels, repairing citations, regenerating experiments, or preparing a submission with verification evidence.
---

# Maintain a LaTeX project

Read root project guidance and identify the requested outcome and claim boundaries.
Inspect relevant source files, their inputs and dependents, and initial Git status.
Record the initial project-health command and findings before changing anything.
Make the smallest coherent change; preserve shared notation and all callers of
renamed labels. Keep generated and source files separate. Regenerate derived
artifacts when source experiments change rather than editing outputs by hand.
Compile the complete paper, inspect errors and relevant warnings, run the
deterministic health checker, and review the Git diff. Report modifications,
command evidence, and remaining issues; unavailable tools are not successful checks.
Read [the checklist](references/maintenance-checklist.md) for submission work.

Project instructions define local rules. This skill supplies a reusable workflow.
Built-in filesystem, search, shell and Git tools perform the work; deterministic
scripts supply repeatable observations. Hooks enforce selected checks at lifecycle
boundaries. None of those mechanisms verifies mathematical truth. Evaluate any
proposed claim change separately and disclose it; do not weaken claims to silence checks.
