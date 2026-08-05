# G6-B Schema-Only Governance v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development to implement this plan task-by-task.
> If that surface is unavailable, use superpowers:executing-plans and preserve
> the separate implementer, specification-review, and code-quality-review
> passes defined below. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Implement the approved G6-B v2 schema, data-only validator, mutation-test, and project-status surface without creating a case, running normalization, enumerating an LTS, opening target preflight, running CTMC or DES, inspecting scientific outputs, or changing G6-B from OPEN/PENDING.

**Architecture:** Keep all executable behavior on a data-only validation surface. A new canonical-JSON module owns duplicate-member rejection, Unicode/numeric/path rules, null-placeholder self-hashes, and hash-DAG checks; a schema-contract module owns exact immutable vocabularies and pure hypothetical-instance validators. The existing top-level and nested validators consume those primitives, while the committed JSON documents remain the human-auditable source objects. No normalizer, case builder, preflight runner, evidence writer, quantitative runner, or scientific entrypoint is added in this tranche.

**Tech Stack:** Python 3.11+ standard library, pytest, Ruff, strict mypy, JSON data contracts, SHA-256.

---

## Authority Lock

- Approved source worktree: D:\worktree\IMS_deadlock-g6b-spec-final-review
- Approved branch: codex/g6b-case-target-certification-final-review
- Approved source commit: 2d890708858bb29ef118158d96437c9290ec5cf3
- Audited pre-spec base commit:
  1f342baea755f7c85ef538c7403c52cfb9d610c4
- Approved specification:
  docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md
- Approved specification SHA-256:
  b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6
- Renewed user review: approved on 2026-08-01.

Before this plan is published, and again before every implementation task's
first write, prove all of the following:

- Git top-level is exactly the approved source worktree;
- the checkout is a linked worktree of D:\py_pro\IMS_deadlock;
- the branch and full HEAD equal the task's recorded authority epoch;
- the configured upstream exists, ahead/behind is 0/0, and
  git status --short is empty;
- the approved specification SHA-256 is unchanged;
- the audited base is an ancestor of the approved source commit;
- the diff from the audited base through the approved source commit contains
  only
  docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md;
  and
- no path or byte from the quarantined worktree appears in the candidate diff.

The task records a new authority epoch after each reviewed commit, and the next
task locks that full HEAD. A changed specification byte, unexpected commit,
branch, upstream relation, dirty state, worktree identity, or ancestry proof
revokes the task. The dirty worktree
D:\worktree\IMS_deadlock-g6b-case-target-design at 719194c is quarantined
evidence from a stale exact-eleven plan. It is not a code source or test oracle.

## Scope And Stop Contract

This plan may change only schema JSON, data-only validator code, validator
tests, this plan, current project status/handoff documents, and one new
verification review. It must keep the following current facts true:

- study_role = discovery_only;
- confirmation_use = prohibited;
- scientific_execution_authorized = false;
- all four row-family typed capability values are false;
- adversarial_review_status = PENDING;
- current nested state = ROW_FAMILY_BUNDLE_IMPLEMENTED;
- G6-B = OPEN;
- the governance/{bundle_id}, case_units/{case_unit_id},
  evidence/g6b/target_certification, and artifacts/g6b/quantitative instance
  roots are absent.

Stop immediately if a task would:

- create a governed authorization instance or set authorized = true in a
  committed schema/current-state document, governed instance root, or project
  status record;
- construct or materialize a case, method observation, or output root;
- parse or read any prohibited G5/G6-R result, stdout, stderr, status, record,
  or outcome payload in an implementation, validator, fixture, or new test;
- implement or run retired-authority normalization;
- enumerate states, classify terminal sets, certify a target, construct/solve a
  CTMC, run DES, score a hypothesis, or write a scientific summary;
- add a thirteenth nested JSON document; or
- change the approved specification.

## File Structure

### Create

- docs/superpowers/plans/2026-08-01-g6b-schema-only-governance-v2-implementation.md
  - This content-addressed execution plan; publish it alone before Task 1.
- src/ims_deadlock/g6b_canonical_json.py
  - Canonical JSON v2 parsing/serialization, historical decimal conversion,
    repo-relative path validation, self-hash finalization/verification, and
    directed-acyclic hash-reference validation.
- src/ims_deadlock/g6b_schema_contracts.py
  - Exact v2 vocabularies, nested contract descriptors, and pure validators for
    schema definitions and hypothetical records. No filesystem writer and no
    scientific import.
- tests/test_g6b_canonical_json.py
  - Property vectors and mutation tests for Section 7.2.
- tests/test_g6b_schema_contracts.py
  - Pure contract tests for subject/projection, lineage, set/count, command,
    file-role, refusal, and no-claim-upgrade invariants.
- cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/target_certification_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/quantitative_authorization_schema.json
- docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md

### Modify

- cases/discovery/g6b/protocol.json
- cases/discovery/g6b/independence_schema.json
- src/ims_deadlock/g6b_protocol.py
- tests/test_g6b_protocol.py
- cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json
- cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json
- cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json
- cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json
- cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json
- src/ims_deadlock/g6b_row_family_protocol.py
- tests/test_g6b_row_family_protocol.py
- PROJECT_HANDOFF.md
- docs/ROADMAP.md
- docs/cases/CASE_CHANGE_LEDGER.md

### Preserve Byte-For-Byte

- cases/discovery/g6b/estimand_schema.json
- cases/discovery/g6b/negative_controls.json
- cases/discovery/g6b/failure_ledger.json
- cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json

### Never Modify In This Tranche

- historical G4/G5/G6-R authorities;
- every historical or current scientific artifact/output;
- any historical evidence, result, stdout, stderr, status, or record root; and
- any quarantined-worktree file.

A failing test cannot authorize a historical-evidence change. Retired-source
fixture tests use synthetic or already-reviewed metadata only. Running the
existing full repository suite is permitted as black-box validation; its
pass/fail output is not an input to any new G6-B evidence or projection.

The top-level failure ledger remains v1. Section 16.2 requires the nested
row-family failure ledger to move to v2; it does not authorize an unlisted
top-level version change.

## Encoding Decisions Locked By This Plan

The specification fixes meanings and required fields but leaves some JSON
container names implicit. This plan resolves those implementation encodings
without changing scientific meaning:

1. Top-level protocol.json defines typed_capability_vocabulary as the ordered
   four canonical boolean-field names ending _authorized and
   current_row_family_capability_reference as
   row_families/structural_discovery_v1/row_family_protocol.json#/typed_capabilities.
   It retains scientific_execution_authorized = false only as the legacy v1
   summary; no transition reads it.
2. Canonical current capability values appear only in
   row_family_protocol.json.typed_capabilities. review_state.json stores
   typed_capabilities_reference plus typed_capabilities_sha256, never duplicate
   booleans.
3. independence_schema.json v2 replaces unconditional zero-overlap language
   with typed_admission_contract and nonreuse_claim_lattice. The word
   independent is not a result field.
4. canonicalization_contract is a closed object containing version,
   duplicate_members, unicode_normalization, object_key_order,
   array_order_policy, utf8_serialization, numeric_policy, path_policy, and
   timestamp_policy.
5. self_hash_finalization_contract is a closed object containing version,
   placeholder_value, replaced_field_count, omitted_field_allowed,
   prepopulated_digest_allowed, excluded_field_escape_hatch_allowed,
   cross_record_reference_order, digest_algorithm, and digest_encoding.
6. Each fingerprint_payload_schemas entry contains projection_kind,
   subject_type, required_fields, set_like_array_paths, nested_field_contracts,
   additional_properties, and prohibited_fields. The required_fields arrays
   and nested meanings are copied exactly from Sections 7.3-7.7.
