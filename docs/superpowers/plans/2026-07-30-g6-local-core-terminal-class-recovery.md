# IMS Deadlock G6 Local-Core And Terminal-Class Recovery Plan

Status: `PRE-IMPLEMENTATION / G5 CLOSED / NO G6 HELD-OUT OUTPUT`.

## Goal

Close the three mechanisms exposed by G5 without repairing or rerunning its
sealed panel:

1. theorem prediction and ancillary metrics were conflated by the locked
   scorer;
2. a declared local CRP bridge used a global operational-deadlock extractor;
3. the quantitative layer assumed `D union F` exhausted reachable terminal
   behavior before closed-class decomposition.

G6 may advance to a new confirmation freeze only after these mechanisms are
defined, implemented, proved on the restricted model class, and locked by
synthetic regression. G4/G5 rows are historical discovery/regression evidence
only.

## Immutable Historical Evidence

- G4 implementation A:
  `f9b9a5a5652c7a49053e7ef26d08911bd757f465`.
- G4 preregistration B2:
  `58bbd4ab7da8c2c1d0bcdea4a12f2ae7c020d09a`.
- G4 seal C:
  `e91be4d6d7511c76918093899269de4b78e69fd8`.
- G4 freeze ID:
  `G4-FREEZE-C-20260730T051210Z`.
- G5 tooling A:
  `b5e5dc0494b23a54c78c420bbca50a3639de8bff`.
- G5 execution lock B:
  `8aa752804b885b79e5371c98e7961087c540f2a8`.
- G5 original scored evidence C:
  `ff281481068a2325cb0bde00e85fd7b753ba854a`.
- Original locked score:
  `4 SUPPORTED / 3 FALSIFIED / 2 INCONCLUSIVE`.
- Transparent non-overwriting rule audit:
  `6 SUPPORTED / 1 FALSIFIED / 2 INCONCLUSIVE`, plus two independent
  `certificate_minimality=FAIL` observations.

No G6 code, theorem, score, or experiment may overwrite these objects or
retroactively change the status of a G5 row.

The retired G4 models may be executed after the G6 fix only as
`historical_replay` regression experiments requested by the investigator. Such
rows must use a new output root, code commit, schema and estimand identifier;
they cannot be called held-out confirmation or replace the G5 captures. A
publishable G6 confirmation claim still requires an independently generated and
newly sealed case set.

## Scientific Claim Boundary

The strongest admissible G6 claim is:

> For the explicitly defined finite IMS subclass, deterministic enumeration of
> inclusion-minimal local capacity-mediated blocking kernels supports a
> scope-correct partial-core bridge, and a closed-class-first stochastic
> partition yields exact and DES-consistent estimands for a newly sealed case
> set.

G6 does not claim:

- general IMS/Petri or plant-level S3PR equivalence;
- a universal deadlock theorem outside capacity-mediated semantics;
- CRP validity outside the frozen S4PR overlap;
- that every local core is an irreversible global failure;
- that relabelling local cores preserves the G5 estimand;
- a post-hoc repair or successful rerun of G5.

## Formal Objects To Freeze Before New Confirmation

### 1. Certificate Scope

Every certificate result declares one of:

- `global_covering`;
- `local_minimal`;
- `local_nonminimal_cover`;
- `unavailable`.

The API returns:

- a separately checkable global covering certificate when one exists;
- the complete, deterministically ordered family of inclusion-minimal local
  kernels;
- capacity and release evidence for each kernel;
- an explicit proof that no omitted proper subset is a kernel;
- bridge applicability and refusal reasons per local kernel.

Ordering is lexicographic over canonical job/resource identifiers and must not
affect truth values.

### 2. CRP Partial-Bridge Predicate

For a frozen target state and mapped CRP resource set `R_crp`, report four
orthogonal observations:

1. `target_reachable`;
2. `local_certificate_family_available`;
3. `matching_kernel_count = |{K: resources(K)=R_crp}|`;
4. `source_profile_consistent`.

`partial_bridge_agreement` is true only under the preregistered quantifier over
the whole minimal-kernel family. The initial G6 rule is exact existence:
`matching_kernel_count >= 1`; ambiguity and multiple matches remain visible.

### 3. Terminal-Class Taxonomy

On the complete reachable stable LTS, classify:

- `D_global`: global capacity-mediated deadlocks;
- `D_local`: states containing a local minimal core but not in `D_global`;
- `F`: declared completion states;
- `R_livelock`: non-`D/F` closed recurrent communicating classes;
- `R_terminal`: non-resource terminal states, including calendar-empty or
  missing-external-synchronization boundaries;
- `P_policy`: stalls created only by a supplied policy, excluded from the plant
  partition unless the policy is itself the analysis object;
- `S_T`: states that almost surely reach the selected absorbing target classes.

Membership priority and overlap handling must be explicit. In particular,
`D_global` is a subset of states with a local core but is reported only once.

### 4. Versioned Estimand

Every quantitative result records:

- state-space hash;
- class-partition hash;
- selected bad-class union;
- selected success class;
- exact stopping rule;
- rate-manifest hash;
- DES stopping-rule hash.

