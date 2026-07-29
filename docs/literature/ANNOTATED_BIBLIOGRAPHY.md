# Annotated Bibliography

This bibliography separates proof-source anchors from contextual and candidate
sources. It intentionally records evidence limits instead of smoothing them
away.

## Proof-source Anchors

**Ezpeleta, J., Colom, J. M., & Martinez, J. (1995). A Petri net based deadlock
prevention policy for flexible manufacturing systems.**
https://doi.org/10.1109/70.370500

Use only for controlled S3PR liveness/siphon-control boundaries. The recorded
locators are Corollary V.2, Theorem VI.1, and Section VI. IMS migration still
requires a separate proof that an IMS subclass maps into the S3PR assumptions.

**Lawley, M. A., & Reveliotis, S. A. (2001). Deadlock avoidance for sequential
resource allocation systems: hard and easy cases.**
https://doi.org/10.1023/A:1012203214611

Use for SU-RAS safety NP-completeness and hard/easy subclass boundaries as
located in Sections 3-5. This is a safety-class anchor, not a direct theorem
about BAS, AGV, reservations, or zero-time closure.

**Nazeem, A., & Reveliotis, S. A. (2011). A practical approach for maximally
permissive liveness-enforcing supervision of complex resource allocation
systems.** https://doi.org/10.1109/TASE.2011.2159112

Use for the offline/online two-stage maximally permissive LES design framework
as supported by the author `CASE-2010.pdf` abstract and Sections II-III. Do not
attribute unlocated additional theorems to this source.

**Fei, Z., Reveliotis, S. A., Miremadi, S., & Akesson, K. (2015). BDD-based
symbolic computations for deadlock avoidance in resource allocation systems.**
https://doi.org/10.1109/TASE.2014.2369858

Use for the EFA/BDD framework and Theorem IV.1 on Algorithm 2 correctness. It
is an implementation benchmark, not the structural IMS contribution.

**Palmer, G. I., Harper, P. R., & Knight, V. A. (2018). Modelling deadlock in
open restricted queueing networks.** https://doi.org/10.1016/j.ejor.2017.10.039

Use as the strongest current structural certificate source for finite-buffer
queueing deadlock. Theorem 1 gives the knot equivalence; Theorem 2 gives the
restrictions under which the no-sink WCC shortcut works; the 2/3-server
counterexample is central to IMS case `C3`.

**Wu, N., & Zhou, M. (2001). Resource-oriented Petri nets in deadlock avoidance
of AGV systems.** https://doi.org/10.1109/ROBOT.2001.932531

Use for AGV circuit/cycle-chain conditions and the corresponding control law
only within the paper's AGV Petri-net assumptions. Recorded locators are
Theorems 3.1, 3.2, 4.1, and 5.1.

**Metzner, P., Schutte, C., & Vanden-Eijnden, E. (2009). Transition path theory
for Markov jump processes.** https://doi.org/10.1137/070699500

Use for Markov jump process TPT and the discrete committor equations in the
appendix. Its assumptions are ergodic Markov jump processes and A-B reactive
paths; it does not directly prove absorbing IMS-deadlock results.

## Verified Context Sources

**Li, Z. W., & Zhou, M. C. (2004). Elementary siphons of Petri nets and their
application to deadlock prevention in flexible manufacturing systems.**
https://doi.org/10.1109/TSMCA.2003.820576

The author PDF supports Sections 3, 4, 5, and 7 as context for elementary
siphon definitions, controllability discussion, algorithms, and FMS examples.
No theorem claim is migrated until exact theorem locators are extracted.

**Ramadge, P. J., & Wonham, W. M. (1987). Supervisory control of a class of
discrete event processes.** https://doi.org/10.1137/0325013

This remains the DES conceptual baseline, but this G1 library has not recorded
a theorem locator. It should be upgraded only after extracting the exact result
used for the IMS supervisor benchmark.

**Liu et al. Siphon survey.** https://doi.org/10.1016/j.ins.2015.08.037

Use as a siphon-review map only until stable locators are recorded. The wrong
DOI `10.1016/j.ins.2016.02.010` is rejected in `SOURCE_VERIFICATION.md`.

**Viswanadham, Johnson, Narahari 1990 conference text.**

Use only as provenance-limited inspiration for the `C4` three-resource
machine/AGV deadlock example. It is distinct from the journal paper
`Deadlock prevention and deadlock avoidance in flexible manufacturing systems
using Petri net models`, https://doi.org/10.1109/70.63257.

**Cerou, F., & Guyader, A. (2007). Adaptive multilevel splitting for rare event
analysis.** https://doi.org/10.1080/07362990601139628

Use as rare-event estimation context. No IMS theorem migration is currently
recorded.

## Candidate Sources

The remaining DOI-verified rows in `LITERATURE_MATRIX.md` are backlog or
metadata candidates. They should not appear in theorem statements until their
full-text assumptions and locators are recorded.
