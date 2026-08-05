# G6-B Retired-Authority Fingerprint Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement, independently review, authorize, and execute the first post-R7 data-only G6-B tranche that normalizes the frozen G4, G5, and G6-R retired authorities into canonical fingerprint records without reading scientific outcomes, performing overlap comparisons, enumerating states, or running quantitative science.

**Architecture:** Apply the narrowly scoped companion capability corrigendum, extend the existing schema-contract layer with exact validators for normalization locks, source records, manifests, and authorization bindings, and add one capability-contained `g6b_retired_normalizer` module whose source is statically guarded and whose five artifact-specific writers are restricted to one approved governance root. Implementation and synthetic testing finish first at a source-only commit. A second exact authorization approval binds that source commit, normalizer byte hash, retired-source inventory, canonical two-lane review bundle, and output root before the normalizer may read retired inputs once and materialize an artifact-only successor commit. Completeness is marked only by a valid manifest written last; an interrupted root without that manifest is preserved as incomplete negative evidence and is never promoted or retried silently.

**Tech Stack:** Python 3.13.9, existing `ims_deadlock.g6b_canonical_json` v2 utilities, existing `ims_deadlock.g6b_schema_contracts`, pytest, Ruff, strict mypy, Git linked worktrees, Windows remote runtime qualified by `REMOTE_PROJECT_OPERATIONS.md`.

---

## Status and authority

**Plan state:** `PROPOSED / PLAN-ONLY / AWAITING EXACT-BYTES USER APPROVAL`.

Writing, reviewing, hashing, committing, pushing, or opening a Draft PR for this plan does not authorize implementation or normalization. Implementation begins only after the user names and approves the final raw SHA-256 of this plan, the companion capability corrigendum, and the independent plan-review artifact.

This plan contains two distinct approval gates:

1. **Plan gate:** exact approval of this plan, its companion capability corrigendum, and their independent review authorizes Tasks 1-8 only: isolated implementation, synthetic/input-only tests, static validation, source freeze, and construction/review of an external authorization candidate. It does not authorize parsing retired authorities for projections or creating the normalization root.
2. **Execution gate:** after Task 8, the user must separately name and approve the exact raw/self SHA-256 of the normalization authorization and the exact raw SHA-256 of its independent review. Only that approval authorizes Tasks 9-10.

Ordinary continuation language, Draft PR state, case-construction authorization, hashes, schema tests, or reviewer PASS verdicts do not substitute for either gate.

## Frozen starting subject

The planning base is the clean R7 documentation successor:

- branch: `codex/g6b-case-construction-v2-r6-testfix`;
- C4 commit: `0943e6eeeb17ff9a310d0d4b461cca301c08aefa`;
- C4 tree: `c1ba3956614988c6deb39ead085f6e57cf9e278c`;
- C3 sealed artifact commit: `0fa08e66c249fb19d8c014127cca8441efa90505`;
- C3 tree: `8153fd46c4dae6dbd08a20fec93eab469fa8bc37`;
- C3 bundle manifest raw SHA-256: `95fc411a02d8085b84c1a4f2025d2c7806e1d8c632b645f556c61aefe1b6406b`;
- C3 bundle manifest self SHA-256: `36622495237f2c22677190b3858d275ea8285d0ee8fc1ed004f8c03e8543a68c`;
- R7 review raw SHA-256: `069307796147e25edf077ab8019e1b8b7e5cd2c27b980955c950e1dec2f65739`.

The existing approved design and schema bytes remain immutable:

- `docs/superpowers/specs/2026-08-01-g6b-case-target-certification-design.md` raw SHA-256 `b51b35848bec77ed787696a9c4fc88b4f299bde7368cc34380c2fc9143df3da6`;
- `cases/discovery/g6b/row_families/structural_discovery_v1/retired_authority_fingerprint_schema.json` raw SHA-256 `f0c8b649bee392752aec15aed28ac492584a6071d09ef7bdd963ee28a00323bc`;
- current `src/ims_deadlock/g6b_schema_contracts.py` raw SHA-256 `cf84fff421eae6d31eed5ac578748eb00de4d3bda9095456f979146b523e9a27`;
- current `tests/test_g6b_schema_contracts.py` raw SHA-256 `22f3bc365d141eee3b4d4fa5b210568f0e9d10b65eb501b6a2d51844448c8522`;
- schema v2 review raw SHA-256 `cabdb3c1cf9994197eda58809ea328f01a2558976594c06ef792f2dc0f4cd5ab`.

This plan is accompanied by
`docs/superpowers/specs/2026-08-05-g6b-retired-normalization-capability-corrigendum.md`
at proposed raw SHA-256
`79c843fd64c6249447309b84e19d73b503fdfe9b4372018a483b89e15af23e49`.
It narrowly closes the five-artifact writer surface, exact schema-validator
import surface, Git-object-ID typing, and two-lane source-review aggregation.
Exact approval of this plan must bind those corrigendum bytes. Changing either
original approved design/schema file remains
out of scope. Any further inconsistency stops with a typed refusal and a new
separately reviewed corrigendum; implementation must not silently repair or
broadly reinterpret the frozen specification.

## Scientific boundary

This tranche may:

- byte-hash the exact 27-file concrete retired inventory;
- parse only the schema-declared JSON pointers for their singular declared use;
- reconstruct input-only canonical projections using the frozen producer map;
- record missing or unreconstructable dimensions without favorable selection;
- link G5/G6-R inherited records to one unique G4 lineage;
- create authority lock records, authority source records, fingerprint records, and one normalization manifest inside the authorized governance root.

