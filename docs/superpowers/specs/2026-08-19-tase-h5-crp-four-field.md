# T-ASE H5 — Proposition 6.4 Four-Field Diagnostic

Status: `DESIGN / DIAGNOSTIC ONLY / NO L31 THEOREM / WORKTREE ONLY`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Prop: G6 Proposition 6.4
Roots: `cases/discovery/tase_hardening_v1/h5/`,
  `evidence/tase_hardening/h5/`

This tranche implements the *rule*, not Su et al. CRP. It does not run
SBA, does not generate CRP candidates, and does not reuse G4/G5 hashes.

## 1. Four independent fields

Given a frozen target and a declared resource set `R_crp`:

1. target reachable in the frozen stable LTS (independent BFS);
2. local certificate family available at that target;
3. `matching_kernel_count = |{K : resources(K)=R_crp}|`;
4. source profile in a declared S4PR overlap with an *independent*
   embedding hash.

Agreement is true only if all four hold. A global covering certificate
must not substitute for (2)–(3).

## 2. Field 4 is refused on purpose

This project has no audited external S4PR embedding for a new plant.
PO-T3-8a forbids inventing one. Therefore every H5 row sets

```text
s4pr_overlap = false
field4_reason = no_independent_s4pr_embedding
bridge_agreement = false
```

Rows still expose fields 1–3 so a reviewer can see the rule working:

| subject | intended 1–3 |
| --- | --- |
| `H5_unit_pair_fields123` | reachable, family, match `{r1,r2}` |
| `H5_unit_triple_fields123` | reachable, family, match `{r1,r2,r3}` |
| `H5_reachable_pair_fields123` | reachable via LTS witness, match |
| `H5_wrong_r_crp_zero_match` | family exists, match count 0 |
| `H5_outside_agv_and` | IMS AND/AGV plant; still no field 4 |
| `H5_residual_no_local_family` | residual C1 cycle; no local family |

G5 `G4_CRP_S4PR_AGREE` remains the historical *negative* witness.
H5 is not a repair of G5 and not a CRP refutation.

## 3. Forbidden sentences

- “We have a CRP theorem.”
- “We disproved Su et al.”
- “First reachable partial-deadlock certificate.”
- Any reuse of G4/G5 case, snapshot, or raw hashes.
