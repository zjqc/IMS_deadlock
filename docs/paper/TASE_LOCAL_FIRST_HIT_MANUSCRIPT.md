# Typed Local First-Hit Analysis of Capacity-Mediated Blocking in Finite Manufacturing Resource-Allocation Systems

**IEEE Transactions on Automation Science and Engineering**  
Regular Paper (double-anonymous manuscript; author identities omitted)  
Manuscript type: Regular Paper  
Primary methodology (suggested): Discrete-event / resource-allocation analysis  
Primary application (suggested): Intelligent / flexible manufacturing systems

---

## Abstract

Wait-for cycles and unmarked plant-net siphons do not, by themselves, stop an operational manufacturing cell: residual capacity or a completion bypass can still finish the batch, while a local interlock can already make some jobs incomplete. This paper treats local blocking as a first hit of a certified bad set in a stopped process. A local closed kernel is admitted by a request-closed argument or by a complete finite labelled-transition-system audit that batch completion is unreachable, and is refused if a shortest bypass exists. Diagnostic siphons apply only on a unit-capacity, residual-zero, one-hold-one-request wait-snapshot; otherwise the method returns a typed refusal. After a certified absorption partition, exact continuous-time first-hit probabilities and discrete-event replications share one stopping hash. On a three-job machine–AGV island the initial state is already a local hit (\(\theta_\ell=1\)); an optional AGV drain yields \(\theta_b=0\), with six exact/simulation cells inside a Hoeffding band of \(7.35\times 10^{-3}\) at \(n=65536\). A ten-plant table gives four siphon agreements and four typed refusals (false positives and false negatives zero). A tandem family reaches \(10^3\)–\(10^4\) states and refuses three rows at a declared cap. The increment is this checkable first-hit object, not a plant-net liveness theorem or a shop-floor controller.

*Abstract word count: 197.*

## Note to Practitioners

This work was motivated by a cell-control question: when two jobs hold a machine and an automated guided vehicle (AGV) and wait for each other, has the batch already failed, or can it still finish if a buffer slot or another unload remains? A cycle on the wait graph is not a reliable stop. Leftover capacity or a later bypass can still complete every job, and cutting the “obvious” edge can create a new interlock. The quantity computed here is the first time the cell enters a certified blocked set, not the event that the plant graph has no outgoing arc. If every move of a waiting job must use its current request, a local closed kernel is enough to conclude those jobs will never finish; otherwise the kernel is kept only after a complete finite state graph shows that batch completion is unreachable, and it is dropped if a bypass appears. Siphon language is used only when every core resource is unit capacity, fully occupied, and requested one-for-one; otherwise the method returns “not applicable” instead of installing a monitor. On a synthetic three-job island, allowing the AGV holder to leave without entering the contested machine changes the cell from already locally stopped to all jobs finishing. Exact probabilities and simulations are compared only after they share the same stopping rule. The island is not factory data, the method is not a shop policy, and it does not replace a published Petri-net supervisor on a vendor cell. It is a pre-release audit of a finite digital twin.

*Note to Practitioners word count: 257.*

## Index Terms

Automated guided vehicles, deadlock, discrete-event systems, flexible manufacturing systems, Markov processes, Petri nets, resource allocation, supervisory control.

---

## I. Introduction

Finite-capacity manufacturing cells allocate machines, buffers, and transporters to a finite set of jobs that hold resources after service (blocking after service) and may request several resources at once. A classical diagnosis of a stop is a directed cycle in a wait-for graph, a knot in a state-dependent blocking graph, or an empty siphon of a plant Petri net [1]–[6]. Those objects are inexpensive to state and, on the subclasses for which they were proved, they are correct. They are not interchangeable with an *operational* stop of an intelligent manufacturing system (IMS) model that records residual capacity, OR-of-AND requests, AGV occupancy, and a declared transition registry.

Three mismatches appear as soon as the model is operational rather than purely structural. First, a residual-feasible cycle is not a deadlock: a job can still acquire the residual unit and complete [4], [6]. Second, a local interlock among a subset of jobs can already make batch completion unreachable while another job continues—so the plant labelled transition system (LTS) still has outgoing arcs [7]. Calling that local interlock a terminal strongly connected component (SCC) is a category error. Third, a completion bypass—an enabled sequence that ignores the current request and finishes a kernel job after an outside release—means that the local cycle was never irreversible. Promoting it to a bad absorbing class falsifies the subsequent probability.

A fourth mismatch is linguistic. Empty-siphon control on S3PR/S4PR plant nets [1], [3], [8], [9] and critical-resource-place (CRP) characterizations of partial deadlock [10] are mature. They are not automatically certificates of the IMS operational state. A wait-snapshot dual exists only on a narrow unit-capacity subclass; outside that subclass the honest output is a typed refusal, not a monitor.

This paper therefore changes the *object* that is computed. Local blocking is treated as a first hit of a certified bad set \(D_\mathrm{local}\) (or of the covering global set \(D_\mathrm{global}\)) in a *stopped* process, not as a terminal SCC of the plant. Admission of a local kernel to \(D_\mathrm{local}\) is typed:

1. under CW1–CW10 and the request-closed discipline A2b, a local closed kernel makes every kernel job permanently incomplete, hence batch completion \(F\) is unreachable (Theorem 4);
2. if A2b cannot be verified, the same candidate is admitted only after a complete, untruncated LTS audit shows that \(F\) is unreachable from that state (Theorem 5), and is refused if a shortest completion bypass exists (Theorem 6).

After the absorption domain is certified—no unselected closed class, no truncated LTS—exact first-hit probabilities on the stopped continuous-time Markov chain (CTMC) and independent discrete-event (DES) replications share one stopping hash. Agreement inside a predeclared simultaneous Hoeffding band is a numerical check, not a proof of the theorem and not a claim of plant fidelity [11].

The experimental clothing is a new discovery panel with a distinct scope identifier. It is not a relabelling of a six-case constructive manuscript and not a historical replay of a failed CRP encoding. Four families are reported.

- *Island.* A three-job machine–AGV cell starts already locally stopped (\(\theta_\ell=1\), mean stopped time \(0\)). An optional one-slot AGV drain sends every sample path to completion (\(\theta_b=0\), mean time \(3.23\)). Six probability cells agree with DES at \(n=65536\) inside tolerance \(7.35\times 10^{-3}\).
- *Baselines.* Ten plants are scored by a wait-for/SCC screen, a closed-core certificate, a siphon-or-refuse predicate, and LTS truth. Four plants agree with the diagnostic siphon; four refuse it for OR, AND, multi-capacity, or conjunctive AGV demand; false positives and false negatives are both zero.
- *Scale.* A tandem family enumerates twelve rows with at least \(10^3\) stable states and four with at least \(10^4\), and refuses three rows at \(10^5\) states or \(300\,\mathrm{s}\).
- *CRP diagnostic.* Proposition 8’s four fields are scored on six new subjects. Fields 1–3 (reachability, local family, resource match) can hold; field 4 (independent S4PR embedding) is refused on every row. Bridge agreement is therefore zero. A prior implementation-level CRP encoding remains a negative witness; it is not a refutation of the source theorem [10].

The publishable increment is the checkable first-hit object and its typed admission/refusal rules. The paper does not claim a new siphon-control policy, a general IMS–S3PR isomorphism, a bit-polynomial reachability procedure, a shop-floor throughput gain, or priority over PDDP/CRP/monitor synthesis [3], [8]–[10].

Section II places the increment against Petri, RAS, knot, and probability baselines. Sections III–IX give the complete formal development: the capacity-aware closed-wait subclass, the finite LTS representation, the covering-core characterization of global operational deadlock, the wait-snapshot siphon dual, the two typed local-admission routes with full proofs, a chain-decomposable sufficient condition, and the stopped-process first-hit equations including invertibility and first-jump derivations. Section X reports the four experimental families. Section XI records limitations. Section XII concludes. Family-specific exact thresholds (BIX1/BIX2) are proved in Appendix C so that the original derivation is not abbreviated out of the archival draft.

---

## II. Related Work

T-ASE asks that a Regular Paper compare methods and cite archival work from the last two years [12]. The comparison here is organized by the *object* each literature family computes, not by a priority slogan.

### A. Wait-For Cycles, Knots, and Sequential RAS

A directed wait-for cycle is the oldest operational picture of deadlock. In sequential single-unit resource allocation it is tightly connected to safety: Lawley and Reveliotis proved that SU-SAFE is NP-complete and isolated structural subclasses that eliminate deadlock-free unsafe states [4]. Palmer, Harper, and Knight characterized deadlock of open restricted queueing networks by a knot in a state-dependent blocking graph and exhibited 2-/3-server counterexamples to a weakly-connected-component shortcut [6]. Those results remain the correct baselines for a cycle/SCC *screen*. They do not treat residual capacity, OR-of-AND alternatives, and BAS hold-after-service as first-class IMS tokens, and a residual-feasible cycle is not an IMS deadlock. Family II below keeps the cycle/SCC column precisely so that this false-positive mode stays visible.

Banker’s-algorithm and ordered-avoidance tests are sufficient safety filters on sequential RAS. They are not theorems of the IMS operational model once AGV occupancy and reservations are tokens.

### B. Petri-Net Siphons, Monitors, and Finite-Capacity Configuration

