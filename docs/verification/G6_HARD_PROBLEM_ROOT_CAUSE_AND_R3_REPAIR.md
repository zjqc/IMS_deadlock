# G6 Hard Problem Root Cause And R3 Repair

## Scope

This report records the G6 historical replay hard-problem diagnosis and the R3
repair result. It covers only the mechanism-regression question exposed after
G5:

- the Windows scheduler lease failure exposed by R1;
- the quantitative producer/consumer tolerance drift exposed by R2;
- the R3 preregistered historical replay that checks those two repaired
  mechanisms on the same five historical cases.

It does not rescore R1 or R2, fill missing R1 rows, rewrite R2 artifacts,
replace G5 evidence, or claim that an independent G6-C/D/E confirmation gate
has completed.

## Problem Symptoms

| Replay | Symptom | Preserved status |
| --- | --- | --- |
| R1 | Concurrent schedule-state admission on Windows could trip the old fixed `0.25` second lease threshold. Two legitimate contenders were classified as schedule-lease failures. | `FAILED_INCOMPLETE`; missing rows remain missing |
| R2 | All five primary/repro pairs matched exactly, but grid and medium cases failed the mechanism summary because consumers required exact `[0, 1]` probability bounds. | `FAILED_MECHANISM_CHECK`; no R3 rescoring |
| R3 | New replay required a fresh lock, code tree, output root, primary pass, and repro pass. | Historical replay mechanism closure only |

R1 also exposed an unsafe scheduler edge: contenders attempted to inspect the
sentinel while it could be owned by another process, and a dangerous retry after
an unlink failure could delete a replacement sentinel created by a later
contender.

R2 exposed the quantitative edge. The affected payloads reported a maximum
probability of `1.0000000000000002`, only
`2.220446049250313e-16` above one, while the largest observed committor
residual was `3.1086244689504383e-15`. The producer and linear-algebra routines
used an absolute tolerance of `1e-10`; the replay and G5 consumers imposed an
exact `0 <= min <= max <= 1` rule. That mismatch made roundoff look like a
mechanism failure.

## Minimal Reproduction And Evidence

The minimal R1 failure mechanism is schedule-state lock contention, not a
scientific rerun failure:

1. launch concurrent captures that must serialize access to
   `schedule_state.json`;
2. force a contender to wait longer than the old fixed `0.25` second window;
3. on Windows, allow a waiting process to read or hold the sentinel while the
   owner tries to release it;
4. observe a manual-incident classification or a delete-sharing failure instead
   of ordinary critical-section waiting.

The minimal R2 failure mechanism is numeric contract drift:

1. produce a valid committor map with roundoff-scale values such as
   `1.0000000000000002`;
2. report bounds derived from that map;
3. check the same payload with an exact `[0, 1]` consumer rule;
4. mark `probability_bounds_valid=false` even though the residual and excess
   are far below the producer tolerance.

Repository-relative audit anchors:

| Evidence | Path |
| --- | --- |
| R1/R2 preserved failure ledger | `evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json` |
| R1 preregistration | `docs/cases/G6_HISTORICAL_REPLAY_PREREGISTRATION.md` |
| R1 execution lock | `evidence/g6/G6_HISTORICAL_REPLAY_LOCK.json` |
| R2 preregistration and scheduler diagnosis | `docs/cases/G6_HISTORICAL_REPLAY_R2_PREREGISTRATION.md` |
| R2 execution lock | `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R2.json` |
| R3 preregistration and quantitative repair boundary | `docs/cases/G6_HISTORICAL_REPLAY_R3_PREREGISTRATION.md` |
| R3 execution lock | `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json` |
| Historical replay implementation | `src/ims_deadlock/historical_replay.py` |
| Historical replay tests | `tests/test_historical_replay.py` |

`validate-lock` must point `--bundle-root` at the frozen historical authority
`D:\worktree\IMS_deadlock-g5-confirmation\cases\confirmation\g4`. The copy under
the R3 code worktree is not the frozen bundle authority and correctly fails
that validation. The R3 code, R3 lock, and frozen G5/G4 bundle therefore remain
three separately locked provenance objects.

## Root Cause Chain

The hard problem was not one defect. It was a chain of two independent
mechanism regressions.

First, the scheduler conflated a state-file critical section with scientific
case execution. A short lease threshold treated ordinary contention as a stale
lease. The Windows sentinel handling then widened the failure: reading an
occupied sentinel could interfere with release, and retrying a failed unlink
could remove a replacement sentinel.

Second, the quantitative consumers were stricter than the producer and the
linear solver. The producer accepted floating-point roundoff at `1e-10`, but
the replay/G5 consumer path required exact probability bounds. The consumer
therefore rejected payloads whose numerical error was roughly `2.22e-16`, far
below the producer contract.

These defects are separable. The scheduler repair makes the replay executable
without scientific retry. The tolerance repair makes the consumer judge the
same numerical contract used by the producer and residual checks.

## Repair Boundary

The R1 repair is operational only:

- serialize only the schedule-state critical section;
- do not retry, relaunch, or backfill scientific captures;
- record timeout, stale, corrupt, and release incidents as immutable sidecar
  incident records;
- on Windows, do not use `os.kill` as liveness evidence and do not read an
  occupied sentinel during contention;
