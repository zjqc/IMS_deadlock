# T-ASE Hardening Spec Self-Review

Status: `AUTHOR SELF-REVIEW / NOT A SUBSTITUTE FOR INDEPENDENT THREE-LANE REVIEW`
Date: 2026-08-19
Revision: `compute-parallel-v2` — this review’s bytes replace
`52bf822d230377543bee0c91b449e9ced3353e844d0b3304c9a89574c2cfe3a0`.
Subjects:
- `docs/superpowers/specs/2026-08-19-tase-hardening-panel-design.md`
- `docs/superpowers/plans/2026-08-19-tase-hardening-panel.md`
- `docs/cases/TASE_HARDENING_PREREGISTRATION.md`

## Verdict

`PASS FOR APPROVAL GATE`, with the following explicit limits:

- This review is written by the same author as the spec. It can catch
  internal contradictions. It cannot count as the independent ontology /
  scientific-boundary / code-capability triad if the user wants that
  standard.
- No P0 contradiction with the audit or loop map was found.
- No authorization flag is true.
- No case JSON is created.
- The unapproved first-draft hashes are void.

## Checks

| Check | Result |
| --- | --- |
| Paper A centre remains typed local first-hit | yes |
| Article-core v1 immutable | yes |
| G6-B overlap not a prerequisite | yes |
| H1 maps to still-open CE/audit items | yes; CE-NB1 correctly reused |
| H2 same-semantics rule | yes; now 32 plants |
| H3 cannot prove a theorem | yes |
| H3/H4 sized for the 56-thread / 127 GiB box | yes |
| Parallelism cannot overlap primary and repro | yes |
| BLAS oversubscription banned | yes |
| GPU not claimed | yes; RTX PRO 2000 recorded unused |
| H4 not labelled plant data | yes |
| H5 default omitted | yes |
| New evidence root | `evidence/tase_hardening/v1/` plus shard dir |
| Tolerance not copied | yes; n=65536, t≈0.00724 |
| Implementation plan starts with T0 approval | yes |
| Science not in the same breath as case JSON | yes; T6 is a later authorization |

## Residual risks the user should accept before naming hashes

1. H3 576 × 100k-state rows can still take wall-hours even at 32 workers;
   refusals are part of the result.
2. H4 KPI set is still small; T-ASE Note to Practitioners still needs prose.
3. Independent three-lane review is still available if requested.
4. Live CPU/RAM must be re-probed; the Xeon/56/127 GiB snapshot is not a
   standing guarantee.

## Approval line to copy

After reading the three subject files:

```text
approved_spec_sha256=<sha256 of the spec file>
approved_plan_sha256=<sha256 of the plan file>
approved_review_sha256=<sha256 of this self-review, or of a later independent review>
```
