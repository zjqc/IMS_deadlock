# T-ASE H2-v2 / H3-v2 Design

Status: `DESIGN / AUTHORIZED BY CONTINUATION / WORKTREE ONLY`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Programme: `docs/superpowers/specs/2026-08-19-tase-submission-programme.md`
User authorization: 2026-08-19 instruction “持续推进，自行迭代优化”
  after T6 quantitative approval. New evidence roots only.

This file authorizes P2 and P3 *implementation and one write-once wave each*.
It does not authorize overwriting H2/H3 v1, H4 v1/v2/v3, or article-core v1.
It does not authorize a G4/G5 CRP hash replay. CRP overlap is **omitted**.

## 1. Diagnosis that this tranche repairs

H2 v1 scored siphon as `sip1_or_refuse` on 32 plants and recorded 32/32
refusals. Live probe on this worktree showed the dominant cause:

- `_check_sip1_assumptions` requires unit capacity, residual 0,
  one-hold-one-request, no OR/AND, and
  `certificate.shortest_reachable_prefix is not None`.
- `find_deadlock_certificate(...)` defaults the prefix to `None`.
- H2 capacity cells (`one-below` / `balanced` / `loose`) inflate
  capacity, so even the named `sip1_positive` type fails SIP1 on residual
  or missing witness.

H3 v1 is a 576-row axis product whose plants are one- or two-step. Max
enumerated size was 496 states. That cannot be a T-ASE scale figure.

## 2. P2 — H2-v2 in-domain table

Curated 10 plants, not an 8×4 capacity product.

| type_id | role | SIP1 gate intended to fire |
| --- | --- | --- |
| `sip1_unit_pair` | agree | 2-job unit cycle, prefix `()` |
| `sip1_unit_triple` | agree | 3-job unit cycle, prefix `()` |
| `sip1_reachable_pair` | agree | idle start; prefix is the LTS witness |
| `sip1_machine_agv_unit` | agree | unit machine–AGV cycle, no AND |
| `refuse_or` | typed refusal | OR alternatives |
| `refuse_and` | typed refusal | conjunctive demand |
| `refuse_multi_capacity` | typed refusal | capacity 2, residual 0 |
| `refuse_agv_and` | typed refusal | AGV+buffer AND (H2 `agv_required` tight) |
| `residual_cycle` | C1 boundary | residual wait-cycle, not deadlock |
| `local_with_bypass` | bypass boundary | local-looking cycle with completion path |

Evaluation: enumerate the stable LTS; attach the shortest deadlock
record’s `witness` as `reachable_prefix`; run the wait-snapshot bridge
on that certified state. Closed-core vs LTS truth remains the FP/FN
columns.

**Done when** ≥4 `sip1_agree` rows and ≥4 `typed_refusal` rows, FP=0,
FN=0, all on one generator.

**CRP.** G-H2-CRP stays `open / omitted`. A Prop 6.4 four-field row
needs an independent S4PR embedding and must not reuse G4/G5 hashes.
That is a later optional H5, not this tranche.

## 3. P3 — H3-v2 multi-stage family

Tandem line: `n_jobs` distinguishable jobs visit `r0..r_{k-1}` of
capacity `c`, then complete.

Live serial probe (this session):

| jobs | stages | cap | `|X|` | time |
| --- | --- | --- | --- | --- |
| 4 | 3 | 1 | 304 | 0.04 s |
| 4 | 4 | 1 | 648 | 0.15 s |
| 5 | 4 | 1 | 2512 | 1.56 s |
| 6 | 3 | 1 | 3040 | 1.95 s |
| 6 | 4 | 1 | 8992 | 19.1 s |
| 6 | 5 | 1 | 24064 | 156 s |

Family: unit-capacity product `{4,5,6,7,8} × {3,4,5}` plus four
capacity-2 rows `(4,3,2)`, `(5,3,2)`, `(5,4,2)`, `(6,3,2)`. 19 rows.
Caps remain `1e5` states / 300 s. 32–48 workers, BLAS threads = 1.

**Done when** ≥8 enumerated rows have `|X|≥1e3` and ≥2 have `|X|≥1e4`,
or a declared-cap refusal curve is reported. The 496-state family is
not cited as “large”.

## 4. Roots

- cases: `cases/discovery/tase_hardening_v1/h2_v2/`, `.../h3_v2/`
- evidence: `evidence/tase_hardening/h2_v2/`, `.../h3_v2/`
- CLI: `tase_hardening_run.py --h2-v2` and `--h3-v2`
- frozen: `evidence/tase_hardening/v1|v2|v3/`

## 5. What this spec will not do

- Overwrite H2/H3 v1 reports
- Call H3-v2 a shop-floor plant
- Claim siphon control or S3PR equivalence
- Claim bit-polynomial reachability
- Push `main`