Ezpeleta, Colom, and Martínez gave the S3PR liveness and siphon-control policy that still organizes the plant-net school [1]. Li and Zhou refined the construction with elementary siphons [2]. Chen and Li formulated maximally permissive monitor synthesis as a marking/place-covering problem (MCPP) whose optimum exists only when a monitor supervisor is expressible; full reachability-graph enumeration is exponential and MCPP is NP-hard [3]. Pang *et al.* gave sufficient liveness and resource-configuration conditions for finite-capacity S3PR after an ENS3PR transformation, with a worst-case SMS bound \(O(2^{N_p})\) [9]. None of these results is an IMS operational certificate: they assume a plant-net subclass, not BAS blocked-unload, AGV occupancy, or OR-of-AND acquisition. The present paper uses an empty siphon only as a *diagnostic dual* of a wait-snapshot net on the unit-capacity subclass IMS-SIP\(^1\) (Theorem 3) and refuses the dual outside that subclass.

### C. Partial Deadlock, MR2G/PDDP, and CRP

Lu, Chen, Hadjicostis, and Li characterized partial deadlock of bounded FMS Petri nets by a modified resource-requirement graph (MR2G) and a PDDP predicate, and synthesized control places iteratively [8, Def. 3, Th. 1]. Su *et al.*, in this Transactions, characterized partial deadlock of S4PR at a marking by a critical resource place (CRP) and delegated reachability of candidates to a structural backward algorithm (SBA) [10, Defs. 5–8, Ths. 1–4]. Those papers are the closest 2025–2026 comparators. They do not supply an IMS operational certificate, a typed bypass refusal, or a first-hit probability on a certified stopped process. CRP equations alone are not a reachable-prefix proof [10]. A four-field partial-bridge *rule* (reachability, local family, resource equality, declared S4PR overlap) is stated as Proposition 4; without an independent S4PR embedding the fourth field is refused and agreement is not claimed. A historical implementation that used a global extractor in the presence of an unrelated job remains a negative witness; it does not refute [10].

Recorder-place and transformed-net reachability procedures [13], [14] decide legal firing sequences after a model transform. They are not used here as an IMS reachability engine; the operational LTS is enumerated directly and refused when truncated.

### D. Supervisory Control and Finite-State LES

Ramadge and Wonham formulated nonblocking supervisory control of discrete-event processes [15]. Nazeem and Reveliotis gave a practical maximally permissive liveness-enforcing supervisor for complex RAS via a boundary-unsafe-state representation [5]. Those constructions remain the right *finite-state supervisor* baselines. They are not the centre of this paper: the centre is a typed first-hit set, not a supremal controllable sublanguage and not a compact monitor.

### E. Absorbing Markov Models

Narahari, Viswanadham, and Krishna Prasad computed mean time to deadlock and absorption probabilities on finite manufacturing Markov models [11]. The linear algebra is classical. The modelling obligation that is easy to miss—and that this paper enforces—is that the absorbing classes must be the *same* certified first-hit sets used by the theorem, and that an unselected closed class makes the committor undefined. Exact/DES agreement on that shared target is a check, not a new CTMC theorem.

### F. Positioning Sentence

Table I records the five-axis difference. The paper adds a *checkable object* (typed \(D_\mathrm{local}/D_\mathrm{global}/F\) with a bypass refusal and a certified absorption domain). It does not add a new siphon, a new CRP equation, or a new polynomial reachability algorithm.

**Table I**  
Difference of computed objects (not a priority ranking)

| Family | Object they compute | Assumption not inherited here | Checkable addition |
| --- | --- | --- | --- |
| Cycle / SCC / knot [4], [6] | directed cycle or knot | residual, OR-of-AND, BAS | closed core; residual cycle \(\neq\) deadlock |
| S3PR siphon / MCPP [1], [3] | empty siphon; monitor cover | plant S3PR; compact monitor | wait-snapshot dual on IMS-SIP\(^1\); typed refusal |
| Finite-capacity S3PR [9] | sufficient marking inequalities | exact reachable iff threshold | none as a main theorem |
| PDDP / MR2G [8] | local marking deadlock | local cycle \(\Rightarrow\) irreversible failure | A2b or complete-LTS; bypass refusal |
| S4PR CRP [10] | CRP iff partial deadlock, then SBA | S4PR embedding; CRP set \(=\) local kernel | four-field rule; no SBA in this paper |
| Absorbing CTMC [11] | \(\theta\), mean time | almost-sure hit of a declared \(D/F\) | certified \(S_T\); same-target DES hash |

---

## III. Capacity-Aware Closed-Wait Semantics

All theorems below are stated on a restricted finite subclass, written \(\mathrm{IMS\text{-}RAS}^{CW}\) (capacity-aware closed wait). They do not cover general IMS-RAS, classical S3PR structural equivalence, soft reservations, non-Markov timing, infinite arrivals, failures, preemption, or online job insertion.

### A. Structural Hypotheses CW1–CW10

- **CW1 (Finiteness).** The job set \(J\), resource set \(R\), capacities \(\mathrm{cap}(r)\in\mathbb{Z}_{>0}\), route stages, hard-reservation tokens, and event templates are finite.
- **CW2 (Closure normalization).** Every main statement is made on the set \(S_{\mathrm{st}}\) of stable states. After each non-zero-time event a zero-time closure is executed and terminates. If the closure is non-confluent, all stable successors are retained as a set.
- **CW3 (Capacity conservation).** For a physical resource, \(\mathrm{occ}_s(r)=\sum_j \mathrm{hold}_s(j,r)\le\mathrm{cap}(r)\). For a hard-reservation token \(v\), \(\mathrm{book}_s(v)=\sum_j \mathrm{res}_s(j,v)\le\mathrm{cap}(v)\). Soft reservations are excluded from the completeness theorems.
- **CW4 (Finite capacity-ready alternatives).** For each unfinished job \(j\) at \(s\in S_{\mathrm{st}}\), every currently guard-ready direct progress is written as a finite OR-of-AND family \(\mathrm{Alt}_s(j)=\{a_1,\ldots,a_m\}\). Each alternative \(a\) is a demand vector \(\mathrm{need}_s(j,a,r)\in\mathbb{N}\). Non-capacity guards that are not yet true do not enter \(\mathrm{Alt}_s(j)\). Every currently enabled timed or transport completion enters as an *empty* demand alternative.
- **CW5 (Atomic acquisition).** An acquisition/progress event may fire only if some alternative \(a\) satisfies \(\mathrm{avail}_s(r)\ge\mathrm{need}_s(j,a,r)\) for every \(r\), simultaneously. Partial acquisition is forbidden.
- **CW6 (BAS/AGV hold).** A blocked-after-service holder, a blocked unload, or a committed AGV does not release its resource until a successful acquire/unload/handoff/leave or a designated completion-release.
- **CW7 (Autonomous-release decidability).** For every holding it is decidable whether a release exists that does not require a new acquisition. Witness capacity used by a certificate must be explained by a non-autonomous holding or a hard reservation.
- **CW8 (Event taxonomy).** Non-zero-time events at a stable state fall into four classes: timed/transport completion; acquire/dispatch/reservation/transport choice; unload/handoff/release; completion/marking. Zero-time events occur only inside the closure.
- **CW9 (First-paper exclusions).** No device failure, preemption, dynamic insertion, infinite exogenous arrival, or soft-reservation oversell.
- **CW10 (Policy stall excluded).** A stall created by disabling controllable events is not operational deadlock. A calendar-empty *terminal-block interpretation* is a separate boundary and is not mixed into a structural certificate. The Boolean `event_calendar_empty` only records that no timed event is currently scheduled; it is not synonymous with that interpretation.

These are hypotheses. If any fails, the implementation returns a structured refusal.

### B. Availability and Direct Progress

Write \(\mathrm{avail}_s(r)\) from CW3. Alternative \(a\) is capacity-feasible at \(s\) if and only if \(\mathrm{avail}_s(r)\ge\mathrm{need}_s(j,a,r)\) for all \(r\). If \(j\) is complete, \(\mathrm{Alt}_s(j)=\emptyset\). If the next step is an enabled timed completion, a pure completion mark, or a release that needs no new capacity, the corresponding alternative has the zero demand vector. If \(j\) is blocked after service or blocked on unload, \(\mathrm{Alt}_s(j)\) contains every currently guard-ready unload, handoff, output-buffer entry, AGV claim, or reservation redeem.

A *capacity-gap witness* for \((j,a)\) is a resource \(r\) with \(\mathrm{need}_s(j,a,r)>\mathrm{avail}_s(r)\). An empty demand has no capacity-gap witness.

### C. Request-Closed Discipline A2b

A2b is used *only* for the structural local-noncompletion theorem. For every unfinished job with uncleared requests, every transition that would change that job’s mode, holdings, requests, or completion consumes at least one currently feasible alternative of \(\mathrm{Alt}_s(j)\). There is no same-mode bypass that depends on an outside resource, a guard, or an intermediate mode. If A2b cannot be proved statically, the complete-LTS route of Section VII-C must be used.

Probability constructions add **A8**: the stable LTS is complete and untruncated, and a frozen positive rate manifest is supplied. Scientific execution re-enumerates the LTS from the same model, initial stable state, and registry, and requires state signatures and plant arcs to match.

---

## IV. Finite LTS and Reachability-Net Representation

