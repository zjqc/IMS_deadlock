# Literature Matrix

Status values are defined in `SEARCH_PROTOCOL.md`. `FULLTEXT-THEOREM` requires
full-text inspection plus a reproducible theorem, section, appendix, or equation
locator. `FULLTEXT-CONTEXT`, `ABSTRACT`, `METADATA`, and `PENDING` rows are not
proof sources for theorem statements.

## Core Verified Matrix

These rows have enough bibliographic identity and field completion to remain in
the core matrix. Low-evidence rows may guide search or background only.

| ID | Chain | Source | Model | Main assumptions | Result / theorem type | Proof technique | Complexity | Counterexample / boundary | IMS transferable | IMS non-transferable | DOI / authority | Status | Locator |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L01 | Petri/S3PR | Ezpeleta, Colom, Martinez 1995 | S3PR Petri nets | sequential processes sharing reusable resources | S3PR liveness and siphon-control policy | structural PN and monitor construction | not IMS-wide | only within S3PR assumptions | restricted siphon bridge seed | no BAS, AGV, reservation semantics | https://doi.org/10.1109/70.370500 | FULLTEXT-THEOREM | Corollary V.2; Theorem VI.1; Section VI control policy |
| L02 | Petri/S3PR | Li and Zhou 2004 | elementary siphons in PN/FMS | ordinary Petri-net FMS classes | elementary siphon definitions, controllability, algorithms, FMS application | elementary-siphon decomposition and monitors | algorithmic burden depends on siphon structure | rest-dependent siphons and controllability conditions | context for minimal siphon bridge | no IMS operational equivalence | https://doi.org/10.1109/TSMCA.2003.820576 | FULLTEXT-CONTEXT | author PDF; Sections 3, 4, 5, 7; no theorem locator used |
| L03 | Petri/S3PR | Li et al. 2012 survey | Petri-net deadlock control taxonomy | multiple PN subclasses | survey of deadlock prevention/control methods | literature synthesis | survey only | subclass-specific claims | map of PN school | no direct theorem migration | https://doi.org/10.1109/TSMCC.2011.2160626 | METADATA | DOI verified only |
| L04 | Petri/S3PR | Liu et al. siphon survey | ordinary PN and S3PR | marked siphons | siphon theorem map and S3PR liveness discussion | PN structural review | not fixed | class-sensitive necessity/sufficiency | siphon proof backlog | cannot replace IMS certificate | https://doi.org/10.1016/j.ins.2015.08.037 | FULLTEXT-CONTEXT | theorem-number clues only; stable page/equation locator still pending |
| L05 | Petri/S3PR | Yamalidou et al. 1996 | controlled Petri nets | linear marking constraints | place-invariant control design | invariant synthesis | not fixed | uncontrollable transition restrictions | supervisor constraint encoding | IMS completion/unload semantics not modeled | https://doi.org/10.1016/0005-1098(95)00103-4 | METADATA | DOI verified only |
| L06 | DES/RAS | Ramadge and Wonham 1987 | DES languages | controllable/uncontrollable event partition | supervisory control and supremal controllable language baseline | formal-language fixed point | state explosion | observability/nonblocking variants need care | exact finite-state benchmark | no structural deadlock certificate | https://doi.org/10.1137/0325013 | FULLTEXT-CONTEXT | publication metadata and full-text access known; no theorem locator recorded here |
| L07 | DES/RAS | Wonham and Ramadge 1988 | modular DES | modular plants/supervisors | modular supervisory control | automata/language composition | composition complexity | nonconflicting modules needed | decomposition candidate | IMS shared resources may violate modularity | https://doi.org/10.1007/BF02551233 | METADATA | DOI verified only |
| L08 | DES/RAS | Lawley and Reveliotis 2001 | SU-RAS | sequential resource allocation; safety states | SU-RAS safety NP-complete; hard/easy boundary; polynomial subclasses | reduction and structural classification | NP-complete for safety in SU-RAS | easy subclasses only under specified structures | safety-set and subclass boundary | BAS/AGV/zero-time closure not explicit | https://doi.org/10.1023/A:1012203214611 | FULLTEXT-THEOREM | author PDF; Sections 3, 4, 5 |
| L09 | DES/RAS | Nazeem and Reveliotis 2011 | complex RAS LES | finite RAS; liveness-enforcing supervision | offline/online two-stage maximally permissive LES design framework | automata and compact safe/unsafe representation | NP-hardness motivates deployment approach | finite RAS assumptions | exact supervisor benchmark for small IMS | not an IMS structural theorem | https://doi.org/10.1109/TASE.2011.2159112 | FULLTEXT-THEOREM | author `CASE-2010.pdf`; Abstract; Sections II-III |
| L10 | DES/RAS | Fei et al. 2015 | EFA/BDD RAS control | finite-state RAS encoded symbolically | Algorithm 2 correctness for BDD-based control computation | symbolic BDD/EFA construction | mitigates, not removes, state growth | implementation scale depends on encoding | exact/symbolic benchmark | no IMS bridge without semantic mapping | https://doi.org/10.1109/TASE.2014.2369858 | FULLTEXT-THEOREM | author PDF; Sections III-IV; Theorem IV.1 |
| L11 | DES/RAS | Cordone et al. 2013 | deadlock avoidance policies | specific RAS/DAP model classes | optimal/approximate policy candidate | graph/optimization methods | class-dependent | assumptions pending | complexity/backstop candidate | not a theorem source yet | https://doi.org/10.1109/TAC.2013.2266952 | METADATA | DOI verified only |
| L12 | DES/RAS | Reveliotis and Nazeem 2013 | DAP mathematical programming | complex finite RAS | exact/compact DAP candidate | optimization and automata | hard exact synthesis | compactness is structural | finite IMS benchmark candidate | BAS semantics absent | https://doi.org/10.1137/120866427 | METADATA | DOI verified only |
| L13 | DES/RAS | Liu 2016 complexity | Petri-net resource allocation | PNRA/G-system variants | PSPACE/NP complexity clue | reductions | PSPACE-complete / NP-complete candidate | exact class assumptions pending | complexity warning | no citation as proof before locator | https://doi.org/10.1016/j.ins.2015.11.025 | ABSTRACT | abstract/metadata only |
| L14 | Queueing | Kundu and Akyildiz 1989 | finite-buffer queueing networks | blocking after service and finite buffers | deadlock/buffer allocation concepts | queueing-network analysis | class dependent | blocking discipline matters | BAS vocabulary candidate | routes/AGV absent | https://doi.org/10.1007/BF01150855 | METADATA | DOI verified only |
| L15 | Queueing | Akyildiz and von Brand 1994 | finite-buffer queueing networks | blocking mechanisms | blocking-network analysis boundary | queueing theory | state-space growth | product-form restrictions | finite-buffer baseline | not an IMS certificate theorem | https://doi.org/10.1016/0304-3975(94)90296-8 | METADATA | DOI verified only |
| L16 | Queueing | Narahari, Viswanadham, Krishna Prasad 1990 | manufacturing performance and deadlock | official abstract states absorbing Markov modeling | MTTD, parts until deadlock, distribution clues | absorbing Markov chain candidate | state-space limited | no equation locator in this library | probability background only | cannot support equations yet | https://doi.org/10.1007/BF02811330 | ABSTRACT | official abstract/metadata only |
| L17 | Queueing | Palmer, Harper, Knight 2018 | open restricted queueing networks | finite buffers; state-dependent blocking graph `D(t)` | deadlocked iff `D(t)` contains a knot; WCC shortcut restrictions | SCC/knot graph proof | brute-force SCC in simulation | 2-node 2/3-server counterexample | knot certificate backbone | queueing nodes not IMS resources one-to-one | https://doi.org/10.1016/j.ejor.2017.10.039 | FULLTEXT-THEOREM | p3 Theorem 1; p3-p6 Theorem 2; p6-p7 counterexample |
| L18 | AGV/traffic | Wu and Zhou 2001 | resource-oriented PN for AGV | AGV circuits and cycle chains | circuit/cycle-chain deadlock-free conditions and control law | Petri-net/graph structural control | not IMS-wide | theorem assumptions are AGV-system specific | transport-resource proof vocabulary | cannot cover machines/BAS alone | https://doi.org/10.1109/ROBOT.2001.932531 | FULLTEXT-THEOREM | full text; Theorems 3.1, 3.2, 4.1, 5.1 |
| L20 | AGV/traffic | IET 2022 container terminal PN | interacting terminal equipment | Petri-net equipment interaction model | deadlock detection and recovery for automated container terminals | Petri-net analysis | pending | not generic AGV theorem | reservation/equipment analogy | title must not be generalized | https://doi.org/10.1049/itr2.12168 | METADATA | corrected title verified |
| L21 | AGV/traffic | Viswanadham, Johnson, Narahari 1990 conference text | AGV + two machines example | finite manufacturing with transporter | illustrative three-resource deadlock | example reasoning | none | no DOI/provenance limitation | `C4` inspiration | not a proof source | no DOI; provenance-limited conference text | FULLTEXT-CONTEXT | example: m2 + AGV + m1 blocking chain |
| L22 | Petri/RAS | Viswanadham, Narahari, Johnson 1990 journal | FMS Petri-net models | FMS resources modeled by PN | deadlock prevention and avoidance in FMS using PN models | Petri-net modeling/control candidate | pending | not read for theorem use | canonical nearby journal source | distinct from L21 conference example | https://doi.org/10.1109/70.63257 | METADATA | Crossref title/authors/journal/year verified |
| L23 | CTMC/committor | Metzner, Schutte, Vanden-Eijnden 2009 | Markov jump processes | ergodic continuous-time Markov chain; A-B reactive paths | transition path theory; discrete committor equations | Markov-process potential theory | finite/discrete state computations | not an absorbing IMS-deadlock theorem | committor/path-flux formalism | must adapt from ergodic A-B setting to competing absorbing IMS classes | https://doi.org/10.1137/070699500 | FULLTEXT-THEOREM | SIAM article; Appendix "Discrete committor equations" around pp.1216 ff. |
| L25 | Rare event | Cerou and Guyader 2007 | rare-event simulation | Markov/rare event setting | adaptive multilevel splitting candidate | simulation/probability methods | estimator efficiency context | not IMS-specific | future rare-event estimator context | no migrated theorem yet | https://doi.org/10.1080/07362990601139628 | FULLTEXT-CONTEXT | source identified; no theorem migration recorded |
| L27 | Error | Wrong siphon-survey DOI | unrelated l1-gain paper | none for IMS | none | none | none | false-positive DOI | none | must not cite | https://doi.org/10.1016/j.ins.2016.02.010 | REJECTED/CORRECTED | rejected; corrected to L04 |

