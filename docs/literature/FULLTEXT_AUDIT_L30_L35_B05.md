# Full-text Audit: L30-L35 and B05

Date: 2026-07-30 Asia/Shanghai.

Scope: seven supplied full texts plus two author supplement files were audited
for theorem locators, assumptions, proof shape, complexity, limitations, and
IMS migration boundaries. The PDFs and temporary extracted text remain outside
Git. This file records locators and permitted use only.

G1 verdict after this audit: `PASS (scope-bounded)`. This means bounded
taxonomy saturation and full-text theorem-locator extraction are complete for
the current G1 comparator set. It does not prove scientific priority. Broad
first claims, generic Petri-net bit-polynomial reachability claims, and general
IMS priority claims remain prohibited.

Full-text theorem-located anchor count after this audit: 20. Newly upgraded
anchors, each under the limitations below: `L30`, `L31`, `L32`, `L33`, `L34`,
`L35`, and `B05`.

## Manifest

| ID | File class | SHA-256 | Pages | Locator status |
| --- | --- | --- | --- | --- |
| L30 | supplied full text | `8d2c2a43a4ec5570ec519e4280a32b88a74fc76a77795da500476342044ca6ea` | 11 | full-text theorem locator extracted |
| L31 | supplied full text | `b1abf149e95916a1d2afa4f6cadf6ddf1c11dbb4c4ff063ca711271b3ab04ddc` | 12 | full-text theorem locator extracted; supplement audited |
| L32 | supplied full text | `d4c41b67f716b278d2c14f15bbca49e69e3a81ff9cff0c9301bb1b56e5d5d19b` | 12 | full-text theorem locator extracted |
| L33 | supplied full text | `08ac32d4db03bc5ed8c203de8fe10d5544dd9018381bd492579e06ecc137fe4e` | 12 | full-text theorem locator extracted; supplement audited |
| L34 | supplied full text | `fb6d8c25fdbe5d63a26da64161b195d17dbf8c4f768e485354eb60c247d6f76f` | 12 | full-text theorem/algorithm locator extracted |
| L35 | supplied full text | `5f984ac8cf78a8fb744b9da40d8c80df2537a1bc57a1af20f3f06c367473c5a5` | 8 | full-text theorem/algorithm locator extracted |
| B05 | supplied full text | `d0c73000b702a22079f316bf0830d1452342f04d581c28b5ad6f06856f76b7f4` | 7 | full-text theorem locator extracted |
| L31 supplement | author GitHub supplement, `Supplementary-File-of-T-ASE-2025-4089`, commit `f05b4b884480ba9ce217470ab52cdb865afedc66` | `6ffee05ae4f21e14802c2d6547f2e3d1ac9d1a41ce7beb9045b590fa13397088` | 10 | proofs and Algorithms S1-S4 support L31 |
| L33 supplement | author GitHub supplement, `S.F.TASE.2025.3588429`, commit `c54223b9a68a1b16758f2d90cdef7a486b5a588c` | `50e00f06c8d927b8c7a33d3b47dbbeb639a0768c01bed75da969440f60b482ed` | 1 | compact functionality/preservation support for L33 |

## L30: finite-capacity S3PR resource configuration

Source: Pang et al., "Deadlock prevention in flexible manufacturing systems:
A verification-free resource configuration approach for liveness of
finite-capacity S3PR," https://doi.org/10.1177/01423312251369553.

Locators:

- PDF p3: Definition 1 defines `S3PR`.
- PDF p4: Definition 2 defines finite-capacity `S3PR`.
- PDF p4: Definition 3 defines the equivalent net of a finite-capacity S3PR
  (`ENS3PR`) by adding capacity places; the text states that `ENS3PR` is a
  kind of `S4PR`.
- PDF p4-p5: Definitions 4-6 define liveness, acceptable initial marking, SMS,
  holders, and complementary set.
- PDF p5: Theorems 1-3 give the sufficient liveness/resource-configuration
  conditions for the marked `ENS3PR`.
