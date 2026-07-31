# G6-B Discovery Protocol

## Status

Status: `PROTOCOL-FOUNDATION / DISCOVERY-ONLY / EXECUTION-DISABLED`.

This document is the normative human authority for G6-B discovery admission.
It creates no cases, authorizes no enumeration, authorizes no CTMC solve, and
authorizes no DES run. Scientific execution is disabled until an adversarial
protocol review passes and records a later explicit authorization artifact.

Fixed values:

- `study_role = discovery_only`;
- `confirmation_use = prohibited`;
- `scientific_execution_authorized = false`;
- `adversarial_review_status = PENDING`.

## Scientific Boundary

G6-B is a discovery-only protocol foundation. It may define admissibility,
estimand, independence, negative-control, failure-ledger, and stop-rule
requirements for future discovery rows. It must not be cited as confirmation
evidence, must not repair G4/G5 confirmation outputs, and must not satisfy any
future G6-C, G6-D, or G6-E held-out confirmation gate.

Retired G4/G5/G6-R artifacts are historical authorities only. They provide
frozen exclusions, failure mechanisms, scoring boundaries, and replay
provenance. They cannot be renamed into G6-B discovery rows, shifted by
parameter edits, copied as target cases, or used to support a confirmation
claim.

The local `bootstrap_source` snapshot may omit materialized copies of remote
historical evidence. Such omission is not evidence that the remote authority is
absent. Existence validation for `evidence/g5/G5_RESULT_SUMMARY.json` and
`evidence/g5/G5_RAW_HASH_MANIFEST.json` is remote-authority-only; this protocol
records the repository-relative paths but does not copy those files into the
local source.

## Terminal-Class Ontology

`D_local` means the verified first-hit bad set selected by the G6-B estimand.
It is not a plant terminal SCC and must not be inferred from a local-kernel
candidate alone.

The live G6-B ontology is typed. It is not a flat objective-class list.

- `selected_stopping_targets`: bad hit sets are exactly `D_global` and
  `D_local`; the success class is exactly `F`. These define the stopped target
  set `A = D_global union D_local union F`.
- `unselected_plant_terminal_classes`: `R_livelock` and `R_terminal`. These are
  plant classifications and are not selectable bad or success targets.
- `policy_analysis_class`: `P_policy`. It is outside the plant partition and is
  not a selectable target.
- derived, nonselectable sets: `S_reach` is the diagnostic complete stopped-LTS
  support graph basin with at least one support path to `A`; `S_T` is the
  certified finite positive-rate stopped-CTMC domain whose states hit `A` with
  probability one.

Exact and DES rows must use the same selected stopping targets, the same
versioned target, and the same non-null `absorption_domain_hash` before any
future scientific execution can be considered.

## Local Candidate Admission

A local candidate can enter `D_local` only by one of two routes:

- an accepted A2b proof that establishes structural irreversibility under the
  declared finite semantics; or
- a complete-LTS completion-nonreachability audit showing no completion path
  exists from the candidate state.

Any local candidate with a reachable bypass completion, feasible OR-of-AND
branch, release alternative, AGV/reservation boundary, or missing complete-LTS
audit is refused or classified outside `D_local` according to the applicable
negative control. A rejected local candidate does not support a bad-class
claim.

## Independence Rule

G6-B discovery rows require zero overlap with retired G4/G5/G6-R authorities on
exactly these eight canonical dimensions:

1. `case_content_sha256`
2. `state_snapshot_sha256`
3. `route_signature_sha256`
4. `parameter_tuple_sha256`
5. `random_stream_manifest_sha256`
6. `output_root`
7. `sealed_prediction_sha256`
8. `metric_schema_sha256`

Hashes are computed from canonical JSON: UTF-8, sorted keys, minimal
separators, no duplicate keys, and no path-dependent serialization. A discovery
row that shares any of the eight dimensions with a retired G4/G5 authority or a
G6-R historical replay authority is refused. Changing a name while retaining
content, route, parameter, random stream, output root, prediction, or metric
schema identity from a retired authority is still overlap.

This rule does not impose an unconditional zero-overlap requirement among all
admitted G6-B discovery rows for `metric_schema_sha256` or
`sealed_prediction_sha256`. Discovery-internal case identity and provenance
rules must be declared by the row-family protocol that admits those rows.

Future G6 confirmation rows must be independent from retired authorities and
from G6-B discovery case identity/provenance on exactly these seven dimensions:
`case_content_sha256`, `state_snapshot_sha256`, `route_signature_sha256`,
`parameter_tuple_sha256`, `random_stream_manifest_sha256`, `output_root`, and
`sealed_prediction_sha256`. Reuse of `metric_schema_sha256` may be allowed only
when it is explicitly preregistered for same-target comparability and is not
derived from inspected outcomes.

## Orthogonal Scoring Layers

Future G6-B rows must serialize and evaluate these layers independently:

- `theorem_prediction_status`;
- `metric_applicability`;
- `metric_observations`;
- `execution_status`;
- `reproducibility_status`.

No metric failure may change `theorem_prediction_status` unless the frozen
falsifier for that row explicitly references the metric as a theorem falsifier.
Execution refusal, missing output, metric inapplicability, and reproducibility
failure must remain separate from theorem support or falsification unless the
frozen protocol states otherwise before output inspection.