7. Descriptive schema files contain no live artifact instance, current lock,
   result, or authorization. Required schema-vocabulary strings such as
   artifact_id, authorization_id, runtime_lock_id, case_unit_id, and
   method_observation_id may appear only inside *_required_fields,
   allowed_*_fields, prohibited-field vocabularies, or other exact descriptive
   arrays required by the approved specification. They must never appear as
   live instance values or instance-shaped objects. authorized = true,
   observed results, and materialized roots are prohibited on every committed
   or governed current-state surface. A clearly synthetic in-memory/tmp_path
   validator fixture may contain authorized = true only to prove future schema
   representability; it never changes current typed capabilities and is never
   written under a governed root.
8. The audited v1 row-family fact case_creation_authorized = false migrates
   exactly to typed_capabilities.case_construction_authorized = false. The v2
   nested protocol does not retain the legacy mutable key. Tests load the v1
   value, prove the false-to-false mapping, and reject any legacy true value or
   migration that changes meaning. The top-level legacy
   scientific_execution_authorized summary remains false as stated above.

## Test Command Convention

Committed commands remain machine-neutral:

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider ...
python -m ruff check --no-cache ...
python -m ruff format --check --no-cache ...
python -m mypy --strict ...
~~~

The operator must execute them with the qualified project runtime recorded in
REMOTE_PROJECT_OPERATIONS.md and PYTHONPATH bound to the exact locked worktree.
No absolute contributor path is committed in this plan.

## Subagent-Driven Execution Protocol

Execute Tasks 1-7 sequentially. Never run two implementation tasks in
parallel. For each task:

1. the leader re-locks the authority epoch using the full checklist above;
2. one fresh implementer receives only that task's owned files and writes the
   failing tests before the corresponding production change;
3. the implementer captures the exact RED command and failure reason, makes
   the smallest GREEN change, and runs the task's focused regression suite;
4. a separate read-only specification reviewer reports P0-P3 findings with
   file/line evidence and the owning task for each repair;
5. after all specification findings are closed and re-reviewed, a different
   read-only code-quality reviewer checks scope, purity, mutation strength,
   typing, and maintainability using the same P0-P3/evidence/owner format;
6. the implementer repairs only the owning task, reviewers re-check the fixes,
   and the leader runs the task verification gate; and
7. only then may the task be committed, pushed, re-locked at 0/0 clean, and
   used as the next authority epoch.

Every task handoff repeats the approved specification commit and SHA-256.
Stale agents, plans, staging directories, and transfers from an earlier epoch
are revoked. Reviewer approval is not inferred from silence.

## TDD Enforcement And Tranche Coverage

The phrase "Section 17.3 requirement N" has two distinct meanings in this
plan:

- schema-tranche evidence: the v2 schema can express the contract, the
  data-only validator rejects malformed hypothetical records, and the
  capability remains absent/unauthorized; and
- capability-runtime evidence: a separately authorized implementation exists
  and is exercised with import guards, runtime spies, real artifact fixtures,
  and exact command/runtime locks.

This first tranche may implement only the first category. In particular,
Section 17.3 requirement 15 cannot prove behavior of a retired-authority
normalizer that does not yet exist, and requirement 27 cannot prove runtime
behavior of a target-preflight entrypoint that Section 16.3 forbids this first
tranche from adding. The current tranche must prove the exact allowlist/guard
schemas, pure source-analysis helper behavior on synthetic strings, governance
validator isolation, capability/root absence, and false authorization flags.
It must record the runtime portions of requirements 15 and 27 as
DEFERRED_REQUIRES_SEPARATE_GATE, not PASS, xfail, or an assumed result. The
future normalizer and preflight plans must add their runtime-spy tests before
their first production edit.

Before each production edit, the owning RED tests must already exist and must
have failed for the intended missing/drifted behavior:

| Owning task | Section 17.3 test surface written before production |
| --- | --- |
| Task 1 | 3-5 canonical bytes, null-placeholder self-hash, exact Decimal |
| Task 2 | 1-2 and 36 top-level state/capability/claim boundary |
| Task 3 | 6, 11, 25-26, 29-30, 34, and 39-44 pure closed-vocabulary/accounting primitives |
| Task 4 | exact-twelve schema structure for 1-2, 6, 10-44, including schema-only portions of 15 and 27 |
| Task 5 | behavioral/mutation oracles for 6-44, with runtime portions of 15 and 27 explicitly deferred |
| Task 6 | capability/root absence, durable status, append-only reporting, and no claim upgrade |

A test that is already green because it checks a retained invariant is not RED
evidence. Add a falsifying mutation or stale-document assertion and observe its
failure first. Test collection errors, skipped tests, xfails, comments, and
name-only placeholders do not count as RED or coverage.

## Pre-Task Plan Publication Gate

Before Task 1, re-lock the clean approved source commit and spec digest, copy
only this plan into the approved worktree, and prove the candidate diff contains
exactly this one new path. Run git diff --check, recompute the plan and spec
SHA-256 values, commit with
docs: add G6-B schema-only v2 implementation plan, push, and require 0/0 clean.
Record that full plan-commit HEAD as Task 1's authority epoch. No schema,
validator, test, status, historical, or scientific file may change in this
publication commit.

### Task 1: Lock Canonical JSON v2 And Self-Hash Semantics

**Files:**

- Create: tests/test_g6b_canonical_json.py
- Create: src/ims_deadlock/g6b_canonical_json.py

- [ ] **Step 1: Write the red canonical parser and serializer tests**

Create table-driven tests for all of these inputs and exact refusal codes:

~~~python
@pytest.mark.parametrize(
    ("raw", "code"),
    [
        ('{"a":1,"a":2}', "duplicate_member"),
        ('{"nested":{"a":1,"a":2}}', "duplicate_member"),
        ('{"text":"e\\u0301"}', "non_nfc_string"),
        ('{"value":NaN}', "non_finite_number"),
        ('{"value":Infinity}', "non_finite_number"),
        ('{"value":-Infinity}', "non_finite_number"),
        ('{"value":-0}', "negative_zero"),
        ('{"value":1.5}', "json_float_prohibited"),
    ],
)
def test_loads_v2_rejects_noncanonical_json(raw: str, code: str) -> None:
    with pytest.raises(CanonicalJsonError, match=code):
        loads_v2(raw)
~~~

Before production code, also write the self-hash, historical-decimal, path,
and DAG mutations listed in Step 4. Own Section 17.3 requirements 3, 4, and 5
with named groups test_spec_17_3_03_schema_self_hash_and_dag,
test_spec_17_3_04_schema_canonical_json_refusals, and
test_spec_17_3_05_schema_historical_decimal_exactness. Every group contains a
valid vector and at least one mutation with an exact error code.

Add positive byte vectors proving UTF-8, no ASCII escaping, code-point key
sorting, compact separators, and declared array-order preservation. Add
set-like array tests in which duplicates or non-sorted values fail.

- [ ] **Step 2: Run the tests and verify RED**

Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_canonical_json.py
~~~

Expected: collection/import failure because ims_deadlock.g6b_canonical_json
does not exist. Do not create production code until this exact failure is read.

- [ ] **Step 3: Implement the minimal canonical JSON API**

First create only the typed API shell with deliberately noncompliant baseline
behavior: standard json.loads/json.dumps, no self-hash validation, and no DAG
cycle rejection. Run one representative test from each canonical, self-hash,
historical-decimal, path, and DAG group and capture RED-1 showing the intended
mutation is accepted or miscomputed. RED-0 import failure from Step 2 does not
count as sufficient evidence for the mutation oracles. Remove the permissive
behavior while implementing the real checks below; no scaffold is committed.