Changing any item creates a new estimand and invalidates direct comparison with
an earlier result.

### 5. Scoring Algebra

Each case row has independent fields:

- `execution_status`;
- `theorem_prediction_status`;
- `metric_applicability`;
- `metric_observations`;
- `reproducibility_status`;
- `claim_scope`.

No metric failure can change a theorem status unless the frozen falsifier
explicitly references that metric. No execution refusal can be scored as a
measured contradiction.

## Commit Topology

### G6-A — Semantics And Synthetic Regression

- theorem/metric scorer separation;
- all-minimal local-kernel enumeration;
- scope-correct CRP bridge;
- closed-class decomposition and structured refusal;
- no G4/G5 scientific rerun;
- synthetic tests only.

### G6-B — Discovery And Estimand Lock

- new discovery models that do not copy G4 case snapshots or parameter rows;
- terminal-class ontology and estimand schema;
- exact/DES implementation validation on discovery rows;
- negative controls and failure ledger;
- no held-out confirmation output.

### G6-C — Independent Confirmation Preregistration

- independently generated confirmation cases;
- predictions, falsifiers, baselines, metrics, state/rate bounds and random
  streams;
- discovery-overlap exclusions;
- runtime and resource plan;
- no confirmation execution.

### G6-D — Confirmation Seal

- exact file hashes, case hashes, schema hashes and command manifest;
- freeze checker returning `FROZEN`;
- `confirmation_results_inspected=false`;
- no held-out execution in this commit.

### G6-E — One Primary And One Repro

- execute only after G6-D is pushed and independently reviewed;
- retain all failures, refusals and negative controls;
- no automatic retry, no third run, no post-hoc seed or threshold change.

### G6-R — Historical G4 Replay

- run the previously failing CRP, grid and medium rows after G6-A/B only to
  verify the diagnosed mechanisms;
- label every record `historical_replay`, never `heldout_confirmation`;
- preserve the G5 raw hashes and status alongside the new result;
- one primary and one repro under the new G6 code/estimand;
- do not use replay success in confirmation-set prediction accuracy.

## Task 1: Repair Scoring Semantics With TDD

Files:

- `src/ims_deadlock/g5_scoring.py` or a versioned G6 scorer module;
- `tests/test_g5_scoring.py`;
- new G6 scoring schema and tests.

RED tests:

- adversarial boundary with `is_minimal=false` and all frozen theorem predicates
  satisfied is theorem `SUPPORTED` plus metric failure;
- outside-S4PR refusal with the same minimality miss remains theorem
  `SUPPORTED`;
- missing capacity-aware core remains a theorem falsifier only where the frozen
  prediction requires it;
- missing output or nonzero execution is `INCONCLUSIVE`, not a contradiction;
- original G5 summary remains byte/hash stable.

GREEN implementation:

- separate theorem reasons from metric observations;
- serialize each layer independently;
- provide a migration-free erratum view rather than replacing G5 output.

## Task 2: Enumerate All Minimal Local Kernels With TDD

Files:

- `src/ims_deadlock/certificates.py`;
- `src/ims_deadlock/analysis.py`;
- `tests/test_certificates.py`;
- `tests/test_analysis.py`.

RED tests:

- a model with two incomparable minimal local kernels returns both in canonical
  order;
- adding an unfinished outside job does not remove the local kernels and does
  prevent promotion to global deadlock;
- a nonminimal global cover and every minimal subkernel remain separately
  visible;
- OR-of-AND, capacity residuals, hard reservations and release alternatives
  remain in each witness;
- repeated enumeration is byte-identical.

Proof obligation:

For a finite job set, enumerate subsets in increasing cardinality and canonical
order, retain exactly those satisfying the six closed-kernel clauses, and
discard any set with a retained proper subkernel. Prove soundness, completeness
and order independence over the declared finite semantics.

## Task 3: Make The CRP Bridge Local And Multi-Kernel Safe

Files:

- `src/ims_deadlock/g4_protocol.py` or a versioned G6 bridge module;
- `tests/test_g4_protocol.py`;
- theory proof and migration-card updates.

RED tests:

- a reachable two-job local core plus an unrelated unfinished `free_job`
  produces a local certificate and one exact mapped-resource match;
- two minimal kernels do not make the result depend on enumeration order;
- unreachable target, outside-S4PR input and external-profile disagreement
  remain separate refusals;
- a global certificate is never substituted for a declared local bridge.

The synthetic models may reproduce the mechanism but may not reuse G4 target
snapshots, identifiers or frozen parameter values.

## Task 4: Decompose Closed Classes Before CTMC Construction

Files:

- `src/ims_deadlock/g4_instances.py`;
- `src/ims_deadlock/ctmc.py`;
- `src/ims_deadlock/stochastic.py`;
- tests for instances, CTMC and stochastic behavior.

RED tests:

- a local-core closed class outside `D_global/F` is identified before generator
  solve;
- a current local-kernel candidate whose job later uses a request-disconnected
  bypass after an outside-resource release is rejected with a shortest
  completion counterexample; structural irreversibility is claimed only for a
  request-closed subclass, while the generic finite implementation requires a
  complete-LTS completion-nonreachability audit;