- PDF p6: Algorithm 1, "Obtaining the minimum of `M0(PR)`."
- PDF p7-p8: "Complex analysis" decomposes Algorithm 1 into SMS computation,
  complement computation, linear-program condition formulation, and ILP
  solving.

Assumptions and proof shape:

- The net is a finite-capacity S3PR transformed into `ENS3PR`; liveness is
  argued through the transformed net's S4PR/SMS conditions.
- Capacity is represented structurally by additional capacity places, not by
  arbitrary IMS finite buffers.
- The proof chain is structural and sufficient: compute/control SMS conditions
  in `ENS3PR` so the original finite-capacity S3PR inherits liveness through
  the stated equivalence.

Complexity:

- The paper records SMS enumeration as worst-case `O(2^Np)`, ILP solving as
  worst-case exponential `O(2^v)`, and the simplified overall bound as
  `O(2^Np)` when resource-place variables are fewer than total places.
- This is not a polynomial-time resource-configuration theorem.

IMS migration:

- DIRECT: finite-capacity S3PR and equivalent-net resource configuration are
  mandatory comparators for restricted Petri-encodable capacity thresholds.
- ADAPTED: use only after an IMS subclass is encoded as the paper's
  finite-capacity S3PR/ENS3PR with matching capacity-place semantics.
- NONTRANSFERABLE: no result covers BAS blocked-unload semantics, AGV
  occupancy/reservations, OR-of-AND acquisition, zero-time closure, probability
  interfaces, or general IMS plant liveness.
- Claim boundary: L30 is a sufficient liveness configuration result, not an
  exact iff threshold for IMS. `BIX1-SAT` remains only a family-specific exact
  threshold under its declared start/completion/drain semantics.

## L31: S4PR CRP reachable partial-deadlock detection

Source: Su et al., "A Novel Petri Net-Based Deadlock Detection Method for
Automated Manufacturing Systems," https://doi.org/10.1109/TASE.2026.3689269.

Locators:

- PDF p4: Definition 5 defines `S4PR`; Properties 1-2 are delegated to the
  supplement.
- PDF p4: Definition 6 defines partial deadlock for S4PR as all ongoing jobs
  being stuck, with a backward-control rationale.
- PDF p5: Definition 7 defines critical places; Definition 8 defines
  resource-limits; Theorem 1 gives the iff condition for an output transition
  not being enabled at a marking.
- PDF p6: Theorem 2 connects all output transitions of a marked critical place
  to a set of resource-limit pairs.
- PDF p6: Definition 10 defines the critical set of resource-limit pairs
  (`CRP`); Theorem 3 states that a marking is a partial deadlock iff there is a
  CRP at the marking.
- PDF p6-p7: Theorem 4 gives a necessary resource-occupancy condition for a
  CRP; the detection method is then expressed through CRP enumeration and
  equations.
- PDF p7: the paper states that the reachability of obtained partial deadlocks
  is determined via SBA and that Algorithm S3 is repeated for each CRP.
- PDF p8-p10: examples and case studies compare CRP-based detection against
  PA-circuits and reachability-graph scale.
- Supplement PDF pp1-10: proofs of properties/lemmas/theorems and Algorithms
  S1-S4 for RP/CRP detection and reduced CRP selection.

Assumptions and proof shape:

- The plant class is S4PR. The partial-deadlock definition is specialized to
  ongoing jobs in the paper's activity/resource-place structure.
- CRP exactness is a marking-level characterization inside S4PR.
- Reachability of candidate partial deadlocks is not supplied by CRP equations
  alone; candidates are still checked with SBA.

Complexity:

- The supplement reports Algorithm S2 as
  `O(|Omega|^3+|P_R||Omega|^2)` and Algorithm S3 as
  `O(|Omega|^2(R_1+R_2))`, where `R_2` is the SBA cost. These are
  source-reported bounds, not an independent proof of polynomial scaling in a
  compact plant encoding.
