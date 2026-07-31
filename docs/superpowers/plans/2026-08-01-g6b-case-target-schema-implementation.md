# G6-B Case-Target Schema Implementation Plan

Status: `APPROVED WRITTEN SPEC -> SCHEMA-ONLY IMPLEMENTATION PLAN /
EXECUTION-DISABLED / NO CASE CREATION`.

> **For agentic workers:** implement task-by-task. Every code or schema task
> starts with failing tests and ends with targeted validation before moving to
> the next task.

## Goal

Implement the approved G6-B case-construction, retired-authority overlap,
target-certification, and quantitative-authorization governance schema as a
machine-auditable, execution-disabled bundle.

The implementation must make later gates representable and testable. It must
not create discovery cases, enumerate states, certify a target, construct or
solve a CTMC, run DES, inspect outputs, authorize science, or mark G6-B as
passed.

Approved written spec:
`docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`
at or after commit `c846383b39335bf66133a39d64722e43c2d69d85`.

## Ontology Lock

Use these normalized meanings throughout the implementation:

- `case unit`: one planned scientific input unit; exact and DES companions are
  not separate cases.
- `method observation`: one method attached to one case unit.
- `method companion group`: the exact/DES comparability object that controls
  shared target and metric-schema reuse.
- `subject_free_comparison_payload`: the projection compared against retired
  authorities.
- `record_identity_envelope`: traceability metadata; never evidence of
  retired-authority non-reuse by itself.
- `output_root_reservation_sha256`: containment-only provenance reservation,
  not semantic case identity.
- `target-certification preflight`: result-bearing eligibility evidence; not
  quantitative science and not theorem validation.

Reject any implementation that lets a new bundle/case/method ID, filename,
path, display name, author, timestamp, review ID, or new provenance label
change a subject-free semantic comparison hash.

## Authorized Scope

This plan may modify only:

- `cases/discovery/g6b/*.json`;
- `cases/discovery/g6b/row_families/structural_discovery_v1/*.json`;
- `src/ims_deadlock/g6b_protocol.py`;
- `src/ims_deadlock/g6b_row_family_protocol.py`;
- `tests/test_g6b_protocol.py`;
- `tests/test_g6b_row_family_protocol.py`;
- `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md`
  only for implementation-discovered consistency corrections;
- `docs/superpowers/plans/2026-08-01-g6b-case-target-schema-implementation.md`;
- `docs/verification/G6_B_CASE_TARGET_SCHEMA_REVIEW.md`;
- `docs/cases/CASE_CHANGE_LEDGER.md`;
- `docs/ROADMAP.md`; and
- `PROJECT_HANDOFF.md`.

Any additional file requires a written rationale in the commit message and the
review record.

## Stop Boundary

Stop immediately before or on any attempt to:

- create a future `case_unit` instance;
- create a case input, route signature, parameter tuple, sealed prediction, or
  random stream for an actual case;
- materialize an output root or preflight evidence root;
- run LTS enumeration, terminal partitioning, target certification, CTMC, DES,
  G4/G5 execution, or G6-R replay;
- set `case_creation_authorized`, `target_certification_preflight_authorized`,
  or `quantitative_execution_authorized` to true;
- advance `adversarial_review_status` past `PENDING`; or
- state that G6-B, G6-C, G6-D, or G6-E passed.

## Runtime And Target Lock

Use direct SSH to the remote worktree unless a later instruction changes the
channel. Before Task 1, lock:

```text
TARGET_PATH=D:\worktree\IMS_deadlock-g6b-case-target-design
TARGET_BRANCH=codex/g6b-case-target-certification-design
REQUIRED_SPEC_ANCESTOR=c846383b39335bf66133a39d64722e43c2d69d85
REMOTE=git@github.com:zjqc/IMS_deadlock.git
PYTHON=D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
PYTHONPATH=D:\worktree\IMS_deadlock-g6b-case-target-design\src
PYTHONDONTWRITEBYTECODE=1
```

The target must be clean, on the named branch, and contain the required spec
ancestor. Do not continue from the local snapshot or another worktree.

## Task 1: Red Tests For Schema File Set And Authorization State

Files:

- `tests/test_g6b_protocol.py`
- `tests/test_g6b_row_family_protocol.py`

- [ ] Add tests proving the current top-level G6-B bundle remains
  execution-disabled and `PENDING`.
- [ ] Add tests proving the nested row-family schema set is exact for its
  schema version and will become exact eleven after the new schema files are
  added.
- [ ] Add tests rejecting schema files that contain actual case instances,
  target-certification results, current runtime locks, output roots, overlap
  results, or authorization flags set to true.
- [ ] Add tests proving versioned validators fail closed on unknown keys,
  duplicate keys, missing files, stale artifact paths, and mixed v1/v2 file-set
  meanings.

Acceptance for Task 1: tests fail for the current implementation for the
expected missing v2 schema behavior and do not fail because of environment or
import errors.

## Task 2: Red Tests For Subject-Free Fingerprints

Files:

- `tests/test_g6b_row_family_protocol.py`

- [ ] Add fixture records for `case_content_sha256`,
  `state_snapshot_sha256`, `route_signature_sha256`,
  `parameter_tuple_sha256`, `random_stream_manifest_sha256`,
  `output_root_reservation_sha256`, `sealed_prediction_sha256`, and
  `metric_schema_sha256`.