This tranche must not:

- use G5 result values, G6-R result/report values, stdout/stderr, scores, observed probabilities, observed times, or mechanism verdicts as projection inputs;
- read raw historical output payloads;
- compare new C3 subjects with retired subjects or create an overlap result;
- enumerate/partition an LTS, certify a target, build/solve a CTMC, run DES, score a hypothesis, inspect scientific output, or advance G6-B status;
- create target-preflight, quantitative, confirmation, or manuscript-evidence roots;
- rewrite or delete missing, failed, refused, ambiguous, duplicate-lineage, or unreconstructable records.

At every task boundary, `G6-B` remains `OPEN/PENDING`; `G6-C/D/E` remain `NOT STARTED`; the paper gate remains closed.

The handoff must continue to preserve the already reported G5 `4/3/2`, transparent `6/1/2`, G6 R1/R2 failures, R3 historical-only status, minimality failures, and all refused/inconclusive evidence. Their outcome-bearing source files are raw-byte hash inputs only where the frozen selector matrix says so; the normalizer must not parse those values or use their direction to retain, discard, or rewrite a fingerprint.

## Exact output closure

After the execution gate, the only normalizer-materialized repository output root is:

```text
cases/discovery/g6b/row_families/structural_discovery_v1/
  governance/g6b_retired_authority_normalization_v1/
    normalization_authorization.json
    authority_locks/
      G4_FREEZE.json
      G5_EXECUTION.json
      G6_R_REPLAY_R3.json
    source_records/
      sha256-of-repo-relative-source-path.json
    fingerprints/
      sha256-of-record-id.json
    normalization_manifest.json
```

The angle-bracket descriptions above document cardinality roles, not literal filenames or implementation placeholders. Concrete source-record filenames are `sha256(repo_relative_posix_path).json`; concrete fingerprint filenames are `sha256(record_id).json`. The manifest is written last. No overlap report, comparison record, target certificate, output reservation, scientific summary, or execution result belongs in this root.

## File map

**Create during implementation:**

- `src/ims_deadlock/g6b_retired_normalizer.py` — capability-contained source reader, pointer selector, pure producer map, lineage builder, guarded writers, and command entrypoint.
- `tests/test_g6b_retired_normalizer.py` — synthetic/input-only TDD coverage and actual-module static-guard tests.

**Modify during implementation:**

- `src/ims_deadlock/g6b_schema_contracts.py` — exact manifest/lock/source validators, stronger authorization identity binding, and lexical writer-boundary support.
- `tests/test_g6b_schema_contracts.py` — RED/GREEN tests for the new validators and writer guard.

**Read as binding after exact plan approval:**

- `docs/superpowers/specs/2026-08-05-g6b-retired-normalization-capability-corrigendum.md` — narrow writer, schema-validator import, Git-object-ID, and source-review-bundle repair; it is not an execution authorization.

**Create only after execution authorization:**

- the exact governance root listed above.

**Create after artifact review:**

- `docs/verification/G6_B_RETIRED_AUTHORITY_NORMALIZATION_REVIEW.md`.
- updates to `PROJECT_HANDOFF.md` and `docs/ROADMAP.md` that report normalization only and preserve the stop before actual overlap.

## Runtime and compute policy

- Resolve the project-qualified Python runtime from `REMOTE_PROJECT_OPERATIONS.md` and export it as `G6B_PYTHON`; never reuse another project runtime.
- Every test command sets `PYTHONPATH=%CD%\src`, `PYTHONDONTWRITEBYTECODE=1`, and disables pytest cache.
- The normalizer itself is deliberately sequential. The inventory is 27 small committed files and lineage order is scientific/provenance order; parallel parsing would add nondeterministic failure ordering without material speedup.
- Focused and full pytest may use remote parallel capacity. Before a long run, record logical CPUs, available memory, active Python processes, pytest-xdist availability, and repository status. Use at most four xdist workers with `--dist worksteal` only if the live machine has capacity and an isolated task-owned xdist install exposed as `G6B_XDIST`; keep the exact worktree source first on `PYTHONPATH` and append the dependency directory without modifying the shared canonical environment. Otherwise run serially.
- Do not guess an ETA. Record elapsed time and completed-test percentage after the run has real progress. Continue runs projected under 24 hours. If real progress projects beyond 24 hours and the run remains scientifically necessary, stop before launching or continuing and obtain user approval.
- A disconnected SSH stream is not a failed test and is not permission to start a duplicate run. Reconcile process identity, terminal output, artifact root, and exit record first.

---

### Task 1: Re-lock the approved plan subject and create an isolated implementation lane

**Files:**

- Read: `AGENTS.md`
- Read: `REMOTE_PROJECT_OPERATIONS.md`
- Read: this plan, the companion capability corrigendum, and their final independent review
- No repository file changes

- [ ] **Step 1: Verify exact plan approval**

Resolve the final plan, companion capability corrigendum, and review bytes from the published plan branch. Compute SHA-256 over raw bytes and require exact equality with the three hashes named in the user's approval. The review must itself name the exact plan and corrigendum hashes. Record the plan branch, commit, tree, all three raw hashes, upstream, and clean state in an external task lock. A mismatch is `PLAN_IDENTITY_DRIFT` and stops the task.

