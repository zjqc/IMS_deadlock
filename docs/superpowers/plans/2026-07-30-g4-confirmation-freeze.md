# IMS Deadlock G4 Confirmation Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or
> `superpowers:executing-plans` to implement this plan task-by-task. Every code
> task follows RED -> GREEN -> REFACTOR, and no held-out confirmation protocol
> may be executed before the final freeze seal is committed.

**Goal:** Move G4 from `NOT FROZEN` to an auditable preregistration freeze
without inspecting any held-out outcome, while implementing and development-
testing the exact finite-state comparison primitives required by the frozen
protocol.

**Architecture:** Keep discovery fixtures under `cases/*.json` and place all
held-out inputs under `cases/confirmation/g4/`. Add a separate confirmation
loader that validates provenance and rejects result-bearing fields. Add
strictly labelled comparison primitives: an L31 CRP evidence-profile
interoperability audit, an L32/L33 fixed-recorder-target augmented-LTS oracle,
an L30 supplied-sufficient-inequality checker, and a B05-inspired candidate
monitor-cover backend. None is labelled as a reproduction of the source
algorithm. Freeze integrity is checked by the internal module
`python -m ims_deadlock.g4_freeze`; the stable five-command public CLI remains
unchanged.

**Freeze topology:** Use three non-circular commits on the authoritative Dell
branch. Commit A locks implementation and development tests. Commit B locks
held-out case inputs, predictions, metrics, baselines, runtime, random streams,
theory/script manifests, and records Commit A. Commit C adds
`FREEZE_ENTRY.json`, which records Commit B and hashes every prerequisite.
Only Commit C may change G4 status to `FROZEN`.

**Tech Stack:** Python 3.13, frozen dataclasses, deterministic finite-state
BFS, exhaustive subset search for small candidate covers, canonical JSON,
SHA-256, pytest, Ruff, strict mypy, Markdown ledgers, and direct Dell
verification.

---

### Task 1: Separate Confirmation Inputs from Discovery

**Files:**
- Create: `src/ims_deadlock/confirmation.py`
- Create: `tests/test_confirmation.py`
- Modify: `src/ims_deadlock/cases.py`
- Modify: `tests/test_cases.py`

- [ ] **Step 1: Write failing discovery-isolation tests**

Assert that nested `cases/confirmation/**` files never appear in
`list_case_ids()` or `case_manifest()`. Add an explicit
`list_confirmation_case_ids("g4", root=...)` test.

- [ ] **Step 2: Verify RED**

Run:

```text
python -m pytest tests/test_cases.py tests/test_confirmation.py -q
```

Expected: confirmation symbols are missing.

- [ ] **Step 3: Implement a data-only confirmation loader**

Define:

```python
CONFIRMATION_SCHEMA_VERSION = "ims-deadlock/confirmation-case/v1"


@dataclass(frozen=True)
class ConfirmationCase:
    case_id: str
    family: str
    held_out: bool
    status: str
    protocol: str
    contamination: Mapping[str, object]
    input_payload: Mapping[str, object]
    expected_outputs_schema: Mapping[str, object]
```

The loader must:

- require uppercase unique IDs and a declared G4 family;
- require `held_out=true` and
  `contamination.derived_from_discovery_case=false`;
- require the complete discovery-exclusion list;
- recursively reject result-bearing keys such as `observed_result`,
  `confirmation_result`, `match`, `pass`, `fail`, `estimate`, and
  `measured`;
- parse only preregistration structure and never call an analyzer, simulator,
  supervisor, or confirmation runner.

- [ ] **Step 4: Add provenance and leakage negative tests**

Reject a discovery-derived fixture, an omitted exclusion, a nested observed
field, a duplicate JSON key, an unknown protocol, and a discovery ID reused as
a confirmation ID.

- [ ] **Step 5: Verify GREEN**

Run:

```text
python -m pytest tests/test_cases.py tests/test_confirmation.py -q
```

Expected: all selected tests pass.

---

### Task 2: Implement Exact Development-Only Comparison Primitives

**Files:**
- Create: `src/ims_deadlock/g4_comparators.py`
- Create: `tests/test_g4_comparators.py`
- Modify: `docs/literature/MIGRATION_CARDS.md`
- Modify: `docs/theory/PROOF_OBLIGATIONS.md`
- Modify: `docs/theory/ASSUMPTION_REGISTER.md`

- [ ] **Step 1: Write failing fixed-recorder-target tests**

On a development-only `FiniteLTS`, preregister a target state and event-count
vector. Assert that:

- ordinary target reachability and fixed-count target reachability are
  distinct fields;
- augmented BFS returns a deterministic shortest witness;
- counts greater than the fixed target are safely pruned;
- the target and count vector are immutable inputs, never inferred from
  reachable output.

- [ ] **Step 2: Implement the recorder oracle**

Define:

```python
def fixed_recorder_target_reachability(
    lts: FiniteLTS,
    *,
    target_state: str,
    recorder_events: tuple[str, ...],
    fixed_counts: Mapping[str, int],
) -> RecorderTargetResult:
```