**Lemma 1 (Representation; Theorem P1).**  
Let \(I\) be any \(\mathrm{IMS\text{-}RAS}^{CW}\) model and \(s_0\in S_{\mathrm{st}}\) an initial stable state. There exists a finite closure-normalized LTS
\[
\mathcal T_I=(X,x_0,E,\to,F,D)
\]
and a 1-safe bounded Petri net \(N_I=(P,T,\mathrm{Pre},\mathrm{Post},M_0)\) such that the reachable stable states \(X\) are in bijection with \(\mathrm{Reach}(N_I,M_0)\), and every LTS edge corresponds to exactly one Petri transition.

This is a representation lemma, not an S3PR structural equivalence and not a siphon theorem.

*Construction.* By CW1–CW3 every job stage, blocking mode, holding, reservation, and pending-free configuration is taken from a finite set. Let \(X\) be the set of stable states reachable from \(s_0\) after CW2 closure. Then \(X\) is finite. For \(x,y\in X\) and a non-zero-time event \(e\), draw an LTS edge \(x\xrightarrow{e} y\) whenever there is an immediate successor \(u=\mathrm{fire}(x,e)\) with \(y\in\mathrm{Cl}(u)\). If the closure is multi-valued, one edge is drawn for each \(y\in\mathrm{Cl}(u)\).

Build \(N_I\) as follows: one place \(p_x\) for each \(x\in X\); one transition \(t_b\) for each LTS edge \(b=(x,e,y)\); \(\mathrm{Pre}(p_x,t_b)=1\), \(\mathrm{Post}(t_b,p_y)=1\), and all other arc weights zero; \(M_0(p_{s_0})=1\) and \(M_0(p_x)=0\) otherwise. Write \(\phi(x)\) for the marking with a single token on \(p_x\).

*Proof of finiteness.* \(X\) is a subset of a finite configuration space. Edges are generated by a finite event template, so \(N_I\) is finite.

*Proof of 1-safety.* \(M_0\) has one token. Every transition consumes exactly one state-place token and produces exactly one state-place token. By induction on the firing sequence every reachable marking has total token count one and every place is 0-1. Hence \(N_I\) is 1-safe and bounded.

*Proof of forward path preservation.* For the empty path, \(x=s_0\) and \(\phi(x)=M_0\). If a path to \(x\) corresponds to \(\phi(x)\) and \(x\xrightarrow{e} y\) exists, the construction supplies \(t_b\) with unique input \(p_x\). That transition is enabled under \(\phi(x)\) and yields \(\phi(y)\).

*Proof of backward path preservation.* The empty firing sequence is \(M_0=\phi(s_0)\). If a reachable marking is \(\phi(x)\), every enabled transition has input \(p_x\) and therefore comes from some LTS edge \(x\xrightarrow{e} y\). Firing it yields \(\phi(y)\).

*Proof of bijection.* \(\phi\) is injective by construction. Forward and backward preservation show that every LTS-reachable state is Petri-reachable and every Petri-reachable marking equals some \(\phi(x)\). \(\square\)

Lemma 1 uses only CW1–CW3 and CW2. It does not use S3PR hypotheses. If infinite arrivals, unbounded soft oversell, or a nonterminating closure are added, \(X\) may be infinite or undefined, and the lemma is outside its scope.

---

## V. Closed Blocking Cores and Global Operational Deadlock

### A. Closed Blocking Core

**Definition 6 (Closed blocking core).**  
At \(s\in S_{\mathrm{st}}\), a tuple \(K=(J_K,R_K,W_K,H_K)\) is a *closed blocking core* if and only if all five conditions hold independently.

1. *Nonempty unfinished.* \(J_K\neq\emptyset\) and every \(j\in J_K\) is unfinished.
2. *Every alternative blocked.* For every \(j\in J_K\) and every \(a\in\mathrm{Alt}_s(j)\) there is a record \((j,a,r)\in W_K\) with \(r\in R_K\) a capacity-gap witness of \(a\).
3. *Gap explanation.* For every witness \((j,a,r)\), writing \(\mathrm{block}_K(j,a,r)\) for the sum of non-autonomous kernel holdings recorded in \(H_K\) for that witness,
   \[
   \mathrm{need}_s(j,a,r)>\mathrm{cap}(r)-\mathrm{block}_K(j,a,r)-\mathrm{fixed\_out}_s(r).
   \]
   When \(K\) is used as a *covering* global certificate, \(\mathrm{fixed\_out}_s(r)=0\). The same holder may appear in several witness records; each inequality is audited only with its own \(\mathrm{block}_K(j,a,r)\).
4. *Release dependence.* Every holding recorded in \(H_K\) has no legal release/unload/handoff that frees the corresponding capacity without firing a capacity-ready alternative already blocked by condition 2.
5. *At least one genuine waiter.* Some \(j\in J_K\) has \(\mathrm{Alt}_s(j)\neq\emptyset\) and is waiting, blocked after service, blocked on unload, waiting for transport, or waiting to redeem a hard reservation.

\(K\) *covers* \(s\) if and only if \(J_K\) equals the set of all unfinished jobs of \(s\) that are not calendar-empty terminal-boundary jobs. Definition 6 does *not* take “no successor” as a hypothesis, so the subsequent theorem is not tautological.

**Definition 7 (Capacity-mediated global operational deadlock).**  
A stable state \(s\) is a capacity-mediated global operational deadlock if and only if (i) \(s\) is a general global operational deadlock (no admissible successor to a different stable state); (ii) \(s\) is not a policy stall, calendar-empty terminal block, permanent non-resource guard, permanent missing synchronization, or other unmodelled external boundary; (iii) every covered unfinished job has nonempty capacity-ready \(\mathrm{Alt}_s(j)\); (iv) every currently enabled timed/transport completion has entered \(\mathrm{Alt}_s(j)\) as an empty demand, hence no such completion is enabled at \(s\).

### B. Equivalence

**Theorem 2 (Covering core \(\Leftrightarrow\) capacity-mediated global deadlock; P2).**  
In \(\mathrm{IMS\text{-}RAS}^{CW}\), a stable state \(s\) is a capacity-mediated global operational deadlock if and only if \(s\) admits a covering closed blocking core.

*Proof of \(\Rightarrow\).* Let \(s\) be a capacity-mediated global operational deadlock and let \(U_s\) be the set of unfinished non-terminal-boundary jobs. Then \(U_s\neq\emptyset\), every covered blocked job has nonempty capacity-ready \(\mathrm{Alt}_s(j)\), and at least one job is waiting or blocked. Set \(J_K=U_s\).

Fix \(j\in J_K\) and \(a\in\mathrm{Alt}_s(j)\). If \(a\) had no capacity-gap witness, then by the capacity-ready definition all non-capacity guards would hold, by CW5 the alternative would be capacity-feasible, and by CW8 the corresponding acquire/progress/release/completion event would be in the taxonomy; firing it and applying CW2 would produce a stable successor, contradicting global operational deadlock. Hence every alternative has at least one witness. Collect all such resources into \(R_K\) and all triples into \(W_K\).

For gap explanation: \(\mathrm{avail}_s(r)<\mathrm{need}_s(j,a,r)\) means that occupancy or hard reservation already saturates \(r\). Any unfinished outside holder of that shortage would belong to \(U_s=J_K\), a contradiction. A completed job cannot hold a machine, buffer, AGV, or reservation token. An environmental occupancy of calendar-empty terminal-block type is excluded by the theorem’s premise. Therefore, when \(K\) covers a global deadlock, the shortage is explained by kernel holdings or hard reservations. Choose enough non-autonomous kernel holdings to form \(H_K\) so that condition 3 holds.

For release dependence: if a holder used to explain a witness could release that resource without progressing a blocked alternative, that release would be guard-ready and would enter \(\mathrm{Alt}_s(j_h)\) (as an empty demand if no new capacity is needed). CW8 and CW2 would produce a stable successor, contradicting deadlock. Hence those holdings may be chosen non-autonomous, and condition 4 holds.

Conditions 1–5 are therefore satisfied, and \(K\) covers \(s\).

*Proof of \(\Leftarrow\).* Let \(K\) be a covering closed blocking core. We show that \(s\) has no admissible successor, by the CW8 taxonomy.

1. *Acquire/dispatch/reservation/transport choice.* If the non-capacity guards of such an event hold, it corresponds to some unfinished job \(j\) and some capacity-ready alternative \(a\). Coverage gives \(j\in J_K\). Condition 2 supplies a capacity-gap witness, so CW5 forbids the event. If the guards do not hold, the event is not currently admissible.
2. *Unload/handoff/release.* If the event is legal for an unfinished job it is a direct-progress alternative. If it needs no new resource it is an empty demand, so condition 2 cannot hold unless the event is not actually enabled; if it needs an output buffer, a handoff slot, an AGV, or a reservation redeem, condition 2 supplies a witness and the event cannot fire. If it claimed to free certificate-explaining capacity without depending on a blocked alternative, it would also violate condition 4. Completed jobs hold nothing. External terminal blocks are excluded.
3. *Timed/transport completion.* Every currently enabled completion is an empty-demand alternative by CW4. An empty demand has no capacity-gap witness, contradicting condition 2. Hence no such completion is enabled. A completion whose clock has not matured is not currently admissible. If completion still requires a blocked unload, CW6 says the holder is not released, and the subsequent unblock is again a capacity-ready alternative, already blocked.
4. *Completion/marking.* If a job can complete and release every resource, its alternative is empty or capacity-feasible, contradicting condition 2. If every job is already complete, conditions 1 and coverage fail.
5. *Zero-time closure.* \(s\in S_{\mathrm{st}}\), so no zero-time event is enabled. Closures after non-zero-time events are already accounted for in (1)–(4).

