# T-ASE Submission Readiness v2

Status: `VERDICT / NOT A MANUSCRIPT`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
HEAD: `e311a79406c57e6f1e2232a4b6c2c3b37f71b8d7`
Venue: IEEE Transactions on Automation Science and Engineering only

This is a re-evaluation after P0–P4, H5, and the NtP process draft.
It does not upgrade G6-B, does not supersede G5 FAIL, and does not
authorize IEEE-template production by itself.

## 1. One-line verdict

A **scoped T-ASE Regular Paper draft may start now**. The package is
**not submission-ready**. The theory–case loop is self-consistent for
TA1–TA10 if TX1–TX12 stay forbidden. The publishable increment is
narrower than a 2026 Petri/CRP “first detector” paper, and that
narrowness is the only honest novelty.

## 2. What is closed (live evidence)

| Block | Fact |
| --- | --- |
| Theory centre | Theorem 1 (A2b) and Prop. 2 (complete-LTS fallback) remain the Paper A theorems; audit found no P0 unsoundness |
| H1 | four logical witnesses (CL1, BIXD2, INT1, P3 non-chain refuse) |
| H4-v3 | Barrier A certified; base \(\theta_l=1,\theta_b=1\), mean time 0; drain \(\theta_b=0\), mean time \(\approx 3.23\); 6/6 exact–DES compatible |
| H2-v2 | 10 plants; 4 SIP1 agrees; 4 typed refusals; FP=0 FN=0 |
| H3-v2 | 16/19 enumerated; 12 rows \(\ge 10^3\); 4 rows \(\ge 10^4\); 3 typed cap/time refusals |
| H5 | Prop 6.4 scorer; fields 1–3 can hold (4/6); field 4 refused; agreement 0 |
| Locators | L29/L30/L31/B05 (and L01/L08/L16/L17) attached |
| NtP | ~220-word process draft, not IEEE body |

Frozen negatives retained: G5 FAIL; G6-B `OPEN_PENDING`; H4 v1
`completed_job_holds_resource`; H4 v2 \(\theta_b=0\).

## 3. Remaining gap vs a T-ASE *submission*

| Gap | Kind | Blocks draft? | Blocks submit? |
| --- | --- | --- | --- |
| IEEE body, figures, template, title/abstract metadata | packaging | no | **yes** |
| H4-v3 is a 3-job synthetic island already in `D_local` at \(t=0\) | scientific limitation | no, if labelled | maybe (AE “toy / already stopped”) |
| No published S3PR/S4PR benchmark replay | comparator | no | maybe (T-ASE 2026 CRP paper L31 sits next door) |
| H5 field 4 has no S4PR embedding | correctly open | no | no, if not claimed |
| G6-B eight-dimension overlap | out of Paper A | no | no, if TX1 held |
| Shop-floor / throughput | forbidden | no | no, if TX12 held |
| General IMS ≡ S3PR; CRP theorem; polynomial reachability | correctly open | no | **desk-reject if claimed** |
| Rendered Figs F1–F7 | packaging | no | **yes** |

T-ASE itself asks for foundational automation methods that a
practitioner can read (Note to Practitioners is mandatory). The science
fits that charter **only** as operational IMS local-blocking analysis,
not as a new plant-net liveness theorem.

## 4. Innovation (what a 2026 referee will compare)

Closest full-text comparators already in G1:

- L29 Automatica 2026: MR2G / PDDP iff partial-deadlock marking
- L31 T-ASE 2026: CRP iff partial deadlock, then SBA
- B05 Automatica 2011: maximally permissive monitors via MCPP
- L08 / L17: SU-RAS NP-c and knot screens

The only increment that is both new **and** checkable:

```text
local blocking is a verified stopped-process first-hit set,
admitted by A2b or by complete-LTS nonreachability,
refused when a completion bypass exists,
and wired to exact/DES only after the absorption domain is certified.
```

That is enough for a T-ASE Regular Paper *attempt*. It is not enough
to write “first reachable certificate”, “siphon-free detector”, or
“we outperform CRP”. If the introduction sells those, the paper is
logically inconsistent with L29/L31/B05 and with H5 agreement = 0.

## 5. Logical self-consistency

Hold, if every sentence maps to TA1–TA10 and every limitation maps to
an open row:

- A2b is sufficient, not necessary (TX3).
- Complete-LTS admission is model-specific and exponential (TX4).
- A local core is not automatically `D_local` (TX5); bypass refuses it.
- `D_local` is not a plant terminal SCC (TX6); H4-v3 base still has
  plant motion on job C while A,B are locally stopped.
- P2 / certificates are relative to the declared transition registry.
- `IMS-SIP^1` is a wait-snapshot dual, not plant S3PR.
- Exact/DES 6/6 is a numerical check, not a proof (TX7).
- H4-v3 base \(\mathbb{E}[T]=0\) because the initial state *is* the
  local hit. The intervention changes the *class*, not a long transient
  risk path. Write that sentence; do not hide it.
- Article-core six cases are constructive, not held-out (TX2).

Break, if the manuscript mixes Paper B (covering-core / P3 thresholds)
or Paper C (risk-budget supervisor) into the T-ASE main claims.

## 6. May writing start?

**Yes, start a scoped draft on this worktree**, with these rules:

1. Centre: typed local first-hit (TA1–TA4, TA6).
2. Clothing: H4-v3 island + H2-v2 table + H3-v2 scale curve.
3. Related work: locator table, especially L31 as a T-ASE neighbour.
4. Limitations: G5 FAIL, G6-B open, H5 field 4, H4-v3 \(t=0\) hit,
   synthetic digital-twin, no shop floor.
5. Do not wait for another science family. Another island or an S4PR
   embedding would be a *new* version, not a prerequisite to typing
   Section 1.
6. Do not paste NtP into IEEE format until the body outline exists;
   the 220-word process draft is the source, not the submission file.

**Do not submit** until IEEE body, rendered figures, and a
self-contained limitation section exist, and a co-author/read-through
has hunted TX1–TX12.

## 7. Recommended manuscript skeleton (still not body copy)

1. Introduction + NtP (local first-hit; AGV drain KPI)
2. Related work (L29/L31/B05/L08; five-axis matrix)
3. IMS-RAS and certificates (registry-relative)
4. Typed admission: A2b vs complete LTS; bypass refusal
5. Stopped-process first-hit; Barrier A; exact/DES
6. Cases: H4-v3, H2-v2, H3-v2; H1 as boundaries; H5 as diagnostic
7. Limitations and what is not claimed
8. Conclusion: checkable object, not a factory controller
