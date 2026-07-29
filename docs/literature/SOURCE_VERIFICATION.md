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
| L10 | Fei et al. 2015, https://doi.org/10.1109/TASE.2014.2369858 | Author/public version; Theorem IV.1. | Algorithm 2 correctness in the BDD/EFA framework. |
| L17 | Palmer et al. 2018, https://doi.org/10.1016/j.ejor.2017.10.039 | CC BY full text; p3 Theorem 1, p3-p6 Theorem 2, p6-p7 counterexample. | Knot certificate, WCC shortcut restrictions, multi-server counterexample. |
| L18 | Wu and Zhou 2001, https://doi.org/10.1109/ROBOT.2001.932531 | Public version: https://www.academia.edu/144415118/Resource_oriented_Petri_nets_in_deadlock_avoidance_of_AGV_systems; Theorems 3.1, 3.2, 4.1, 5.1. | AGV circuit/cycle-chain deadlock-free conditions and associated control-law scope only. |
| L23 | Metzner, Schutte, and Vanden-Eijnden 2009, https://doi.org/10.1137/070699500 | Institutional public version: https://refubium.fu-berlin.de/bitstream/handle/fub188/6487/05_chapter4.pdf; Appendix subsection "Discrete Committor Equations", pp. 1216-1217. | Markov-jump-process TPT and discrete committor equations; not an absorbing IMS-deadlock theorem without adaptation. |
| L28 | Corstanje and van der Meulen 2025, https://doi.org/10.1007/s11203-025-09326-9 | Public full text inspected; Section 3.1, Eq. 3.1, Eq. 3.3, Appendix D. | Doob-style change of measure and conditioned CT jump-process generator baseline. |

## Verified Context Sources

| ID | Source | Verification | Allowed use |
| --- | --- | --- | --- |
| L02 | Li and Zhou 2004, https://doi.org/10.1109/TSMCA.2003.820576 | Author PDF; Sections 3, 4, 5, 7. | Elementary-siphon definitions, controllability discussion, algorithms, FMS application context. |
| L04 | Liu et al. siphon survey, https://doi.org/10.1016/j.ins.2015.08.037 | Full-text/theorem-number clues exist, but stable locator is not recorded here. | Siphon-review map only until locator extraction. |
| L08 | Lawley and Reveliotis 2001, https://doi.org/10.1023/A:1012203214611 | Author PDF; broad Sections 3, 4, 5 only. | SU-RAS safety and hard/easy class context; no theorem claim from this row. |
| L09 | Nazeem and Reveliotis 2011, https://doi.org/10.1109/TASE.2011.2159112 | Author `Nazeem-Rev-TASE.pdf`; abstract and broad Sections II-III only. | Offline/online LES framework context; no theorem claim from this row. |
| L21 | Viswanadham, Johnson, Narahari 1990 conference text | Provenance-limited text. | `C4` three-resource AGV/machine blocking inspiration only. |
| L25 | Cerou and Guyader 2007, https://doi.org/10.1080/07362990601139628 | Source identified, theorem migration not recorded. | Rare-event estimation context/backlog. |

## Metadata-only / Abstract Candidates

- L03: https://doi.org/10.1109/TSMCC.2011.2160626
- L05: https://doi.org/10.1016/0005-1098(95)00103-4
- L07: https://doi.org/10.1007/BF02551233
- L11: https://doi.org/10.1109/TAC.2013.2266952
- L12: https://doi.org/10.1137/120866427
- L13: https://doi.org/10.1016/j.ins.2015.11.025
- L14: https://doi.org/10.1007/BF01150855
- L15: https://doi.org/10.1016/0304-3975(94)90296-8
- L16: https://doi.org/10.1007/BF02811330
- L19: https://doi.org/10.1080/00207540110073037
- L20: https://doi.org/10.1049/itr2.12168
- L22: https://doi.org/10.1109/70.63257
- L24: https://doi.org/10.1080/17442508.2022.2150081
- L26: https://doi.org/10.1023/A:1007937925728

## Corrections

| Error | Finding | Action |
| --- | --- | --- |
| Siphon survey DOI recorded as `10.1016/j.ins.2016.02.010`. | That DOI resolves to an unrelated l1-gain paper. | Marked `REJECTED/CORRECTED`; corrected candidate is `10.1016/j.ins.2015.08.037`. |
| IET 2022 paper described as generic AGV deadlock theorem. | Verified title is about Petri-net-based detection and recovery for interacting equipment in automated container terminals. | Keep as metadata/context only; do not generalize to IMS theorem. |
| Design guideline paper year recorded as 1999. | DOI metadata indicates 1997. | Corrected in matrix. |
| `10.1109/ROBOT.2001.932531` previously marked author-anomalous metadata only. | Public version was located with Theorems 3.1, 3.2, 4.1, and 5.1. | Upgraded to `FULLTEXT-THEOREM` with theorem-specific scope. |
| Viswanadham/Narahari/Johnson 1990 conference text and journal paper were conflated. | Journal DOI `10.1109/70.63257` resolves to "Deadlock prevention and deadlock avoidance in flexible manufacturing systems using Petri net models"; the conference text remains DOI-less and provenance-limited. | Split into L21 and L22. |
| Lawley/Reveliotis and Nazeem/Reveliotis were over-promoted. | They had broad section/abstract locators rather than exact theorem/equation/page locators. | Downgraded L08 and L09 to `FULLTEXT-CONTEXT`. |

## Open Gates

1. Extract stable theorem/page locators for L04 before using its siphon
   theorem claims.
2. Extract theorem/equation locators for L16 before using absorbing Markov
   equations; currently it is abstract-only in this library.
3. Extract exact locators for L08 and L09 before using SU-RAS safety or LES
   framework as theorem support.
4. Full-read L22, B04, and B05 before comparing Petri-net maximum
   permissiveness.
5. L28 now supplies the conditioned CT jump-process generator baseline, so
   the primary Doob-h source is fixed for the first paper. L23 remains TPT for
   ergodic Markov jump processes rather than an IMS absorption theorem, and
   absorbing IMS boundary adaptation is still a separate proof obligation.
