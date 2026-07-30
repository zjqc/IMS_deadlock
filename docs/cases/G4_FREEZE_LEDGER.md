# G4 Freeze Ledger

Status: `SEALED / FROZEN`.

This ledger is an append-only audit surface for the G4 confirmation freeze.
It contains no held-out scientific outcome. A row may advance to `SEALED` only
after the prerequisite commit and every canonical artifact hash are recorded in
`cases/confirmation/g4/FREEZE_ENTRY.json`.

## Implementation Baseline

- Branch: `codex/g4-confirmation-freeze`.
- Implementation commit:
  `f9b9a5a5652c7a49053e7ef26d08911bd757f465`.
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

The earlier preregistration candidate
`a71f623ec0b6c597ec7339a335137c78ed336cb7` is retained as `B1-SUPERSEDED`.
An adversarial pre-seal review showed that its prospective seal checker did not
enforce the contents of `excluded_cases`. No C seal or held-out execution was
committed. The implementation above closes that gap; the next preregistration
commit was B2
`58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`, which refreshed every
implementation-dependent hash.

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

At candidate time the preregistration commit was intentionally left pending.
It was filled only after the complete bundle was structurally validated,
committed, and pushed; the immutable value is recorded in the seal below.

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

- Implementation commit A:
  `f9b9a5a5652c7a49053e7ef26d08911bd757f465`.
- Preregistration commit B2:
  `58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`.
- Seal commit C:
  `e91be4d6d7511c76918093899269de4b78e69fd8`.
- Freeze ID: `G4-FREEZE-C-20260730T051210Z`.
- Freeze time: `2026-07-30T05:12:10Z`.
- Exact seal:
  `cases/confirmation/g4/FREEZE_ENTRY.json`.
- The seal records all nine case canonical hashes, all nine prerequisite
  artifact hashes, the exact nine included cases, and exact discovery
  exclusions `C0-C5`, `C5_DAG`, `BIX1-SAT`, and `BIX2-PERSIST`.
- Dell post-commit checker evidence:
  `FROZEN`, `errors=[]`, `confirmation_results_inspected=false`.
- Structural protocol evidence:
  nine cases valid under
  `structural_only_no_scientific_execution`.
- Quality evidence before C:
  `187 passed`, Ruff check/format passed, strict mypy passed.
- Quality evidence after C:
  51 freeze/confirmation/protocol tests passed.
- Independent code, scientific-boundary, and static-hash reviews all returned
  `PASS`.

No held-out scientific backend was executed before or during the seal. The
frozen cases also remain scientifically uninspected after C; executing them is
a separate G5 action governed by the frozen commands and immutable reporting
rules.

If pre-seal validation finds a defect, repair it before the preregistration
commit and record the repair in the execution plan. If any outcome is inspected
after sealing, the frozen inputs may not be replaced; a scientifically
necessary change requires a successor freeze with an explicit supersession
reason.
