# Theorem–Case Loop Map

Status: `MAP / NO SCIENCE EXECUTION`
Worktree HEAD base: `5f852e06650e29b71f79bc344246aca79524bfba`
Companion audit: `docs/verification/JOURNAL_THEORY_AUDIT_V1.md`

Four columns only. A later hardening spec may not contradict a `closed` or
`correctly open` row without a new version id.

| Theorem / claim | Required witness type | Existing case / evidence | Gap |
| --- | --- | --- | --- |
| P1 finite LTS + reachability-net representation | small-model state/edge bijection | C0–C5 enumeration tests | closed as representation; not a novelty |
| P2 covering-core iff capacity-mediated global deadlock | covering kernel + no admissible successor | C0; article global positive | closed on small declared-registry models; tighten “relative to registry” |
| cycle ≠ deadlock | residual-feasible cycle | C1 / CE-C1 | scientifically closed; ledger rebound in this tranche |
| P3 chain-decomposable strict-precedence sufficient | DAG + no covering kernel | C2 | closed as sufficient condition |
| P3 not vacuous | covering kernel that is not chain-decomposable, P3 refuses | H1 P3 `not_applicable` | **closed in tase v1** |
| multi-capacity ≠ simple cycle / WCC shortcut | residual or incomplete coverage | C3 / CE-C3 | IMS screening closed; Palmer 2/3-server replica not required for Paper A |
| AGV projection false negative | machine projection live, full model deadlocked | C4 / CE-C4 | discovery closed; not a journal-scale transport study |
| island bidirectional / DAG repair | paired ring vs deleted backflow | C5 + C5_DAG; BIX2-PERSIST | discovery closed; P3e remains a 3-resource subclass |
| P2c `IMS-SIP^1` siphon dual | unit-capacity one-hold/one-request bijection | C0; CE-SIP1 inverse-map refusal | closed inside `IMS-SIP^1` only |
| P3d/P3e exact thresholds | preregistered grids | BIX1-SAT; BIX2 32-row grid | closed for those families; PO-T4-6e still open |
| A2b local noncompletion | request-closed local kernel, outside job still moves | article A2b positive | constructively closed |
| complete-LTS fallback | local hit with plant outgoing arcs, `F` unreachable | article multi-kernel | constructively closed |
| bypass refusal | local candidate path to `F` | article bypass; CE-G6-BYPASS | closed |
| global-before-local convention | global predicate plus local-looking core counted once | article overlap control | closed as versioned convention |
| exact/DES same-target | 18 predeclared cells | article-core v1 | closed as within-case cross-check |
| `S_T` ≠ support reachability | path to `F` exists but unselected closed class reachable | CE-NB1 + terminal-class test | closed as boundary |
| CRP local bridge | four independent Prop 6.4 fields | G5 `G4_CRP_S4PR_AGREE` falsified | **not a positive journal result** |
| unselected closed class in island CTMC | classified `R_*` or certified `S_T` | G5 grid/medium inconclusive; mechanism repaired | **no new independent quantitative island** |
| plant/S3PR general isomorphism | none allowed | none | correctly open |
| risk-budget supervisor / Pareto | recursive feasibility theorem | none | correctly open |
| same-semantics baselines | cycle / closed-core / siphon-or-refuse / LTS truth | none unified | **T-ASE blocker; Family H2** |
| scale / diversity | parameterized enumerable or typed refusal | none as a panel | **T-ASE blocker; Family H3** |
| realistic manufacturing KPI | documented island + intervention + predeclared KPI | H4 v2 certified but \(\theta_b=0\) | **T-ASE blocker; H4-v3 must deadlock** |
| non-confluent closure | two zero-time sequences, two stable successors | H1 CL1 | **closed in tase v1** |
| optional drain ≠ structural repair | controllable alternate drain, ring prefix still reachable | H1 BIXD2 | **closed in tase v1** |
| intervention creates new core | delete backflow, new kernel appears | H1 INT1 | **closed in tase v1** |
| soft reservation ≠ capacity | two soft claims, one physical slot | CE-RSV1 only | open; not required for Paper A centre |

## Journal split frozen by this map

- Paper A (this worktree): typed local first-hit + T-ASE hardening of
  baselines, scale, and one high-fidelity island.
- Paper B (later): covering-core, P3/P3d/P3e, `IMS-SIP^1`.
- Paper C (later): risk-budget supervisor, only if a new theorem closes.
- Original G6-B eight-dimension overlap: optional, not on the critical path.
- Target venue for Paper A after hardening: IEEE T-ASE.
- Automatica / TAC are not current targets.

## Loop verdict

Paper A’s scoped constructive loop is **closed**.
The top-journal loop is **not closed**. The missing witnesses are H1–H4,
not another audit of P1–P6 and not a relabel of article-core v1.
