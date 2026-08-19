# Typed Local First-Hit Analysis of Capacity-Mediated Blocking in Finite Manufacturing Resource-Allocation Systems

**IEEE Transactions on Automation Science and Engineering**  
Regular Paper (double-anonymous manuscript; author identities omitted)  
Manuscript type: Regular Paper  
Primary methodology (suggested): Discrete-event / resource-allocation analysis  
Primary application (suggested): Intelligent / flexible manufacturing systems

---

## Abstract

Wait-for cycles and unmarked plant-net siphons do not, by themselves, stop an operational manufacturing cell: residual capacity or a completion bypass can still finish the batch, while a local interlock can already make some jobs incomplete. This paper treats local blocking as a first hit of a certified bad set in a stopped process. A local closed kernel is admitted by a request-closed argument or by a complete finite labelled-transition-system audit that batch completion is unreachable, and is refused if a shortest bypass exists. Diagnostic siphons apply only on a unit-capacity, residual-zero, one-hold-one-request wait-snapshot; otherwise the method returns a typed refusal. After a certified absorption partition, exact continuous-time first-hit probabilities and discrete-event replications share one stopping hash. On a three-job machine–AGV island that starts transient, the first local hit occurs at positive time (\(\theta^{\mathrm{L}}=0.537\), \(m=3.60\)); one extra AGV slot yields \(\theta^{\mathrm{B}}=0\). An independently hashed two-process S3PR embedding decides the fourth field of a four-field diagnostic; a declared AGV distortion refuses it. A finite-state supervisor on the same graph retains 56 of 64 states and also yields \(\theta^{\mathrm{B}}=0\). The increment is this checkable first-hit object, not a plant-net liveness theorem or a shop-floor controller.

*Abstract word count: 193.*

## Note to Practitioners

This work was motivated by a cell-control question: when two jobs hold a machine and an automated guided vehicle (AGV) and wait for each other, has the batch already failed, or can it still finish if a buffer slot or another unload remains? A cycle on the wait graph is not a reliable stop. Leftover capacity or a later bypass can still complete every job, and cutting the “obvious” edge can create a new interlock. The quantity computed here is the first time the cell enters a certified blocked set, not the event that the plant graph has no outgoing arc. If every move of a waiting job must use its current request, a local closed kernel is enough to conclude those jobs will never finish; otherwise the kernel is kept only after a complete finite state graph shows that batch completion is unreachable, and it is dropped if a bypass appears. Siphon language is used only when every core resource is unit capacity, fully occupied, and requested one-for-one; otherwise the method returns “not applicable” instead of installing a monitor. On a synthetic three-job island the cell runs and then locally stops; adding one AGV slot prevents that stop. Exact probabilities and simulations are compared only after they share the same stopping rule. The island is not factory data, the method is not a shop policy, and it does not replace a published Petri-net supervisor on a vendor cell. It is a pre-release audit of a finite digital twin.

*Note to Practitioners word count: 249.*

## Index Terms

Automated guided vehicles, deadlock, discrete-event systems, flexible manufacturing systems, Markov processes, Petri nets, resource allocation, supervisory control.

---

## Reader's Orientation and Notation

This section is written for a first reading. It locates the uncommon objects of the paper against the manufacturing cell under study and fixes a single notation for the remainder of the text. Table~0 is binding: a symbol is not reused for a second meaning.

### What is being modelled

An *intelligent manufacturing cell* here is a finite batch of jobs that share a finite pool of reusable resources—machines, buffers, and an automated guided vehicle (AGV). After a machine finishes service the job typically *keeps holding* that machine until an unload or a transporter is obtained (blocking after service, BAS). A job may request several resources at once (a conjunctive, or AND, demand) or any one of several options (a disjunctive, or OR, demand). The paper studies *capacity-mediated blocking*: a job cannot proceed because the units it needs are held by other unfinished jobs, not because a quality gate, a human approval, or a disabled controllable event is missing.

Three classical pictures of “deadlock” are *not* identified with the object computed here.

- A *wait-for cycle* is a directed cycle in the graph whose nodes are jobs or resources and whose edges mean “waits for.” Residual free units can make a cycle traversable, so a cycle need not stop the batch.
- A *siphon* of a plant Petri net is a place set that, once unmarked, stays unmarked. On S3PR/S4PR plant nets this is a standard liveness tool. It is used below only as a *diagnostic dual* of a wait-snapshot, and only on a unit-capacity subclass.
- A *terminal strongly connected component* (SCC) of the plant state graph is a set of states with no plant edge leaving it. A local interlock can already make some jobs incompletable while another job still moves, so the plant graph need not be terminal.

The object of the paper is a *first hit* of a certified bad set in a *stopped* process. The plant graph is left unchanged. After the declared failure or success set is entered, outgoing plant arcs are ignored for probability. That is why a local-hit state may still have plant successors: membership records that the failure event has occurred, not that the cell graph has died.

A *closed blocking core* is an auditable witness that a designated subset of jobs is capacity-blocked: every current request option of those jobs is short of a resource whose missing units are explained by holdings *inside* the same subset, and none of those jobs has an enabled transition. If the subset is all unfinished jobs, the core is *covering* and characterises global operational deadlock. If it is a proper subset, it is only a *local candidate* until a typed admission proof shows that those jobs can never complete, or a completion *bypass* (a path that finishes the batch anyway) refuses the candidate.

A *typed refusal* is an explicit “not applicable” with a reason (OR demand, AND demand, residual capacity, missing reachability witness, missing S4PR embedding, …). It is a designed output, not a failed run. The request-closed discipline used by the structural local-noncompletion theorem is labelled A2b: every progress of a waiting job must consume a currently feasible request alternative. If A2b cannot be proved, admission falls back to exhaustive search on the finite state graph.

### Binding notation


**Table 0**  
Symbols used once

| Symbol | Meaning |
| --- | --- |
| \(J,R\) | finite job set and resource set |
| \(\kappa(r)\) | capacity of resource \(r\) |
| \(\omega_s(j,r)\) | units of \(r\) held by job \(j\) in state \(s\) |
| \(\Omega_s(r)\) | occupancy of \(r\) |
| \(\alpha_s(r)=\kappa(r)-\Omega_s(r)\) | residual availability |
| \(\rho_s(j,v),\varrho_s(v)\) | hard reservation of token \(v\) by \(j\), and its sum |
| \(\mathcal{A}_s(j)\) | OR-of-AND family of capacity-ready alternatives of \(j\) |
| \(\nu_s(j,a,r)\) | units of \(r\) demanded by alternative \(a\) of \(j\) |
| \(\chi_s\) | \(1\) iff no timed event is currently scheduled |
| \(S^{\star}\) | stable states (after zero-time closure) |
| \(\mathcal{M}\) | an \(\mathrm{IMS}^{CW}\) model |
| \(\Sigma\) | declared transition registry of \(\mathcal{M}\) |
| \(\mathcal{G}=(X,x_0,\mathcal{E},\to)\) | reachable stable LTS of \(\mathcal{M}\) |
| \(\delta(x,e),\Gamma(u)\) | immediate fire; zero-time closure |
| \(\mathcal{N}=(P,\Theta,W^-,W^+,M_0)\) | 1-safe state-place net of Lemma 1 |
| \(K=(J_K,R_K,W_K,H_K)\) | one closed blocking core |
| \(\beta_K(j,a,r),\zeta_s(r)\) | kernel-held units charged to a witness; non-kernel fixed occupancy |
| \(X^{\ell}\) | non-global states that contain a local core (candidates) |
| \(F\) | all-batch completion |
| \(D^{\mathrm{G}},D^{\mathrm{L}}\) | global / admitted-local first-hit sets |
| \(D^{\dagger}=D^{\mathrm{G}}\cup D^{\mathrm{L}}\) | selected bad set |
| \(A^{\dagger}=D^{\dagger}\cup F\) | stopped target |
| \(X^{\circ}=X\setminus A^{\dagger}\) | candidate transient states |
| \(S^{\circ}\) | certified almost-sure transient domain |
| \(S^{\mathrm{p}}\) | states with a support path to \(A^{\dagger}\) |
| \(B^{\circ}\) | reverse basin of unselected closed SCCs |
| \(\Lambda^{\infty},\Lambda^{0}\) | leftover livelock / terminal SCC classes |
| \(\tau^{\mathrm{G}},\tau^{\mathrm{L}},\tau^{\mathrm{F}},\tau^{\dagger}\) | first-hit times of \(D^{\mathrm{G}}\), \(D^{\dagger}\), \(F\), \(A^{\dagger}\) |
| \(\theta^{\mathrm{G}},\theta^{\mathrm{L}},\theta^{\mathrm{B}}\) | first-hit probabilities of \(D^{\mathrm{G}}\), \(D^{\mathrm{L}}\), \(D^{\dagger}\) |
| \(Q,h,m\) | stopped generator, committor, mean absorption time |
| \(H^+\) | \(\{i\in S^{\circ}:h_i>0\}\) |
| \(\Phi\) | fundamental matrix \(-Q_{S^{\circ}S^{\circ}}^{-1}\) |
| \(\varepsilon,n_{\mathrm{s}}\) | Hoeffding tolerance; DES replication count |
| \(\eta(j),\varrho(j)\) | unique held / requested core resource in the siphon subclass |
| \(p_r,\Psi_K\) | wait-snapshot place of \(r\); candidate siphon |
| \(R^{\star},R^{\prec}\) | declared CRP resource set; key resources of an acquisition order |
| \(\mathsf{M}_1,\mathsf{M}_2,\mathsf{V}\) | island machine 1, machine 2, AGV |
| \(\mathsf{m},\mathsf{g},\mathsf{b},\mathsf{v},\mathsf{p}\) | Appendix C machine, transporter, buffer, reservation token, next station |

The generator \(Q\) is never a plant resource. The completion set \(F\) is never a buffer. Job names in examples are \(\mathsf{A},\mathsf{B},\mathsf{C}\) in roman sans-serif, distinct from sets \(A^{\dagger}\) and SCCs \(\mathcal{C}\).


---

## I. Introduction

Finite-capacity manufacturing cells allocate machines, buffers, and transporters to a finite set of jobs that hold resources after service (blocking after service) and may request several resources at once. A classical diagnosis of a stop is a directed cycle in a wait-for graph, a knot in a state-dependent blocking graph, or an empty siphon of a plant Petri net [1]–[6]. Those objects are inexpensive to state and, on the subclasses for which they were proved, they are correct. They are not interchangeable with an *operational* stop of an intelligent manufacturing system (IMS) model that records residual capacity, OR-of-AND requests, AGV occupancy, and a declared transition registry.

Three mismatches appear as soon as the model is operational rather than purely structural. First, a residual-feasible cycle is not a deadlock: a job can still acquire the residual unit and complete [4], [6]. Second, a local interlock among a subset of jobs can already make batch completion unreachable while another job continues—so the plant labelled transition system (LTS) still has outgoing arcs [7]. Calling that local interlock a terminal strongly connected component (SCC) is a category error. Third, a completion bypass—an enabled sequence that ignores the current request and finishes a kernel job after an outside release—means that the local cycle was never irreversible. Promoting it to a bad absorbing class falsifies the subsequent probability.

A fourth mismatch is linguistic. Empty-siphon control on S3PR/S4PR plant nets [1], [3], [8], [9] and critical-resource-place (CRP) characterizations of partial deadlock [10] are mature. They are not automatically certificates of the IMS operational state. A wait-snapshot dual exists only on a narrow unit-capacity subclass; outside that subclass the honest output is a typed refusal, not a monitor.

This paper therefore changes the *object* that is computed. Local blocking is treated as a first hit of a certified bad set \(D^{\mathrm{L}}\) (or of the covering global set \(D^{\mathrm{G}}\)) in a *stopped* process, not as a terminal SCC of the plant. Admission of a local kernel to \(D^{\mathrm{L}}\) is typed:

1. under CW1–CW10 and the request-closed discipline A2b, a local closed kernel makes every kernel job permanently incomplete, hence batch completion \(F\) is unreachable (Theorem 3);
2. if A2b cannot be verified, the same candidate is admitted only after a complete, untruncated LTS audit shows that \(F\) is unreachable from that state (Theorem 4), and is refused if a shortest completion bypass exists (Theorem 5).

After the absorption domain is certified—no unselected closed class, no truncated LTS—exact first-hit probabilities on the stopped continuous-time Markov chain (CTMC) and independent discrete-event (DES) replications share one stopping hash. Agreement inside a predeclared simultaneous Hoeffding band is a numerical check, not a proof of the theorem and not a claim of plant fidelity [11].

The experimental clothing is a new discovery panel with a distinct scope identifier. It is not a relabelling of a six-case constructive manuscript and not a historical replay of a failed CRP encoding. Six families are reported.

