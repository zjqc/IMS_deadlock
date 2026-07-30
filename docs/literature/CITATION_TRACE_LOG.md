# Citation Trace Log

## Scope

This log records the bounded citation tracking begun on 2026-07-29 and the
current-work freshness audit on 2026-07-30. It is not a systematic review and
not a proof source. The goal is to test whether new in-scope model classes,
theorem families, complexity boundaries, or counterexample categories keep
appearing.

Conclusion:

> R2/R3 reached historical scope-bounded saturation. Round 4 reopened the
> search, Round 6 found the reachability-decidable structure-modification
> category, and Rounds 7-8 then completed two consecutive bounded rounds
> without another new first-paper category.

The taxonomy stop rule is satisfied again as a bounded OpenAlex result. The
later user-supplied full-text audit closes the current theorem-locator gate as
`PASS (scope-bounded)`, while leaving priority unproved.

## Method Limits

- Database: OpenAlex.
- Sorting: `cited_by_count:desc`, which favors visible, older, highly cited
  records and can miss recent or niche work.
- Screening: title/abstract/metadata first, with follow-up only for candidate
  category changes.
- Coverage: OpenAlex reference lists and citation edges can be incomplete.
- Exclusions: unreliable-resource, partial-observation, continuous/hybrid timed
  PN, collision scheduling, and generic vehicle-routing branches were logged as
  outside the first-paper scope unless they changed IMS-RAS deadlock theory.

## Round 1

- Date: 2026-07-29.
- Database: OpenAlex.
- Seeds and OpenAlex IDs:
  - `10.1109/70.370500` -> `W2140872435`
  - `10.1137/0325013` -> `W1979349468`
  - `10.1023/A:1012203214611` -> `W1483186571`
  - `10.1016/j.ejor.2017.10.039` -> `W2767453465`
  - `10.1109/ROBOT.2001.932531` -> `W2133158797`
  - `10.1137/070699500` -> `W2055484248`
- Forward filter: `filter=cites:<id>&sort=cited_by_count:desc&per-page=10`.
- Backward screen: up to first 50 referenced IDs, sorted by cited count, with
  `per-page=10`.
- In-scope new categories / boundaries:
  - multiple acquisition and flexible routing: `10.1109/9.956052`;
  - multi-AGV deadlock/liveness control: `10.1109/TSMCB.2005.850141`;
  - multi-vehicle maximal-permissive complexity: `10.1109/TAC.2010.2046111`;
  - classical FMS Petri-net prevention/avoidance: `10.1109/70.63257`;
  - siphon plus mathematical programming: `10.1109/70.650158`;
  - intersection deadlock probability: `10.1049/itr2.12210`.
- Out-of-scope branches:
  - unreliable-resource and outage robustness for first paper;
  - partial observation/diagnosis variants.
- Reseed reason: new in-scope taxonomy categories appeared.

## Round 2

- Date: 2026-07-29.
- Database: OpenAlex.
- Anchors:
  - six new Round 1 items above;
  - `10.1109/TASE.2006.884674`;
  - `10.1109/TAC.2008.929375`.
- Forward filter: `filter=cites:<id>&sort=cited_by_count:desc&per-page=8`.
- Backward screen: referenced IDs sorted by cited count, `per-page=8`.
- In-scope result:
  - repeated taxonomy: siphon control, maximally permissive supervision,
    multi-AGV deadlock/liveness, and traffic/intersection deadlock.
- Out-of-scope categories:
  - continuous/hybrid timed Petri nets;
  - collision scheduling and generic vehicle routing.
- Stop/reseed reason: no new in-scope model/theorem/counterexample category,
  but one more bounded round was required to test saturation.

## Round 3

- Date: 2026-07-29.
- Database: OpenAlex.
- Anchors:
  - `10.1109/TAC.2014.2381453`;
  - `10.1109/TASE.2018.2798630`;
  - `10.1109/TSMC.2022.3232743`;
  - `10.1109/TASE.2010.2060332`;
  - `10.1109/TSMCA.2008.2007947`.
- Forward/backward bound: `per-page=5`.
- In-scope result:
  - repeated categories: vehicle routing/scheduling, PN supervisory control,
    maximally permissive control, complexity, and multi-AGV traffic.
- Out-of-scope categories:
  - continuous/hybrid timed Petri nets;
  - collision-free scheduling and path planning without IMS-RAS blocking
    certificate implications.
- Stop reason:
  - second consecutive bounded round without a new in-scope
    model/theorem/counterexample category.

## Use in G1 Gate

