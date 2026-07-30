# G6 Historical Replay R2 Preregistration

Status: `FROZEN CANDIDATE / SUPERSEDES FAILED R1 / NO CONFIRMATION USE`.

R2 is a fresh historical mechanism replay after R1 exposed a scheduler defect.
It is not a retry of either failed R1 case and does not reuse any R1 scientific
row. All five cases restart from `primary`, followed by a new `repro`, under a
new code tree, lock file, output root, and raw-evidence manifest.

## Retained R1 Failure

The original frozen replay used:

- code HEAD `eb9c1fc877f21639c55bee0852e19f0755aad3e9`;
- code tree `50d15583b172e00d088050ca5a1580351b059212`;
- lock SHA-256
  `87dec93e2933b2b553091e912097314df4edd39e2019132c77d433bd3b3f6cac`;
- output root
  `D:\worktree\IMS_deadlock-g6-replay-code\artifacts\g6-historical-replay\G6-R-20260730-R1`.

P1 and P2 completed all five primary rows. At R1, only
`G4_CRP_S4PR_AGREE` completed. The other two concurrent commands exited 1 with:

```text
existing schedule lease requires manual incident classification;
automatic recovery is forbidden
```

The failed output root contains 19 retained files totaling 9,090,470 bytes.
Its canonical path-to-SHA-256 manifest hash is
`b6de160ee3de57a3232f5e03a62dc98ba49b6c39966d5aaa3c32357c30da5fb7`;
the final `schedule_state.json` hash is
`eb7c6a4f5ee7d3387d1b1ddcdd7b9059234e2a9f9c7e48a87daf8b084ebb52d3`.
The old implementation did not durably record pre-admission lock failures in
`schedule_state.json`; that missing audit edge is part of the diagnosed defect,
not evidence that the invocations did not occur.

No missing R1 row will be filled. R1 remains an incomplete failed replay.

## Root Cause And Repair Boundary

Three coupled scheduler faults were repaired:

1. a fixed 0.25-second window treated legitimate serialization of
   `schedule_state.json` as a stale-lease incident;
2. contenders read `.schedule.lock` while waiting, which on Windows could
   prevent the owner from deleting it with `WinError 32`;
3. retrying a failed delete could remove a replacement sentinel owned by a new
   contender.

The repaired scheduler:

- waits up to 30 seconds only to enter the schedule-state critical section;
- never retries or relaunches a scientific child;
- never reads the Windows sentinel during contention or timeout;
- records timeout/stale/corrupt classifications in immutable sidecar incidents;
- never automatically reaps an unknown lock;
- performs one release attempt and fails closed on `PermissionError`, preserving
  a possible replacement lock.

The repair is covered by deterministic tests for three concurrent P1 captures,
Windows delete-sharing semantics, malformed/dead/live/unknown lease
classification, pre-admission sidecar audit, formal-success gating, and
replacement-lock preservation. Dell validation at the repaired source state
reported 49 replay tests and 323 total tests passing, plus Ruff, formatting, and
strict mypy.

## R2 Frozen Boundary

- published ref: `refs/heads/codex/g6-replay-code`;
- published HEAD: `fd6421b0bf214de5346402d711da83ff800e99a3`;
- published tree: `4db174dc06be127451c526c7bea85811e9d6cf22`;
- clean code worktree: `D:\worktree\IMS_deadlock-g6-replay-code-v2`;
- lock:
  `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R2.json`;
- output root:
  `D:\worktree\IMS_deadlock-g6-replay-code-v2\artifacts\g6-historical-replay\G6-R-20260730-R2`;
- historical G4 bundle:
  `D:\worktree\IMS_deadlock-g5-confirmation\cases\confirmation\g4`;
- Python:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`;
- required source override:
  `PYTHONPATH=D:\worktree\IMS_deadlock-g6-replay-code-v2\src`.

The same five historical cases, estimands, caps, and P1/P2/R1/R2 schedule are
used. R2 changes only the scheduler implementation and code provenance required
to execute that already frozen schedule reliably. It does not change G4 inputs,
G5 evidence, theorem predictions, metric applicability, random streams,
quantitative estimands, or case parameters.

## R2 Execution Rule

Exactly ten new captures are permitted:

1. `P1`: three primary CRP/boundary cases, concurrency cap 3;
2. `P2`: primary grid and medium cases, concurrency cap 2;
3. `R1`: three repro CRP/boundary cases, concurrency cap 3;
4. `R2`: repro grid and medium cases, concurrency cap 2.

All primary captures must complete before any repro. A terminal incident blocks
the affected and downstream schedule; there is no automatic retry or third run.
Primary/repro comparisons and the final summary are generated only if all ten
formal-success capture records exist.

As with R1, R2 is `historical_replay` evidence only. It can close the diagnosed
mechanism-regression question but cannot pass the independent G6-C/D/E
confirmation gate or be counted as a new held-out success.
