# G6-B Row-Family Protocol Review

Date: 2026-07-31

This document records Phase A state integration evidence, Phase B independent
review verdicts, and Phase C post-commit verification evidence for the G6-B
row-family protocol. It is not a scientific result, not a case-construction
authorization, and not an execution-runtime lock.

## Earlier Phase A Target And Runtime

```text
target path = D:\worktree\IMS_deadlock-g6b-discovery
branch = codex/g6b-discovery-estimand-lock
HEAD = 4fda4896d2284c360f3021e48475f7678b0f37fd
upstream = NO_UPSTREAM
candidate dirty scope = PROJECT_HANDOFF.md; docs/ROADMAP.md;
  docs/cases/CASE_CHANGE_LEDGER.md;
  docs/superpowers/plans/2026-07-31-g6b-row-family-protocol.md;
  untracked docs/verification/G6_B_ROW_FAMILY_PROTOCOL_REVIEW.md
Python = D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python version = 3.13.9
PYTHONPATH = D:\worktree\IMS_deadlock-g6b-discovery\src
PYTHONDONTWRITEBYTECODE = 1
pytest = -p no:cacheprovider
Ruff = --no-cache
mypy = --no-incremental
```

The `4fda4896d2284c360f3021e48475f7678b0f37fd` evidence above is earlier
Phase A evidence from before the first documentation commit. It is retained for
traceability and is not the current committed target.

## Earlier Phase A Verification Commands

| Check | Command | Result |
| --- | --- | --- |
| Full pytest | `python -m pytest -p no:cacheprovider -q` | `1307 passed in 150.84s` |
| Ruff check | `python -m ruff check --no-cache src tests` | `All checks passed!` |
| Ruff format | `python -m ruff format --check --no-cache src tests` | `43 files already formatted` |
| Strict mypy src | `python -m mypy --no-incremental --strict src` | `Success: no issues found in 23 source files` |
| Strict mypy src tests | `python -m mypy --no-incremental --strict --explicit-package-bases src tests` | `Success: no issues found in 43 source files` |
| Clean-tree whitespace | `git diff --check` | passed before documentation edits |
| Nested JSON parse | `python -m json.tool` on all nested files | 8/8 parsed |
| Top-level foundation suite | `python -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py` | `52 passed in 5.00s` |
| Canonical row-family test | `python -m pytest -p no:cacheprovider -q tests/test_g6b_row_family_protocol.py::test_canonical_row_family_bundle_is_valid_and_disabled` | `1 passed in 0.12s` |
| Canonical validator | `validate_g6b_row_family_bundle(...)` | `valid=True`, errors empty, `science=False`, `case=False`, `adversarial_review_status=PENDING`, `current_state=ROW_FAMILY_BUNDLE_IMPLEMENTED`, 8 hashes |
| Recursive authorization scan | exact-eight nested JSON scan | 8 scientific authorization occurrences all false; 18 case authorization occurrences all false; both review-status occurrences `PENDING` |
| Task 1-7 implementation diff | `git diff --name-only a4897ab..4fda489` | only exact-eight nested JSON, `src/ims_deadlock/g6b_row_family_protocol.py`, and `tests/test_g6b_row_family_protocol.py` |
| Task-owned mypy cache cleanup | directory absence check | `D:\worktree\_task8_mypy_src_cache` and `D:\worktree\_task8_mypy_src_tests_cache` absent |

## Phase C Post-Commit Verification

These checks were collected on committed HEAD
`13adc15e8b7b8047a25ab5a340880621ee3ad0bd`, subject
`docs: record G6-B row-family protocol gate`.

```text
target path = D:\worktree\IMS_deadlock-g6b-discovery
branch = codex/g6b-discovery-estimand-lock
HEAD = 13adc15e8b7b8047a25ab5a340880621ee3ad0bd
upstream = NO_UPSTREAM
dirty state = clean
Python = D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python version = 3.13.9
```