Implement these public symbols with typed exceptions and no project imports:

~~~python
class CanonicalJsonError(ValueError):
    code: str

def loads_v2(raw: str) -> JsonValue: ...
def canonical_bytes_v2(
    value: JsonValue,
    *,
    set_like_paths: frozenset[JsonPath] = frozenset(),
) -> bytes: ...
def canonical_sha256_v2(
    value: JsonValue,
    *,
    set_like_paths: frozenset[JsonPath] = frozenset(),
) -> str: ...
def canonical_decimal_from_historical_token(token: str) -> str: ...
def validate_repo_relative_posix_path(value: str) -> None: ...
def finalized_self_hash(record: JsonObject, field: str) -> str: ...
def verify_finalized_self_hash(record: JsonObject, field: str) -> None: ...
def validate_hash_reference_dag(
    record_ids: frozenset[str],
    upstream_by_record_id: Mapping[str, frozenset[str]],
) -> None: ...
~~~

Implementation rules:

- use object_pairs_hook to reject duplicate members at every depth;
- use parse_int to reject -0, parse_float to reject every JSON float, and
  parse_constant to reject NaN/infinities;
- validate every key and string as already NFC;
- reject Python float values even when passed directly;
- validate set-like arrays before serialization rather than silently sorting;
- serialize with ensure_ascii=False, sort_keys=True, separators=(",", ":"),
  allow_nan=False;
- validate committed paths only through validate_repo_relative_posix_path;
- canonicalize historical number tokens through Decimal without a binary float;
- require the self-hash field to exist; replace exactly it with None; reject
  hash_excludes_fields; and verify a lowercase 64-hex digest;
- reject a missing DAG node, self-loop, or directed cycle.

- [ ] **Step 4: Audit the pre-existing self-hash, decimal, path, and DAG RED tests**

Confirm the Step 1 tests reject omission, empty digest, included digest, forged digest, a
second excluded field, cross-record cycle, exponent-form governance decimals,
-0 decimals, drive paths, leading slash, backslash, empty component, dot,
parent, and symlink-dependent path notation. Historical tokens 1e-7,
1000.000, and -12.3400 must become 0.0000001, 1000, and -12.34 exactly.
The exponent token is accepted only by
canonical_decimal_from_historical_token; loads_v2 and committed governance JSON
must reject exponent-form numeric strings wherever the schema declares a
canonical decimal field.

- [ ] **Step 5: Qualify two runtimes and verify GREEN on both**

Before running, record the exact executable path, version, implementation, and
platform for the qualified project runtime and a second independently resolved
Python runtime. The second runtime must satisfy the repository's declared
Python support range; do not silently use an incompatible interpreter. If no
second supported runtime exists, record a blocked cross-runtime gate and do not
publish a cross-runtime PASS. Run the pytest file with the qualified project
runtime, then use the second runtime to import the module and recompute the
checked-in vector:

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_canonical_json.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -c "from ims_deadlock.g6b_canonical_json import canonical_sha256_v2; assert canonical_sha256_v2({'z':'é','a':1}) == '160c52d506c747530bfe5649cb89704189ea10f8734fbb2a6c6b04cbddf687c8'"
~~~

Expected: all pytest cases pass and both runtimes emit the same digest.

- [ ] **Step 6: Commit**

~~~bash
git add src/ims_deadlock/g6b_canonical_json.py tests/test_g6b_canonical_json.py
git commit -m "feat: add G6-B canonical JSON v2 validator"
~~~

### Task 2: Migrate The Top-Level Protocol And Independence Contract

**Files:**

- Modify: tests/test_g6b_protocol.py
- Modify: cases/discovery/g6b/protocol.json
- Modify: cases/discovery/g6b/independence_schema.json
- Modify: src/ims_deadlock/g6b_protocol.py

- [ ] **Step 1: Write red tests for the exact v2 top-level shape**

The tests must assert:

~~~python
assert protocol["schema_version"] == "ims-deadlock/g6b-discovery-protocol/v2"
assert protocol["typed_capability_vocabulary"] == [
    "case_construction_authorized",
    "retired_authority_fingerprint_normalization_authorized",
    "target_certification_preflight_authorized",
    "quantitative_execution_authorized",
]
assert protocol["current_row_family_capability_reference"] == (
    "row_families/structural_discovery_v1/"
    "row_family_protocol.json#/typed_capabilities"
)
assert protocol["scientific_execution_authorized"] is False
assert independence["schema_version"] == (
    "ims-deadlock/g6b-independence-schema/v2"
)
assert independence["dimensions"][5] == "output_root_reservation_sha256"
assert "output_root" not in independence["dimensions"]
assert set(independence["fingerprint_subject_map"]) == set(
    independence["dimensions"]
)
assert "independent" not in independence["allowed_claim_predicates"]
~~~

Also freeze the exact claim lattice:
canonical_byte_distinctness, provenance_nonreuse,
semantic_non_derivation, construction_process_separation,
mechanism_diversity, random_process_independence,
confirmation_blinding, and bounded_nonreuse_admission.

The tests that own Section 17.3 requirements 1, 2, and 36 are named
test_spec_17_3_01_schema_state_order,
test_spec_17_3_02_schema_only_capabilities_false, and
test_spec_17_3_36_no_status_upgrade_from_intermediate_state. Each includes one
valid expected object and at least one falsifying mutation.

Before production edits, also add every vocabulary-entry, subject, policy,
claim-predicate, legacy-flag, row-family-reference, and recursive forbidden-
claim mutation described in Step 4.

- [ ] **Step 2: Verify RED**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py
~~~

Expected: v1/v2 version mismatch and missing typed-vocabulary/claim-lattice
fields. Existing ontology and negative-control tests must remain green.

- [ ] **Step 3: Implement the exact v2 documents and validator constants**

Use this exact dimension-to-subject map:

~~~python
{
    "case_content_sha256": "case_unit",
    "state_snapshot_sha256": "case_unit",
    "route_signature_sha256": "case_unit",
    "parameter_tuple_sha256": "case_unit",
    "random_stream_manifest_sha256": "method_observation",
    "output_root_reservation_sha256": "method_observation",
    "sealed_prediction_sha256": "case_unit",
    "metric_schema_sha256": "method_companion_group",
}
~~~

Use this exact dimension-to-policy map:

~~~python
{
    "case_content_sha256": "strict_semantic_distinctness",
    "state_snapshot_sha256": "strict_semantic_distinctness",
    "route_signature_sha256": "strict_semantic_distinctness",
    "parameter_tuple_sha256": "strict_semantic_distinctness",
    "random_stream_manifest_sha256": "disjoint_random_substreams",
    "output_root_reservation_sha256": "provenance_containment_only",
    "sealed_prediction_sha256": "strict_semantic_distinctness",
    "metric_schema_sha256": "controlled_schema_reuse",
}
~~~

The top-level validator must:

- accept exactly the five existing top-level JSON filenames;
- require protocol v2 and independence v2 while preserving estimand v2,
  negative-controls v1, and top failure-ledger v1;
- reject a top-level typed capability value object, because canonical row-family
  values live only in the nested protocol;
- reject legacy output_root in every v2 dimension list;
- reject a claim lattice that collapses predicates into independent;
- keep current scientific_execution_authorized false.

- [ ] **Step 4: Audit the pre-existing drift and claim-boundary RED tests**

