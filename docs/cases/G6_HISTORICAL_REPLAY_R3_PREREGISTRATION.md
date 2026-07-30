# G6 Historical Replay R3 Preregistration

Status: `FROZEN CANDIDATE / SUPERSEDES FAILED R2 / NO CONFIRMATION USE`.

R3 is a fresh historical mechanism replay after R2 exposed a quantitative
consumer-contract defect. It does not rescore, copy, or complete either R1 or
R2. All five cases restart from `primary`, followed by a new `repro`, under a
new published code tree, lock file, output root, and raw-evidence manifest.

## Retained R1 And R2 Failures

R1 remains incomplete. Its two failed concurrent R1 commands were not retried
or filled after the old 0.25-second scheduler window rejected legitimate
schedule-state lock contention.

R2 used:

- code HEAD `fd6421b0bf214de5346402d711da83ff800e99a3`;
- code tree `4db174dc06be127451c526c7bea85811e9d6cf22`;
- lock SHA-256
  `64cf04cac098d5019af72a83555bb388a9b3af1cbfecc70305a6bdbc9f4d4b16`;
- output root
  `D:\worktree\IMS_deadlock-g6-replay-code-v2\artifacts\g6-historical-replay\G6-R-20260730-R2`.

R2 completed exactly ten formal-success captures. Every primary/repro raw
stdout hash, canonical JSON hash, and stderr hash matched. Its scheduler ended
with ten completed entries, no active entry, and no recorded incident.
Nevertheless, the frozen R2 summary is a failed result: the grid and medium
mechanism checks reported `probability_bounds_valid=false`.

The R2 CTMC payloads contained exact reported committor ranges. Six grid cells
and the medium case had maximum
`1.0000000000000002 = 1 + 2.220446049250313e-16`; the largest observed
committor residual was `3.1086244689504383e-15`. The producer correctly used
an absolute `1e-10` numerical tolerance, but the replay and G5 consumers
independently imposed exact `0 <= min <= max <= 1`. R2 therefore exposed a
consumer/producer contract drift, not a material probability violation.

R2 remains failed and immutable. Its summary is not replaced by the R3
checker.

## R3 Repair And Adversarial Boundary

The R3 code centralizes two explicit numerical contracts:

- scalar committor and range absolute tolerance: `1e-10`;
- absolute linear-system residual tolerance: `1e-10`.

The tolerance accepts linear-algebra roundoff only. Raw values are neither
clamped nor rewritten. The independent consumer audit now:

1. validates every value in the complete `deadlock_probability` map;
2. recomputes the map minimum and maximum and matches them to the reported
   bounds within the same tolerance;
3. requires both committor and mean-time residuals to be finite, nonnegative,
   and no larger than `1e-10`;
4. requires the producer `probability_bounds_valid` flag as an additional,
   not sufficient, condition;
5. retains the terminal-class provenance and local-bad soundness audits.

Regression tests reject Boolean, NaN/infinite, reversed, materially out-of-
range, extra-state probability, loose-bound, and large-residual payloads.
In particular, `1.000001`, an added probability `2.0`, a reported `[0,1]`
range for an actual singleton `0.5`, and a `1e-6` residual all fail.

The locked Dell source state passed 335 tests, Ruff, the 90-file format check,
strict mypy for 21 source files, and `git diff --check`. An independent review
first raised the incomplete consumer audit as HIGH, then returned `APPROVED`
after the full-map, exact-range, and residual checks were added.

## R3 Frozen Boundary

- published ref: `refs/heads/codex/g6-replay-code-r3`;
- published HEAD: `7b213d279ca6d57b0a8f8e904f4028b315e9b2b5`;
- published tree: `9349bf891acc8d68925ba35e72463663fedab5a4`;
- clean code worktree: `D:\worktree\IMS_deadlock-g6-replay-code-v3`;
- lock:
  `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json`;
- output root:
  `D:\worktree\IMS_deadlock-g6-replay-code-v3\artifacts\g6-historical-replay\G6-R-20260730-R3`;
- historical G4 bundle:
  `D:\worktree\IMS_deadlock-g5-confirmation\cases\confirmation\g4`;
- Python:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`;
- required source override:
  `PYTHONPATH=D:\worktree\IMS_deadlock-g6-replay-code-v3\src`.

The same five historical cases, case parameters, estimands, resource caps, G4
freeze, G5 provenance inputs, and P1/P2/R1/R2 schedule are retained. R3 changes
only the quantitative integrity contract and the code provenance required to
execute that contract.

## R3 Execution Rule

Exactly ten new captures are permitted:

1. `P1`: three primary CRP/boundary cases, concurrency cap 3;
2. `P2`: primary grid and medium cases, concurrency cap 2;
3. `R1`: three repro CRP/boundary cases, concurrency cap 3;
4. `R2`: repro grid and medium cases, concurrency cap 2.

All primary captures must complete before any repro. A terminal incident blocks
the affected and downstream schedule; there is no automatic retry or third
run. Primary/repro comparisons and the final summary are generated only if all
ten formal-success capture records exist.

R3 remains `historical_replay` evidence only. It may close the scheduler and
quantitative-consumer mechanism regressions. It cannot pass the independent
G6-C/D/E confirmation gate, replace G5 evidence, or be counted as a new
held-out success.
