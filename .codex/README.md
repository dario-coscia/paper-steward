# Lifecycle enforcement

Schema checked against Codex CLI 0.157.0 and the
[official hooks documentation](https://learn.chatgpt.com/docs/hooks) on 2026-09-27.
Inspect hooks.json and hook_guard.py before trusting them. Project hooks require a
trusted project config layer and exact-definition review. In Codex CLI use `/hooks`
to inspect, trust, or disable individual hooks; changed definitions require review.
For a teaching session use `codex -c features.hooks=false` to disable hooks for
that invocation, or disable individual hooks in `/hooks`. Do not bypass trust.

- PreToolUse: denies direct patches to generated/build/protected paths. Shell
  commands mentioning obvious protected paths receive a warning. Shell syntax is
  not fully parsed; this is a guardrail, not a security sandbox. Source regeneration
  and read-only inspection remain allowed. Disable the guard through `/hooks` for
  explicitly authorized policy changes and re-review it afterward.
- PostToolUse: after relevant paper .tex/.bib patches, runs strict static health and
  returns actionable model context. It does not demand compilation after each edit
  and cannot undo a completed tool operation. Shell edits are caught at Stop.
- Stop: runs strict static health plus read-only verification of build/evidence.json,
  source hashes, PDF hash and warning-free log. Missing/stale evidence blocks the
  first stop and asks for `sh scripts/build.sh`; a repeated failed stop reports the
  incomplete verification rather than causing an endless continuation loop.

All hooks read JSON stdin, use documented JSON feedback, have bounded timeouts,
never call Codex, and never write project files. The explicit build command creates
ignored build evidence. Regular `project_health.py --strict` performs a fresh
compilation in a temporary directory. Hooks inspect evidence rather than build.

AGENTS.md and skills guide decisions. Hooks execute deterministic enforcement at
lifecycle boundaries; sandbox permissions still define actual filesystem access.
These hooks have fixture/contract checks, but no unattended LLM session is required
or claimed by this workshop. At Stage 4 they correctly report an unhealthy project.
