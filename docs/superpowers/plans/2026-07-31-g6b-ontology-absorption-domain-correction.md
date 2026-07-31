# G6-B Ontology and Absorption-Domain Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the heterogeneous G6-B objective registry with a typed
ontology, distinguish support-graph reachability from probability-one
absorption, and make every current CTMC construction fail closed unless a
versioned finite positive-rate absorption-domain certificate covers the full
claimed nonabsorbing domain.

**Architecture:** Keep plant classification, policy analysis, structural
reachability, and probabilistic absorption as separate typed layers. Build the
v3 plant partition first; certify the stopped positive-rate graph with a pure
SCC/reverse-basin function; attach that immutable certificate before generator
construction; keep v2 historical payloads readable only through an explicit
legacy reader; and migrate the execution-disabled G6-B schema and row-family
matrix to the corrected identities without creating cases or running science.

**Tech Stack:** Python 3.13, stdlib `dataclasses`/`hashlib`/`json`/`pathlib`,
pytest, Ruff, strict mypy, Git, and direct Tailscale SSH to the authoritative
Windows worktree.

Skill routing note: this plan preserves the canonical `superpowers:` handoff
header required by the plan format. In the current Codex catalog, invoke the
installed aliases `subagent-driven-development` or `executing-plans`.

---

## Frozen Design, Scope, and Stop Boundary

Approved design:
`docs/superpowers/specs/2026-07-31-g6b-ontology-absorption-domain-correction-design.md`.

The implementation base is commit
`d0a8dca2bd735d39f16d060c545d13ce85029f60` or a later descendant containing
that commit. Re-read the live hash before Task 1; if the abbreviated value
`d0a8dca` does not resolve to the full value recorded above, record the live
full value and stop before editing because the plan identity is inconsistent.

This plan may modify only:

- `cases/discovery/g6b/estimand_schema.json`;
- `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`;
- `src/ims_deadlock/g6b_protocol.py`;
- `src/ims_deadlock/terminal_classes.py`;
- `src/ims_deadlock/g4_instances.py`;
- `src/ims_deadlock/g4_protocol.py` when a failing consumer test proves a
  nested-contract update is needed;
- `src/ims_deadlock/historical_replay.py` only for version-aware reading of
  already captured terminal payloads;
- `src/ims_deadlock/g6b_row_family_protocol.py`;
- `tests/test_g6b_protocol.py`;
- `tests/test_terminal_classes.py`;
- `tests/test_g4_protocol.py`;
- `tests/test_historical_replay.py`;
- `tests/test_g6b_row_family_protocol.py`;
- the G6-B protocol, theory, symbol, assumption, roadmap, handoff,
  change-ledger, and verification documents identified in Task 7;
- this implementation plan and the final correction-review record.

Do not edit, regenerate, refresh, or delete:

- any file under `cases/confirmation/g4/`;
- any file under `evidence/g5/`;
- `evidence/g6/G6_HISTORICAL_REPLAY_LOCK.json`;
- `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R2.json`;
- `evidence/g6/G6_HISTORICAL_REPLAY_LOCK_R3.json`;
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_RAW_HASH_MANIFEST.json`;
- `evidence/g6/G6_HISTORICAL_REPLAY_R3_REPORT.json`;
- `evidence/g6/G6_HISTORICAL_REPLAY_FAILURE_LEDGER.json`;
- any historical output root, prediction, random stream, frozen result, or G4/G5
  scientific summary.

Stop before:

- discovery-case or `CaseSpec` creation;
- new LTS enumeration for G6-B case design;
- CTMC or DES execution for G6-B;
- output-root creation or scientific output inspection;
- any R3 replay from the current v3 source tree;
- `adversarial_review_status = PASSED`;
- `case_creation_authorized = true`;
- `scientific_execution_authorized = true`;
- G6-B `PASS` or any G6-C/D/E progress.

Existing unit/integration tests may construct their frozen development fixtures
and solve their existing development CTMCs. They are verification of code
behavior, not authorization to create or execute a G6-B scientific case.

## Direct-SSH Target and Runtime Lock

All commands run through `friend-win`; do not use the local bootstrap snapshot,
a visible CMD window, or VS Code Remote-SSH. Before Task 1 run:

```bash
ssh -o BatchMode=yes friend-win 'cmd /v:off /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && cd && git rev-parse --show-toplevel && git rev-parse --git-common-dir && git rev-parse --git-dir && git branch --show-current && git rev-parse HEAD && git remote get-url origin && git status --porcelain=v1 && git rev-list --left-right --count @{u}...HEAD && git merge-base --is-ancestor d0a8dca2bd735d39f16d060c545d13ce85029f60 HEAD && if exist D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe (D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe --version) else (exit /b 91)"'
```

Required output:

- top level `D:/worktree/IMS_deadlock-g6b-discovery`;
- common dir `D:/py_pro/IMS_deadlock/.git`;
- worktree-specific Git dir for `IMS_deadlock-g6b-discovery`;
- branch `codex/g6b-discovery-estimand-lock`;
- origin `git@github.com:zjqc/IMS_deadlock.git`;
- no porcelain-status lines;
- ahead/behind `0 0` at the start of implementation;
- successful ancestor check;
- Python `3.13.9` from
  `D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe`.

Use this exact executable and environment for every test, lint, and type-check
command. This example is also the Task 1 full-file command:

```bash
ssh -o BatchMode=yes friend-win 'cmd /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && set PYTHONDONTWRITEBYTECODE=1&& set PYTHONPATH=D:\worktree\IMS_deadlock-g6b-discovery\src&& D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py"'
```

Every later `pytest`, `ruff`, or `mypy` line is the exact argument suffix after
the same qualified `python.exe -m` invocation.

## Frozen Runtime and Payload Contract

Use these exact version identifiers:

```python
TERMINAL_CLASSIFICATION_VERSION = "ims-deadlock/g6-terminal-stopping-partition/v3"
ESTIMAND_SPEC_VERSION = "ims-deadlock/g6-versioned-estimand/v2"
ABSORPTION_DOMAIN_CERTIFICATE_VERSION = (
    "ims-deadlock/g6-absorption-domain-certificate/v1"
)
ABSORPTION_DOMAIN_ALGORITHM_VERSION = (
    "finite-positive-rate-stopped-ctmc-scc-domain/v1"
)
G6_CTM_GENERATOR_PROVENANCE = (
    "derived_from_g6_terminal_stopping_partition_ims_lts_v3"
)
SUPPORT_GRAPH_SEMANTICS = "complete_stopped_lts_support"
CERTIFIED_STATUS = "certified_finite_positive_rate_stopped_ctmc"
NOT_CERTIFIED_STATUS = "not_certified"
NO_POLICY_FILTER_DECLARATION = {
    "version": "ims-deadlock/g6-policy-filter-declaration/v1",
    "mode": "no_policy_filter",
    "excluded_plant_arcs": [],
}
```

`VersionedEstimandSpec` must expose `policy_analysis_class`, not
`plant_policy_class`. The v3 JSON shape is exact at the namespace level:

```json
{
  "classes": {
    "D_global": [],
    "D_local": [],
    "F": [],
    "R_livelock": [],
    "R_terminal": []
  },
  "policy_analysis_classes": {
    "P_policy": []
  },
  "derived_state_sets": {
    "S_reach": {
      "state_ids": [],
      "support_unreachable_state_ids": [],
      "graph_semantics": "complete_stopped_lts_support",
      "positive_rate_verified": false
    },
    "S_T": {
      "state_ids": null,
      "certification_status": "not_certified",
      "reason_codes": ["rate_manifest_absent"]
    },
    "unselected_closed_sccs": null,
    "closed_class_reverse_basin_state_ids": null,
    "non_almost_sure_absorbing_state_ids": null
  }
}
```

The top-level payload also contains one
`absorption_domain_certificate` object with this exact shape; the derived sets
remain solely under `derived_state_sets`:

```json
{
  "version": "ims-deadlock/g6-absorption-domain-certificate/v1",
  "algorithm_version": "finite-positive-rate-stopped-ctmc-scc-domain/v1",
  "certification_status": "not_certified",
  "reason_codes": ["rate_manifest_absent"],
  "selected_absorbing_state_ids": [],
  "identity": {
    "state_space_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "partition_hash": "1111111111111111111111111111111111111111111111111111111111111111",
    "rate_manifest_hash": null,
    "positive_rate_graph_hash": null,
    "policy_filter_hash": null,
    "absorption_domain_hash": null
  },
  "assumptions": {
    "finite_state_space_verified": true,
    "complete_nontruncated_lts_verified": true,
    "lts_generation_provenance_verified": false,
    "positive_finite_rate_manifest_verified": false,
    "selected_target_identity_verified": true,
    "policy_filter_identity_verified": false
  }
}
```

It must not duplicate `S_T` under `classes` or keep `P_policy` under
`classes`.

The certificate type is:

```python
@dataclass(frozen=True)
class AbsorptionDomainCertificate:
    version: str
    algorithm_version: str
    certification_status: str
    reason_codes: tuple[str, ...]
    selected_absorbing_state_ids: tuple[str, ...]
    unselected_closed_sccs: tuple[tuple[str, ...], ...] | None
    closed_class_reverse_basin_state_ids: tuple[str, ...] | None
    s_t_state_ids: tuple[str, ...] | None
    non_almost_sure_absorbing_state_ids: tuple[str, ...] | None
    finite_state_space_verified: bool
    complete_nontruncated_lts_verified: bool
    lts_generation_provenance_verified: bool
    positive_finite_rate_manifest_verified: bool
    selected_target_identity_verified: bool
    policy_filter_identity_verified: bool
    state_space_hash: str
    partition_hash: str
    rate_manifest_hash: str | None
    positive_rate_graph_hash: str | None
    policy_filter_hash: str | None
    absorption_domain_hash: str | None
