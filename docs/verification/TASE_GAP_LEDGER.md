# T-ASE Gap Ledger

Status: `LIVING PROCESS LEDGER`
Updated: 2026-08-19
Programme: `docs/superpowers/specs/2026-08-19-tase-submission-programme.md`

| Gap | Phase | State | Evidence | Next action |
| --- | --- | --- | --- | --- |
| G-CLAIM | P0 | **closed** | `TASE_CLAIM_LADDER.md` | keep frozen unless a phase forces a new id |
| G-H1 | P0 | **closed** | H1 four witnesses in tase v1 report | do not rerun |
| G-H4-HOLD | P1 precursor | **closed as v2** | v1 refusal retained; v2 certified \(\theta_b=0\) | do not overwrite |
| G-H4-DEADLOCK | P1 | **closed in v3** | base \(\theta_b=1\) (`D_local`), intervention \(\theta_b=0\), 6/6 compatible | keep v3; do not overwrite |
| G-H2-SIPHON+ | P2 | **closed in h2_v2** | 4 SIP1 agrees, 4 typed refusals, FP=0 FN=0; v1 32/32 refusals retained | do not overwrite |
| G-H2-CRP | P2 leftover | **closed as diagnostic** | H5 four-field scorer; fields 1–3 can hold; field 4 refused (`no_independent_s4pr_embedding`); G5 remains the negative witness | do not claim CRP theorem |
| G-H3-SCALE | P3 | **closed in h3_v2** | 16/19 enumerated; 12 rows \(\ge 10^3\), 4 rows \(\ge 10^4\); 3 typed cap/time refusals; max 100000 | do not cite 496-state H3 v1 as large |
| G-NOVELTY-LOC | P4 | **closed as locators** | `NOVELTY_DIFFERENCE_MATRIX.md` G1 locator table | cite only those rows |
| G-NTP | P5 | **draft prose in process file** | `TASE_NOTE_TO_PRACTITIONERS_OUTLINE.md` ≈220 words | IEEE paste only when body starts |
| G-IEEE-BODY | P5 | **draft on worktree** | `docs/paper/TASE_LOCAL_FIRST_HIT_MANUSCRIPT.md` | IEEE two-column conversion later; claims frozen to this file |

Closed gaps stay closed. Reopening requires a new version id.
G5 FAIL and G6-B `OPEN_PENDING` are retained.
