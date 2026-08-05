# Local Deadlock as a Stopping Event: Two Sound Admission Routes and a Constructive Finite-Case Closure for IMS-RAS

Manuscript status: `SCOPED CONSTRUCTIVE DRAFT`

Evidence status: `TIER A DUAL-ROUTE CLOSURE`

Original programme status: `G6-B OPEN_PENDING`

## Abstract

Local resource blocking in an integrated manufacturing system can prevent a
subset of jobs from ever completing while other jobs remain able to move. Such
a state is operationally important, but it need not be a terminal strongly
connected component of the plant state graph. Treating every apparent local
blocking core as a terminal class is therefore unsound; treating only global
no-transition states as deadlock can instead miss irreversible local failure.

We formulate local deadlock as a verified bad first-hit set in a stopped
finite-state process. A local blocking candidate is admitted by one of two
routes: a request-closed structural sufficient condition, denoted A2b, or a
complete finite-LTS audit proving that all-batch completion is unreachable from
that candidate. We separate the plant graph from the stopped graph, impose
global-before-local classification precedence, and reject candidates with a
completion bypass. Three component probabilities—first absorption in global
deadlock, verified local deadlock, and their union—are then computed from the
same stopped target by an exact CTMC solver and a reproducible discrete-event
simulation.

The theory is closed against a predeclared six-case constructive panel: five
sealed discovery/boundary cases and one nondegenerate competing-absorption
bridge. In the bridge, a transient state jumps to verified local deadlock at
rate 1 or completion at rate 2, yielding the analytical selected-bad
probability `1/3`. With 4096 frozen-seed replications, simulation gives
`0.33642578125`; the absolute error is `0.0030924479166667`. All 18
case-estimand comparisons satisfy the preregistered simultaneous tolerance
`0.028340`. The result establishes an internally consistent, scoped
theory-to-witness closure for both admission routes. It is not held-out
confirmation, does not show that one method covers every IMS case, and does not
close the original full G6-B overlap programme.

Keywords: integrated manufacturing systems; resource allocation systems;
deadlock; local blocking; first-hit probability; absorbing CTMC; discrete-event
simulation; finite labelled transition system

## 1. Introduction

Deadlock analysis in manufacturing resource-allocation systems is often
presented as a search for a plant state from which nothing can move. That
global notion is important but incomplete for systems with several weakly
coupled jobs or cells. A subset of jobs may enter an irreversible capacity
cycle while another job continues to execute. The plant therefore has outgoing
arcs, yet all-batch completion has already become impossible.

This creates two symmetrical errors.

First, a method that reports only a global no-transition state can miss a
local, completion-destroying hit. Second, a method that promotes every current
local cycle to deadlock can be fooled by a bypass: a job may later use a
transition unrelated to its current request, release a resource, and allow all
jobs to complete. The appropriate question is consequently not whether a
single local-certificate rule covers every model. It is whether each declared
method has explicit assumptions, whether candidates outside those assumptions
are refused or sent to a stronger audit, and whether the resulting bad set is
used consistently by the probability layer.

This paper develops that scoped answer. Its central distinction is

```text
verified local bad hit != plant terminal SCC.
```

We make four contributions.

1. We define a mutually exclusive stopped target containing global deadlock,
   verified local deadlock, and all-batch completion.
2. We state a request-closed sufficient condition under which a certified local
   blocking kernel makes completion unreachable.
3. We give complete finite-LTS completion nonreachability as a model-specific
   fallback when the structural condition cannot be proved.
4. We close the definitions against matched constructive and boundary cases,
   including a nondegenerate exact-versus-DES probability bridge.

The contribution is deliberately limited. The cases show logical closure of a
theory/method article. They do not establish population-level performance,
method superiority, or universal coverage.

## 2. Model and semantic boundary

### 2.1 Stable finite plant LTS

Let the plant be represented after zero-time normalization by a finite labelled
transition system

\[
\mathcal G=(X,E),
\]

