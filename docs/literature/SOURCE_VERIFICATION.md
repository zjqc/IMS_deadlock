# Source Verification Log

## Verification Standard

For theorem use, a source must have:

1. stable bibliographic identity;
2. full text or public version inspected;
3. theorem/proposition/equation/appendix locator precise enough to recheck;
4. explicit IMS migration boundary.

DOI metadata alone is insufficient. Broad section ranges and abstracts are
`FULLTEXT-CONTEXT`, not theorem anchors.

## Verified Theorem Anchors

These rows exactly match `FULLTEXT-THEOREM` in `LITERATURE_MATRIX.md`.

| ID | Source | Verification | Authorized use |
| --- | --- | --- | --- |
| L01 | Ezpeleta et al. 1995, https://doi.org/10.1109/70.370500 | Corollary V.2, Theorem VI.1, Section VI control policy. | S3PR liveness/siphon-control boundary only; no IMS generalization without a separate equivalence proof. |
| L06 | Ramadge and Wonham 1987, https://doi.org/10.1137/0325013 | Public full text inspected; Theorem 7.1 and Proposition 7.1 on pp. 218-219. | DES controllability / supremal controllable language / nonblocking benchmark. |
| L08 | Lawley and Reveliotis 2001, https://doi.org/10.1023/A:1012203214611 | Author PDF inspected; PDF p10 Theorem 1, p15 Proposition 2, pp18-24 capacitated-knot definition and RC1/SR1/SR2/CB1 conditions. | SU-RAS safety complexity and hard/easy subclass boundary only; no direct IMS complexity result. |
| L09 | Nazeem and Reveliotis 2011, https://doi.org/10.1109/TASE.2011.2159112 | Author `Nazeem-Rev-TASE.pdf` inspected; PDF p5 Proposition 1, Definition 1, and Section III boundary-unsafe-state construction. | D/C-RAS state-order monotonicity and exact LES implementation benchmark after an IMS finite-state encoding. |
| B04 | Chen et al. 2011, https://doi.org/10.1109/TASE.2010.2060332 | Author-uploaded technical report inspected; report p19 Theorem 6, with Assumptions 1-2 immediately before the theorem. The separate correction https://doi.org/10.1109/TASE.2012.2183739 is recorded because it corrects Section V-B. | Maximum-permissiveness benchmark only for bounded FMS Petri-net models satisfying the stated P-semiflow assumptions and only if such a monitor-expressible supervisor exists; not an IMS theorem. |
| L10 | Fei et al. 2015, https://doi.org/10.1109/TASE.2014.2369858 | Author/public version; Theorem IV.1. | Algorithm 2 correctness in the BDD/EFA framework. |
| L16 | Narahari, Viswanadham, and Krishna Prasad 1990, https://doi.org/10.1007/BF02811330 | Full 11-page article inspected; Section 3 (journal pp. 346-348) gives the finite transient/absorbing partition and `F=(I-T)^-1`; Section 3.1 gives mean time to deadlock; Section 3.2 gives `G=FC`; Section 4 (journal pp. 350-351) gives the transient time-to-deadlock distribution. | Historical absorbing-DTMC and embedded-chain metric anchor only. The IMS CTMC committor, sensitivity, and Doob-h formulas remain independently proved in P4 and sourced separately by L23/L28. |
| L17 | Palmer et al. 2018, https://doi.org/10.1016/j.ejor.2017.10.039 | CC BY full text; p3 Theorem 1, p3-p6 Theorem 2, p6-p7 counterexample. | Knot certificate, WCC shortcut restrictions, multi-server counterexample. |
| L18 | Wu and Zhou 2001, https://doi.org/10.1109/ROBOT.2001.932531 | Public version: https://www.academia.edu/144415118/Resource_oriented_Petri_nets_in_deadlock_avoidance_of_AGV_systems; Theorems 3.1, 3.2, 4.1, 5.1. | AGV circuit/cycle-chain deadlock-free conditions and associated control-law scope only. |
| L23 | Metzner, Schutte, and Vanden-Eijnden 2009, https://doi.org/10.1137/070699500 | Institutional public version: https://refubium.fu-berlin.de/bitstream/handle/fub188/6487/05_chapter4.pdf; Appendix subsection "Discrete Committor Equations", pp. 1216-1217. | Markov-jump-process TPT and discrete committor equations; not an absorbing IMS-deadlock theorem without adaptation. |
| L25 | Cerou and Guyader 2007, https://doi.org/10.1080/07362990601139628 | Author full text inspected; journal p422 (PDF p7) Hypothesis H and Theorem 1; journal p425 (PDF p10) Theorem 2. | Almost-sure consistency and asymptotic normality of the paper's one-dimensional adaptive splitting estimator; IMS transfer requires a valid score and the paper's Markov/continuity assumptions. |
| L28 | Corstanje and van der Meulen 2025, https://doi.org/10.1007/s11203-025-09326-9 | Public full text inspected; Section 3.1, Eq. 3.1, Eq. 3.3, Appendix D. | Doob-style change of measure and conditioned CT jump-process generator baseline. |
| L29 | Lu, Chen, Hadjicostis, and Li 2026, https://doi.org/10.1016/j.automatica.2025.112631 | Publisher full text inspected; Definition 3 constructs the modified resource requirement graph, Definition 4 defines safe operation places, Theorem 1 characterizes partial-deadlock markings by the PDDP, Algorithm 1 iteratively inserts control places, and Theorem 2 establishes liveness of the resulting controlled net. | Current strongest structural holder/request-graph and iterative control-place comparator. It does not establish an IMS operational bridge, a maximally permissive supervisor, or the probability/control interface. Polynomial ILP dimensions are not a polynomial-time guarantee. |

