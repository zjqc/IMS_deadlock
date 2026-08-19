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

1. under assumptions A0–A7 and the request-closed discipline A2b, a local closed kernel makes every kernel job permanently incomplete, hence batch completion \(F\) is unreachable (Theorem 1);
2. if A2b cannot be verified, the same candidate is admitted only after a complete, untruncated LTS audit shows that \(F\) is unreachable from that state (Proposition 1), and is refused if a shortest completion bypass exists (Proposition 2).

After the absorption domain is certified—no unselected closed class, no truncated LTS—exact first-hit probabilities on the stopped continuous-time Markov chain (CTMC) and independent discrete-event (DES) replications share one stopping hash. Agreement inside a predeclared simultaneous Hoeffding band is a numerical check, not a proof of the theorem and not a claim of plant fidelity [11].

The experimental clothing is a new discovery panel with a distinct scope identifier. It is not a relabelling of a six-case constructive manuscript and not a historical replay of a failed CRP encoding. Four families are reported.

- *Island.* A three-job machine–AGV cell starts already locally stopped (\(\theta_\ell=1\), mean stopped time \(0\)). An optional one-slot AGV drain sends every sample path to completion (\(\theta_b=0\), mean time \(3.23\)). Six probability cells agree with DES at \(n=65536\) inside tolerance \(7.35\times 10^{-3}\).
- *Baselines.* Ten plants are scored by a wait-for/SCC screen, a closed-core certificate, a siphon-or-refuse predicate, and LTS truth. Four plants agree with the diagnostic siphon; four refuse it for OR, AND, multi-capacity, or conjunctive AGV demand; false positives and false negatives are both zero.
- *Scale.* A tandem family enumerates twelve rows with at least \(10^3\) stable states and four with at least \(10^4\), and refuses three rows at \(10^5\) states or \(300\,\mathrm{s}\).
- *CRP diagnostic.* Proposition 6.4’s four fields are scored on six new subjects. Fields 1–3 (reachability, local family, resource match) can hold; field 4 (independent S4PR embedding) is refused on every row. Bridge agreement is therefore zero. A prior implementation-level CRP encoding remains a negative witness; it is not a refutation of the source theorem [10].

The publishable increment is the checkable first-hit object and its typed admission/refusal rules. The paper does not claim a new siphon-control policy, a general IMS–S3PR isomorphism, a bit-polynomial reachability procedure, a shop-floor throughput gain, or priority over PDDP/CRP/monitor synthesis [3], [8]–[10].

Section II places the increment against Petri, RAS, knot, and probability baselines. Section III fixes the IMS model and the closed-kernel certificate. Section IV states the typed admission theorems. Section V defines the stopped estimands and the exact/DES protocol. Section VI reports the four families. Section VII records limitations. Section VIII concludes.

---

## II. Related Work

T-ASE asks that a Regular Paper compare methods and cite archival work from the last two years [12]. The comparison here is organized by the *object* each literature family computes, not by a priority slogan.

### A. Wait-For Cycles, Knots, and Sequential RAS

A directed wait-for cycle is the oldest operational picture of deadlock. In sequential single-unit resource allocation it is tightly connected to safety: Lawley and Reveliotis proved that SU-SAFE is NP-complete and isolated structural subclasses that eliminate deadlock-free unsafe states [4]. Palmer, Harper, and Knight characterized deadlock of open restricted queueing networks by a knot in a state-dependent blocking graph and exhibited 2-/3-server counterexamples to a weakly-connected-component shortcut [6]. Those results remain the correct baselines for a cycle/SCC *screen*. They do not treat residual capacity, OR-of-AND alternatives, and BAS hold-after-service as first-class IMS tokens, and a residual-feasible cycle is not an IMS deadlock. Family II below keeps the cycle/SCC column precisely so that this false-positive mode stays visible.

Banker’s-algorithm and ordered-avoidance tests are sufficient safety filters on sequential RAS. They are not theorems of the IMS operational model once AGV occupancy and reservations are tokens.

### B. Petri-Net Siphons, Monitors, and Finite-Capacity Configuration

Ezpeleta, Colom, and Martínez gave the S3PR liveness and siphon-control policy that still organizes the plant-net school [1]. Li and Zhou refined the construction with elementary siphons [2]. Chen and Li formulated maximally permissive monitor synthesis as a marking/place-covering problem (MCPP) whose optimum exists only when a monitor supervisor is expressible; full reachability-graph enumeration is exponential and MCPP is NP-hard [3]. Pang *et al.* gave sufficient liveness and resource-configuration conditions for finite-capacity S3PR after an ENS3PR transformation, with a worst-case SMS bound \(O(2^{N_p})\) [9]. None of these results is an IMS operational certificate: they assume a plant-net subclass, not BAS blocked-unload, AGV occupancy, or OR-of-AND acquisition. The present paper uses an empty siphon only as a *diagnostic dual* of a wait-snapshot net on the unit-capacity subclass IMS-SIP\(^1\) (Proposition 3) and refuses the dual outside that subclass.

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

