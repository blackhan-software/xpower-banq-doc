# Spread and slippage

The protocol's oracle quotes both a price and a **bidirectional spread**. The spread captures the typical bid-ask gap and slippage cost for the asset, used to compute fair-value bounds for collateral and debt valuation.

## Why a spread?

A single mid-price oracle doesn't capture an asset's *liquidity*. A token with 1B XPOW in 24h volume and a token with 10K XPOW in 24h volume can have the same mid-price but very different real liquidation outcomes.

The spread is the protocol's way of pricing this difference. A wider spread means:

- More conservative collateral valuation.
- Larger over-collateralisation buffer required.
- More cautious liquidation bonus.

## How it's computed

The oracle computes both:

- A smoothed **log-mid-price** (geometric mean).
- A smoothed **log-spread** (the ratio of bid to ask, in log space).

These are stored separately and updated on each refresh, with the same `α = 0.944` decay.

The reported bid and ask use an **auto-widening** spread that scales with the notional being quoted. Per `Oracle::_hlfSpread`:

```
center      = quote at requested amount        (mid price)
rel         = stored relative half-spread      (from the TWAP'd log-spread)
x           = center * rel / mid               (normalised notional)
mu          = log2(x + 1) + 1                  (auto-widening multiplier)
hlf_spread  = center * (rel * mu) / 2

bid = center - hlf_spread
ask = center + hlf_spread
```

For small notionals (`x → 0`, so `mu → 1`), `hlf_spread → center · rel / 2` — i.e. the small-notional limit reduces to the simple `bid = center · (1 − rel/2)`, `ask = center · (1 + rel/2)` form. For larger notionals, `mu` grows logarithmically and the quoted spread widens, capturing the additional price impact a larger trade would face.

This shape gives two properties at once: small queries hit the smoothed log-space spread directly (linear in log-price, so the same multiplicative factor at any price level), and large queries pay an auto-widened premium proportional to `log₂(x+1)`.

## Empirical scaling

For most liquid assets:

- Major stablecoins (XPOW): spread ≈ 0.05–0.10%.
- Major majors (APOW, BTC): spread ≈ 0.05–0.20%.
- Mid-cap altcoins: spread ≈ 0.20–1.0%.
- Long-tail tokens: spread ≈ 1.0–10%.

The protocol uses the live oracle-reported spread; it doesn't hard-code these.

## Practical effect

For most users, the spread doesn't change the user-facing math. Health factor calculations use mid-price; the spread is a secondary input for risk-management computations.

The spread *does* affect the protocol-default LTV for newly added tokens. Higher spread = lower default LTV. Governance can adjust per-token weights to compensate.

## Where to go next

- [Manipulation resistance](/features/twap-oracle/manipulation-resistance) — security properties
- [Oracle parameters](/parameters/oracle-parameters) — defaults and bounds
- [Log-space index](/research/papers/log-space-index) — the math behind log-space TWAP