## Verified Context Sources

| ID | Source | Verification | Allowed use |
| --- | --- | --- | --- |
| L02 | Li and Zhou 2004, https://doi.org/10.1109/TSMCA.2003.820576 | Author PDF; Sections 3, 4, 5, 7. | Elementary-siphon definitions, controllability discussion, algorithms, FMS application context. |
| L04 | Liu et al. siphon survey, https://doi.org/10.1016/j.ins.2015.08.037 | Publisher full text inspected; Section 4, Theorem 2 (persistent siphon marking is sufficient for ordinary-net deadlock freedom), Theorem 3 (unmarked places at an ordinary dead marking form a siphon), and Theorems 4-7 (generalized/controlled-siphon and S3PR-family map). | Secondary theorem map and terminology only. The survey is not substituted for the original proofs, and none of these statements yields an IMS bridge without P2c. |
| L21 | Viswanadham, Johnson, Narahari 1990 conference text | Provenance-limited text. | `C4` three-resource AGV/machine blocking inspiration only. |
| L22 | Viswanadham, Narahari, and Johnson 1990, https://doi.org/10.1109/70.63257 | Full 11-page article inspected: Petri/GSPN preliminaries, GE-FMS model with blocked machines and finite buffers, a reachable deadlock, reachability-graph prevention, and online finite-look-ahead avoidance. No numbered theorem/proposition/lemma chain was found. | Historical manufacturing-model and controller baseline only; not a siphon theorem or an IMS equivalence source. |

## Metadata-only / Abstract Candidates

- L03: https://doi.org/10.1109/TSMCC.2011.2160626
- L05: https://doi.org/10.1016/0005-1098(95)00103-4
- L07: https://doi.org/10.1007/BF02551233
- L11: https://doi.org/10.1109/TAC.2013.2266952
- L12: https://doi.org/10.1137/120866427
- L13: https://doi.org/10.1016/j.ins.2015.11.025
- L14: https://doi.org/10.1007/BF01150855
- L15: https://doi.org/10.1016/0304-3975(94)90296-8
- L19: https://doi.org/10.1080/00207540110073037
- L20: https://doi.org/10.1049/itr2.12168
- L24: https://doi.org/10.1080/17442508.2022.2150081
- L26: https://doi.org/10.1023/A:1007937925728
- L30: https://doi.org/10.1177/01423312251369553
- L31: https://doi.org/10.1109/TASE.2026.3689269
- L32: https://doi.org/10.1109/TSMC.2024.3473851
- L33: https://doi.org/10.1109/TASE.2025.3588429
- L34: https://doi.org/10.1109/TSMC.2023.3241101
- L35: https://doi.org/10.1109/LRA.2023.3246384

## Closed-access Freshness Audit

- `L30`, `10.1177/01423312251369553`:
  - SAGE article and DOI metadata verified;
  - official abstract describes an equivalent finite-capacity S3PR net,
    minimum initial resource-place markings, and an ILP configuration method;
  - SAGE full text is restricted and OpenAlex reports no repository full text;
  - no theorem, equation, proof, or complexity locator is authorized.
