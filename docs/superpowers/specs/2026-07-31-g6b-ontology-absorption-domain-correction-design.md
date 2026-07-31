# G6-B Ontology and Absorption-Domain Correction Design

Status: `APPROVED DIRECTION / WRITTEN SPEC REVIEW REQUIRED / EXECUTION-DISABLED`.

This design corrects a theory-to-schema and theory-to-runtime mismatch found
while designing G6-B case construction. It is a prerequisite correction, not a
case-construction authorization. It creates no discovery case, runs no LTS
enumeration, solves no CTMC, runs no DES, inspects no scientific output, and
does not change the G6-B status from open.

The audited base is commit
`43cfc3539e7ffa385eae3942fe724c4f76c2ad27`. The target branch is still
unmerged, the protocol and row-family bundles are execution-disabled, and both
`case_creation_authorized` and `scientific_execution_authorized` remain false.

## 1. Blocking Finding

The current G6-B schema places these symbols in one flat field named
`objective_classes`:

- `D_global`;
- `D_local`;
- `F`;
- `R_livelock`;
- `R_terminal`;
- `P_policy`;
- `S_T`.

That field conflates distinct mathematical kinds:

- `D_global` is a plant deadlock state predicate and an eligible stopped-process
  bad hit set;
- `D_local` is a verified first-hit bad set, not a plant terminal SCC;
- `F` is the completion stopping class;
- `R_livelock` and `R_terminal` are residual plant terminal SCC classes;
- `P_policy` is a policy-analysis class and is excluded from the plant
  partition unless policy is itself the analysis object;
- `S_T` is a derived probability domain, not an outcome or selectable target
  class.

The human documents partially explain these distinctions, but
`cases/discovery/g6b/estimand_schema.json` erases them, and
`src/ims_deadlock/g6b_protocol.py` validates the flat list by exact equality.
The validator therefore freezes the ambiguity instead of rejecting it.

The runtime has a second mismatch. `TerminalStoppingPartition.to_json_dict()`
writes `selected_reachable_state_ids` as `classes["S_T"]`. The helper that
produces those IDs proves only existential graph reachability to a selected
target. Project theory defines `S_T` as the states that hit the selected
absorbing target with probability one.

Existential reachability and almost-sure absorption are not interchangeable.
Consider a finite positive-rate CTMC with transitions `s0 -> F`, `s0 -> c`,
and a closed self-loop at `c`. State `s0` can reach `F`, but it has positive
probability of entering `c` and never hitting `F`. Thus `s0` belongs to the
existential reachability basin but not to `S_T`.

This does not contaminate existing G6-B science because no G6-B case or
scientific execution exists. Existing full-domain CTMC construction also
refuses when any nonabsorbing state cannot reach selected absorption. The
mismatch is nevertheless a hard blocker for case-construction readiness and
for any claim that the protocol ontology is machine-clean.

## 2. Rejected Repairs

### 2.1 Reinterpret the flat list as a heterogeneous registry

Rejected. Calling `objective_classes` an arbitrary list of named sets removes
the field's scientific meaning and leaves the same false coverage affordance.

### 2.2 Keep `objective_classes` and add a sidecar kind map

Rejected. The misleading flat field remains authoritative and can still be
used as a pseudo-coverage checklist.

### 2.3 Rename only `S_T`

Rejected. This leaves `D_local`, the residual `R_*` classes, and `P_policy`
flattened into one outcome namespace and does not repair the probability-one
semantics.

### 2.4 Treat `selected_reachable_state_ids` as a partial `S_T`

Rejected by the branching-to-closed-class counterexample above. A partial
committor domain must exclude every state that can reach an unselected closed
positive-rate SCC, not merely states that cannot reach the selected target.

## 3. Chosen Architecture

The correction has four coordinated parts:

1. replace the flat protocol ontology with typed groups;
2. separate existential reachability from the almost-sure absorption domain;
3. version and hash the corrected runtime semantics;
4. keep global scientific construction fail-closed while deferring any
   partial-domain solver.

The correction is schema-first and test-locked. No later case manifest may
refer to the old flat ontology or to an uncertified `S_T`.

## 4. Typed G6-B Ontology

`estimand_schema.json` must replace `objective_classes` with explicit roles:

- `selected_stopping_targets`:
  - bad hit sets: exactly `D_global`, `D_local`;
  - success class: exactly `F`;
- `unselected_plant_terminal_classes`:
  - exactly `R_livelock`, `R_terminal`;
