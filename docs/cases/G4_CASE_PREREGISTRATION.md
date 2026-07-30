# G4 Literature-Informed Case Preregistration Draft

Status: `DRAFT-NOT-FROZEN`.

This document designs the next hard G4 gate after the seven-paper audit. It
does not freeze cases, does not report results, and does not upgrade any
theorem truth status. All rows are planned confirmation candidates or
comparator checks whose final parameters, hashes, prediction sheet, runtime,
and baseline manifests still must be frozen in `CONFIRMATION_PREREGISTRATION.md`.

## Design Principles

- Keep discovery cases out of confirmation: `C0-C5`, `BIX1-SAT`, and
  `BIX2-PERSIST` can inspire mechanisms but cannot become held-out evidence.
- Separate structural/algebraic candidates from executable prefixes. A CRP,
  siphon, state-equation NIS, or recorder-transformed marking is not an IMS
  result until reachability and semantic mapping obligations are checked.
- Preserve negative results: unreachable candidates, bridge refusals, and
  baseline inapplicability are planned outcomes, not cleanup targets.
- Treat `L30`, `L31`, `L32/L33`, `L34/L35`, and `B05` as comparators with
  explicit assumptions, not theorem donors.

## Planned G4 Families

| Family | Purpose | Required outcome fields | Freeze status |
| --- | --- | --- | --- |
| `G4-CRP-S4PR-AGREE` | Restricted S4PR overlap where IMS wait-snapshot/core, S4PR CRP, and executable prefix should agree. | S4PR map hash, CRP set, IMS core, SBA/BFS prefix, siphon/core comparison. | draft |
| `G4-CRP-UNREACHABLE-CANDIDATE` | Structural/algebraic CRP or siphon candidate exists, but legal firing sequence or IMS prefix is absent. | candidate equations, failed SBA/BFS reason, no IMS deadlock claim, supervisor-not-needed flag. | draft |
| `G4-CRP-OUTSIDE-S4PR` | BAS blocked-unload, AGV occupancy/reservation, or AND request violates S4PR/CRP assumptions. | refusal code, missing S4PR assumption, IMS certificate status, projection false-positive/false-negative note. | draft |
| `G4-RECORDER-TARGET-QUANTIFICATION` | `L32/L33` recorder-place transformation obligation for fixed original targets. | original target, recorder target construction, existential/fixed-count quantifier check, preservation direction. | draft |
| `G4-L30-RESOURCE-BASELINE` | Finite-capacity S3PR/ENS3PR resource-configuration comparator. | sufficient-resource prediction, IMS exact-threshold prediction, disagreement classification. | draft |
| `G4-B05-SUPERVISOR-COMPARATOR` | Small explicit PN/RG maximally permissive supervisor comparator. | full RG hash, legal/FBM covering summary, MCPP status, permissiveness comparison, inapplicability reason if not run. | draft |

## CRP Triad

The G4 CRP package must include all three rows below before any S4PR overlap
claim is allowed.

### 1. S4PR Agreement

Build a small S4PR-compatible IMS instance whose resource places, activity
places, initial marking, and firing semantics have an explicit bidirectional
map. The preregistered prediction may state agreement only inside this overlap:

- CRP marks the same partial-deadlock resource/activity set as the IMS local
  closed blocking core;
- the candidate marking has an explicit legal firing/event prefix verified
  against the source and IMS models; complete finite BFS/LTS enumeration is
  the independent oracle, while SBA is reported only as a comparator;
- the wait-snapshot diagnostic siphon is applicable only if `IMS-SIP^1`
  assumptions also hold.

### 2. Unreachable Structural/Algebraic Candidate

Build a paired S4PR-compatible instance where a siphon, CRP-shaped algebraic
candidate, or state-equation NIS is generated but no legal firing sequence from
the initial marking exists. Nonreachability must be closed by complete
finite-state BFS/LTS enumeration under a preregistered state bound, not by an
SBA return code alone. The expected report is a refusal:

- `structural_candidate_present=true`;
- `executable_prefix_present=false`;
- `ims_deadlock_claim=false`;
- no supervisor-cost win is credited for controlling the unreachable marking.

### 3. BAS/AGV/AND Outside S4PR

Build an IMS instance with one or more of:

- BAS blocked-unload holding after processing completion;
- AGV occupancy or hard reservation token required for the blocking kernel;
- AND/conjunctive request that cannot be reduced to a single S4PR resource
  request without changing semantics.

The expected report is not CRP disagreement. It is `not_applicable` unless an
explicit S4PR embedding is separately proved and hashed.

## Recorder Target-Quantification Obligation

`L32/L33`-style recorder transformations add output-only recorder places and
do not change original transition enabling. G4 must therefore avoid assuming a
negative preservation result. The case asks a narrower question: whether the
recorder construction, together with a fixed original IMS/Petri target marking,
closes the quantification needed by this project.

Required checks:

- every original executable trace used in the case maps into the instrumented
  model with the expected recorder count;
- the original target marking is mapped to a recorder target before solving
  reachability, rather than chosen after the fact;
- existential reachability of some recorder count is distinguished from
  reachability of the fixed count required by the original target;
- completion, partial-deadlock, and global-deadlock predicates are evaluated on
  the projected original marking, not on recorder-only state.

If all obligations are proved, the row is comparator agreement. If only one-way
trace preservation is available or the fixed-count target obligation remains
open, the row is a non-migration boundary. It is not a forced counterexample.

## L30 Resource-Configuration Baseline

The `L30` baseline is applicable only after an instance is represented as the
finite-capacity S3PR/ENS3PR class required by that paper. The planned question
is whether its minimum initial resource marking is a conservative sufficient
configuration relative to IMS exact reachable-threshold claims.

Allowed conclusions:

- `sufficient_configuration_agrees`;
- `sufficient_configuration_conservative`;
- `not_applicable_non_s3pr_ims_features`;
- `exact_threshold_not_claimed`.

Forbidden conclusions:

- `L30 proves IMS iff threshold`;
- `L30 eliminates need for executable reachability witness`;
- `L30 validates BIX2 outside its explicit three-resource family`.

## B05 Supervisor Comparator

The `B05` baseline is applicable only for small explicit Petri/RG overlap
instances where:

- the full reachability graph is generated and hashed;
- legal markings and first-met bad markings are identified;
- the covering/MCPP optimization result is recorded;
- P-semiflow control-place assumptions are checked.

If any condition fails, the baseline is reported as inapplicable. A successful
run compares structural compression and permissiveness only; it does not prove
that compact IMS supervisor synthesis is tractable.

## Freeze Checklist

Before G4 can move from draft to frozen, record:

- exact case JSON identifiers and SHA-256 hashes;
- S4PR/IMS embedding specifications and hashes;
- prediction sheet for every family above;
- baseline applicability sheet for `L30`, `L31`, `L32/L33`, `L34/L35`, and
  `B05`;
- explicit-prefix verifier and full finite BFS/LTS oracle per case; SBA may be
  added as a separately reported comparator but cannot be the sole oracle;
- metric schema and negative-result reporting rules;
- runtime and command lock.

Until all fields are filled, G4 status remains `NOT FROZEN`.