- `L31`, `10.1109/TASE.2026.3689269`:
  - IEEE and institutional metadata verified; the University of Zielona Góra
    record's shorter DOI string is a typo and is not used;
  - official abstract describes CRP/linear-equation detection of reachable
    partial deadlocks without reachability-tree traversal;
  - no legal full text or accepted manuscript was located;
  - no theorem, equation, proof, or complexity locator is authorized.
- `L32`, `10.1109/TSMC.2024.3473851`:
  - IEEE document `10736656`, Crossref, and NJIT metadata verified;
  - official abstract describes a structure modification with at most one NIS,
    preserved modeled functionality, and polynomial-time reachability;
  - Crossref's IEEE staging PDF endpoint returned HTTP 418 and no legal
    institutional manuscript was located;
  - no theorem, equation, preservation, or complexity locator is authorized.
- `L33`, `10.1109/TASE.2025.3588429`:
  - IEEE document `11078878`, Crossref, and NJIT metadata verified;
  - official abstract gives the AMS-specific structure-modification claim;
  - Crossref's IEEE staging PDF endpoint returned HTTP 418 and no legal
    institutional manuscript was located;
  - no theorem, equation, preservation, or complexity locator is authorized.

The human-readable acquisition queue and required extraction fields are in
`FULLTEXT_REQUEST_LIST.md`. Downloaded PDFs remain outside Git.

## Corrections

| Error | Finding | Action |
| --- | --- | --- |
| Siphon survey DOI recorded as `10.1016/j.ins.2016.02.010`. | That DOI resolves to an unrelated l1-gain paper. | Marked `REJECTED/CORRECTED`; corrected candidate is `10.1016/j.ins.2015.08.037`. |
| IET 2022 paper described as generic AGV deadlock theorem. | Verified title is about Petri-net-based detection and recovery for interacting equipment in automated container terminals. | Keep as metadata/context only; do not generalize to IMS theorem. |
| Design guideline paper year recorded as 1999. | DOI metadata indicates 1997. | Corrected in matrix. |
| `10.1109/ROBOT.2001.932531` previously marked author-anomalous metadata only. | Public version was located with Theorems 3.1, 3.2, 4.1, and 5.1. | Upgraded to `FULLTEXT-THEOREM` with theorem-specific scope. |
| Viswanadham/Narahari/Johnson 1990 conference text and journal paper were conflated. | Journal DOI `10.1109/70.63257` resolves to "Deadlock prevention and deadlock avoidance in flexible manufacturing systems using Petri net models"; the conference text remains DOI-less and provenance-limited. | Split into L21 and L22. |
| Lawley/Reveliotis and Nazeem/Reveliotis were initially over-promoted. | They first had broad section/abstract locators rather than exact theorem/equation/page locators. A later author-PDF audit located Lawley/Reveliotis Theorem 1 and Proposition 2 and Nazeem/Reveliotis Proposition 1 and Definition 1. | Downgraded until exact extraction, then re-upgraded with the narrower theorem-specific scope recorded above. |

## Open Gates

1. L04 is closed as a full-text secondary theorem map, not an original proof
   source. P2c must still prove the IMS-SIP1 bridge independently.
2. L16 is closed for its historical absorbing-DTMC/embedded-chain equations.
   It does not source the project's CTMC sensitivity or Doob-h theorem.
3. L22 is closed as full-text historical context. B05 remains closed-access
   and theorem-level use is blocked; B04 supplies the theorem-located
   Petri-net maximum-permissiveness benchmark, with its P-semiflow assumptions,
   monitor-existence proviso, and published correction.
4. L28 supplies the conditioned CT jump-process generator baseline, so
   the primary Doob-h source is fixed for the first paper. L23 remains TPT for
   ergodic Markov jump processes rather than an IMS absorption theorem, and
   absorbing IMS boundary adaptation is still a separate proof obligation.
5. L25 now supplies consistency and asymptotic-normality locators for one
   adaptive splitting construction, but an IMS-specific reaction coordinate,
   finite-sample protocol, and assumption check remain open before deployment.
6. L29 must be an explicit algorithm/control comparator. L30's finite-capacity
   S3PR minimum-resource configuration, L31's claimed reachable
   partial-deadlock detection without reachability-tree traversal, and
   L32-L33's reachability-decidable structure-modification claims are the
   highest-priority freshness threats. All remain abstract-level here and
   cannot be used as theorem sources until their full proofs and subclasses are
   audited. The exact manual acquisition list is
   `FULLTEXT_REQUEST_LIST.md`.