- `policy_analysis_class`:
  - label `P_policy`;
  - not a plant-partition member for the G6-B plant estimand;
- `derived_state_sets`:
  - `S_reach`: nonabsorbing states from which a selected target is reachable
    by at least one path in the complete stopped-LTS support graph; this is a
    structural diagnostic, not a probability-one certificate;
  - `S_T`: nonabsorbing states that hit the selected target with probability
    one in the complete finite stopped CTMC.

Only after every support edge has a frozen finite strictly positive rate does
`S_reach` also describe existential reachability in the positive-rate graph.

The existing `D_local` definition and its two alternative admission routes
remain unchanged. `selected_bad_classes` and `selected_success_class` remain
explicit cross-checks for exact/DES target identity.

The G6-B estimand schema is bumped from v1 to v2. Although the branch is
unmerged, v1 has already been reviewed and published on the draft PR; a
version bump makes the correction auditable instead of silently changing the
meaning of a reviewed version.

The v2 validator must reject:

- the legacy `objective_classes` key;
- `S_T` or `S_reach` in any selected target field;
- `R_livelock`, `R_terminal`, or `P_policy` in G6-B selected bad/success
  fields;
- `P_policy` as a plant-partition member;
- a missing or weakened `S_T` definition;
- exact/DES contracts that do not require the same absorption-domain identity.

## 5. Runtime Output Contract

The corrected terminal/stopping payload is version v3.

`classes` contains only the plant terminal/stopping partition symbols:

- `D_global`;
- `D_local`;
- `F`;
- `R_livelock`;
- `R_terminal`.

`P_policy` moves to a separate `policy_analysis_classes` object. It is not
included in the plant partition hash for a plant-only estimand.

Derived sets move to `derived_state_sets`:

- `selected_reachable_state_ids` retains the complete stopped-LTS support-graph
  existential diagnostic and is serialized as `S_reach`, not `S_T`;
- `S_reach.positive_rate_verified` stays false until every support edge has a
  frozen finite strictly positive rate;
- `S_T` is serialized from a new almost-sure absorption-domain computation;
- unselected closed SCCs and their reverse basin are serialized separately;
- a certification record states the finite/completeness/rate/stopping/policy
  assumptions used.

Legacy v2 outputs remain immutable historical evidence. They are not rewritten
or rehashed. New v3 code may read historical v2 material only through explicit
legacy handling; it must not present a v2 `classes["S_T"]` value as a v3
almost-sure certificate.

`VersionedEstimandSpec.plant_policy_class` is renamed
`policy_analysis_class`, and the estimand-spec version is bumped from v1 to
v2. The name change is required because `P_policy` is not part of the plant
partition by default. The CTMC generator-provenance identifier is bumped with
the terminal/stopping contract.

## 6. Exact Almost-Sure Domain

Let `A` be the selected stopped absorbing set:

`A = D_selected union F`.

Build the actual stopped positive-rate graph after the target and policy
filters are frozen. Let `T = V minus A`.

The statewise domain is computed as follows:

1. require a finite, complete, nontruncated stable LTS;
2. require every actual graph edge to have a finite strictly positive frozen
   rate;
3. treat every state in `A` as absorbing, regardless of outgoing plant arcs;
4. compute SCCs of the positive-rate graph induced by `T`;
5. mark an SCC as unselected closed when it has no positive-rate exit to
   another SCC or to `A`;
6. compute the reverse-reachable basin `B_closed` of all unselected closed
   SCCs within `T`;
7. define `S_T = T minus B_closed`.

For a finite nonexplosive CTMC, this construction is equivalent to probability
one of eventually hitting `A`: any path that avoids `A` forever must end in an
unselected closed communicating class, and every state that can reach such a
class has positive probability of nonabsorption.

`S_reach` remains useful as a counterexample diagnostic but is never a
substitute for `S_T`.

## 7. Scientific Gate

The current project supports only a global two-target absorbing CTMC. It does
not gain a partial-domain solver in this correction.

A scientific CTMC derivation must therefore require all of the following:

- complete nontruncated LTS;
- verified LTS provenance;
- frozen positive finite rate manifest covering every plant arc event;
- explicit no-policy filter or a frozen policy-filter hash;
- selected targets exactly matching the versioned estimand;
- `non_almost_sure_absorbing_state_ids = []`;
- certified `S_T` equal to every nonabsorbing state in the claimed global
  domain.