```

`TerminalStoppingPartition.rate_manifest_hash`, the three new hashes, and
`estimand_id` have type `str | None`. With `event_rates=None`, all five are
`None`. With an explicit manifest, `rate_manifest_hash` is nonnull; the three
new hashes and `estimand_id` remain null until a certificate is attached.
Explicit `{}` is valid only for an edgeless LTS; it is not equivalent to
`None`.

The partition is the single immutable runtime carrier. Add these exact fields
and return type changes:

```python
@dataclass(frozen=True)
class TerminalStoppingPartition:
    declared_transition_event_names: tuple[str, ...]
    absorption_domain_certificate: AbsorptionDomainCertificate
    rate_manifest_hash: str | None
    positive_rate_graph_hash: str | None
    policy_filter_hash: str | None
    absorption_domain_hash: str | None
    estimand_id: str | None

    def hashes_json_dict(self) -> dict[str, str | None]:
        """Return structural, stopping, and nullable certificate identities."""
```

The structural constructor always installs an uncertified certificate object;
the field is never null, so v3 serialization always has one audit record.
`with_absorption_domain_certificate` uses `dataclasses.replace` to replace that
slot and the nullable hashes together. `to_json_dict()` projects the certificate
slot into both the exact certificate record and the nonduplicated
`derived_state_sets` view.

The public certification boundary is:

```python
def certify_absorption_domain(
    partition: TerminalStoppingPartition,
    stable_lts: StableLTS,
    event_rates: Mapping[str, float] | None,
    *,
    selected_bad_state_ids: Iterable[str],
    selected_success_state_ids: Iterable[str],
    policy_filter_declaration: Mapping[str, object],
    require_global: bool,
) -> AbsorptionDomainCertificate:
    """Certify the finite stopped positive-rate absorption domain."""
```

`TerminalStoppingPartition.with_absorption_domain_certificate(certificate)`
returns a new frozen partition, verifies certificate/partition identity, copies
the three certificate hashes, recomputes `estimand_id`, and never mutates the
structural partition.

## Task 1: Lock and Implement the Typed G6-B Estimand Schema v2

**Files:**

- Modify: `tests/test_g6b_protocol.py`
- Modify: `cases/discovery/g6b/estimand_schema.json`
- Modify: `src/ims_deadlock/g6b_protocol.py`

- [ ] **Step 1: Add RED tests for the exact typed ontology**

Add tests named:

```python
def test_estimand_schema_v2_uses_typed_ontology() -> None:
def test_legacy_objective_classes_is_rejected(tmp_path: Path) -> None:
def test_selected_target_kind_drift_is_rejected(tmp_path: Path) -> None:
def test_future_hashes_require_absorption_identity(tmp_path: Path) -> None:
def test_exact_des_contract_requires_same_absorption_domain(tmp_path: Path) -> None:
```

The canonical test must assert:

```python
assert estimand["schema_version"] == "ims-deadlock/g6b-estimand-schema/v2"
assert "objective_classes" not in estimand["ontology"]
assert estimand["ontology"]["selected_stopping_targets"] == {
    "bad_hit_sets": ["D_global", "D_local"],
    "success_class": "F",
}
assert estimand["ontology"]["unselected_plant_terminal_classes"] == [
    "R_livelock",
    "R_terminal",
]
assert estimand["ontology"]["policy_analysis_class"] == {
    "label": "P_policy",
    "plant_partition_member": False,
    "selectable_target": False,
}
assert estimand["ontology"]["derived_state_sets"] == {
    "S_reach": {
        "definition": "complete_stopped_lts_support_reachability",
        "role": "diagnostic_only",
        "selectable_target": False,
    },
    "S_T": {
        "definition": (
            "probability_one_hit_selected_target_in_finite_positive_rate_"
            "stopped_ctmc"
        ),
        "role": "certified_absorption_domain",
        "selectable_target": False,
    },
}
```

Mutations must insert the legacy key, put `S_T`, `S_reach`, `R_livelock`, or
`P_policy` into a selected target, remove each new hash, and set the same-domain
rule false. Each mutation must make `validate_g6b_protocol_bundle` invalid.

- [ ] **Step 2: Run the five new tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_g6b_protocol.py -k
"typed_ontology or objective_classes or target_kind or absorption_identity or
same_absorption_domain"` through the frozen SSH prefix.