Run complete BFS on `(state, bounded_count_vector)`. This is an exact
finite-LTS oracle for output-only event counters, not an implementation or
complexity reproduction of L32/L33.

- [ ] **Step 3: Write and implement the L31 evidence-profile audit**

Define a structured `CRPEvidenceProfile` requiring:

- declared S4PR applicability;
- a content hash for the external S4PR embedding;
- a frozen CRP/resource-limit-pair set;
- a frozen translated IMS target state;
- an external legal-prefix claim;
- the independent finite-LTS reachability classification.

The audit may classify `agreement`, `unreachable_candidate`,
`not_applicable`, `incomplete_evidence`, or `evidence_disagreement`. The last
class preserves a negative result when a frozen external legal-prefix claim
contradicts complete finite-LTS BFS; it is not a CRP theorem result. The audit
must never generate CRPs or claim to reproduce L31/SBA.

- [ ] **Step 4: Write and implement the L30 supplied-inequality checker**

Define a finite set of integer linear `>=` constraints and evaluate a supplied
capacity vector only when `finite_capacity_s3pr_ens3pr=true` and the inequality
provenance is `sms_derived_external`. It must refuse missing applicability
evidence and must never claim SMS enumeration, Algorithm 1, minimum
`M0(P_R)`, or an IMS iff threshold.

- [ ] **Step 5: Write and implement the B05-inspired cover backend**

Given explicit legal states, first-met bad states, and explicit candidate
monitor cover sets, exhaustively select the lexicographically deterministic
minimum-cardinality legal-preserving cover. Return infeasible when the
candidates cannot cover all bad states without excluding legal states. Label
the result `adapted_candidate_monitor_cover`; do not claim P-semiflow
synthesis, MCPP reproduction, minimal control places in the source net, or
source-theorem maximal permissiveness.

- [ ] **Step 6: Lock the adaptation proofs and refusals**

Document the direct/adapted/nontransferable class for each comparator and the
exact implementation invariant. Add explicit proof obligations for:

- augmented-BFS recorder equivalence;
- reachability being independent of a supplied CRP claim;
- inequality evaluation being only a sufficient-condition check;
- exhaustive optimality only over the frozen candidate-monitor set.

- [ ] **Step 7: Verify GREEN**

Run:

```text
python -m pytest tests/test_g4_comparators.py -q
python -m ruff check src/ims_deadlock/g4_comparators.py tests/test_g4_comparators.py
python -m mypy src/ims_deadlock/g4_comparators.py
```

Expected: all selected checks pass.

---

### Task 3: Implement a No-Result Freeze Checker

**Files:**
- Create: `src/ims_deadlock/g4_freeze.py`
- Create: `tests/test_g4_freeze.py`
- Modify: `pyproject.toml` only if module packaging requires it; do not add a
  sixth public `ims-deadlock` command.

- [ ] **Step 1: Write failing canonical-hash and missing-artifact tests**

Assert key-order-independent canonical JSON SHA-256, rejection of duplicate
keys, and `NOT_FROZEN` when any required file or hash is missing.

- [ ] **Step 2: Implement canonical hashing and schema validation**

Use UTF-8 JSON with sorted keys and compact separators. Hash the canonical
semantic payload for manifests and exact bytes for source/model files where
the manifest declares `hash_mode="file_bytes"`.

- [ ] **Step 3: Implement freeze-bundle validation**

Require:

- all nine G4 case families:
  the six literature-informed rows plus `G4-IMS-PARAMETER-GRID`,
  `G4-MEDIUM-ISLAND-REBUILD`, and `G4-ADVERSARIAL-BOUNDARY`;
- a prediction for every included case;
- per-case applicability decisions for L30, L31, L32/L33, L34/L35, B05, and
  the existing project baselines;
- locked metric applicability and freeze-time reasons for every inapplicable
  metric;
- runtime, commands, theory files, experiment entrypoints, exclusions, and
  random-stream policies;
- `confirmation_results_inspected=false`;
- no result/output directory beneath the G4 bundle.

- [ ] **Step 4: Prove the checker is no-result**

Tests monkeypatch all analysis/simulation/control entrypoints to raise and
assert that `check_g4_freeze()` still succeeds on a complete temporary bundle.
The internal module may read, validate, and hash files only.

- [ ] **Step 5: Add an internal module entrypoint**

Support:

```text
python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check
```

It emits versioned JSON with `FROZEN` or `NOT_FROZEN`, validation errors, and
hash comparisons. It must not modify files or execute a confirmation case.

- [ ] **Step 6: Verify GREEN**

Run:

```text
python -m pytest tests/test_g4_freeze.py tests/test_confirmation.py -q
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
```

Expected: all selected checks pass.

---

### Task 4: Build and Seal the Held-Out G4 Bundle

