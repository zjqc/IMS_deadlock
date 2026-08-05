# Article Claim–Evidence Matrix

Status: `FROZEN AGAINST MINIMAL ARTICLE CLOSURE V1`

Scope lock self SHA-256:
`86ec7b80c888c7758d326a9de7793b0f0f65f4740ecf0303e1b17d2d14344660`

Evidence manifest self SHA-256:
`1693342ac470b72f9b813edccb772f85751045940a243f7abc9241877cab0c77`

## Supported scoped claims

| ID | Manuscript claim | Formal basis | Case/evidence basis | Status | Boundary |
| --- | --- | --- | --- | --- | --- |
| C1 | `D_local` is a verified stopped-process bad hit set and need not be a plant terminal SCC. | Objective target definition plus plant/stopped graph separation in Sections 2.2–2.3. | `g6b_cu_pc_dlocal_lts_multi_kernel_v1`; certificate reports 6 plant arcs and 4 stopped arcs. | supported | Does not say every local candidate is irreversible. |
| C2 | Under A0–A7 and A2b request closure, a local closed blocking kernel makes all-batch completion unreachable. | Theorem 1 and its invariant proof. | `g6b_cu_pc_dlocal_a2b_single_kernel_v1`; A2b proof flag and time-zero `D_local` classification. | supported within assumptions | A2b is sufficient, not necessary; no claim outside request-closed semantics. |
| C3 | A complete finite-LTS completion-nonreachability audit is a sound fallback for the concrete enumerated model. | Proposition 2. | `g6b_cu_pc_dlocal_lts_multi_kernel_v1`; both admitted states have no path to `F`. | supported for the finite case | No structural generalization beyond the enumerated LTS. |
| C4 | A current local candidate must be refused when a completion bypass exists. | Contrapositive boundary of the admission rule. | `g6b_cu_nc_local_bypass_completes_v1`; path `candidate -> bypass -> F`, selected-bad probability zero. | supported | One counterexample establishes insufficiency, not prevalence. |
| C5 | A state satisfying the global predicate is counted only in `D_global`, even if local-candidate structure is present. | Pairwise disjoint partition and global-before-local precedence. | `g6b_cu_nc_dglobal_only_with_dlocal_v1`; exact/DES `(1,0,1)`. | supported | Classification convention for this versioned estimand only. |
| C6 | The bridge selected-bad probability is analytically `1/3`. | Competing exponential rates `1` and `2`. | `g6b_article_bridge_competing_local_completion_v1`; exact result records analytical identity `1/3`. | supported | Minimal two-exit case, not a production facility model. |
| C7 | Exact and DES agree on the same three-class first-hit target within the frozen tolerance. | Exact committor equations, frozen Gillespie stopping rule, and simultaneous Hoeffding threshold. | 18/18 cells compatible; maximum error `0.0030924479166667 < 0.028340`; `article_closure_report.json`. | supported | Within-case semantic cross-check only; no external validation or retired-study independence. |
| C8 | Both A2b and complete-LTS routes have matched constructive closure with the required boundary controls. | Frozen claim ladder. | `claim_tier=tier_a_dual_route_closure`; all six retained cases and four evidence artifacts. | supported as scoped Tier A | Does not imply original G6-B PASS. |
| C9 | Different methods may cover different cases without logical inconsistency when assumptions and refusals are explicit. | Typed method boundary in Section 3.4. | A2b positive, LTS positive, and bypass negative control are all retained rather than forced under one rule. | supported as article logic | Method superiority and universal coverage are not evaluated. |

## Evidence objects

| Evidence code | Repository artifact | Raw SHA-256 | Role |
| --- | --- | --- | --- |
| E1 | `cases/article_core/article_scope_lock_v1.json` | `7bde6a5f8f06afc42aa28c7338fe2aa79fb83237a1151415dd8c2197910ce900` | pre-outcome roster, claim ladder, seed, sample size, tolerance, forbidden claims |
| E2 | `evidence/article_core/minimal_closure_v1/article_case_certificates.json` | `7ddbc11f296c396c6df04b4647cc01f0020869c35ed8d4f2aee6a6f8cde0446b` | theory obligations and plant/stopped graph counts |
| E3 | `evidence/article_core/minimal_closure_v1/exact_results.json` | `e9b9758d43df85847dccaae0676d4e976221d1829da959e73a9fe0794b9b5f3a` | exact component committors and mean stopped times |
| E4 | `evidence/article_core/minimal_closure_v1/des_results.json` | `c20cdfd60219fc66d7838b42532228acabc3361ef1f5e59f178340cf7c48ea3b` | 4096-replication counts, probabilities, times, and seed manifest for each case |
| E5 | `evidence/article_core/minimal_closure_v1/article_closure_report.json` | `135c939bad1f2e335147f887fccdb9493db59210b16ae1ecb8f7953fefddd037` | 18 cell errors, compatibility decisions, and mechanical tier |
| E6 | `evidence/article_core/minimal_closure_v1/article_closure_manifest.json` | `d8b409d6bfb766ab6b992c187afd849e4e67d77cbb34751ffd418574c7b5a98c` | write-last identity binding E2–E5 |
| E7 | `docs/verification/G6_B_MINIMAL_ARTICLE_CLOSURE_REPORT.md` | assigned by Git commit | human-readable target, protocol, result, and limitation audit |

## Unsupported or forbidden stronger claims

| Code | Stronger claim | Decision | Why |
| --- | --- | --- | --- |
| F1 | The original G6-B eight-dimension gate passed. | forbidden | Original gate remains `OPEN_PENDING`; the article scope is a versioned successor, not a relabelling. |
| F2 | The six cases are held-out confirmation. | forbidden | Five cases come from sealed discovery/boundary construction; the bridge is preregistered constructive evidence. |
| F3 | A2b is necessary or complete for local deadlock. | forbidden | Only sufficiency under request-closed assumptions is proved. |
| F4 | Complete-LTS admission generalizes to unenumerated or infinite models. | forbidden | The audit proves reachability only in the concrete complete finite LTS. |
| F5 | Every local blocking core is `D_local`. | forbidden | The completion-bypass control is an explicit counterexample. |
| F6 | `D_local` is a plant terminal SCC. | forbidden | The multi-kernel positive retains plant outgoing arcs after the bad hit. |
| F7 | Exact/DES agreement proves the theorem or plant fidelity. | forbidden | It checks same-target quantitative implementation only. |
| F8 | New random streams or metric schemas are independent of retired studies. | forbidden | Retired normalization has no eligible projection for those two dimensions. |
| F9 | The method improves throughput, tardiness, WIP, recovery, or controller performance. | unsupported | None of these estimands is implemented in the article scope. |
| F10 | One method covers all 13 sealed cases or all IMS-RAS semantics. | forbidden | The article explicitly uses method-specific assumptions and retains eight noncore cases outside its minimal denominator. |
| F11 | G5 failures or G6-R failures are superseded. | forbidden | G5 `4/3/2`, transparent `6/1/2`, both minimality failures, R1/R2 failures, and historical-only R3 remain evidence. |
| F12 | The manuscript is publication-ready solely because Tier A passed. | forbidden | External bibliography, venue formatting, broader positioning, and independent scientific review remain editorial/future work. |

## Mechanical manuscript rule

Every declarative result sentence in
`docs/paper/IMS_LOCAL_FIRST_HIT_THEORY_AND_CASES.md` must map to C1–C9 or be
stated explicitly as an assumption, definition, limitation, or future-work
item. Any sentence requiring F1–F12 must be removed or weakened before release.
