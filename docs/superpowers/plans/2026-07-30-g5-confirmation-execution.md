# IMS Deadlock G5 Frozen Confirmation Execution Plan

Status: `PRE-EXECUTION / NO HELD-OUT OUTPUT INSPECTED`.

## Goal

Execute the nine C-sealed G4 confirmation cases exactly as frozen, reproduce
every result once under the same runtime and streams, score the preregistered
predictions without retuning, and produce a compact evidence package suitable
for manuscript claims and independent audit.

## Immutable Inputs

- Integrated source commit:
  `58694a214458669525791d7d8100c8d9b4183a62`.
- Implementation commit A:
  `f9b9a5a5652c7a49053e7ef26d08911bd757f465`.
- Preregistration commit B2:
  `58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`.
- Seal commit C:
  `e91be4d6d7511c76918093899269de4b78e69fd8`.
- Freeze ID:
  `G4-FREEZE-C-20260730T051210Z`.
- Canonical runtime:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`.
- Scientific commands:
  exactly the nine `g4_protocol ... run <CASE_ID>` entries in
  `cases/confirmation/g4/runtime_lock.json`.

No case, prediction, metric, baseline applicability decision, stream, seed,
replicate count, state bound, route, rate, or scoring rule may change after
execution begins.

## Commit Topology

1. **G5-A — non-scientific evidence tooling**
   - immutable command capture;
   - exact rerun comparison;
   - frozen-rule scorer;
   - synthetic tests only.
2. **G5-B — pre-execution lock**
   - records G5-A;
   - fixes execution order, output paths, timeouts, scoring rules, and stop
     conditions;
   - contains no held-out result.
3. **G5-C — primary and reproducibility evidence**
   - stores compact scored evidence and raw-output hashes;
   - does not alter frozen G4 artifacts;
   - retains every negative, failed, refused, or inconclusive row.
4. **G5-D — manuscript evidence closure**
   - claim-evidence table;
   - confirmation and reproducibility reports;
   - roadmap and counterexample/bug ledger updates;
   - paper-ready tables only after independent review.

## Task 1: Implement Immutable Command Capture

Create `src/ims_deadlock/g5_capture.py` and
`tests/test_g5_capture.py` using RED -> GREEN -> REFACTOR.

Required behavior:

- execute exactly one frozen `g4_protocol run` command using the current
  interpreter;
- require a valid `FROZEN` seal before launch;
- reject output paths inside `cases/confirmation/g4`;
- reject an existing run-label directory instead of overwriting it;
- capture raw stdout, stderr, exit code, UTC timestamps, elapsed time, command
  argv, cwd, Git branch/HEAD, freeze ID and status;
- compute byte SHA-256 and canonical-JSON SHA-256 where applicable;
- record timeout separately from a scientific failure;
- never retry automatically;
- compare primary and reproducibility captures by exact byte and canonical
  JSON hashes.

## Task 2: Implement Frozen-Rule Scoring

Create `src/ims_deadlock/g5_scoring.py` and
`tests/test_g5_scoring.py` using RED -> GREEN -> REFACTOR.

The scorer must:

- distinguish `execution_status` from `scientific_status`;
- return `SUPPORTED`, `FALSIFIED`, or `INCONCLUSIVE` per frozen case;
- require the exact nine-case universe and sealed hashes;
- implement the nine existing `predictions.json` rules without enabling a new
  metric;
- score grid cells against the exact
  `G01=false`, `G02=false`, `G03-G10=true` vector;
- fail a grid or medium prediction on truncation;
- report CTMC initial deadlock probability, mean absorption time, residuals,
  probability bounds, and case-derived provenance only for grid/medium;
- report each DES master seed separately, with no pooling;
- check whether each frozen 95% Wilson interval contains the exact CTMC
  probability;
- preserve all inapplicable metrics and non-reproduction claims;
- emit a deterministic compact JSON summary with raw-output hashes.

Missing fields or runtime errors are `INCONCLUSIVE`; a measured contradiction
to a frozen falsifier is `FALSIFIED`. The scorer must never synthesize an
observation from a log line.

Wilson coverage is a preregistered cross-check metric, not a falsifier of the
structural theorem prediction. A well-formed frozen interval that misses the
exact CTMC probability is retained and counted as a coverage miss; it does not
by itself change `theorem_prediction_correctness`.

## Task 3: Pre-execution Lock

Create `evidence/g5/G5_EXECUTION_LOCK.json` and commit it before the first
held-out run. It fixes:

- execution waves, preserving the listed order inside every recorded wave:
  - primary P1, at most four concurrent processes:
    L30, recorder, B05, CRP agreement;
  - primary P2, at most three concurrent processes:
    CRP unreachable, CRP outside-S4PR, adversarial;
  - primary P3, at most two concurrent processes:
    medium, grid;
  - reproducibility R1, R2, and R3 repeat the same wave membership only after
    all primary waves complete;
- one `primary` and one `repro` run per case;
- exact raw paths under the ignored task-owned directory
  `artifacts/g5-confirmation/G5-CONFIRMATION-20260730-R1`;
- 300-second hard timeout for exact/static cases;
- 1,800-second hard timeout for medium and grid;
- 30-second process-alive monitoring cadence;
- exact-match reproducibility for raw and canonical JSON hashes;
- stop on invalid freeze, hash drift, missing case, output overwrite,
  unexpected runtime, or unclassified execution error.

The scheduling choice was locked before held-out execution after a live Dell
resource probe reported one Intel Xeon w7-3465X with 28 physical cores,
56 logical processors, 127.25 GiB total memory, and 104.78 GiB free memory.
A separate pre-execution storage probe reported 5,693.04 GiB free on drive
`D:`.
Every scientific child remains single-process; there is no nested scientific
parallelism, no primary/repro overlap for the same case, and no change to a
case, stream, seed, replicate count, state bound, timeout, or scoring rule.
The lower caps for the state-heavy wave retain ample CPU and memory headroom.

## Task 4: Execute Primary Runs

Before every case:

1. verify remote path, branch, HEAD, clean state and `FROZEN`;
2. execute the exact frozen command through the capture layer;
3. record exit status and output hash;
4. do not retry a failure;
5. classify the failure before moving to the next case.

Run cheap exact waves first and the state-heavy/stochastic wave last. A wave
advances only after every member has a terminal capture record and each
failure, if any, has been classified. Monitor long-running commands at the
declared cadence.

## Task 5: Execute Reproducibility Runs

Run the same nine commands once under label `repro`, with unchanged runtime,
working directory, source commit, seeds and replicate counts.

- Deterministic and fixed-stream stochastic outputs must be byte-identical.
- Any mismatch is retained as a reproducibility failure.
- No third run, extra seed, pooled estimate or post-hoc tolerance is allowed.

## Task 6: Score And Validate

Generate:

- `evidence/g5/G5_RESULT_SUMMARY.json`;
- `evidence/g5/G5_RAW_HASH_MANIFEST.json`;
- `docs/verification/G5_CONFIRMATION_REPORT.md`;
- `docs/verification/G5_REPRODUCIBILITY_AUDIT.md`;
- `docs/verification/G5_CLAIM_EVIDENCE_TABLE.md`.

Required aggregate reporting:

- supported/falsified/inconclusive count over all nine cases;
- ten-cell grid agreement count;
- exact CTMC probabilities and mean absorption times;
- seed-specific DES estimates and Wilson intervals;
- exact-in-interval counts;
- certificate minimality and transport-resource membership where applicable;
- all baseline refusal and metric inapplicability decisions;
- any execution or claim-scope bug.

## Task 7: Independent Review And Paper Gate

Run independent:

1. result-schema and code-quality review;
2. scientific-method and frozen-claim review;
3. exact rerun/hash verification;
4. adversarial top-journal reviewer simulation.

G5 may pass only if:

- all frozen commands have one primary and one exact rerun record;
- no frozen artifact changed;
- every mismatch and negative result is retained;
- exact and DES results are reported under their frozen estimands;
- all manuscript claims are traceable to a theorem, frozen prediction, raw
  hash, and compact result field;
- the authoritative Dell test, Ruff, strict mypy, freeze, and Git checks pass.

If a result falsifies a prediction, keep it and narrow or revise the scientific
claim in G5-D. If an implementation bug is found, add a regression test and a
successor bug-fix ledger entry; do not edit the sealed input or silently rerun.