Failure produces a structured refusal before generator construction or solve.
A reachable unselected closed class may be handled only by a new versioned
boundary estimand or a future separately reviewed partial-domain design.
Dropping the closed class and retaining states that can also reach it is
prohibited.

`derive_absorbing_ctmc` must request the strict certificate directly instead
of calling permissive partitioning and then relying on a weaker existential
check. The implementation boundary is a named pure function,
`certify_absorption_domain`, that consumes the structural partition, complete
stable LTS, frozen event-rate manifest, selected stopped targets, and frozen
policy-filter declaration and returns a versioned `AbsorptionDomainCertificate`.
`derive_absorbing_ctmc` must call it with `require_global=True` before generator
construction.

## 8. Hash and Identity Contract

The plant `partition_hash` remains structural and independent of the selected
bad union. In v3 it excludes `P_policy`, `S_reach`, and `S_T`.

A new `positive_rate_graph_hash` fixes the actual positive-rate stopped graph.
A new `policy_filter_hash` fixes either the applied policy filter or the
canonical no-policy declaration.

A new `absorption_domain_hash` binds:

- state-space identity;
- v3 plant partition identity;
- positive-rate graph identity;
- policy-filter identity;
- selected absorbing target identity;
- unselected closed SCCs;
- their reverse basin;
- `S_T`;
- the absorption-domain algorithm version.

`estimand_id` incorporates `absorption_domain_hash` in addition to the existing
state-space, partition, rate-manifest, exact-stopping, and DES-stopping hashes.
The G6-B v2 schema requires all three new hashes for any future scientific row.
Exact and DES companions must share the same target and absorption-domain hash.

Classification-only calls without a frozen rate manifest may return
structural classes and support-graph `S_reach`, but they must serialize
`derived_state_sets.S_reach.graph_semantics = "complete_stopped_lts_support"`
and `derived_state_sets.S_reach.positive_rate_verified = false`. The
uncertified `S_T` representation is exact:
`derived_state_sets.S_T.state_ids = null`,
`derived_state_sets.S_T.certification_status = "not_certified"`, and
`derived_state_sets.S_T.reason_codes` is a nonempty sorted list. The three new
hashes are null. An empty list is never used to mean uncertified. For a
certified zero-state domain, `state_ids = []`, status is
`certified_finite_positive_rate_stopped_ctmc`, `reason_codes = []`, and
`derived_state_sets.S_reach.positive_rate_verified = true`.

## 9. Counterexample and Proof Ledger

The existing `CE-NB1` warning that existential nonblocking does not imply
almost-sure completion becomes a machine regression:

- `s0` has positive-rate branches to `F` and to a closed state `c`;
- `S_reach` includes `s0`;
- `S_T` excludes `s0` and `c`;
- the global absorption gate refuses;
- no committor or mean absorption time is produced.

The theory documents must distinguish:

- graph-reachable basin `S_reach`;
- almost-sure absorption domain `S_T`;
- the stronger global assumption `A_abs`, under which `S_T` equals all
  nonabsorbing analysis states.

## 10. Historical v2 and R3 Boundary

Frozen v2 outputs and R3 replay evidence remain historical and immutable.
Their hashes, locks, results, and published estimand IDs are never recomputed
under v3.

The historical replay lock intentionally hashes behavior files including
`historical_replay.py`, `g4_protocol.py`, `g4_instances.py`, and
`terminal_classes.py`. Changing v3 behavior therefore makes the current branch
ineligible to masquerade as the immutable R3 runtime. This is expected. The
implementation must not refresh the R3 lock, edit its required runtime hashes,
or rerun R3 merely to make the current tree pass.

Historical R3 execution remains pinned to its recorded immutable code ref.
Current-code compatibility is limited to reading already captured payloads:

- a v2 terminal payload is accepted only as legacy historical input;
- `classes["D_local"]` may be read for the existing historical mechanism check;
- v2 `classes["S_T"]` is ignored as an almost-sure certificate;
- a captured `estimand_id` is treated as an opaque historical identifier and
  is never recalculated with v3 hashes;
- unknown terminal-classification versions fail closed;
- v2 input can never authorize a current v3 solve, case, or scientific claim.

`tests/test_historical_replay.py` must lock these rules with v2 fixtures and a
v3 fixture. A version-aware pure reader may be added to
`historical_replay.py`, but the immutable R3 lock remains unchanged and is
validated only in its recorded code worktree.

## 11. Row-Family Alignment

