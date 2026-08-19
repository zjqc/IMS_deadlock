# T-ASE Hardening Panel Implementation Plan

Status: `PLAN / AWAITING EXACT USER APPROVAL / NO IMPLEMENTATION`
Revision: `compute-parallel-v2` — supersedes unapproved `7cc80339…8eec`
Spec: `docs/superpowers/specs/2026-08-19-tase-hardening-panel-design.md`
Preregistration: `docs/cases/TASE_HARDENING_PREREGISTRATION.md`

> After approval, implement with TDD in
> `D:\worktree\IMS_deadlock-journal-hardening-v1` only.

**Goal:** After exact hash approval, add a fail-closed runner and sealed
inputs for families H1–H4. Do not execute science in the same commit that
creates case JSON.

**Global constraints:** all authorization flags false until a later hashed
authorization object; never write article-core v1 or G4/G5/G6 evidence;
`PYTHONPATH` must point at this worktree; scientific runs must follow
spec Section 12 (live probe, 32 default / 48 max workers, BLAS threads
= 1, shard files, primary-before-repro).

## Task T0 — Approval gate

- [ ] User names `approved_spec_sha256`, `approved_plan_sha256`, and
      `approved_review_sha256`.
- [ ] Re-lock the journal-hardening worktree. If spec/plan bytes differ,
      stop.

No other task may start before T0.

## Task T1 — Failing authorization and identity tests

**Files:**
- Create: `tests/test_tase_hardening.py`
- Create: `src/ims_deadlock/tase_hardening.py`

- [ ] Write tests that:
  - parse the spec scope id `tase_hardening_v1`
  - assert all five authorization flags are false
  - reject a fixture hash equal to the article-core scope-lock self SHA-256
    `86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660`
  - refuse quantitative entry points
  - clamp worker counts to the Section 12 formula
  - set BLAS/OpenMP thread env to 1 when workers >= 8
  - reject a run that would overlap primary and repro of one case
  - reject two reducers on one manifest
- [ ] Run the tests and confirm they fail (module missing).
- [ ] Add the minimal module that makes those tests pass and still cannot
      run CTMC/DES.
- [ ] Commit: `test: lock tase-hardening authorization and nonreuse`

## Task T2 — H1 structural witnesses, still no science

- [ ] Add failing tests for the four H1 expected outcomes listed in the spec.
- [ ] Materialize `cases/discovery/tase_hardening_v1/h1/` only after T1 is
      green and T0 remains valid.
- [ ] Implement classifiers/refusals using existing `certificates`,
      `engine`, and `terminal_classes` APIs. Do not add a new deadlock
      semantics.
- [ ] Commit: `feat: materialize H1 theory-hardening witnesses`

## Task T3 — H2 baseline harness

- [ ] Add failing tests for the four methods and the six predeclared
      metrics on a residual-cycle plant and an `IMS-SIP^1` plant.
- [ ] Implement adapters that wrap existing cycle/SCC, closed-core,
      `petri.try_sip1_bridge`, and complete-LTS truth.
- [ ] Schedule the 32 plants with a process pool; one plant per worker;
      four methods stay in-process on that plant’s LTS.
- [ ] Commit: `feat: add same-semantics baseline harness`

## Task T4 — H3 scale family with caps

- [ ] Add failing tests that a 100_001-state or 301-second row is refused.
- [ ] Implement the 576-row product with those caps.
- [ ] Implement a process-pool scheduler that writes one shard per row
      and never shares a writable JSON.
- [ ] Add a test that a forced `workers=1` launch is refused when the
      probe fixture reports 56 logical CPUs and 64 GiB free RAM.
- [ ] Commit: `feat: add capped H3 scale family`

## Task T5 — H4 island spec materialization, no DES yet

- [ ] Add failing tests that H4 carries routes, BAS, AGV/reservation,
      one intervention, and the synthetic-digital-twin label.
- [ ] Materialize H4 inputs only.
- [ ] Commit: `feat: materialize H4 synthetic island inputs`

## Task T6 — Separate quantitative authorization

- [ ] A new hashed authorization object is required. This plan does not
      contain it.
- [ ] Only after that object is approved: Barrier A for both H4 plants
      in parallel; exact solves in parallel; DES primary shards (65536
      replications, sharded) in parallel; then the repro wave.
- [ ] One reducer writes `evidence/tase_hardening/v1/` after each wave
      is complete. Partial shard sets are failed waves.
- [ ] Verification suites may use up to 16 xdist workers already present
      in the qualified venv. Do not install packages.
- [ ] Theory correction, if any, is a later commit with a new version id.

## Stop conditions

Stop if T0 is missing, if a test is made green by deleting a negative
case, if H5 is implemented without a spec amendment, if any commit
touches `evidence/article_core/`, or if a scientific entry point has no
worker-clamp / shard-isolation tests.