where `X` is the set of reachable stable states and an edge
`(x,e,y) in E` denotes a positive-rate plant transition. The article assumes:

- finite jobs, resources, capacities, modes, and request alternatives;
- complete, nontruncated state and transition enumeration for every case that
  uses the complete-LTS route;
- per-job state updates, no preemption, no exogenous release, no dynamic job
  insertion, and resource-capacity conservation for the A2b theorem;
- OR-of-AND request semantics;
- a complete transition registry;
- positive finite rates for the quantitative layer;
- no reachable unselected closed class in the stopped transient domain.

These are scope conditions, not empirical findings. If a case violates them,
the correct output is refusal or a new versioned model, not forced
classification.

### 2.2 Objective state predicates

Let `F` be the set of all-batch-complete states. A state in `F` has every job
complete, no retained resource, and no unresolved request.

Let `D_global` be the set of stable, incomplete states in which no transition
is enabled, every unfinished job is blocked, and a capacity-mediated closed
blocking certificate covers all unfinished jobs. `D_global` is a plant-level
operational predicate.

Let `K_local` be the set of non-global states containing at least one
inclusion-minimal local closed blocking kernel. A kernel contains a nonempty
job set, the witness resources that make every current request alternative
infeasible, and the corresponding holders. A current kernel is only a
candidate: it proves present blocking, not future noncompletion.

Let `D_local` be the subset of `K_local` admitted by either the A2b structural
route or the complete-LTS route defined below. Classification precedence is

```text
F exclusion -> D_global -> D_local among the remaining states.
```

Thus `D_global`, `D_local`, and `F` are pairwise disjoint, and a global state
that also contains a local-looking core is counted once in `D_global`.

### 2.3 Plant process and stopped process

Define the selected stopped target

\[
A_{\mathrm{stop}}=D_{\mathrm{global}}\cup D_{\mathrm{local}}\cup F
\]

and the first-hit time

\[
\tau=\inf\{t\ge 0:X_t\in A_{\mathrm{stop}}\}.
\]

The plant graph is unchanged. The stopped process removes outgoing arcs only
after a selected target has been hit. Therefore a state may belong to
`D_local` even if the plant has outgoing arcs from it. This is not a
contradiction: membership states that the declared failure event has occurred,
not that the entire plant has become graph-terminal.

## 3. Two local-admission routes

### 3.1 Local closed blocking kernel

At a stable state `x`, let

\[
K=(J_K,R_K,W_K)
\]

be a local closed blocking kernel if:

1. `J_K` is nonempty and every job in it is incomplete;
2. each kernel job has at least one current capacity-ready request alternative;
3. every alternative of every kernel job is short of at least one resource in
   `R_K`;
4. the holders that explain each witness shortage are kernel jobs or declared
   kernel-internal hard reservations;
5. no kernel job has an enabled transition; and
6. the job/resource witness is inclusion-minimal.

The all-alternatives requirement is essential. Blocking one branch of an
OR-of-AND request does not establish blocking when another branch is feasible.

### 3.2 A2b request-closed sufficient condition

The A2b condition applies only to a declared request-closed subclass. For an
incomplete job with current unresolved requests, every transition that could
change its mode, holdings, request state, or completion status must consume a
currently declared feasible request alternative. There is no bypass through a
different external resource, guard, or intermediate mode.

**Theorem 1 (request-closed local noncompletion).** Under the finite per-job,
no-preemption, conservation, complete-registry, and A2b assumptions, if a stable
state contains a local closed blocking kernel `K`, no job in `J_K` can complete
on any future plant path. Consequently, all-batch completion `F` is unreachable
from the hit state.

**Proof.** At the hit state, no kernel job has an enabled transition. A plant
transition of an outside job cannot directly change a kernel job's mode,
holdings, requests, or completion flag. No external action can preempt or
exogenously release a witness unit held inside the kernel. Every request
alternative of every kernel job is short of at least one such witness resource.
Outside jobs can at most use and release residual capacity; they cannot release
units locked by kernel jobs or raise the available amount above the hit-state
upper bound. Finally, A2b excludes a progress, release, or completion bypass
that ignores the unresolved requests. Hence no kernel job can acquire a
feasible alternative or complete. Since `F` requires every kernel job to
complete, `F` is unreachable. QED.