Confirm Step 1 mutates each vocabulary entry, subject, policy, claim predicate,
legacy flag, and row-family reference, and includes a recursive test that rejects claims equivalent
to G6-B passed, eight independent dimensions, exact/DES as two independent
cases, or confirmation.

- [ ] **Step 5: Verify GREEN and unchanged files**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_protocol.py
git diff --exit-code -- cases/discovery/g6b/estimand_schema.json cases/discovery/g6b/negative_controls.json cases/discovery/g6b/failure_ledger.json
~~~

Expected: top-level tests pass and all three preserved files have no diff.

- [ ] **Step 6: Commit**

~~~bash
git add cases/discovery/g6b/protocol.json cases/discovery/g6b/independence_schema.json src/ims_deadlock/g6b_protocol.py tests/test_g6b_protocol.py
git commit -m "feat: migrate G6-B foundation to typed v2 governance"
~~~

### Task 3: Build The Pure Schema-Contract Vocabulary And Validators

**Files:**

- Create: tests/test_g6b_schema_contracts.py
- Create: src/ims_deadlock/g6b_schema_contracts.py

- [ ] **Step 1: Write red tests for every closed vocabulary**

The test imports and freezes these public constants:

~~~python
CAPABILITY_NAMES = (
    "case_construction",
    "retired_authority_fingerprint_normalization",
    "target_certification_preflight",
    "quantitative_execution",
)

CAPABILITY_FIELDS = (
    "case_construction_authorized",
    "retired_authority_fingerprint_normalization_authorized",
    "target_certification_preflight_authorized",
    "quantitative_execution_authorized",
)

FINGERPRINT_DIMENSIONS = (
    "case_content_sha256",
    "state_snapshot_sha256",
    "route_signature_sha256",
    "parameter_tuple_sha256",
    "random_stream_manifest_sha256",
    "output_root_reservation_sha256",
    "sealed_prediction_sha256",
    "metric_schema_sha256",
)

PROJECTION_KINDS = (
    "controlled_schema",
    "provenance_containment",
    "random_process",
    "semantic_content",
)

COMPARISON_POLICIES = (
    "controlled_schema_reuse",
    "disjoint_random_substreams",
    "provenance_containment_only",
    "strict_semantic_distinctness",
)
~~~

Freeze the exact bundle, case, and method state arrays from Section 13; the
dimension_status and comparison_status arrays from Section 7.8; the six refusal
code groups from Section 14; the fourteen Barrier-A operations, eight output
schema IDs, eleven file roles, and exact role-to-schema map from Section 4; the
preflight and quantitative placeholder vocabularies; the project-import,
writer, forbidden-import, forbidden-call, forbidden-result, and forbidden-side-
effect arrays from Sections 10.3 and 16.3.3-16.3.4.

Before production code exists, also add the named RED tests for Section 17.3
requirements 6, 11, 25, 26, 29, 30, 34, and 39-44. At this task they own only
closed-vocabulary, exact-key, partition, command-manifest, source-pointer,
file-role, refusal-union, overlap-lock, and hash-reconciliation primitives.
Every test contains a valid synthetic object, one explicit mutation, and the
exact refusal code expected from that mutation.

Before production edits, also add every category/accounting mutation described
in Step 4.

- [ ] **Step 2: Verify RED**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_schema_contracts.py
~~~

Expected: import failure because ims_deadlock.g6b_schema_contracts does not
exist.

- [ ] **Step 3: Implement immutable constants and narrow public APIs**

Expose tuples and MappingProxyType-backed maps. Do not expose a mutable list or
dict as a module constant. Implement:

~~~python
def validate_exact_keys(
    value: Mapping[str, JsonValue],
    required: Collection[str],
    *,
    label: str,
) -> None: ...

def validate_typed_capabilities(value: Mapping[str, JsonValue]) -> None: ...

def validate_subject_free_projection(
    dimension: str,
    projection: Mapping[str, JsonValue],
) -> None: ...

def validate_refusal_codes(
    gate: Literal[
        "construction",
        "normalization_overlap",
        "preflight",
        "quantitative",
        "ledger",
    ],
    codes: Sequence[str],
) -> None: ...

def validate_declared_terminal_partition(
    declared_ids: Sequence[str],
    terminal_id_sets: Mapping[str, Sequence[str]],
    counts: Mapping[str, int],
) -> None: ...

def validate_command_manifest(
    manifest: Mapping[str, JsonValue],
    command_records: Mapping[str, Mapping[str, JsonValue]],
    *,
    capability: Literal["target_certification_preflight", "quantitative_execution"],
) -> None: ...

def validate_file_role_cardinality(
    *,
    batch_status: str,
    certified_count: int,
    refused_count: int,
    failure_ledger_entry_count: int,
    file_roles: Sequence[str],
) -> None: ...

def validate_source_pointer_use(
    source_path: str,
    json_pointer: str | None,
    allowed_use: str,
    matrix: Sequence[Mapping[str, JsonValue]],
) -> None: ...
~~~

The validators are pure. They do not read the repository, write files, import
engine/model/terminal/CTMC/DES modules, or infer omitted values.

- [ ] **Step 4: Audit the pre-existing category and accounting RED tests**

Confirm the Step 1 tests reject:

- an extra/missing/currently true capability;
- a case ID in a subject-free semantic projection;
- bundle/method/group IDs, filenames, repo paths, display labels, author,
  timestamp, review ID, or new-G6-B provenance labels in subject-free
  projections;
- state_space_hash substituted for state_snapshot_sha256;
- exact/DES counted as two case IDs;
- a method or companion group absent from declared maps;
- overlapping, incomplete, duplicated, or miscounted terminal ID partitions;
- a wrong-gate or free-form refusal code;
- an operation alias, reordered Barrier-A operation, unknown output schema,
  file role, wrong role/schema mapping, duplicate ownership, or wrong
  conditional cardinality;
- wildcard/glob/prefix scope, shell string, redirection, command substitution,
  unknown placeholder, unknown environment variable, or downstream
  runtime-lock/authorization reference inside an upstream command manifest;
- a source pointer read for a different allowed use, a raw-bytes-only JSON
  parse, or permissions unioned across two matrix rows.

- [ ] **Step 5: Verify GREEN and static import isolation**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_schema_contracts.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -c "import ast, pathlib; p=pathlib.Path('src/ims_deadlock/g6b_schema_contracts.py'); names={n.module for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.ImportFrom)}; assert not any(name and name.startswith('ims_deadlock.') for name in names)"
~~~

Expected: all contract tests pass and the module has no project import.

- [ ] **Step 6: Commit**

~~~bash
git add src/ims_deadlock/g6b_schema_contracts.py tests/test_g6b_schema_contracts.py
git commit -m "feat: add pure G6-B schema contract validators"
~~~

### Task 4: Migrate The Nested Bundle From Exact Eight To Exact Twelve

**Files:**

- Modify: tests/test_g6b_row_family_protocol.py
- Modify: src/ims_deadlock/g6b_row_family_protocol.py
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/row_family_protocol.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/identity_schema.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/reuse_matrix.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/overlap_report_schema.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/runtime_lock_schema.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/review_state.json
- Modify: cases/discovery/g6b/row_families/structural_discovery_v1/failure_ledger.json
- Create: cases/discovery/g6b/row_families/structural_discovery_v1/case_construction_schema.json
- Create: cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json
- Create: cases/discovery/g6b/row_families/structural_discovery_v1/target_certification_schema.json
- Create: cases/discovery/g6b/row_families/structural_discovery_v1/quantitative_authorization_schema.json

- [ ] **Step 1: Write red exact-inventory, version, and current-state tests**

Freeze this exact ordered document tuple:

~~~python
(
    "row_family_protocol.json",
    "identity_schema.json",
    "row_family_matrix.json",
    "reuse_matrix.json",
    "overlap_report_schema.json",
    "runtime_lock_schema.json",
    "review_state.json",
    "failure_ledger.json",
    "case_construction_schema.json",
    "retired_authority_fingerprint_schema.json",
    "target_certification_schema.json",
    "quantitative_authorization_schema.json",
)
~~~

Freeze these changed versions:

~~~python
{
    "row_family_protocol.json": "ims-deadlock/g6b-row-family-protocol/v2",
    "identity_schema.json": "ims-deadlock/g6b-row-family-identity/v2",
    "row_family_matrix.json": "ims-deadlock/g6b-row-family-matrix/v1",
    "reuse_matrix.json": "ims-deadlock/g6b-row-family-reuse/v2",
    "overlap_report_schema.json": (
        "ims-deadlock/g6b-row-family-overlap-schema/v2"
    ),
    "runtime_lock_schema.json": (
        "ims-deadlock/g6b-row-family-runtime-lock-schema/v2"
    ),
    "review_state.json": "ims-deadlock/g6b-row-family-review-state/v2",
    "failure_ledger.json": (
        "ims-deadlock/g6b-row-family-failure-ledger/v2"
    ),
    "case_construction_schema.json": (
        "ims-deadlock/g6b-case-construction-schema/v1"
    ),
    "retired_authority_fingerprint_schema.json": (
        "ims-deadlock/g6b-retired-authority-fingerprint-schema/v1"
    ),
    "target_certification_schema.json": (
        "ims-deadlock/g6b-target-certification-schema/v1"
    ),
    "quantitative_authorization_schema.json": (
        "ims-deadlock/g6b-quantitative-authorization-schema/v1"
    ),
}
~~~

Assert row_family_protocol.json.typed_capabilities equals:

~~~python
{
    "case_construction_authorized": False,
    "retired_authority_fingerprint_normalization_authorized": False,
    "target_certification_preflight_authorized": False,
    "quantitative_execution_authorized": False,
}
~~~

Assert source_design is the approved 2026-08-01 specification and
source_design_sha256 equals the approved digest. Assert review_state remains
ROW_FAMILY_BUNDLE_IMPLEMENTED/PENDING and references the capability object and
its canonical SHA rather than duplicating booleans.

Before any JSON or validator edit, add the schema-shape cases assigned to Task
4 in the TDD table. For every changed/new JSON, the RED suite includes one
missing top-level key, one extra key, one version drift, one reordered set-like
array, one wrong nested field, and one recursive live-instance/prohibited-field
mutation. It also includes a parameterized exact-document mutation walker that
changes every scalar leaf and removes every list/map member at least once. The
scan must distinguish required vocabulary strings in descriptive arrays from
live instance-shaped objects.

- [ ] **Step 2: Verify RED**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_row_family_protocol.py -k "inventory or version or capability or review_state"
~~~

Expected: four missing documents, v1/v2 mismatches, and missing typed capability
reference/hash. The preserved row-family matrix tests must not fail.

- [ ] **Step 3: Encode the seven existing v2 documents**

Use these responsibilities:

- row_family_protocol.json: exact twelve-file manifest, source spec commit/hash,
  false typed capabilities, schema-only role, PENDING review, and closed
  execution boundary for case construction, retired normalization, target
  preflight, quantitative execution, output inspection, and status advance.
- identity_schema.json: exact eight dimensions, subject/projection/policy maps,
  Section 7.1 fingerprint fields, Section 7.4 projection descriptors,
  dependency/correlation rules, method-owned exact not-applicable records,
  inert output-root reservation contract, and subject-free/provenance split.
- reuse_matrix.json: case-, method-, and companion-group subject rules;
  controlled metric reuse; one-case/two-method exact-DES counting; no claim of
  independence.
- overlap_report_schema.json: G4/G5/G6-R lineage-deduplicated typed admission,
  per-case/per-method/per-group maps, terminal partitions/counts, semantic
  lineage and reuse record references, and fail-closed incomplete status.
- runtime_lock_schema.json: distinct input-overlap authority,
  target-certification, and quantitative runtime-lock descriptors; no lock
  contains a downstream authorization field.
- review_state.json: exact Section 13 bundle-state order, exact case/method
  states, current ROW_FAMILY_BUNDLE_IMPLEMENTED, forward-only semantics,
  aggregate predicate definitions, typed-capability reference/hash, PENDING.
- failure_ledger.json: append-only empty current ledger plus the exact
  lexicographically sorted six refusal groups and vocabulary version. An empty
  current ledger means no authorized current attempt, never no historical
  failure.

Remove current mutable case/science booleans from all v2 documents except the
single typed-capability object in row_family_protocol.json. Preserve
row_family_matrix.json byte-for-byte.

- [ ] **Step 4: Encode the four new schema files exactly**

For each file, copy the exact top-level key table and field-name arrays from
Sections 16.3.1-16.3.4 into closed JSON objects. Specific non-negotiable checks:

- case construction includes semantic_lineage_declaration_hashes, exact
  case/method/group key-set/count relations, recursive additionalProperties =
  false, inert root reservation, and recursive prohibited fields;
- retired authority includes the exact source inventory, nine-case
  protocol-kind map, composite subunit selectors, per-authority/dimension
  producer map, exact pointer-to-single-use matrix, no historical builders,
  lineage deduplication, and schema_does_not_authorize_normalization = true;
- target certification includes the one-command tokenized manifest, two
  environment variables, exact Barrier-A operations/schema IDs/file roles/
  role map/cardinalities, project import/writer allowlists, forbidden
  imports/calls/results/side effects, batch partitions/counts, and
  schema_does_not_authorize_preflight = true;
- quantitative authorization includes same-target fields, six-field runtime
  identity, tokenized multi-command manifest, exact non-wildcard scope,
  output-root/run/retry/stop policies, original-denominator claim boundary, and
  schema_does_not_authorize_quantitative_execution = true.

Schema files may contain artifact_id, authorization_id, runtime_lock_id,
case_unit_id, method_observation_id, and related names only as exact descriptive
schema vocabulary required by Section 16.3. They may not contain live ID
values, live instance-shaped objects, observed results, materialized roots, or
authorized = true.

- [ ] **Step 5: Update the validator without adding execution capability**

The validator may load the exact twelve files, reject duplicate members, verify
exact documents/versions, call pure canonical/schema helpers, verify the source
spec SHA, scan recursively for live instance/result shapes, and prove the later
instance roots absent. The scanner explicitly allows required_fields,
allowed_*_fields, prohibited-field vocabularies, and other closed descriptive
arrays while rejecting the same names when used as live object fields/values.
It must not import a normalizer, runner, engine, model, terminal-class, CTMC,
DES, scoring, confirmation, CLI, or writer module.

- [ ] **Step 6: Audit the pre-existing file-by-file RED suite for completeness**

Confirm the Step 1 tests cover every changed/new JSON, every scalar leaf, every
list/map member, and the vocabulary-versus-live-instance distinction. Do not
add an unobserved test after production and call it TDD evidence. Any newly
discovered gap must first be made RED against the current implementation, then
fixed minimally and recorded as a late-found mutation gap.

- [ ] **Step 7: Verify GREEN and preserved matrix**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_row_family_protocol.py
git diff --exit-code -- cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json
~~~

Expected: row-family tests pass; row_family_matrix.json has no diff.

- [ ] **Step 8: Commit**

~~~bash
git add cases/discovery/g6b/row_families/structural_discovery_v1 src/ims_deadlock/g6b_row_family_protocol.py tests/test_g6b_row_family_protocol.py
git commit -m "feat: implement exact-twelve G6-B schema bundle"
~~~