## Mandatory Negative Controls

The following controls are mandatory before any discovery attempt can be
admitted:

- `NC_LOCAL_BYPASS_COMPLETES`: a local candidate with a completion bypass must
  be refused as `D_local_not_admitted`.
- `NC_UNSELECTED_LIVELOCK`: a non-`D/F` closed recurrent class must classify as
  `R_livelock` and must not count as selected bad.
- `NC_CALENDAR_EMPTY_TERMINAL`: a non-resource terminal boundary must classify
  as `R_terminal` and must not count as selected bad.
- `NC_POLICY_ONLY_STALL`: a policy-only stall must classify as `P_policy` and
  must not alter the plant partition.
- `NC_OR_OF_AND_FEASIBLE_BRANCH`: a feasible branch in an OR-of-AND request
  structure must prevent `D_local` admission.
- `NC_AGV_RESERVATION_BOUNDARY`: a change in AGV or reservation semantics must
  create a boundary classification or new versioned target, not silent support.
- `NC_DGLOBAL_ONLY_WITH_DLOCAL`: a global deadlock that contains a local core
  must report `D_global` once and must not double count through `D_local`.

Failure of a negative control has `not_support_if_failed` force: it does not
support the G6-B discovery hypothesis, does not authorize execution, and must
be appended to the failure ledger.

## Acceptance Rules

A future discovery attempt is admissible only if all of the following are true:

- the adversarial protocol review has passed in a later explicit artifact;
- scientific execution has been explicitly authorized in that later artifact;
- all required independence dimensions are present and have zero overlap under
  the applicable comparison scope;
- the ontology, selected bad labels, selected success label, and versioned
  target match the G6-B estimand schema;
- exact and DES use the same target and stopping labels;
- all mandatory negative controls are included before outcome inspection;
- the failure ledger is append-only and current.

## Refusal Rules

Refuse admission when any of the following occurs:

- `confirmation_use` is anything other than `prohibited`;
- `study_role` is anything other than `discovery_only`;
- scientific execution is requested before adversarial review passes;
- `D_local` is defined as a terminal SCC, terminal class, or unverified local
  candidate;
- exact and DES targets differ;
- any independence dimension overlaps under the applicable comparison scope or
  is missing;
- a retired G4/G5/G6-R case is renamed, copied, or parameter-shifted into the
  G6-B set;
- a negative control is absent, reclassified after output inspection, or used
  as support after failure;
- the failure ledger is replaced, summarized destructively, or treated as
  optional.

## Failure And Change Ledger Discipline

Every refused admission, failed negative control, schema incompatibility,
target drift, overlap hit, missing hash, incomplete LTS audit, or execution
attempt must be retained in the append-only failure ledger. Empty ledger
entries mean no discovery attempt has been admitted under this protocol; they
do not mean no failures exist.

Protocol changes require a new versioned schema or a ledger entry that states
the old value, new value, reason, affected artifact hashes, and whether prior
rows remain comparable. No change can retroactively authorize a row that failed
the active protocol at the time of attempted admission.

## Resource, Output, And Stop Rules

This task creates protocol documents only. It must not create discovery cases,
output roots, state snapshots, random streams, predictions, exact outputs, DES
outputs, or scientific summaries.

Stop before execution if:

- adversarial review is still `PENDING`;
- scientific execution is not explicitly authorized by a later gate;
- any required schema file is missing or invalid JSON;
- any independence dimension is missing or overlapping under the applicable
  comparison scope;
- exact/DES labels or targets diverge;
- any negative control is missing or failed;
- the failure ledger is not append-only.

No scientific execution is authorized in this task.

## Certified Absorption-Domain Gate

The stopped target set is `A = D_global union D_local union F`; the remaining
states are `T = V \ A`. `S_reach` is computed only on the complete stopped-LTS
positive-support graph and is diagnostic: a support path to `A` is necessary for
almost-sure absorption, but it is not sufficient.

For the finite complete positive-rate stopped CTMC, find every unselected
closed SCC in the positive-rate graph induced by `T`. Let `B_closed` be the
reverse basin of those closed SCCs and let `S_T = T \ B_closed`. Under these
assumptions, and only under these assumptions, `x in S_T` iff
`P_x(tau_A < infinity) = 1`. The stronger global-domain gate `A_abs` requires
`B_closed = empty` over the claimed nonabsorbing analysis domain. Production G4
integration still refuses partial-domain solves; committor, mean-time,
sensitivity, and Doob-h payloads are restricted to certified `S_T`.

Every accepted future exact/DES pairing must carry certificate version
`ims-deadlock/g6-absorption-domain-certificate/v1`, generator provenance
`derived_from_g6_terminal_stopping_partition_ims_lts_v3`, a v2 foundation
estimand, v3 terminal partition, and the identities `positive_rate_graph_hash`,
`policy_filter_hash`, `absorption_domain_hash`, and `estimand_id`. A missing
rate manifest is distinct from an explicit empty rate manifest. Never invent a
hash value; absent identity remains null. A missing, mismatched, or non-global
certificate fails closed with the appropriate refusal code, including
`non_almost_sure_absorption_domain` when an unselected closed basin is reachable.