- [ ] Assert that changing only governance IDs, paths, filenames, display
  names, authors, timestamps, review IDs, or new provenance labels does not
  change subject-free projections.
- [ ] Assert that changing scientific content changes the relevant projection.
- [ ] Assert that a renamed retired input with the same projection produces
  `semantic_identity_reuse` or `rename_shift_refused`, not `pass_distinct`.
- [ ] Assert that correlated dimensions record dependencies and are not counted
  as independent case identities.
- [ ] Assert that exact methods produce
  `not_applicable_by_protocol_pass` for the random-stream dimension rather than
  random-process independence.
- [ ] Assert that output-root reservations are
  `provenance_containment_only` and cannot repair semantic overlap.

Acceptance for Task 2: every subject-free/evelope category mistake has a
failing test before production code changes.

## Task 3: Add Schema-Only JSON Contracts

Files:

- `cases/discovery/g6b/protocol.json`
- `cases/discovery/g6b/independence_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/target_certification_schema.json`
- `cases/discovery/g6b/row_families/structural_discovery_v1/quantitative_authorization_schema.json`

- [ ] Version-bump changed meanings to v2, preserving current instance values
  as false/PENDING/open.
- [ ] Add exact `case_construction_schema.json` with the fingerprint record,
  payload schema, companion-group, nested-field, dependence, and output-root
  reservation contracts from the written spec.
- [ ] Add exact `target_certification_schema.json` with preflight runtime-lock,
  authorization, result, forbidden-call, forbidden-field, semantic-lineage, and
  source-projection-map contracts.
- [ ] Add exact `quantitative_authorization_schema.json` with same-target lock,
  companion-group, output-root-reservation, scope, and no-wildcard contracts.
- [ ] Update the nested artifact manifest from exact eight to exact eleven for
  the v2 row-family protocol.
- [ ] Keep every new file schema-only. No instance record may contain
  `authorized = true`.

Acceptance for Task 3: JSON parse checks with duplicate-key rejection pass;
tests still fail only where validator support is intentionally missing.

## Task 4: Implement Data-Only Validators

Files:

- `src/ims_deadlock/g6b_protocol.py`
- `src/ims_deadlock/g6b_row_family_protocol.py`

- [ ] Update document registries and exact file-set validators.
- [ ] Validate the top-level typed capability object and refuse legacy broad
  science-authorization as a transition key.
- [ ] Validate every fingerprint record's subject, projection kind,
  comparison policy, dependency/correlation fields, and no-extra-fields rule.
- [ ] Validate subject-free projection contamination rules.
- [ ] Validate lineage-deduplicated retired-authority admission statuses.
- [ ] Validate method companion groups and controlled metric-schema reuse.
- [ ] Validate output-root reservation objects as containment-only and
  unmaterialized.
- [ ] Validate state-machine vocabularies and count reconciliation without
  creating instance states.
- [ ] Keep validators data-only: no imports or calls to LTS, CTMC, DES, G4/G5
  execution, historical replay, target-certification runner, or output writers.

Acceptance for Task 4: focused tests pass without any scientific execution
surface imported or called.

## Task 5: Review Record, Roadmap, And Handoff

Files:

- `docs/verification/G6_B_CASE_TARGET_SCHEMA_REVIEW.md`
- `docs/cases/CASE_CHANGE_LEDGER.md`
- `docs/ROADMAP.md`
- `PROJECT_HANDOFF.md`

- [ ] Record the exact target path, branch, start/end HEAD, changed files,
  validation commands, and no-case/no-science boundary.
- [ ] State explicitly that the result is schema implementation only:
  G6-B remains open, adversarial review remains pending unless separately
  reviewed, and no target preflight or quantitative execution is authorized.
- [ ] Preserve every negative/boundary finding: subject-ID contamination risk,
  rename reuse risk, output-root containment boundary, exact-method
  not-applicable random stream, metric-schema controlled reuse, and
  target-certification circularity.
- [ ] Update the handoff as the next durable continuation entry point.

Acceptance for Task 5: documentation claims match the validator state exactly.

## Final Verification

Run from the locked remote worktree with the qualified runtime:

```cmd
set PYTHONDONTWRITEBYTECODE=1
set PYTHONPATH=D:\worktree\IMS_deadlock-g6b-case-target-design\src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m ruff check --no-cache src tests
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m ruff format --check --no-cache src tests
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m mypy --no-incremental --strict src
D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m mypy --no-incremental --strict --explicit-package-bases src tests
git diff --check
git status --porcelain=v1 -b
```

Do not report success unless the final branch is clean after commit and push.

## Claim Boundary

Allowed claim after this plan is fully implemented:

```text
The G6-B case-target governance schema validates as execution-disabled,
subject-aware, lineage-deduplicated, and capability-separated. No case,
target-certification preflight, quantitative execution, or G6-B verdict is
authorized.
```

Forbidden claims:

- G6-B passed;
- the new cases are independent;
- zero overlap across eight independent dimensions;
- exact and DES are two independent cases;
- target certification validates the theorem; or
- schema implementation makes the project top-journal ready.
