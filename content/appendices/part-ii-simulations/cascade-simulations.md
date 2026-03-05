---
title: "Appendix E: Cascade Simulations"
description: "Liquidation cascade simulation implementation with multi-scenario comparison and detailed per-scenario analysis."
---

# Appendix E: Cascade Simulation Implementation

This appendix provides the cascade simulation implementation. Both scripts share a common `simulate` function and output semicolon-separated values.

## Multi-Scenario Comparison

The following script compares lock effectiveness across five market liquidity scenarios at a fixed 20% price shock:

```python
#!/usr/bin/env python3
from numpy import clip, random

def simulate(positions, price_drop, impact_coef):
    """Simulates liquidation cascade with market impact."""
    initial_supply = sum(p[0] for p in positions)
    price = 1.0 - price_drop
    total_liquidated = 0
    while True:
        underwater = [p for p in positions
            if p[0] > 0 and (p[0] * price) / p[1] < 1.0]
        if not underwater:
            break
        round_sold = 0
        for p in underwater:
            unlocked = p[0] * (1 - p[2])
            round_sold += unlocked
            total_liquidated += p[0]
            p[0] = 0
            p[1] = 0
        price -= impact_coef * round_sold
        if price <= 0:
            break
    return (total_liquidated / initial_supply * 100
            ) if initial_supply > 0 else 0

def gen_positions(seed, n, lock):
    """Generate positions with given lock fraction."""
    random.seed(seed)
    sizes = random.lognormal(mean=0, sigma=1, size=n)
    healths = clip(random.normal(1.5, 0.3, n), 1.0, 3.0)
    return [[s, s/h, lock] for s, h in zip(sizes, healths)]

if __name__ == "__main__":
    n, seed, drop = 1000, 42, 0.20
    scenarios = [("Liquid", 1e-6, 0.2),
                 ("Moderate", 6e-5, 10.1),
                 ("Strong", 1.5e-4, 25.2),
                 ("Severe", 3e-4, 50.5),
                 ("Extreme", 5e-4, 84.1)]
    print("scenario;depth;k;liq0;liq1;reduction")
    for name, k, depth in scenarios:
        liq0 = simulate(gen_positions(seed, n, 0.0), drop, k)
        liq1 = simulate(gen_positions(seed, n, 1.0), drop, k)
        reduction = (liq0-liq1)/liq0 * 100 if liq0 > 0 else 0
        print(f"{name};{depth:.1f};{k:.0e};{liq0:.1f};{liq1:.1f};{reduction:.1f}")
```

## Detailed Per-Scenario Analysis

The following script generates detailed results for a specific scenario, varying both lock fraction and price shock:

```python
#!/usr/bin/env python3
import sys
from numpy import clip, random

# simulate() and gen_positions() same as above (omitted)

SCENARIOS = [("Liquid", 1e-6, 0.2),
             ("Moderate", 6e-5, 10.1),
             ("Strong", 1.5e-4, 25.2),
             ("Severe", 3e-4, 50.5),
             ("Extreme", 5e-4, 84.1)]

if __name__ == "__main__":
    idx = int(sys.argv[1])  # 0-4
    name, k, depth = SCENARIOS[idx]
    n, seed = 1000, 42
    locks = [0.00, 0.25, 0.50, 0.75, 1.00]
    drops = [0.10, 0.15, 0.20, 0.25, 0.30]
    print("lock;drop;liquidated")
    for lock in locks:
        for drop in drops:
            result = simulate(gen_positions(seed, n, lock), drop, k)
            print(f"{lock:.2f};{drop:.2f};{result:.3f}")
```

## Algorithm

The `simulate` function iterates a liquidation cascade: after applying the initial price drop, it identifies underwater positions ($H < 1$), liquidates them (computing unlocked collateral as supply $\times\,(1{-}\phi)$), applies linear market impact $p \leftarrow p - k \cdot V_{\text{sold}}$, and repeats until no underwater positions remain or price reaches zero.

## Market Impact Model

The linear price impact coefficient $k$ determines market depth ($1/k$ in supply units). The five scenarios range from *Liquid* ($k = 10^{-6}$, pool is 0.2% of depth, no cascade amplification) through *Strong* ($k = 1.5 \times 10^{-4}$, 25% of depth, 46% reduction from locks) to *Extreme* ($k = 5 \times 10^{-4}$, 84% of depth, 80% reduction). The locked fraction $\phi$ attenuates market impact by factor $(1{-}\phi)$, directly reducing cascade sell pressure.

## Limitations

The simulation assumes complete (rather than partial $2^{-e}$) liquidation, a linear impact model (real markets exhibit convex slippage), greedy liquidators (real behavior may involve front-running or strategic timing), and a single collateral asset (cross-collateral pools may exhibit different dynamics).