**Files:**
- Create: `cases/confirmation/g4/cases/*.json`
- Create: `cases/confirmation/g4/case_manifest.json`
- Create: `cases/confirmation/g4/predictions.json`
- Create: `cases/confirmation/g4/baseline_applicability.json`
- Create: `cases/confirmation/g4/metrics_schema.json`
- Create: `cases/confirmation/g4/runtime_lock.json`
- Create: `cases/confirmation/g4/random_stream_manifest.json`
- Create: `cases/confirmation/g4/experiment_scripts_manifest.json`
- Create: `cases/confirmation/g4/theory_manifest.json`
- Create: `cases/confirmation/g4/exclusions.json`
- Create: `docs/cases/G4_FREEZE_LEDGER.md`

- [ ] **Step 1: Create nine independent preregistration inputs**

Freeze:

1. S4PR/CRP agreement with a hashed explicit embedding;
2. an unreachable structural/algebraic candidate;
3. an outside-S4PR BAS/AGV/AND refusal;
4. a fixed recorder-target/count obligation;
5. an L30 supplied sufficient-inequality comparison;
6. a small full finite-LTS plus B05-inspired candidate-cover comparison;
7. a new parameterized small IMS grid not used for P3d/P3e derivation;
8. an independently specified medium manufacturing-island rebuild;
9. an adversarial OR-of-AND/multi-capacity/reservation boundary.

Do not copy C0-C5/BIX1/BIX2 parameters and do not include observed outcomes.

- [ ] **Step 2: Freeze predictions and negative-result semantics**

Every row records only pre-result theorem scope, expected
agreement/refusal/boundary class, required evidence, and a falsifier. No
observed state count, mismatch, probability, cost, witness, or pass/fail field
is permitted.

- [ ] **Step 3: Freeze all manifests**

Record exact:

- parameter ranges and state bounds;
- metric definitions, denominators, and applicability rules;
- baseline eligibility and refusal reasons;
- random-stream seeds/derivation or exact-only `N/A` reasons;
- Dell Python path/version/package versions and exact commands;
- theory and experiment-script file hashes;
- discovery exclusions and contamination controls.

- [ ] **Step 4: Validate schema only**

Run only:

```text
python -m pytest tests/test_confirmation.py tests/test_g4_freeze.py -q
python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check
```

Expected before the seal: schema passes but status is `NOT_FROZEN` solely
because `FREEZE_ENTRY.json` is absent. Do not invoke `validate`, `prove`,
`quantify`, `simulate`, `verify-case`, or any G4 experiment entrypoint on these
files.

- [ ] **Step 5: Commit A and Commit B**

Commit A contains implementation, development tests, plan, and theory
boundaries. Commit B contains the held-out bundle and records Commit A as
`implementation_commit`. Push both commits to the isolated G4 branch.

---

### Task 5: Add the Freeze Seal and Pass G4

**Files:**
- Create: `cases/confirmation/g4/FREEZE_ENTRY.json`
- Modify: `docs/cases/CONFIRMATION_PREREGISTRATION.md`
- Modify: `docs/cases/G4_CASE_PREREGISTRATION.md`
- Modify: `docs/cases/CASE_CATALOG.md`
- Modify: `docs/cases/G4_FREEZE_LEDGER.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: Build the non-circular freeze entry**

Record:

- Commit A as `implementation_commit`;
- Commit B as `preregistration_commit`;
- every required manifest/file hash;
- all included/excluded cases;
- locked metrics/baselines;
- date/owner;
- `confirmation_results_inspected=false`;
- a prohibition on changing cases, predictions, metrics, or baseline
  applicability without a successor freeze.

- [ ] **Step 2: Run the no-result checker**

Run:

```text
python -m ims_deadlock.g4_freeze --root cases/confirmation/g4 check
```

Expected: `status="FROZEN"` with zero validation errors. This is a preregistered
artifact-integrity result, not a scientific confirmation result.

- [ ] **Step 3: Update gate documents**

Mark G4 `PASS (preregistration frozen; confirmation unexecuted)`. State
explicitly that no held-out outcome has been inspected and G5 execution has
not started.

- [ ] **Step 4: Run full quality verification**

On the authoritative Dell worktree:

```text
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m mypy src
git diff --check
```

Expected: all tests and static checks pass.

- [ ] **Step 5: Independent reviews**

Run a specification review against this plan, then a separate code-quality and
scientific-claim review. Any critical/high issue returns to the relevant TDD
task before sealing.

- [ ] **Step 6: Commit C, push, and synchronize**

Commit the freeze seal and status documents, push the G4 branch, merge or
fast-forward only after all checks pass, push `origin/main`, and synchronize
`D:\py_pro\IMS_deadlock` to the verified main commit without overwriting
unrelated changes.

- [ ] **Step 7: Re-lock final evidence**

Report exact path, branch, HEAD, upstream/ahead-behind, clean state, runtime,
test/lint/typecheck results, freeze ID, Commit A/B/C identities, and the
explicit statement:

```text
G4 is frozen; held-out confirmation results remain unexecuted and uninspected.
```