- [ ] **Step 2: Re-lock C4 and its publication boundary**

Run from the C4 worktree:

```bat
git branch --show-current
git rev-parse HEAD
git show -s --format=%T HEAD
git status --porcelain=v1
git rev-list --left-right --count @{u}...HEAD
git diff --name-status 0fa08e66c249fb19d8c014127cca8441efa90505..HEAD
```

Expected: branch `codex/g6b-case-construction-v2-r6-testfix`, HEAD `0943e6eeeb17ff9a310d0d4b461cca301c08aefa`, tree `c1ba3956614988c6deb39ead085f6e57cf9e278c`, clean, upstream `0 0`, and exactly the three R7 documentation paths.

- [ ] **Step 3: Create a fresh linked worktree**

Use the worktree root and remote channel defined by `REMOTE_PROJECT_OPERATIONS.md`. Create branch `codex/g6b-retired-normalization` from the exact approved normalization-plan commit. The path and absolute runtime are external lock data and must not be committed.

Verify:

```bat
git branch --show-current
git rev-parse HEAD
git status --porcelain=v1
git rev-parse --git-dir
git rev-parse --git-common-dir
```

Expected: the new branch, the approved plan commit, clean state, and distinct git/common directories proving linked-worktree isolation.

- [ ] **Step 4: Run the narrow clean baseline**

```bat
set PYTHONPATH=%CD%\src
set PYTHONDONTWRITEBYTECODE=1
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_schema_contracts.py -k "normalization_authorization or schema_retired_sources_reproduce_without_outcome_reads"
git diff --check
git status --porcelain=v1
```

Expected at the planning base: `6 passed, 461 deselected`, empty diff-check output, and clean status. Any baseline failure is investigated before editing.

### Task 2: Add RED tests for exact normalization governance records

**Files:**

- Modify: `tests/test_g6b_schema_contracts.py`
- Test: `tests/test_g6b_schema_contracts.py`

- [ ] **Step 1: Add exact fixtures for lock, source, and manifest records**

Add fixtures with the exact schema fields from Sections 7 and 10 of the frozen design. The manifest fixture must contain all 25 fields in `normalization_manifest_required_fields`, three authority-lock hashes, 27 source-record hashes, a key-closed fingerprint hash map, a unique-lineage map, dimension-status counts, explicit missing/unreconstructable lists, comparison eligibility, and a finalized `manifest_sha256`.

Under the approved capability corrigendum, update `valid_normalization_authorization()` so `source_head` and `source_tree_hash` are 40-character lowercase Git SHA-1 object IDs, matching the current repository object format; leave content, review, record, and manifest digests at 64-character SHA-256.

```python
def valid_authority_lock_record(authority_id: str) -> JsonObject:
    record: JsonObject = {
        "authority_id": authority_id,
        "origin_remote": "retired-authority-logical-origin",
        "origin_commit_or_null": "1" * 40,
        "origin_tree_hash_or_null": "2" * 40,
        "origin_lock_artifact_ref": "source:lock",
        "origin_artifact_inventory_hash": "3" * 64,
        "current_merged_copy_tree_hash": "4" * 64,
        "identity_verification_status": "verified_merged_copy_against_historical_hashes",
        "authority_lock_record_sha256": None,
    }
    record["authority_lock_record_sha256"] = finalized_self_hash(
        record, "authority_lock_record_sha256"
    )
    return record
```

Use synthetic hashes and synthetic records only. Do not invoke the future normalizer on repository retired sources.

- [ ] **Step 2: Add fail-closed validator tests**

Add tests that require rejection of:

- extra or missing keys in every record type;
- authority IDs outside `G4_FREEZE`, `G5_EXECUTION`, `G6_R_REPLAY_R3`;
- non-verified lock identities supplying projections;
- source paths outside the exact 27-file inventory;
- `contains_outcome_fields=true` paired with a projection use not allowed by the selector matrix;
- unsorted/duplicate hash maps and lineage members;
- manifest references to absent records or mismatched self-hashes;
- a manifest that upgrades `unreconstructable_refuse` to an eligible comparison;
- authorization source HEAD/tree, file-manifest hash, normalizer code hash, review hash, or output root that differs from the caller-supplied expected value. `source_head` and `source_tree_hash` are Git object IDs resolved under the repository's live object format; in the current SHA-1 repository they are 40 lowercase hexadecimal characters, not generic 64-character content hashes.

The core identity-binding test is:

```python
def test_normalization_authorization_binds_exact_source_code_review_and_root() -> None:
    record = valid_normalization_authorization()
    expected_root = (
        "cases/discovery/g6b/row_families/structural_discovery_v1/"
        "governance/g6b_retired_authority_normalization_v1"
    )
    validate_normalization_authorization(
        record,
        expected_schema_inventory_patterns=EXPECTED_RETIRED_SOURCE_INVENTORY,
        expected_concrete_source_paths=EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY,
        expected_selector_matrix=_retired_selector_rows(),
        expected_git_object_format="sha1",
        expected_source_head=record["source_head"],
        expected_source_tree_hash=record["source_tree_hash"],
        expected_file_manifest_hash=record["expected_file_manifest_hash"],
        expected_normalizer_code_sha256=record["normalizer_code_sha256"],
        expected_review_artifact_hash=record["review_artifact_hash"],
        expected_output_root=expected_root,
    )
```

- [ ] **Step 3: Run RED tests**