## III. IMS-RAS Model and Closed-Kernel Certificates

### A. Finite Operational Model

An IMS resource-allocation system is a finite tuple \((J,R,\kappa,\Sigma)\), where \(J\) is a finite set of jobs, \(R\) a finite set of resources, \(\kappa:R\to\mathbb{Z}_{>0}\) a capacity, and \(\Sigma\) a finite *declared* registry of per-job transition specifications. A specification names a source mode, a target mode, an acquire vector, a release vector, optional next requests, and whether it clears requests or marks completion. Alternatives of a job are OR-of-AND: each alternative is a conjunctive demand, and the job may proceed on any feasible alternative.

A state records holds, requests, modes, completion flags, and an event calendar. Analysis is performed only after a zero-time closure. If that closure is non-confluent, the successor is set-valued and a deterministic \(\kappa\)-map is refused (Family I, CL1). Completed jobs do not hold resources [assumption A5]; a state that marks completion while still holding is an invalid LTS state and is refused.

Assumptions A0–A7 (finiteness, zero-time normalization, per-job ownership, no preemption, complete registry, capacity conservation, OR-of-AND requests, capacity-mediated blocking only) are *hypotheses*, not observations. If any fails, the implementation returns a structured refusal. Probability constructions additionally require A8: an untruncated stable LTS and a frozen rate manifest.

All certificates and probabilities in this paper are relative to the declared registry \(\Sigma\). They are not claims about an unmodelled physical plant.

### B. Global and Local Closed Kernels

**Definition 1 (Local closed blocking kernel).**  
At a stable state \(s\), a triple \(K=(J_K,R_K,W_K)\) is a local closed blocking kernel if and only if (i) \(J_K\) is a nonempty set of unfinished jobs; (ii) every \(j\in J_K\) has a nonempty family of capacity-ready request alternatives; (iii) every alternative of every \(j\in J_K\) is blocked by some \(r\in R_K\) with \(\mathrm{avail}_s(r)\) strictly below the demand; (iv) every witness unit that creates that shortage is held by \(J_K\) (or by a hard reservation of \(J_K\)); (v) no job in \(J_K\) has an enabled transition in \(\Sigma\); (vi) \(K\) is inclusion-minimal in jobs and resources.

**Definition 2 (\(D_\mathrm{global}\), \(F\)).**  
\(s\in F\) if and only if every job is complete and no resource is held. \(s\in D_\mathrm{global}\) if and only if \(s\) is stable and incomplete, the calendar is empty, no transition is enabled, every unfinished job is blocked, and a closed kernel *covers* every unfinished job.

A global covering certificate must not be substituted for a local kernel when the question is partial blocking [10]. Local kernels are enumerated by increasing job-subset cardinality and inclusion-minimal resource witnesses (Proposition 6.2 of the companion theory: completeness on finite \(J,R\)). Worst-case cost is exponential in the number of blocked jobs; that cost is reported, not hidden.

### C. Diagnostic Siphon Dual

**Definition 3 (IMS-SIP\(^1\)).**  
A certified local kernel at a reachable stable state lies in IMS-SIP\(^1\) when every core resource has capacity one and residual zero, every core job holds exactly one core resource and requests exactly one core resource (no OR, no AND), the certificate is inclusion-minimal, and a reachability witness (possibly the empty prefix) is attached.

On that subclass the wait-snapshot net has a place \(\mathrm{free}:r\) for each core resource and a transition \(t_j\) that consumes \(\mathrm{free}:q(j)\) and produces \(\mathrm{free}:h(j)\).

**Proposition 3 (Wait-snapshot dual).**  
Under IMS-SIP\(^1\), the set of places \(\{\mathrm{free}:r:r\in R_K\}\) is an inclusion-minimal empty siphon of the wait-snapshot net, and the dual recovers the kernel. The siphon predicate is the ordinary one (\(\bullet\Sigma\subseteq\Sigma\bullet\)). The net is not a plant S3PR. If any IMS-SIP\(^1\) hypothesis fails, the bridge returns a typed reason and does not emit a corresponding siphon.

---

## IV. Typed Local First-Hit

### A. Request-Closed Structural Route

**Definition 4 (A2b).**  
A2b holds at \(s\) when every transition that would change the mode, holds, requests, or completion of a job with uncleared requests consumes at least one currently feasible request alternative. There is no same-mode bypass that depends on an outside resource, guard, or intermediate mode.

