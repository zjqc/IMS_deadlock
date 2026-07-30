# Full-text Request List

This list records full-text requests and their closure state. The previous
Priority A/B requests for `L30-L35` and `B05` were fulfilled on 2026-07-30 by
user-supplied full texts and author supplements. It is retained as an
acquisition ledger rather than an active request queue.

Do not add downloaded PDFs to Git. Provide them out of band for inspection.

## Fulfilled on 2026-07-30

| ID | Citation | DOI / official entry | Supplied evidence | Extraction result |
| --- | --- | --- | --- | --- |
| L31 | Su, Zhou, Qi, et al., "A Novel Petri Net-Based Deadlock Detection Method for Automated Manufacturing Systems," IEEE T-ASE 23 (2026), 10247-10258 | https://doi.org/10.1109/TASE.2026.3689269 | 12-page full text plus author supplement repository `Supplementary-File-of-T-ASE-2025-4089` at commit `f05b4b884480ba9ce217470ab52cdb865afedc66` | S4PR, CRP definition, Theorems 1-4, supplement proofs/Algorithms S1-S4, SBA reachability-check boundary recorded. |
| L30 | Pang et al., "Deadlock prevention in flexible manufacturing systems: A verification-free resource configuration approach for liveness of finite-capacity S3PR," Transactions of the Institute of Measurement and Control 48(12), 3249-3259 | https://doi.org/10.1177/01423312251369553 | 11-page full text | Finite-capacity S3PR, ENS3PR, Theorems 1-3, Algorithm 1, and exponential complexity terms recorded; sufficient not exact iff. |
| L32 | Su, Zhou, Qi, and Wisniewski, "A Reachability-Decidable Petri Net Modeling Method for Discrete Event Systems," IEEE T-SMC: Systems 55(1), 453-464 | https://doi.org/10.1109/TSMC.2024.3473851 | 12-page full text | Transformation algorithms and Theorems 1-11 recorded; use limited to transformed-model trace/counter preservation unless separate IMS bridge is proved. |
| L33 | Su, Zhou, Qi, Albeshri, and Abusorrah, "A Structure-Modification-Based Petri Net Modeling and Reachability Analysis Method for Automated Manufacturing Systems," IEEE T-ASE 22 (2025), 20493-20504 | https://doi.org/10.1109/TASE.2025.3588429 | 12-page full text plus author supplement repository `S.F.TASE.2025.3588429` at commit `c54223b9a68a1b16758f2d90cdef7a486b5a588c` | AMS structure modification, Algorithms 1-2, preservation theorems, boundedness-may-change caveat, and SBA complexity caveat recorded. |
| B05 | Chen and Li, maximally permissive Petri-net supervisor paper | https://doi.org/10.1016/j.automatica.2011.01.070 | 7-page full text | Definitions 1-3, MCPP, Algorithm 1, Theorem 1, full-RG dependence, monitor-expressibility, and NP-hard MCPP recorded. |
| L34 | Su et al., state-equation-based backward legal-firing-sequence approach | https://doi.org/10.1109/TSMC.2023.3241101 | 12-page full text | Theorems 1-6, Algorithms 1-5, and `O(n*n1*(c*m+n^2))` complexity caveat recorded. |
| L35 | Su et al., backward legal-firing-sequence algorithm for ordinary Petri nets | https://doi.org/10.1109/LRA.2023.3246384 | 8-page full text | Theorems 1-5, Algorithms 1-5, ordinary-PN NIS false-positive boundary, and complexity caveat recorded. |

## Active Requests

None for the current G1 theorem-source gate.

Future requests should be added only if a new comparator is needed for a
specific claim or if a cited source needs exact theorem/proof locators.

## Delivery Check

For each supplied file, record:

- filename and SHA-256;
- whether it is publisher version, accepted manuscript, or author manuscript;
- page count;
- visible DOI/title/authors;
- any access or sharing restriction communicated by the provider.

The research library records locators and notes only. It does not commit the
PDF itself. The detailed manifest for this fulfilled batch is
`FULLTEXT_AUDIT_L30_L35_B05.md`.
