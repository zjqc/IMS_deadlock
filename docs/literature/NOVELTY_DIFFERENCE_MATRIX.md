# Novelty Difference Matrix

Status: `POSITIONING / NO PRIORITY CLAIM FROM RENAMING`
Base HEAD: `5f852e06650e29b71f79bc344246aca79524bfba`
Axes: definition / assumption / output / complexity / checkable object

This matrix answers one reviewer question per row: what condition do they
lack that this project adds, and what object can be checked? It does not
claim that siphon control, RAS safety, CTMC committors, or Gillespie
sampling are new.

| Comparator family | Definition they use | Assumption we do not inherit | Our added output | Complexity we may claim | Checkable object |
| --- | --- | --- | --- | --- | --- |
| Classical wait-for cycle / SCC | directed wait graph cycle or terminal SCC | residual capacity, OR-of-AND alternatives, BAS hold-after-service | covering closed core with witness/holder records; C1 residual cycle is not deadlock | graph scan is cheap; not a completeness claim for IMS | C1; Family H2 false-positive column |
| Palmer knot / no-sink WCC | queueing-network knot shortcuts | single-server or 2-server special cases | capacity-mediated kernel, not WCC shortcut | do not claim a new knot theorem | C3 screening; Palmer 2/3-server remains literature baseline |
| Petri siphon / monitor (`S3PR`, `B05`) | empty or unmarked siphon on a plant net; monitor places | plant-level S3PR structure; compact monitor form | `IMS-SIP^1` diagnostic wait-snapshot dual only; typed refusal outside it | siphon enum on the small diagnostic net; not bit-polynomial plant reachability | CE-SIP1; P2c; Family H2 siphon-or-refuse |
| Finite-capacity resource configuration (`L30`) | sufficient initial marking inequalities | exact reachable iff threshold | family-specific BIX1/BIX2 reachable thresholds | those families only | BIX grids; cannot beat `L30` on general S3PR |
| S4PR CRP (`L31`) | marking-level partial-deadlock iff, then SBA | S4PR embedding; CRP resource set is the local kernel | local-kernel family + four-field partial bridge (Prop 6.4) | NP-hard reachability remains | G5 CRP row is a **negative** implementation witness, not a CRP refutation |
| Recorder / transformed PN (`L32`–`L35`) | reachability after model transform or NIS legal sequence | IMS operational ≡ transformed plant | independent BFS / executable prefix obligation | do not claim bit-polynomial IMS reachability | G4 recorder/L34 obligations stay open or adapted-oracle |
| Sequential RAS / Banker | ordered resource avoidance | BAS hold-after-service, AGV occupancy, reservations as first-class tokens | same objects in one certificate | Banker-style sufficient tests remain baselines, not theorems | C4/C5; Family H2 |
| Partial / local deadlock (`L29`, informal “local cycle”) | local marking or subgraph deadlock | local cycle ⇒ irreversible completion failure | typed admission: A2b **or** complete-LTS; bypass refusal | A2b is structural on a subclass; LTS route is model-specific and exponential | article A2b / multi-kernel / bypass; C1–C4 of claim matrix |
| Supervisory control (Ramadge–Wonham, `B05`) | max nonblocking controllable sublanguage or monitor cover | full observation, explicit LTS, compact monitor | finite state-based supervisor baseline (P5); not risk-budget optimal | explicit-graph polynomial; compact input at least NP-hard | P5 tests; Paper C still open |
| Absorbing CTMC / committor / Doob-`h` | standard linear equations | almost-sure hit of a declared `D/F` partition | certified `S_T`, unselected-class refusal, same-target DES hash | standard linear algebra on `\|S_T\|` | CE-NB1; article 18 cells; do not claim new CTMC math |
| Exact vs simulation validation | interval coverage or visual overlay | DES as theorem proof or plant-fidelity proof | same stopping hash, frozen seed, simultaneous tolerance | statistical only for the declared `n` | article-core v1; F7 remains forbidden |

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