**Theorem 1 (Kernel-job noncompletion).**  
Assume A0–A7 and A2b. If a stable state \(s\) contains a local closed kernel \(K\), then on every plant path from \(s\) every job in \(J_K\) remains incomplete and its requests at the hit remain unsatisfiable. Consequently \(F\) is unreachable from \(s\).

*Proof sketch.* Definition 1(v) and A4 imply that no kernel job is enabled. A2 implies that an outside transition cannot complete a kernel job or rewrite its requests. A3 and A5 imply that witness units held by \(J_K\) are not released by preemption, failure, or a completed job. Definition 1(iii)–(iv) imply that every alternative is blocked by a kernel-held witness; outside jobs can occupy at most the residual that was already free at the hit, so they cannot raise availability of those witness units. A2b excludes a request-independent bypass. Therefore no kernel job ever acquires a feasible alternative or fires a progress/release/completion transition, and \(F\)—which requires every job to complete—is unreachable. The forward invariant is kernel-job noncompletion, not identity of the certificate JSON after the hit. \(\square\)

A2b is *sufficient*, not necessary. It is not claimed that every local deadlock arises from A2b.

### B. Complete-LTS Fallback and Bypass Refusal

**Proposition 1 (Model-specific admission).**  
If A2b is not established, a local kernel at \(s\) may be placed in \(D_\mathrm{local}\) only after the complete, untruncated LTS generated from the same registry shows that no state of \(F\) is reachable from \(s\). The conclusion is a property of that finite model, not a general structural theorem.

**Proposition 2 (Bypass refusal).**  
If the same LTS contains a path from the candidate to a state of \(F\), the candidate is refused and the shortest event prefix is retained. The kernel is not entered into \(D_\mathrm{local}\).

**Definition 5 (\(D_\mathrm{local}\)).**  
\(s\in D_\mathrm{local}\) if and only if \(s\notin D_\mathrm{global}\), \(s\) contains at least one local closed kernel, and either Theorem 1 applies or Proposition 1 applies. \(D_\mathrm{local}\) may have outgoing plant arcs: outside jobs may still move. It is a first-hit *stopping* set of the stopped process, not a terminal SCC of the plant.

### C. Precedence Convention

When a state satisfies both the global and the local predicates it is counted only in \(D_\mathrm{global}\). That precedence is a versioned estimand convention, not a physical law. Estimands that ignore it must be labelled as different objects.

### D. Four-Field CRP Rule (Not a CRP Theorem)

**Proposition 4 (Partial bridge, four independent fields).**  
Given a frozen target state and a declared resource set \(R_\mathrm{crp}\), a partial-bridge *agreement* is true only if all four hold independently: (i) the target is reachable in the frozen stable LTS; (ii) the local certificate family at that target is nonempty; (iii) \(\lvert\{K:\mathrm{resources}(K)=R_\mathrm{crp}\}\rvert\ge 1\); (iv) the source profile is a declared S4PR overlap with an independent embedding hash. A global covering certificate must not replace (ii)–(iii). If any field fails, agreement is false and the failing field is reported.

Field (iv) is refused in this paper: no audited external S4PR embedding is supplied. The rule is implemented; a CRP theorem is not.

---

## V. Stopped-Process Estimands and the Exact/DES Protocol

### A. First-Hit Times

On the underlying CTMC \((X_t)_{t\ge 0}\) define
\[
T_G=\inf\{t\ge 0:X_t\in D_\mathrm{global}\},\quad
T_L=\inf\{t\ge 0:X_t\in D_\mathrm{global}\cup D_\mathrm{local}\},\quad
T_F=\inf\{t\ge 0:X_t\in F\}.
\]
The estimands are \(\theta_g=\mathbb{P}(T_G<T_F)\), \(\theta_\ell=\mathbb{P}(T_L<T_F)\), and \(\theta_b=\mathbb{P}(T_G\wedge T_L<T_F)=\mathbb{P}(T_L<T_F)\) under the convention of Section IV-C, together with the mean stopped time \(\mathbb{E}[T_L\wedge T_F]\). Event inclusion gives \(\theta_g\le\theta_\ell\) on a common process.

If the initial state already lies in \(D_\mathrm{local}\) (respectively \(F\)), then \(\theta_\ell=1\) (respectively \(0\)) and the mean stopped time is zero (respectively a positive absorption time). That is a legitimate first-hit value, not a numerical defect. It must be reported as an already-hit initial condition.

### B. Barrier A

A quantitative row is emitted only if Barrier A returns `certified`:

- the stable LTS is nonempty and not truncated;
- every reachable state is classified into \(D_\mathrm{global}\), \(D_\mathrm{local}\), \(F\), or an explicitly selected residual class;
- no reachable unselected livelock or terminal SCC remains;
- no state is complete while holding a resource.

Otherwise the row is refused and the refusal code is retained. An unselected closed class makes the committor of the binary CTMC undefined [11]; the correct output is refusal, not an invented probability.