Expected: failures show the canonical v1 schema, legacy flat ontology, missing
new hashes, or absent exact/DES domain rule. No test may fail because a G6-B
case or output is missing.

- [ ] **Step 3: Replace the JSON ontology with the exact v2 object**

Keep the existing `D_local` definition and admission routes. Add the exact
typed groups asserted above. Set `future_required_hashes` to:

```python
[
    "state_space_hash",
    "partition_hash",
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "stopping_rule_hash",
    "des_stopping_rule_hash",
    "estimand_id",
]
```

Set `exact_des_consistency` to the current four true rules plus:

```json
"certified_absorption_domain_required": true,
"same_absorption_domain_hash_required": true
```

Keep `scientific_execution_authorized` false.

- [ ] **Step 4: Replace the flat validator constants and exact expectation**

In `g6b_protocol.py`, bump only `G6B_ESTIMAND_SCHEMA_VERSION`, replace
`_OBJECTIVE_CLASSES` with exact typed constants, add the three new future hash
names, and make `_validate_estimand` exact-match the canonical v2 object. The
exact matcher must reject unknown keys; do not add a compatibility branch for
v1 at the live G6-B protocol boundary.

- [ ] **Step 5: Run the full G6-B foundation test file and record GREEN**

Run `pytest -p no:cacheprovider -q tests/test_g6b_protocol.py` through SSH.

Expected: all tests pass; the bundle still reports PENDING and
`scientific_execution_authorized is False`.

- [ ] **Step 6: Commit the schema slice**

Run `git diff --check`, inspect the exact three-file diff, then commit with:

```text
test:lock-g6b-estimand-ontology-v2
```

## Task 2: Lock and Implement the v3 Structural Runtime Contract

**Files:**

- Modify: `tests/test_terminal_classes.py`
- Modify: `src/ims_deadlock/terminal_classes.py`
- Modify: `tests/test_g4_protocol.py` only for import/version expectations that
  must compile with the renamed estimand field

- [ ] **Step 1: Add RED tests for versions, namespaces, and absent identity**

Add tests named:

```python
def test_v3_serialization_separates_plant_policy_and_derived_sets() -> None:
def test_classification_without_rates_is_explicitly_uncertified() -> None:
def test_absent_and_explicitly_empty_rate_manifests_are_distinct() -> None:
def test_rate_manifest_keys_exactly_match_declared_transition_events() -> None:
def test_plant_partition_payload_excludes_policy_and_derived_sets() -> None:
def test_estimand_spec_v2_uses_policy_analysis_class() -> None:
```

The first test must assert exact key sets:

```python
assert set(payload["classes"]) == {
    "D_global",
    "D_local",
    "F",
    "R_livelock",
    "R_terminal",
}
assert payload["policy_analysis_classes"] == {"P_policy": []}
assert set(payload["derived_state_sets"]) == {
    "S_reach",
    "S_T",
    "unselected_closed_sccs",
    "closed_class_reverse_basin_state_ids",
    "non_almost_sure_absorbing_state_ids",
}
assert "S_T" not in payload["classes"]
assert "P_policy" not in payload["classes"]
```

For `event_rates=None`, assert `S_reach` has support semantics and
`positive_rate_verified is False`, `S_T.state_ids is None`, reason codes are
`["rate_manifest_absent"]`, and these hashes are null:

```python
(
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "estimand_id",
)
```

For a complete edgeless LTS, compare `event_rates=None` with
`event_rates={}`. The former rate hash is null; the latter is the canonical hash
of the explicitly supplied empty manifest. Both remain uncertified until Task
3 attaches a certificate.

Freeze rate-manifest semantics over the supplied transition registry, not only
the arcs realized from one initial state. Its key set must exactly equal the
sorted names of all supplied `TransitionSpec` objects. A missing declared event
raises `missing_event_rate`; an unknown extra key raises
`unexpected_event_rate`. Rates for declared but unreachable transitions remain
in `rate_manifest_hash` and intentionally change `estimand_id`, while
`positive_rate_graph_hash` binds only realized stopped support.

- [ ] **Step 2: Run the six new terminal tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_terminal_classes.py -k
"v3_serialization or without_rates or absent_and_explicitly_empty or
rate_manifest_keys or plant_partition_payload or policy_analysis_class"`
through SSH.

Expected: current v2 constants, flat `classes`, `plant_policy_class`, and hash
of an absent `{}` manifest cause assertion failures.

- [ ] **Step 3: Add the v3 constants and immutable certificate skeleton**

Add the exact constants and `AbsorptionDomainCertificate` fields frozen above.
Add a private constructor for an uncertified certificate that receives the
structural selected-target IDs, state-space hash, partition hash, optional rate
hash, and sorted nonempty reason codes. Reject an empty reason list, nonnull
probabilistic derived sets on an uncertified certificate, and null sets on a
certified certificate. Add the nonoptional certificate slot and nullable hash
fields to `TerminalStoppingPartition`, and change `hashes_json_dict()` to
`dict[str, str | None]` in the same RED/GREEN slice.

- [ ] **Step 4: Rename the estimand policy field and remove the misleading gate**

Rename `plant_policy_class` to `policy_analysis_class` in the dataclass,
validation, JSON, and stopping-rule hash payload. Remove
`require_selected_absorption` from `partition_stable_lts` and delete the unused
`_validate_selected_absorption` helper. The only strict probability-one gate
will be `certify_absorption_domain` in Task 3.

- [ ] **Step 5: Split structural serialization into exact namespaces**

Retain `selected_reachable_state_ids` as a Python structural field. Serialize
it only as `derived_state_sets.S_reach.state_ids`. Serialize its complement as
`support_unreachable_state_ids`. Do not keep duplicate v2 top-level
reachability fields in the v3 JSON payload.

Add `plant_partition_json_dict()` returning only classification version, the
five plant classes, bad-hit sets, local soundness audit, and terminal SCCs.
Compute `partition_hash` only from this payload.

- [ ] **Step 6: Make absent-rate identity nullable and explicit-empty distinct**

Change `_validated_rate_manifest` to receive the declared transition-event
names, return `None` for `event_rates=None`, and return a sorted dictionary only
when an explicitly supplied mapping has exactly that key set. Store
`declared_transition_event_names` on the structural partition so the certifier
can repeat the identity check. Hash only a nonnull manifest. Initialize the
three certificate hashes and `estimand_id` to null in the structural partition.
Use reason `rate_manifest_absent` for `None` and
`absorption_domain_not_certified` when a manifest exists but no certificate is
attached. Update the old rate-drift test to include a declared and realized arc
instead of assigning a rate to a nonexistent event.

- [ ] **Step 7: Run the full terminal-class test file and repair only v3 drift**