Thus there is no admissible successor to a different stable state. Coverage and condition 5 give incompleteness and a genuine waiter. Conditions 2 and Definition 6 give that every covered block is a capacity gap on a capacity-ready alternative, not a permanent non-resource guard, missing synchronization, policy stall, or calendar-empty terminal block. Therefore \(s\) is a capacity-mediated global operational deadlock. \(\square\)

**Corollary 1 (P2a).**  
If \(s\) admits a covering closed blocking core, it admits an inclusion-minimal one. The partial order is componentwise inclusion of \(J_K,R_K,W_K,H_K\). Finiteness of \(J,R\) and of the witness set supplies a minimal element. Inclusion-minimality is not uniqueness, not minimum cardinality, and not minimum capacity increment.

**Corollary 2 (P2b; unit one-hold-one-request).**  
In the additional subclass where every key resource has capacity one, every blocked job holds exactly one key resource and requests exactly one key resource, there is no alternate route, no split hard reservation, no residual, and a holder releases its current resource only after acquiring the requested one: (i) every terminal SCC \(C\) of the resource wait-for digraph defines a local closed core \(K_C\) whose jobs are exactly the holders in \(C\); conversely every inclusion-minimal local closed core induces exactly one terminal SCC; if every out-degree is one, that SCC contains a simple directed cycle; (ii) if some \(K_C\) covers every unfinished job, Theorem 2 yields a capacity-mediated global deadlock.

*Proof of Corollary 2.* Each blocked alternative has a single requested resource, and a capacity gap means that resource is held by a kernel job, so each blocked job has a wait-for edge to a holder. If \(C\) is a terminal SCC, every requested holder remains in \(C\) and there is no outgoing edge, so \(K_C\) is a local closed core. Conversely, if \(K\) is inclusion-minimal, the induced wait-for graph has out-degree one and all edges stay inside \(K\). If it contained several terminal SCCs or a predecessor outside a terminal SCC, deleting the predecessor or retaining one terminal SCC would preserve closed blocking, contradicting inclusion-minimality. Coverage lifts the local statement to the global one. The corollary does not apply to multi-capacity, multi-request, OR-of-AND, AGV/reservation splits, or residual capacity. \(\square\)

---

## VI. Wait-Snapshot Siphon Dual

**Definition 8 (IMS-SIP\(^1\)).**  
A local core \(K\) at a reachable stable state \(s\) lies in IMS-SIP\(^1\) when: a reachability witness is attached (\(s\) itself may have the empty prefix); \(K\) is inclusion-minimal; every core resource or hard-reservation token has unit capacity and residual zero; every core job holds exactly one core resource \(h(j)\) and has exactly one current alternative, which requests exactly one unit of a core resource \(q(j)\); there is no OR, no conjunctive AND, no soft reservation, no external guard, no hidden release, and no release-affecting non-confluent closure. An AGV or hard-reservation token may enter only as an ordinary unit resource.

The implementation checks the mechanical hypotheses (witness, minimality, stability, unit capacity, one-hold-one-request, no OR/AND, residual marking). Closed-world completeness, absence of hidden releases, satisfied guards, and closure semantics remain proof obligations on the registry. The check is not a plant/S3PR bisimulation.

*Wait-snapshot net.* Places \(P_K=\{\mathrm{free}{:}r\mid r\in R_K\}\); marking \(M_s(\mathrm{free}{:}r)=\mathrm{cap}(r)-\mathrm{occ}_s(r)\); for each \(j\in J_K\) a transition \(t_j\) with \(\mathrm{Pre}(t_j)=\{\mathrm{free}{:}q(j)\}\) and \(\mathrm{Post}(t_j)=\{\mathrm{free}{:}h(j)\}\). The transition \(t_j\) is *not* an IMS event; it is the diagnostic projection “the current resource can be freed only after the requested resource is obtained.” This net is distinct from the one-place-per-state net of Lemma 1.

**Theorem 3 (P2c).**  
At a reachable stable IMS-SIP\(^1\) state, inclusion-minimal local closed cores are in bijection with inclusion-minimal empty siphons of the wait-snapshot net.

*Proof of \(\Rightarrow\).* Let \(\Sigma_K=\{\mathrm{free}{:}r\mid r\in R_K\}\). Unit capacity and residual zero imply that \(\Sigma_K\) is empty under \(M_s\). Every transition that outputs into \(\mathrm{free}{:}h(j)\) is \(t_j\), whose unique input \(\mathrm{free}{:}q(j)\) still lies in \(\Sigma_K\). Hence \(\bullet\Sigma_K\subseteq\Sigma_K\bullet\), so \(\Sigma_K\) is an ordinary siphon. If a proper subset were an empty siphon, the one-hold-one-request semantics would recover a proper subcore, contradicting inclusion-minimality of \(K\).

*Proof of \(\Leftarrow\).* Let \(\Sigma\) be an inclusion-minimal empty siphon and \(R_\Sigma=\{r\mid\mathrm{free}{:}r\in\Sigma\}\). Emptiness and unit capacity imply that each \(r\in R_\Sigma\) is held by exactly one core job. The siphon condition says that every holder transition that outputs into \(R_\Sigma\) requests, before that release, a resource still in \(R_\Sigma\). One-hold-one-request and the absence of alternatives therefore recover a local closed core. If that core were not inclusion-minimal, its proper subcore would yield a proper empty siphon, a contradiction. \(\square\)

Theorem 3 does not apply to conjunctive requests, OR routes, multi-capacity residuals, soft reservations, control-only/approval-only siphons, or any Petri auxiliary place that lacks a job hold–request evidence edge.

---

## VII. Typed Local First-Hit

### A. Local Kernel and \(D_{\mathrm{local}}\)

A *local* closed blocking kernel is a closed core in the sense of Definition 6 that need not cover every unfinished job. Write \(K_{\mathrm{local}}\) for the set of non-global states that contain at least one inclusion-minimal local core. A state of \(K_{\mathrm{local}}\) is only a *candidate*: it proves present blocking, not future noncompletion.

**Definition 9 (\(F\), \(D_{\mathrm{global}}\), \(D_{\mathrm{local}}\)).**  
\(s\in F\) if and only if every job is complete, no resource is held, and no request remains. \(s\in D_{\mathrm{global}}\) if and only if \(s\) satisfies Definition 7. \(s\in D_{\mathrm{local}}\) if and only if \(s\notin D_{\mathrm{global}}\), \(s\in K_{\mathrm{local}}\), and either Theorem 4 applies or Theorem 5 applies. Classification precedence is
\[
F \;\text{excluded first},\quad\text{then }D_{\mathrm{global}},\quad\text{then }D_{\mathrm{local}}.
\]
Thus the three sets are pairwise disjoint. Precedence is a versioned estimand convention, not a physical law.

\(D_{\mathrm{local}}\) may have outgoing *plant* arcs, because outside jobs may still move. Membership says that the declared failure event has occurred, not that the plant graph is terminal. The plant process is unchanged; the *stopped* process deletes outgoing arcs only after a selected target has been hit.

### B. Request-Closed Noncompletion

**Theorem 4 (A2b local noncompletion; Theorem 1 of the claim ladder).**  
Assume CW1–CW10 and A2b. If a stable state \(s\) contains a local closed kernel \(K=(J_K,R_K,W_K,H_K)\), then on every plant path from \(s\) every job in \(J_K\) remains incomplete and the requests present at the hit remain unsatisfiable. Consequently \(F\) is unreachable from \(s\).

*Proof.* The argument is the capacity invariant, not identity of a serialized certificate.

