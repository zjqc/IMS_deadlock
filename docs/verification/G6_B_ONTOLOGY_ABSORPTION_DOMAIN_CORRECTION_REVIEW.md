# G6-B Ontology And Absorption-Domain Correction Review

Verification date: 2026-07-31
Record commit date: 2026-08-01

This document records the Task 8 governance, theory, and code correction review
for the G6-B ontology and absorption-domain repair. It is not a scientific
result, not a case-construction authorization, not a G6-B PASS, and not a
G6-C/D/E opening condition.

The verification target below is the code/documentation state that was reviewed
before this record was committed. The later commit that first created this file
is self-identifying through Git history:
`git log --diff-filter=A --format=%H -- docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md`.
The latest commit that changes the current file content is:
`git log -1 --format=%H -- docs/verification/G6_B_ONTOLOGY_ABSORPTION_DOMAIN_CORRECTION_REVIEW.md`.

## Verification Target

```text
target path = D:\worktree\IMS_deadlock-g6b-discovery
branch = codex/g6b-discovery-estimand-lock
verification HEAD = 94fbf6517eb0abaf3c09a4c7238129547e76b8f5
upstream = origin/codex/g6b-discovery-estimand-lock
upstream relation at review lock = 0 behind / 20 ahead
dirty state at review lock = clean
git dir = D:/py_pro/IMS_deadlock/.git/worktrees/IMS_deadlock-g6b-discovery
git common dir = D:/py_pro/IMS_deadlock/.git
Python = D:\worktree\IMS_deadlock-final-integration\.venv\Scripts\python.exe
Python version = 3.13.9
PYTHONPATH = D:\worktree\IMS_deadlock-g6b-discovery\src
PYTHONDONTWRITEBYTECODE = 1
pytest = -p no:cacheprovider
Ruff = --no-cache
mypy = --no-incremental
```

Approved design:
`docs/superpowers/specs/2026-07-31-g6b-ontology-absorption-domain-correction-design.md`
at commit `d0a8dca2bd735d39f16d060c545d13ce85029f60`.

Implementation plan:
`docs/superpowers/plans/2026-07-31-g6b-ontology-absorption-domain-correction.md`.

## Review Scope

This review covers only the ontology and absorption-domain correction already
present at verification HEAD `94fbf6517eb0abaf3c09a4c7238129547e76b8f5`.

It verifies that the correction:

- separates selected stopped targets, unselected plant terminal classes,
  policy-analysis labels, and derived state sets;
- separates existential support reachability `S_reach` from probability-one
  stopped-domain membership `S_T`;
- binds the corrected finite positive-rate stopped-CTMC absorption domain with
  versioned hashes;
- preserves the historical failed/boundary definition and `CE-NB1`;
- keeps G6-B `OPEN/PENDING`, with case creation and science disabled.

## Root Cause

The defect was a flat ontology/category mix. The earlier reviewed G6-B
foundation placed unlike symbols in one authority surface:

- `D_global`, `D_local`, and `F` are selected stopped-target labels;
- `R_livelock` and `R_terminal` are unselected plant terminal classes;
- `P_policy` is a policy-analysis label, not a plant partition member by
  default;
- `S_reach` and `S_T` are derived sets, not selectable outcomes.

The second defect was treating existential reachability to a selected stopped
target as if it proved probability-one stopping. Closure must be computed on
the full stopped graph, including exits to `A_stop`, and must retain unselected
closed SCCs and their reverse basin. The historical failed definition is
preserved as boundary evidence rather than silently rewritten.

## Corrected Notation And Modality

The corrected notation is:

- `X_stop`: the stopped finite state universe after the complete stable LTS and
  stopping transformation are fixed;
- `D_sel`: the selected bad stopped set, `D_global union D_local`;
- `A_stop`: selected absorbing targets, `D_sel union F`;
- `T`: nonabsorbing analysis states, `X_stop \ A_stop`;
- `C_closed`: unselected closed SCC with membership `C_closed subset T`;
  closedness is checked against every outgoing positive-rate edge in the full
  stopped graph, including exits to `A_stop`;
- `B_closed`: reverse-reachable basin of `C_closed` inside `T`;
- `S_T`: `T \ B_closed`, the states that hit `A_stop` with probability one
  under the finite complete finite-positive-rate stopped CTMC;
- `A_abs`: the stronger global assumption under which all nonabsorbing
  analysis states are in `S_T`.

The accepted modality is finite, complete, nontruncated, finite-positive-rate
stopped CTMC analysis. Current production supports only the global `A_abs`
certificate-or-refusal protocol. It does not support a partial-domain
quantitative solve or payload; any such payload requires a separate versioned
and reviewed design. Dropping only `C_closed` while retaining
`B_closed \ C_closed` is also prohibited.

## Versioned Contract

| Surface | Version |
| --- | --- |
| Terminal/stopping partition | `ims-deadlock/g6-terminal-stopping-partition/v3` |
| Versioned estimand | `ims-deadlock/g6-versioned-estimand/v2` |
| Absorption-domain certificate | `ims-deadlock/g6-absorption-domain-certificate/v1` |
| Absorption-domain algorithm | `finite-positive-rate-stopped-ctmc-scc-domain/v1` |
| CTMC generator provenance | `derived_from_g6_terminal_stopping_partition_ims_lts_v3` |
| G6-B foundation estimand schema | `ims-deadlock/g6b-estimand-schema/v2` |

## Identity Boundaries

The row-family identity hierarchy has exactly three levels:

