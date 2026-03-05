---
title: Evaluation
prev: '/whitepaper/07-security'
next: '/whitepaper/09-limitations'
---

# Evaluation

## Agent-Based Cascade Simulation

We simulate 1,000 borrowers with log-normal positions, health factors $H \sim \mathcal{N}(1.5, 0.3)$ truncated at $[1.0, 3.0]$, and linear price impact $\Delta p = k \cdot V_{\text{sold}}$ with $k = 1.5 \times 10^{-4}$ (pool ${\sim}25\%$ of market depth).

**Cascade simulation — positions liquidated (%), $k = 1.5 \times 10^{-4}\text{:}$**

| Lock $\phi$ | 10% | 15% | 20% | 25% | 30% |
|---:|---:|---:|---:|---:|---:|
| 0% | 8.6 | 19.8 | 36.5 | 85.7 | 99.1 |
| 25% | 8.2 | 16.5 | 30.6 | 55.8 | 84.9 |
| 50% | 7.8 | 14.4 | 26.7 | 37.1 | 61.2 |
| 75% | 7.8 | 13.5 | 22.4 | 33.3 | 47.9 |
| 100% | 7.4 | 12.7 | 19.8 | 29.4 | 38.6 |

<figure>
  <img src="/images/007-cascade.svg" alt="Cascade depth vs. price drop for varying lock fractions">
  <figcaption>Figure 7: Cascade depth vs. price drop for varying lock fractions</figcaption>
</figure>

**Simulation Limitations.** The simulation uses 1,000 agents, which is too few for high statistical confidence. Health factor distributions are assumed rather than calibrated against real DeFi data. The linear price impact model (Kyle, 1985) is a first-order approximation; real order books exhibit concave impact. No confidence intervals or sensitivity analysis on $k$ are provided, and historical stress events are discussed narratively but not backtested. Implementation details appear in [Appendix E](/appendices/part-ii-simulations/cascade-simulations).

## Gas Cost Analysis

**Cross-protocol gas comparison, warm interactions (kgas):**

| Operation | Morpho Blue | Comp. V2 | Aave V3 | Aave V4 | XPower Banq |
|---|---:|---:|---:|---:|---:|
| Supply | 90k | 93k | 160k | 107k | 235k |
| Borrow | 130k | 200k | 320k | 205k | 336k |
| Settle | 91k | 112k | 180k | 120k | 161k |
| Redeem | 138k | 150k | 175k | 129k | 306k |
| Liquidate | — | 285k | 450k | 345k | 648k |

XPower Banq's gas costs are 1.8–2.6$\times$ those of Morpho Blue and 1.3–2.4$\times$ those of Aave V4. This comparison should be interpreted carefully: Morpho Blue achieves low costs through a minimalist singleton (approximately 550 lines) that delegates oracle validation, position caps, and risk management to external curators—an architectural trade-off with documented consequences (e.g., a 2024 oracle misconfiguration exploit). Euler V2 and Liquity V2, which are closer architectural comparators, were not available for inclusion. On Avalanche (approximately 1.55 gwei, AVAX <\$10), all operations cost under 1 cent USD.