### C. Exact CTMC and DES

On a certified stopped graph the exact values are the unique solutions of the standard absorbing-chain equations on the transient states [11]. DES uses Gillespie sampling of the same graph, \(n=65536\) replications per plant, a primary seed and a subsequent reproduction seed, contiguous shards, and one reducer. The simultaneous Hoeffding band for six probability cells at \(\alpha=0.01\) is
\[
t=\sqrt{\frac{\log(2\cdot 6/0.01)}{2n}}=7.35\times 10^{-3}.
\]
A cell is compatible when the absolute error is at most \(t\). Compatibility does not prove Theorem 1 and does not prove that the digital-twin equals a factory.

BLAS threads are pinned to one; independent plants and DES shards run in a process pool (32 workers by default, 48 when free RAM is at least \(64\,\mathrm{GiB}\)).

---

## VI. Experimental Studies

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

The base initial state *is* a local hit, so \(\theta_\ell=1\) and the mean stopped time is zero. The partition still contains a distinct \(D_\mathrm{global}\) state that is not the first hit from the initial state, which is exactly the distinction Theorem 1 forces: first-hit is not “the plant has no outgoing arc,” and it is not “every bad state is equally the start.” After the drain, the only absorbing class is \(F\). The intervention therefore changes the *class* of the initial state, not a long transient risk path. That sentence is part of the result, not a defect to be edited out.

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

The residual cycle is the C1 witness: a wait-for cycle exists, residual capacity remains, and LTS truth is “not deadlocked.” The bypass plant is the Proposition 2 witness: a local-looking pair is not a global deadlock because a third job can open a completion path. The four siphon agreements occupy IMS-SIP\(^1\). The four refusals occupy the hypotheses that Proposition 3 declines to inherit from S3PR monitor theory [1], [3]. A cycle/SCC screen alone would mark the residual cycle as a stop and is therefore not used as a theorem.

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

## VII. Discussion and Limitations

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

## VIII. Conclusion

Local blocking in a finite manufacturing resource-allocation system is a first hit of a certified stopped-process set, not a wait-for cycle and not a plant terminal SCC. The set is admitted by a request-closed structural argument or by a complete-LTS nonreachability audit, and it is refused when a completion bypass exists. Diagnostic siphons apply only on a wait-snapshot of the unit-capacity one-hold-one-request subclass. Exact and simulated first-hit values share a stopping hash only after the absorption domain is certified. A three-job machine–AGV island, a ten-plant baseline table, a tandem scale family, and a four-field CRP diagnostic support those sentences and no stronger ones.

The checkable object is the typed first-hit set. Controllers, monitors, shop-floor policies, and general plant-net isomorphisms are outside the claim.

---

## Appendix A  
Retained Negative Clothings

An island that marked a job complete while it still held the next buffer was refused as `completed_job_holds_resource` (invalid LTS state) and is not replaced in place. A repaired all-completion island with the same topology produced Barrier A certified and \(\theta_b=0\) on both the base and the intervention; it is a certified demonstration that an always-finishing twin cannot clothe Theorem 1. Both clothings remain in the evidence record.

## Appendix B  
Implementation Notes

Certificates, LTS enumeration, the wait-snapshot bridge, Barrier A, the absorbing CTMC, and the DES shards are generated from one registry. Independent plants and DES shards run in a process pool; BLAS threads equal one. Primary DES finishes before reproduction. Evidence roots are write-once. The quantitative protocol, including the Hoeffding band and the seeds, is fixed before the island wave.

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

**Fig. 1.** Operational distinction used throughout the paper. A wait-for cycle or an empty plant-net siphon is a structural candidate. A local closed kernel becomes \(D_\mathrm{local}\) only after typed admission (Theorem 1 or Proposition 1) and bypass refusal (Proposition 2). The stopped process first-hits \(D_\mathrm{global}\), \(D_\mathrm{local}\), or \(F\). The plant LTS may still have outgoing arcs at a \(D_\mathrm{local}\) state.

**Fig. 2.** Exact first-hit KPIs on the three-job machine–AGV island (Family IV). Base: already a local hit. Optional AGV drain: every trajectory completes. Files: `docs/paper/figures/fig_h4_island_kpis.pdf`, `.png`.

**Fig. 3.** Tandem scale (Family III, unit capacity). Left: \(\lvert X\rvert\) versus jobs (log). Right: runtime versus jobs (log). Horizontal guides mark \(10^3\), \(10^4\) states and the \(300\,\mathrm{s}\) cap. Files: `docs/paper/figures/fig_h3_scale.pdf`, `.png`.

---

*End of double-anonymous Regular Paper draft. Conversion to the IEEE two-column template is a later production step; scientific claims in that conversion must remain identical to this file.*
