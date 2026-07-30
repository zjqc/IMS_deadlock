# G6-B Protocol Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task-by-task.
> Each production-code change uses `superpowers:test-driven-development`.

**Goal:** Establish a machine-auditable, execution-disabled G6-B discovery
protocol foundation before any new scientific enumeration, CTMC solve, or DES
run.

**Architecture:** Add a strict six-document JSON bundle under
`cases/discovery/g6b/`, a validator that performs data-only parsing and
cross-document consistency checks, and a human-readable protocol that fixes the
scientific ontology and stop conditions. The validator must reject duplicate
keys, unknown keys, historical-case reuse, incomplete independence dimensions,
ambiguous `D_local` terminology, exact/DES target drift, missing negative
controls, and any attempt to authorize scientific execution before the
adversarial protocol review is recorded.

**Tech Stack:** Python 3.13, standard-library `json`, frozen dataclasses,
`hashlib.sha256`, pytest, Ruff, strict mypy.

**Scope boundary:** This plan creates and validates the protocol foundation
only. It does not create discovery models, inspect discovery outcomes, run a
scientific backend, create G6-C confirmation artifacts, or alter G4/G5/R1/R2/R3
evidence.

---

## File Responsibilities

- `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`: scientific definitions, independence
  rule, negative-control obligations, review gate, and execution stop rules.
- `cases/discovery/g6b/protocol.json`: bundle index, study role, historical
  authority references, and execution-disabled state.
- `cases/discovery/g6b/estimand_schema.json`: objective class ontology and the
  exact fields that every future estimand instance must freeze.
- `cases/discovery/g6b/independence_schema.json`: canonical fingerprint
  dimensions and zero-overlap rule against retired G4/G5 evidence.
- `cases/discovery/g6b/negative_controls.json`: mandatory refusal/classification
  controls that must exist before a discovery run can be admitted.
- `cases/discovery/g6b/failure_ledger.json`: append-only discovery failure
  ledger, initially empty and explicitly unable to authorize execution.
- `src/ims_deadlock/g6b_protocol.py`: data-only loader and strict validator; it
  must not import or call LTS, CTMC, DES, G4 execution, or historical replay
  entrypoints.
- `tests/test_g6b_protocol.py`: RED/GREEN tests for schema strictness,
  cross-document consistency, scientific boundaries, and execution refusal.
- `docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md`:
  historical-plan status correction so completed G6-R is not presented as
  pending after G6-B.
- `docs/cases/CASE_CHANGE_LEDGER.md`: durable record of the protocol-foundation
  batch and its no-scientific-execution boundary.
- `docs/ROADMAP.md`: point G6-B to the new protocol bundle while retaining its
  open status.

## Task 1: Correct The Historical Plan And Publish The Protocol Documents

**Files:**

- Modify:
  `docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md`
- Create: `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`
- Create: `cases/discovery/g6b/protocol.json`
- Create: `cases/discovery/g6b/estimand_schema.json`
- Create: `cases/discovery/g6b/independence_schema.json`
- Create: `cases/discovery/g6b/negative_controls.json`
- Create: `cases/discovery/g6b/failure_ledger.json`

- [ ] **Step 1: Correct the stale G6-R sequence without rewriting history**

Replace the recovery-plan status with:

```text
Status: G6-A PASS / G6-R PASS HISTORICAL-ONLY / G6-B NEXT HARD GATE /
NO G6-C/D/E HELD-OUT OUTPUT.
```

Add a note immediately after the status:

```text
Sequence update: the original draft placed G6-R after G6-B. Subsequent
preregistered R1/R2/R3 work executed G6-R after G6-A as an isolated
historical-only mechanism regression with no confirmation use. G6-R does not
satisfy G6-B, and G6-B remains the next hard gate.
```

Change the G6-R commit-topology heading to
`G6-R — Historical G4 Replay (completed historical-only)` and retain all
no-confirmation-use language.

- [ ] **Step 2: Write the human-readable protocol**