## Candidate Backlog

These are deliberately outside the core matrix until a full-text locator or a
clear non-use decision is recorded.

| ID | Chain | Candidate | Reason kept | DOI / authority | Status | Next check |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | Petri/S3PR | Li et al. 2017 elementary siphon | possible refined elementary-siphon bridge | https://doi.org/10.1177/1687814017734709 | METADATA | extract theorem locators |
| B02 | DES/RAS | Reveliotis monograph | terminology and RAS control baseline | https://doi.org/10.1561/2600000010 | METADATA | read relevant chapters |
| B03 | DES/RAS | Reveliotis 2016 review | review map for RAS logical control | https://doi.org/10.1016/j.arcontrol.2016.04.009 | METADATA | classify references |
| B04 | Petri/RAS | Chen et al. 2011 | maximally permissive PN supervisor candidate | https://doi.org/10.1109/TASE.2010.2060332 | METADATA | full-read assumptions |
| B05 | Petri/RAS | Chen and Li 2011 Automatica | high-quality PN maximum-permissive baseline | https://doi.org/10.1016/j.automatica.2011.01.070 | METADATA | full-read assumptions |
| B06 | DES/RAS | Reveliotis and Fei 2017 robust TASE | resource-outage extension boundary | https://doi.org/10.1109/TASE.2017.2722382 | FULLTEXT-CONTEXT | keep for future extensions, not first paper |
| B07 | DES/RAS | Reveliotis and Fei 2016 COASE | conference precursor to robust TASE | https://doi.org/10.1109/COASE.2016.7743492 | METADATA | cite journal first |
| B08 | Rare event | canonical Doob-h source beyond TPT | needed for conditioned absorbing IMS process | source to be selected | PENDING | identify primary theorem source |
| L19 | AGV/traffic | Wu and Zeng 2002 | AGV manufacturing system; guidepath/traffic constraints; deadlock-free routing/control candidate kept for transport modeling, but full text and theorem locator are pending | https://doi.org/10.1080/00207540110073037 | METADATA | full-read and extract assumptions before theorem use |
| L24 | CTMC/committor | Corstanje et al. 2022 | guided CTMP candidate for rare-path implementation; not deadlock-specific until read | https://doi.org/10.1080/17442508.2022.2150081 | METADATA | full-read before using any Markov-transform claim |
| L26 | Design/FMS | Design guidelines for deadlock handling 1997 | FMS deadlock-handling design framework candidate; guideline is not a theorem unless read | https://doi.org/10.1023/A:1007937925728 | METADATA | full-read for case-design context only |

## Coverage and Gate Status

Total tracked items: 35 (`24` core rows plus `11` backlog rows). The six chains
are covered, but unevenly: Petri/S3PR, DES/RAS, and queueing have strong seed
anchors; AGV has one theorem source and one provenance-limited example; CTMC
has a TPT theorem anchor; rare-event estimation remains context/backlog.

G1 is **not fully passed**. It has enough verified seed sources to start
formal definitions and proof obligations, but not enough verified full-text
locators to freeze all theorem claims or declare citation saturation.