- *Island.* A three-job machine–AGV cell starts transient. The first local hit occurs at positive time (\(\theta^{\mathrm{L}}=0.537\), \(m=3.60\), \(\theta^{\mathrm{B}}=7/12\)). One extra AGV slot sends every sample path to completion (\(\theta^{\mathrm{B}}=0\), \(m=6.30\)). Six probability cells agree with DES at \(n_{\mathrm{s}}=65536\) inside tolerance \(7.35\times 10^{-3}\). A time-zero local-hit clothing of the same island (\(\theta^{\mathrm{L}}=1\), \(m=0\)) is retained as a boundary.
- *Baselines.* Ten plants are scored by a wait-for/SCC screen, a closed-core certificate, a siphon-or-refuse predicate, and LTS truth. Four plants agree with the diagnostic siphon; four refuse it for OR, AND, multi-capacity, or conjunctive AGV demand; false positives and false negatives are both zero.
- *Scale.* A tandem family enumerates twelve rows with at least \(10^3\) stable states and four with at least \(10^4\), and refuses three rows at \(10^5\) states or \(300\,\mathrm{s}\).
- *CRP diagnostic.* Proposition 4’s four fields are scored on six subjects without an embedding (field 4 refused; agreement zero) and on two new subjects with an independently hashed two-process S3PR embedding. The faithful embedding decides field 4; a declared AGV distortion refuses it. Neither row is a CRP theorem or a replay of [10].
- *Supervisor baseline.* On the same 64-state island LTS, a finite-state nonblocking supervisor [5], [15] retains 56 states, disables 14 controllable state-events, and yields supervised \(\theta^{\mathrm{B}}=0\).

The publishable increment is the checkable first-hit object and its typed admission/refusal rules. The paper does not claim a new siphon-control policy, a general IMS–S3PR isomorphism, a bit-polynomial reachability procedure, a shop-floor throughput gain, or priority over PDDP/CRP/monitor synthesis [3], [8]–[10].

Section II places the increment against Petri, RAS, knot, and probability baselines. Sections III–IX give the complete formal development: the capacity-aware closed-wait subclass, the finite LTS representation, the covering-core characterization of global operational deadlock, the wait-snapshot siphon dual, the two typed local-admission routes with full proofs, a chain-decomposable sufficient condition, and the stopped-process first-hit equations including invertibility and first-jump derivations. Section X reports the experimental families. Section XI records limitations. Section XII concludes. Family-specific exact thresholds (BIX1/BIX2) are proved in Appendix C so that the original derivation is not abbreviated out of the archival draft.

---

## II. Related Work

T-ASE asks that a Regular Paper compare methods and cite archival work from the last two years [12]. The comparison here is organized by the *object* each literature family computes, not by a priority slogan.

### A. Wait-For Cycles, Knots, and Sequential RAS

A directed wait-for cycle is the oldest operational picture of deadlock. In sequential single-unit resource allocation it is tightly connected to safety: Lawley and Reveliotis proved that SU-SAFE is NP-complete and isolated structural subclasses that eliminate deadlock-free unsafe states [4]. Palmer, Harper, and Knight characterized deadlock of open restricted queueing networks by a knot in a state-dependent blocking graph and exhibited 2-/3-server counterexamples to a weakly-connected-component shortcut [6]. Those results remain the correct baselines for a cycle/SCC *screen*. They do not treat residual capacity, OR-of-AND alternatives, and BAS hold-after-service as first-class IMS tokens, and a residual-feasible cycle is not an IMS deadlock. Family II below keeps the cycle/SCC column precisely so that this false-positive mode stays visible.

Banker’s-algorithm and ordered-avoidance tests are sufficient safety filters on sequential RAS. They are not theorems of the IMS operational model once AGV occupancy and reservations are tokens.

### B. Petri-Net Siphons, Monitors, and Finite-Capacity Configuration

Ezpeleta, Colom, and Martínez gave the S3PR liveness and siphon-control policy that still organizes the plant-net school [1]. Li and Zhou refined the construction with elementary siphons [2]. Chen and Li formulated maximally permissive monitor synthesis as a marking/place-covering problem (MCPP) whose optimum exists only when a monitor supervisor is expressible; full reachability-graph enumeration is exponential and MCPP is NP-hard [3]. Pang *et al.* gave sufficient liveness and resource-configuration conditions for finite-capacity S3PR after an ENS3PR transformation, with a worst-case SMS bound \(O(2^{N_p})\) [9]. None of these results is an IMS operational certificate: they assume a plant-net subclass, not BAS blocked-unload, AGV occupancy, or OR-of-AND acquisition. The present paper uses an empty siphon only as a *diagnostic dual* of a wait-snapshot net on the unit-capacity subclass IMS-SIP\(^1\) (Theorem 2) and refuses the dual outside that subclass.

### C. Partial Deadlock, MR2G/PDDP, and CRP

Lu, Chen, Hadjicostis, and Li characterized partial deadlock of bounded FMS Petri nets by a modified resource-requirement graph (MR2G) and a PDDP predicate, and synthesized control places iteratively [8, Def. 3, Th. 1]. Su *et al.*, in this Transactions, characterized partial deadlock of S4PR at a marking by a critical resource place (CRP) and delegated reachability of candidates to a structural backward algorithm (SBA) [10, Defs. 5–8, Ths. 1–4]. Those papers are the closest 2025–2026 comparators. They do not supply an IMS operational certificate, a typed bypass refusal, or a first-hit probability on a certified stopped process. CRP equations alone are not a reachable-prefix proof [10]. A four-field partial-bridge *rule* (reachability, local family, resource equality, declared S4PR/S3PR overlap) is stated as Proposition 4. Field 4 is true only with an independently hashed embedding. Section X-E reports that field 4 is decided on the definitional two-process unit S3PR of [1] and refused on a declared AGV distortion of the same net and on six subjects without an embedding. This is not a replay of a figure in [10], not SBA, and not a CRP iff. A historical implementation that used a global extractor in the presence of an unrelated job remains a negative witness; it does not refute [10].

Recorder-place and transformed-net reachability procedures [13], [14] decide legal firing sequences after a model transform. They are not used here as an IMS reachability engine; the operational LTS is enumerated directly and refused when truncated.

### D. Supervisory Control and Finite-State LES

Ramadge and Wonham formulated nonblocking supervisory control of discrete-event processes [15]. Nazeem and Reveliotis gave a practical maximally permissive liveness-enforcing supervisor for complex RAS via a boundary-unsafe-state representation [5]. Those constructions remain the right *finite-state supervisor* baselines. Section X-F reports an explicit-graph Ramadge–Wonham supervisor on the same island LTS as a baseline: synthesis is polynomial in \(\lvert X\rvert\); the compact input remains at least NP-hard; the construction is not a risk-budget supervisor and not maximally permissive in the MCPP sense [3]. The centre of this paper remains a typed first-hit set, not a supremal controllable sublanguage and not a compact monitor.

### E. Absorbing Markov Models

Narahari, Viswanadham, and Krishna Prasad computed mean time to deadlock and absorption probabilities on finite manufacturing Markov models [11]. The linear algebra is classical. The modelling obligation that is easy to miss—and that this paper enforces—is that the absorbing classes must be the *same* certified first-hit sets used by the theorem, and that an unselected closed class makes the committor undefined. Exact/DES agreement on that shared target is a check, not a new CTMC theorem.

### F. Positioning Sentence

Table I records the five-axis difference. The paper adds a *checkable object* (typed \(D^{\mathrm{L}}/D^{\mathrm{G}}/F\) with a bypass refusal and a certified absorption domain). It does not add a new siphon, a new CRP equation, or a new polynomial reachability algorithm.

**Table I**  
Difference of computed objects (not a priority ranking)

| Family | Object they compute | Assumption not inherited here | Checkable addition |
| --- | --- | --- | --- |
| Cycle / SCC / knot [4], [6] | directed cycle or knot | residual, OR-of-AND, BAS | closed core; residual cycle \(\neq\) deadlock |
| S3PR siphon / MCPP [1], [3] | empty siphon; monitor cover | plant S3PR; compact monitor | wait-snapshot dual on IMS-SIP\(^1\); typed refusal |
| Finite-capacity S3PR [9] | sufficient marking inequalities | exact reachable iff threshold | none as a main theorem |
| PDDP / MR2G [8] | local marking deadlock | local cycle \(\Rightarrow\) irreversible failure | A2b or complete-LTS; bypass refusal |
| S4PR CRP [10] | CRP iff partial deadlock, then SBA | S4PR embedding of [10]’s running example; CRP set \(=\) local kernel | four-field rule; field 4 decided on the S3PR core of [1]; no SBA; not CRP iff |
| Finite-state LES / RW [5], [15] | supremal nonblocking; boundary-unsafe LES | compact input; MCPP existence | explicit-graph baseline on the island LTS |
| Absorbing CTMC [11] | \(\theta\), mean time | almost-sure hit of a declared \(D^{\dagger}/F\) | certified \(S^{\circ}\); same-target DES hash |

---

## III. Capacity-Aware Closed-Wait Semantics

All theorems below are stated on a restricted finite subclass \(\mathrm{IMS}^{CW}\) (capacity-aware closed wait), already located for a first reading in the orientation section. They do not cover unrestricted IMS models, classical S3PR structural equivalence, soft reservations, non-Markov timing, infinite arrivals, failures, preemption, or online job insertion. Symbols follow Table 0 and are not reused.

### A. Structural Hypotheses CW1–CW10

- **CW1 (Finiteness).** The job set \(J\), resource set \(R\), capacities \(\kappa(r)\in\mathbb{Z}_{>0}\), route stages, hard-reservation tokens, and event templates are finite.
- **CW2 (Closure normalization).** Every main statement is made on the set \(S^{\star}\) of stable states. After each non-zero-time event a zero-time closure is executed and terminates. If the closure is non-confluent, all stable successors are retained as a set.
- **CW3 (Capacity conservation).** For a physical resource, \(\Omega_s(r)=\sum_j \omega_s(j,r)\le\kappa(r)\). For a hard-reservation token \(v\), \(\varrho_s(v)=\sum_j \rho_s(j,v)\le\kappa(v)\). Soft reservations are excluded from the completeness theorems.
- **CW4 (Finite capacity-ready alternatives).** For each unfinished job \(j\) at \(s\in S^{\star}\), every currently guard-ready direct progress is written as a finite OR-of-AND family \(\mathcal{A}_s(j)=\{a_1,\ldots,a_m\}\). Each alternative \(a\) is a demand vector \(\nu_s(j,a,r)\in\mathbb{N}\). Non-capacity guards that are not yet true do not enter \(\mathcal{A}_s(j)\). Every currently enabled timed or transport completion enters as an *empty* demand alternative.
- **CW5 (Atomic acquisition).** An acquisition/progress event may fire only if some alternative \(a\) satisfies \(\alpha_s(r)\ge\nu_s(j,a,r)\) for every \(r\), simultaneously. Partial acquisition is forbidden.
- **CW6 (BAS/AGV hold).** A blocked-after-service holder, a blocked unload, or a committed AGV does not release its resource until a successful acquire/unload/handoff/leave or a designated completion-release.
- **CW7 (Autonomous-release decidability).** For every holding it is decidable whether a release exists that does not require a new acquisition. Witness capacity used by a certificate must be explained by a non-autonomous holding or a hard reservation.
- **CW8 (Event taxonomy).** Non-zero-time events at a stable state fall into four classes: timed/transport completion; acquire/dispatch/reservation/transport choice; unload/handoff/release; completion/marking. Zero-time events occur only inside the closure.
- **CW9 (First-paper exclusions).** No device failure, preemption, dynamic insertion, infinite exogenous arrival, or soft-reservation oversell.
- **CW10 (Policy stall excluded).** A stall created by disabling controllable events is not operational deadlock. A calendar-empty *terminal-block interpretation* is a separate boundary and is not mixed into a structural certificate. The flag \(\chi_s\in\{0,1\}\) records only whether a timed event is currently scheduled (\(\chi_s=1\) means none is); it is not synonymous with that interpretation.

These are hypotheses. If any fails, the implementation returns a structured refusal.

### B. Availability and Direct Progress

Write \(\alpha_s(r)\) from CW3. Alternative \(a\) is capacity-feasible at \(s\) if and only if \(\alpha_s(r)\ge\nu_s(j,a,r)\) for all \(r\). If \(j\) is complete, \(\mathcal{A}_s(j)=\emptyset\). If the next step is an enabled timed completion, a pure completion mark, or a release that needs no new capacity, the corresponding alternative has the zero demand vector. If \(j\) is blocked after service or blocked on unload, \(\mathcal{A}_s(j)\) contains every currently guard-ready unload, handoff, output-buffer entry, AGV claim, or reservation redeem.

A *capacity-gap witness* for \((j,a)\) is a resource \(r\) with \(\nu_s(j,a,r)>\alpha_s(r)\). An empty demand has no capacity-gap witness.

