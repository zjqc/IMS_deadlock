# G6 Historical Replay Preregistration

Status: `FROZEN CANDIDATE / HISTORICAL REPLAY ONLY / NO CONFIRMATION USE`.

This protocol tests whether the mechanisms diagnosed after G5 have been
repaired under a newly versioned G6 implementation and estimand. It does not
rescore or overwrite G5, does not reuse the label `heldout_confirmation`, and
cannot support a new confirmation-set accuracy claim. A publishable G6
confirmation result still requires the independent G6-C/D/E seal described in
the recovery plan.

## Frozen Code And Evidence Boundary

- repository: `zjqc/IMS_deadlock`;
- published ref: `refs/heads/codex/g6-replay-code`;
- published HEAD: `eb9c1fc877f21639c55bee0852e19f0755aad3e9`;
- published tree: `50d15583b172e00d088050ca5a1580351b059212`;
- code worktree: `D:\worktree\IMS_deadlock-g6-replay-code`;
- historical G4 bundle:
  `D:\worktree\IMS_deadlock-g5-confirmation\cases\confirmation\g4`;
- historical freeze ID: `G4-FREEZE-C-20260730T051210Z`;
- execution lock:
  `evidence/g6/G6_HISTORICAL_REPLAY_LOCK.json`;
- output root:
  `D:\worktree\IMS_deadlock-g6-replay-code\artifacts\g6-historical-replay\G6-R-20260730-R1`.

The lock pins every Python behavior file by SHA-256, the complete G4 freeze
artifact-hash map, the original G5 summary/raw-manifest/execution-lock/erratum
and scorer hashes, the runtime, the output limits, the schedule, and the exact
estimand payload. A change to any pinned object invalidates this replay rather
than silently creating a comparable row.

## Root Causes Under Test

The replay tests five already discovered mechanisms:

1. theorem truth and certificate-minimality observations must remain
   orthogonal in scoring;
2. the CRP overlap bridge must consume the complete local minimal-kernel
   family rather than substitute a global certificate;
3. quantitative analysis must partition the complete stable LTS into
   `D_global`, verified `D_local`, `F`, `R_livelock`, and
   `R_terminal` before constructing the competing-class estimand;
4. a current local kernel is not promoted to `D_local` when a completion path
   exists in the complete generated LTS;
5. a replay capture is successful only when exit status, canonical JSON,
   schema, case ID, and nonempty estimand identifiers all agree.

The replay may show that a mechanism is fixed, still fails, or is refused under
the declared scope. No outcome authorizes threshold, seed, route, class,
scoring, timeout, or case changes.

## Frozen Cases And Estimands

| Case | Historical role | G6 estimand |
| --- | --- | --- |
| `G4_CRP_S4PR_AGREE` | prior local-bridge failure | local certificate-family availability and exact CRP resource-set match |
| `G4_CRP_OUTSIDE_S4PR` | boundary/refusal row | theorem prediction and independent certificate-minimality observation |
| `G4_ADVERSARIAL_BOUNDARY` | adversarial boundary row | theorem prediction and independent certificate-minimality observation |
| `G4_IMS_PARAMETER_GRID` | prior quantitative failure | per-cell deadlock probability and probability-bound validity under the G6 class partition |
| `G4_MEDIUM_ISLAND_REBUILD` | prior medium quantitative failure | medium-island deadlock probability and probability-bound validity under the G6 class partition |

The exact estimand specification is
`ims-deadlock/g6-default-estimand-spec/v1` with canonical SHA-256
`4643e9bdd9532ac3fcd65c37783143966f75344cb70199a88838153dd1345eeb`.

## Frozen Schedule

Exactly one `primary` and one `repro` capture are allowed for each case.
Automatic retry and a third run are forbidden.

1. `P1`: run the three CRP/boundary cases concurrently, cap 3.
2. `P2`: after all P1 rows complete, run grid and medium concurrently, cap 2.
3. `R1`: only after all five primary rows complete, run the three
   CRP/boundary repro rows concurrently, cap 3.
4. `R2`: after all R1 rows complete, run grid and medium repro concurrently,
   cap 2.

The replay module enforces this order with an atomic schedule lease and durable
schedule state. The same case may not overlap itself. Each scientific child has
`max_parallel_cases=1`; nested scientific parallelism is disabled.

## Runtime And Resource Lock

- Python:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`;
- Python version: `3.13.9`;
- required source override:
  `PYTHONPATH=D:\worktree\IMS_deadlock-g6-replay-code\src`;
- per-child timeout: 1800 seconds;
- stdout cap: 256 MiB;
- stderr cap: 16 MiB.

The live pre-execution probe on 2026-07-30 reported an Intel Xeon w7-3465X
with 28 physical cores/56 logical processors, 127.25 GiB visible memory,
104.83 GiB free memory, and 5.55 TiB free on drive D. The case-level caps of
3 and 2 are therefore conservative; they use the machine without changing any
single-case scientific semantics.

## Failure And Evidence Rules

- Nonzero exit, timeout, oversized output, non-UTF-8 stdout, malformed JSON,
  wrong schema, wrong case ID, or empty estimand identifiers are terminal
  capture incidents.
- A terminal incident blocks automatic recapture and downstream waves according
  to the frozen schedule. Recovery requires explicit incident classification;
  stale leases are never reaped automatically.
- `stdout.bin`, `stderr.bin`, `record.json`, schedule events, canonical output,
  comparisons, and hashes are retained even when the row is unfavorable.
- Primary/repro equality is assessed only after both formal-success records
  exist. A deterministic refusal is evidence, not permission to edit the
  protocol.
- Original G5 artifacts remain byte-stable and are included only as provenance.
- Replay outputs remain under the ignored task-owned artifact root. The final
  repository records a compact hash manifest and report rather than copying raw
  scientific output into Git.

## Exact Command Shape

All commands run from the clean G6 code worktree with the source override
above:

```text
python -m ims_deadlock.historical_replay validate-lock \
  --lock <external-lock-path> \
  --bundle-root <frozen-g4-bundle> \
  --published-head eb9c1fc877f21639c55bee0852e19f0755aad3e9 \
  --published-tree 50d15583b172e00d088050ca5a1580351b059212

python -m ims_deadlock.historical_replay capture \
  --lock <external-lock-path> \
  --bundle-root <frozen-g4-bundle> \
  --published-head eb9c1fc877f21639c55bee0852e19f0755aad3e9 \
  --published-tree 50d15583b172e00d088050ca5a1580351b059212 \
  --case-id <LOCKED_CASE_ID> \
  --run-label <primary-or-repro>
```

After the ten captures, `compare` is run once per case and `summarize` once for
the complete replay. These diagnostic results close only the historical
mechanism-regression question. They do not pass the independent G6
confirmation gate.