1. By Definition 6(5) and the local-kernel reading of “no enabled transition for \(J_K\)”, no kernel job is enabled at \(s\). By the complete-registry hypothesis this is not an omitted-transition false negative.
2. By per-job ownership (the A2 reading of CW8), an outside transition changes only its own job’s mode, holdings, requests, and completion. It cannot complete a job of \(J_K\) and cannot rewrite a kernel job’s request vector.
3. By CW6, CW7, CW9 (no preemption, no failure, no exogenous release) and the completion convention that a completed job holds nothing, a witness unit held by \(J_K\) at the hit is not released by an outside event.
4. *Capacity invariant.* For each witness resource \(r\), write \(L_s(r)\) for the number of units of \(r\) locked by \(J_K\) at the hit. Then \(L\) is nonincreasing along any path (step 3), and
   \[
   \mathrm{avail}_{s'}(r)\;\le\;\mathrm{cap}(r)-L_{s'}(r)\;\le\;\mathrm{cap}(r)-L_s(r)
   \]
   at every successor \(s'\). Outside jobs may occupy and later release only the residual that was already free at the hit; they cannot raise availability of those witness units above the hit-state bound.
5. Definition 6(2)–(3) says that every alternative of every kernel job is short of at least one witness resource by more than that residual. Combined with step 4, no such alternative ever becomes capacity-feasible.
6. A2b excludes a progress, release, or completion transition that ignores the unresolved requests. Therefore no kernel job ever acquires a feasible alternative or fires a progress/release/completion transition.
7. \(F\) requires every job to complete, in particular every job of \(J_K\). This contradicts step 6.

Hence \(F\) is unreachable. The forward invariant is kernel-job noncompletion and request blockedness. The certificate extractor need not return the same JSON at later states: outside jobs may occupy residual, so a syntactic “all current holders lie in \(J_K\)” test can flicker; state identifiers, prefixes, and residual vectors may change. \(\square\)

A2b is sufficient, not necessary. The theorem does not say that every local deadlock arises from A2b.

### C. Complete-LTS Fallback and Bypass Refusal

**Theorem 5 (Model-specific semantic admission).**  
Suppose A2b is not established. Let \(\mathcal T_I\) be the complete, untruncated LTS of Lemma 1 generated from the same registry. A candidate \(x\in K_{\mathrm{local}}\) may be placed in \(D_{\mathrm{local}}\) if and only if no directed plant path of \(\mathcal T_I\) from \(x\) to any state of \(F\) exists.

*Proof.* If such a path exists, then from \(x\) a finite event sequence reaches batch completion, so treating \(x\) as an irreversible bad hit is unsound for this model: the first-hit probability of “selected bad before \(F\)” would charge a path that in fact reaches \(F\). Conversely, if the LTS is complete and no path to \(F\) exists, every trajectory from \(x\) remains forever outside \(F\). Using \(x\) as a stopping set of the stopped process is then sound *for that enumerated model*. The argument is exhaustive reachability on a finite graph. It does not create a structural theorem for unenumerated or infinite models. \(\square\)

**Theorem 6 (Bypass refusal).**  
If \(\mathcal T_I\) contains a path from the candidate to a state of \(F\), the candidate is refused, the shortest event prefix is retained as a counterexample, and the candidate is not entered into \(D_{\mathrm{local}}\).

The two routes are alternatives, not competitors required to cover the same plant.

| Route | What it proves | Required boundary | Correct failure |
| --- | --- | --- | --- |
| A2b (Theorem 4) | structural noncompletion of \(J_K\) | per-job semantics and no request-independent bypass | refuse A2b; use Theorem 5 if the LTS is complete |
| Complete LTS (Theorem 5) | \(F\)-nonreachability in one finite model | complete untruncated registry | return the path (Theorem 6) or a structural refusal |

### D. All-Minimal Enumeration

**Proposition 5 (Soundness).**  
Every local certificate returned by cardinality-increasing blocked-job enumeration followed by inclusion-minimal resource-witness filtering satisfies Definition 6.

**Proposition 6 (Completeness).**  
If \(s\) contains an inclusion-minimal local closed kernel, the same enumeration returns it. Finiteness is CW1.

**Proposition 7 (Order independence).**  
Truth values do not depend on first-hit enumeration order. Output order may be canonicalized; a bridge judgment must quantify the entire minimal-kernel family.

**Proposition 8 (CRP partial bridge).**  
Given a frozen target and a declared resource set \(R_{\mathrm{crp}}\), partial-bridge *agreement* is true only if all four hold independently: (i) the target is reachable in the frozen stable LTS; (ii) the local family at that target is nonempty; (iii) \(\lvert\{K:\mathrm{resources}(K)=R_{\mathrm{crp}}\}\rvert\ge 1\); (iv) the source profile is a declared S4PR overlap with an independent embedding hash. A global covering certificate must not replace (ii)–(iii). Multiplicity is reported when several kernels match; a zero match is reported as zero, not as a first-certificate artefact. In this paper field (iv) is refused on every subject (Section X-E).

---

## VIII. Chain-Decomposable Acquisition Order

The following sufficient condition is part of the original completeness chain. It is *not* a local-first-hit novelty and is not used to claim a general manufacturing deadlock-prevention policy.

**Definition 10 (Global acquisition order).**  
A strict partial order \(<\) on a key-resource set \(R_{\mathrm{key}}\) *covers* every machine, buffer, AGV, and hard-reservation token that can appear as a blocked holder or a demand witness. The model satisfies acquisition precedence if whenever a job holds \(r\) and then requests or hard-reserves \(r'\), one has \(r<r'\). BAS holders, AGV holders, and reservation redeems obey the same order.

**Definition 11 (Chain-decomposable core).**  
A closed core \(K\) is chain-decomposable if for every witness \((j,a,r)\in W_K\) there is a holder record \((j_h,r,q,j,a)\in H_K\) in which \(r\) itself is a non-autonomous key holding of \(j_h\), and that holder has its *own* blocked capacity-ready alternative with a next witness \(r'\) satisfying \(r<r'\). Aggregate capacity gaps that cannot be charged to a holder-dependency chain lie outside the theorem.

**Lemma 2 (P3-L1).**  
If \(K\) is a nonempty covering closed core and is chain-decomposable, then from any witness one can build an infinite resource sequence \(r_1,r_2,\ldots\) with \(r_n<r_{n+1}\) at every step.

*Proof.* Start from any witness \((j_0,a_0,r_1)\). Chain-decomposability supplies a holder \(j_1\) of \(r_1\) together with that holder’s own next witness \(r_2\), and acquisition precedence gives \(r_1<r_2\). Repeat. The core is finite but the selection may be repeated indefinitely, producing an infinite strictly ascending chain. \(\square\)

**Theorem 7 (P3).**  
If every covering closed core of an \(\mathrm{IMS\text{-}RAS}^{CW}\) model is chain-decomposable and a global acquisition strict order exists, then there is no capacity-mediated global operational deadlock in the sense of Theorem 2.

The conclusion does not imply standard nonblocking, livelock-freeness, policy-stall-freeness, or almost-sure completion.

*Proof.* Suppose, for a contradiction, that a capacity-mediated global operational deadlock exists. Theorem 2 supplies a covering closed core \(K\). By hypothesis \(K\) is chain-decomposable. Lemma 2 yields an infinite chain \(r_1<r_2<r_3<\cdots\) inside the finite set \(R_{\mathrm{key}}\). Hence there exist \(m<n\) with \(r_m=r_n\). Transitivity of \(<\) gives \(r_m<r_m\), contradicting irreflexivity. Therefore no covering closed core exists, and Theorem 2 yields the claim. \(\square\)

If the order is built only on a machine projection and omits an AGV, buffer, or reservation inversion, Theorem 7 does not apply. If a multi-capacity pool cannot be charged to a holder chain, it does not apply. Family I contains a non-chain covering core so that “not applicable” is returned rather than “deadlock-free.” Exact reachable thresholds for two concrete families (BIX1-SAT, BIX2-PERSIST) are proved in Appendix C; they are not main T-ASE novelties.

---

## IX. Stopped First-Hit Process and Exact Equations

### A. First-Hit Times and Inclusion

On the underlying CTMC \((X_t)_{t\ge 0}\) define
\begin{align*}
T_G&=\inf\{t\ge 0:X_t\in D_{\mathrm{global}}\},\\
T_L&=\inf\{t\ge 0:X_t\in D_{\mathrm{global}}\cup D_{\mathrm{local}}\},\\
T_F&=\inf\{t\ge 0:X_t\in F\}.
\end{align*}
The component estimands used in the experiments are
\[
\theta_g=\mathbb{P}(X_\tau\in D_{\mathrm{global}}),\quad
\theta_\ell=\mathbb{P}(X_\tau\in D_{\mathrm{local}}),\quad
\theta_b=\theta_g+\theta_\ell,
\]
where \(\tau=\inf\{t\ge 0:X_t\in A_{\mathrm{stop}}\}\) and
\[
A_{\mathrm{stop}}=D_{\mathrm{global}}\cup D_{\mathrm{local}}\cup F.
\]
They are evaluated under the same three-way first-hit partition: the local component is *not* computed by allowing paths to pass through \(D_{\mathrm{global}}\).

Because \(D_{\mathrm{global}}\subseteq D_{\mathrm{global}}\cup D_{\mathrm{local}}\), one has the event inclusion \(\{T_G<T_F\}\subseteq\{T_L<T_F\}\), hence \(\theta_G\le\theta_L\) on a common process, common \(F\), and a certified absorption domain, where \(\theta_G=\mathbb{P}(T_G<T_F)\) and \(\theta_L=\mathbb{P}(T_L<T_F)\). If a path of positive probability hits \(D_{\mathrm{local}}\setminus D_{\mathrm{global}}\) before \(F\), the inequality is typically strict. Pathwise \(T_L\le T_G\) on the bad-hit part, so
\[
\mathbb{E}[\min(T_L,T_F)]\le\mathbb{E}[\min(T_G,T_F)]
\]
as an extended-real inequality; a finite mean is reported only when absorption is almost sure and both sides are finite. Conditional means \(\mathbb{E}[T_L\mid T_L<T_F]\) and \(\mathbb{E}[T_G\mid T_G<T_F]\) are not comparable in general.

Changing the bad class from \(D_{\mathrm{global}}\) to \(D_{\mathrm{global}}\cup D_{\mathrm{local}}\) changes the target event and the stopping-rule hash. It is a new estimand, not a rescoring of a previous one. If the objective state partition is unchanged, the partition hash stays; selection is expressed by a separate stopping-rule hash.

If the initial state already lies in \(D_{\mathrm{local}}\) (respectively \(F\)), then \(\theta_\ell=1\) (respectively \(0\)) and the mean stopped time is zero (respectively a positive absorption time). That is a legitimate first-hit value.

### B. Probability-One Absorption Domain

Let \(T=X\setminus A_{\mathrm{stop}}\) be the candidate transient set. In a finite positive-rate graph, identify every unselected closed SCC \(C\subset T\) (no positive-rate edge from \(C\) to \(T\setminus C\) and none from \(C\) to \(A_{\mathrm{stop}}\)). Let \(B_{\mathrm{closed}}\) be the reverse basin in \(T\) of all such SCCs, and set \(S_T=T\setminus B_{\mathrm{closed}}\). Then \(x\in S_T\) if and only if \(\mathbb{P}_x(\tau_{A_{\mathrm{stop}}}<\infty)=1\). The global hypothesis \(A_{\mathrm{abs}}\) is the stronger condition \(B_{\mathrm{closed}}=\emptyset\) on the claimed domain. \(S_{\mathrm{reach}}\) (existence of a support path to \(A_{\mathrm{stop}}\)) is necessary but not sufficient for probability-one absorption.

### C. Generator, Committor, and Mean Time

On a certified domain the stopped generator has the block form
\[
Q=\begin{pmatrix}Q_{S_T,S_T}&Q_{S_T,D_{\mathrm{sel}}}&Q_{S_T,F}\\0&0&0\\0&0&0\end{pmatrix},
\]
with \(D_{\mathrm{sel}}=D_{\mathrm{global}}\cup D_{\mathrm{local}}\). Off-diagonal entries are nonnegative and rows sum to zero. Selected states of \(A_{\mathrm{stop}}\) are absorbing. Non-exponential durations require a phase-type expansion before they enter \(Q\).

**Theorem 8 (Stopped absorbing chain; P4).**  
Assume a finite IMS-CTMC and either \(A_{\mathrm{abs}}\) or restriction of the analysis to a certified \(S_T\). Then:

1. The deadlock committor \(h_i=\mathbb{P}_i(\tau_{D_{\mathrm{sel}}}<\tau_F)\) is the unique solution of \(Q_{S_T,S_T}h=-Q_{S_T,D_{\mathrm{sel}}}\mathbf{1}\) with \(h=1\) on \(D_{\mathrm{sel}}\) and \(h=0\) on \(F\).
2. The mean absorption time \(m_i=\mathbb{E}_i[\tau_{A_{\mathrm{stop}}}]\) is the unique solution of \(Q_{S_T,S_T}m=-\mathbf{1}\).
3. If \(Q(\vartheta)\) is differentiable and the partition \((S_T,D_{\mathrm{sel}},F)\) is locally constant, then \(h(\vartheta)\) is differentiable and
   \[
   Q_{S_T,S_T}\partial_\vartheta h=-(\partial_\vartheta Q_{S_T,S_T})h-(\partial_\vartheta Q_{S_T,D_{\mathrm{sel}}})\mathbf{1}.
   \]
4. On \(H=\{i\in S_T:h_i>0\}\), the Doob-\(h\) rates \(q^h_{ij}=q_{ij}h_j/h_i\) (\(i\neq j\), \(j\in H\)), \(q^h_{id}=q_{id}/h_i\) (\(d\in D_{\mathrm{sel}}\)), and \(q^h_{iF}=0\), with diagonal equal to the negative off-diagonal row sum, define the generator of the chain conditioned on hitting \(D_{\mathrm{sel}}\) first. The construction is undefined where \(h_i=0\) and is not a controller.

*Proof of invertibility.* Every state of \(S_T\) leaves and hits \(A_{\mathrm{stop}}\) almost surely, so \(Q_{S_T,S_T}\) is a transient subgenerator. The fundamental matrix
\[
N=\int_0^\infty\exp(Q_{S_T,S_T}t)\,dt
\]
is finite and satisfies \(Q_{S_T,S_T}N=NQ_{S_T,S_T}=-I\). Hence \(Q_{S_T,S_T}\) is invertible.

*Proof of the committor equation.* For \(i\in S_T\) let \(\lambda_i=-q_{ii}>0\). First-jump decomposition gives
\[
h_i=\sum_{j\in S_T}\frac{q_{ij}}{\lambda_i}h_j+\sum_{d\in D_{\mathrm{sel}}}\frac{q_{id}}{\lambda_i}.
\]
Multiplication by \(\lambda_i\) and rearrangement yield \(\sum_{j\in S_T}q_{ij}h_j+\sum_{d}q_{id}=0\), i.e. \(Q_{S_T,S_T}h=-Q_{S_T,D_{\mathrm{sel}}}\mathbf{1}\). Uniqueness follows from invertibility.

*Proof of the mean-time equation.* First-jump decomposition yields \(m_i=1/\lambda_i+\sum_{j\in S_T}(q_{ij}/\lambda_i)m_j\). Multiplication by \(\lambda_i\) gives \(Q_{S_T,S_T}m=-\mathbf{1}\).

*Proof of sensitivity.* Write \(A(\vartheta)h(\vartheta)=b(\vartheta)\) with \(A=Q_{S_T,S_T}\) and \(b=-Q_{S_T,D_{\mathrm{sel}}}\mathbf{1}\). On a neighbourhood where the partition is fixed and rates are differentiable, \(A(\vartheta)\) remains invertible, inversion is \(C^1\) on \(\mathrm{GL}_n\), and \(h=A^{-1}b\) is differentiable. Differentiating gives \((\partial_\vartheta A)h+A(\partial_\vartheta h)=\partial_\vartheta b\).

*Proof of the Doob-\(h\) generator.* For \(i\in H\) the off-diagonal rates into \(H\cup D_{\mathrm{sel}}\) are nonnegative. Jumps into \(F\) are set to zero because the conditioning event is “\(D_{\mathrm{sel}}\) first.” The diagonal is defined so that every row in \(H\cup D_{\mathrm{sel}}\) sums to zero; rows of \(D_{\mathrm{sel}}\) are identically zero. A jump of the original chain into \(S_T\setminus H\) has \(h=0\) and is killed. For any finite path \(i_0,\ldots,i_n\) that has not yet hit \(F\), the path rate is multiplied by the Radon–Nikodym factor \(h_{i_n}/h_{i_0}\); absorption at \(D_{\mathrm{sel}}\) ends the path. The transform does not enable or disable plant events, so it is not a supervisor. \(\square\)

If a reachable unselected closed class remains, \(Q_{S_T,S_T}\) as declared is incomplete, \(\tau_{A_{\mathrm{stop}}}=\infty\) on those paths, and the unconditional mean is \(+\infty\). The correct output is the refusal `non_almost_sure_absorption_domain`, not an invented finite mean. Sensitivity holds only on pieces of parameter space where the partition is constant.

### D. Barrier A and Partition Soundness

**Algorithm (terminal/stopping partition).**  
(i) Enumerate the complete untruncated stable LTS and re-enumerate from the same registry for provenance. (ii) Mark \(F\). (iii) Mark \(D_{\mathrm{global}}\) and store global certificates. (iv) Enumerate all-minimal local kernels on the remainder; mark \(K_{\mathrm{local}}\). (v) If A2b is proved, apply Theorem 4; otherwise apply Theorems 5–6 on each candidate. (vi) Compute SCCs on the leftover plant graph; classify terminal SCCs as \(R_{\mathrm{terminal}}\) or \(R_{\mathrm{livelock}}\). (vii) Form \(A_{\mathrm{stop}}\) and \(S_T\); refuse if \(B_{\mathrm{closed}}\neq\emptyset\) on a global claim. (viii) Freeze the state-space, partition, rate-manifest, and stopping-rule hashes.

**Theorem 9 (Partition soundness).**  
Under CW1–CW10 and A8, if the algorithm returns successfully, then: (i) \(D_{\mathrm{global}}\), \(D_{\mathrm{local}}\), \(F\), \(R_{\mathrm{livelock}}\), and \(R_{\mathrm{terminal}}\) are pairwise disjoint under the stated precedence; (ii) \(R_{\mathrm{livelock}}\) and \(R_{\mathrm{terminal}}\) are terminal-SCC classes of the leftover plant graph; (iii) \(D_{\mathrm{local}}\) is used only as a stopped-process bad hit set admitted by Theorem 4 or Theorem 5; (iv) \(S_{\mathrm{reach}}\) is an existential support diagnostic and \(S_T\) is the certified probability-one domain; (v) the exact CTMC and DES may share the same selected labels.

The algorithm *must* refuse a binary CTMC when any of the following holds: truncated or unavailable LTS; an invalid model/state (including completion while holding); LTS provenance mismatch; missing source/target or missing frozen rate; overlapping completion and bad labels; a transient state with no positive outgoing rate; a transient state that cannot reach selected absorption; a reachable unselected \(R_*\) that cannot reach selected absorption; a \(D_{\mathrm{global}}\)-only estimand in the presence of \(D_{\mathrm{local}}\) unless that estimand is separately declared; a policy-only stall not entered in a policy schema; a local candidate with a path to \(F\).

### E. Exact/DES Protocol Used in Section X

On a Barrier-A-certified graph the implementation solves the three binary reductions of Theorem 8 (global, local, selected-bad) and checks \(\theta_g+\theta_\ell=\theta_b\) numerically. DES uses Gillespie sampling of the same rates and the same three classes, \(n=65536\) replications, a primary seed and a subsequent reproduction seed, contiguous shards, and one reducer. The simultaneous Hoeffding band for six probability cells at \(\alpha=0.01\) is
\[
t=\sqrt{\frac{\log(2\cdot 6/0.01)}{2n}}=7.35\times 10^{-3}.
\]
A cell is compatible when the absolute error is at most \(t\). Compatibility does not prove Theorem 4 and does not prove plant fidelity. BLAS threads equal one; independent plants and DES shards run in a process pool (32 workers by default, 48 when free RAM is at least \(64\,\mathrm{GiB}\)).

Complexity (not a polynomial-time claim): SCC decomposition on an explicit LTS is \(O(\lvert X\rvert+\lvert E\rvert)\); all-minimal local enumeration is exponential in the number of blocked jobs; the linear solve scales with \(\lvert S_T\rvert\).

---

## X. Experimental Studies

All subjects use a new scope identifier and new evidence roots. Frozen historical refusals are retained and are not overwritten. No shop-floor log is used. Plants are synthetic digital twins.

### A. Family I: Theory-Hardening Witnesses

Four logical witnesses keep the theorems from becoming tautologies.

1. *Non-confluent closure.* Two zero-time sequences from one unstable state yield two stable successors. A deterministic \(\kappa\) is refused.
2. *Optional drain.* A controllable alternate release does not prove the ring deadlock-free; the saturated ring prefix remains reachable. Drain is control, not a structural repair.
3. *Wrong cut.* Deleting a backflow edge creates a *new* kernel. Cutting the “obvious” wait-edge is not a repair.
4. *Non-chain covering kernel.* A covering kernel that is not chain-decomposable makes a strict-order sufficient condition inapplicable rather than “deadlock-free.”

These four rows are cited as boundaries, not as main theorems.

### B. Family IV: Machine–AGV Island

The manufacturing clothing is a three-job island (Fig. 1, Table II). Job \(A\) holds machine M1 and requests the AGV; job \(B\) holds the AGV and requests M1; job \(C\) is in service on M2. The only structural interlock is \(\{A,B\}\) on \(\{\mathrm{M1},\mathrm{AGV}\}\). Job \(C\) still has an outgoing plant arc, so a terminal-SCC diagnosis would miss the local stop. The predeclared intervention is an optional drain that lets \(B\) release the AGV without entering M1.

**Table II**  
Island first-hit values (exact). DES agrees on all six cells at \(n=65536\), \(t=7.35\times 10^{-3}\)

| Plant | Barrier A | \(\theta_g\) | \(\theta_\ell\) | \(\theta_b\) | Mean time |
| --- | --- | --- | --- | --- | --- |
| Base | certified | \(0\) | \(1\) | \(1\) | \(0\) |
| Optional AGV drain | certified | \(0\) | \(0\) | \(0\) | \(3.23\) |

The base initial state *is* a local hit, so \(\theta_\ell=1\) and the mean stopped time is zero. The partition still contains a distinct \(D_\mathrm{global}\) state that is not the first hit from the initial state, which is exactly the distinction Theorem 4 forces: first-hit is not “the plant has no outgoing arc,” and it is not “every bad state is equally the start.” After the drain, the only absorbing class is \(F\). The intervention therefore changes the *class* of the initial state, not a long transient risk path. That sentence is part of the result, not a defect to be edited out.

An earlier all-completion clothing of the same island (release-then-complete, no local hit) produced \(\theta_b=0\) on both the base and the intervention and is retained as a certified negative: a digital-twin that always finishes cannot demonstrate local-first-hit. A still earlier clothing that marked completion while holding a buffer was refused as an invalid LTS state and is retained.

Fig. 2 plots the four exact KPIs. Every DES cell matches the exact value to machine zero on this island (the initial state is already absorbing, or the drain graph is small); the Hoeffding band is therefore slack, and it is not sold as a rare-event study.

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

The residual cycle is the C1 witness: a wait-for cycle exists, residual capacity remains, and LTS truth is “not deadlocked.” The bypass plant is the Theorem 6 witness: a local-looking pair is not a global deadlock because a third job can open a completion path. The four siphon agreements occupy IMS-SIP\(^1\). The four refusals occupy the hypotheses that Theorem 3 declines to inherit from S3PR monitor theory [1], [3]. A cycle/SCC screen alone would mark the residual cycle as a stop and is therefore not used as a theorem.

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

Six new subjects reuse no historical case hash and do not run SBA or CRP equations. Table V reports Proposition 4.

**Table V**  
Four-field diagnostic. Agreement requires all four fields

| Subject | Reachable | Local family | Match \(\lvert K\rvert\) | S4PR overlap | Agreement |
| --- | --- | --- | --- | --- | --- |
| Unit pair, \(R_\mathrm{crp}=\{r_1,r_2\}\) | yes | yes | 1 | no embedding | no |
| Unit triple | yes | yes | 1 | no embedding | no |
| Reachable pair | yes | yes | 1 | no embedding | no |
| Wrong \(R_\mathrm{crp}=\{r_9\}\) | yes | yes | 0 | no embedding | no |
| AGV \(\wedge\) buffer | yes | yes | 1 | no embedding | no |
| Residual cycle | yes | no | 0 | no embedding | no |

Fields 1–3 hold on four subjects. Field 4 is `no_independent_s4pr_embedding` on all six, so agreement is identically zero. That is the intended reading of Proposition 4 and of [10]: without an audited S4PR embedding, a CRP overlap claim is not licensed.

---

## XI. Discussion and Limitations

T-ASE evaluates automation methods by quality, completeness, complexity, verification, and reliability [12], [16]. The verification offered here is a certified first-hit set, a typed refusal, and a same-target exact/DES check. The reliability claim is scoped: relative to a declared finite registry, not relative to an open shop floor.

Several limitations are essential to the contribution rather than residual bugs.

1. *Already-hit island.* Family IV begins in \(D_\mathrm{local}\). The intervention changes the absorbing class; it does not illustrate a long transient that wanders into a local hit. A larger cell with a positive-time first hit is future work, not a silent reinterpretation of Table II.
2. *Synthetic plants.* Every subject is a digital twin. No vendor trace, no throughput number, and no claim that an optional drain “improves productivity” on a factory is licensed.
3. *No published PN benchmark replay.* The paper does not rerun a classical S3PR/S4PR example from [1], [8], or [10] inside the IMS operational semantics. Doing so would require an independently hashed embedding and is exactly field 4 of Proposition 4.
4. *SIP\(^1\) is small.* Four agreements demonstrate the dual; they do not make siphon control the method.
5. *Exponential LTS.* Family III hits a \(10^5\)/300 s wall. All-minimal local enumeration is exponential in blocked jobs. No bit-polynomial IMS reachability is claimed [13], [14].
6. *Historical negatives retained.* A CRP implementation-level encoding that used a global extractor in the presence of an unrelated job remains failed. An eight-dimension overlap gate used in earlier internal work remains open. Neither is a confirmation set for this paper.
7. *What is not proved.* A2b is not necessary. Complete-LTS admission is not a general structural theorem. A local core is not automatically \(D_\mathrm{local}\). \(D_\mathrm{local}\) is not a plant terminal SCC. Exact/DES agreement does not prove the theorem. The method is not a risk-budget supervisor.

The natural extensions are an independently embedded S4PR overlap row, a larger island whose first local hit occurs at positive time, and a finite-state supervisor baseline in the sense of [5], [15]. Those are later papers.

---

## XII. Conclusion

Local blocking in a finite manufacturing resource-allocation system is a first hit of a certified stopped-process set, not a wait-for cycle and not a plant terminal SCC. The set is admitted by a request-closed structural argument or by a complete-LTS nonreachability audit, and it is refused when a completion bypass exists. Diagnostic siphons apply only on a wait-snapshot of the unit-capacity one-hold-one-request subclass. Exact and simulated first-hit values share a stopping hash only after the absorption domain is certified. A three-job machine–AGV island, a ten-plant baseline table, a tandem scale family, and a four-field CRP diagnostic support those sentences and no stronger ones.

The checkable object is the typed first-hit set. Controllers, monitors, shop-floor policies, and general plant-net isomorphisms are outside the claim.

---

## Appendix A  
Retained Negative Clothings

An island that marked a job complete while it still held the next buffer was refused as `completed_job_holds_resource` (invalid LTS state) and is not replaced in place. A repaired all-completion island with the same topology produced Barrier A certified and \(\theta_b=0\) on both the base and the intervention; it is a certified demonstration that an always-finishing twin cannot clothe Theorem 4. Both clothings remain in the evidence record.

## Appendix B  
Implementation Notes

Certificates, LTS enumeration, the wait-snapshot bridge, Barrier A, the absorbing CTMC, and the DES shards are generated from one registry. Independent plants and DES shards run in a process pool; BLAS threads equal one. Primary DES finishes before reproduction. Evidence roots are write-once. The quantitative protocol, including the Hoeffding band and the seeds, is fixed before the island wave.

## Appendix C  
Exact Reachable Thresholds (BIX1-SAT and BIX2-PERSIST)

These two families close the original exact-threshold derivations. They are not T-ASE main novelties and are not finite-capacity configuration theorems in the sense of [9].

### C.1 Family BIX1-SAT (Theorem 10)

The instance \(\mathrm{BIX1\text{-}SAT}(c_M,c_G,c_D,c_V,n_A,n_B)\) has capacities at least one. All A-jobs initially request \(M\) and all B-jobs initially request \(G\). The registry contains:

- *A-chain:* `start` acquires \(M\) and clears the start request; `service_complete` is uncontrollable, keeps \(M\), and requests \(\{G,D,V\}\); `transfer` is controllable and atomically acquires \(G,D,V\), releases \(M\), and clears requests; `drain` is uncontrollable and releases \(G,D,V\) and completes.
- *B-chain:* `start` acquires \(G\); `transport_complete` is uncontrollable, keeps \(G\), and requests \(M\); `unload` acquires \(M\) and releases \(G\); `complete` releases \(M\) and completes.
- \(V\) is a hard-reservation token. Zero-time closure is trivial. The flag `event_calendar_empty` records the absence of an external calendar, not the absence of completion events.

**Theorem 10 (P3d).**  
A capacity-mediated global operational deadlock is reachable in BIX1-SAT if and only if \(n_A\ge c_M\) and \(n_B\ge c_G\).

*Sufficiency.* Execute `start` and `service_complete` for exactly \(c_M\) A-jobs, so they saturate \(M\) and request \(\{G,D,V\}\). Then execute `start` and `transport_complete` for exactly \(c_G\) B-jobs, so they saturate \(G\) and request \(M\). The prefix contains no successful transfer, hence residuals are \(M=0\), \(G=0\), \(D=c_D\), \(V=c_V\). Every A-job’s AND request is blocked by the \(G\)-gap; every B-job is blocked by the \(M\)-gap; unstarted A/B jobs cannot start. No job is in a mode that enables a completion event. All unfinished activity is covered by the same \(M\)–\(G\) closed core, so Theorem 2 applies.

*Necessity.* No global deadlock can contain an `a_transferred` job (`drain` is uncontrollable and enabled) or a `b_on_M` job (`complete` is uncontrollable and enabled). Hence in a global deadlock \(M\) is held only by A-jobs that have not transferred, \(G\) only by B-jobs that have not unloaded, and \(D,V\) are free.

If \(n_A<c_M\), then \(M\) cannot be saturated, so residual \(M>0\). A `b_blocked_unload` job would have `unload` enabled; otherwise every unfinished B-job is `b_idle` or `b_in_transport`, the former can `start` when \(G\) has residual, and the latter has `transport_complete` enabled. If \(G\) has no residual then some B-job holds \(G\); under the assumption that none is `b_blocked_unload`, that holder is `b_in_transport` and still has an enabled completion. If there is no unfinished B-job, every unfinished A-job is `a_idle`, `a_in_service`, or `a_blocked_complete`, which enable `start`, `service_complete`, or—because \(D,V\) are free and \(G\) is not saturated by B—`transfer`. Hence there is no global deadlock.

Symmetrically, if \(n_B<c_G\), residual \(G>0\) and \(D,V\) are empty in the necessary deadlock shape. Any `a_blocked_complete` has `{G,D,V}` transfer enabled; if none exists, every unfinished A-job has `start` or `service_complete` enabled. If there is no unfinished A-job, every unfinished B-job has an enabled event on the `start`/`transport_complete`/`unload`/`complete` chain; if \(M\) is saturated by A-jobs they are `a_in_service` or `a_blocked_complete`, which are enabled. Therefore every global deadlock requires \(n_A\ge c_M\) and \(n_B\ge c_G\).

The capacities \(c_D,c_V\) disappear from the threshold because the witnessing prefix has no successful transfer, so no job holds \(D\) or \(V\), and the A-job AND request is already blocked by the \(G\)-gap. This is not a general statement that buffer or reservation capacities never matter. If a successful A-transfer may occupy \(D\) persistently, the instance \(c_M=c_G=c_D=1\), \(n_A=2\), \(n_B=0\) already leaves the family: it is an `outside_bix1_sat` terminal-boundary, not a mismatch of Theorem 10.

### C.2 Family BIX2-PERSIST (Theorems 11–12)

The instance \(\mathrm{BIX2\text{-}PERSIST}(c_M,c_D,c_Q,n_A,n_B,n_C,\mathrm{mode})\) starts empty. Each successful handoff is followed by an explicit uncontrollable release, so completed jobs hold nothing. Every demand is one unit.

- A-chain: \(M\to D\to\mathrm{release}(D)\);
- B-chain: \(D\to Q\to\mathrm{release}(Q)\);
- *ring* C-chain: \(Q\to M\to\mathrm{release}(M)\);
- *dag* mode deletes the \(Q\to M\) request; C releases \(Q\) on completion.

Each \(X\to Y\) chain has four events: controllable start acquiring \(X\); uncontrollable completion keeping \(X\) and requesting \(Y\); controllable handoff acquiring \(Y\) and releasing \(X\); uncontrollable release of \(Y\) with completion.

**Theorem 11 (P3e-a, ring).**  
A capacity-mediated global operational deadlock is reachable in ring mode if and only if \(n_A\ge c_M\), \(n_B\ge c_D\), and \(n_C\ge c_Q\). On the minimal \(1/1/1\) instance the minimal closed-core resources are exactly \(\{M,D,Q\}\).

*Sufficiency.* Select \(c_M\) A-jobs, \(c_D\) B-jobs, and \(c_Q\) C-jobs. For each selected A-job fire start-\(M\) then complete-request-\(D\); likewise for B and C. The finite prefix has no successful handoff, so A, B, C saturate \(M\), \(D\), \(Q\) respectively and request the next resource. Unstarted jobs are blocked by full capacity; no job is in a mode with an enabled completion or release. The three job classes and \(\{M,D,Q\}\) form a covering closed core, so Theorem 2 applies inside the capacity-mediated subdomain.

*Necessity.* In any global deadlock of the family, a job `in_service` has an uncontrollable completion enabled and a job `on_target` after a successful handoff has an uncontrollable release enabled; neither mode can occur. Hence every unfinished job is idle or blocked-before-handoff, and \(M,D,Q\) can be held only by blocked A, B, C respectively. Write \(I_A,I_B,I_C\) for idle sets and \(K_A,K_B,K_C\) for blocked-before-handoff sets, so holders satisfy \(H_M=K_A\), \(H_D=K_B\), \(H_Q=K_C\). Moreover: residual \(M>0\) implies \(I_A=K_C=\emptyset\) (else start-\(M\) or C-handoff is enabled); residual \(D>0\) implies \(I_B=K_A=\emptyset\); residual \(Q>0\) implies \(I_C=K_B=\emptyset\).

If \(n_A<c_M\), then because \(M\) is held only in unit by \(K_A\) one has residual \(M>0\), hence \(I_A=K_C=\emptyset\). Then \(Q\) has no holder, so residual \(Q>0\), hence \(I_C=K_B=\emptyset\). Then \(D\) has no holder, so residual \(D>0\), hence \(I_B=K_A=\emptyset\). Every permitted unfinished mode is empty, so the state is complete, contradicting global deadlock. The cases \(n_B<c_D\) and \(n_C<c_Q\) are cyclic permutations of the same argument.

**Theorem 12 (P3e-b, deleted backflow).**  
In dag mode no capacity-mediated global operational deadlock is reachable. If the batch is nonempty, a marked completion path exists from the empty initial state.

*Proof of deadlock-freeness.* After deleting \(Q\to M\), hold-then-request obeys \(M<D<Q\). In a hypothetical deadlock, exclude again every `in_service` and `on_target` mode. C has no blocked-before-handoff mode; an idle C would make start-\(Q\) enabled unless \(Q\) were saturated by a job with no enabled release, which has already been excluded. Hence a deadlock has no unfinished C and \(Q\) is empty. Every blocked B-job can then hand off into \(Q\), after which \(D\) is empty; every blocked A-job can hand off into \(D\), after which \(M\) is empty; remaining idle jobs can start. The only state with no enabled event is complete, a contradiction.

*Proof of a completion path.* Execute jobs serially: start one job, then its completion, handoff (if any), and release. Every capacity is at least one, so every finite batch can be completed one job at a time. \(\square\)

The three-resource circular wait and the deletion of one backflow edge are classical and are not claimed as new graph theory. Theorems 11–12 close a concrete IMS-event-semantic pair: a reachable, capacity-auditable persistent-buffer core and its matched repair. Alternate routes, AND requests, AGV/reservations, external drains, forced priorities, and multiple persistent buffers lie outside the family.

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

**Fig. 1.** Operational distinction used throughout the paper. A wait-for cycle or an empty plant-net siphon is a structural candidate. A local closed kernel becomes \(D_\mathrm{local}\) only after typed admission (Theorem 4 or Theorem 5) and bypass refusal (Theorem 6). The stopped process first-hits \(D_\mathrm{global}\), \(D_\mathrm{local}\), or \(F\). The plant LTS may still have outgoing arcs at a \(D_\mathrm{local}\) state.

**Fig. 2.** Exact first-hit KPIs on the three-job machine–AGV island (Family IV). Base: already a local hit. Optional AGV drain: every trajectory completes. Files: `docs/paper/figures/fig_h4_island_kpis.pdf`, `.png`.

**Fig. 3.** Tandem scale (Family III, unit capacity). Left: \(\lvert X\rvert\) versus jobs (log). Right: runtime versus jobs (log). Horizontal guides mark \(10^3\), \(10^4\) states and the \(300\,\mathrm{s}\) cap. Files: `docs/paper/figures/fig_h3_scale.pdf`, `.png`.

---

*End of double-anonymous Regular Paper draft. Conversion to the IEEE two-column template is a later production step; scientific claims in that conversion must remain identical to this file.*