| Check | Result |
| --- | --- |
| Full pytest | `1307 passed in 144.93s (0:02:24)` |
| Ruff check | `All checks passed!` |
| Ruff format | `43 files already formatted` |
| Strict mypy src | `Success: no issues found in 23 source files` |
| Strict mypy src tests | `Success: no issues found in 43 source files` |
| `git diff --check` | passed |
| Top-level foundation suite | `52 passed in 9.87s` |
| Canonical row-family test | `1 passed in 0.09s` |
| Nested JSON parse | 8/8 parsed |
| Top-level G6-B JSON set | exact five |
| Nested row-family JSON set | exact eight |
| Foundation validator | valid, 0 errors, science false, `PENDING`, 5 hashes |
| Row-family validator | valid, 0 errors, science false, case false, `PENDING`, `ROW_FAMILY_BUNDLE_IMPLEMENTED`, 8 hashes |
| Recursive 13-JSON scan | `non_false_auth=0`, `non_pending_status=0` |
| Base diff forbidden paths and actual marker scan | `forbidden_paths=0`, `actual_marker_hits=0` |
| Relevant output roots | absent |
| Task mypy cache directories | absent |
| Independent review verdicts | specification `APPROVED`; code quality `APPROVED`; scientific boundary `PASS PROTOCOL ONLY` |

## Artifact Inventory

- Top-level `cases/discovery/g6b/` JSON set is exactly five:
  `estimand_schema.json`, `failure_ledger.json`,
  `independence_schema.json`, `negative_controls.json`, `protocol.json`.
- Nested row-family JSON set is exactly eight:
  `failure_ledger.json`, `identity_schema.json`,
  `overlap_report_schema.json`, `reuse_matrix.json`, `review_state.json`,
  `row_family_matrix.json`, `row_family_protocol.json`,
  `runtime_lock_schema.json`.
- `row_families/` contains exactly one `structural_discovery_v1/` directory and
  that directory contains only the exact-eight JSON files above.
- Nested bundle status is `IMPLEMENTED / DATA-ONLY`.
- `case_creation_authorized=false` everywhere in the exact-eight bundle.
- `scientific_execution_authorized=false` everywhere in the exact-eight bundle.
- Bundle `adversarial_review_status` remains `PENDING` and must not be changed
  by this review document.
- Actual overlap report is absent.
- Overlap-authority lock is absent.
- Execution-runtime lock is absent.
- Discovery cases and discovery outcomes are absent.
- No output root, result/science summary, enumeration output, CTMC output, DES
  output, or science artifact exists.
- The Task 1-7 diff from `a4897ab` through `4fda489` introduced no case
  artifact, actual overlap report/value, current lock, output root,
  result/science summary, enumeration, CTMC, or DES artifact.
- Historical G4/G5/R1/R2/R3 evidence changed = false.

## Claim Boundary

The implemented row-family protocol is a machine-auditable data protocol only.
Canonical validation means the disabled protocol bundle is structurally valid;
it is not scientific evidence, does not prove independence by actual overlap,
does not authorize case construction, and does not authorize science execution.

The independent reviews below approve only the protocol specification,
data-only code boundary, and scientific-boundary wording. They do not change
the JSON bundle state, authorize case construction, authorize science, or make
G6-B pass.

G6-B remains `OPEN`. G6-C, G6-D, and G6-E remain `NOT STARTED`. The only
permitted successor after the final gate is a separately approved
case-construction plan.

## Open Gates

- No case-construction plan has been approved.
- No case artifact, actual overlap value, current lock, output root,
  enumeration, CTMC, DES, or science summary exists.
- Bundle `adversarial_review_status` remains `PENDING`; review verdicts remain
  separate from the implemented JSON bundle state.
- The final allowed reviewer scientific verdict remains `PASS PROTOCOL ONLY`.

## Verdicts

Specification compliance review: `APPROVED`; no blockers.

Code-quality review: `APPROVED`; no Critical/Important/Minor blockers.

Scientific-boundary review: `PASS PROTOCOL ONLY`; no blockers.