```bat
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_schema_contracts.py -k "normalization_manifest or authority_lock_record or authority_source_record or binds_exact_source_code_review_and_root"
```

Expected: failures because the new validators and expanded authorization signature do not exist. Capture this RED result.

- [ ] **Step 4: Commit RED tests only**

```bat
git add tests\test_g6b_schema_contracts.py
git commit -m "test(g6b): specify retired normalization closure"
```

### Task 3: Implement exact record validators and the corrigendum's closed writer surface

**Files:**

- Modify: `src/ims_deadlock/g6b_schema_contracts.py`
- Modify: `tests/test_g6b_schema_contracts.py`

- [ ] **Step 1: Add exact field constants and validators**

Add constants copied mechanically from the frozen schema and implement these exact public signatures:

```text
validate_authority_lock_record(record: Mapping[str, JsonValue]) -> None
validate_authority_source_record(record: Mapping[str, JsonValue], *, authority_lock_hashes: Mapping[str, str], expected_source_hashes: Mapping[str, str], selector_rows: Sequence[Mapping[str, JsonValue]]) -> None
validate_normalization_manifest(manifest: Mapping[str, JsonValue], *, authority_lock_records: Mapping[str, Mapping[str, JsonValue]], authority_source_records: Mapping[str, Mapping[str, JsonValue]], fingerprint_records: Mapping[str, Mapping[str, JsonValue]]) -> None
```

Each validator uses `validate_exact_keys`, lower-case SHA-256 checks for content digests, exact caller-bound Git object-ID checks for `source_head`/`source_tree_hash`, finalized self-hash verification, exact inventory closure, exact authority IDs, sorted/unique arrays, and key-closed maps. `comparison_eligibility` is false for any missing, ambiguous, or `unreconstructable_refuse` unique lineage. An inherited or duplicate member that maps unambiguously to one valid origin lineage is a non-counting alias, not an automatic lineage refusal; the unique origin remains eligible exactly once.

- [ ] **Step 2: Strengthen authorization binding**

Replace the ambiguous `expected_inventory` argument with separate caller-supplied `expected_schema_inventory_patterns` and `expected_concrete_source_paths` values. Extend `validate_normalization_authorization` with all caller-supplied expected values shown in Task 2, including `expected_git_object_format`. Reject any missing expected value; require the pattern inventory to equal the frozen 19-row schema list, the concrete paths to equal the expanded 27-file tuple, the authorization's `allowed_source_paths` to equal those 27 paths, and every identity/hash/root binding to match exactly. Require this output schema:

```python
{
    "schema_id": "ims-deadlock/g6b-retired-normalization-records/v1",
    "schema_version": "v1",
}
```

Require this exact repository-relative output root:

```text
cases/discovery/g6b/row_families/structural_discovery_v1/governance/g6b_retired_authority_normalization_v1
```

- [ ] **Step 3: Permit writes only inside the five artifact-specific writer functions**

Apply the exact operation and symbol sequences from the approved capability corrigendum. The only writer symbols are `write_normalization_authorization`, `write_authority_lock_record`, `write_authority_source_record`, `write_fingerprint_record`, and `write_normalization_manifest`. Mark AST call nodes lexically enclosed by only those five top-level function definitions. Permit only `Path.mkdir`, `Path.write_bytes`, and `Path.replace` in those lexical contexts. Continue rejecting `open` in write/append mode, `os.*`, subprocess/network imports, generic writers/publishers, arbitrary writer aliases, and the same calls anywhere else.

Extend the safe Path read surface only with `exists`, `is_file`, `is_symlink`, `read_bytes`, `read_text`, `resolve`, and `relative_to`; teach the call-result alias map that `Path.resolve()` returns another safe Path object. Do not add directory iteration, globbing, deletion, renaming outside the five writer functions, ownership/permission changes, or arbitrary method dispatch. The command entrypoint parses its exact fixed argument vocabulary without importing the project CLI or constructing a dynamic plugin surface.

Add tests proving:

- all five actual writer definitions pass;
- each writer accepts only its fixed artifact role and path grammar;
- the same `Path.write_bytes`, `Path.mkdir`, or `Path.replace` call in any other function fails;
- nested functions/lambdas inside a writer do not inherit writer authority;
- rebinding or aliasing a writer symbol fails;
- writer paths still require runtime containment checks in the normalizer tests.

Apply the corrigendum's exact project-import list and exact five-symbol
`g6b_schema_contracts` call surface. Add AST/import-closure tests proving the
normalizer can call only those validators, `g6b_schema_contracts.py` transitively
imports only `ims_deadlock.g6b_canonical_json`, and any added direct/transitive
project import, unlisted validator call, alias, or rebind fails closed. Do not
create or import `ims_deadlock.g6b_governance`.

- [ ] **Step 4: Run GREEN tests**

```bat
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_schema_contracts.py -k "normalization or retired or fingerprint or normalizer"
%G6B_PYTHON% -B -m ruff check src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_schema_contracts.py
%G6B_PYTHON% -B -m ruff format --check src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_schema_contracts.py
%G6B_PYTHON% -B -m mypy src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_schema_contracts.py
git diff --check
```

Expected: all selected tests pass and all static checks exit 0.

- [ ] **Step 5: Commit validator implementation**

```bat
git add src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_schema_contracts.py
git commit -m "feat(g6b): validate retired normalization records"
```

### Task 4: Specify the capability-contained normalizer with synthetic RED tests

