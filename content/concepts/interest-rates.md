# Interest rates

XPower Banq uses a **piecewise-linear interest rate model with a kink**, the same broad design as Compound and Aave. The rate is a function of pool **utilization** — the fraction of supplied tokens that have been borrowed.

![Interest rate curve](../diagrams/interest-rate-curve.svg)

## The model

Let U be utilization, U* be the optimal utilization (default 90%), and R* be the rate at the kink (default 10%). The **kinked rate** is:

$$
R_k(U) = \begin{cases}
U \cdot R^* / U^* & \text{if } U \leq U^* \\
\dfrac{U(1 - R^*) - (U^* - R^*)}{1 - U^*} & \text{otherwise}
\end{cases}
$$

On top of the kinked rate sits a flat **base risk premium** $b$ — the on-chain `BASE` parameter (default 0%). It lifts the entire curve by a constant amount regardless of utilization:

$$
R(U) = \min\big(R_k(U) + b,\; 200\%\big)
$$

The `min` with 200% caps the rate to bound interest in extreme post-kink scenarios. Because the premium is additive, a pool can price in a persistent risk floor (for example a high-volatility collateral) while keeping the same kink shape.

The borrow and supply rates derive from `R(U)` by adding/subtracting the spread (default s = 10%):

- **Borrow rate** = R(U) × (1 + s)
- **Supply rate** = U × R(U) × (1 − s)

The supply rate is scaled by utilization because interest is only earned on the *borrowed* portion of the pool — the idle supply earns nothing. This is the same utilization scaling Aave applies to its lender rate, and it guarantees the supply claim is always funded by actual borrower interest (no negative carry).

The 2s spread is the protocol's margin, applied to the **borrowed** portion: margin = U × S × R(U) × 2s = B × R(U) × 2s.

## Why a kink?

Below the kink, rates rise gently. Liquidity providers earn a modest yield; borrowers face manageable costs. The pool is in its normal operating regime.

Above the kink, rates rise steeply. This serves two purposes:

1. It pushes borrowers to repay (debt becomes expensive), reducing utilization.
2. It pushes new suppliers into the pool (yield becomes attractive), again reducing utilization.

The kink isn't a hard cap — utilization can exceed U* — but the steep slope discourages that for long.

## Default values

| Parameter | Default | Range |
|---|---|---|
| Base risk premium (b / `BASE`) | 0% | 0–50% |
| Optimal utilization (U*) | 90% | 0–100% |
| Rate at kink (R*) | 10% | 0–100% |
| Spread (s) | 10% | 0–50% |
| Maximum rate cap | 200% | (compile-time) |

All five are governable via [lethargic governance](/features/lethargic-governance/overview), so they can change over time but only slowly.

## Why a base risk premium?

The kinked curve sets the *utilization-dependent* rate. The base risk premium adds a *utilization-independent* floor: even at zero utilization the rate never drops below `b`. Governance can use it to encode a minimum cost of capital for a particular asset — for example to reflect the cost of the liquidity providers' opportunity set, or a risk floor for volatile collateral.

With the default `b = 0`, the model behaves exactly like the classic kinked curve. The premium is an optional dial, not a change to the default behaviour.

## How rates apply

Rates are quoted as **annualised continuous compounding rates** (in WAD precision, 18 decimals). They're not block-by-block discrete rates — interest accrues continuously based on elapsed time.

When you interact with the protocol, the global index updates from your last touchpoint to now using the elapsed time and the rate active over that period. If utilization changed during that window, the rate is integrated piecewise.

## What you actually pay (or earn)

For most users, the easy answer:

- Look up the **current borrow APY** and **current supply APY** in the app at [app.xpowerbanq.com](https://app.xpowerbanq.com).
- These are the *current* rates. They will change as utilization changes.
- For a quick estimate: borrow APY ≈ R(U) × 1.10, supply APY ≈ U × R(U) × 0.90.

Locked positions adjust this — locked suppliers earn more, locked borrowers pay less. See [Bonus and malus](/features/locked-positions/bonus-and-malus).

## Locked-position adjustments

The [lock bonus/malus](/features/locked-positions/bonus-and-malus) modifies effective rates based on a user's lock ratio λ ∈ [0, 1]:

- Locked supplier effective rate ≈ U × R(U) × (1 − s + s · λ) → at full lock, supply rate approaches U × R(U).
- Locked borrower effective rate ≈ R(U) × (1 + s − s · λ) → at full lock, borrow rate approaches R(U).

At full lock adoption, the effective spread compresses toward zero — the protocol margin trades off against incentivising lock adoption. Note the two sides do **not** converge to the same rate: the supply side retains its utilization scaling, so at full lock the supply rate is `U × R(U)` while the borrow rate is `R(U)`.

## Why this design?

The kinked model is well-understood, easy to reason about, and works well in practice. Alternatives (Euler's reactive controller, dynamic models) have stronger theoretical properties but are harder to predict.

XPower Banq's contribution isn't a new rate model; it's the *log-space accumulation* of interest over time, which avoids overflow in the index storage and improves precision. This is invisible to users — your APYs are quoted exactly the same way as in any other protocol — but it matters for protocol longevity. See [Log-space index](/research/papers/log-space-index) if you want the gory details.

## Where to go next

- [Bonus and malus](/features/locked-positions/bonus-and-malus) — how locking changes your effective rate
- [Pool parameters](/parameters/pool-parameters) — the full parameter table
- [Position parameters](/parameters/position-parameters) — base, utilization, rate, and spread defaults