Run `pytest -p no:cacheprovider -q tests/test_terminal_classes.py` through SSH.
Update the old `classes["S_T"]` assertion to inspect `S_reach`; do not weaken
the existing local-first-hit, LTS-completeness, rate-validation, SCC, or
partition-invariance tests.

- [ ] **Step 8: Run targeted Ruff and strict mypy**

Run through SSH:

```text
ruff check --no-cache src/ims_deadlock/terminal_classes.py tests/test_terminal_classes.py
ruff format --check --no-cache src/ims_deadlock/terminal_classes.py tests/test_terminal_classes.py
mypy --no-incremental --strict src/ims_deadlock/terminal_classes.py
```

- [ ] **Step 9: Commit the structural v3 slice**

After `git diff --check`, commit with:

```text
feat:separate-g6-structural-runtime-namespaces
```

## Task 3: Certify the Exact Almost-Sure Absorption Domain

**Files:**

- Modify: `tests/test_terminal_classes.py`
- Modify: `src/ims_deadlock/terminal_classes.py`

- [ ] **Step 1: Add the branching closed-class counterexample as RED**

Build a one-job, resource-free model with mode `start`, two enabled transitions
from `start` to completion and to mode `closed`, and a self-loop transition in
`closed`. Generate its complete LTS with `enumerate_stable_lts`; its positive
support is `s0 -> F`, `s0 -> c`, and `c -> c`. Partition it with
`verify_generated_lts=True`, then call the certifier with that partition and
LTS, the explicit rate manifest, exact selected bad/success IDs, the canonical
no-policy declaration, and `require_global=False`. Assert:

```python
assert partition.selected_reachable_state_ids == (start_state_id,)
assert certificate.unselected_closed_sccs == ((closed_state_id,),)
assert certificate.closed_class_reverse_basin_state_ids == tuple(
    sorted((closed_state_id, start_state_id))
)
assert certificate.s_t_state_ids == ()
assert certificate.non_almost_sure_absorbing_state_ids == tuple(
    sorted((closed_state_id, start_state_id))
)
```

Resolve `start_state_id` and `closed_state_id` from the generated records'
source-state modes rather than assuming enumeration ID order.

Call the same function with `require_global=True` and assert a structured
`TerminalPartitionError` with code `non_almost_sure_absorption_domain`. This is
the machine form of counterexample `CE-NB1`.

- [ ] **Step 2: Add RED tests for complete, empty, and refusal domains**

Add tests named:

```python
def test_full_positive_rate_domain_certifies_global_s_t() -> None:
def test_explicit_empty_manifest_certifies_empty_nonabsorbing_domain() -> None:
def test_missing_rate_manifest_fails_scientific_certification() -> None:
def test_zero_rate_fails_scientific_certification() -> None:
def test_extra_rate_event_fails_scientific_certification() -> None:
def test_truncated_lts_fails_scientific_certification() -> None:
def test_unavailable_branch_fails_scientific_certification() -> None:
def test_unverified_lts_provenance_fails_certification() -> None:
def test_selected_target_drift_fails_certification() -> None:
def test_policy_filter_drift_fails_certification() -> None:
def test_absorption_hash_binds_target_support_and_closed_basin() -> None:
def test_attached_certificate_marks_positive_rate_reachability_verified() -> None:
```

Use a simple `s0 -> F` graph for the successful nonempty domain and an
all-absorbing edgeless graph for the certified-empty domain. Missing rates must
raise `missing_rate_manifest`; zero, negative, boolean, NaN, or infinite rates
must raise `invalid_event_rate`; an extra rate key must raise
`unexpected_event_rate`; a truncated or unavailable LTS must raise
`incomplete_stable_lts`; an unverified provenance audit must raise
`unverified_lts_provenance`; target mismatch must raise
`selected_target_drift`; any declaration other than the exact canonical
no-policy object must raise `policy_filter_drift`.

For the certifier extra-key test, create the structural partition with the
valid exact manifest, then pass a mutated mapping containing one unknown event
to `certify_absorption_domain`; this proves the public certificate boundary
revalidates identity instead of relying only on partition construction.

Generate the positive certificate fixtures from their simple declared models
and call `partition_stable_lts(..., verify_generated_lts=True)`; do not forge a
verified audit with `dataclasses.replace`. The separate unverified-provenance
test builds the same valid partition with verification disabled and proves the
public certifier rejects `caller_contract_only`.

- [ ] **Step 3: Run the new certificate tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_terminal_classes.py -k
"branching_closed or full_positive_rate or explicit_empty_manifest or
scientific_certification or unavailable_branch or unverified_lts_provenance or
target_drift or policy_filter_drift or absorption_hash or
attached_certificate"` through SSH.

Expected: import or attribute failures for the absent certificate API. The
branching graph must not be made to pass by renaming structural reachability.

- [ ] **Step 4: Implement stopped positive-rate graph construction**

Validate the supplied LTS against the structural partition before graph work:

1. classification version is v3;
2. LTS is finite, complete, nontruncated, and has no unavailable branch;
3. `lts_provenance_audit` has the exact deterministic re-enumeration method and
   `verified is True`;
4. its state-space hash and sorted plant arcs equal the partition identities;
5. selected bad and success IDs exactly equal the partition-selected IDs;
6. the policy declaration exactly equals `NO_POLICY_FILTER_DECLARATION`;
7. the rate manifest is explicitly supplied, its keys exactly equal
   `declared_transition_event_names`, and every value is finite and strictly
   positive; consequently every realized plant arc event is covered.

Construct stopped arcs by removing every arc whose source is in the selected
absorbing set. Keep `(source, event, target)` identity and sort it. Hash this
support payload with:

```python
{
    "version": "ims-deadlock/g6-positive-rate-stopped-graph/v1",
    "state_ids": sorted_state_ids,
    "selected_absorbing_state_ids": sorted_selected_ids,
    "arcs": sorted_stopped_arcs,
}
```

Do not put numeric rates in this graph hash; `rate_manifest_hash` separately
binds their frozen values. A support edge may not be dropped because its rate is
missing or nonpositive; that condition is a refusal.

- [ ] **Step 5: Implement SCC, closed-class, reverse-basin, and `S_T`**

Let `A` be selected IDs and `T = V - A`. Reuse `_strong_components` on the graph
induced by `T`. A component is unselected closed iff no stopped positive-rate
arc leaves it to another component or to `A`. Compute the reverse basin of all
such components within `T`. Return:

```python
s_t_state_ids = tuple(sorted(T - closed_basin))
non_almost_sure_absorbing_state_ids = tuple(sorted(closed_basin))
```

An isolated nonabsorbing state is a singleton unselected closed SCC. An empty
`T` produces a certified empty tuple, not null.

- [ ] **Step 6: Implement the three hashes and certificate invariants**

Hash the exact no-policy declaration for `policy_filter_hash`. Compute
`absorption_domain_hash` over:

