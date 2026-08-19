# Novelty Difference Matrix

Status: `P4 LOCATORS ATTACHED / NO PRIORITY CLAIM FROM RENAMING`
Base HEAD: `5f852e06650e29b71f79bc344246aca79524bfba`
Worktree HEAD at attachment: `2527db45da28ea4478d7c713a7f6d40b3e3a5101`
Axes: definition / assumption / output / complexity / checkable object
G1 authority: `docs/literature/LITERATURE_MATRIX.md` and
  `docs/literature/FULLTEXT_AUDIT_L30_L35_B05.md`

This matrix answers one reviewer question per row: what condition do they
lack that this project adds, and what object can be checked? It does not
claim that siphon control, RAS safety, CTMC committors, or Gillespie
sampling are new.

| Comparator family | Definition they use | Assumption we do not inherit | Our added output | Complexity we may claim | Checkable object |
| --- | --- | --- | --- | --- | --- |
| Classical wait-for cycle / SCC | directed wait graph cycle or terminal SCC | residual capacity, OR-of-AND alternatives, BAS hold-after-service | covering closed core with witness/holder records; C1 residual cycle is not deadlock | graph scan is cheap; not a completeness claim for IMS | C1; Family H2 false-positive column; H2-v2 `residual_cycle` |
| Palmer knot / no-sink WCC | queueing-network knot shortcuts | single-server or 2-server special cases | capacity-mediated kernel, not WCC shortcut | do not claim a new knot theorem | C3 screening; Palmer 2/3-server remains literature baseline |
| Petri siphon / monitor (`S3PR`, `B05`) | empty or unmarked siphon on a plant net; monitor places | plant-level S3PR structure; compact monitor form | `IMS-SIP^1` diagnostic wait-snapshot dual only; typed refusal outside it | siphon enum on the small diagnostic net; not bit-polynomial plant reachability | CE-SIP1; P2c; H2-v2 siphon-agree and typed-refusal columns |
| Finite-capacity resource configuration (`L30`) | sufficient initial marking inequalities | exact reachable iff threshold | family-specific BIX1/BIX2 reachable thresholds | those families only | BIX grids; cannot beat `L30` on general S3PR |
| S4PR CRP (`L31`) | marking-level partial-deadlock iff, then SBA | S4PR embedding; CRP resource set is the local kernel | local-kernel family + four-field partial bridge (Prop 6.4) | NP-hard reachability remains | G5 CRP row is a **negative** implementation witness, not a CRP refutation; H5 omitted this tranche |
| Recorder / transformed PN (`L32`–`L35`) | reachability after model transform or NIS legal sequence | IMS operational ≡ transformed plant | independent BFS / executable prefix obligation | do not claim bit-polynomial IMS reachability | G4 recorder/L34 obligations stay open or adapted-oracle |
| Sequential RAS / Banker | ordered resource avoidance | BAS hold-after-service, AGV occupancy, reservations as first-class tokens | same objects in one certificate | Banker-style sufficient tests remain baselines, not theorems | C4/C5; Family H2 |
| Partial / local deadlock (`L29`, informal “local cycle”) | local marking or subgraph deadlock | local cycle ⇒ irreversible completion failure | typed admission: A2b **or** complete-LTS; bypass refusal | A2b is structural on a subclass; LTS route is model-specific and exponential | article A2b / multi-kernel / bypass; H4-v3 `D_local` island |
| Supervisory control (Ramadge–Wonham, `B05`) | max nonblocking controllable sublanguage or monitor cover | full observation, explicit LTS, compact monitor | finite state-based supervisor baseline (P5); not risk-budget optimal | explicit-graph polynomial; compact input at least NP-hard | P5 tests; Paper C still open |
| Absorbing CTMC / committor / Doob-`h` | standard linear equations | almost-sure hit of a declared `D/F` partition | certified `S_T`, unselected-class refusal, same-target DES hash | standard linear algebra on `\|S_T\|` | CE-NB1; article 18 cells; do not claim new CTMC math |
| Exact vs simulation validation | interval coverage or visual overlay | DES as theorem proof or plant-fidelity proof | same stopping hash, frozen seed, simultaneous tolerance | statistical only for the declared `n` | article-core v1; F7 remains forbidden |

## G1 locators (P4)

Every Paper A related-work sentence must footnote one of these rows.
Locators are copied from the G1 full-text audit. They are not new claims.

