# Objective maintenance evals

Run `python -m unittest discover -s evals -v`. Small fixtures cover healthy and
unhealthy sources, exit codes, strict warnings, artifacts, provenance and compiler
failure/unavailability. They use temporary directories and require no model key.
These evals measure the checker, not agent reasoning or theorem correctness.

Health scans the reachable literal input/include graph relative to paper/, ignores
LaTeX comments for references, and includes comments when checking pending markers.
It supports common ref/cite commands with optional arguments and graphic extensions.
It cannot expand arbitrary macros, conditional TeX, verbatim environments, custom
bibliography systems or dynamic paths. Adapt conventions/checks for other projects.
Timestamp freshness is a warning because Git does not preserve modification times;
the final stage adds hashes for durable source/output provenance. Hashes detect
changes, not whether an author intentionally falsified a manifest. Numerical table
consistency is ensured by generation and tested separately in the final stage.

At Stage 3 and Stage 4, health exits 1 intentionally. Expect broken references,
citations, figure inclusion, a pending marker, omitted section, auxiliary artifact,
macro inconsistency and freshness warnings. Compilation also fails on the missing
figure. Do not hide those failures; compare them with Stage 5.

Final-stage experiment evals check recurrence parameters, bisection brackets,
exact decimal error identity samples, and tracked CSV/table consistency. Hook
evals check direct protected patches, valid source patches, stop continuation,
post-edit findings and JSON stdin/output contracts. No live-model score is claimed.