### C. Request-Closed Discipline A2b

A2b is used *only* for the structural local-noncompletion theorem. For every unfinished job with uncleared requests, every transition that would change that job’s mode, holdings, requests, or completion consumes at least one currently feasible alternative of \(\mathcal{A}_s(j)\). There is no same-mode bypass that depends on an outside resource, a guard, or an intermediate mode. If A2b cannot be proved statically, the complete-LTS route of Section VII-C must be used.

Probability constructions add **CW11**: the stable LTS is complete and untruncated, and a frozen positive rate manifest is supplied. Scientific execution re-enumerates the LTS from the same model, initial stable state, and registry, and requires state signatures and plant arcs to match.

---

## IV. Finite LTS and Reachability-Net Representation

**Lemma 1 (Representation; Theorem P1).**  
Let \(\mathcal{M}\) be any \(\mathrm{IMS}^{CW}\) model and \(s_0\in S^{\star}\) an initial stable state. There exists a finite closure-normalized LTS
\[
\mathcal{G}=(X,x_0,\mathcal{E},\to)
\]
and a 1-safe bounded Petri net \(\mathcal{N}=(P,\Theta,W^-,W^+,M_0)\) such that the reachable stable states \(X\) are in bijection with \(\mathcal{R}(\mathcal{N},M_0)\), and every LTS edge corresponds to exactly one Petri transition.

This is a representation lemma, not an S3PR structural equivalence and not a siphon theorem.

*Construction.* By CW1–CW3 every job stage, blocking mode, holding, reservation, and pending-free configuration is taken from a finite set. Let \(X\) be the set of stable states reachable from \(s_0\) after CW2 closure. Then \(X\) is finite. For \(x,y\in X\) and a non-zero-time event \(e\), draw an LTS edge \(x\xrightarrow{e} y\) whenever there is an immediate successor \(u=\delta(x,e)\) with \(y\in\Gamma(u)\). If the closure is multi-valued, one edge is drawn for each \(y\in\Gamma(u)\).

Build \(\mathcal{N}\) as follows: one place \(p_x\) for each \(x\in X\); one transition \(\theta_b\in\Theta\) for each LTS edge \(b=(x,e,y)\); \(W^-(p_x,\theta_b)=1\), \(W^+(\theta_b,p_y)=1\), and all other arc weights zero; \(M_0(p_{s_0})=1\) and \(M_0(p_x)=0\) otherwise. Write \(\phi(x)\) for the marking with a single token on \(p_x\).

*Proof of finiteness.* \(X\) is a subset of a finite configuration space. Edges are generated by a finite event template, so \(\mathcal{N}\) is finite.

*Proof of 1-safety.* \(M_0\) has one token. Every transition consumes exactly one state-place token and produces exactly one state-place token. By induction on the firing sequence every reachable marking has total token count one and every place is 0-1. Hence \(\mathcal{N}\) is 1-safe and bounded.

*Proof of forward path preservation.* For the empty path, \(x=s_0\) and \(\phi(x)=M_0\). If a path to \(x\) corresponds to \(\phi(x)\) and \(x\xrightarrow{e} y\) exists, the construction supplies \(\theta_b\) with unique input \(p_x\). That transition is enabled under \(\phi(x)\) and yields \(\phi(y)\).

*Proof of backward path preservation.* The empty firing sequence is \(M_0=\phi(s_0)\). If a reachable marking is \(\phi(x)\), every enabled transition in \(\Theta\) has input \(p_x\) and therefore comes from some LTS edge \(x\xrightarrow{e} y\). Firing it yields \(\phi(y)\).

*Proof of bijection.* \(\phi\) is injective by construction. Forward and backward preservation show that every LTS-reachable state is Petri-reachable and every Petri-reachable marking equals some \(\phi(x)\). \(\square\)

Lemma 1 uses only CW1–CW3 and CW2. It does not use S3PR hypotheses. If infinite arrivals, unbounded soft oversell, or a nonterminating closure are added, \(X\) may be infinite or undefined, and the lemma is outside its scope.

---

## V. Closed Blocking Cores and Global Operational Deadlock

### A. Closed Blocking Core

**Definition 1 (Closed blocking core).**  
At \(s\in S^{\star}\), a tuple \(K=(J_K,R_K,W_K,H_K)\) is a *closed blocking core* if and only if all five conditions hold independently.

1. *Nonempty unfinished.* \(J_K\neq\emptyset\) and every \(j\in J_K\) is unfinished.
2. *Every alternative blocked.* For every \(j\in J_K\) and every \(a\in\mathcal{A}_s(j)\) there is a record \((j,a,r)\in W_K\) with \(r\in R_K\) a capacity-gap witness of \(a\).
3. *Gap explanation.* For every witness \((j,a,r)\), writing \(\beta_K(j,a,r)\) for the sum of non-autonomous kernel holdings recorded in \(H_K\) for that witness,
   \[
   \nu_s(j,a,r)>\kappa(r)-\beta_K(j,a,r)-\zeta_s(r).
   \]
   When \(K\) is used as a *covering* global certificate, \(\zeta_s(r)=0\). The same holder may appear in several witness records; each inequality is audited only with its own \(\beta_K(j,a,r)\).
4. *Release dependence.* Every holding recorded in \(H_K\) has no legal release/unload/handoff that frees the corresponding capacity without firing a capacity-ready alternative already blocked by condition 2.
5. *At least one genuine waiter.* Some \(j\in J_K\) has \(\mathcal{A}_s(j)\neq\emptyset\) and is waiting, blocked after service, blocked on unload, waiting for transport, or waiting to redeem a hard reservation.

\(K\) *covers* \(s\) if and only if \(J_K\) equals the set of all unfinished jobs of \(s\) that are not calendar-empty terminal-boundary jobs. Definition 1 does *not* take “no successor” as a hypothesis, so the subsequent theorem is not tautological.

**Definition 2 (Capacity-mediated global operational deadlock).**  
A stable state \(s\) is a capacity-mediated global operational deadlock if and only if (i) \(s\) is a general global operational deadlock (no admissible successor to a different stable state); (ii) \(s\) is not a policy stall, calendar-empty terminal block, permanent non-resource guard, permanent missing synchronization, or other unmodelled external boundary; (iii) every covered unfinished job has nonempty capacity-ready \(\mathcal{A}_s(j)\); (iv) every currently enabled timed/transport completion has entered \(\mathcal{A}_s(j)\) as an empty demand, hence no such completion is enabled at \(s\).

### B. Equivalence

**Theorem 1 (Covering core \(\Leftrightarrow\) capacity-mediated global deadlock; P2).**  
In \(\mathrm{IMS}^{CW}\), a stable state \(s\) is a capacity-mediated global operational deadlock if and only if \(s\) admits a covering closed blocking core.

*Proof of \(\Rightarrow\).* Let \(s\) be a capacity-mediated global operational deadlock and let \(U_s\) be the set of unfinished non-terminal-boundary jobs. Then \(U_s\neq\emptyset\), every covered blocked job has nonempty capacity-ready \(\mathcal{A}_s(j)\), and at least one job is waiting or blocked. Set \(J_K=U_s\).

Fix \(j\in J_K\) and \(a\in\mathcal{A}_s(j)\). If \(a\) had no capacity-gap witness, then by the capacity-ready definition all non-capacity guards would hold, by CW5 the alternative would be capacity-feasible, and by CW8 the corresponding acquire/progress/release/completion event would be in the taxonomy; firing it and applying CW2 would produce a stable successor, contradicting global operational deadlock. Hence every alternative has at least one witness. Collect all such resources into \(R_K\) and all triples into \(W_K\).

For gap explanation: \(\alpha_s(r)<\nu_s(j,a,r)\) means that occupancy or hard reservation already saturates \(r\). Any unfinished outside holder of that shortage would belong to \(U_s=J_K\), a contradiction. A completed job cannot hold a machine, buffer, AGV, or reservation token. An environmental occupancy of calendar-empty terminal-block type is excluded by the theorem’s premise. Therefore, when \(K\) covers a global deadlock, the shortage is explained by kernel holdings or hard reservations. Choose enough non-autonomous kernel holdings to form \(H_K\) so that condition 3 holds.

For release dependence: if a holder used to explain a witness could release that resource without progressing a blocked alternative, that release would be guard-ready and would enter \(\mathcal{A}_s(j_h)\) (as an empty demand if no new capacity is needed). CW8 and CW2 would produce a stable successor, contradicting deadlock. Hence those holdings may be chosen non-autonomous, and condition 4 holds.

Conditions 1–5 are therefore satisfied, and \(K\) covers \(s\).

*Proof of \(\Leftarrow\).* Let \(K\) be a covering closed blocking core. We show that \(s\) has no admissible successor, by the CW8 taxonomy.

1. *Acquire/dispatch/reservation/transport choice.* If the non-capacity guards of such an event hold, it corresponds to some unfinished job \(j\) and some capacity-ready alternative \(a\). Coverage gives \(j\in J_K\). Condition 2 supplies a capacity-gap witness, so CW5 forbids the event. If the guards do not hold, the event is not currently admissible.
2. *Unload/handoff/release.* If the event is legal for an unfinished job it is a direct-progress alternative. If it needs no new resource it is an empty demand, so condition 2 cannot hold unless the event is not actually enabled; if it needs an output buffer, a handoff slot, an AGV, or a reservation redeem, condition 2 supplies a witness and the event cannot fire. If it claimed to free certificate-explaining capacity without depending on a blocked alternative, it would also violate condition 4. Completed jobs hold nothing. External terminal blocks are excluded.
3. *Timed/transport completion.* Every currently enabled completion is an empty-demand alternative by CW4. An empty demand has no capacity-gap witness, contradicting condition 2. Hence no such completion is enabled. A completion whose clock has not matured is not currently admissible. If completion still requires a blocked unload, CW6 says the holder is not released, and the subsequent unblock is again a capacity-ready alternative, already blocked.
4. *Completion/marking.* If a job can complete and release every resource, its alternative is empty or capacity-feasible, contradicting condition 2. If every job is already complete, conditions 1 and coverage fail.
5. *Zero-time closure.* \(s\in S^{\star}\), so no zero-time event is enabled. Closures after non-zero-time events are already accounted for in (1)–(4).

Thus there is no admissible successor to a different stable state. Coverage and condition 5 give incompleteness and a genuine waiter. Conditions 2 and Definition 1 give that every covered block is a capacity gap on a capacity-ready alternative, not a permanent non-resource guard, missing synchronization, policy stall, or calendar-empty terminal block. Therefore \(s\) is a capacity-mediated global operational deadlock. \(\square\)

**Corollary 1 (P2a).**  
If \(s\) admits a covering closed blocking core, it admits an inclusion-minimal one. The partial order is componentwise inclusion of \(J_K,R_K,W_K,H_K\). Finiteness of \(J,R\) and of the witness set supplies a minimal element. Inclusion-minimality is not uniqueness, not minimum cardinality, and not minimum capacity increment.

**Corollary 2 (P2b; unit one-hold-one-request).**  
In the additional subclass where every key resource has capacity one, every blocked job holds exactly one key resource and requests exactly one key resource, there is no alternate route, no split hard reservation, no residual, and a holder releases its current resource only after acquiring the requested one: (i) every terminal SCC \(\mathcal{C}\) of the resource wait-for digraph defines a local closed core \(K_{\mathcal{C}}\) whose jobs are exactly the holders in \(\mathcal{C}\); conversely every inclusion-minimal local closed core induces exactly one terminal SCC; if every out-degree is one, that SCC contains a simple directed cycle; (ii) if some \(K_{\mathcal{C}}\) covers every unfinished job, Theorem 1 yields a capacity-mediated global deadlock.

*Proof of Corollary 2.* Each blocked alternative has a single requested resource, and a capacity gap means that resource is held by a kernel job, so each blocked job has a wait-for edge to a holder. If \(\mathcal{C}\) is a terminal SCC, every requested holder remains in \(\mathcal{C}\) and there is no outgoing edge, so \(K_{\mathcal{C}}\) is a local closed core. Conversely, if \(K\) is inclusion-minimal, the induced wait-for graph has out-degree one and all edges stay inside \(K\). If it contained several terminal SCCs or a predecessor outside a terminal SCC, deleting the predecessor or retaining one terminal SCC would preserve closed blocking, contradicting inclusion-minimality. Coverage lifts the local statement to the global one. The corollary does not apply to multi-capacity, multi-request, OR-of-AND, AGV/reservation splits, or residual capacity. \(\square\)

---

## VI. Wait-Snapshot Siphon Dual