| Level | Meaning |
| --- | --- |
| `family_id` | One structural discovery family, not a case. |
| `case_unit_id` | One planned plant/model input unit; this is the discovery-case identity unit. |
| `method_observation_id` | One method attached to a case unit; paired exact/DES observations are not independent cases. |

The row-family canonical dimensions remain exact-eight:
`case_content_sha256`, `state_snapshot_sha256`, `route_signature_sha256`,
`parameter_tuple_sha256`, `random_stream_manifest_sha256`, `output_root`,
`sealed_prediction_sha256`, and `metric_schema_sha256`.

Their identity meanings are bounded:

- `case_content_sha256`: canonical case-definition content identity;
- `state_snapshot_sha256`: canonical state-space or state-snapshot identity;
- `route_signature_sha256`: route and structural-flow signature identity;
- `parameter_tuple_sha256`: frozen parameter tuple identity;
- `random_stream_manifest_sha256`: random-stream provenance identity;
- `output_root`: generated-output provenance, not an independent case identity;
- `sealed_prediction_sha256`: pre-result sealed prediction identity;
- `metric_schema_sha256`: metric comparability identity, not case identity reuse
  permission.

## Absorption-Domain Hash Boundary

`absorption_domain_hash` binds:

- absorption-domain algorithm version;
- `state_space_hash`;
- `partition_hash`;
- `positive_rate_graph_hash`;
- `policy_filter_hash`;
- selected absorbing target IDs;
- unselected closed SCCs;
- `B_closed`;
- `S_T`.

It explicitly excludes the full rate manifest. `rate_manifest_hash` binds the
full declared rate manifest separately, and `estimand_id` binds both the rate
manifest identity and the certified absorption-domain identity.

Missing and explicit empty are distinct. An absent rate manifest leaves
`rate_manifest_hash`, `positive_rate_graph_hash`, `policy_filter_hash`,
`absorption_domain_hash`, and `estimand_id` null. A frozen explicit empty
manifest can receive a rate-manifest identity only under the separately
validated edgeless-domain conditions; an empty list is never used to mean
uncertified.

## CE-NB1 Boundary Case

`CE-NB1` remains the unit-rate counterexample:

```text
s0 -> F
s0 -> c
c -> c
```

With unit rates, `P(hit F | s0) = 1/2`. Therefore `s0` has `S_reach = yes` but
`S_T = no`. The closed basin is `B_closed = {s0, c}`. Under the current global
production protocol, this refuses with `non_almost_sure_absorption_domain`
before CTMC generator construction or solve. This is a protocol-domain refusal,
not a mathematical claim that partial-domain probabilities do not exist. No
committor, mean absorption time, case result, or science payload is produced
from this global claim.

## Main Verification Evidence

| Check | Result |
| --- | --- |
| Focused verification | `1157 passed in 132.13s` |
| Full pytest | `1410 passed in 167.44s` |
| Ruff check | passed |
| Ruff format | `43 files already formatted` |
| Strict mypy `src` | passed on 23 source files |
| Strict mypy `src tests` | passed on 43 source files |
| `git diff --check` | passed |
| Full-range `git diff --check` | passed |
| Validators | exact `5/8`, valid, no errors, science false, case false, `PENDING` |
| Changed-path review | 24 changed paths, 1 added plan, outside allowed `[]`, immutable diff `[]`, forbidden additions `[]` |

The approved strict mypy command shape is the standard no-incremental form with
no Windows `MYPY_CACHE_DIR=NUL` override:

```text
python -m mypy --no-incremental --strict src
python -m mypy --no-incremental --strict --explicit-package-bases src tests
```

## Independent Verdicts

| Review | Verdict |
| --- | --- |
| Theory review | `PASS`; 45 targeted checks reproduced the finite positive-rate stopped-CTMC SCC/reverse-basin boundary. |
| Code review | `PASS`; no actionable blockers; focused suite `1157 passed in 116.08s`. |
| Verifier | `PASS`; focused suite `1157 passed in 125.10s`, full suite `1410 passed in 172.45s`, static checks and guards reproduced. |
| Task 7 final review | Specification, theory, quality, and citation traceability `PASS`. |

Traceability citations are limited to project-internal source-verification
anchors `L16`, `L23`, and `L28` and their primary DOI URLs:
`https://doi.org/10.1007/BF02811330`,
`https://doi.org/10.1137/070699500`, and
`https://doi.org/10.1007/s11203-025-09326-9`. These citations are not used to
claim a new scientific result in this review.

## Invocation Incident

One non-required operator invocation set Windows `MYPY_CACHE_DIR=NUL` and caused
a mypy 2.3.0 internal error before source checking. The approved commands
without that override passed in both main and independent verification. This is
classified as an operator invocation issue, not as a project type-check failure.

Continuation command notes must not use `MYPY_CACHE_DIR=NUL` on Windows for this
project.

## Non-Authorization Statements

This review explicitly did not:

- create a G6-B case;
- run G6-B enumeration;
- solve a G6-B CTMC;
- run a G6-B DES simulation;
- inspect a G6-B output root or scientific result;
- replay R3;
- change authorization flags;
- modify immutable G4, G5, or G6 evidence.

The correction leaves immutable G4/G5/G6 evidence unchanged.

## Residual Stage

G6-B remains `OPEN/PENDING`. `case_creation_authorized=false` and
`scientific_execution_authorized=false` remain in force. G6-C, G6-D, and G6-E
are not started.

The next safe successor is a separately reviewed and approved
case-construction plan. It is not discovery execution, not CTMC/DES execution,
not a partial-domain production solve, and not a G6-B PASS claim.
