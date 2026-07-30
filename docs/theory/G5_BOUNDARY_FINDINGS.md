# G5 Boundary Findings And G6 Successor Obligations

Status: `POST-G5 / HISTORICAL EVIDENCE / NOT PART OF THE G4 SEAL`.

This document records findings made only after the G4 C seal and G5 execution.
It intentionally lives outside the frozen G4 theory manifest. The sealed
theory files, predictions and metrics remain byte-identical to their historical
hashes. Any theorem change must enter a separately versioned G6 successor seal.

## BF-G5-1 Theorem Status And Metric Status Are Orthogonal

The locked G5 scorer treated `certificate_minimality` failures as
theorem-prediction falsifiers for `G4_ADVERSARIAL_BOUNDARY` and
`G4_CRP_OUTSIDE_S4PR`, although neither frozen falsifier contains minimality.

Both cases start from a frozen target snapshot (`s0`), so their shortest
reachable prefix is empty. The returned global covering certificate contains
jobs `gate,left,right`; a proper local subkernel is witnessed by
`gate,left` with resources `reserve_a,cart_right,inspection`.

Successor obligations:

- score `execution_status`, `theorem_prediction_correctness`,
  `metric_applicability`, metric values and reproducibility independently;
- retain the two `certificate_minimality=FAIL` observations;
- preserve the locked `4/3/2` output and report the transparent theorem audit
  `6/1/2` without overwriting it;
- permit a metric to change theorem status only when the frozen falsifier
  explicitly references that metric.

## BF-G5-2 Global Coverage Cannot Substitute For A Local CRP Bridge

`G4_CRP_S4PR_AGREE` has the reachable witness:

`admit_left -> admit_right -> left_service_complete -> right_service_complete`.

Independent reachability and the supplied evidence profile agree, and the
mapped CRP resources are `{cell_x,cell_y}`. The implementation nevertheless
classified the row as `partial_deadlock_bridge_disagreement` because the bridge
called the global operational-deadlock extractor while an unrelated
`free_job` remained unfinished outside the intended two-job core.

This falsifies the frozen implementation-level bridge prediction, not the
general CRP theorem. G6 must:

- declare certificate scope as global or local;
- retain a separately checkable global covering certificate;
- deterministically enumerate all inclusion-minimal local kernels;
- compare mapped CRP resources against the whole intended local-kernel family;
- report zero, one or multiple matches without order-dependent first-hit
  semantics.

## BF-G5-3 `D/F` Did Not Exhaust Reachable Terminal Behavior

The G5 quantitative rows refused construction before producing probability or
DES results:

- parameter grid: `state 's5' must have reachable absorbing transition`;
- medium island: `state 's79' must have reachable absorbing transition`.

Primary and repro have identical exit codes, empty stdout and stderr hashes.
The validator correctly rejected an unproved absorption assumption. The
reachable LTS contains local-core or other non-`D/F` terminal/recurrent
behavior not covered by the global-deadlock/completion partition.

G6 must classify, before generator construction:

- `D_global`: global capacity-mediated deadlock;
- `D_local`: a local minimal core without global coverage;
- `F`: declared completion;
- `R_livelock`: other closed recurrent classes;
- `R_terminal`: calendar-empty, external-synchronization or other non-resource
  terminal boundaries;
- `P_policy`: policy-only stalls, when applicable.

It must then freeze a bad-class union and record a state-space hash,
class-partition hash, rate hash and DES stopping-rule hash. Changing
`D_global` to `D_global union D_local` is a new estimand, not a repair of G5.
The strict absorption-reachability validator must not be weakened.

## G6 Proof And Test Gate

Before a new held-out confirmation freeze, G6 must close:

1. soundness, completeness and order independence of all-minimal local-kernel
   enumeration over the declared finite semantics;
2. reachability, local-certificate availability and mapped-resource equality as
   three independent CRP bridge obligations;
3. an exhaustive/disjoint terminal-class partition under a declared precedence
   rule;
4. exact CTMC and independent DES use of the same versioned estimand;
5. synthetic regressions for the three G5 mechanisms;
6. an independent new confirmation set.

Retired G4 rows may be replayed only as labelled historical regressions under a
new G6 code commit, output root and estimand. Replay success cannot replace G5
evidence or count as new held-out confirmation.
