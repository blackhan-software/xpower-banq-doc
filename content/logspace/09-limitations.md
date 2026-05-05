---
title: "9. Limitations & Future Work"
prev:
  text: "8. Adversarial Analysis"
  link: /logspace/08-adversarial-analysis
next:
  text: "10. Conclusion"
  link: /logspace/10-conclusion
---

## Limitations

1. **Single-protocol validation.** All benchmarks and precision measurements are from XPower Banq. Results may differ for protocols with different accrual frequencies, utilization patterns, or index structures (e.g., Aave's rebasing aTokens, where `balanceOf` is the interest-inclusive view).
2. **Read-path cost increase.** Protocols with on-chain read/write ratios $R > 1.09$ may see a net gas increase ([Gas Analysis](/logspace/06-gas-analysis#theoretical-cost-model)).
3. **Optimizer-off benchmarks.** Gas measurements were taken with the Solidity optimizer disabled to ensure reproducibility. Optimizer-on results may narrow or widen deltas depending on how `exp()` and `mulDiv` are inlined and optimized.
4. **Self-referential citations.** References to the [Whitepaper](/whitepaper/01-introduction) and [Time Locks](/timelocks/01-introduction) are unpublished XPower Banq preprints. Independent reproduction requires access to the protocol's source code.

## Future Work

1. **Cross-protocol benchmarks.** Apply the transformation to a fork of Aave v3 or Compound v3 and measure gas and precision under their accrual patterns and read frequencies.
2. **Optimizer-on gas profile.** Re-run benchmarks with the Solidity optimizer enabled at standard settings (200 runs) to provide production-representative figures.
3. **Formal verification.** A machine-checked proof (e.g., in Certora or Halmos) of the conservation invariant ([§4](/logspace/04-log-space-index#invariants)) would strengthen confidence for high-TVL deployments.
4. **`ln(1+x)` variant.** For protocols using linear approximation $(1 + r \cdot \Delta t)$ rather than $\exp(r \cdot \Delta t)$, a log-space variant storing $\sum \ln(1 + r_i \cdot \Delta t_i)$ may be preferable. Its gas and precision tradeoffs remain uncharacterised.