```python
{
    "version": ABSORPTION_DOMAIN_ALGORITHM_VERSION,
    "state_space_hash": partition.state_space_hash,
    "partition_hash": partition.partition_hash,
    "positive_rate_graph_hash": positive_rate_graph_hash,
    "policy_filter_hash": policy_filter_hash,
    "selected_absorbing_state_ids": list(selected_ids),
    "unselected_closed_sccs": [list(component) for component in closed_sccs],
    "closed_class_reverse_basin_state_ids": list(closed_basin),
    "S_T": list(s_t_state_ids),
}
```

Return a certified object with empty reason codes and all six assumption flags
true. Populate its state-space, plant-partition, and rate-manifest identity
fields directly from the validated structural partition. If `require_global`
and `non_almost_sure_absorbing_state_ids` is nonempty, raise before returning a
usable global certificate; include the complete certificate payload in error
details for auditability.

- [ ] **Step 7: Attach the certificate and recompute the estimand identity**

`with_absorption_domain_certificate` must reject uncertified objects, mismatched
certificate `state_space_hash`, `partition_hash`, or `rate_manifest_hash`, and
certificate target drift. Recompute `estimand_id` from:

```python
{
    "state_space_hash": state_space_hash,
    "partition_hash": partition_hash,
    "rate_manifest_hash": rate_manifest_hash,
    "positive_rate_graph_hash": positive_rate_graph_hash,
    "policy_filter_hash": policy_filter_hash,
    "absorption_domain_hash": absorption_domain_hash,
    "stopping_rule_hash": stopping_rule_hash,
    "des_stopping_rule_hash": des_stopping_rule_hash,
}
```

The attached JSON must set `S_reach.positive_rate_verified` true and serialize
certified `S_T`, closed SCCs, reverse basin, and non-almost-sure IDs as lists.

- [ ] **Step 8: Preserve partition invariance and prove estimand drift**

Keep the existing test that changing selected bad classes does not change
`partition_hash`. Update it to certify both targets and assert that the
`absorption_domain_hash` and `estimand_id` do change. Add a support-arc mutation
with identical plant classes and assert the same two hashes change.

- [ ] **Step 9: Run the full terminal suite, Ruff, and strict mypy**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_terminal_classes.py
ruff check --no-cache src/ims_deadlock/terminal_classes.py tests/test_terminal_classes.py
ruff format --check --no-cache src/ims_deadlock/terminal_classes.py tests/test_terminal_classes.py
mypy --no-incremental --strict src/ims_deadlock/terminal_classes.py
```

Expected: all pass. No test may solve a partial-domain CTMC.

- [ ] **Step 10: Commit the certificate slice**

After inspecting the diff and running `git diff --check`, commit with:

```text
feat:certify-g6-almost-sure-absorption-domain
```

## Task 4: Gate G4 CTMC Construction on the Strict Certificate

**Files:**

- Modify: `tests/test_g4_protocol.py`
- Modify: `src/ims_deadlock/g4_instances.py`
- Inspect: `src/ims_deadlock/g4_protocol.py`; the expected implementation leaves
  it unchanged because it delegates nested serialization to the partition

- [ ] **Step 1: Add RED integration assertions for a certified v3 payload**

Update the existing development-grid and medium-protocol tests to assert:

```python
assert classification["classification_version"] == (
    "ims-deadlock/g6-terminal-stopping-partition/v3"
)
assert "P_policy" not in classification["classes"]
assert "S_T" not in classification["classes"]
assert classification["derived_state_sets"]["S_T"][
    "certification_status"
] == "certified_finite_positive_rate_stopped_ctmc"
assert classification["derived_state_sets"][
    "non_almost_sure_absorbing_state_ids"
] == []
for name in (
    "rate_manifest_hash",
    "positive_rate_graph_hash",
    "policy_filter_hash",
    "absorption_domain_hash",
    "estimand_id",
):
    assert isinstance(estimand["hashes"][name], str)
    assert estimand["hashes"][name]
```

Keep the existing numerical probability-bound and residual checks.

- [ ] **Step 2: Add a pre-generator refusal test**

Monkeypatch `ims_deadlock.g4_instances.certify_absorption_domain` to raise a
sentinel `TerminalPartitionError`, and monkeypatch the module's
`AbsorbingCTMC` constructor to set a flag if invoked. Run an existing small
development case through `derive_absorbing_ctmc`. Assert the sentinel error is
returned and the constructor flag remains false. Because the certifier symbol
does not exist on the RED baseline, install the sentinel with
`monkeypatch.setattr(g4_instances, "certify_absorption_domain", sentinel,
raising=False)`; keep the constructor patch strict.

- [ ] **Step 3: Run the focused integration tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_g4_protocol.py -k
"development_grid_derives or medium_protocol_payload or pre_generator"`
through SSH.

Expected: v2 payload or absent certificate assertions fail; the new monkeypatch
test fails because the certifier is not yet called directly.

- [ ] **Step 4: Replace the existential post-check with strict certification**

In `derive_absorbing_ctmc`:

1. enumerate and validate the complete stable LTS as before;
2. build the v3 structural partition with the explicit frozen event-rate map;
3. preserve the `D_global`-only refusal when a verified `D_local` exists;
4. call `certify_absorption_domain` with exact partition bad/success IDs,
   `NO_POLICY_FILTER_DECLARATION`, and `require_global=True`;
5. attach the certificate;
6. only then derive transient, completion, and deadlock rates and instantiate
   `AbsorbingCTMC`.

Delete the old `unreachable_nonabsorbing_state_ids` scientific gate. Structural
support reachability remains diagnostic and cannot authorize generator
construction. `certify_absorption_domain(require_global=True)` becomes the sole
probability-one absorption authority before generator construction; the
separate `D_global`-only-with-`D_local` check remains an estimand-label refusal,
not a competing absorption-domain test.

- [ ] **Step 5: Keep the outer G4 schema stable unless a test proves otherwise**

The terminal payload and estimand are self-versioned. Do not bump the outer G4
result schema merely because the nested contract is v3. `g4_protocol.py`
continues delegating nested serialization and receives no production edit in
this task; the focused test proves that boundary.