**Definition 3 (IMS-SIP\(^1\)).**  
A local core \(K\) at a reachable stable state \(s\) lies in IMS-SIP\(^1\) when: a reachability witness is attached (\(s\) itself may have the empty prefix); \(K\) is inclusion-minimal; every core resource or hard-reservation token has unit capacity and residual zero; every core job holds exactly one core resource \(\eta(j)\) and has exactly one current alternative, which requests exactly one unit of a core resource \(\varrho(j)\); there is no OR, no conjunctive AND, no soft reservation, no external guard, no hidden release, and no release-affecting non-confluent closure. An AGV or hard-reservation token may enter only as an ordinary unit resource.

The implementation checks the mechanical hypotheses (witness, minimality, stability, unit capacity, one-hold-one-request, no OR/AND, residual marking). Closed-world completeness, absence of hidden releases, satisfied guards, and closure semantics remain proof obligations on the registry. The check is not a plant/S3PR bisimulation.

*Wait-snapshot net.* Places \(P_K=\{p_r\mid r\in R_K\}\); marking \(M_s(p_r)=\kappa(r)-\Omega_s(r)\); for each \(j\in J_K\) a transition \(t_j\) with \(W^-(t_j)=\{p_{\varrho(j)}\}\) and \(W^+(t_j)=\{p_{\eta(j)}\}\). The transition \(t_j\) is *not* an IMS event; it is the diagnostic projection “the current resource can be freed only after the requested resource is obtained.” This net is distinct from the one-place-per-state net of Lemma 1.

**Theorem 2 (P2c).**  
At a reachable stable IMS-SIP\(^1\) state, inclusion-minimal local closed cores are in bijection with inclusion-minimal empty siphons of the wait-snapshot net.

*Proof of \(\Rightarrow\).* Let \(\Psi_K=\{p_r\mid r\in R_K\}\). Unit capacity and residual zero imply that \(\Psi_K\) is empty under \(M_s\). Every transition that outputs into \(p_{\eta(j)}\) is \(t_j\), whose unique input \(p_{\varrho(j)}\) still lies in \(\Psi_K\). Hence \(\bullet\Psi_K\subseteq\Psi_K\bullet\), so \(\Psi_K\) is an ordinary siphon. If a proper subset were an empty siphon, the one-hold-one-request semantics would recover a proper subcore, contradicting inclusion-minimality of \(K\).

*Proof of \(\Leftarrow\).* Let \(\Psi\) be an inclusion-minimal empty siphon and \(R_{\Psi}=\{r\midp_r\in\Psi\}\). Emptiness and unit capacity imply that each \(r\in R_{\Psi}\) is held by exactly one core job. The siphon condition says that every holder transition that outputs into \(R_{\Psi}\) requests, before that release, a resource still in \(R_{\Psi}\). One-hold-one-request and the absence of alternatives therefore recover a local closed core. If that core were not inclusion-minimal, its proper subcore would yield a proper empty siphon, a contradiction. \(\square\)

Theorem 2 does not apply to conjunctive requests, OR routes, multi-capacity residuals, soft reservations, control-only/approval-only siphons, or any Petri auxiliary place that lacks a job hold–request evidence edge.

---

## VII. Typed Local First-Hit

### A. Local Kernel and \(D^{\mathrm{L}}\)

A *local* closed blocking kernel is a closed core in the sense of Definition 1 that need not cover every unfinished job. Write \(X^{\ell}\) for the set of non-global states that contain at least one inclusion-minimal local core. A state of \(X^{\ell}\) is only a *candidate*: it proves present blocking, not future noncompletion.

**Definition 4 (\(F\), \(D^{\mathrm{G}}\), \(D^{\mathrm{L}}\)).**  
\(s\in F\) if and only if every job is complete, no resource is held, and no request remains. \(s\in D^{\mathrm{G}}\) if and only if \(s\) satisfies Definition 2. \(s\in D^{\mathrm{L}}\) if and only if \(s\notin D^{\mathrm{G}}\), \(s\in X^{\ell}\), and either Theorem 3 applies or Theorem 4 applies. Classification precedence is
\[
F \;\text{excluded first},\quad\text{then }D^{\mathrm{G}},\quad\text{then }D^{\mathrm{L}}.
\]
Thus the three sets are pairwise disjoint. Precedence is a versioned estimand convention, not a physical law.

\(D^{\mathrm{L}}\) may have outgoing *plant* arcs, because outside jobs may still move. Membership says that the declared failure event has occurred, not that the plant graph is terminal. The plant process is unchanged; the *stopped* process deletes outgoing arcs only after a selected target has been hit.

### B. Request-Closed Noncompletion

**Theorem 3 (request-closed local noncompletion).**  
Assume CW1–CW10 and A2b. If a stable state \(s\) contains a local closed kernel \(K=(J_K,R_K,W_K,H_K)\), then on every plant path from \(s\) every job in \(J_K\) remains incomplete and the requests present at the hit remain unsatisfiable. Consequently \(F\) is unreachable from \(s\).

*Proof.* The argument is the capacity invariant, not identity of a serialized certificate.