**Files:**

- Create: `tests/test_g6b_retired_normalizer.py`
- Test: `tests/test_g6b_retired_normalizer.py`

- [ ] **Step 1: Add source-reader and selector tests**

Use only temporary synthetic files. Cover duplicate JSON members, non-NFC strings, forbidden floats, exact historical decimals, exact/prefix/element-pointer selectors, raw-bytes-only rows, singular allowed-use enforcement, and refusal on any unlisted pointer.

```python
def test_selector_cannot_reuse_hash_validation_field_as_projection(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"locked_hashes":{"result":"' + "1" * 64 + '"}}', encoding="utf-8")
    with pytest.raises(SchemaContractError, match="source_field_read_violation"):
        select_allowed_value(
            source.read_bytes(),
            pointer="/locked_hashes/result",
            selector_rows=synthetic_selector_rows(),
            requested_use="case_content_projection",
        )
```

- [ ] **Step 2: Add five-writer root-containment and manifest-last tests**

Require the authorization writer to create the previously absent exact root and preserve the exact approved canonical authorization bytes. Require the lock, source, fingerprint, and manifest writers to accept only their fixed artifact roles; canonicalize records through `canonical_bytes_v2`; reject absolute, parent, symlink-dependent, misnamed, or pre-existing destinations; and write the manifest last. Simulate an exception before manifest finalization and assert that the incomplete root is preserved without `normalization_manifest.json`, cannot validate as complete, and cannot be reused or retried in place.

- [ ] **Step 3: Add actual-module static-guard test**

```python
def test_actual_normalizer_source_passes_static_capability_guard() -> None:
    source = Path(normalizer.__file__).read_text(encoding="utf-8")
    validate_normalizer_static_source(source)
```

- [ ] **Step 4: Run RED tests**

```bat
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_retired_normalizer.py
```

Expected: collection fails because `ims_deadlock.g6b_retired_normalizer` does not exist. Capture the RED result.

- [ ] **Step 5: Commit RED tests**

```bat
git add tests\test_g6b_retired_normalizer.py
git commit -m "test(g6b): specify data-only retired normalizer"
```

### Task 5: Implement source containment, canonical writers, and pure record builders

**Files:**

- Create: `src/ims_deadlock/g6b_retired_normalizer.py`
- Modify: `tests/test_g6b_retired_normalizer.py`

- [ ] **Step 1: Implement the closed public surface**

The module exposes only these exact public signatures:

```text
select_allowed_value(source_bytes: bytes, *, pointer: str, selector_rows: Sequence[Mapping[str, JsonValue]], requested_use: str) -> JsonValue
build_authority_lock_records(repo_root: Path, authorization: Mapping[str, JsonValue], source_hashes: Mapping[str, str]) -> dict[str, JsonObject]
build_authority_source_records(repo_root: Path, authorization: Mapping[str, JsonValue], authority_locks: Mapping[str, Mapping[str, JsonValue]]) -> dict[str, JsonObject]
build_retired_fingerprint_records(repo_root: Path, authorization: Mapping[str, JsonValue], authority_locks: Mapping[str, Mapping[str, JsonValue]], source_records: Mapping[str, Mapping[str, JsonValue]]) -> dict[str, JsonObject]
write_normalization_authorization(authorized_root: Path, authorization_bytes: bytes) -> str
write_authority_lock_record(authorized_root: Path, authority_id: str, record: Mapping[str, JsonValue]) -> str
write_authority_source_record(authorized_root: Path, repo_relative_source_path: str, record: Mapping[str, JsonValue]) -> str
write_fingerprint_record(authorized_root: Path, record_id: str, record: Mapping[str, JsonValue]) -> str
write_normalization_manifest(authorized_root: Path, manifest: Mapping[str, JsonValue]) -> str
run_normalization(repo_root: Path, authorization_path: Path, output_root: Path) -> JsonObject
main(argv: Sequence[str] | None = None) -> int
```

Private helpers may parse pointers, hash bytes, validate path containment, compute record IDs, and construct projections. No class definitions, plugins, dynamic imports, subprocesses, sockets, environment discovery, arbitrary callbacks, or filesystem globbing are allowed.

- [ ] **Step 2: Implement read and write containment**

The source reader resolves only a path already present in the exact authorization list and requires `candidate.resolve().is_relative_to(repo_root.resolve())`. It rejects symlinks and verifies raw bytes before parsing. `raw_bytes_only` rows never call `loads_v2`.

The authorization writer alone creates the previously absent exact authorized governance root and copies the already validated, independently approved canonical authorization bytes. The other four writers require that exact root and use only their corrigendum-defined deterministic child paths. Each writer writes canonical bytes to a new sibling temporary file inside the root, verifies the written SHA-256, and uses `Path.replace` once to finalize a previously absent destination. The manifest writer refuses unless every referenced record already exists with matching bytes. If execution fails, the incomplete root and any task-owned temporary record remain without a valid manifest and are preserved for incident review; no cleanup, promotion, overwrite, or in-place retry is allowed.

- [ ] **Step 3: Keep provenance envelopes separate from projections**

Every projection is subject-free and contains only the exact payload fields declared by `fingerprint_payload_schemas`. Authority, stage, subject ID, owner ID, paths, timestamps, and record IDs exist only in the fingerprint envelope. Compute `comparison_projection_sha256_or_null` from the projection and `record_provenance_sha256` from the finalized envelope.

