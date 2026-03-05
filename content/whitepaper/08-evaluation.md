---
title: "8. Evaluation"
prev:
  text: "7. Security Analysis"
  link: /whitepaper/07-security
next:
  text: "9. Limitations & Future Work"
  link: /whitepaper/09-limitations
---

## Agent-Based Cascade Simulation

We simulate 1,000 borrowers with log-normal positions, health factors $H \sim \mathcal{N}(1.5, 0.3)$ truncated at $[1.0, 3.0]$, and linear price impact $\Delta p = k \cdot V_{\text{sold}}$ with $k = 1.5 \times 10^{-4}$ (pool ${\sim}25\%$ of market depth).

| Lock $\phi$ | 10% | 15% | 20% | 25% | 30% |
|---:|---:|---:|---:|---:|---:|
| 0% | 8.6 | 19.8 | 36.5 | 85.7 | 99.1 |
| 25% | 8.2 | 16.5 | 30.6 | 55.8 | 84.9 |
| 50% | 7.8 | 14.4 | 26.7 | 37.1 | 61.2 |
| 75% | 7.8 | 13.5 | 22.4 | 33.3 | 47.9 |
| 100% | 7.4 | 12.7 | 19.8 | 29.4 | 38.6 |

<small>Cascade simulation — positions liquidated (%), $k = 1.5 \times 10^{-4}$.</small>

<figure>
  <img src="/images/007-cascade.svg" alt="Cascade depth vs. price drop for varying lock fractions">
  <figcaption>Figure 8: Cascade depth versus price drop for varying lock fractions.</figcaption>
</figure>

**Simulation Limitations.** The simulation uses 1,000 agents, which is too few for high statistical confidence. Health factor distributions are assumed rather than calibrated against real DeFi data. The linear price impact model [\[kyle1985continuous\]](/reference/bibliography#kyle1985continuous) is a first-order approximation; real order books exhibit concave impact. No confidence intervals or sensitivity analysis on $k$ are provided, and historical stress events are discussed narratively but not backtested. Implementation details appear in [Cascade Simulations](/simulations/02-cascade).

## Gas Cost Analysis

Gas measurements are post-optimization Foundry snapshots (`FOUNDRY_OPTIMIZER=true`, default profile, `via_ir=false`), benchmarked against Aave V3.3 figures from a 2025 Cyfrin gas-optimization audit. Banq's warm-path gas is competitive with mainstream lending protocols on supply and dominates them on every other operation:

| Operation | Banq | Aave V3 | Δ |
|---|---:|---:|---:|
| Supply | 167,209 | 146,354 | +14% |
| Borrow | 140,884 | 247,485 | −43% |
| Repay (settle) | 123,403 | 189,518 | −35% |
| Withdraw (redeem) | 128,380 | 181,430 | −29% |
| Liquidation (full) | 298,882 | 389,059 | −23% |

<small>Banq vs. Aave V3 warm-path gas (Foundry, optimizer ON).</small>

| Operation | Cold | Warm | Notes |
|---|---:|---:|---|
| Supply | 285,814 | 167,209 | — |
| Borrow | 244,833 | 140,884 | self-pair |
| Borrow (cross-pair) | — | 194,317 | +53k oracle leg |
| Liquidation (full) | 298,882 | — | — |
| `healthOf` (view) | 44,611 | — | view-only |
| `lockSupply` (timed) | 179,860 | 66,688 | ring-slot lock |
| `lockSupply` (perma) | 86,712 | — | irrevocable |
| `lockBorrow` (timed) | 180,904 | 67,720 | debt lock |
| `xfer_supply` (1 slot) | 191,463 | — | lock-aware ERC20 |
| `xfer_supply` (16 slots) | 402,525 | — | worst-case ring scan |

<small>Cold-vs-warm and Banq-unique operations.</small>

The savings come from two implementation choices: (i) the [log-space compounding index](/logspace/01-introduction) eliminates `exp()` from the write path, saving $\sim$1,200 gas per accrual at the cost of $\sim$1,100 gas per `totalOf` read; (ii) the packed `_state` (global) and `_stateOf` (per-user) storage words pack `[uint80 index | uint64 stamp/depth | uint112 balance]` into a single `SSTORE`, halving the write cost relative to the canonical three-slot layout. The `Lock` library applies the same technique: `uint128[16]` ring slots pack two epoch-value pairs per word (8 words instead of 16 per user), and a single `cache` word packs `[uint120 perma | uint120 total | uint16 bits]`. On Avalanche (approximately 1.55 gwei, AVAX < \$10), all operations cost well under 1 cent USD.