### Task 5: Implement The Schema-Tranche Portions Of The Required Contracts

**Files:**

- Modify: tests/test_g6b_canonical_json.py
- Modify: tests/test_g6b_schema_contracts.py
- Modify: tests/test_g6b_protocol.py
- Modify: tests/test_g6b_row_family_protocol.py
- Modify: src/ims_deadlock/g6b_schema_contracts.py
- Modify: src/ims_deadlock/g6b_row_family_protocol.py

- [ ] **Step 1: Add reusable valid hypothetical-record fixtures**

Fixtures are in-memory or tmp_path-only and may describe future records without
creating a governed instance. Add builders for:

~~~python
def valid_fingerprint_record(*, dimension: str) -> JsonObject: ...
def valid_output_root_reservation() -> JsonObject: ...
def valid_normalization_authorization() -> JsonObject: ...
def valid_overlap_report() -> JsonObject: ...
def valid_preflight_command_manifest() -> tuple[JsonObject, dict[str, JsonObject]]: ...
def valid_preflight_batch_manifest() -> JsonObject: ...
def valid_same_target_lock() -> JsonObject: ...
def valid_quantitative_command_manifest() -> tuple[JsonObject, dict[str, JsonObject]]: ...
def valid_quantitative_authorization() -> JsonObject: ...
~~~

Every self-hashed fixture starts with its one self-hash field equal to None,
calls finalized_self_hash, and then validates. Fixture IDs are synthetic,
clearly test-only, and never written under a governed repository root.
Authorization fixtures may set authorized = true solely to prove that the pure
future-artifact validator can represent a separately gated authorization. Add
an invariant that the pure validator accepts the valid synthetic object while
the schema-bundle/current-state/governed-root validator rejects the same object
if it is placed on any current committed surface. This is
SCHEMA_REPRESENTABILITY_ONLY, never capability evidence and never a current
state transition.

Add closed oracle tables rather than prose-only expectations:

- projection fixtures: exact canonical bytes and SHA-256 before/after every
  governance-only and scientific-content mutation;
- semantic-lineage fixtures: origin/inherited IDs, unique-lineage count, and
  exact duplicate-lineage refusal code;
- retired source-selector fixtures: exact source path, JSON pointer or
  raw-bytes marker, one allowed use, forbidden uses, and refusal code;
- G4 manifest/freeze fixtures: exact path/ID/hash triples plus one mutation for
  missing, extra, duplicate, cross-ID, and wrong-base path;
- composite-subunit fixtures: parent ID, subunit selector, deterministic
  subunit ID/hash, and rename/copy refusal; and
- refusal fixtures: gate, valid union, one wrong-gate code, and exact expected
  exception/refusal code.

Add
test_spec_18_schema_retired_authority_declared_sources_and_lineage_statuses_are_reproduced_without_outcome_reads.
It loads only the v2 schema inventory, source-selector/use matrix, lineage map,
and synthetic fixture metadata. It requires one exact fixture row for every
declared retired source selector and every direct, derived, inherited,
not-applicable, unreconstructable, and normalizer-error status. It checks exact
expected status/lineage and fail-closed mutations for missing source, stale
hash, wrong lineage, duplicate lineage, local-only/unverified source, and any
unreconstructable or normalizer-error record changed to pass_distinct. It never
opens or parses result/stdout/stderr/status/outcome payloads. This is Section 18
schema-tranche fixture evidence, not proof of an actual normalizer runtime.

- [ ] **Step 2: Verify fixture tests fail before missing validators are added**

Run:

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_schema_contracts.py -k "fixture or hypothetical"
~~~

Expected: failures identify unimplemented pure validators, not schema parse
errors and not scientific code.

- [ ] **Step 3: Write RED behavioral and mutation tests for the pure surfaces**

Write tests that require exact validators for:

- fingerprint record fields, dimension/subject/projection/policy relation,
  subject-free payload closure, dependencies/correlations, and self-hash;
- output-root reservation template/path/reserved/materialized/self-hash;
- lineage origin/inheritance/duplicate rules and one-unique-lineage accounting;
- source inventory/pointer/use rows and normalizer capability allowlists;
- overlap subject maps, terminal partitions, relation ownership, count
  reconciliation, and complete/incomplete status;
- command token unions, environment maps, command-ID/hash maps, upstream-only
  hash references, and wildcard prohibition;
- preflight file-role/schema/cardinality and batch set/count relations;
- same-target exact/DES one-case/two-method identity;
- quantitative exact scope, certificate/lock/root maps, run-role/retry/stop
  policy, and original-denominator claim boundary;
- recursive additional-property/prohibited-key scanning; and
- AST import/call/writer analysis over supplied source strings.

Do not add production behavior in this step. Tests use synthetic source strings
for the future allowlist guards and synthetic record objects for all later
artifact shapes. They must not read prohibited historical outcome payloads.

- [ ] **Step 4: Add the exact requirement-to-test and tranche-status matrix**

Complete the named test groups begun in Tasks 1-4 so every numbered requirement
has at least one behavior-specific test. Names begin
test_spec_17_3_NN_schema_ so coverage can be audited mechanically without
implying runtime-capability proof. Add an exact 1..44 manifest that lists every
fully qualified collected test ID and owning task. Add a separate status object
per number with schema_tranche and runtime_capability fields. Requirements 15
and 27 use PASS_SCHEMA_GUARD_ONLY plus
DEFERRED_REQUIRES_SEPARATE_GATE; every other entry uses PASS_SCHEMA_TRANCHE and
NOT_REQUIRED_BY_THIS_SCHEMA_ITEM unless the approved specification explicitly
assigns a later runtime proof. Status changes occur only after the stated
positive and negative oracle passes.
Any aspect that validates a synthetic authorized = true record carries the
additional label SCHEMA_REPRESENTABILITY_ONLY and cannot satisfy a capability,
current-state, or runtime-evidence row.

1. State order places normalization/overlap before preflight and preflight
   before quantitative authorization.
2. Current state remains PENDING and all four capabilities false.
3. Null-placeholder self-hash and DAG mutations fail.
4. Canonical JSON duplicate/NFC/number/path/set-array mutations fail.
5. Historical numeric tokens use exact Decimal conversion.
6. Fingerprint subject/projection/payload/dependency/correlation/envelope
   relations are enforced.
7. Governance-only ID/path/label/timestamp changes leave subject-free
   projection hashes invariant.
8. Renamed retired content and paraphrased unchanged predictions refuse;
   provenance-envelope inequality cannot rescue them.
9. Scientific content mutations change the owning projection without
   converting correlated subdimensions into independent evidence.
10. state_snapshot is pre-enumeration, parent-linked, subject-free, and cannot
    be replaced by state_space_hash.
11. Unknown scientific input fields refuse rather than hash silently.
12. Retired inventory missing/stale/mismatched/local-only/unverified states
    fail closed.
13. G5/G6-R inherited G4 records keep one lineage and one evidence count.
14. Direct/derived/inherited/not-applicable/unreconstructable statuses remain
    distinct and failures never become pass_distinct.
15. The schema and synthetic source analyzer reject normalizer imports, calls,
    reads, and outputs outside the exact data-only allowlist. Runtime behavior
    of an actual normalizer is deferred because no normalizer may exist in this
    tranche.
16. Exact methods own provenance envelopes; equal subject-free not-applicable
    projections yield only not_applicable_by_protocol_pass.
17. Stochastic streams require a disjoint-substream proof; unequal hashes alone
    do not pass.