- [ ] **Step 4: Run focused GREEN checks**

```bat
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_retired_normalizer.py -k "selector or writer or static or containment"
%G6B_PYTHON% -B -m ruff check src\ims_deadlock\g6b_retired_normalizer.py tests\test_g6b_retired_normalizer.py
%G6B_PYTHON% -B -m ruff format --check src\ims_deadlock\g6b_retired_normalizer.py tests\test_g6b_retired_normalizer.py
%G6B_PYTHON% -B -m mypy src\ims_deadlock\g6b_retired_normalizer.py tests\test_g6b_retired_normalizer.py
```

Expected: all selected tests and static checks pass.

- [ ] **Step 5: Commit the containment core**

```bat
git add src\ims_deadlock\g6b_retired_normalizer.py tests\test_g6b_retired_normalizer.py
git commit -m "feat(g6b): contain retired normalization IO"
```

### Task 6: Implement the frozen producer map and lineage semantics

**Files:**

- Modify: `src/ims_deadlock/g6b_retired_normalizer.py`
- Modify: `tests/test_g6b_retired_normalizer.py`

- [ ] **Step 1: Lock the G4 protocol discriminator and composite selectors**

Implement the exact nine-case discriminator from Section 10.2. Composite subunits are only grid cells selected by unique `cell_id`, L30 inequalities selected by unique `name`, and B05 candidate monitors selected by unique `monitor_id`. Zero or multiple selector matches refuse. Parent context is exactly the frozen context list; a subunit may not copy a parent-wide prediction unless the producer map explicitly permits it.

- [ ] **Step 2: Implement all eight fingerprint dimensions**

Implement explicit dispatch for:

- `case_content_sha256`;
- `state_snapshot_sha256`;
- `route_signature_sha256`;
- `parameter_tuple_sha256`;
- `random_stream_manifest_sha256`;
- `output_root_reservation_sha256`;
- `sealed_prediction_sha256`;
- `metric_schema_sha256`.

For each authority/subject/dimension, the transform/status and source pointers must match the frozen Section 10.2 producer table. Schema-declared absence produces `not_applicable_retired_stage` with a null projection; missing or ambiguous required input produces `unreconstructable_refuse`, never a guessed value.

- [ ] **Step 3: Implement lineage inheritance and deduplication**

Origin lineage IDs are `sha256:` plus the canonical-v2 hash of exactly the frozen six-field preimage: `origin_authority_id`, `origin_subject_type`, `origin_subject_id`, `origin_dimension`, `origin_comparison_projection_sha256_or_null`, and sorted `origin_source_artifact_byte_hashes`. The record's `source_stage`, `owner_object_id`, `projection_schema_version`, and `normalizer_version` remain provenance/envelope fields and never enter the lineage-ID preimage. G5 and G6-R inherited records copy the exact ancestor lineage ID and name their immediate ancestor. A duplicate record points to the canonical origin, remains visible in the lineage map, and is a non-counting alias; the unique lineage is compared at most once. Missing, ambiguous, or unreconstructable lineage status remains fail-closed and cannot be upgraded downstream.

- [ ] **Step 4: Add exhaustive parameterized tests**

Use synthetic fixtures shaped like all nine G4 protocol kinds plus G5 and G6-R locks. Parameterize every producer-table row, all null statuses, each composite selector, exact-decimal edge cases, G5 root containment, G6-R unique suffix parsing, inheritance, duplicate lineage, and missing/ambiguous refusal. Add golden canonical-hash tests for the exact six-field origin preimage, inherited copies, duplicate aliases, and one-time unique-lineage counting.

The tests must assert that forbidden names such as `completion_probability`, `deadlock_probability`, `mean_absorption_time`, `score`, `stdout`, and `stderr_raw_sha256` never appear in the actual normalizer module source, any projection object, or serialized normalization output. Schema-contract definitions and negative tests may name forbidden fields solely to enforce their rejection.

- [ ] **Step 5: Run the focused suite**

```bat
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q tests\test_g6b_retired_normalizer.py tests\test_g6b_schema_contracts.py -k "retired or normalization or fingerprint or lineage or source_selector"
%G6B_PYTHON% -B -m ruff check src\ims_deadlock\g6b_retired_normalizer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_retired_normalizer.py tests\test_g6b_schema_contracts.py
%G6B_PYTHON% -B -m ruff format --check src\ims_deadlock\g6b_retired_normalizer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_retired_normalizer.py tests\test_g6b_schema_contracts.py
%G6B_PYTHON% -B -m mypy src\ims_deadlock\g6b_retired_normalizer.py src\ims_deadlock\g6b_schema_contracts.py tests\test_g6b_retired_normalizer.py tests\test_g6b_schema_contracts.py
git diff --check
```

Expected: all focused tests and static checks pass.

- [ ] **Step 6: Commit the producer implementation**

```bat
git add src\ims_deadlock\g6b_retired_normalizer.py tests\test_g6b_retired_normalizer.py
git commit -m "feat(g6b): normalize retired authority fingerprints"
```

### Task 7: Freeze and independently review the source-only implementation

**Files:**

- Read/verify: all changed source and tests
- External evidence only: lane reviews, canonical source-review bundle, task locks, and test records
- No normalization output root

- [ ] **Step 1: Verify the actual source against the static guard**

