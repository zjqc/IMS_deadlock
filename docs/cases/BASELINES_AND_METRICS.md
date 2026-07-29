# Baselines and Metrics

## Baselines

| Baseline | Purpose | Expected limitation |
| --- | --- | --- |
| simple directed cycle | cheap static screen | false positives when WIP/capacity cannot populate a cycle; false negatives when transport/reservation edges are omitted. |
| state-dependent knot | structural certificate baseline | requires full state-dependent wait graph after zero-time closure. |
| Banker safety sequence | RAS safety benchmark | may not match BAS blocked-complete and AGV blocked-unload semantics without adaptation. |
| siphon control | Petri-net bridge benchmark | valid only after explicit IMS-to-Petri assumptions are satisfied. |
| exact maximally permissive supervisor | finite-state gold standard | state explosion; benchmark only for small and medium finite models. |
| delete-backflow route repair | manufacturing-island practical repair | can sacrifice throughput and may overfit one route family. |

## Metrics

| Metric | Definition | Evidence source |
| --- | --- | --- |
| theorem prediction correctness | whether the stated theorem predicts deadlock/nondeadlock and certificate existence for a frozen case | frozen prediction sheet and enumeration output |
| certificate minimality | no proper subkernel is also closed and blocking under the same state | exhaustive subset check |
| exact deadlock probability | absorbing probability of reaching any deadlock class before completion | CTMC linear solve |
| mean absorption time | expected time to completion or deadlock; optionally conditional on deadlock | CTMC linear solve |
| conditioned path mass | probability flux through certificate-bearing states conditioned on deadlock | committor/Doob-h computation |
| DES confidence interval | independent simulation estimate with fixed random streams | simulation manifest |
| supervisor cost | all preregistered and applicable components: throughput loss, makespan loss, WIP change, and due-date-risk change relative to the uncontrolled feasible baseline | exact supervisor and simulation |
| rare-event efficiency | variance, effective sample size, and wall-clock cost for rare deadlock estimation | rare-event experiment logs |

## Reporting Rules

- Report negative and failed results.
- Report cases where a baseline is inapplicable instead of forcing a score.
- Do not choose one supervisor-cost component after seeing results. After
  freeze, report every preregistered and applicable component: throughput,
  makespan, WIP, and due-date risk. Any inapplicable component must have a
  freeze-time reason.
- Separate exact finite-state results from DES sampling estimates.
- Do not compare against old private project numbers.