The document must state all of the following in normative language:

```text
study_role = discovery_only
confirmation_use = prohibited
D_local = verified first-hit bad set, not a plant terminal SCC
local candidate admission = A2b proof OR complete-LTS completion
nonreachability audit
exact/DES = same selected bad/success labels and the same versioned target
independence = zero overlap on eight canonical dimensions
scientific execution = disabled until adversarial review passes
```

It must enumerate the eight independence dimensions exactly:

```text
case_content_sha256
state_snapshot_sha256
route_signature_sha256
parameter_tuple_sha256
random_stream_manifest_sha256
output_root
sealed_prediction_sha256
metric_schema_sha256
```

It must define the mandatory controls:

```text
NC_LOCAL_BYPASS_COMPLETES
NC_UNSELECTED_LIVELOCK
NC_CALENDAR_EMPTY_TERMINAL
NC_POLICY_ONLY_STALL
NC_OR_OF_AND_FEASIBLE_BRANCH
NC_AGV_RESERVATION_BOUNDARY
NC_DGLOBAL_ONLY_WITH_DLOCAL
```

- [ ] **Step 3: Create the six-document JSON bundle**

Use these schema versions:

```json
{
  "protocol": "ims-deadlock/g6b-discovery-protocol/v1",
  "estimand": "ims-deadlock/g6b-estimand-schema/v1",
  "independence": "ims-deadlock/g6b-independence-schema/v1",
  "negative_controls": "ims-deadlock/g6b-negative-controls/v1",
  "failure_ledger": "ims-deadlock/g6b-failure-ledger/v1"
}
```

`protocol.json` must list the other five artifact filenames, declare
`scientific_execution_authorized=false`, declare
`adversarial_review_status="PENDING"`, and reference only tracked historical
authorities:

```text
cases/confirmation/g4/FREEZE_ENTRY.json
cases/confirmation/g4/case_manifest.json
cases/confirmation/g4/random_stream_manifest.json
cases/confirmation/g4/predictions.json
cases/confirmation/g4/metrics_schema.json
evidence/g5/G5_EXECUTION_LOCK.json
evidence/g5/G5_SCORING_ERRATUM.json
evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json
evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json
```

`failure_ledger.json` must use an empty `entries` list, set
`append_only=true`, and state that empty means “no discovery attempt has been
admitted,” not “no failures exist.”

- [ ] **Step 4: Validate the documents mechanically**

Run:

```bash
python -m json.tool cases/discovery/g6b/protocol.json
python -m json.tool cases/discovery/g6b/estimand_schema.json
python -m json.tool cases/discovery/g6b/independence_schema.json
python -m json.tool cases/discovery/g6b/negative_controls.json
python -m json.tool cases/discovery/g6b/failure_ledger.json
rg -n "D_local.*terminal SCC|confirmation_use.*allowed|scientific_execution_authorized.*true" \
  docs/cases/G6_B_DISCOVERY_PROTOCOL.md cases/discovery/g6b
```

Expected: all JSON parses; the fixed-string boundary scan finds only explicit
prohibitions or refusal examples.

- [ ] **Step 5: Commit the document foundation**

```bash
git add docs/superpowers/plans/2026-07-30-g6-local-core-terminal-class-recovery.md \
  docs/cases/G6_B_DISCOVERY_PROTOCOL.md cases/discovery/g6b
git commit -m "docs: define G6-B discovery protocol foundation"
```

## Task 2: Implement The Strict Data-Only Bundle Validator With TDD

**Files:**

- Create: `src/ims_deadlock/g6b_protocol.py`
- Create: `tests/test_g6b_protocol.py`

- [ ] **Step 1: Write the first RED test for the canonical bundle**

```python
from pathlib import Path

from ims_deadlock.g6b_protocol import validate_g6b_protocol_bundle


def test_repository_g6b_protocol_bundle_is_valid_and_execution_disabled() -> None:
    root = Path(__file__).parents[1] / "cases" / "discovery" / "g6b"
    result = validate_g6b_protocol_bundle(root)

    assert result.valid is True
    assert result.errors == ()
    assert result.scientific_execution_authorized is False
    assert result.adversarial_review_status == "PENDING"
```

