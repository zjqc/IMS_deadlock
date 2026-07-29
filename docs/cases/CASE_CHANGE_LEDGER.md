# Case Change Ledger

Every discovery-case change that alters a theorem, definition, metric, or case
mechanism must be recorded here.

| Date | Case | Change | Reason | Consequence |
| --- | --- | --- | --- | --- |
| 2026-07-29 | all | Initial discovery/confirmation separation created. | Prevent post-hoc case selection. | Discovery cases may shape theory; confirmation cases remain unfrozen. |
| 2026-07-29 | C5 | Marked `C5-independent-witness-v1` as non-final because `output_capacity=0` prevents real AGV dispatch. | Avoid overstating evidence from a minimal blocked-complete witness. | Final C5 must add AGV blocked-unload and hard-reservation comparison. |
| 2026-07-29 | C1/C2/C4 | Added explicit non-zero structural transitions for bounded LTS enumeration. | Make cycle/projection screens executable instead of static-only. | C1 keeps a cycle false positive with completion; C2 remains acyclic with completion; C4 full model blocks on AGV while its machine/buffer projection has progress. |
| 2026-07-29 | C5/C5_DAG | Kept `C5` as bidirectional blocking and added `C5_DAG` with the reverse route removed. | Provide the requested paired repair witness. | C5 has an initial closed blocking kernel; C5_DAG has no certificate and a marked completion path. |
| 2026-07-29 | C0-C5 | Added bounded stable-LTS enumeration with per-branch zero-time traces, all initial closure outcomes, frontier omissions and full-event shortest prefixes. | Close audit gaps caused by non-confluent closure and state-count truncation. | Reachable certificates now carry the shortest deterministic event prefix; truncated searches cannot claim exact supervisor completeness. |
| 2026-07-29 | C0/C1/C3/C4 | Added a capacity-aware state-dependent bipartite wait-graph `knot` baseline distinct from finite-LTS terminal SCCs. | Prevent the Palmer-style queueing baseline from being conflated with an IMS proof or a simple-cycle screen. | C0/C4 have capacity-closed knots; C1/C3 reject raw-cycle false positives caused by residual capacity or missing holders. |
| 2026-07-29 | BIX0 | Added deterministic candidate-state grid verification for capacities 1-3 and job counts 0-4. | Machine-check the P3c threshold without treating enumeration as proof. | Every checked point matches `n_A>=c_M and n_B>=c_G`; `c_D` invariance is confined to the no-transfer candidate prefix. |
| 2026-07-29 | CTMC fixtures | Added exact residuals, sensitivity equations, Doob-h generator checks and independent Gillespie streams with Wilson intervals. | Close the small-model probability audit while preserving rate provenance. | `C0/C1` remain `fixture_unverified`; no structural-case rate derivation or confirmation claim is made. |