- attempt sentinel release once and fail closed on unlink failure.

The R2/R3 repair is quantitative only:

- use shared absolute tolerance `1e-10` for scalar committor/range checks;
- use shared absolute tolerance `1e-10` for linear residual checks;
- validate the complete `deadlock_probability` map, reported bounds, and
  residuals;
- require the producer `probability_bounds_valid` flag as necessary but not
  sufficient;
- do not clamp values, rewrite raw outputs, or modify old R1/R2 artifacts.

The repair does not alter G4 frozen inputs, G5 primary/repro captures, theorem
predictions, case parameters, estimands, resource caps, or random-stream
provenance.

## Scientific Self-Consistency

The R3 rule is scientifically self-consistent because it aligns the consumer
contract with the numerical contract already used by the producer and linear
algebra residuals. A value of `1.0000000000000002` is accepted only as
roundoff-scale excess under the `1e-10` absolute tolerance. Material violations
remain failures: reversed bounds, extra-state probabilities, NaN or infinite
values, loose reported bounds, and residuals above tolerance are rejected.

This preserves the scientific meaning of the replay:

- exact artifacts remain exact artifacts;
- floating-point roundoff is not upgraded into a theorem failure;
- material probability or residual violations still fail;
- old failed evidence stays visible instead of being silently repaired.

## R3 Preregistration And Result

R3 was locked as a fresh historical replay:

| Item | Value |
| --- | --- |
| Code branch | `codex/g6-replay-code-r3` |
| Code HEAD | `7b213d279ca6d57b0a8f8e904f4028b315e9b2b5` |
| Code tree | `9349bf891acc8d68925ba35e72463663fedab5a4` |
| Lock branch head | `36476bd516786c78dc3759a53b29e98f00bd3968` |
| Runtime lock SHA-256 | `99adb8c6725751037f066db5bcd36bb799f22137ba66aeb796094f38d7594bbb` |
| Output root | `D:\worktree\IMS_deadlock-g6-replay-code-v3\artifacts\g6-historical-replay\G6-R-20260730-R3` |
| Study role | `historical_replay` |
| Confirmation use | `no_confirmation_use=true` |

The locked five cases were:

- `G4_CRP_S4PR_AGREE`;
- `G4_CRP_OUTSIDE_S4PR`;
- `G4_ADVERSARIAL_BOUNDARY`;
- `G4_IMS_PARAMETER_GRID`;
- `G4_MEDIUM_ISLAND_REBUILD`.

Supplied R3 execution evidence reports:

| Check | Result |
| --- | --- |
| Primary/repro raw stdout | 5/5 match |
| Primary/repro canonical JSON | 5/5 match |
| Primary/repro stderr | 5/5 match |
| Mechanism summary | 5/5 `PASS` |
| Boundary theorem status | two boundary cases `SUPPORTED` |
| Boundary `certificate_minimality` | retained `FAIL` / `false` |

The boundary rows therefore close the theorem-prediction replay mechanism while
preserving the separate certificate-minimality failures.

## Negative Evidence

The following negative evidence remains part of the record:

- R1 remains `FAILED_INCOMPLETE`; missing repro rows are not filled.
- R2 remains `FAILED_MECHANISM_CHECK`; its summary is not replaced by R3.
- R2's exact primary/repro agreement is preserved, but the failed consumer
  status remains the frozen R2 result.
- The two boundary certificate-minimality observations remain `FAIL` /
  `false`.
- Historical G4/G5 rows remain retired from future held-out use.

No negative row is deleted, reclassified as a new held-out success, or used to
claim an independent confirmation pass.

## Remaining Scope

R3 closes only the historical replay mechanism-regression question:

- the Windows schedule-state lease mechanism no longer requires scientific
  retries;
- the quantitative consumer now applies the same tolerance contract as the
  producer and residual checker;
- the five historical primary/repro pairs are reproducible under R3.

R3 does not complete:

- independent G6-C/D/E confirmation;
- a new held-out case freeze;
- replacement of G5 evidence;
- certificate-minimality repair;
- general plant-level Petri/S3PR closure;
- broader stochastic or risk-budget claims outside the stated G6 replay scope.

## Auditable Paths

Use these paths to audit the report without relying on chat history:

| Purpose | Repository-relative path |
| --- | --- |
| Preserved R1/R2 failures | `evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json` |
| R3 preregistered scope and execution rule | `docs/cases/G6_HISTORICAL_REPLAY_R3_PREREGISTRATION.md` |
| R3 lock fields and case list | `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json` |
| Shared probability tolerance tests | `tests/test_ctmc.py` |
| Historical replay scheduler and mechanism tests | `tests/test_historical_replay.py` |
| Historical replay implementation | `src/ims_deadlock/historical_replay.py` |
| G5 scorer separation context | `docs/verification/G5_CONFIRMATION_REPORT.md` |
| Claim/evidence boundary table | `docs/verification/G5_CLAIM_EVIDENCE_TABLE.md` |

Audit stop condition: R3 may be cited as a historical replay mechanism repair
only when the cited evidence includes the R1/R2 failure ledger, the R3
preregistration, the R3 lock, and the R3 primary/repro match summary. It may
not be cited as an independent G6 confirmation result.