The invariant is job noncompletion and request blockedness, not textual
identity of a certificate object. State identifiers, holder lists, residual
capacity, and a certificate serialization may change as outside jobs move.

### 3.3 Complete finite-LTS fallback

When A2b cannot be proved, current local structure alone is insufficient. For a
complete, finite, nontruncated plant LTS, define a candidate `x in K_local` to
be LTS-admissible precisely when there is no directed plant path from `x` to
any state in `F`.

**Proposition 2 (finite-model semantic admission).** If the enumerated LTS is
complete and `F` is unreachable from a local candidate `x`, using `x` as a bad
first-hit target is sound for that concrete finite model.

The proof follows directly from exhaustive reachability. Its strength and its
limitation are the same: it proves a property of the enumerated model only. It
does not create a general structural theorem for unenumerated models.

If a path to `F` exists, the method must retain the path as a counterexample and
exclude the candidate from `D_local`.

### 3.4 Method boundary

The two routes are alternatives, not competitors required to cover the same
case.

| Route | What it establishes | Required boundary | Correct failure response |
| --- | --- | --- | --- |
| A2b | structural sufficiency for request-closed models | per-job semantics and no request-independent bypass | refuse A2b; use complete LTS if available |
| complete LTS | completion nonreachability in one finite enumerated model | complete, nontruncated state/edge registry | return a completion path or structural refusal |

This division is the article's main scope discipline: a method is judged on
cases that satisfy its declared assumptions, not on whether it covers every
possible IMS semantics.

## 4. Stopped CTMC and estimands

### 4.1 Probability-one absorption domain

Let

\[
T=X\setminus A_{\mathrm{stop}}
\]

be the transient candidate set. In a finite positive-rate graph, every state in
the claimed quantitative domain must reach `A_stop`, and no reachable closed
strongly connected component may remain entirely inside `T`. Under these
conditions, absorption in `A_stop` occurs almost surely and the transient
generator block is nonsingular.

### 4.2 Three component probabilities

This article uses component notation to avoid overloading earlier aggregate
symbols:

\[
\theta_g=P(X_\tau\in D_{\mathrm{global}}),
\]

\[
\theta_\ell=P(X_\tau\in D_{\mathrm{local}}),
\]

\[
\theta_b=P(X_\tau\in D_{\mathrm{global}}\cup D_{\mathrm{local}})
         =\theta_g+\theta_\ell.
\]

The machine-readable names are respectively
`theta_global_before_success`, `theta_local_before_success`, and
`theta_selected_bad_before_success`. All three are evaluated under the same
three-way first-hit partition; the local component is not computed by allowing
paths to pass through `D_global`.

### 4.3 Exact committors

For each absorbing class `c`, let `h^(c)` be its first-absorption committor. If
`Q_TT` is the transient generator block and `Q_Tc` contains rates from transient
states to class `c`, then

\[
Q_{TT}h_T^{(c)}=-Q_{Tc}\mathbf 1,
\]

with boundary values one on class `c` and zero on the other selected classes.
The mean stopped time satisfies

\[
Q_{TT}m_T=-\mathbf 1.
\]

The implementation solves the global, local, and selected-bad reductions and
checks `theta_g + theta_l = theta_b` numerically.

### 4.4 Independent-seed DES cross-check

DES uses Gillespie sampling of the same positive-rate transitions and stops on
the same three target classes. Replication `i` uses

```text
seed_i = integer(sha256("2026080601:i")).
```

The cross-check is semantic, not inferential generalization. It tests whether
an independently executed stochastic path mechanism agrees with the exact
first-hit calculation on the declared cases.

For 4096 replications in each of six cases and at most 18 comparisons, the
predeclared familywise Hoeffding tolerance is