- [ ] **Step 6: Run G4 and terminal integration tests**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_terminal_classes.py tests/test_g4_protocol.py
ruff check --no-cache src/ims_deadlock/terminal_classes.py src/ims_deadlock/g4_instances.py src/ims_deadlock/g4_protocol.py tests/test_terminal_classes.py tests/test_g4_protocol.py
ruff format --check --no-cache src/ims_deadlock/terminal_classes.py src/ims_deadlock/g4_instances.py src/ims_deadlock/g4_protocol.py tests/test_terminal_classes.py tests/test_g4_protocol.py
mypy --no-incremental --strict src/ims_deadlock/terminal_classes.py src/ims_deadlock/g4_instances.py src/ims_deadlock/g4_protocol.py
```

- [ ] **Step 7: Commit the strict construction gate**

After `git diff --check`, commit with:

```text
feat:gate-g4-ctmc-on-global-absorption-certificate
```

## Task 5: Add an Explicit Historical v2/v3 Reader Without Rewriting R3

**Files:**

- Modify: `tests/test_historical_replay.py`
- Modify: `src/ims_deadlock/historical_replay.py`

- [ ] **Step 1: Add RED reader tests for legacy, current, and unknown versions**

Add a frozen view type and tests named:

```python
def test_v2_terminal_payload_is_legacy_and_s_t_is_not_certificate() -> None:
def test_v3_terminal_payload_reads_only_certified_derived_s_t() -> None:
def test_v3_terminal_payload_requires_top_level_certificate() -> None:
def test_v3_terminal_payload_rejects_certificate_hash_or_status_drift() -> None:
def test_unknown_terminal_classification_version_fails_closed() -> None:
def test_captured_v2_estimand_id_remains_opaque() -> None:
```

The v2 fixture must keep a nonempty `classes["S_T"]`; the reader must return
`certified_s_t_state_ids is None`. The v3 fixture must put certified `S_T` only
under `derived_state_sets` and carry a matching top-level certificate plus
nonnull `hashes.absorption_domain_hash`. Missing certificate, wrong certificate
version/algorithm/status, nonempty certificate reason codes, or mismatch
between certificate identity and the top-level absorption-domain hash must fail
closed. An unknown version must return no accepted view and make the mechanism
check fail closed. `extract_estimand_ids` must return the exact captured string
without recomputation.

- [ ] **Step 2: Run the six tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_historical_replay.py -k
"terminal_payload or classification_version or opaque"` through SSH.

Expected: current code accepts `D_local` without checking a classification
version and has no representation proving that v2 `S_T` was ignored.

- [ ] **Step 3: Implement the pure historical terminal view**

Add exact string constants for v2 and v3 inside `historical_replay.py`; do not
import current runtime constructors. Add:

```python
@dataclass(frozen=True)
class HistoricalTerminalClassification:
    classification_version: str
    d_local_state_ids: tuple[str, ...]
    certified_s_t_state_ids: tuple[str, ...] | None
```

Implement `read_historical_terminal_classification(payload)`:

- require verified LTS provenance and local-bad soundness audits;
- accept only v2 or v3;
- parse `classes.D_local` for both;
- set certified `S_T` to null for v2 regardless of `classes.S_T`;
- for v3, require the exact top-level certificate version and algorithm,
  certified status, empty certificate reason codes, all six assumption flags
  true, nonnull certificate identity hashes, and equality between certificate
  and top-level `absorption_domain_hash`;
- accept `derived_state_sets.S_T.state_ids` only when its status is the same
  certified status, its reason codes are empty, and
  `S_reach.positive_rate_verified is True`;
- return null for unknown or malformed versions.

Change `_terminal_d_local` to use this reader. Do not change captured estimand
ID extraction.

- [ ] **Step 4: Prove no immutable R3 artifact changed**

Run:

```bash
ssh -o BatchMode=yes friend-win 'cmd /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && git diff --name-only d0a8dca2bd735d39f16d060c545d13ce85029f60...HEAD -- evidence/g6"'
```

Expected: no output. Do not run the R3 replay from this current v3 worktree;
its recorded runtime hashes intentionally refer to the immutable historical
code ref.

- [ ] **Step 5: Run the full historical-reader test file and static checks**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_historical_replay.py
ruff check --no-cache src/ims_deadlock/historical_replay.py tests/test_historical_replay.py
ruff format --check --no-cache src/ims_deadlock/historical_replay.py tests/test_historical_replay.py
mypy --no-incremental --strict src/ims_deadlock/historical_replay.py
```

- [ ] **Step 6: Commit the historical boundary**

After `git diff --check`, commit with:

```text
fix:make-historical-terminal-version-boundary-explicit
```

## Task 6: Migrate the Exact-Eight Row-Family Matrix to the Corrected Domain

**Files:**

- Modify: `tests/test_g6b_row_family_protocol.py`
- Modify:
  `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`
- Modify: `src/ims_deadlock/g6b_row_family_protocol.py`

- [ ] **Step 1: Add RED mutation tests for the corrected matrix**

Add tests named:

```python
def test_row_family_matrix_requires_foundation_estimand_v2(tmp_path: Path) -> None:
def test_row_family_matrix_requires_terminal_partition_v3(tmp_path: Path) -> None:
def test_row_family_matrix_rejects_s_reach_as_selected(tmp_path: Path) -> None:
def test_row_family_matrix_requires_nonnull_certified_domain_hash(
    tmp_path: Path,
) -> None:
def test_exact_des_pairing_requires_same_absorption_domain_hash(
    tmp_path: Path,
) -> None:
```

Use the existing `_copy_bundle`, `_row_family_matrix_from`, `_write`, and
`_assert_invalid` helpers. Each test mutates one canonical field and expects
`row_family_matrix.json: document must match`.

- [ ] **Step 2: Run the five tests and record RED**

Run `pytest -p no:cacheprovider -q tests/test_g6b_row_family_protocol.py -k
"foundation_estimand_v2 or terminal_partition_v3 or s_reach_as_selected or
certified_domain_hash or same_absorption_domain_hash"` through SSH.

Expected: missing-key or current-matrix assertion failures. The exact-eight
file-set test must remain green.

- [ ] **Step 3: Extend the exact matrix ontology contract**

Keep the matrix schema version v1 because this branch's row-family matrix has
not merged, but make its exact `ontology_contract`:

```json
{
  "foundation_estimand_schema_version": "ims-deadlock/g6b-estimand-schema/v2",
  "terminal_classification_version": "ims-deadlock/g6-terminal-stopping-partition/v3",
  "selected_stopping_targets": {
    "bad_hit_sets": ["D_global", "D_local"],
    "success_class": "F"
  },
  "unselected_plant_terminal_classes": ["R_livelock", "R_terminal"],
  "policy_analysis_class": {
    "label": "P_policy",
    "plant_partition_member": false,
    "selectable_target": false
  },
  "derived_state_sets": {
    "S_reach": {
      "role": "diagnostic_only",
      "selectable_target": false
    },
    "S_T": {
      "role": "certified_absorption_domain",
      "selectable_target": false,
      "requires_nonnull_absorption_domain_hash": true
    }
  },
  "D_local_definition": "verified_first_hit_bad_set_not_terminal_scc",
  "D_local_admission_routes": [
    "A2b_proof",
    "complete_LTS_completion_nonreachability_audit"
  ]
}
```

Extend `exact_des_pairing` with:

```json
"certified_absorption_domain_required": true,
"same_absorption_domain_hash": true
```

Add `absorption_domain_hash_mismatch` to the frozen falsifiers for the
same-target exact/DES probe. Keep `reuse_matrix.json` unchanged: the corrected
domain equality belongs to the same-case exact/DES pairing contract and must
not be declared as reusable identity across different case units.

- [ ] **Step 4: Update the exact Python object in the same change**

