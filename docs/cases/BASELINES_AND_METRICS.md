# Baselines and Metrics

G4 status: `B-PREREGISTRATION-CANDIDATE-PENDING-C-SEAL`. The applicability
statements below describe the current preregistered candidate bundle only; they
are not held-out results.

## Baselines

| Baseline | Purpose | Expected limitation |
| --- | --- | --- |
| simple directed cycle | cheap static screen | false positives when WIP/capacity cannot populate a cycle; false negatives when transport/reservation edges are omitted. |
| state-dependent knot | structural certificate baseline | requires full state-dependent wait graph after zero-time closure. |
| Banker safety sequence | RAS safety benchmark | may not match BAS blocked-complete and AGV blocked-unload semantics without adaptation. |
| siphon control | Petri-net bridge benchmark | valid only after explicit IMS-to-Petri assumptions are satisfied. |
| exact maximally permissive supervisor | finite-state gold standard | state explosion; benchmark only for small and medium finite models. |
| delete-backflow route repair | manufacturing-island practical repair | can sacrifice throughput and may overfit one route family. |
| `L30` S3PR/ENS3PR resource configuration | finite-capacity Petri resource baseline | sufficient/conservative liveness configuration only; not an IMS exact reachable iff threshold. |
| `L31` CRP/SBA detector | S4PR partial-deadlock overlap comparator | CRP is marking-level; small confirmation cases require an explicit prefix and complete BFS/LTS oracle, with SBA reported separately; the overall source method remains computationally hard. |
| `L32/L33` recorder transformation | reachability-decidable Petri modeling comparator | output-only recorder places do not change original transition enabling; fixed-target recorder quantification still must be reported. |
| `L34/L35` BA/SBA filter | legal firing sequence check for a given NIS | parameter/pseudopolynomial bound; not a standard bit-polynomial IMS reachability theorem. |
| `B05` compressed supervisor | maximally permissive PN/RG comparator | requires full RG, legal/FBM covering, and NP-hard MCPP; inapplicable to large compact IMS by default. |

## G4 Baseline Applicability Boundary

The B candidate freezes applicability as a per-case manifest decision. The
important current boundaries are:

- `L31_CRP_EVIDENCE_PROFILE` applies only as an evidence-profile or refusal
  audit; it is not an SBA reproduction and never replaces complete finite-LTS
  reachability.
- `L30_SUPPLIED_SUFFICIENT_INEQUALITIES` applies only to the supplied
  finite-capacity S3PR/ENS3PR inequality row; it does not claim SMS enumeration
  or an exact IMS threshold.
- `L32_L33_FIXED_RECORDER_TARGET` applies only to the fixed recorder target
  row; it does not claim the source algorithm or its complexity result.
- `B05_ADAPTED_MONITOR_COVER` applies only to the supplied finite-LTS monitor
  candidate row; its optimality is restricted to the frozen candidate monitor
  set.
- `exact_max_nonblocking_supervisor` is a small finite-state baseline where
  applicability is manifest-declared. It is not a project-wide compact
  supervisor synthesis claim.

## Metrics

| Metric | Definition | Evidence source |
| --- | --- | --- |
| theorem prediction correctness | whether the stated theorem predicts deadlock/nondeadlock and certificate existence for a frozen case | frozen prediction sheet and enumeration output |
| certificate minimality | no proper subkernel is also closed and blocking under the same state | exhaustive subset check |
| exact deadlock probability | absorbing probability of reaching any deadlock class before completion | CTMC linear solve |
| mean absorption time | expected time to completion or deadlock; optionally conditional on deadlock | CTMC linear solve |
| conditioned path mass | probability flux through certificate-bearing states conditioned on deadlock | committor/Doob-h computation |
| DES confidence interval | per-master-seed direct Gillespie estimate and two-sided 95% Wilson score interval, with no post-result pooling or retuning | frozen random-stream and metric manifests |
| supervisor cost | all preregistered and applicable components: throughput loss, makespan loss, WIP change, and due-date-risk change relative to the uncontrolled feasible baseline | exact supervisor and simulation |
| rare-event efficiency | variance, effective sample size, and wall-clock cost for rare deadlock estimation | rare-event experiment logs |

## G4 Metric Applicability Boundary

The current G4 B candidate explicitly marks these metrics as inapplicable for
every G4 case:

- conditioned path mass;
- rare-event efficiency;
- supervisor throughput loss;
- supervisor makespan loss;
- supervisor WIP change;
- supervisor due-date-risk change.

Current quantitative applicability is restricted:

| Metric | Applicable G4 cases |
| --- | --- |
| exact deadlock probability | `G4_IMS_PARAMETER_GRID`, `G4_MEDIUM_ISLAND_REBUILD` |
| mean absorption time | `G4_IMS_PARAMETER_GRID`, `G4_MEDIUM_ISLAND_REBUILD` |
| DES confidence interval | `G4_IMS_PARAMETER_GRID`, `G4_MEDIUM_ISLAND_REBUILD` |

No current G4 row has an applicable supervisor-cost, conditioned-path-mass, or
rare-event-efficiency estimand. CTMC and DES reporting for G4 is limited to the
grid and medium rows above.

## Reporting Rules

- Report negative and failed results.
- Report cases where a baseline is inapplicable instead of forcing a score.
- Do not choose one supervisor-cost component after seeing results. After
  freeze, report every preregistered and applicable component: throughput,
  makespan, WIP, and due-date risk. Any inapplicable component must have a
  freeze-time reason.
- Separate exact finite-state results from DES sampling estimates.
- For grid and medium DES, report all three seed-specific 95% Wilson intervals
  and whether the exact CTMC probability lies in each; sampling does not replace
  the exact solver.
- Do not compare against old private project numbers.