- a genuine livelock SCC and a calendar-empty terminal state are distinguished;
- an unclassified closed class triggers structured refusal;
- `_validate_absorption_reachability` remains strict;
- selecting `D_global` versus `D_global union D_local` yields different
  partition/estimand hashes;
- exact and DES stop on the same frozen class labels;
- seed derivation and repeated output remain deterministic.

Do not weaken the validator. Repair the upstream partition and require an
explicit analysis target. `K_local` (current structural candidate) and
`D_local` (verified bad first-hit set) must not be conflated.

## Task 5: Close The Restricted Proof Chain

Update:

- `DEADLOCK_CERTIFICATES.md`;
- `PROBABILITY_LAYER.md`;
- `PETRI_BRIDGE.md`;
- `CORE_THEOREMS_AND_PROOFS.md`;
- `PROOF_OBLIGATIONS.md`;
- `COUNTEREXAMPLE_LEDGER.md`.

Required proof chain:

`finite stable LTS`
`-> complete minimal-local-kernel family`
`-> scope-correct local CRP bridge on declared overlap`
`-> closed communicating-class decomposition`
`-> versioned competing-class estimand`
`-> exact finite CTMC equations`
`-> independent DES cross-check`.

Every arrow must list assumptions and a smallest known failure boundary.
Enumeration validates proofs; it does not replace them.

## Task 6: Design Stronger Cases Without Post-Hoc Tuning

Discovery cases must include:

- two incomparable local kernels;
- a local core with an unrelated progressing job;
- a global core containing a proper local core;
- a genuine non-deadlock livelock;
- a calendar-empty non-resource terminal state;
- a policy-only stall;
- a paired case where adding AGV/reservation semantics changes the local-kernel
  family;
- a closed-class estimand pair showing why target choice changes probability.

The future independent confirmation set must include:

- a small exhaustively enumerable parameter family;
- a newly reconstructed medium manufacturing island;
- one adversarial multi-kernel CRP case;
- one negative control for each terminal class;
- exact and DES rows only where the complete partition is valid.

Independence checks reject any confirmation case sharing a frozen G4 case hash,
snapshot hash, route signature, parameter tuple or random-stream manifest.

## Task 7: Parallel Execution Policy

Use live Dell resource probes before each execution stage. Parallelism may
accelerate independent tests and future cases, but it may not alter scientific
semantics.

- run unit-test shards in parallel only when they do not share outputs;
- keep each scientific child single-process unless nested parallelism is
  separately frozen;
- isolate output directories by case and run label;
- never overlap primary and repro of the same case;
- reserve memory headroom for state-space construction;
- record CPU, memory, storage, worker cap and scheduling waves before held-out
  execution.

## Task 8: Root-Cause Replay Experiment

After the code and theory gates pass, execute a G6 historical replay of:

- `G4_CRP_S4PR_AGREE` to test local-kernel bridge availability and exact
  resource-set matching;
- `G4_IMS_PARAMETER_GRID` to test complete terminal-class partition and the
  newly declared estimand;
- `G4_MEDIUM_ISLAND_REBUILD` for the same partition/estimand mechanism at
  medium scale;
- adversarial and outside-S4PR rows to verify theorem/metric score separation
  while retaining the minimality metric failures.

Use a new task-owned output root and an execution lock that records the G6
commit, retired-case status, partition hashes and no-confirmation-use flag.
Execute exactly one primary and one repro. This experiment answers whether the
diagnosed software/semantic mechanisms were repaired; it does not answer the
new held-out scientific hypothesis.

## Verification Gates

### G6-A Code Gate

- all synthetic RED/GREEN regressions pass;
- full pytest, Ruff check/format and strict mypy pass on Dell;
- original G5 evidence hashes remain unchanged;
- no G4/G5 scientific command ran.

### G6-B Theory/Discovery Gate

- local-kernel soundness/completeness proof reviewed;
- terminal-class partition exhaustive and disjoint under declared precedence;
- exact/DES target hashes match;
- all discovery failures remain in the ledger.

### G6-C/D Freeze Gate

- confirmation cases are independent of G4/G5 and G6 discovery;
- predictions, falsifiers, metrics, random streams and timeouts are fixed;
- hashes and runtime commands are sealed before output inspection;
- independent reviewer returns `FROZEN`.

### G6-E Evidence Gate

- every case has exactly one primary and one repro;
- raw/canonical hashes and deterministic failures are reported;
- theorem, metric, execution and reproducibility statuses remain orthogonal;
- exact/DES claims use the same partition and estimand hashes;
- paper gate remains failed if any main-chain obligation is falsified or
  inconclusive.

## Stop Conditions

Stop before new held-out execution if:

- all-minimal enumeration is incomplete or order-sensitive;
- CRP bridge still consumes a global certificate;
- any closed class is unclassified;
- the bad-class union or DES stopping rule is not frozen;
- scorer layers are not orthogonal;
- confirmation independence cannot be demonstrated;
- code, static checks or freeze validation fail.

If G6 only relabels G5 failures without a new theorem or estimand boundary,
stop and reformulate the scientific question instead of expanding experiments.