Mirror the JSON changes in `_EXPECTED_ROW_FAMILY_MATRIX`. Keep all eight JSON
files present, every authorization false, PENDING review, null observed
outcomes, and data-only behavior. Do not weaken exact-object comparison to make
the migration easier.

- [ ] **Step 5: Extend the existing exact/DES parameterized mutation test**

Add mutations for:

```python
"certified_absorption_domain_required_false"
"same_absorption_domain_hash_false"
```

Keep the current selected-label, versioned-target, case-unit, and method-counting
mutations.

- [ ] **Step 6: Run the full row-family and top-level G6-B suites**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
ruff check --no-cache src/ims_deadlock/g6b_protocol.py src/ims_deadlock/g6b_row_family_protocol.py tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
ruff format --check --no-cache src/ims_deadlock/g6b_protocol.py src/ims_deadlock/g6b_row_family_protocol.py tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
mypy --no-incremental --strict src/ims_deadlock/g6b_protocol.py src/ims_deadlock/g6b_row_family_protocol.py
```

- [ ] **Step 7: Commit the row-family alignment**

After verifying exact-five top-level and exact-eight nested file sets and
running `git diff --check`, commit with:

```text
fix:align-g6b-row-families-with-certified-domain
```

## Task 7: Correct the Theory, Protocol, Review, and Handoff Surface

**Files:**

- Modify: `docs/cases/G6_B_DISCOVERY_PROTOCOL.md`
- Modify: `docs/theory/G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md`
- Modify: `docs/theory/ASSUMPTION_REGISTER.md`
- Modify: `docs/theory/PROBABILITY_LAYER.md`
- Modify: `docs/theory/SYMBOL_TABLE.md`
- Modify: `docs/theory/COUNTEREXAMPLE_LEDGER.md`
- Modify: `docs/verification/G6_B_PROTOCOL_FOUNDATION_REVIEW.md`
- Modify: `docs/cases/CASE_CHANGE_LEDGER.md`
- Modify: `docs/ROADMAP.md`
- Modify: `PROJECT_HANDOFF.md`
- Modify: `README.md`

- [ ] **Step 1: Add a documentation-contract test before prose edits**

In `tests/test_g6b_protocol.py`, add
`test_g6b_theory_documents_lock_typed_absorption_domain`, which reads the first
six theory and protocol documents above, including the canonical
counterexample ledger, and asserts:

```python
assert "S_reach" in combined_text
assert "support graph" in combined_text or "support-graph" in combined_text
assert "probability one" in combined_text
assert "absorption_domain_hash" in combined_text
assert "Objective classes are:" not in g6b_protocol_text
assert "selected_stopping_targets" in g6b_protocol_text
assert "unselected_plant_terminal_classes" in g6b_protocol_text
assert "CE-NB1" in counterexample_ledger_text
assert "S_reach" in counterexample_ledger_text
assert "S_T" in counterexample_ledger_text
assert "non_almost_sure_absorption_domain" in counterexample_ledger_text
```

Also assert the foundation review contains `SUPERSEDED IN PART` and points to
the approved correction design. This test prevents a later code-only rollback
of the theory boundary.

- [ ] **Step 2: Run the documentation test and record RED**

Run
`pytest -p no:cacheprovider -q tests/test_g6b_protocol.py::test_g6b_theory_documents_lock_typed_absorption_domain`
through SSH. Expected: the current protocol/theorem still calls reverse
reachability `S_T`, the `CE-NB1` ledger entry is still candidate/pending, and
the old foundation review still states no finding without a supersession
marker.

- [ ] **Step 3: Correct the theorem and probability documents**

Make these distinctions explicit and mathematically consistent:

- `S_reach`: complete stopped-LTS support-graph states with at least one path to
  the selected target;
- `S_T`: states with probability one of hitting the selected target in the
  finite positive-rate stopped CTMC;
- `B_closed`: reverse basin of unselected closed SCCs;
- `S_T = T - B_closed`;
- `A_abs`: the stronger global condition `B_closed = empty` over the claimed
  nonabsorbing analysis domain.

Replace the incorrect reverse-reachability construction at
`G6_LOCAL_FIRST_HIT_AND_STOPPING_THEOREMS.md` around the old steps 7 and 4. Keep
the existing committor, mean-time, sensitivity, and Doob-h equations restricted
to certified `S_T`. Add the branching `s0 -> F` and `s0 -> c` counterexample.

- [ ] **Step 4: Correct protocol and governance documents without claim upgrade**

In `G6_B_DISCOVERY_PROTOCOL.md`, replace the flat objective list with typed
groups and add the strict certificate/refusal rules. In the assumption and
symbol registers, add `S_reach`, `B_closed`, certificate version, and the
global-domain gate. Mark the old foundation review `SUPERSEDED IN PART` rather
than deleting its historical review record.

Append one dated correction entry to `CASE_CHANGE_LEDGER.md`. Update roadmap,
README, and handoff with the corrected versions/hashes and the implementation
status. Keep G6-B OPEN/PENDING, case creation false, science false, and G6-C/D/E
not started.

In `COUNTEREXAMPLE_LEDGER.md`, replace the `CE-NB1` candidate/pending warning
with the concrete stopped-chain witness `s0 -> F`, `s0 -> c`, `c -> c`. Record
that `s0` belongs to `S_reach` but not `S_T`, that the global certificate must
refuse with `non_almost_sure_absorption_domain`, and that no committor or
mean-time payload may be emitted for that uncertified domain. Link the ledger
entry to the machine regression added in Task 3; do not erase the fact that the
older definition failed.

- [ ] **Step 5: Search for stale semantic aliases**

Run:

```bash
ssh -o BatchMode=yes friend-win 'cmd /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && git grep -n -I -e objective_classes -e plant_policy_class -e g6-terminal-stopping-partition/v2 -e g6-versioned-estimand/v1 -e \"classes.*S_T\" -- README.md PROJECT_HANDOFF.md docs cases src tests"'
```

Expected remaining hits only:

- explicit rejection tests for `objective_classes`;
- v2 historical fixtures and version-aware reader constants;
- prose explicitly describing the legacy defect;
- immutable evidence files, which are outside the search or unchanged.

Every other hit must be corrected or documented as an intentional historical
reference before proceeding.

- [ ] **Step 6: Run documentation test, targeted suites, and diff check**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_g6b_protocol.py::test_g6b_theory_documents_lock_typed_absorption_domain
pytest -p no:cacheprovider -q tests/test_g6b_protocol.py
```

Then run `git diff --check`.

- [ ] **Step 7: Commit the theory/governance correction**

Commit with:

```text
docs:align-g6b-theory-with-certified-absorption-domain
```

## Task 8: Adversarial Review, Full Verification, Push, and Draft-PR Handoff

**Files:**

- Create:
  `docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md`
- Modify: `PROJECT_HANDOFF.md` with the final verified commit/evidence record

- [ ] **Step 1: Re-lock target identity before full verification**