\[
\epsilon=
\sqrt{\frac{\log(2\cdot18/0.05)}{2\cdot4096}}
<0.028340.
\]

No rerun is permitted solely because an empirical cell misses this threshold.

## 5. Predeclared constructive case panel

The panel was frozen before article-core outcomes were generated. Five cases
reuse sealed discovery/boundary artifacts; one bridge case was separately
declared to supply a nondegenerate probability.

| Case | Purpose | Route or guard |
| --- | --- | --- |
| global positive | show time-zero `D_global` classification | global predicate |
| A2b local positive | local kernel with an outside progressing job | A2b |
| multi-kernel local positive | two local hit states with plant arcs after the hit | complete LTS |
| completion bypass | show that a current local candidate can still complete | nonadmission control |
| global/local overlap | prevent duplicate global and local counting | precedence control |
| competing bridge | create nontrivial local-versus-completion probability | A2b plus complete two-exit LTS |

### 5.1 Competing bridge

The bridge is

```text
s0 -- enter_local, rate 1 --> d_local
s0 -- complete,    rate 2 --> f_complete.
```

The exact probabilities follow from competing exponential hazards:

\[
\theta_g=0,
\qquad
\theta_\ell=\theta_b=\frac{1}{1+2}=\frac13,
\qquad
E[\tau]=\frac{1}{1+2}=\frac13.
\]

This small case is intentional. It isolates the estimand and stopping semantics
without pretending to represent a full production facility.

## 6. Results

### 6.1 Theory-obligation results

Both positive routes satisfy their matched obligations. The A2b case carries
the explicit request-closed proof flag. In the complete-LTS case,
`dlocal_ab` and `dlocal_cd` cannot reach `F`. Its plant graph contains six arcs,
whereas the stopped graph contains four, because arcs leaving already-hit local
states are removed only after stopping. This directly witnesses that
`D_local` need not be a plant terminal SCC.

The bypass control follows

```text
s_local_candidate -> s_bypass -> f_complete,
```

so the candidate is excluded from `D_local`. The precedence control begins in
a global state that also has local-candidate structure; it is recorded only as
`D_global`.

### 6.2 Exact and DES probabilities

| Case | Exact `(theta_g, theta_l, theta_b)` | DES `(theta_g, theta_l, theta_b)` | max error |
| --- | --- | --- | ---: |
| competing bridge | `(0, 0.3333333333333333, 0.3333333333333333)` | `(0, 0.33642578125, 0.33642578125)` | `0.0030924479166667` |
| global/local precedence | `(1, 0, 1)` | `(1, 0, 1)` | `0` |
| completion bypass | `(0, 0, 0)` | `(0, 0, 0)` | `0` |
| global positive | `(1, 0, 1)` | `(1, 0, 1)` | `0` |
| A2b local positive | `(0, 1, 1)` | `(0, 1, 1)` | `0` |
| complete-LTS local positive | `(0, 1, 1)` | `(0, 1, 1)` | `0` |

All 18 cells pass the frozen tolerance. The bridge produces 1378 local hits and
2718 completion hits in 4096 replications. Its empirical selected-bad
probability differs from `1/3` by `0.0030924479166667`, about one ninth of the
allowed simultaneous bound.

The exact/DES mean stopped times are also consistent with the case mechanics:
`1/3` versus `0.33568223553583404` for the bridge, `2` versus
`2.0179046383604264` for the two-stage bypass, and `0.5` versus
`0.5035233533037509` for the equal-rate first local hit in the multi-kernel
case. Time-zero classification witnesses have zero stopped time by definition.

### 6.3 Frozen claim tier

The predeclared ladder selects

```text
tier_a_dual_route_closure.
```

This means that both local-admission routes, both boundary controls, and the
same-target quantitative bridge support the scoped article thesis. It does not
mean that every case in the original 13-case G6-B bundle has been quantitatively
executed or that the original eight-dimension overlap gate has passed.