The taxonomy screen supports continuing to G2 formalization with the current
six-chain map. It does not close the full-text verification gate. Sources may
enter theorem statements only through `SOURCE_VERIFICATION.md` and
`LITERATURE_MATRIX.md` as `FULLTEXT-THEOREM` rows with exact locators.

## Targeted Full-Text Locator Audit

- Date: 2026-07-29.
- Temporary research copies only; PDFs were not added to the repository.
- `L08`, Lawley and Reveliotis (2001):
  - author PDF visually inspected;
  - PDF p10: Theorem 1, `SU-SAFE is NP-complete`;
  - PDF p15: Proposition 2, intractable SU-RAS subclasses contain
    deadlock-free unsafe states;
  - PDF pp18-24: capacitated-knot definition and RC1/SR1/SR2/CB1
    hard/easy-boundary conditions.
- `L09`, Nazeem and Reveliotis (2011):
  - Georgia Tech author PDF visually inspected;
  - PDF p5: Proposition 1 and Definition 1 on componentwise safe/unsafe
    monotonicity and maximal-safe/minimal-unsafe states;
  - Section III: boundary reachable unsafe states as the implementation
    interface for the maximally permissive LES.
- `L25`, Cerou and Guyader (2007):
  - author full text visually inspected;
  - journal p422 / PDF p7: Hypothesis H and Theorem 1 on almost-sure
    consistency;
  - journal p425 / PDF p10: Theorem 2 on asymptotic normality and variance.
- `L16`, Narahari et al. (1990):
  - full 11-page article inspected;
  - Section 3 / journal pp. 346-348: finite transient/absorbing partition and
    `F=(I-T)^-1`;
  - Section 3.1: mean time to deadlock;
  - Section 3.2: `G=FC` absorption probabilities;
  - Section 4 / journal pp. 350-351: transient time-to-deadlock distribution;
  - upgraded only for this historical DTMC/embedded-chain scope, not for the
    project's CTMC sensitivity or Doob-h theorem.
- `B04`, Chen et al. (2011):
  - author-uploaded technical-report text inspected;
  - report p19: Assumptions 1-2 and Theorem 6, with the explicit proviso
    "if such a supervisor exists";
  - the 2012 correction to Section V-B is recorded and blocks verbatim reuse
    of that implementation paragraph until the correction text is checked.

## Targeted Full-Text Locator Audit, Round 2

- Date: 2026-07-30.
- `L04`, Liu et al. siphon survey:
  - publisher full text inspected;
  - Section 4, Theorems 2-3 locate the ordinary-net deadlock/siphon facts;
  - Theorems 4-7 map generalized/controlled-siphon and S3PR-family results;
  - retained as `FULLTEXT-CONTEXT` because it is a secondary survey, not the
    original proof source.
- `L22`, Viswanadham, Narahari, and Johnson (1990):
  - full 11-page journal article inspected;
  - Petri/GSPN definitions, GE-FMS blocked-machine/buffer model, reachable
    deadlock, reachability-based prevention, and finite-look-ahead avoidance
    were located;
  - retained as `FULLTEXT-CONTEXT` because the methods paper has no numbered
    theorem/proposition/lemma chain for migration.
- `B05`, Chen and Li (2011):
  - DOI and publisher metadata were stable at this stage;
  - no auditable full theorem text had been recovered in Round 2;
  - this was later superseded by the supplied full-text audit recorded below.

These audits close the targeted L04/L16/L22 locator questions with
scope-specific classifications. No source's complexity, liveness, or
convergence result transfers to IMS without the assumption mapping in
`MIGRATION_CARDS.md`.

## Round 4: Current-work Freshness Audit

- Date: 2026-07-30.
- Search objective: challenge the proposed reachability-certificate,
  finite-capacity-threshold, and structural-control novelty against work
  published or indexed after the original anchor set.
- Current in-scope comparators:
  - `L29`, Lu, Chen, Hadjicostis, and Li (2026), was read in publisher full
    text. Its modified resource-requirement graph, PDDP characterization,
    iterative control-place insertion, and controlled-net liveness theorem
    make it the mandatory structural/control baseline.
  - `L30`, Pang et al. (2025), officially describes minimum resource
    configuration for an equivalent finite-capacity S3PR net. At this stage it
    remained abstract-only; this was later superseded by the supplied full-text
    audit below.
  - `L31`, Su et al. (2026), officially describes critical
    resource-limit-pair linear equations for detecting reachable partial
    deadlocks without a reachability tree. At this stage it remained
    abstract-only; this was later superseded by the supplied full-text audit
    below.
- New category found:
  - `L31` adds a direct reachable-partial-deadlock/no-reachability-tree claim,
    which is materially closer to the proposed structural certificate than
    the categories recorded in Rounds 1-3.