The nested row-family bundle remains schema-only and execution-disabled, but
its ontology contract must stop referring only to `D_local`. The v1 draft
bundle is revised before merge to require:

- `foundation_estimand_schema_version = ims-deadlock/g6b-estimand-schema/v2`;
- `terminal_classification_version = ims-deadlock/g6-terminal-stopping-partition/v3`;
- the typed target, residual-terminal, policy, and derived-domain groups;
- `S_reach` as diagnostic-only and never a selected label;
- a certified nonnull `absorption_domain_hash` before any future scientific
  row can pass;
- the same `absorption_domain_hash` for exact/DES companions;
- `P_policy` excluded from plant-partition support;
- unchanged false case/science authorization.

`g6b_row_family_protocol.py` currently exact-matches the canonical matrix.
Its expected payload and mutation tests must be updated together. Tests must
reject a stale foundation version, a missing absorption-domain requirement,
or a companion rule that permits domain-hash drift.

## 12. Change Surface

Implementation is expected to touch only the following surfaces:

- `cases/discovery/g6b/estimand_schema.json`;
- `cases/discovery/g6b/row_families/structural_discovery_v1/row_family_matrix.json`;
- `src/ims_deadlock/g6b_protocol.py`;
- `src/ims_deadlock/terminal_classes.py`;
- `src/ims_deadlock/g4_instances.py`;
- `src/ims_deadlock/g4_protocol.py`;
- `src/ims_deadlock/historical_replay.py` only for version-aware reading of
  already captured payloads, never for an R3 lock refresh;
- `src/ims_deadlock/g6b_row_family_protocol.py`;
- `tests/test_g6b_protocol.py`;
- `tests/test_terminal_classes.py`;
- `tests/test_g4_protocol.py`;
- `tests/test_historical_replay.py`;
- `tests/test_g6b_row_family_protocol.py`;
- G6-B protocol, theory, symbol, assumption, counterexample, review, roadmap,
  handoff, and change-ledger documents that currently encode the old meaning;
- any other file only when a failing selector or type check proves it is an
  actual consumer of the versioned contract.

No case file, prediction, output root, random stream, historical result, G4/G5
evidence, or G6-R evidence may be rewritten.

## 13. Required Tests

The implementation plan must lock at least these failures before production
edits:

1. legacy `objective_classes` is rejected by G6-B schema v2;
2. `S_T` cannot be selected as bad or success;
3. `P_policy` cannot enter the plant partition hash;
4. v3 serialization places plant classes, policy class, and derived sets in
   separate namespaces;
5. the branching closed-class counterexample separates `S_reach` from `S_T`;
6. a full finite positive-rate domain certifies `S_T` and passes strict
   derivation;
7. missing rates leave support-graph `S_reach` diagnostic-only with
   `positive_rate_verified = false` and fail scientific certification closed;
   a zero rate, truncated LTS, unavailable branch, target drift, policy-filter
   drift, or unselected closed SCC also fails scientific certification closed;
8. `partition_hash` is independent of selected bad union while
   `absorption_domain_hash` and `estimand_id` drift when the selected target or
   positive-rate support changes;
9. uncertified, certified-empty, and certified-nonempty `S_T` payloads are
   unambiguous and strictly validated;
10. v2 historical payloads remain readable only as historical input; v2
    `classes["S_T"]` is never accepted as v3 proof, and captured v2 estimand IDs
    are never recomputed;
11. the immutable R3 runtime-hash lock is not edited and current v3 code is not
    presented as a successful R3 replay runtime;
12. the row-family validator rejects stale ontology versions and exact/DES
    absorption-domain drift;
13. the G6-B and row-family bundles remain execution-disabled and authorize no
    case creation.

## 14. Verification and Stop Conditions

Implementation is complete only after:

- targeted ontology, terminal-class, G4 integration, historical-reader, and
  row-family tests pass;
- the full test suite passes on the exact corrected commit;
- Ruff check and format check pass;
- strict mypy passes for source and source/tests;
- JSON file-set and duplicate-key validators pass;
- `git diff --check` passes;
- an independent theory review validates the probability-one proof boundary;
- an independent code review finds no unhandled legacy/version path;
- the branch is re-locked clean and pushed without rewriting history;
- the draft PR records the correction and does not claim G6-B `PASS`.

After this correction, work returns to the case-construction coverage design.
G6-B remains open, adversarial review remains pending, case creation remains
unauthorized, science remains unauthorized, and G6-C/D/E remain not started.
