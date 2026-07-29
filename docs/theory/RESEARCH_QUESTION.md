# IMS-RAS Research Question

## Primary Question

在明确定义的有限批 IMS-RAS 子类中，操作死锁何时具有可计算、可审计且足以支持非阻塞监督的最小结构证书？

## Subquestions

1. **Structural equivalence.** After zero-time closure, when is an IMS
   operational deadlock equivalent to a terminal closed blocking kernel in a
   state-dependent wait graph?
2. **Petri/RAS bridge.** Under which structural assumptions does that blocking
   kernel correspond to a minimal deadly siphon or to an RAS unsafe state, and
   where do those correspondences fail?
3. **Probability layer.** For an IMS-CTMC with completion and deadlock as
   competing absorbing classes, how do committor probabilities, mean absorption
   times, and conditioned deadlock paths relate to the same structural
   certificates?
4. **Control layer.** Which controllable choices can eliminate all minimal
   deadlock kernels while preserving maximum-permissive nonblocking behavior
   or a quantified risk budget?

## Exclusions for the First Paper

- equipment failure and repair;
- preemption;
- dynamic order insertion;
- infinite exogenous arrivals;
- non-Markov timing except as a later PH-approximation or simulation extension.

These exclusions are modeling boundaries, not claims that the phenomena are
unimportant.

## Evidence Standard

Theorems must be supported by:

- explicit assumptions;
- constructive proof or reduction;
- counterexample ledger for failed stronger claims;
- exhaustive enumeration on small models as falsification support;
- frozen confirmation cases only after the theory gate.
