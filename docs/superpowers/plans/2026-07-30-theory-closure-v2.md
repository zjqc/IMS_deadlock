# IMS Deadlock Theory Closure V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the next publishable theory loop by repairing local-certificate
semantics, proving and implementing a narrowly exact Petri siphon diagnostic
bridge, and replacing the `BIX0` constructed-state observation with an
explicitly reachable `BIX1-SAT` threshold family.

**Architecture:** Preserve the generic `IMS-RAS^CW` semantics and add two
strictly opt-in subfamilies. `IMS-SIP^1` produces a state-induced
resource-availability Petri diagnostic net only when unit-capacity,
one-hold/one-request assumptions are machine-checkable. `BIX1-SAT` builds an
executable empty-system model with start, service/transport completion,
unload, and drain events, then compares reachable certificates against an
independent theorem oracle. Literature and theorem documents are updated only
after executable counterexamples and enumeration pass.

**Tech Stack:** Python 3.13, frozen dataclasses, deterministic finite-state
enumeration, pytest, Ruff, strict mypy, Markdown proof artifacts, direct SSH
validation on Dell.

---

### Task 1: Repair Local-Core and Calendar Semantics

**Files:**
- Modify: `src/ims_deadlock/certificates.py`
- Modify: `tests/test_certificates.py`
- Modify: `docs/theory/DEFINITIONS.md`
- Modify: `docs/theory/CORE_THEOREMS_AND_PROOFS.md`

- [ ] **Step 1: Write the failing local-core regression**

Add a state containing a closed `j1`/`j2` cycle and an unrelated `j3` with an
enabled progress transition:

```python
def test_local_kernel_survives_unrelated_enabled_progress() -> None:
    local = find_local_blocking_certificate(model, state, (j3_progress,))
    assert local is not None
    assert local.scope == "local"
    assert local.kernel_jobs == frozenset({"j1", "j2"})
```

- [ ] **Step 2: Verify RED**

Run:

```text
python -m pytest tests/test_certificates.py::test_local_kernel_survives_unrelated_enabled_progress -q
```

Expected: `local is None`, proving the global enabled-transition guard is
incorrectly suppressing a local certificate.

- [ ] **Step 3: Remove only the global-progress guard from local detection**

Keep the enabled-transition rejection in `find_deadlock_certificate`, but
remove it from `find_local_blocking_certificate`. The subset enumeration and
closed-holder checks remain unchanged, so unrelated progress cannot enter the
local kernel.

- [ ] **Step 4: Lock calendar terminology**

Document:

```text
event_calendar_empty = no currently scheduled timed completion in the encoded
state; it is a state fact needed by exact global detection.

calendar-empty terminal block = an explanatory terminal classification in
which missing future/external events, rather than a capacity-ready closed core,
cause the stall.
```

State explicitly that the first does not imply the second.

- [ ] **Step 5: Verify GREEN**

Run:

```text
python -m pytest tests/test_certificates.py -q
```

Expected: all certificate tests pass.

---

### Task 2: Implement the Exact `IMS-SIP^1` Wait-Snapshot Petri Bridge

**Files:**
- Create: `src/ims_deadlock/petri.py`
- Create: `tests/test_petri.py`
- Modify: `src/ims_deadlock/certificates.py`
- Modify: `src/ims_deadlock/analysis.py`
- Modify: `tests/test_analysis.py`
- Modify: `docs/theory/PETRI_BRIDGE.md`
- Modify: `docs/theory/CORE_THEOREMS_AND_PROOFS.md`
- Modify: `docs/theory/ASSUMPTION_REGISTER.md`
- Modify: `docs/theory/PROOF_OBLIGATIONS.md`
- Modify: `docs/theory/COUNTEREXAMPLE_LEDGER.md`

- [ ] **Step 1: Write failing C0 duality tests**

Specify the public result before implementation:

```python
result = build_wait_snapshot_bridge(model, state, certificate)
assert result.applicable is True
assert result.exact is True
assert result.siphon_places == ("free:r1", "free:r2")
assert result.empty is True
assert result.minimal is True
assert result.core_resources == ("r1", "r2")
```

Add negative tests for a conjunctive request (`C4/C5`), a capacity-two
resource, an OR alternative, and a synthetic control-only empty siphon. Each
must return a precise non-applicability reason rather than a false bridge.

- [ ] **Step 2: Verify RED**

Run:

```text
python -m pytest tests/test_petri.py -q
```

Expected: import failure because `ims_deadlock.petri` does not yet exist.

- [ ] **Step 3: Implement the diagnostic net**

Use these core types:

```python
@dataclass(frozen=True)
class PetriTransition:
    name: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class WaitSnapshotNet:
    places: tuple[str, ...]
    transitions: tuple[PetriTransition, ...]
    marking: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class SiphonBridgeResult:
    applicable: bool
    exact: bool
    reason: str
    core_jobs: tuple[str, ...]
    core_resources: tuple[str, ...]
    siphon_places: tuple[str, ...]
    empty: bool
    minimal: bool
```

For each qualifying job holding `h(j)` and requesting `q(j)`, create
`t_j: free:q(j) -> free:h(j)`. Mark `free:r` with the residual capacity in the
IMS state. Enumerate all nonempty place subsets deterministically and apply the
ordinary siphon predicate `•S subseteq S•`.

- [ ] **Step 4: Attach only exact bridge evidence**

When `IMS-SIP^1` assumptions pass, populate
`DeadlockCertificate.corresponding_siphon` and set:

```text
bridge_status = exact_ims_sip1_wait_snapshot_duality
```

Otherwise preserve `corresponding_siphon=None` and record:

```text
bridge_status = not_applicable_ims_sip1_assumptions_failed:<reason>
```

The analysis payload must rename the unavailable result from a universal
Petri claim to a structured diagnostic status.

- [ ] **Step 5: Prove the restricted theorem and record the counterexample**

Add theorem `P2c`:

```text
For reachable stable IMS-SIP^1 states, inclusion-minimal local closed blocking
cores are in bijection with inclusion-minimal empty siphons of the
state-induced wait-snapshot net.
```

The proof must show both structural siphon inclusion and inverse recovery. It
must state that this is not the P1 reachability net, not a general S3PR plant
equivalence, and not valid for control/approval places, multi-capacity
aggregation, conjunctions, OR alternatives, soft reservations, or hidden
closure releases.

- [ ] **Step 6: Verify GREEN**

Run:

```text
python -m pytest tests/test_petri.py tests/test_certificates.py tests/test_analysis.py -q
```

Expected: all selected tests pass, with C0 exact and C4/C5 explicitly outside
the bridge.

---

### Task 3: Implement Reachable `BIX1-SAT`

**Files:**
- Modify: `src/ims_deadlock/families.py`
- Modify: `tests/test_families.py`
- Modify: `docs/theory/CORE_THEOREMS_AND_PROOFS.md`
- Modify: `docs/theory/ASSUMPTION_REGISTER.md`
- Modify: `docs/theory/PROOF_OBLIGATIONS.md`
- Modify: `docs/theory/COUNTEREXAMPLE_LEDGER.md`
- Modify: `docs/cases/C5_RECONSTRUCTION.md`
- Modify: `docs/cases/CASE_CHANGE_LEDGER.md`

- [ ] **Step 1: Write failing reachability and threshold tests**

Define:

```python
parameters = BIX1Parameters(c_M=1, c_G=1, c_D=1, c_V=1, n_A=1, n_B=1)
instance = build_bix1_sat(parameters)
observation = observe_bix1_sat(parameters, max_states=512)
assert instance.initial_state.holds == ()
assert observation.truncated is False
assert observation.reachable_closed_kernel is True
assert observation.certificate_resources == ("G", "M")
assert observation.shortest_prefix
```

Add below-threshold cases, a grid comparison, and a persistent-D boundary case
that is classified outside `BIX1-SAT` rather than used to falsify its theorem.

- [ ] **Step 2: Verify RED**

Run:

```text
python -m pytest tests/test_families.py -q
```

Expected: missing `BIX1Parameters`/builder/observer symbols.

- [ ] **Step 3: Build an executable empty-system family**

Use resources `M`, `G`, `D`, and hard-reservation token `V_D`.

For each A job:

```text
idle --start/acquire M--> in_service
in_service --service_complete--> blocked_complete(request G,D,V_D)
blocked_complete --transfer/acquire G,D,V_D; release M--> transferred
transferred --drain/release G,D,V_D--> completed
```

For each B job:

```text
idle --start/acquire G--> in_transport
in_transport --transport_complete--> blocked_unload(request M)
blocked_unload --unload/acquire M; release G--> on_M
on_M --complete/release M--> completed
```

All resource effects must be explicit `TransitionSpec` acquire/release effects.

- [ ] **Step 4: Compare theorem and independent enumeration**

The theorem oracle is:

```python
parameters.predicts_reachable_closed_kernel = (
    parameters.n_A >= parameters.c_M and parameters.n_B >= parameters.c_G
)
```

The observation oracle must independently enumerate the stable LTS, reject a
truncated graph, scan reachable states with the existing certificate builder,
and select the shortest certificate whose minimal resources are exactly
`{"M", "G"}`.

- [ ] **Step 5: State and prove `P3d`**

Prove existential reachability from the empty system in both directions. State
that `c_D,c_V >= 1` disappear only because the chosen saturation witness has no
successful pre-deadlock transfer. Keep `CE-BIXD1` as the boundary showing that
persistent D occupancy or an external drain creates a different family.