```bat
set PYTHONPATH=%CD%\src
set PYTHONDONTWRITEBYTECODE=1
%G6B_PYTHON% -B -c "from pathlib import Path; from ims_deadlock.g6b_schema_contracts import validate_normalizer_static_source; p=Path('src/ims_deadlock/g6b_retired_normalizer.py'); validate_normalizer_static_source(p.read_text(encoding='utf-8')); print('NORMALIZER_STATIC_GUARD=PASS')"
```

Expected: `NORMALIZER_STATIC_GUARD=PASS`.

- [ ] **Step 2: Run focused verification**

Run the Task 6 focused pytest/Ruff/format/mypy/diff-check commands. Record command, runtime, source binding, duration, exit code, terminal summary, and log SHA-256 externally.

- [ ] **Step 3: Analyze remote parallel capacity before full pytest**

Record CPU count, available memory, active Python/pytest processes, and whether a task-owned pytest-xdist installation imports under the qualified runtime. If four workers are safe, run:

```bat
set PYTHONPATH=%CD%\src;%G6B_XDIST%
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q -n 4 --dist worksteal
```

Otherwise run serially:

```bat
set PYTHONPATH=%CD%\src
%G6B_PYTHON% -B -m pytest -p no:cacheprovider -q
```

Use a task-owned external base-temp and remove it only after a terminal pass and hash capture. Estimate completion only from observed progress.

- [ ] **Step 4: Obtain two independent reviews**

Review lane A (`implementation_contract`) checks implementation/spec/corrigendum compliance, exact pointer-to-use enforcement, five-writer closure, producer coverage, lineage semantics, deterministic serialization, and test adequacy. Review lane B (`scientific_boundary`) checks the scientific boundary, outcome non-readability, capability containment, refusal preservation, and absence of overlap/preflight/quantitative work. Both lanes review the same exact candidate HEAD/tree. Any source or test change invalidates both reviews and requires both lanes to rerun. P0 or P1 blocks source freeze.

- [ ] **Step 5: Freeze source commit C1**

Require a clean index containing only:

```text
src/ims_deadlock/g6b_retired_normalizer.py
src/ims_deadlock/g6b_schema_contracts.py
tests/test_g6b_retired_normalizer.py
tests/test_g6b_schema_contracts.py
```

If review fixes are needed, commit them before rerunning both reviews. C1 is the exact HEAD/tree accepted by both final PASS reviews; no source/test change is permitted after those reviews. Build the capability-corrigendum `source_review_bundle` as canonical JSON v2 with the two sorted lane records, exact C1 HEAD/tree, normalizer byte hash, lane raw hashes/verdicts/P0-P1-P2 counts, aggregate counts, and finalized self-hash. Record C1 commit/tree, raw file hashes, focused/full evidence hashes, both review hashes, bundle raw SHA-256, and bundle self-hash externally. Confirm that the normalization governance root and all downstream roots remain absent.

### Task 8: Construct and approve the exact external normalization authorization

**Files:**

- External candidate: `normalization_authorization.json`
- External independent review: `normalization_authorization_review.json`
- No repository output yet

- [ ] **Step 1: Re-lock C1 and compute the raw source inventory**

Require branch `codex/g6b-retired-normalization`, exact C1 HEAD/tree, clean state, and no task output root. Record the live Git object format and require the authorization's 40-character SHA-1 object IDs to equal C1 HEAD/tree in the current repository. Byte-hash exactly the 27 paths in `EXPECTED_RETIRED_CONCRETE_SOURCE_INVENTORY`; do not parse raw-bytes-only sources or scientific result fields. Build a sorted path-to-SHA-256 manifest and its canonical SHA-256.

- [ ] **Step 2: Build the external authorization candidate**

The record has exactly the 22 fields in `NORMALIZATION_AUTHORIZATION_REQUIRED_FIELDS` and binds:

- C1 HEAD/tree;
- authority IDs `G4_FREEZE`, `G5_EXECUTION`, `G6_R_REPLAY_R3`;
- the exact 27 source paths and their manifest hash;
- the frozen selector matrix;
- empty `allowed_historical_builder_symbols`;
- raw SHA-256 of C1 `g6b_retired_normalizer.py`;
- exact allowed/forbidden operation and import lists;
- schema ID `ims-deadlock/g6b-retired-normalization-records/v1`;
- the exact governance output root in this plan;
- raw SHA-256 of the final canonical `source_review_bundle`, whose two lane subjects equal C1 HEAD/tree, whose two verdicts are `PASS`, and whose aggregate P0/P1 counts are zero;
- `authorized=true` and `invalidated_by_identity_drift=false`;
- finalized `authorization_sha256`.

- [ ] **Step 3: Independently review the authorization**

The reviewer recomputes raw/self hashes, source HEAD/tree, normalizer byte hash, inventory hash, selector matrix, corrigendum operation/writer lists, the canonical source-review bundle raw/self hashes and both lane references, and the output root. The review must state `PASS AUTHORIZATION CANDIDATE / NORMALIZATION NOT YET AUTHORIZED` with P0/P1/P2 counts.

- [ ] **Step 4: Mandatory execution stop**

Present the exact authorization raw/self SHA-256 and authorization-review raw SHA-256 to the user. Do not commit the candidate, parse retired projection fields, create the governance root, or start Task 9 until the user names and approves those exact hashes.

### Task 9: Execute the approved data-only normalizer exactly once

**Files:**

- Create only: the exact governance root declared above
- External: stdout/stderr/progress/exit records and their hashes