Repeat the direct-SSH preflight. The worktree may be clean after task commits;
if the review document is not yet committed, the only permitted dirty paths are
the review document and an additive handoff update. Confirm the approved design
commit and every task commit are ancestors of HEAD.

- [ ] **Step 2: Run the focused correction suite**

Run through SSH:

```text
pytest -p no:cacheprovider -q tests/test_g6b_protocol.py tests/test_terminal_classes.py tests/test_g4_protocol.py tests/test_historical_replay.py tests/test_g6b_row_family_protocol.py
```

Expected: all pass with no G6-B case or scientific output required.

- [ ] **Step 3: Run the full repository test suite**

Run:

```text
pytest -p no:cacheprovider -q
```

Record the exact pass count and elapsed time from this HEAD. Do not reuse the
earlier `1307 passed` result as current evidence.

- [ ] **Step 4: Run all static checks**

Run through SSH:

```text
ruff check --no-cache src tests
ruff format --check --no-cache src tests
mypy --no-incremental --strict src
mypy --no-incremental --strict --explicit-package-bases src tests
```

Then run both `git diff --check` for the uncommitted review surface and
`git diff --check d0a8dca2bd735d39f16d060c545d13ce85029f60...HEAD` for every
already committed plan/implementation change.

- [ ] **Step 5: Prove authorization and file-set boundaries**

Run the two protocol validators through their tests and inspect the canonical
JSON roots. Confirm:

- exactly five top-level G6-B JSON files;
- exactly eight row-family JSON files;
- every `scientific_execution_authorized` false;
- every `case_creation_authorized` false where present;
- PENDING review state;
- no case, result, output, prediction, or random-stream file added.

- [ ] **Step 6: Prove immutable evidence remained untouched**

Run:

```bash
ssh -o BatchMode=yes friend-win 'cmd /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && git diff --name-only d0a8dca2bd735d39f16d060c545d13ce85029f60...HEAD -- cases/confirmation/g4 evidence/g5 evidence/g6"'
```

Expected: no output. Also inspect the full changed-path list and reject any
path outside the frozen scope unless a failing test proved it as a real
consumer and the review record explains it.

- [ ] **Step 7: Obtain independent theory and code reviews**

Use separate reviewers:

- theory reviewer: prove the SCC/reverse-basin characterization, inspect the
  branching counterexample, and verify every universal statement is limited to
  finite complete positive-rate stopped CTMCs;
- code reviewer: inspect all version paths, null versus empty semantics, hash
  composition, generator-before-certificate ordering, and historical-reader
  isolation;
- verifier: reproduce focused/full/static evidence and changed-path guards.

Any finding is fixed with a new failing test and the relevant targeted/full
rerun. Do not close a finding by prose-only reassurance.

- [ ] **Step 8: Write the correction review record**

Record:

- exact path, branch, HEAD, upstream, dirty state, runtime, and Python version;
- design and plan paths;
- root cause and counterexample;
- versions and exact hash meanings;
- focused/full/static command results;
- immutable-artifact and authorization guards;
- independent review verdicts and resolved findings;
- explicit statement that no G6-B case or science ran;
- residual boundary: partial-domain solve remains unsupported;
- stage: G6-B OPEN/PENDING, case creation false, science false.

- [ ] **Step 9: Commit the review record and final handoff**

After `git diff --check`, commit with:

```text
docs:record-g6b-ontology-absorption-correction-review
```

- [ ] **Step 10: Push without rewriting history and re-lock**

Push normally:

```bash
ssh -o BatchMode=yes friend-win 'cmd /d /c "cd /d D:\worktree\IMS_deadlock-g6b-discovery && git push origin codex/g6b-discovery-estimand-lock"'
```

Then confirm HEAD equals upstream, ahead/behind is `0 0`, status is clean, and
the Draft PR branch head equals the pushed commit by comparing `git rev-parse
HEAD`, `git rev-parse @{u}`, and `git ls-remote origin
refs/heads/codex/g6b-discovery-estimand-lock`. Do not mark the PR ready and do
not claim G6-B PASS.

## Approved-Design Section Map

| Design section | Plan authority |
| --- | --- |
| 1. Blocking finding | Frozen goal plus Tasks 1-3 RED tests |
| 2. Rejected repairs | Exact typed schema, namespace split, and prohibition on treating `S_reach` as partial `S_T` |
| 3. Chosen architecture | Tasks 1-6 in dependency order |
| 4. Typed G6-B ontology | Task 1 |
| 5. Runtime output contract | Task 2 |
| 6. Exact almost-sure domain | Task 3 |
| 7. Scientific gate | Task 4 and the frozen no-science boundary |
| 8. Hash and identity contract | Tasks 2-3 |
| 9. Counterexample and proof ledger | Tasks 3 and 7 |
| 10. Historical v2 and R3 boundary | Task 5 plus Task 8 immutable guards |
| 11. Row-family alignment | Task 6 |
| 12. Change surface | Frozen allowed-path list plus Task 8 changed-path review |
| 13. Required tests | Spec-to-test matrix below |
| 14. Verification and stop conditions | Task 8 |

## Spec-to-Test Coverage Matrix

| Approved requirement | Locked by |
| --- | --- |
| Reject legacy flat ontology | Task 1 legacy-key mutation |
| Derived sets cannot be selected targets | Task 1 target-kind mutations |
| Exclude policy from plant partition | Task 2 namespace and payload tests |
| Exact v3 serialization | Task 2 exact key-set test |
| Branching counterexample | Task 3 `CE-NB1` regression |
| Full domain certification | Task 3 successful global test |
| Missing/invalid/extra rate, truncated/unavailable LTS, and unverified provenance fail closed | Tasks 2-4 explicit certifier and integration refusal tests |
| Partition independence and estimand drift | Task 3 hash tests |
| Null, empty, and nonempty identities are distinct | Tasks 2-3 absent/empty/certified tests |
| Historical v2 is opaque and nonauthorizing | Task 5 reader tests |
| Immutable R3 evidence stays pinned | Tasks 5 and 8 changed-path guards |
| Row-family version/domain alignment | Task 6 exact-object mutations |
| No case or science authorization | Tasks 1, 6, and 8 bundle guards |

## Plan Self-Review Before Implementation

- [x] Verify every approved-spec section 1-14 maps to a task or frozen boundary.
- [x] Search this plan for unfinished prose markers and accidental pseudocode;
  permit only valid Python variadic tuple annotations and Git range syntax.
- [x] Verify every named path exists at the locked base except the one review
  document declared as a create.
- [x] Verify every RED test has a stated current failure reason and every GREEN
  step names an exact command.
- [x] Verify dataclass optional types agree with null/empty JSON semantics.
- [x] Verify no step runs R3, creates a G6-B case, enumerates a G6-B LTS, solves
  G6-B CTMC/DES, inspects a scientific output, or changes an authorization.
- [x] Run `git diff --check` on the plan and obtain an independent plan review
  before Task 1 implementation begins.
