# G6-B Protocol Foundation Review

## Verdict

Verdict: `PASS FOUNDATION ONLY`.

This separate-agent review found no `Critical`, `Important`, or `Minor`
protocol findings in the G6-B protocol foundation as a foundation artifact. The
scope was local and read-only: no SSH, no remote commands, no source edits, no
case creation, no enumeration, no CTMC solve, no DES run, and no science-output
inspection.

This verdict does not set `adversarial_review_status` to `PASSED`. It does not
authorize science, does not pass G6-B, and does not satisfy any G6-C/D/E
confirmation gate. It only allows drafting and reviewing a separate row-family
discovery-model/execution plan.

## Scope

Review target: local snapshot under `bootstrap_source`, with the exact review
surface below.

| Role | File |
| --- | --- |
| Human protocol | `docs/cases/G6_B_DISCOVERY_PROTOCOL.md` |
| Protocol control JSON | `cases/discovery/g6b/protocol.json` |
| Estimand schema | `cases/discovery/g6b/estimand_schema.json` |
| Independence schema | `cases/discovery/g6b/independence_schema.json` |
| Negative controls | `cases/discovery/g6b/negative_controls.json` |
| Failure ledger | `cases/discovery/g6b/failure_ledger.json` |
| Data-only validator | `src/ims_deadlock/g6b_protocol.py` |
| Targeted validator tests | `tests/test_g6b_protocol.py` |
| Boundary status anchors | `docs/ROADMAP.md`, `PROJECT_HANDOFF.md`, `docs/cases/CASE_CHANGE_LEDGER.md` |

Remote authoritative full-suite validation was already recorded at locked
worktree `D:\worktree\IMS_deadlock-g6b-discovery` HEAD `4c24f39` before the
state-doc commit: full `393` tests, Ruff, two strict mypy checks, five JSON
parse checks, `52` targeted protocol tests, and `git diff --check`. The later
state integration commit is `ab82413`. That remote record is treated here as
pre-existing validation evidence, not as a command run by this local review.

Local review verification in this pass:

| Check | Result |
| --- | --- |
| Five protocol JSON files parsed as JSON objects | `PASS` |
| Targeted local protocol tests | `52 passed` |

## Review Questions

1. Does the foundation keep G6-B discovery-only and execution-disabled?
2. Does it keep `adversarial_review_status` at `PENDING` instead of silently
   passing the review gate?
3. Does it define `K_local`/local candidates separately from admitted
   `D_local`?
4. Does it distinguish the A2b proof route from the complete-LTS
   completion-nonreachability audit route?
5. Does it keep `D_local` separate from plant terminal SCC classes?
6. Does it require exact and DES rows to share the same target identity,
   selected bad labels, selected success label, and versioned target?
7. Does it preserve five orthogonal scoring layers?
8. Does it require discovery-vs-retired independence across the eight G4/G5/G6-R
   dimensions?
9. Does it define the seven future-confirmation independence dimensions and the
   limited metric-schema reuse exception?
10. Does it retain negative controls and an append-only failure ledger?

## Findings

| Severity | Finding | Evidence |
| --- | --- | --- |
| Critical | None. | The human protocol fixes `scientific_execution_authorized = false` and `adversarial_review_status = PENDING` (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:16`, `docs/cases/G6_B_DISCOVERY_PROTOCOL.md:17`). The protocol JSON carries the same disabled/pending state (`cases/discovery/g6b/protocol.json:6`, `cases/discovery/g6b/protocol.json:7`). |
| Important | None. | The validator treats specified G5 historical authorities as remote-only and validates tracked authorities without requiring those remote-only files to exist in the local snapshot (`src/ims_deadlock/g6b_protocol.py:63`, `src/ims_deadlock/g6b_protocol.py:66`; `src/ims_deadlock/g6b_protocol.py:264`, `src/ims_deadlock/g6b_protocol.py:271`). |
| Minor | None. | The targeted tests cover valid bundle status, duplicate keys, wrong layout, extra/missing JSON, top-level key drift, ontology drift, exact/DES drift, negative-control drift, unsafe paths, execution-true while review-pending, append-only drift, and ambiguous artifact paths (`tests/test_g6b_protocol.py:124`, `tests/test_g6b_protocol.py:140`, `tests/test_g6b_protocol.py:156`, `tests/test_g6b_protocol.py:163`, `tests/test_g6b_protocol.py:170`, `tests/test_g6b_protocol.py:180`, `tests/test_g6b_protocol.py:253`, `tests/test_g6b_protocol.py:266`, `tests/test_g6b_protocol.py:288`, `tests/test_g6b_protocol.py:312`, `tests/test_g6b_protocol.py:323`, `tests/test_g6b_protocol.py:332`, `tests/test_g6b_protocol.py:341`). |

## Evidence Notes

### Execution Boundary

The protocol creates no cases and authorizes no enumeration, CTMC solve, or DES
run. It requires adversarial review before scientific execution
(`cases/discovery/g6b/protocol.json:28`, `cases/discovery/g6b/protocol.json:33`).
The human protocol states the same boundary and says scientific execution is
disabled until a later adversarial protocol review passes and records a later
explicit authorization artifact (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:7`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:10`).

### `K_local` Versus `D_local`

`K_local` or any local candidate is only a candidate surface. It can enter
`D_local` only after one admitted proof/audit route succeeds. The protocol says a
local candidate enters `D_local` only through an accepted A2b proof or a
complete-LTS completion-nonreachability audit
(`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:64`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:69`). The change ledger records that the
review-found corrections distinguish `K_local` from `D_local`
(`docs/cases/CASE_CHANGE_LEDGER.md:25`).