- Algorithm S3 is repeated for each CRP. The source gives a coarse CRP-count
  bound and empirical evidence that the CRP set is smaller than the
  reachability graph, but this does not remove the SBA call or state an exact
  bit-complexity bound for the complete detector.
- The main paper's conclusion describes the overall computational burden as
  NP-hard. Reachability confirmation also inherits the `c` and numeric-`n1`
  caveats recorded for L34/L35.

IMS migration:

- DIRECT: S4PR CRP detection is a direct novelty comparator for any reachable
  partial-deadlock detector claim.
- ADAPTED: compare against IMS only through an explicit IMS-to-S4PR semantic
  encoding and a legal-event/reachability bridge.
- NONTRANSFERABLE: CRPs are not automatically IMS blocking kernels; equations
  do not replace a reachable IMS prefix; BAS, AGV, reservations, zero-time
  closure, OR-of-AND requests, and probability/control interfaces are outside
  the source theorem.
- Claim boundary: do not claim first reachable partial-deadlock detector or
  first reachability-tree-free detector. The defensible IMS claim must be the
  operational certificate/interface and refusal boundary.

## L32: reachability-decidable PN modeling for DES

Source: Su et al., "A Reachability-Decidable Petri Net Modeling Method for
Discrete Event Systems," https://doi.org/10.1109/TSMC.2024.3473851.

Locators:

- PDF p3: Theorems 1-2 restate state-equation necessity and acyclic-net
  sufficiency.
- PDF p4-p5: Algorithm 1 constructs a subnet/TP net; Theorem 3 gives time
  complexity `O(m^2 n^2)`.
- PDF p5-p7: Theorems 4-7 analyze independent places/transitions and show
  transformation toward a USPN-like modified net.
- PDF p7: Algorithm 2 constructs modified PNs; Theorem 8 gives Algorithm 2
  time complexity `O(m^2 n^2)`.
- PDF p7-p8: Theorems 9-10 give preservation directions between the original
  ordinary PN and modified PN.
- PDF p8: Algorithm 3 determines reachability; Theorem 11 gives the combined
  reachability decision procedure and polynomial-time claim for the modified
  model.

Assumptions and proof shape:

- The source works on ordinary PNs and modified PNs. Its preservation
  statements concern the original PN and its transformed model.
- It does not establish plant-level bisimulation for arbitrary IMS systems.
  The preserved object is the modeled/transformed PN trace or property relation
  stated by the paper.
- Algorithm 3 is displayed with an ordinary-PN input signature, while its
  surrounding text and Theorem 11 use it after the USPN transformation. This
  audit therefore authorizes only the explicit transform-then-decide call
  chain; it does not treat Algorithm 3 as a direct arbitrary-PN subroutine.

Complexity:

- The transformation algorithms are polynomial in structural parameters
  reported in the paper.
- The reachability-decision claim depends on the modified model construction
  and the legal-firing-sequence subroutine; it is not a generic polynomial
  reachability theorem for arbitrary original Petri nets or IMS plants.

IMS migration:

- DIRECT: mandatory comparator for any "reachability-decidable modeling" claim.
- ADAPTED: usable as a transformed-PN baseline only after defining what IMS
  behavior the source PN represents and what the modified PN preserves.
- NONTRANSFERABLE: the paper does not itself establish an IMS plant
  bisimulation, BAS/AGV/reservation/closure semantics, or preservation of IMS
  deadlock/completion absorbing classes.

## L33: AMS structure modification and reachability analysis

Source: Su et al., "A Structure-Modification-Based Petri Net Modeling and
Reachability Analysis Method for Automated Manufacturing Systems,"
https://doi.org/10.1109/TASE.2025.3588429.

Locators:

- PDF p3: Theorems 1-2 restate state-equation necessity and acyclic-net
  sufficiency.
- PDF p4: Theorems 3-4 give the vector/linear-independence basis for modifying
  a PN into a UniPN.
- PDF p5: Algorithm 1 constructs the modified PN; Theorem 5 gives time
  complexity `O(n^2 m)`.
