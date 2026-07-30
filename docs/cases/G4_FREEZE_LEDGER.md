# G4 Freeze Ledger

Status: `PREREGISTRATION-CANDIDATE / NOT SEALED`.

This ledger is an append-only audit surface for the G4 confirmation freeze.
It contains no held-out scientific outcome. A row may advance to `SEALED` only
after the prerequisite commit and every canonical artifact hash are recorded in
`cases/confirmation/g4/FREEZE_ENTRY.json`.

## Implementation Baseline

- Branch: `codex/g4-confirmation-freeze`.
- Implementation commit:
  `2a89fe1409d5000225e22499878454e964c01363`.
- Runtime authority:
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`.
- Structural parser:
  `ims_deadlock.g4_protocol:validate_bundle_protocols`.
- Freeze checker:
  `ims_deadlock.g4_freeze:check_g4_freeze`.
- Post-freeze dispatcher:
  `ims_deadlock.g4_protocol:run_after_freeze`.

The implementation commit precedes the held-out preregistration commit. It
contains the protocol decoder, deterministic case generators, CTMC derivation,
freeze checker, development fixtures, proof obligations, regression tests, and
LF normalization needed for checkout-stable file-byte hashes.

## Candidate Bundle

- Nine held-out G4 cases are declared in `case_manifest.json`.
- `G4_IMS_PARAMETER_GRID` contains ten exact, named cells with one Boolean
  reachable-closed-core prediction per cell.
- Stochastic execution is applicable only to the parameter grid and medium
  rebuild; every other case is exact-only.
- Supervisor cost, conditioned path mass, and rare-event efficiency are frozen
  as inapplicable for this confirmation tranche.
- Discovery cases `C0-C5`, `C5_DAG`, `BIX1-SAT`, and `BIX2-PERSIST` are
  explicitly excluded.

The preregistration commit is intentionally left pending in this candidate
ledger. It will be filled only after the complete bundle is structurally
validated, committed, and pushed.

## Pre-Seal Allowed Operations

Only the following operations may inspect the candidate bundle:

1. JSON parsing and canonical hashing;
2. `python -m ims_deadlock.g4_protocol --root cases/confirmation/g4 validate`;
3. `python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check`;
4. development/schema tests that use synthetic fixtures and assert that
   scientific entrypoints are not called;
5. static formatting, type checking, Git diff review, and file-byte hashing.

`g4_protocol run`, public analysis/quantification/simulation commands, direct
calls to a case generator followed by reachability analysis, and inspection of
any held-out output are prohibited until the seal commit exists and the freeze
checker returns `FROZEN`.

## Seal Record

Pending fields:

- preregistration commit;
- seal commit;
- freeze identifier and UTC timestamp;
- nine case hashes;
- nine prerequisite artifact hashes;
- final `FROZEN` checker evidence.

If pre-seal validation finds a defect, repair it before the preregistration
commit and record the repair in the execution plan. If any outcome is inspected
after sealing, the frozen inputs may not be replaced; a scientifically
necessary change requires a successor freeze with an explicit supersession
reason.