### A2b Route Versus Complete-LTS Audit Route

The A2b route establishes structural irreversibility under declared finite
semantics. The complete-LTS route proves completion nonreachability from the
candidate state. They are alternative admission routes, not aliases
(`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:64`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:69`;
`cases/discovery/g6b/estimand_schema.json:24`,
`cases/discovery/g6b/estimand_schema.json:30`).

### `D_local` Versus Terminal SCC

`D_local` is a verified first-hit bad set selected by the G6-B estimand, not a
plant terminal SCC (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:40`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:44`;
`cases/discovery/g6b/estimand_schema.json:24`,
`cases/discovery/g6b/estimand_schema.json:26`). The implementation-level
terminal partition makes the same distinction: `D_local` may have outgoing
plant-LTS arcs, while only `R_livelock` and `R_terminal` come from terminal SCCs
of the remaining graph (`src/ims_deadlock/terminal_classes.py:97`,
`src/ims_deadlock/terminal_classes.py:103`;
`src/ims_deadlock/terminal_classes.py:181`).

### Exact/DES Target Identity

Future exact and DES rows must share the same selected bad labels, selected
success label, and versioned target (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:58`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:60`). The estimand schema requires future
hashes for state space, partition, rate manifest, stopping rule, DES stopping
rule, and estimand id (`cases/discovery/g6b/estimand_schema.json:6`,
`cases/discovery/g6b/estimand_schema.json:13`) and requires same target, bad
labels, success label, and versioned target for exact/DES consistency
(`cases/discovery/g6b/estimand_schema.json:39`,
`cases/discovery/g6b/estimand_schema.json:44`).

### Five Orthogonal Scoring Layers

The five scoring layers are `theorem_prediction_status`,
`metric_applicability`, `metric_observations`, `execution_status`, and
`reproducibility_status` (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:113`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:119`;
`cases/discovery/g6b/protocol.json:35`,
`cases/discovery/g6b/protocol.json:45`). Metric failure cannot change theorem
status unless the frozen falsifier explicitly references the metric
(`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:121`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:125`).

### Discovery-Versus-Retired Independence

G6-B discovery rows require zero overlap with retired G4/G5/G6-R authorities on
eight dimensions: case content, state snapshot, route signature, parameter
tuple, random-stream manifest, output root, sealed prediction, and metric schema
(`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:77`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:96`;
`cases/discovery/g6b/independence_schema.json:16`,
`cases/discovery/g6b/independence_schema.json:27`). Retired authorities are
historical only (`cases/discovery/g6b/independence_schema.json:28`,
`cases/discovery/g6b/independence_schema.json:31`).

### Future Confirmation And Limited Metric Reuse

Future G6 confirmation rows must be independent from retired authorities and
G6-B discovery case identity/provenance across seven dimensions: case content,
state snapshot, route signature, parameter tuple, random-stream manifest, output
root, and sealed prediction (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:103`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:109`;
`cases/discovery/g6b/independence_schema.json:62`,
`cases/discovery/g6b/independence_schema.json:79`). Metric schema reuse is not a
blanket permission; it is allowed only if explicitly preregistered, needed for
same-target comparability, and not derived from inspected outcomes
(`cases/discovery/g6b/independence_schema.json:80`,
`cases/discovery/g6b/independence_schema.json:87`).

### Negative Controls And Failure Ledger

The seven mandatory negative controls are present and have
`not_support_if_failed=true` (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:127`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:149`;
`cases/discovery/g6b/negative_controls.json:6`,
`cases/discovery/g6b/negative_controls.json:49`). The failure ledger is
append-only, currently has no admitted discovery entries, and explicitly says
empty entries do not mean no failures exist
(`cases/discovery/g6b/failure_ledger.json:6`,
`cases/discovery/g6b/failure_ledger.json:8`). The human protocol requires every
refused admission, failed negative control, schema incompatibility, target drift,
overlap hit, missing hash, incomplete LTS audit, or execution attempt to remain
in the append-only ledger (`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:184`,
`docs/cases/G6_B_DISCOVERY_PROTOCOL.md:190`).

## Non-Authorization Statements

This review explicitly does not authorize any of the following:

- changing `adversarial_review_status` from `PENDING` to `PASSED`;
- marking G6-B as passed;
- claiming scientific confirmation;
- creating discovery cases;
- running enumeration, CTMC, or DES;
- creating output roots, state snapshots, random streams, predictions, exact
  outputs, DES outputs, or scientific summaries;
- reusing retired G4/G5/G6-R evidence as G6-B discovery rows;
- opening G6-C/D/E confirmation gates;
- treating metric-schema reuse as case-identity reuse permission;
- deleting or summarizing away negative controls, failures, refused admissions,
  or boundary cases.

## Stop Condition

Stop condition for this review is met: the protocol foundation can be used as
the input to a separate row-family discovery-model/execution-plan draft and
review. Any later move from planning to scientific execution requires a new
explicit authorization artifact, a zero-overlap report, a runtime lock, current
failure ledger, exact/DES same-target evidence, and full G6-B pass criteria.