- [ ] **Step 6: Verify GREEN**

Run:

```text
python -m pytest tests/test_families.py -q
```

Expected: the deterministic small grid has zero theorem/enumeration mismatches
and no truncated result is counted as evidence.

---

### Task 4: Close Verifiable G1 Sources and Tighten Innovation Claims

**Files:**
- Modify: `docs/literature/LITERATURE_MATRIX.md`
- Modify: `docs/literature/SOURCE_VERIFICATION.md`
- Modify: `docs/literature/ANNOTATED_BIBLIOGRAPHY.md`
- Modify: `docs/literature/MIGRATION_CARDS.md`
- Modify: `docs/literature/CITATION_TRACE_LOG.md`
- Modify: `docs/literature/FAILURE_LEDGER.md`
- Modify: `docs/literature/RESEARCH_POSITIONING.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: Promote L04 only with stable theorem locators**

Record the full-text section “Controllability condition of siphons in an
ordinary Petri net”, Theorem 2, Theorem 3, and Corollary 2. Restrict use to the
ordinary-net facts that persistent marking of every siphon is sufficient for
deadlock freedom and that the unmarked places of an ordinary dead marking form
a siphon.

- [ ] **Step 2: Promote L16 with equation/section locators**

Record Sections 3, 3.1, 3.2, and 4; fundamental matrix
`F=(I-T)^{-1}`; absorption probabilities `G=FC`; mean-time construction; and
the transient time-to-deadlock distribution. Mark these as historical DTMC /
embedded-chain anchors, not as the source of the project's CTMC sensitivity or
Doob theorem.

- [ ] **Step 3: Promote L22 only for its demonstrated scope**

Record the full article's Petri-net definitions, GE FMS blocked-machine/buffer
model, reachable deadlock construction, reachability-based prevention, and
finite-look-ahead online avoidance limitation. Do not label it a siphon
theorem.

- [ ] **Step 4: Keep B05 open if the full theorem text remains unavailable**

Metadata and publisher HTML may support positioning but cannot support a
project theorem. Record the exact access limitation and use the already
full-read B04 source for maximally permissive Petri-supervisor theorem claims.

- [ ] **Step 5: Update the novelty boundary**

State that the publishable novelty is not “Petri + CTMC + supervisor.” It is
the proved interface between a capacity-auditable operational certificate,
its exact `IMS-SIP^1` diagnostic dual, the reachable `BIX1-SAT` threshold, and
the quantitative/control layers, with explicit counterexamples outside each
interface.

---

### Task 5: Integrated Verification, Independent Review, and Remote Delivery

**Files:**
- Modify: `docs/verification/G3_ALGORITHM_AUDIT.md`
- Modify: `docs/ROADMAP.md`
- Modify: `README.md`
- Modify: `REMOTE_PROJECT_OPERATIONS.md` in the local coordination folder if
  the remote workflow or qualified checkpoint changes

- [ ] **Step 1: Run targeted tests**

```text
python -m pytest tests/test_certificates.py tests/test_petri.py tests/test_families.py -q
```

- [ ] **Step 2: Run the complete local quality gate**

```text
python -m pytest -q
ruff check .
ruff format --check .
mypy --strict src tests
```

- [ ] **Step 3: Run theorem-specific deterministic audits**

Record:

```text
local-core unrelated-progress regression: PASS
IMS-SIP^1 exact C0 bridge and boundary refusals: PASS
BIX1-SAT reachable grid: row count, mismatch count, truncation count
```

- [ ] **Step 4: Run specification review, then quality review**

The specification reviewer must verify every theorem qualifier, counterexample,
and gate label. Only after that passes may the quality reviewer inspect code,
tests, deterministic ordering, schemas, and accidental overclaiming.

- [ ] **Step 5: Transfer by manifest and validate on Dell**

Package only tracked project source/document files, exclude caches, downloaded
papers, environments, secrets, and Git metadata, verify SHA-256 on both sides,
expand into `D:\worktree\IMS_deadlock-final-integration`, and run the same full
quality gate with the qualified Python 3.13.9 environment.

- [ ] **Step 6: Commit, push, and fast-forward the primary checkout**

Commit on `codex/g3-theory-integration`, push the verified commit to
`origin/main`, then fast-forward `D:\py_pro\IMS_deadlock` with `--ff-only`.
Require clean status and `0/0` ahead/behind at the worktree, primary checkout,
and GitHub main.

- [ ] **Step 7: Update gates honestly**

`G2` may be strengthened to include `P2c/P3d` only if proofs and enumerations
pass. `G1` remains `PARTIAL` while B05 lacks a full theorem read. `G4` remains
`NOT FROZEN` until the medium C5 model has physical-rate provenance and the
confirmation set is preregistered.