## 7. Discussion

### 7.1 Why a nonterminal bad hit is coherent

A stopping target is defined by the question being asked. Once the event
"verified irreversible local failure has occurred" is the target, later motion
of unrelated jobs is irrelevant to that first-hit estimand. Plant arcs remain
real; the stopped process simply ceases to follow them after the event. This is
the same distinction that separates event occurrence from physical stasis in
many competing-risk models.

### 7.2 Why the bypass case matters

The bypass case prevents a vacuous theory in which every local cycle is called
deadlock. It establishes the negative side of the rule: current structural
blocking is not enough when a completion path exists. The article's positive
claim is therefore paired with an explicit falsifier.

### 7.3 Why exact/DES agreement is useful but limited

Exact and DES share the same declared rates and target labels but execute the
probability calculation differently. Agreement is evidence that the target was
translated consistently into the linear solver and path simulator. It is not
proof of the A2b theorem, proof that the LTS is a faithful plant model, evidence
of rare-event efficiency, or external validation against production data.

### 7.4 Why universal case coverage is unnecessary

The A2b route gains a reusable theorem by imposing a stronger semantic
discipline. The complete-LTS route accepts a broader transition language but
only proves a property of the enumerated finite model. Requiring either method
to dominate the other on every case would erase their actual assumptions. A
logically coherent article instead states the method boundary, supplies a
matched positive witness, and retains counterexamples outside the boundary.

## 8. Limitations

1. The five reused sealed cases are constructive discovery and boundary
   evidence, not independent held-out confirmation.
2. The bridge is deliberately minimal. It demonstrates a nondegenerate
   probability and same-target implementation, not production-scale behavior.
3. A2b is sufficient, not necessary. Models violating A2b may still be safe or
   locally irreversible for other reasons.
4. Complete-LTS admission is valid only for a complete, nontruncated finite
   model with a complete transition registry.
5. The cases use positive exponential rates. Non-Markov durations require a
   declared phase-type expansion or a different quantitative method.
6. The study estimates no throughput, tardiness, WIP, recovery cost, control
   effectiveness, or rare-event efficiency.
7. The original 13-case G6-B overlap gate remains `OPEN_PENDING`; later G6-C,
   G6-D, and G6-E work is outside this article-core closure.
8. Retired evidence lacks eligible random-stream and metric-schema overlap for
   an independence claim. Exact/DES agreement is consequently described only
   as a within-case cross-check.
9. The external bibliography and venue-specific presentation remain editorial
   work. No citation is used here to upgrade the project-local theorem or case
   evidence.

## 9. Reproducibility and evidence boundary

The article scope is frozen in
`cases/article_core/article_scope_lock_v1.json`, self SHA-256
`86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660`.

The write-once evidence is in
`evidence/article_core/minimal_closure_v1/`. The manifest self SHA-256 is
`1693342ac470b72f9b813edccb772f85751045940a243f7abc9241877cab0c77`.
The full verification record is
`docs/verification/G6_B_MINIMAL_ARTICLE_CLOSURE_REPORT.md`.

The scope preserves the original sealed denominator, negative evidence, and
forbidden claim codes. A failed case cannot be replaced after outcomes are
observed, and the evidence root cannot be regenerated in place.

## 10. Conclusion

Local blocking can be treated coherently as a bad first-hit event without
calling it a plant terminal SCC. The key is not a universal detector, but a
typed admission rule: use the A2b theorem where request closure is proved, use
complete finite-LTS nonreachability where exhaustive model-specific evidence is
available, and refuse candidates that retain a completion bypass. A global
precedence rule keeps the target partition disjoint.

The predeclared six-case panel closes this logic in both directions. Matched
positive witnesses support the two admission routes, negative controls enforce
their boundaries, and a `1/3` competing-absorption bridge links the definitions
to exact and simulated first-hit probabilities. The resulting Tier A status is
a scoped constructive closure suitable for a self-consistent theory/method
article. Broader empirical confirmation remains a separate question.