| Citation | G1 locator | They lack | We add (checkable) | Paper A ids allowed to cite |
| --- | --- | --- | --- | --- |
| L29 Lu–Chen–Hadjicostis–Li, Automatica 2026 | Def. 3 MR2G; Def. 4 safe place; Thm. 1 PDDP iff partial-deadlock marking; Alg. 1; Thm. 2 controlled-net liveness. DOI 10.1016/j.automatica.2025.112631 | IMS BAS / AGV / reservation / closure; typed bypass refusal; first-hit probability | A2b or complete-LTS admission; H4-v3 `D_local` vs completion partition | TA1, TA2, TA4 |
| L30 Pang et al. 2025 finite-capacity S3PR | PDF p3 Def. 1; p4 Defs. 2–3 ENS3PR; p5 Defs. 4–6 and Thms. 1–3; p6 Alg. 1; pp7–8 `O(2^Np)` | exact reachable iff threshold; BAS/AGV/OR-of-AND | family-specific BIX thresholds only; H3-v2 reports `|X|`, not a configuration theorem | none as a T-ASE main theorem; limitation sentence only |
| L31 Su et al. T-ASE 2026 CRP | PDF p4 Defs. 5–6; p5 Defs. 7–8 and Thm. 1; p6 Def. 10 and Thms. 2–4; p7 SBA / Alg. S3 | IMS operational certificate; CRP equations are not a reachable-prefix proof | independent LTS BFS prefix; Prop 6.4 four-field *rule* (G5 negative; H5 omitted) | TA3, TA10 as contrast, not “we refute CRP” |
| B05 Chen–Li Automatica 2011 MCPP | PDF p3 Defs. 1–3; p4 MCPP and Alg. 1; p5 Thm. 1; full-RG + NP-hard MCPP | scalable IMS monitor; general monitor expressibility | `IMS-SIP^1` diagnostic dual on a wait-snapshot, refused outside unit/residual-0/one-hold-one-request | TA9, TA10 |
| L01 Ezpeleta–Colom–Martinez 1995 | Cor. V.2; Thm. VI.1; Sec. VI control policy | BAS, AGV, reservation | same siphon-control contrast as B05; no S3PR isomorphism | TA10 |
| L08 Lawley–Reveliotis 2001 | PDF p10 Thm. 1 SU-SAFE NP-c; p15 Prop. 2; pp18–24 capacitated-knot | BAS, AND demand, AGV/zero-time | capacity-mediated closed core; C1 residual cycle is not deadlock | TA1, TA9 |
| L17 Palmer–Harper–Knight 2018 | p3 Thm. 1; p3–p6 Thm. 2; p6–p7 2/3-server counterexample | queueing node ≢ IMS resource | knot screen as baseline column only | TA9 |
| L16 Narahari–Viswanadham–Krishna Prasad 1990 | Sec. 3 `F=(I-T)^-1`; MTTD; Sec. 4 deadlock-time distribution | IMS committor / Doob-h / certified `S_T` | same-target exact/DES after Barrier A | TA6 |
| L09 Nazeem–Reveliotis T-ASE 2011 | PDF p5 Prop. 1, Def. 1, Sec. III boundary-unsafe LES | no IMS structural certificate | finite-state supervisor remains a later baseline, not Paper A centre | none on Paper A main claims |
| L06 Ramadge–Wonham 1987 | Thm. 7.1 and Prop. 7.1 pp. 218–219 | no structural deadlock certificate | P5 finite-state supervisor later; not this paper’s centre | none on Paper A main claims |

## Paper A novelty sentence

The publishable increment is not “we compute deadlock probability.” It is:

```text
local blocking is a verified stopped-process first-hit set,
admitted by one of two typed routes,
refused when a completion bypass exists,
and connected to exact/DES only after the absorption domain is certified.
```

Everything else is either classical, restricted, or later-paper material.

## Forbidden shortcuts

- Do not write “first reachable structural certificate” (`L31`).
- Do not write “first finite-capacity threshold” (`L30`, BIX families).
- Do not write “first polynomial Petri reachability” (`L32`–`L35`).
- Do not write “Doob-`h` is a controller.”
- Do not write “exact/DES agreement proves the theorem.”
- Do not write “first siphon-free detector” (`B05`, `L01`, `L29`).
