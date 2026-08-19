# T-ASE H6/H7/H8 review corrigendum

Status: `CORRIGENDUM / DOES NOT REPLACE HASHED SPECS`
Date: 2026-08-19
Does not change the SHA-256 of
`2026-08-19-tase-h6-embedding-design.md`,
`2026-08-19-tase-h7-island-v4-design.md`, or
`2026-08-19-tase-h8-supervisor-design.md`.

Independent review of commit `533fbac` found four load-bearing
wording defects. This note records the corrections that the proofs
file now follows. The hashed specs stay byte-frozen; later manuscript
delta must follow this corrigendum, not the colliding sentences.

1. **Table 0.** Selected-bad is \(D^\dagger=D^{\mathrm{G}}\cup D^{\mathrm{L}}\).
   Stopped target is \(A^\dagger=D^\dagger\cup F\).
   \(\theta^{\mathrm{B}}\) is the probability of first hitting \(D^\dagger\),
   not \(\mathbb{P}(\tau_{A^\dagger}<\infty)\). Embedding correspondence
   is \(\chi\), not Table 0 \(\chi_s\).

2. **H7 intervention \(|X|\).** Base has 64 states. Extra AGV slot has
   72 states. The proofs table that wrote 64 for the intervention is
   wrong.

3. **E4.** Def H6.2’s one-step commutation is now checked on every
   reachable IMS state that \(\chi\) represents, not only the two idle
   starts. Finite-batch completion is outside \(\chi\). H6-A still
   verifies.

4. **H7 admission.** Recorded route is Theorem 4
   (`admission_route=lts_fallback`, method
   `complete_lts_completion_nonreachability_v1`). Do not cite Theorem 3
   for this clothing unless A2b is separately proved.

Hashed specs are not rewritten so that evidence reports that already
cite those three SHA-256 values remain well-defined.