18. Output-root reservations are deterministic/inert/containment-only and
    cannot rescue copied content.
19. G4 root is not-applicable; G5/G6-R root projections exclude absolute
    prefixes and output content.
20. Metric reuse requires one exact companion-group authorization and preserves
    one-case/two-method counting.
21. Method refusal propagates to its case and sealed methods cannot be dropped.
22. Overlap report covers every case, method, group, unique lineage, and
    required dimension with zero pending for a complete state.
23. Refused and superseded objects remain in later manifests.
24. Unknown/forbidden keys are rejected recursively under every permitted
    nested container.
25. Preflight and quantitative locks are distinct and contain no downstream
    authorization circularity.
26. Preflight authorization has exact scope, imports, writers, and tokenized
    command records.
27. The schema and synthetic source analyzer reject preflight imports/calls of
    hazardous symbols and writers outside the exact allowlist; the governance
    validator is import-guarded from any runner. Runtime-spy proof of an actual
    preflight entrypoint is deferred because no runner may exist in this
    tranche.
28. Preflight result fixtures reject quantitative/scoring/summary/output-root
    fields at every depth.
29. Every declared preflight case is terminal or the batch is incomplete.
30. Batch terminal sets are disjoint/complete and counts/hash-map keys match.
31. Certified records require all runtime hashes and estimand_id.
32. Exact/DES share one case, target, certificate, domain hash, and metric
    schema while retaining distinct method IDs.
33. Failed mandatory control blocks quantitative authorization.
34. Quantitative authorization rejects wildcard, implicit, prefix, glob, null,
    or expanded scope.
35. Failure/refusal/negative/boundary evidence is append-only.
36. No schema, normalization, overlap, or preflight state implies a G6-B or
    later-stage status upgrade.
37. G4 manifest/freeze path-ID-hash sets reconcile exactly; missing/extra/
    duplicate/cross-ID/wrong-base paths fail.
38. Grid cells, L30 inequalities, and B05 monitors expand as deterministic
    parent-owned subunits; renamed enclosing IDs cannot rescue a copied subunit.
39. Each retired dimension uses only its exact producer row; wrong branch,
    missing pointer, fabricated not-applicable, or unlisted transform refuses.
40. Each source selector grants one use only; result/stdout/stderr/status/path/
    count/byte values never enter comparison projections.
41. Barrier A rejects aliases, wrong order, schema/role/map/cardinality drift,
    and duplicate file ownership.
42. Each gate accepts exactly cross-gate union named-gate refusal codes.
43. Overlap lock rejects branch/dirty/non-linked/tree/admin-hash/privacy-path
    drift.
44. Command manifests reconcile hashes/maps/placeholders/environments and
    cannot reference downstream locks or authorizations.

- [ ] **Step 5: Add a mechanical collection and status audit**

Parse the four test modules with ast and collect only FunctionDef/
AsyncFunctionDef names beginning test_spec_17_3_NN_schema_. Require every
integer 1..44 to occur at least once, require every fully qualified test ID to
appear exactly once in the requirement manifest, reject orphan test IDs, and
reject skip/skipif/xfail decorators on those nodes. Multiple tests for one
number are allowed only when the manifest names distinct aspects and owners.
Validate the exact 1..44 tranche-status object and require the special schema-
guard/runtime-deferred pair for 15 and 27. Then run pytest --collect-only on the
four files and confirm every manifest item is collected. Comments and strings
cannot satisfy this audit.

This mechanical audit proves collection and honest tranche status, not test
adequacy. The specification reviewer must confirm that each non-deferred item
exercises at least one valid fixture and one mutation with an exact refusal
oracle; tests 15 and 27 must exercise those oracles for their schema-guard
portion without claiming runtime proof.

- [ ] **Step 6: Run RED/GREEN in narrow groups, then the combined suite**

For each group, first run the new named test and read the expected failure, then
implement the minimal pure validator and rerun. The implementation may add only
the pure validators enumerated in Step 3; it may not add a normalizer, case
builder, preflight runner, writer, or quantitative runner. After all groups:

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_canonical_json.py tests/test_g6b_schema_contracts.py tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
~~~

Expected: all four files pass with no warning or xfail. Do not mark a future
runtime capability as tested; the AST/synthetic tests prove only the schema-
level guard while the runner remains absent.

- [ ] **Step 7: Commit**

~~~bash
git add src/ims_deadlock/g6b_schema_contracts.py src/ims_deadlock/g6b_row_family_protocol.py tests/test_g6b_canonical_json.py tests/test_g6b_schema_contracts.py tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
git commit -m "test: harden G6-B v2 governance mutations"
~~~

### Task 6: Prove Capability Absence And Update Durable Project State

**Files:**

- Modify: PROJECT_HANDOFF.md
- Modify: docs/ROADMAP.md
- Modify: docs/cases/CASE_CHANGE_LEDGER.md
- Create: docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md
- Test: tests/test_g6b_protocol.py
- Test: tests/test_g6b_row_family_protocol.py

- [ ] **Step 1: Write red absence and inventory tests before documentation edits**

Tests must prove:

~~~python
for relative in (
    "cases/discovery/g6b/row_families/structural_discovery_v1/governance",
    "cases/discovery/g6b/row_families/structural_discovery_v1/case_units",
    "evidence/g6b/target_certification",
    "artifacts/g6b/quantitative",
):
    assert not (REPO_ROOT / relative).exists()

for module in (
    "g6b_retired_normalizer.py",
    "g6b_target_preflight.py",
    "g6b_target_artifacts.py",
    "g6b_quantitative_runner.py",
):
    assert not (REPO_ROOT / "src/ims_deadlock" / module).exists()
~~~

Add Git-diff scope tests that reject changes under G4/G5/G6-R evidence,
scientific artifact roots, case-instance roots, or the approved specification.
The oracle compares both tracked changes and untracked files against the exact
Task-5 authority HEAD: use git diff --name-status <task5_head> -- plus
git ls-files --others --exclude-standard. Fail with the first forbidden path
and its policy category; an untracked file is never omitted from the scope
decision.

- [ ] **Step 2: Verify RED only for stale documentation assertions**

Run the absence checks and current documentation inventory assertions. Expected:
capability/artifact absence checks pass; documentation tests fail because the
handoff/roadmap/ledger still describe exact eight.

- [ ] **Step 3: Update current status documents without rewriting history**

PROJECT_HANDOFF.md becomes the single continuation entrypoint and records:

- exact implementation branch, the Task-5 schema-code subject commit, and the
  approved spec digest; it does not attempt to embed the hash of the commit
  that contains itself;
- exact-twelve schema bundle and new validator modules;
- tests/static evidence with commands and counts;
- stale exact-eleven worktree quarantine;
- all four capabilities false and every later instance root absent;
- no case, normalization run, preflight, CTMC, DES, output inspection, or
  scientific verdict;
- next gate is independent schema review, then a separately approved
  case-construction plan, not science.

docs/ROADMAP.md updates only the current G6-B row to exact-twelve schema-only
governance and retains OPEN/PENDING. docs/cases/CASE_CHANGE_LEDGER.md appends a
new row; it does not edit the historical exact-eight row. The new verification
document records actual evidence and reviewer verdicts only after they exist;
unknown counts are not guessed.

- [ ] **Step 4: Verify documentation and claim language**

Run searches that must return no current-v2 claim equivalent to:

- G6-B passed;
- all cases independent;
- eight independent dimensions;
- exact and DES are two independent cases;
- preflight is non-scientific;
- confirmation, generality, robustness, or top-journal readiness.