- Consequence:
  - the previous two-round taxonomy saturation is historical evidence, not a
    current stop certificate;
  - freshness tracking is reopened and must be reseeded from `L29-L31`;
  - at least two consecutive bounded rounds after this reseed must find no new
    in-scope model, theorem, or counterexample category before the taxonomy
    stop rule is satisfied again;
  - no manuscript may claim the first reachable structural certificate,
    the first reachability-free partial-deadlock detector, or general
    finite-capacity threshold novelty. The later full-text audit narrows these
    bans but does not remove them.

## Round 5: L29-L31 Reseed

- Date: 2026-07-30.
- Seeds:
  - `L29`, OpenAlex `W4414887684`: 28 indexed references, no indexed forward
    citation at query time;
  - `L30`, OpenAlex `W4414375876`: 41 indexed references and one indexed
    forward citation;
  - `L31`, OpenAlex `W7160189276`: no indexed reference edges at query time.
    Crossref supplied 47 reference records, 46 with DOI; all 46 DOI records
    resolved to OpenAlex works.
- Bound:
  - backward and forward records sorted by `cited_by_count:desc`;
  - top eight per direction where available;
  - Crossref DOI references substituted only for L31's missing OpenAlex
    backward edges.
- In-scope result:
  - repeated finite-capacity S3PR initial-marking/resource-configuration,
    siphon control, FMS/RAS supervision, and holder/request-graph categories;
  - `10.1109/TSMC.2023.3241101` and
    `10.1109/LRA.2023.3246384` exposed the state-equation-to-legal-firing-
    sequence gap. This is recorded as a proof-mechanism and false-positive
    boundary inside the reopened reachable-partial-deadlock category, not as
    another top-level IMS model category.
- Forward result:
  - L30's sole indexed forward record,
    `10.1109/ICATEI67676.2025.11405088`, stayed in S4PR/controller-deadlock
    design and did not add a new first-paper category.
- Reseed reason:
  - no new top-level category in this round, but one more layer of current
    legal-firing-sequence citations was required.

## Round 6: Legal-Firing-Sequence and Capacity Lineage

- Date: 2026-07-30.
- Anchors:
  - `10.1080/00207543.2011.560204`;
  - `10.1093/imamci/dnv016`;
  - `10.1016/j.ins.2024.121623`;
  - `10.1016/j.automatica.2024.111625`;
  - `10.1109/TSMC.2025.3548655`;
  - `10.1109/TSMC.2023.3241101`;
  - `10.1109/LRA.2023.3246384`;
  - `10.1109/TASE.2021.3138169`.
- Bound: top eight forward records and top eight of the first 50 indexed
  backward references for each anchor, sorted by cited count.
- Screened set: 85 unique OpenAlex works after deduplication.
- New in-scope category:
  - `L32`, `10.1109/TSMC.2024.3473851`, officially claims a
    functionality-preserving Petri-net structure modification with no more
    than one state-equation NIS and polynomial-time reachability;
  - `L33`, `10.1109/TASE.2025.3588429`, presents an AMS-specific
    structure-modification/reachability-analysis method with the same
    high-level objective.
- Repeated in-scope categories:
  - reduced/step reachability graphs, S3PR/S4PR supervision, flexible
    acquisition/assembly, siphon/GMEC control, and minimum initial marking.
- Excluded first-paper branches:
  - unreliable resources and unobservable events;
  - partial-observation/labeled-net minimum marking;
  - generic heuristic marking search.
- Reseed reason:
  - reachability-decidable structure modification is a distinct modeling and
    complexity category. The two-round stop counter reset again.

## Round 7: L32-L33 Reseed

- Date: 2026-07-30.
- Seeds and live OpenAlex counts:
  - `L32`, `W4403826990`: 50 indexed references, 22 indexed citations;
  - `L33`, `W4412352793`: 61 indexed references, 2 indexed citations.
- Bound:
  - top eight backward references by cited count for each seed;
  - top eight forward citations for L32 and all two indexed citations for L33.
- In-scope result:
  - backward records returned classical PN foundations, linear/state-equation
    analysis, resource-transition circuits, and manufacturing-modeling
    references;
  - forward records returned applications, S4PR supervisor synthesis, and
    controller/design optimization papers;
  - no new first-paper model class, theorem type, complexity boundary, or
    counterexample category.
- Stop counter: first consecutive no-new-category round after the Round 6
  reset.

## Round 8: Relevant R7 Forward Branches