1. By Definition 1(5) and the local-kernel reading of “no enabled transition for \(J_K\)”, no kernel job is enabled at \(s\). By the complete-registry hypothesis this is not an omitted-transition false negative.
2. By per-job ownership (the A2 reading of CW8), an outside transition changes only its own job’s mode, holdings, requests, and completion. It cannot complete a job of \(J_K\) and cannot rewrite a kernel job’s request vector.
3. By CW6, CW7, CW9 (no preemption, no failure, no exogenous release) and the completion convention that a completed job holds nothing, a witness unit held by \(J_K\) at the hit is not released by an outside event.
4. *Capacity invariant.* For each witness resource \(r\), write \(L_s(r)\) for the number of units of \(r\) locked by \(J_K\) at the hit. Then \(L\) is nonincreasing along any path (step 3), and
   \[
   \alpha_{s'}(r)\;\le\;\kappa(r)-L_{s'}(r)\;\le\;\kappa(r)-L_s(r)
   \]
   at every successor \(s'\). Outside jobs may occupy and later release only the residual that was already free at the hit; they cannot raise availability of those witness units above the hit-state bound.
5. Definition 1(2)–(3) says that every alternative of every kernel job is short of at least one witness resource by more than that residual. Combined with step 4, no such alternative ever becomes capacity-feasible.
6. A2b excludes a progress, release, or completion transition that ignores the unresolved requests. Therefore no kernel job ever acquires a feasible alternative or fires a progress/release/completion transition.
7. \(F\) requires every job to complete, in particular every job of \(J_K\). This contradicts step 6.

Hence \(F\) is unreachable. The forward invariant is kernel-job noncompletion and request blockedness. The certificate extractor need not return a literally identical record at later states: outside jobs may occupy residual, so a syntactic “all current holders lie in \(J_K\)” test can flicker; state identifiers, prefixes, and residual vectors may change. \(\square\)

A2b is sufficient, not necessary. The theorem does not say that every local deadlock arises from A2b.

### C. Complete-LTS Fallback and Bypass Refusal

**Theorem 4 (Model-specific semantic admission).**  
Suppose A2b is not established. Let \(\mathcal{G}\) be the complete, untruncated LTS of Lemma 1 generated from the same registry. A candidate \(x\in X^{\ell}\) may be placed in \(D^{\mathrm{L}}\) if and only if no directed plant path of \(\mathcal{G}\) from \(x\) to any state of \(F\) exists.

*Proof.* If such a path exists, then from \(x\) a finite event sequence reaches batch completion, so treating \(x\) as an irreversible bad hit is unsound for this model: the first-hit probability of “selected bad before \(F\)” would charge a path that in fact reaches \(F\). Conversely, if the LTS is complete and no path to \(F\) exists, every trajectory from \(x\) remains forever outside \(F\). Using \(x\) as a stopping set of the stopped process is then sound *for that enumerated model*. The argument is exhaustive reachability on a finite graph. It does not create a structural theorem for unenumerated or infinite models. \(\square\)

**Theorem 5 (Bypass refusal).**  
If \(\mathcal{G}\) contains a path from the candidate to a state of \(F\), the candidate is refused, the shortest event prefix is retained as a counterexample, and the candidate is not entered into \(D^{\mathrm{L}}\).

The two routes are alternatives, not competitors required to cover the same plant.

| Route | What it proves | Required boundary | Correct failure |
| --- | --- | --- | --- |
| A2b (Theorem 3) | structural noncompletion of \(J_K\) | per-job semantics and no request-independent bypass | refuse A2b; use Theorem 4 if the LTS is complete |
| Complete LTS (Theorem 4) | \(F\)-nonreachability in one finite model | complete untruncated registry | return the path (Theorem 5) or a structural refusal |

### D. All-Minimal Enumeration

**Proposition 1 (Soundness).**  
Every local certificate returned by cardinality-increasing blocked-job enumeration followed by inclusion-minimal resource-witness filtering satisfies Definition 1.

**Proposition 2 (Completeness).**  
If \(s\) contains an inclusion-minimal local closed kernel, the same enumeration returns it. Finiteness is CW1.

**Proposition 3 (Order independence).**  
Truth values do not depend on first-hit enumeration order. Output order may be canonicalized; a bridge judgment must quantify the entire minimal-kernel family.

**Proposition 4 (CRP partial bridge).**  
Given a frozen target and a declared resource set \(R^{\star}\), partial-bridge *agreement* is true only if all four hold independently: (i) the target is reachable in the frozen stable LTS; (ii) the local family at that target is nonempty; (iii) \(\lvert\{K:R_K=R^{\star}\}\rvert\ge 1\); (iv) the source profile is a declared S4PR/S3PR overlap with an independent embedding hash. A global covering certificate must not replace (ii)–(iii). Multiplicity is reported when several kernels match; a zero match is reported as zero, not as a first-certificate artefact. Field (i) is decided by this paper’s BFS, not by a firing sequence copied from the source paper. Field (iv) is decided on one embedded subject and refused on the remaining subjects (Section X-E).

---

## VIII. Chain-Decomposable Acquisition Order

The following sufficient condition is part of the original completeness chain. It is *not* a local-first-hit novelty and is not used to claim a general manufacturing deadlock-prevention policy.

**Definition 5 (Global acquisition order).**  
A strict partial order \(<\) on a key-resource set \(R^{\prec}\) *covers* every machine, buffer, AGV, and hard-reservation token that can appear as a blocked holder or a demand witness. The model satisfies acquisition precedence if whenever a job holds \(r\) and then requests or hard-reserves \(r'\), one has \(r<r'\). BAS holders, AGV holders, and reservation redeems obey the same order.

**Definition 6 (Chain-decomposable core).**  
A closed core \(K\) is chain-decomposable if for every witness \((j,a,r)\in W_K\) there is a holder record \((j_h,r,q,j,a)\in H_K\) in which \(r\) itself is a non-autonomous key holding of \(j_h\), and that holder has its *own* blocked capacity-ready alternative with a next witness \(r'\) satisfying \(r<r'\). Aggregate capacity gaps that cannot be charged to a holder-dependency chain lie outside the theorem.

**Lemma 2 (P3-L1).**  
If \(K\) is a nonempty covering closed core and is chain-decomposable, then from any witness one can build an infinite resource sequence \(r_1,r_2,\ldots\) with \(r_n<r_{n+1}\) at every step.

*Proof.* Start from any witness \((j_0,a_0,r_1)\). Chain-decomposability supplies a holder \(j_1\) of \(r_1\) together with that holder’s own next witness \(r_2\), and acquisition precedence gives \(r_1<r_2\). Repeat. The core is finite but the selection may be repeated indefinitely, producing an infinite strictly ascending chain. \(\square\)

**Theorem 6 (P3).**  
If every covering closed core of an \(\mathrm{IMS}^{CW}\) model is chain-decomposable and a global acquisition strict order exists, then there is no capacity-mediated global operational deadlock in the sense of Theorem 1.

The conclusion does not imply standard nonblocking, livelock-freeness, policy-stall-freeness, or almost-sure completion.

*Proof.* Suppose, for a contradiction, that a capacity-mediated global operational deadlock exists. Theorem 1 supplies a covering closed core \(K\). By hypothesis \(K\) is chain-decomposable. Lemma 2 yields an infinite chain \(r_1<r_2<r_3<\cdots\) inside the finite set \(R^{\prec}\). Hence there exist \(m<n\) with \(r_m=r_n\). Transitivity of \(<\) gives \(r_m<r_m\), contradicting irreflexivity. Therefore no covering closed core exists, and Theorem 1 yields the claim. \(\square\)

If the order is built only on a machine projection and omits an AGV, buffer, or reservation inversion, Theorem 6 does not apply. If a multi-capacity pool cannot be charged to a holder chain, it does not apply. Family I contains a non-chain covering core so that “not applicable” is returned rather than “deadlock-free.” Exact reachable thresholds for two concrete families (BIX1-SAT, BIX2-PERSIST) are proved in Appendix C; they are not main T-ASE novelties.

---

## IX. Stopped First-Hit Process and Exact Equations

### A. First-Hit Times and Inclusion

On the underlying CTMC \((X_t)_{t\ge 0}\) define
\begin{align*}
\tau^{\mathrm{G}}&=\inf\{t\ge 0:X_t\in D^{\mathrm{G}}\},\\
\tau^{\mathrm{L}}&=\inf\{t\ge 0:X_t\in D^{\mathrm{G}}\cup D^{\mathrm{L}}\},\\
\tau^{\mathrm{F}}&=\inf\{t\ge 0:X_t\in F\}.
\end{align*}
The component estimands used in the experiments are
\[
\theta^{\mathrm{G}}=\mathbb{P}(X_\tau\in D^{\mathrm{G}}),\quad
\theta^{\mathrm{L}}=\mathbb{P}(X_\tau\in D^{\mathrm{L}}),\quad
\theta^{\mathrm{B}}=\theta^{\mathrm{G}}+\theta^{\mathrm{L}},
\]
where \(\tau=\inf\{t\ge 0:X_t\in A^{\dagger}\}\) and
\[
A^{\dagger}=D^{\mathrm{G}}\cup D^{\mathrm{L}}\cup F.
\]
They are evaluated under the same three-way first-hit partition: the local component is *not* computed by allowing paths to pass through \(D^{\mathrm{G}}\).

Because \(D^{\mathrm{G}}\subseteq D^{\mathrm{G}}\cup D^{\mathrm{L}}\), one has the event inclusion \(\{\tau^{\mathrm{G}}<\tau^{\mathrm{F}}\}\subseteq\{\tau^{\mathrm{L}}<\tau^{\mathrm{F}}\}\), hence \(\theta^{\mathrm{G}}\le\theta^{\mathrm{L}}\) on a common process, common \(F\), and a certified absorption domain, where \(\theta^{\mathrm{G}}=\mathbb{P}(\tau^{\mathrm{G}}<\tau^{\mathrm{F}})\) and \(\theta^{\mathrm{L}}=\mathbb{P}(\tau^{\mathrm{L}}<\tau^{\mathrm{F}})\). If a path of positive probability hits \(D^{\mathrm{L}}\setminus D^{\mathrm{G}}\) before \(F\), the inequality is typically strict. Pathwise \(\tau^{\mathrm{L}}\le \tau^{\mathrm{G}}\) on the bad-hit part, so
\[
\mathbb{E}[\min(\tau^{\mathrm{L}},\tau^{\mathrm{F}})]\le\mathbb{E}[\min(\tau^{\mathrm{G}},\tau^{\mathrm{F}})]
\]
as an extended-real inequality; a finite mean is reported only when absorption is almost sure and both sides are finite. Conditional means \(\mathbb{E}[\tau^{\mathrm{L}}\mid \tau^{\mathrm{L}}<\tau^{\mathrm{F}}]\) and \(\mathbb{E}[\tau^{\mathrm{G}}\mid \tau^{\mathrm{G}}<\tau^{\mathrm{F}}]\) are not comparable in general.

Changing the bad class from \(D^{\mathrm{G}}\) to \(D^{\mathrm{G}}\cup D^{\mathrm{L}}\) changes the target event and the stopping-rule hash. It is a new estimand, not a rescoring of a previous one. If the objective state partition is unchanged, the partition hash stays; selection is expressed by a separate stopping-rule hash.

If the initial state already lies in \(D^{\mathrm{L}}\) (respectively \(F\)), then \(\theta^{\mathrm{L}}=1\) (respectively \(0\)) and the mean stopped time is zero (respectively a positive absorption time). That is a legitimate first-hit value.

### B. Probability-One Absorption Domain

Let \(X^{\circ}=X\setminus A^{\dagger}\) be the candidate transient set. In a finite positive-rate graph, identify every unselected closed SCC \(\mathcal{C}\subset X^{\circ}\) (no positive-rate edge from \(\mathcal{C}\) to \(X^{\circ}\setminus\mathcal{C}\) and none from \(\mathcal{C}\) to \(A^{\dagger}\)). Let \(B^{\circ}\) be the reverse basin in \(X^{\circ}\) of all such SCCs, and set \(S^{\circ}=X^{\circ}\setminus B^{\circ}\). Then \(x\in S^{\circ}\) if and only if \(\mathbb{P}_x(\tau^{\dagger}<\infty)=1\). The global hypothesis of almost-sure absorption is the stronger condition \(B^{\circ}=\emptyset\) on the claimed domain. \(S^{\mathrm{p}}\) (existence of a support path to \(A^{\dagger}\)) is necessary but not sufficient for probability-one absorption.

### C. Generator, Committor, and Mean Time

On a certified domain the stopped generator has the block form
\[
Q=\begin{pmatrix}Q_{S^{\circ},S^{\circ}}&Q_{S^{\circ},D^{\dagger}}&Q_{S^{\circ},F}\\0&0&0\\0&0&0\end{pmatrix},
\]
with \(D^{\dagger}=D^{\mathrm{G}}\cup D^{\mathrm{L}}\). Off-diagonal entries are nonnegative and rows sum to zero. Selected states of \(A^{\dagger}\) are absorbing. Non-exponential durations require a phase-type expansion before they enter \(Q\).

**Theorem 7 (Stopped absorbing chain; P4).**  
Assume a finite IMS-CTMC and either almost-sure absorption or restriction of the analysis to a certified \(S^{\circ}\). Then:

1. The deadlock committor \(h_i=\mathbb{P}_i(\tau^{\mathrm{L}}<\tau^{\mathrm{F}})\) is the unique solution of \(Q_{S^{\circ},S^{\circ}}h=-Q_{S^{\circ},D^{\dagger}}\mathbf{1}\) with \(h=1\) on \(D^{\dagger}\) and \(h=0\) on \(F\).
2. The mean absorption time \(m_i=\mathbb{E}_i[\tau^{\dagger}]\) is the unique solution of \(Q_{S^{\circ},S^{\circ}}m=-\mathbf{1}\).
3. If \(Q(\vartheta)\) is differentiable and the partition \((S^{\circ},D^{\dagger},F)\) is locally constant, then \(h(\vartheta)\) is differentiable and
   \[
   Q_{S^{\circ},S^{\circ}}\partial_\vartheta h=-(\partial_\vartheta Q_{S^{\circ},S^{\circ}})h-(\partial_\vartheta Q_{S^{\circ},D^{\dagger}})\mathbf{1}.
   \]
4. On \(H^+=\{i\in S^{\circ}:h_i>0\}\), the Doob-\(h\) rates \(q^h_{ij}=q_{ij}h_j/h_i\) (\(i\neq j\), \(j\in H^+\)), \(q^h_{id}=q_{id}/h_i\) (\(d\in D^{\dagger}\)), and \(q^h_{iF}=0\), with diagonal equal to the negative off-diagonal row sum, define the generator of the chain conditioned on hitting \(D^{\dagger}\) first. The construction is undefined where \(h_i=0\) and is not a controller.

*Proof of invertibility.* Every state of \(S^{\circ}\) leaves and hits \(A^{\dagger}\) almost surely, so \(Q_{S^{\circ},S^{\circ}}\) is a transient subgenerator. The fundamental matrix
\[
\Phi=\int_0^\infty\exp(Q_{S^{\circ},S^{\circ}}t)\,dt
\]
is finite and satisfies \(Q_{S^{\circ},S^{\circ}}\Phi=\Phi Q_{S^{\circ},S^{\circ}}=-I\). Hence \(Q_{S^{\circ},S^{\circ}}\) is invertible.

*Proof of the committor equation.* For \(i\in S^{\circ}\) let \(\lambda_i=-q_{ii}>0\). First-jump decomposition gives
\[
h_i=\sum_{j\in S^{\circ}}\frac{q_{ij}}{\lambda_i}h_j+\sum_{d\in D^{\dagger}}\frac{q_{id}}{\lambda_i}.
\]
Multiplication by \(\lambda_i\) and rearrangement yield \(\sum_{j\in S^{\circ}}q_{ij}h_j+\sum_{d}q_{id}=0\), i.e. \(Q_{S^{\circ},S^{\circ}}h=-Q_{S^{\circ},D^{\dagger}}\mathbf{1}\). Uniqueness follows from invertibility.

*Proof of the mean-time equation.* First-jump decomposition yields \(m_i=1/\lambda_i+\sum_{j\in S^{\circ}}(q_{ij}/\lambda_i)m_j\). Multiplication by \(\lambda_i\) gives \(Q_{S^{\circ},S^{\circ}}m=-\mathbf{1}\).

*Proof of sensitivity.* Write \(\Xi(\vartheta)h(\vartheta)=b(\vartheta)\) with \(\Xi=Q_{S^{\circ},S^{\circ}}\) and \(b=-Q_{S^{\circ},D^{\dagger}}\mathbf{1}\). On a neighbourhood where the partition is fixed and rates are differentiable, \(\Xi(\vartheta)\) remains invertible, inversion is \(C^1\) on \(\mathrm{GL}_n\), and \(h=\Xi^{-1}b\) is differentiable. Differentiating gives \((\partial_\vartheta \Xi)h+\Xi(\partial_\vartheta h)=\partial_\vartheta b\).

*Proof of the Doob-\(h\) generator.* For \(i\in H\) the off-diagonal rates into \(H\cup D^{\dagger}\) are nonnegative. Jumps into \(F\) are set to zero because the conditioning event is “\(D^{\dagger}\) first.” The diagonal is defined so that every row in \(H^+\cup D^{\dagger}\) sums to zero; rows of \(D^{\dagger}\) are identically zero. A jump of the original chain into \(S^{\circ}\setminus H\) has \(h=0\) and is killed. For any finite path \(i_0,\ldots,i_n\) that has not yet hit \(F\), the path rate is multiplied by the Radon–Nikodym factor \(h_{i_n}/h_{i_0}\); absorption at \(D^{\dagger}\) ends the path. The transform does not enable or disable plant events, so it is not a supervisor. \(\square\)

If a reachable unselected closed class remains, \(Q_{S^{\circ},S^{\circ}}\) as declared is incomplete, \(\tau^{\dagger}=\infty\) on those paths, and the unconditional mean is \(+\infty\). The correct output is a structured refusal (non-almost-sure absorption domain), not an invented finite mean. Sensitivity holds only on pieces of parameter space where the partition is constant.

### D. Admission Barrier \(\mathbf{B}\) and Partition Soundness

A quantitative row is emitted only after admission barrier \(\mathbf{B}\) returns certified: the stable LTS is complete, every reachable state is classified, no unselected closed class remains, and no completed job still holds a resource. Otherwise the row is refused and the reason is kept.

**Algorithm (terminal/stopping partition).**  
(i) Enumerate the complete untruncated stable LTS and re-enumerate from the same registry for provenance. (ii) Mark \(F\). (iii) Mark \(D^{\mathrm{G}}\) and store global certificates. (iv) Enumerate all-minimal local kernels on the remainder; mark \(X^{\ell}\). (v) If A2b is proved, apply Theorem 3; otherwise apply Theorem 4–Theorem 5 on each candidate. (vi) Compute SCCs on the leftover plant graph; classify terminal SCCs as \(\Lambda^{0}\) or \(\Lambda^{\infty}\). (vii) Form \(A^{\dagger}\) and \(S^{\circ}\); refuse if \(B^{\circ}\neq\emptyset\) on a global claim. (viii) Freeze the state-space, partition, rate-manifest, and stopping-rule hashes.

**Theorem 8 (Partition soundness).**  
Under CW1–CW10 and CW11, if the algorithm returns successfully, then: (i) \(D^{\mathrm{G}}\), \(D^{\mathrm{L}}\), \(F\), \(\Lambda^{\infty}\), and \(\Lambda^{0}\) are pairwise disjoint under the stated precedence; (ii) \(\Lambda^{\infty}\) and \(\Lambda^{0}\) are terminal-SCC classes of the leftover plant graph; (iii) \(D^{\mathrm{L}}\) is used only as a stopped-process bad hit set admitted by Theorem 3 or Theorem 4; (iv) \(S^{\mathrm{p}}\) is an existential support diagnostic and \(S^{\circ}\) is the certified probability-one domain; (v) the exact CTMC and DES may share the same selected labels.

The algorithm *must* refuse a binary CTMC when any of the following holds: truncated or unavailable LTS; an invalid model/state (including completion while holding); LTS provenance mismatch; missing source/target or missing frozen rate; overlapping completion and bad labels; a transient state with no positive outgoing rate; a transient state that cannot reach selected absorption; a reachable unselected \(\Lambda^{\infty}\) or \(\Lambda^{0}\) that cannot reach selected absorption; a \(D^{\mathrm{G}}\)-only estimand in the presence of \(D^{\mathrm{L}}\) unless that estimand is separately declared; a policy-only stall not entered in a policy schema; a local candidate with a path to \(F\).

### E. Exact/DES Protocol Used in Section X

On a \(\mathbf{B}\)-certified graph the implementation solves the three binary reductions of Theorem 7 (global, local, selected-bad) and checks \(\theta^{\mathrm{G}}+\theta^{\mathrm{L}}=\theta^{\mathrm{B}}\) numerically. DES uses Gillespie sampling of the same rates and the same three classes, \(n_{\mathrm{s}}=65536\) replications, a primary seed and a subsequent reproduction seed, contiguous shards, and one reducer. The simultaneous Hoeffding band for six probability cells at \(\alpha=0.01\) is
\[
\varepsilon=\sqrt{\frac{\log(2\cdot 6/0.01)}{2n_{\mathrm{s}}}}=7.35\times 10^{-3}.
\]
A cell is compatible when the absolute error is at most \(\varepsilon\). Compatibility does not prove Theorem 3 and does not prove plant fidelity. BLAS threads equal one; independent plants and DES shards run in a process pool (32 workers by default, 48 when free RAM is at least \(64\,\mathrm{GiB}\)).

Complexity (not a polynomial-time claim): SCC decomposition on an explicit LTS is \(O(\lvert X\rvert+\lvert\mathcal{E}\rvert)\); all-minimal local enumeration is exponential in the number of blocked jobs; the linear solve scales with \(\lvert S^{\circ}\rvert\).

---

## X. Experimental Studies

All subjects use a new scope identifier and new evidence roots. Frozen historical refusals are retained and are not overwritten. No shop-floor log is used. Plants are synthetic digital twins.

### A. Family I: Theory-Hardening Witnesses

Four logical witnesses keep the theorems from becoming tautologies.

1. *Non-confluent closure.* Two zero-time sequences from one unstable state yield two stable successors. A deterministic closure-selection map \(\sigma\) is refused.
2. *Optional drain.* A controllable alternate release does not prove the ring deadlock-free; the saturated ring prefix remains reachable. Drain is control, not a structural repair.
3. *Wrong cut.* Deleting a backflow edge creates a *new* kernel. Cutting the “obvious” wait-edge is not a repair.
4. *Non-chain covering kernel.* A covering kernel that is not chain-decomposable makes a strict-order sufficient condition inapplicable rather than “deadlock-free.”

These four rows are cited as boundaries, not as main theorems.

### B. Family IV: Machine–AGV Island

The *lead* manufacturing clothing is a three-job island that starts *transient* (Table II). Jobs \(\mathsf{A}\) and \(\mathsf{B}\) are idle; job \(\mathsf{C}\) already holds \(\mathsf{M}_2\) and has two remaining uncontrollable service stages. From that initial state the word \(\mathsf{A}\)-start-\(\mathsf{M}_1\), \(\mathsf{A}\)-service-complete, \(\mathsf{B}\)-start-\(\mathsf{V}\) reaches an admitted local-hit state: \(\mathsf{A}\) holds \(\mathsf{M}_1\) and requests \(\mathsf{V}\), \(\mathsf{B}\) holds \(\mathsf{V}\) and requests \(\mathsf{M}_1\), and \(\mathsf{C}\) still has a plant outgoing arc. The only structural interlock is \(\{\mathsf{A},\mathsf{B}\}\) on \(\{\mathsf{M}_1,\mathsf{V}\}\). A terminal-SCC diagnosis would miss that local stop. Admission of \(D^{\mathrm{L}}\) on this clothing is the complete-LTS fallback of Theorem 4 (recorded route `lts_fallback`); A2b / Theorem 3 is not the recorded route. The predeclared intervention is one extra AGV slot (\(\mathsf{V}\) of capacity 2). Rates are synthetic: starts unit rate 1, \(\mathsf{A}\)-service-complete rate 2, \(\mathsf{C}\)’s remaining services rate \(1/2\), other events rate 1.

**Table II**  
Positive-time island first-hit values (exact). DES agrees on all six cells at \(n_{\mathrm{s}}=65536\), \(\varepsilon=7.35\times 10^{-3}\)

| Plant | \(\lvert X\rvert\) | \(\mathbf{B}\) | \(\theta^{\mathrm{G}}\) | \(\theta^{\mathrm{L}}\) | \(\theta^{\mathrm{B}}\) | \(m\) |
| --- | --- | --- | --- | --- | --- | --- |
| Positive-time base | 64 | certified | \(0.0460\) | \(0.5373\) | \(0.5833\) | \(3.596\) |
| Extra AGV slot | 72 | certified | \(0\) | \(0\) | \(0\) | \(6.296\) |

The core island conclusion is therefore this. The initial state is not in \(D^{\mathrm{G}}\cup D^{\mathrm{L}}\cup F\). Three admitted local-hit states exist, all with a plant outgoing arc, and one global-deadlock state exists after \(\mathsf{C}\) has completed. From the initial state the first local hit is a stopping *event*: \(\theta^{\mathrm{L}}=0.537\), \(\theta^{\mathrm{B}}=7/12\), and \(m=3.596\ge 0.25\). The plant is *not* a terminal SCC at those local-hit states, because \(\mathsf{C}\) can still move. One extra AGV slot destroys the \(\{\mathsf{M}_1,\mathsf{V}\}\) kernel: \(D^{\mathrm{G}}=D^{\mathrm{L}}=\emptyset\), \(\theta^{\mathrm{B}}=0\), and the mean time to completion rises to \(6.296\). For this island, deadlock of the manufacturing cell is a *positive-time local first-hit*, and a one-slot vehicle change prevents that stop.

A *time-zero boundary* clothing of the same island is retained (Fig. 2). There \(\mathsf{A}\) already holds \(\mathsf{M}_1\) requesting \(\mathsf{V}\), \(\mathsf{B}\) already holds \(\mathsf{V}\) requesting \(\mathsf{M}_1\), and \(\mathsf{C}\) is in service on \(\mathsf{M}_2\): \(\theta^{\mathrm{L}}=1\), \(m=0\). An optional drain that lets \(\mathsf{B}\) release \(\mathsf{V}\) without entering \(\mathsf{M}_1\) sends every trajectory to \(F\) (\(\theta^{\mathrm{B}}=0\), \(m=3.23\)). That clothing is scientifically correct and is not overwritten; it is no longer the lead figure, because the first hit is the initial condition rather than an event.

An earlier all-completion clothing of the same island (release-then-complete, no local hit) produced \(\theta^{\mathrm{B}}=0\) on both the base and the intervention and is retained as a certified negative: a digital-twin that always finishes cannot demonstrate local-first-hit. A still earlier clothing that marked completion while holding a buffer was refused as an invalid LTS state and is retained.

Fig. 2 plots the time-zero boundary KPIs. On the positive-time island the six DES cells lie inside the Hoeffding band; that check is a same-target numerical agreement, not a rare-event study and not a shop-floor rate.

### C. Family II: Same-Semantics Baselines

Ten plants are scored by four methods against LTS truth (Table III): a machine-cycle/SCC screen, a closed-core certificate, a siphon-or-refuse predicate, and exhaustive LTS deadlock. Siphon evaluation attaches the LTS witness as a reachability prefix; an empty prefix is legal when the initial state is the deadlock.

**Table III**  
Same-semantics baseline table (false positives \(=0\), false negatives \(=0\))

| Plant | Role | Cycle/SCC | Closed core | SIP\(^1\) | LTS deadlock |
| --- | --- | --- | --- | --- | --- |
| Unit pair | siphon agree | yes | yes | exact | yes |
| Unit triple | siphon agree | yes | yes | exact | yes |
| Reachable pair | siphon agree | yes | yes | exact (prefix length 2) | yes |
| Machine–AGV unit | siphon agree | yes | yes | exact | yes |
| OR alternatives | typed refusal | yes | yes | OR alternatives | yes |
| AND demand | typed refusal | yes | yes | non-minimal global / conjunctive local | yes |
| Capacity-2 saturation | typed refusal | yes | yes | not unit capacity | yes |
| AGV \(\wedge\) buffer | typed refusal | yes | yes | conjunctive demand | yes |
| Residual cycle | C1 boundary | yes | no | no core | no |
| Local cycle with bypass | bypass boundary | yes | no (global) | no core | no |

The residual cycle is the C1 witness: a wait-for cycle exists, residual capacity remains, and LTS truth is “not deadlocked.” The bypass plant is the Theorem 5 witness: a local-looking pair is not a global deadlock because a third job can open a completion path. The four siphon agreements occupy IMS-SIP\(^1\). The four refusals occupy the hypotheses that Theorem 2 declines to inherit from S3PR monitor theory [1], [3]. A cycle/SCC screen alone would mark the residual cycle as a stop and is therefore not used as a theorem.

### D. Family III: Tandem Scale

Jobs visit resources \(r_0,\ldots,r_{k-1}\) of capacity \(c\) and then complete. The family is the unit-capacity product \(\{4,5,6,7,8\}\times\{3,4,5\}\) plus four capacity-2 rows. Caps are \(10^5\) states and \(300\,\mathrm{s}\). Table IV and Fig. 3 report the live wave (48 workers).

**Table IV**  
Tandem enumeration (capacity 1 unless noted). “Refused” means the declared cap was hit

| Jobs | Stages | \(\lvert X\rvert\) | Time (s) | Class |
| --- | --- | --- | --- | --- |
| 4 | 3 | 304 | 0.07 | enumerated |
| 4 | 4 | 648 | 0.21 | enumerated |
| 4 | 5 | 1256 | 0.69 | enumerated |
| 5 | 3 | 992 | 0.37 | enumerated |
| 5 | 4 | 2512 | 1.92 | enumerated |
| 5 | 5 | 5752 | 11.4 | enumerated |
| 6 | 3 | 3040 | 2.30 | enumerated |
| 6 | 4 | 8992 | 23.2 | enumerated |
| 6 | 5 | 24064 | 189 | enumerated |
| 7 | 3 | 8864 | 20.0 | enumerated |
| 7 | 4 | 30144 | 256 | enumerated |
| 7 | 5 | 93088 | 2994 | refused (time) |
| 8 | 3 | 24832 | 184 | enumerated |
| 8 | 4 | 95744 | 3932 | refused (time) |
| 8 | 5 | 100000 | 4189 | refused (truncated) |
| 4 | 3, \(c=2\) | 574 | 0.35 | enumerated |
| 5 | 3, \(c=2\) | 2582 | 5.36 | enumerated |
| 5 | 4, \(c=2\) | 6672 | 37.7 | enumerated |
| 6 | 3, \(c=2\) | 11050 | 102 | enumerated |

Twelve enumerated rows have \(\lvert X\rvert\ge 10^3\) and four have \(\lvert X\rvert\ge 10^4\). The three refusals are typed: two exceed \(300\,\mathrm{s}\) without truncation, one hits the state cap. An earlier 576-row one-step family whose largest LTS had 496 states is not cited as “large.” Family III is computational evidence for T-ASE, not a complexity theorem and not a finite-capacity configuration result [9].

### E. Family V: Four-Field CRP Diagnostic

Six subjects without an embedding reuse no historical case hash and do not run SBA or CRP equations. Table V reports Proposition 4 on those six; two further subjects (H6-A, H6-B) decide field 4.

**Table V**  
Four-field diagnostic. Agreement requires all four fields

| Subject | Reachable | Local family | Match \(\lvert K\rvert\) | S4PR overlap | Agreement |
| --- | --- | --- | --- | --- | --- |
| Unit pair, \(R^{\star}=\{r_1,r_2\}\) | yes | yes | 1 | no embedding | no |
| Unit triple | yes | yes | 1 | no embedding | no |
| Reachable pair | yes | yes | 1 | no embedding | no |
| Wrong \(R^{\star}=\{r_9\}\) | yes | yes | 0 | no embedding | no |
| AGV \(\wedge\) buffer | yes | yes | 1 | no embedding | no |
| Residual cycle | yes | no | 0 | no embedding | no |

Fields 1–3 hold on four of these six subjects. Field 4 is `no_independent_s4pr_embedding` on all six, so agreement is identically zero on this table. That remains the intended reading of Proposition 4 and of [10] *in the absence of an embedding*.

Two further subjects supply the missing field-4 decision. H6-A is an independently hashed embedding of the *definitional* two-process unit-capacity S3PR admitted by [1] (two sequential processes sharing two unit resource places). It is not a reconstruction of [1, Fig. 1] and not a replay of a running example in [10]. The embedding name map \(\iota\) and its marking correspondence (neither is Table 0’s calendar indicator \(\chi_s\)) preserve capacities, the initial marking, enabled events at the initial state, and one-step commutation on every IMS state the correspondence represents; they do not preserve BAS modes, AGV occupancy, OR/AND acquisition, or the cyclic return to idle. Field 1 is this paper’s BFS (\(A\textrm{-start-}r_1\), \(B\textrm{-start-}r_2\)), not a prefix copied from [1]. All four fields hold, so agreement is true. H6-B is the same net after a declared IMS-only AGV token on the second step of process \(\mathsf{A}\). Field 4 is false with typed reason `declared_distortion_agv_token`; field 1 against the *source* target is also false, because \(\mathsf{A}\) then requests \(\{r_2,\mathrm{V}\}\) rather than \(\{r_2\}\). Neither row runs SBA or CRP equations.

**Table V (continued)**  
Embedded subjects. Agreement still requires all four fields

| Subject | Reachable | Local family | Match \(\lvert K\rvert\) | S4PR/S3PR overlap | Agreement |
| --- | --- | --- | --- | --- | --- |
| H6-A definitional S3PR of [1] | yes | yes | 1 | verified embedding | yes |
| H6-B declared AGV distortion | no | no | 0 | distortion (E5 fails) | no |

### F. Family VI: Finite-State Supervisor Baseline

On the positive-time island of Table II, a Ramadge–Wonham nonblocking supervisor is computed on the explicit 64-state LTS [15], treating \(D^{\dagger}=D^{\mathrm{G}}\cup D^{\mathrm{L}}\) as forbidden and \(F\) as marked. Controllability is the registry flag of each event. This is a *baseline*, not a new theorem: the implementation is the greatest fixed point of “remove states that can uncontrollably leave the remaining set or cannot reach a marked state.” Compact-input synthesis remains at least NP-hard; the construction is not maximally permissive in the MCPP sense [3] and is not a risk-budget supervisor.

**Table VI**  
Supervisor baseline on the Table II base plant (same stopping family)

| Quantity | Value |
| --- | --- |
| \(\lvert X\rvert\) | 64 |
| \(\lvert X_{\mathrm{safe}}\rvert\) | 56 |
| disabled controllable state-events | 14 |
| initial feasible | yes |
| supervised \(\theta^{\mathrm{B}}\) | \(0\) |
| supervised \(m\) | \(7.048\) |

The 14 cuts are \(\mathsf{A}\)-start-\(\mathsf{M}_1\) or \(\mathsf{B}\)-start-\(\mathsf{V}\) at states from which the interlock would close, plus two controllable \(\mathsf{C}\)-release-\(\mathsf{M}_2\) cuts required for consistency of the remaining set. Supervised \(\theta^{\mathrm{B}}=0\le 0.583=\theta^{\mathrm{B}}\) of the unsupervised plant. Mean stopped time rises from \(3.596\) to \(7.048\): the supervisor trades a positive first-hit probability for a longer completing run.

---

## XI. Discussion and Limitations

T-ASE evaluates automation methods by quality, completeness, complexity, verification, and reliability [12], [16]. The verification offered here is a certified first-hit set, a typed refusal, and a same-target exact/DES check. The reliability claim is scoped: relative to a declared finite registry, not relative to an open shop floor.

Several limitations are essential to the contribution rather than residual bugs.

1. *Synthetic island, modest \(\lvert X\rvert\).* Family IV’s lead clothing is a 64-state (72-state after the extra slot) synthetic island. It demonstrates a positive-time local hit; it is not a shop-floor log and not a large FMS. The time-zero clothing remains as a boundary example.
2. *Synthetic plants.* Every subject is a digital twin. No vendor trace, no throughput number, and no claim that an extra AGV slot “improves productivity” on a factory is licensed.
3. *Published-net scope.* Field 4 is decided on the definitional two-process unit S3PR of [1], not on [1, Fig. 1] and not on a running example of [10]. No general IMS \(\equiv\) S3PR isomorphism and no CRP iff is claimed.
4. *SIP\(^1\) is small.* Four agreements demonstrate the dual; they do not make siphon control the method.
5. *Exponential LTS.* Family III hits a \(10^5\)/300 s wall. All-minimal local enumeration is exponential in blocked jobs. No bit-polynomial IMS reachability is claimed [13], [14].
6. *Historical negatives retained.* A CRP implementation-level encoding that used a global extractor in the presence of an unrelated job remains failed. An eight-dimension overlap gate used in earlier internal work remains open. Neither is a confirmation set for this paper.
7. *What is not proved.* A2b is not necessary. Complete-LTS admission is not a general structural theorem. A local core is not automatically \(D^{\mathrm{L}}\). \(D^{\mathrm{L}}\) is not a plant terminal SCC. Exact/DES agreement does not prove the theorem. The method is not a risk-budget supervisor.

Natural extensions that remain open are a replay of [10]’s own running example, a shop-floor log, a compact (unexpanded) supervisor, and a CRP theorem. Those are later papers.

---

## XII. Conclusion

The paper’s key conclusions, in the order a first reader needs them, are as follows.

1. *Object.* Capacity-mediated blocking of a finite manufacturing cell is a first hit of a certified set \(D^{\mathrm{G}}\) or \(D^{\mathrm{L}}\) in a stopped process, not a wait-for cycle, not an unmarked plant-net siphon, and not a terminal SCC of the plant graph.
2. *Admission.* A local closed core enters \(D^{\mathrm{L}}\) only by A2b (Theorem 3) or by \(F\)-nonreachability on the complete finite LTS (Theorem 4), and is refused if a completion bypass exists (Theorem 5). Covering cores characterise global operational deadlock (Theorem 1). Diagnostic siphons are exact only on IMS-SIP\(^1\) (Theorem 2).
3. *Island (the manufacturing-cell conclusion).* On the three-job machine–AGV island the initial state is transient. The first local hit occurs at positive time while \(\mathsf{C}\) still moves: \(\theta^{\mathrm{L}}=0.537\), \(\theta^{\mathrm{B}}=7/12\), \(m=3.596\). The cell can locally fail without the plant graph dying. One extra AGV slot removes that local core and sends every trajectory to \(F\) (\(\theta^{\mathrm{B}}=0\), \(m=6.296\)). Exact and DES values agree on all six cells. A time-zero clothing of the same island (\(\theta^{\mathrm{L}}=1\), \(m=0\)) is retained as a boundary. Deadlock of this island is therefore a *positive-time local first-hit*; a one-slot vehicle change prevents that stop.
4. *Baselines, embedding, and scale.* Four siphon agreements and four typed refusals sit on one semantics (false positives and false negatives zero). A tandem family reaches \(10^3\)–\(10^4\) states and refuses three rows at a declared cap. A four-field diagnostic agrees on an independently hashed definitional S3PR of [1] and refuses a declared AGV distortion. A finite-state supervisor on the same 64-state graph retains 56 states and also yields \(\theta^{\mathrm{B}}=0\).

Controllers, monitors, shop-floor policies, and general plant-net isomorphisms remain outside the claim.

---

## Appendix A  
Retained Negative Clothings

An island that marked a job complete while it still held the next buffer was refused as `completed_job_holds_resource` (invalid LTS state) and is not replaced in place. A repaired all-completion island with the same topology produced \(\mathbf{B}\) certified and \(\theta^{\mathrm{B}}=0\) on both the base and the intervention; it is a certified demonstration that an always-finishing twin cannot clothe Theorem 3. Both clothings remain in the evidence record.

## Appendix B  
Implementation Notes

Certificates, LTS enumeration, the wait-snapshot bridge, barrier \(\mathbf{B}\), the absorbing CTMC, and the DES shards are generated from one registry. Independent plants and DES shards run in a process pool; BLAS threads equal one. Primary DES finishes before reproduction. Evidence roots are write-once. The quantitative protocol, including the Hoeffding band and the seeds, is fixed before the island wave.

## Appendix C  
Exact Reachable Thresholds (BIX1-SAT and BIX2-PERSIST)

These two families close the original exact-threshold derivations. They are not T-ASE main novelties and are not finite-capacity configuration theorems in the sense of [9].

### C.1 Family BIX1-SAT (Theorem 9)

The instance \(\mathrm{BIX1\text{-}SAT}(c_{\mathsf{m}},c_{\mathsf{g}},c_{\mathsf{b}},c_{\mathsf{v}},n_{\mathsf{a}},n_{\mathsf{b}})\) has capacities at least one. All A-jobs initially request \(\mathsf{m}\) and all B-jobs initially request \(\mathsf{g}\). The registry contains:

- *A-chain:* `start` acquires \(\mathsf{m}\) and clears the start request; `service_complete` is uncontrollable, keeps \(\mathsf{m}\), and requests \(\{\mathsf{g},\mathsf{b},\mathsf{v}\}\); `transfer` is controllable and atomically acquires \(\mathsf{g},\mathsf{b},\mathsf{v}\), releases \(\mathsf{m}\), and clears requests; `drain` is uncontrollable and releases \(\mathsf{g},\mathsf{b},\mathsf{v}\) and completes.
- *B-chain:* `start` acquires \(\mathsf{g}\); `transport_complete` is uncontrollable, keeps \(\mathsf{g}\), and requests \(\mathsf{m}\); `unload` acquires \(\mathsf{m}\) and releases \(\mathsf{g}\); `complete` releases \(\mathsf{m}\) and completes.
- \(\mathsf{v}\) is a hard-reservation token. Zero-time closure is trivial. The flag \(\chi_s\) records the absence of an external calendar, not the absence of completion events.

**Theorem 9 (P3d).**  
A capacity-mediated global operational deadlock is reachable in BIX1-SAT if and only if \(n_{\mathsf{a}}\ge c_{\mathsf{m}}\) and \(n_{\mathsf{b}}\ge c_{\mathsf{g}}\).

*Sufficiency.* Execute `start` and `service_complete` for exactly \(c_{\mathsf{m}}\) A-jobs, so they saturate \(\mathsf{m}\) and request \(\{\mathsf{g},\mathsf{b},\mathsf{v}\}\). Then execute `start` and `transport_complete` for exactly \(c_{\mathsf{g}}\) B-jobs, so they saturate \(\mathsf{g}\) and request \(\mathsf{m}\). The prefix contains no successful transfer, hence residuals are \(\alpha=0\) on \(\mathsf{m}\) and \(\mathsf{g}\), and \(\alpha=c_{\mathsf{b}}\), \(c_{\mathsf{v}}\) on \(\mathsf{b}\) and \(\mathsf{v}\). Every A-job’s AND request is blocked by the \(\mathsf{g}\)-gap; every B-job is blocked by the \(\mathsf{m}\)-gap; unstarted A/B jobs cannot start. No job is in a mode that enables a completion event. All unfinished activity is covered by the same \(\mathsf{m}\)–\(\mathsf{g}\) closed core, so Theorem 1 applies.

*Necessity.* No global deadlock can contain an `a_transferred` job (`drain` is uncontrollable and enabled) or a `b_on_M` job (`complete` is uncontrollable and enabled). Hence in a global deadlock \(\mathsf{m}\) is held only by A-jobs that have not transferred, \(\mathsf{g}\) only by B-jobs that have not unloaded, and \(\mathsf{b},\mathsf{v}\) are free.

If \(n_{\mathsf{a}}<c_{\mathsf{m}}\), then \(\mathsf{m}\) cannot be saturated, so residual \(\alpha(\mathsf{m})>0\). A `b_blocked_unload` job would have `unload` enabled; otherwise every unfinished B-job is `b_idle` or `b_in_transport`, the former can `start` when \(\mathsf{g}\) has residual, and the latter has `transport_complete` enabled. If \(\mathsf{g}\) has no residual then some B-job holds \(\mathsf{g}\); under the assumption that none is `b_blocked_unload`, that holder is `b_in_transport` and still has an enabled completion. If there is no unfinished B-job, every unfinished A-job is `a_idle`, `a_in_service`, or `a_blocked_complete`, which enable `start`, `service_complete`, or—because \(\mathsf{b},\mathsf{v}\) are free and \(\mathsf{g}\) is not saturated by B—`transfer`. Hence there is no global deadlock.

Symmetrically, if \(n_{\mathsf{b}}<c_{\mathsf{g}}\), residual \(\alpha(\mathsf{g})>0\) and \(\mathsf{b},\mathsf{v}\) are empty in the necessary deadlock shape. Any `a_blocked_complete` has `{\mathsf{g},\mathsf{b},\mathsf{v}}` transfer enabled; if none exists, every unfinished A-job has `start` or `service_complete` enabled. If there is no unfinished A-job, every unfinished B-job has an enabled event on the `start`/`transport_complete`/`unload`/`complete` chain; if \(\mathsf{m}\) is saturated by A-jobs they are `a_in_service` or `a_blocked_complete`, which are enabled. Therefore every global deadlock requires \(n_{\mathsf{a}}\ge c_{\mathsf{m}}\) and \(n_{\mathsf{b}}\ge c_{\mathsf{g}}\).

The capacities \(c_{\mathsf{b}},c_{\mathsf{v}}\) disappear from the threshold because the witnessing prefix has no successful transfer, so no job holds \(\mathsf{b}\) or \(\mathsf{v}\), and the A-job AND request is already blocked by the \(\mathsf{g}\)-gap. This is not a general statement that buffer or reservation capacities never matter. If a successful A-transfer may occupy \(\mathsf{b}\) persistently, the instance \(c_{\mathsf{m}}=c_{\mathsf{g}}=c_{\mathsf{b}}=1\), \(n_{\mathsf{a}}=2\), \(n_{\mathsf{b}}=0\) already leaves the family: it is an `outside_bix1_sat` terminal-boundary, not a mismatch of Theorem 9.

### C.2 Family BIX2-PERSIST (Theorem 10–Theorem 11)

The instance \(\mathrm{BIX2\text{-}PERSIST}(c_{\mathsf{m}},c_{\mathsf{b}},c_{\mathsf{p}},n_{\mathsf{a}},n_{\mathsf{b}},n_{\mathsf{c}},\mathrm{mode})\) starts empty. Each successful handoff is followed by an explicit uncontrollable release, so completed jobs hold nothing. Every demand is one unit.

- A-chain: \(\mathsf{m}\to\mathsf{b}\to\mathrm{release}(\mathsf{b})\);
- B-chain: \(\mathsf{b}\to\mathsf{p}\to\mathrm{release}(\mathsf{p})\);
- *ring* C-chain: \(\mathsf{p}\to\mathsf{m}\to\mathrm{release}(\mathsf{m})\);
- *dag* mode deletes the \(\mathsf{p}\to\mathsf{m}\) request; C releases \(\mathsf{p}\) on completion.

Each station pair \((r,r')\) has four events: controllable start acquiring \(r\); uncontrollable completion keeping \(r\) and requesting \(r'\); controllable handoff acquiring \(r'\) and releasing \(r\); uncontrollable release of \(r'\) with completion.

**Theorem 10 (P3e-a, ring).**  
A capacity-mediated global operational deadlock is reachable in ring mode if and only if \(n_{\mathsf{a}}\ge c_{\mathsf{m}}\), \(n_{\mathsf{b}}\ge c_{\mathsf{b}}\), and \(n_{\mathsf{c}}\ge c_{\mathsf{p}}\). On the minimal \(1/1/1\) instance the minimal closed-core resources are exactly \(\{\mathsf{m},\mathsf{b},\mathsf{p}\}\).

*Sufficiency.* Select \(c_{\mathsf{m}}\) A-jobs, \(c_{\mathsf{b}}\) B-jobs, and \(c_{\mathsf{p}}\) C-jobs. For each selected A-job fire start-\(\mathsf{m}\) then complete-request-\(\mathsf{b}\); likewise for B and C. The finite prefix has no successful handoff, so A, B, C saturate \(\mathsf{m}\), \(\mathsf{b}\), \(\mathsf{p}\) respectively and request the next resource. Unstarted jobs are blocked by full capacity; no job is in a mode with an enabled completion or release. The three job classes and \(\{\mathsf{m},\mathsf{b},\mathsf{p}\}\) form a covering closed core, so Theorem 1 applies inside the capacity-mediated subdomain.

*Necessity.* In any global deadlock of the family, a job `in_service` has an uncontrollable completion enabled and a job `on_target` after a successful handoff has an uncontrollable release enabled; neither mode can occur. Hence every unfinished job is idle or blocked-before-handoff, and \(\mathsf{m},\mathsf{b},\mathsf{p}\) can be held only by blocked A, B, C respectively. Write \(\iota_{\mathsf{a}},\iota_{\mathsf{b}},\iota_{\mathsf{c}}\) for idle sets and \(\mathcal{J}_{\mathsf{a}},\mathcal{J}_{\mathsf{b}},\mathcal{J}_{\mathsf{c}}\) for blocked-before-handoff sets, so holders satisfy \(\mathcal{H}_{\mathsf{m}}=\mathcal{J}_{\mathsf{a}}\), \(\mathcal{H}_{\mathsf{b}}=\mathcal{J}_{\mathsf{b}}\), \(\mathcal{H}_{\mathsf{p}}=\mathcal{J}_{\mathsf{c}}\). Moreover: residual \(\alpha(\mathsf{m})>0\) implies \(\iota_{\mathsf{a}}=\mathcal{J}_{\mathsf{c}}=\emptyset\) (else start-\(\mathsf{m}\) or C-handoff is enabled); residual \(\alpha(\mathsf{b})>0\) implies \(\iota_{\mathsf{b}}=\mathcal{J}_{\mathsf{a}}=\emptyset\); residual \(\alpha(\mathsf{p})>0\) implies \(\iota_{\mathsf{c}}=\mathcal{J}_{\mathsf{b}}=\emptyset\).

If \(n_{\mathsf{a}}<c_{\mathsf{m}}\), then because \(\mathsf{m}\) is held only in unit by \(\mathcal{J}_{\mathsf{a}}\) one has residual \(\alpha(\mathsf{m})>0\), hence \(\iota_{\mathsf{a}}=\mathcal{J}_{\mathsf{c}}=\emptyset\). Then \(\mathsf{p}\) has no holder, so residual \(\alpha(\mathsf{p})>0\), hence \(\iota_{\mathsf{c}}=\mathcal{J}_{\mathsf{b}}=\emptyset\). Then \(\mathsf{b}\) has no holder, so residual \(\alpha(\mathsf{b})>0\), hence \(\iota_{\mathsf{b}}=\mathcal{J}_{\mathsf{a}}=\emptyset\). Every permitted unfinished mode is empty, so the state is complete, contradicting global deadlock. The cases \(n_{\mathsf{b}}<c_{\mathsf{b}}\) and \(n_{\mathsf{c}}<c_{\mathsf{p}}\) are cyclic permutations of the same argument.

**Theorem 11 (P3e-b, deleted backflow).**  
In dag mode no capacity-mediated global operational deadlock is reachable. If the batch is nonempty, a marked completion path exists from the empty initial state.

*Proof of deadlock-freeness.* After deleting \(\mathsf{p}\to\mathsf{m}\), hold-then-request obeys \(\mathsf{m}<\mathsf{b}<\mathsf{p}\). In a hypothetical deadlock, exclude again every `in_service` and `on_target` mode. C has no blocked-before-handoff mode; an idle C would make start-\(\mathsf{p}\) enabled unless \(\mathsf{p}\) were saturated by a job with no enabled release, which has already been excluded. Hence a deadlock has no unfinished C and \(\mathsf{p}\) is empty. Every blocked B-job can then hand off into \(\mathsf{p}\), after which \(\mathsf{b}\) is empty; every blocked A-job can hand off into \(\mathsf{b}\), after which \(\mathsf{m}\) is empty; remaining idle jobs can start. The only state with no enabled event is complete, a contradiction.

*Proof of a completion path.* Execute jobs serially: start one job, then its completion, handoff (if any), and release. Every capacity is at least one, so every finite batch can be completed one job at a time. \(\square\)

The three-resource circular wait and the deletion of one backflow edge are classical and are not claimed as new graph theory. Theorem 10–Theorem 11 close a concrete IMS-event-semantic pair: a reachable, capacity-auditable persistent-buffer core and its matched repair. Alternate routes, AND requests, AGV/reservations, external drains, forced priorities, and multiple persistent buffers lie outside the family.

---

## Acknowledgment

Omitted for double-anonymous review.

---

## References

[1] J. Ezpeleta, J. M. Colom, and J. Martinez, “A Petri net based deadlock prevention policy for flexible manufacturing systems,” *IEEE Trans. Robot. Autom.*, vol. 11, no. 2, pp. 173–184, Apr. 1995.

[2] Z. Li and M. Zhou, “Elementary siphons of Petri nets and their application to deadlock prevention in flexible manufacturing systems,” *IEEE Trans. Syst., Man, Cybern. A, Syst. Humans*, vol. 34, no. 1, pp. 38–51, Jan. 2004.

[3] Y. Chen and Z. Li, “Design of a maximally permissive liveness-enforcing supervisor with a compressed supervisory structure for flexible manufacturing systems,” *Automatica*, vol. 47, no. 5, pp. 1028–1034, May 2011.

[4] M. Lawley and S. Reveliotis, “Deadlock avoidance for sequential resource allocation systems: Hard and easy cases,” *Int. J. Flexible Manuf. Syst.*, vol. 13, no. 4, pp. 385–404, 2001.

[5] A. Nazeem and S. Reveliotis, “A practical approach for maximally permissive liveness-enforcing supervision of complex resource allocation systems,” *IEEE Trans. Autom. Sci. Eng.*, vol. 8, no. 4, pp. 766–779, Oct. 2011.

[6] G. I. Palmer, P. R. Harper, and V. A. Knight, “Modelling deadlock in open restricted queueing networks,” *Eur. J. Oper. Res.*, vol. 266, no. 2, pp. 609–621, Apr. 2018.

[7] N. Viswanadham, Y. Narahari, and T. L. Johnson, “Deadlock prevention and deadlock avoidance in flexible manufacturing systems using Petri net models,” *IEEE Trans. Robot. Autom.*, vol. 6, no. 6, pp. 713–723, Dec. 1990.

[8] Y. Lu, Y. Chen, C. N. Hadjicostis, and Z. Li, “Efficient iterative deadlock prevention for flexible manufacturing systems,” *Automatica*, vol. 174, Art. no. 112631, 2026.

[9] Y. Pang *et al.*, “Deadlock prevention in flexible manufacturing systems: A verification-free resource configuration approach for liveness of finite-capacity S3PR,” *Trans. Inst. Meas. Control*, 2025, doi: 10.1177/01423312251369553.

[10] H. Su *et al.*, “Partial-deadlock detection for S4PR nets via critical resource places,” *IEEE Trans. Autom. Sci. Eng.*, 2026, doi: 10.1109/TASE.2026.3689269.

[11] Y. Narahari, N. Viswanadham, and K. R. Krishna Prasad, “Markovian models for deadlock analysis in automated manufacturing systems,” *Sadhana*, vol. 15, pp. 343–353, 1990.

[12] IEEE Robotics and Automation Society, “Author checklist for papers submitted to IEEE T-ASE.” [Online]. Available: https://www.ieee-ras.org/publications/t-ase/information-for-authors-t-ase/author-checklist-for-papers-submitted-to-ieee-t-ase/

[13] H. Su *et al.*, “Reachability-decidable Petri net modeling,” *IEEE Trans. Syst., Man, Cybern. Syst.*, 2025, doi: 10.1109/TSMC.2024.3473851.

[14] H. Su *et al.*, “State-equation backward legal-firing-sequence approach,” *IEEE Trans. Syst., Man, Cybern. Syst.*, 2023, doi: 10.1109/TSMC.2023.3241101.

[15] P. J. G. Ramadge and W. M. Wonham, “Supervisory control of a class of discrete event processes,” *SIAM J. Control Optim.*, vol. 25, no. 1, pp. 206–230, Jan. 1987.

[16] K. Goldberg, “What is automation?,” IEEE Trans. Autom. Sci. Eng. editorial note, Mar. 2014. [Online]. Available: https://www.ieee-ras.org/images/publications/t-ase/What_is_Automation_March_2014.pdf

[17] Z. Li, M. C. Zhou, and N. Q. Wu, “A survey and comparison of Petri net-based deadlock prevention policies for flexible manufacturing systems,” *IEEE Trans. Syst., Man, Cybern. C*, vol. 42, no. 4, pp. 437–462, Jul. 2012.

[18] N. Wu and M. Zhou, “Resource-oriented Petri nets in deadlock avoidance of AGV systems,” in *Proc. IEEE Int. Conf. Robot. Autom.*, 2001, pp. 64–69.

---

## Figure Captions

**Fig. 1.** Object of the paper versus three classical pictures. A wait-for cycle, a plant-net siphon, and a plant terminal SCC are not identified with the computed object. A closed core \(K\) is only a candidate. Typed admission (Theorems 3–4) and bypass refusal (Theorem 5) produce the stopped first-hit of \(D^{\mathrm{G}}\), \(D^{\mathrm{L}}\), or \(F\). File: `docs/paper/figures/fig_research_object.pdf`.

**Fig. 2.** Exact first-hit KPIs on the *time-zero boundary* clothing of the three-job machine–AGV island. Base: already a local hit (\(\theta^{\mathrm{L}}=1\), \(m=0\)). Optional AGV drain: every trajectory completes. The *lead* island of Table II starts transient and hits \(D^{\mathrm{L}}\) at positive time. Files: `docs/paper/figures/fig_h4_island_kpis.pdf`, `.png`.

**Fig. 3.** Tandem scale (Family III, unit capacity). Left: \(\lvert X\rvert\) versus jobs (log). Right: runtime versus jobs (log). Horizontal guides mark \(10^3\), \(10^4\) states and the \(300\,\mathrm{s}\) cap. Files: `docs/paper/figures/fig_h3_scale.pdf`, `.png`.

---

*End of double-anonymous Regular Paper draft. Conversion to the IEEE two-column template is a later production step; scientific claims in that conversion must remain identical to this file.*
