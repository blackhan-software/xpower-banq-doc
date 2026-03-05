# Simulations paper

Empirical validation of the protocol's properties across capacity dynamics, cascade dynamics, TWAP manipulation, and bad-debt analysis.

## Topics

### Capacity dynamics

Simulation of the cap function over many operations confirms:

- O(√n) Sybil scaling matches the theory.
- A patient attacker with capital retains ~48.6% share after 60 weeks of repeated operations.
- Honest small users are not artificially blocked — the cap floor and √(n+2) divisor combine to give meaningful first-deposit access.

### Cascade dynamics

Simulation of 1,000 borrowers under price shocks across different lock fractions:

| Shock | 0% locked | 25% | 50% | 75% | 100% |
|---|---|---|---|---|---|
| 10% | 8.6% | 8.2% | 7.8% | 7.8% | 7.4% |
| 25% | 85.7% | 55.8% | 37.1% | 33.3% | 29.4% |
| 30% | 99.1% | 84.9% | 61.2% | 47.9% | 38.6% |

Up to 80% reduction in liquidation count at full lock adoption under stress shocks.

### TWAP manipulation

60 Foundry-based scenarios test single-block, sandwich, and sustained manipulation. Two-tick immunity is verified: no single-block manipulation can affect the reported price.

### Bad-debt Monte Carlo

10,000 paths under Merton jump-diffusion confirm:

- At default LTV (66.67%) with 50% buffer: bad debt at 99% CVaR = 0.02% of pool.
- At conservative floor (33% LTV, 200% buffer): zero bad debt for crashes up to 50%.

## Where to find the paper

- **PDF:** [`banq-sim.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-sim.pdf) (latest release)
- **Unified bundle:** [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf) — this paper is Part IV (Simulations & Risk Analysis).

## Where to go next

- [Cascade protection](/features/locked-positions/cascade-protection) — what the simulations measure
- [Bad debt scenarios](/risks/bad-debt-scenarios) — risk implications
- [Manipulation resistance](/features/twap-oracle/manipulation-resistance) — TWAP results