- PDF p5-p7: Theorems 6-10 give preservation directions for reachability,
  liveness, persistence, repetitiveness, and original siphon/trap structure
  between the PN and its modified form. Boundedness may change: the paper
  explicitly allows a bounded source PN to become unbounded after modification.
- PDF p7: Algorithm 2 is the reachability determination algorithm.
- PDF p7: the SBA subroutine is used with complexity `O(n*n1*(c*m+n^2))`;
  `c` is the number of directed circuits and `n1` is the sum of non-zero
  elements in an NIS.
- PDF p9-p10: case studies apply Algorithm 1 and Algorithm 2 to AMS/S4PR
  examples.
- Supplement PDF p1: author supplement for additional preservation/proof
  material.

Assumptions and proof shape:

- The method modifies a PN model of an AMS into a UniPN-like structure and
  then performs state-equation/SBA reachability analysis.
- The preservation relation is between the source PN model and the modified PN
  model; it is not a full IMS plant bisimulation.
- Boundedness is not preserved in the strong direction needed for a blanket
  IMS transfer; it may change after modification.

Complexity:

- Algorithm 1 is polynomial in the paper's structural parameters.
- Algorithm 2 invokes SBA with `O(n*n1*(c*m+n^2))`; this depends on numeric
  `n1` and circuit count `c`. Therefore a standard compact-input
  bit-polynomial theorem is not established by this audit.
- The one-page supplement proposes a polynomial combinatorial upper bound for
  `c`, but its short extreme-case argument does not establish that bound for
  all directed circuits of the transformed net. The project therefore records
  the bound as source-claimed and does not use it to close a standard
  bit-polynomial proof.

IMS migration:

- DIRECT: mandatory AMS Petri-modeling comparator.
- ADAPTED: use only as a transformed-PN baseline after an IMS-to-PN semantic map
  and a proof of which traces/deadlock states are preserved.
- NONTRANSFERABLE: the paper does not itself establish general IMS operational
  equivalence, preservation of BAS/AGV/reservation/closure semantics, or a
  probability/supervisor interface.

## L34: state-equation-based backward LFS approach

Source: Su et al., "A State-Equation-Based Backward Approach to a Legal Firing
Sequence Existence Problem in Petri Nets,"
https://doi.org/10.1109/TSMC.2023.3241101.

Locators:

- PDF p3: Theorems 1-2 state state-equation necessity and acyclic-net
  sufficiency.
- PDF p3-p5: Theorems 3-6 characterize token/directed-circuit obstacles and
  dead-circuit conditions for absence of a legal firing sequence.
- PDF p5-p8: Algorithms 1-5 define SBA, backward decomposition, two directed
  circuit procedures, and reachability determination.
- PDF p7-p8: complexity analysis gives `O(n*n1*(c*m+n^2))` and states that
  `n`, `m`, `c`, and `n1` are independent.

Assumptions and proof shape:

- The input is a PN, initial/destination marking, and a fixed NIS `X` of the
  state equation.
- The proof attacks the necessary-not-sufficient gap by reasoning backward
  through directed-circuit blockers.

Complexity:

- The stated bound depends on the number of directed circuits `c` and numeric
  value `n1`, the sum of non-zero elements in `X`.
- This is a polynomial-time statement in the paper's chosen numeric
  parameters, not a confirmed compact-input bit-polynomial theorem.

IMS migration:

- DIRECT: source for the state-equation false-positive boundary and an SBA
  baseline for candidate NIS checking.
- ADAPTED: only after an IMS event sequence is encoded as a PN firing sequence.
- NONTRANSFERABLE: not an IMS deadlock certificate; not a proof that a linear
  equation solution is an executable IMS prefix.

## L35: backward algorithm for ordinary PN LFS existence

Source: Su et al., "A Backward Algorithm to Determine the Existence of Legal
Firing Sequences in Ordinary Petri Nets,"
https://doi.org/10.1109/LRA.2023.3246384.

Locators:

- PDF p2-p3: Theorems 1-5 give the ordinary-PN state-equation/LFS boundary and
  necessary-sufficient dead-circuit characterization.