- [ ] **Step 1: Revalidate the execution gate**

Recompute the approved authorization and review hashes. Re-lock C1 HEAD/tree and clean state. Recompute the normalizer code hash and 27-file source manifest hash. Require the final root to be absent. Any mismatch sets `invalidated_by_identity_drift=true` in an external incident record and stops before retired-field parsing.

- [ ] **Step 2: Confirm sequential execution is the correct compute shape**

Record inventory count and total bytes. This workload is deterministic file I/O and canonical hashing over 27 committed files; do not shard it. Ensure no other normalizer process holds the task lock.

- [ ] **Step 3: Run once under the qualified runtime**

```bat
set PYTHONPATH=%CD%\src
set PYTHONDONTWRITEBYTECODE=1
%G6B_PYTHON% -B -m ims_deadlock.g6b_retired_normalizer --authorization %NORMALIZATION_AUTHORIZATION% --repo-root . --output-root %NORMALIZATION_OUTPUT_ROOT%
```

`NORMALIZATION_AUTHORIZATION` is an externally resolved absolute path recorded in the execution lock. `NORMALIZATION_OUTPUT_ROOT` resolves to the one approved repository governance root. Before any retired-field parse, the runner validates the exact approved canonical authorization bytes, requires the root to be absent, and uses `write_normalization_authorization` to create the root and materialize those same bytes as its first record. It then emits monotone progress for 27 source records and fingerprint-record counts. Use observed progress to estimate remaining time. No automatic retry is allowed.

The manifest and authority-lock records serialize privacy-safe logical repository identity `zjqc/IMS_deadlock` for `source_remote`/`origin_remote`; they never serialize an SSH alias, absolute contributor path, credential, or private network identifier.

- [ ] **Step 4: Reconcile any interruption before deciding on retry**

If SSH disconnects, inspect the original process identity, task lock, output root, manifest presence, and captured exit record. Never launch a duplicate process while terminal state is unknown. A failure after any record write preserves external logs and the incomplete root without a valid manifest; it does not claim completion.

- [ ] **Step 5: Mark completeness only with the final manifest**

The runner validates every already-written record and then writes `normalization_manifest.json` as the last finalized file. The root is complete only if an independent validator accepts that manifest and every referenced byte. Terminal success means only `RETIRED_AUTHORITY_NORMALIZATION_COMPLETE`; it does not mean actual-overlap PASS.

### Task 10: Artifact-only verification, normalization review, and mandatory stop before overlap

**Files:**

- Create: `docs/verification/G6_B_RETIRED_AUTHORITY_NORMALIZATION_REVIEW.md`
- Modify: `PROJECT_HANDOFF.md`
- Modify: `docs/ROADMAP.md`
- Verify: the exact governance root

- [ ] **Step 1: Run an independent artifact-only verifier**

Verify exact file closure, all raw/self hashes, the three authority locks, all 27 source records, every producer-required fingerprint, unique-lineage counts, status counts, missing/unreconstructable preservation, and manifest cross-references. Scan serialized keys and values for forbidden outcome/result/score/stdout/stderr fields. Require absence of overlap reports, comparison records, target certificates, CTMC/DES outputs, and later roots.

- [ ] **Step 2: Commit artifact-only successor C2**

C1..C2 may contain only files under the exact normalization governance root, including its approved `normalization_authorization.json`. No source, test, plan, handoff, roadmap, overlap, preflight, or quantitative file may change. Run `git diff --check`, commit, and record C2 commit/tree plus artifact-verifier hashes.

- [ ] **Step 3: Obtain three independent R10 reviews**

Lane 1 reviews ontology/estimand and ensures normalization is not called overlap. Lane 2 reviews source-selector/outcome-leakage/nonreuse boundaries. Lane 3 reviews code capability, artifact closure, hashes, lineage, refusals, and absence of downstream roots. P0/P1 blocks publication.

- [ ] **Step 4: Publish the documentation-only successor C3**

Write the normalization review and update handoff/roadmap with exact C1/C2 hashes, counts, negative/refusal evidence, validation results, and review verdicts. C2..C3 must contain only the three documentation paths. Push the feature branch and open a Draft PR stacked on the normalization-plan branch. Do not merge.

- [ ] **Step 5: Mandatory post-normalization stop**

Report `RETIRED_AUTHORITY_NORMALIZATION_COMPLETE / G6-B OPEN-PENDING`. The next possible tranche is a separately bounded input-level actual-overlap audit comparing sealed C3 case inputs with the normalized retired fingerprints. This plan does not authorize that comparison, Barrier A, Barrier B, G6-C/D/E, or the paper gate.

## Completion checklist

This plan is complete only when all applicable statements are true:

- exact plan, capability-corrigendum, and plan-review hashes were approved before implementation;
- exact authorization and authorization-review hashes were approved before retired-field parsing;
- C1 source/tests were independently reviewed and fully verified;
- the sequential normalizer ran once or preserved a typed refusal without favorable deletion;
- C1..C2 is artifact-only and exactly scoped;
- every authority/source/fingerprint/manifest hash and lineage reference reconciles;
- no forbidden outcome field entered a projection or committed normalization record;
- no overlap/preflight/quantitative/confirmation/science root exists;
- three post-run reviews have no P0/P1;
- the branch and Draft PR are published but unmerged;
- handoff and roadmap state `G6-B OPEN/PENDING` and stop before actual overlap.
