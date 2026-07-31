# Probability Layer: IMS-CTMC, Committor, And Doob-h

This document covers finite CTMCs, or finite-state models after an explicit PH
expansion. Non-exponential timing cannot use these equations directly.

## 1. Competing Absorption Domains

Let `A = D_global union D_local union F` be the selected stopped target and let
`T = V \ A` be the nonabsorbing set. `S_reach` is the diagnostic complete
stopped-LTS support graph basin: states with at least one support path to `A`.
`S_reach` is necessary but not sufficient for probability-one absorption.

For the finite complete positive-rate stopped CTMC, identify every unselected
closed SCC `C subset T`. Membership lies in `T`, but closedness is checked
against all outgoing positive-rate edges in the full stopped graph: there is no
positive-rate edge from `C` to `(T \ C)` and no positive-rate edge from `C` to
selected A. A state with `s -> F` is not in an unselected closed SCC.

Let `B_closed` be the reverse basin in `T` of all unselected closed SCCs, and
let `S_T = T \ B_closed`. Under the finite complete positive-rate stopped-CTMC
assumptions, `x in S_T` iff `P_x(tau_A < infinity) = 1`. The global absorption
assumption `A_abs` is the stronger condition `B_closed = empty` over the claimed
nonabsorbing analysis domain.

## 2. Generator Block

The finite CTMC generator `Q` satisfies:

- `q_ij >= 0` for `i != j`;
- `q_ii = -sum_{j != i} q_ij`;
- states in selected A are absorbing, or folded into absorbing classes before
  block construction;
- PH expansion is required before non-exponential durations enter `Q`.

Only after `A_abs` is certified globally, or after a future protocol explicitly
supports a restricted certified `S_T`, may the block be used as:

`Q = [[Q_{S_T,S_T}, Q_{S_T,D}, Q_{S_T,F}], [0,0,0], [0,0,0]]`.

Production G4 currently refuses partial-domain quantitative payloads. That is a
protocol refusal, not a statement that restricted-domain linear systems are
mathematically nonexistent.

## 3. Deadlock Committor

For certified `S_T`, the deadlock committor `h_i = P_i(tau_D < tau_F)` satisfies:

- `h_i = 1` for `i in D`;
- `h_i = 0` for `i in F`;
- `Q_{S_T,S_T} h_{S_T} = - Q_{S_T,D} 1` for `i in S_T`.

`h_i` is a probability of hitting a selected bad target before success. It is
not a structural deadlock-existence predicate. Outside certified `S_T`, the
current production protocol refuses the payload because the global stopped-domain
contract is not certified; this is an unsupported-solver boundary, not a claim
that all conditional probabilities are mathematically nonexistent.

## 4. Mean Absorption Time

For certified `S_T`, the mean time to the selected absorbing target satisfies:

`Q_{S_T,S_T} tau_{S_T} = -1`.

If `B_closed` is reachable with positive probability and has not been selected
into a new target, then `tau_A = infinity` on those paths and the extended
unconditional expectation is `+infinity`. The finite mean-time payload is
therefore protocol-refused for the original global claim. Conditional deadlock
timing must be computed under a separate conditioned model, not by reusing
unconditional `tau`.

## 5. Sensitivity

For parameters `theta` that do not change the certified partition and have
differentiable rates, the candidate sensitivity system on certified `S_T` is:

`Q_{S_T,S_T} partial_theta h_{S_T} = - (partial_theta Q_{S_T,S_T}) h_{S_T} - (partial_theta Q_{S_T,D}) 1`.

The proof obligations are invertibility of `Q_{S_T,S_T}` on the certified
transient-to-absorption subspace, fixed state partition or explicit partition
change handling, and differentiable rate parameters.

## 6. Doob-h Conditioning

For states in certified `S_T` with `h_i > 0`, conditioning on first hitting `D`
uses jump rates:

`q^h_ij = q_ij h_j / h_i` for `i != j`.

The diagonal is:

`q^h_ii = - sum_{j != i} q^h_ij`.

This transform is undefined where `h_i = 0`, explains conditioned high-risk path
statistics, and is not a controller.

## 7. Output Contract

A probability payload must report:

- counts for `A`, `T`, `S_reach`, `S_T`, unselected closed SCCs, and `B_closed`;
- whether `A_abs` is certified;
- `positive_rate_graph_hash`, `policy_filter_hash`, `absorption_domain_hash`,
  `rate_manifest_hash`, and `estimand_id` with nullable identities preserved;
- the generator block construction summary;
- `h`, `tau`, sensitivity, and Doob-h outputs only for certified `S_T`;
- linear-system residuals;
- conditional path statistics when a conditioned model is explicitly declared;
- parameter sensitivity outputs with fixed-partition or partition-change handling;
- independent DES comparison confidence intervals when DES is authorized by a later protocol;
- the used rate manifest and random-stream manifest identities;
- explicit refusal code `non_almost_sure_absorption_domain` when a global claim
  has nonempty `B_closed`.

`rate_manifest_hash` binds the full declared rate manifest. It is separate from
`absorption_domain_hash`, which binds the certified absorption-domain identity.
Missing rates, explicit empty rates, and certified positive rates are distinct
identity states.

## 8. Source Boundary

Markov jump transition path theory and discrete committor background can cite
Metzner et al. 2009, DOI `10.1137/070699500`, but that source supports ergodic
Markov jump process TPT and discrete committor background only. It does not by
itself prove this absorbing IMS stopped-domain theorem.

The committor, mean-time, sensitivity, and Doob-h equations above are finite
CTMC equations used inside this project's certified stopped-domain boundary.
For conditioned jump-process/change-of-measure background, Corstanje and van der
Meulen (2025) provides the publicly checkable baseline: Eq. 3.1 gives adjusted
intensities, Eq. 3.3 gives the generator form, and Appendix D explains the
change of generator. Migrating that background into an IMS absorbing-boundary
theorem still requires the finite stopped-domain proof stated here.

Narahari et al. remains a manufacturing-system absorbing Markov baseline: Section
3 gives `F=(I-T)^-1`, Section 3.1 gives mean deadlock time, Section 3.2 gives
`G=FC`, and Section 4 gives transient deadlock-time distributions. That evidence
supports the historical DTMC/embedded-chain scope only; it does not replace this
project's CTMC committor, sensitivity, Doob-h, or certified absorption-domain
proof obligations.