Historical documents may contain quoted forbidden examples or earlier
protocol-only states; the check must target the changed/current v2 documents,
not erase history.

- [ ] **Step 5: Commit**

~~~bash
git add PROJECT_HANDOFF.md docs/ROADMAP.md docs/cases/CASE_CHANGE_LEDGER.md docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
git commit -m "docs: record G6-B schema-only v2 boundary"
~~~

### Task 7: Run Verification, Independent Reviews, And Publish The Branch

**Files:** no planned production changes; reviewer-directed fixes return to the
owning task and repeat that task's tests.

Maintain an exact Section 18 verification-status table in the review document.
Every row starts NOT_RUN and records subject commit, command/reviewer, and
count or finding total before transition:

| Section 18 gate | Allowed completed status in this tranche |
| --- | --- |
| targeted G6-B protocol/row-family/new tests | PASS_EXECUTED |
| state/subject/overlap/runtime/capability/refusal tests | PASS_SCHEMA_TRANCHE |
| full repository suite at exact commit | PASS_EXECUTED |
| Ruff check and Python format check | PASS_EXECUTED |
| strict mypy for source and source/tests | PASS_EXECUTED |
| all tracked JSON duplicate-member parse | PASS_EXECUTED |
| canonical/self-hash properties across qualified runtimes | PASS_EXECUTED |
| every declared retired source and lineage-status fixture without outcome reads | PASS_SCHEMA_TRANCHE; actual normalizer runtime remains DEFERRED_REQUIRES_SEPARATE_GATE |
| exact top-level/nested file sets | PASS_EXECUTED |
| git diff --check | PASS_EXECUTED |
| independent ontology review | PASS_EXECUTED |
| independent scientific/boundary review | PASS_EXECUTED |
| independent code/capability review | PASS_EXECUTED |
| final branch re-lock clean, pushed, 0/0 | PASS_EXECUTED |

No broad Section 18 PASS exists. The review record reports every row
individually and preserves the normalizer-runtime deferral.

- [ ] **Step 1: Re-lock the content-addressed authority**

Before any verification, prove path, linked-worktree identity, branch, HEAD,
upstream relation, clean/expected dirty state, approved spec SHA, and changed
file list. Fail if the approved spec differs or a quarantined/stale file appears
in the branch.

- [ ] **Step 2: Run targeted suites**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_canonical_json.py tests/test_g6b_schema_contracts.py tests/test_g6b_protocol.py tests/test_g6b_row_family_protocol.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q tests/test_g6b_schema_contracts.py -k "spec_18_schema_retired_authority_declared_sources_and_lineage_statuses"
~~~

Expected: PASS, zero warnings/xfails.

- [ ] **Step 3: Run the full repository suite**

~~~bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -p no:cacheprovider -q
~~~

Expected: PASS at the exact candidate commit.

- [ ] **Step 4: Run static, formatting, JSON, and whitespace checks**

~~~bash
python -m ruff check --no-cache .
python -m ruff format --check --no-cache src tests
python -m mypy --strict src
python -m mypy --strict --explicit-package-bases src tests
git diff --check
~~~

Parse every tracked JSON using duplicate-member rejection, validate the exact
five top-level and exact twelve nested filename sets, and recompute every test
self-hash vector. Run Ruff format checks on touched Python files only. Validate
touched Markdown with git diff --check plus the repository's existing named
Markdown/static checks; do not claim Ruff formatted Markdown.
If a full-repository format scan still identifies only the two frozen
historical plan-document debts present at the approved baseline, report them
separately; do not claim global formatting cleanliness and do not expand scope
without a requirement.

- [ ] **Step 5: Run cross-runtime canonical vectors**

Use the qualified project runtime and the second available Python runtime to
recompute the same canonical bytes/digests and historical decimal vectors.
Record exact versions. A mismatch blocks publication.

- [ ] **Step 6: Dispatch three independent read-only reviews**

1. Ontology/scientific reviewer: subjects, lineage, state categories,
   data-only normalization boundary, Barrier A/B separation, claim limits.
2. Specification reviewer: every Section 16.2-16.3 key/array/map and every
   Section 17.3 requirement has implementation/test evidence.
3. Code/capability reviewer: canonicalization, self-hash/DAG, recursive closure,
   AST guards, no writer/science import, test adequacy, and diff scope.

Each item is a separate read-only subagent/pass. Every reviewer reports P0-P3
findings, exact file/line evidence, and the owning task for repair. Any finding
returns to its owning task. Re-run spec review before code-quality review, then
repeat the full verification gate. Reviewer approval is affirmative evidence,
not absence of a response.

- [ ] **Step 7: Finalize the verification record**

Populate docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md with the exact
tested subject commit, spec digest, changed files, test/static counts,
cross-runtime versions,
review findings/resolutions, historical formatting debt boundary, capability
absence, the schema-tranche status of all Section 17.3 items, the deferred
runtime portions of items 15 and 27, and the OPEN/PENDING claim boundary. Do not
enter PASS before evidence, and never summarize a schema-only status as a
runtime-capability pass.

- [ ] **Step 8: Commit any evidence-only review update and push**

~~~bash
git add docs/verification/G6_B_CASE_TARGET_SCHEMA_V2_REVIEW.md PROJECT_HANDOFF.md docs/ROADMAP.md docs/cases/CASE_CHANGE_LEDGER.md
git commit -m "docs: finalize G6-B schema v2 verification"
git push
~~~

If the evidence document was already exact and no file changed, do not create
an empty commit. Re-lock the pushed branch and require upstream ahead/behind
0/0 and clean status.

- [ ] **Step 9: Verify the final evidence-bearing HEAD**

Because Step 8 may create a documentation-only commit after the recorded
subject commit, re-lock that final pushed HEAD and rerun the targeted suite,
full suite, Ruff check/format, both strict mypy commands, tracked-JSON duplicate
parsing, exact-file-set checks, canonical vectors, and git diff --check. Report
the final HEAD and fresh counts in the external handoff without creating a
self-referential documentation loop. A parent-commit PASS is not evidence for
an untested final HEAD.

## Requirement Coverage Audit

| Specification surface | Plan task |
| --- | --- |
| Section 5 typed capability boundary | Tasks 2, 4, 6 |
| Sections 6-8 identity, projections, nonreuse lattice | Tasks 2-5 |
| Sections 9-10 construction/normalization/overlap schema | Tasks 3-5 |
| Sections 11-12 preflight and same-target schema | Tasks 3-5 |
| Sections 13-15 states, refusals, quantitative schema | Tasks 3-5 |
| Section 16 exact versions/files/shapes | Tasks 2-4 |
| Section 17.1 data-only validator | Tasks 1, 3-6 |
| Section 17.2 future runner boundary | Tasks 3, 5, 6 encode and test the guard; no runner is created |
| Section 17.3 tests 1-44 | Tasks 1-6; one collected schema-tranche test group and explicit tranche status per item; runtime portions of 15 and 27 deferred |
| Section 18 verification/reviews | Task 7 |
| Sections 19-20 reporting/claims | Tasks 2, 5, 6 |
| Section 21 stop conditions | Every task; authority/scope lock above |

## Deferred Capabilities, Not Completion Gaps

This plan intentionally does not implement or execute:

- case-construction authorization or case artifacts;
- retired-authority normalization authorization or normalizer output;
- an actual overlap report;
- the Barrier-A runner or target certificates/refusals;
- same-target instance locks;
- quantitative runtime/authorization/runner/output; or
- any G6-B boundary verdict.

The v2 schemas make these later artifacts representable and fail-closed. Each
capability still needs its own reviewed plan and exact authorization instance.
Schema validation is not capability authorization.