- [ ] **Step 2: Run the test and confirm RED**

Run:

```bash
python -m pytest -p no:cacheprovider -q \
  tests/test_g6b_protocol.py::test_repository_g6b_protocol_bundle_is_valid_and_execution_disabled
```

Expected: collection fails because `ims_deadlock.g6b_protocol` does not exist.

- [ ] **Step 3: Implement the minimal public result and loader**

```python
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class G6BProtocolValidation:
    valid: bool
    errors: tuple[str, ...]
    scientific_execution_authorized: bool
    adversarial_review_status: str
    bundle_hashes: dict[str, str]


def validate_g6b_protocol_bundle(root: Path) -> G6BProtocolValidation:
    required_files = (
        "protocol.json",
        "estimand_schema.json",
        "independence_schema.json",
        "negative_controls.json",
        "failure_ledger.json",
    )
    documents: dict[str, dict[str, object]] = {}
    hashes: dict[str, str] = {}
    errors: list[str] = []
    for filename in required_files:
        path = root / filename
        try:
            payload = json.loads(
                path.read_text(encoding="utf-8"),
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{filename}: root must be an object")
            continue
        documents[filename] = payload
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        hashes[filename] = hashlib.sha256(encoded).hexdigest()

    protocol = documents.get("protocol.json", {})
    authorized = protocol.get("scientific_execution_authorized") is True
    review = protocol.get("adversarial_review_status")
    review_status = review if isinstance(review, str) else "INVALID"
    return G6BProtocolValidation(
        valid=not errors,
        errors=tuple(errors),
        scientific_execution_authorized=authorized,
        adversarial_review_status=review_status,
        bundle_hashes=dict(sorted(hashes.items())),
    )


def _reject_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result
```

The loader must use
`json.loads(text, object_pairs_hook=_reject_duplicate_keys)` to reject duplicate
keys, require exactly the expected filenames, and compute each canonical JSON
SHA-256 using sorted keys and compact separators.

- [ ] **Step 4: Run the canonical-bundle test and confirm GREEN**

Run the Step 2 command.

Expected: `1 passed`.

- [ ] **Step 5: Add RED tests for strict cross-document boundaries**

Add parametrized mutations that require these error codes or stable substrings:

```text
unknown top-level key
duplicate JSON key
unsupported schema_version
missing required independence dimension
D_local ontology is not first_hit_bad_set_not_terminal_scc
exact/DES selected targets differ
missing mandatory negative control
historical authority path is untracked or absolute
scientific execution cannot be authorized while review is PENDING
failure ledger must be append-only
```

Each mutation must copy the repository bundle into `tmp_path`, change only one
field, run the validator, and assert `valid is False` plus the expected error.

- [ ] **Step 6: Run the strict tests and confirm RED**

Run:

```bash
python -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py
```

Expected: the new mutation tests fail because the cross-document checks are not
implemented.

- [ ] **Step 7: Implement the minimal strict checks**

Use exact-key helpers and constants:

```python
G6B_PROTOCOL_SCHEMA_VERSION = "ims-deadlock/g6b-discovery-protocol/v1"
G6B_ESTIMAND_SCHEMA_VERSION = "ims-deadlock/g6b-estimand-schema/v1"
G6B_INDEPENDENCE_SCHEMA_VERSION = "ims-deadlock/g6b-independence-schema/v1"
G6B_NEGATIVE_CONTROLS_VERSION = "ims-deadlock/g6b-negative-controls/v1"
G6B_FAILURE_LEDGER_VERSION = "ims-deadlock/g6b-failure-ledger/v1"
```

The module must remain data-only. Its imports may include only standard-library
modules and local value-free helpers; it must not import `analysis`, `ctmc`,
`stochastic`, `g4_protocol`, `g4_instances`, or `historical_replay`.