- PDF p4-p6: Algorithms 1-5 define BA, backward firing process, output/non-
  output transition circuit procedures, and computation/judgment functions.
- PDF p6: complexity analysis gives `O(n*n1*(c*m+n^2))`.
- PDF p7: conclusion reiterates that state-equation NIS existence is only
  necessary and that BA has polynomial time in the paper's parameters.

Assumptions and proof shape:

- The net class is ordinary PNs and the input includes a fixed NIS.
- The proof develops a backward firing process to decide whether an LFS
  corresponds to that NIS.

Complexity:

- The same `c` and numeric `n1` caveat applies. A compact-input
  bit-polynomial theorem is not established.

IMS migration:

- DIRECT: source for ordinary-PN NIS false positives and BA baseline.
- ADAPTED: only after IMS operations are encoded as an ordinary PN with a
  fixed NIS and a firing-sequence interpretation.
- NONTRANSFERABLE: no general IMS reachability, liveness, or deadlock theorem.

## B05: compressed maximally permissive supervisor

Source: Chen and Li, "Design of a maximally permissive liveness-enforcing
supervisor with a compressed supervisory structure for flexible manufacturing
systems," https://doi.org/10.1016/j.automatica.2011.01.070.

Locators:

- PDF p3: Section 3.2 reviews maximally permissive control-place synthesis
  using the full reachability graph, legal markings, forbidden bad markings
  (`FBM`), and A-covering/minimal covered sets.
- PDF p3: Definitions 1-3 define A-covering, minimal covered set of FBM, and
  minimal covering set of legal markings.
- PDF p4: MCPP is formulated as an integer linear problem; Table 1 records
  constraint and variable counts.
- PDF p4: Algorithm 1, "Deadlock Prevention Policy."
- PDF p5: Theorem 1 states that, if each control place in Algorithm 1 is
  associated with a P-semiflow, Algorithm 1 obtains a maximally permissive
  supervisor with the minimal number of control places iff MCPP has an optimal
  solution.
- PDF p5: the paper states that complete enumeration of reachable markings is
  exponential and that MCPP is NP-hard.

Assumptions and proof shape:

- The method begins from the full reachability graph partitioned into legal and
  forbidden markings.
- The theorem requires monitor/P-semiflow expressibility of selected control
  places and MCPP optimality.
- The paper explicitly notes that there are Petri-net instances with no
  maximally permissive liveness-enforcing supervisor expressible by monitors.

Complexity:

- Full RG enumeration is exponential.
- MCPP is an ILP and NP-hard.

IMS migration:

- DIRECT: maximum-permissiveness and monitor-compression benchmark for small
  Petri-encodable FMS instances.
- ADAPTED: use after constructing the exact finite IMS transition system and a
  Petri-net/monitor representation satisfying the theorem's assumptions.
- NONTRANSFERABLE: no scalable IMS supervisor theorem, no structural IMS
  certificate, and no guarantee that every IMS maximum-permissive supervisor is
  monitor-expressible.

## Cross-source Migration Summary

- L30 blocks broad finite-capacity threshold novelty, but it is sufficient and
  S3PR/ENS3PR-bound, not an exact IMS iff result.
- L31 blocks broad reachable partial-deadlock detection priority, but its CRP
  equations still rely on SBA for reachability of candidates.
- L32-L33 block broad reachability-decidable modeling novelty, but their
  transformed-PN trace/property results do not themselves establish the
  preceding IMS-to-plant semantic bridge or its fixed-target quantification.
- L34-L35 require every linear-equation detector to prove legal firing or
  label itself a relaxation; their complexity bounds depend on `c` and numeric
  `n1`.
- B05 blocks broad maximally permissive monitor-supervisor novelty, but it
  requires full RG data, MCPP optimality, P-semiflow/monitor expressibility,
  and accepts NP-hard computational burden.

Therefore G1 passes only as a scope-bounded evidence gate. It authorizes G2
formalization under narrower claims; it does not authorize "first" or
"general polynomial" claims.