- Date: 2026-07-30.
- Anchor selection rule: retain every R7 forward record whose title/metadata
  directly concerned FMS/AMS deadlock, liveness, or S4PR supervision; exclude
  unrelated application records before querying.
- Anchors and live OpenAlex counts:
  - `10.1109/CICN63059.2024.10847497`: 37 references, 4 citations;
  - `10.1109/ICATEI67676.2025.11405229`: 38 references, 2 citations;
  - `10.1109/ICATEI67676.2025.11405088`: 36 references, 2 citations.
- Bound: top eight backward references and up to eight forward citations per
  anchor.
- In-scope result:
  - all branches repeated optimal/maximally-permissive PN supervision,
    transition-based recovery, siphon control, S3PR/S4PR, flexible
    routes/assembly, or unreliable-resource extensions;
  - no new first-paper model class, theorem type, complexity boundary, or
    counterexample category.
- Stop reason:
  - second consecutive bounded round without a new in-scope category after the
    latest reset.

## Supplied Full-text Audit: L30-L35 and B05

- Date: 2026-07-30.
- Inputs:
  - seven user-supplied full texts for `L30-L35` and `B05`;
  - L31 author supplement repository `Supplementary-File-of-T-ASE-2025-4089`,
    commit `f05b4b884480ba9ce217470ab52cdb865afedc66`;
  - L33 author supplement repository `S.F.TASE.2025.3588429`, commit
    `c54223b9a68a1b16758f2d90cdef7a486b5a588c`.
- Manifest:
  - `L30`: SHA-256 `8d2c2a43a4ec5570ec519e4280a32b88a74fc76a77795da500476342044ca6ea`, 11 pages;
  - `L31`: SHA-256 `b1abf149e95916a1d2afa4f6cadf6ddf1c11dbb4c4ff063ca711271b3ab04ddc`, 12 pages;
  - `L32`: SHA-256 `d4c41b67f716b278d2c14f15bbca49e69e3a81ff9cff0c9301bb1b56e5d5d19b`, 12 pages;
  - `L33`: SHA-256 `08ac32d4db03bc5ed8c203de8fe10d5544dd9018381bd492579e06ecc137fe4e`, 12 pages;
  - `L34`: SHA-256 `fb6d8c25fdbe5d63a26da64161b195d17dbf8c4f768e485354eb60c247d6f76f`, 12 pages;
  - `L35`: SHA-256 `5f984ac8cf78a8fb744b9da40d8c80df2537a1bc57a1af20f3f06c367473c5a5`, 8 pages;
  - `B05`: SHA-256 `d0c73000b702a22079f316bf0830d1452342f04d581c28b5ad6f06856f76b7f4`, 7 pages;
  - L31 supplement: SHA-256 `6ffee05ae4f21e14802c2d6547f2e3d1ac9d1a41ce7beb9045b590fa13397088`, 10 pages;
  - L33 supplement: SHA-256 `50e00f06c8d927b8c7a33d3b47dbbeb639a0768c01bed75da969440f60b482ed`, 1 page.
- Extraction result:
  - `L30`: finite-capacity S3PR/ENS3PR definitions, Theorems 1-3, Algorithm 1,
    and exponential SMS/ILP complexity terms located. It is sufficient
    resource configuration, not an exact IMS iff result.
  - `L31`: S4PR definition, partial-deadlock definition, CRP Theorems 1-4,
    and supplement proofs/Algorithms S1-S4 located. CRP candidates are still
    checked with SBA for reachability.
  - `L32-L33`: structure-modification and reachability algorithms located.
    Their main transferable content is transformed-model trace lift/counter-
    state preservation; they do not automatically prove an IMS operational
    bridge or fixed-target recorder-count completeness.
  - `L34-L35`: BA/SBA theorem and algorithm locators extracted. Complexity is
    `O(n*n1*(c*m+n^2))`, with `c` and numeric `n1` preventing a compact-input
    bit-polynomial claim in this audit.
  - `B05`: full-RG, MCPP, Algorithm 1, and Theorem 1 located. The method is
    maximally permissive only under monitor/P-semiflow expressibility and MCPP
    optimality; RG enumeration is exponential and MCPP is NP-hard.

## Current Gate Interpretation

Rounds 7-8 close the bounded taxonomy-saturation sub-gate. The supplied
full-text audit closes the current theorem-locator sub-gate. Together they set
G1 to `PASS (scope-bounded)`.

This does not make OpenAlex complete, does not prove priority, and does not
authorize broad-first or general PN bit-polynomial claims. L30-L35 and B05 are
now full-text comparators whose assumptions, limitations, and nontransferable
IMS boundaries must remain visible in all G2 and manuscript claims.