- [ ] **Step 8: Run targeted and adjacent tests**

Run:

```bash
python -m pytest -p no:cacheprovider -q \
  tests/test_g6b_protocol.py tests/test_terminal_classes.py \
  tests/test_g4_protocol.py tests/test_g4_freeze.py
```

Expected: all selected tests pass.

- [ ] **Step 9: Run static checks for the new module**

```bash
python -m ruff check --no-cache src/ims_deadlock/g6b_protocol.py \
  tests/test_g6b_protocol.py
python -m ruff format --check --no-cache src/ims_deadlock/g6b_protocol.py \
  tests/test_g6b_protocol.py
python -m mypy --no-incremental --strict src/ims_deadlock/g6b_protocol.py \
  tests/test_g6b_protocol.py
```

Expected: all checks pass.

- [ ] **Step 10: Commit the validator**

```bash
git add src/ims_deadlock/g6b_protocol.py tests/test_g6b_protocol.py
git commit -m "feat: validate G6-B discovery protocol bundle"
```

## Task 3: Integrate The Protocol Foundation Into Project State

**Files:**

- Modify: `docs/cases/CASE_CHANGE_LEDGER.md`
- Modify: `docs/ROADMAP.md`
- Modify: `PROJECT_HANDOFF.md`

- [ ] **Step 1: Record the batch without upgrading G6-B**

Add a ledger entry that records:

```text
G6-B protocol foundation created
scientific execution performed = false
discovery cases created = false
G6-B status = OPEN
G6-C/D/E status = NOT STARTED
historical evidence changed = false
```

- [ ] **Step 2: Update roadmap and handoff source-of-truth paths**

Add the protocol bundle and validator paths to the G6-B sections. Retain:

```text
G6-B = NEXT HARD GATE / OPEN
G6-R = PASS historical replay only
no new scientific output inspected
```

- [ ] **Step 3: Run full repository verification**

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q
PYTHONDONTWRITEBYTECODE=1 python -m ruff check --no-cache src tests
PYTHONDONTWRITEBYTECODE=1 python -m ruff format --check --no-cache src tests
PYTHONDONTWRITEBYTECODE=1 python -m mypy --no-incremental --strict src
PYTHONDONTWRITEBYTECODE=1 python -m mypy --no-incremental --strict \
  --explicit-package-bases src tests
git diff --check
```

Expected: full pytest, Ruff check/format, both strict mypy commands, and diff
check pass.

- [ ] **Step 4: Run protocol-specific integrity checks**

```bash
python -m json.tool cases/discovery/g6b/protocol.json >/dev/null
python -m json.tool cases/discovery/g6b/estimand_schema.json >/dev/null
python -m json.tool cases/discovery/g6b/independence_schema.json >/dev/null
python -m json.tool cases/discovery/g6b/negative_controls.json >/dev/null
python -m json.tool cases/discovery/g6b/failure_ledger.json >/dev/null
python -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py
```

Expected: all JSON and protocol tests pass.

- [ ] **Step 5: Commit the state integration**

```bash
git add docs/cases/CASE_CHANGE_LEDGER.md docs/ROADMAP.md PROJECT_HANDOFF.md
git commit -m "docs: register open G6-B protocol gate"
```

## Final Review Gate

After Tasks 1-3:

1. Run a specification-compliance review against this plan.
2. Run a code-quality review of the validator and tests.
3. Run an independent scientific-boundary review that checks:
   - `D_local` is never a terminal-SCC claim;
   - A2b and full-LTS bypass handling are not conflated;
   - the eight independence dimensions are complete;
   - exact/DES target identity is a hard gate;
   - historical G4/G5/R1/R2/R3 evidence is referenced but unchanged;
   - execution remains disabled.
4. Fix all critical and important findings and re-run the relevant review.
5. Only after all three reviews pass may a separate plan define discovery
   model construction and small-scale scientific execution.
