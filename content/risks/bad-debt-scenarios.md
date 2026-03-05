# Bad debt scenarios

When a position becomes impossible to fully liquidate — because collateral has fallen below debt — the protocol absorbs the loss as bad debt. This is the worst-case for suppliers.

## How it can happen

The basic flow:

1. A borrower has supply of $V and debt of $D, with V > D × (1 + buffer).
2. A crash drops V below D + bonus_compensation.
3. By the time the oracle reflects the crash, the position is unsalvageable: even taking 100% of the supply, the protocol can't fully recover the debt.

## How sized is the buffer?

The default buffer (50% over-collateralisation, derived from LTV 66.67%) is sized so that:

- A 33% instantaneous crash (~half the buffer) leaves comfortable margin for liquidation.
- A 50% instantaneous crash (eats most of the buffer) is the borderline.
- A 60%+ instantaneous crash exceeds the buffer; bad debt can occur.

The Merton jump-diffusion Monte Carlo in the whitepaper computes:

| Configuration | Bad debt at 99% CVaR |
|---|---|
| Default (LTV 66.67%, BUFFER 50%) | 0.02% of pool |
| Conservative floor (LTV 33%, BUFFER 200%) | 0.00% even at 50% crash |

So at the default, very rare tail events can produce ~0.02% bad debt. At the conservative floor, even severe crashes produce no bad debt.

## What happens to bad debt

Bad debt reduces the pool's `totalAssets()`. This means:

- Suppliers' redemption value decreases pro-rata.
- The pool may take time to recover via positive interest accrual.
- In severe cases, governance may inject capital (from a treasury, if one exists).

There's no "socialisation switch" — the loss is automatic and proportional.

## Mitigations

- **Lower-LTV pools.** A pool running at the 33% conservative floor has effectively zero bad-debt risk for crashes up to 50%.
- **Diversify across pools.** A bad-debt event in one pool doesn't spread to others.
- **Watch the risk dashboard.** Aggregate H distribution and oracle staleness are leading indicators.

## What this means for suppliers

If you're supplying XPOW into a pool with diverse collateral types, your worst-case loss in a tail-event crash is bounded around 0.02% at default parameters. That's small but non-zero.

For users who can't tolerate any bad-debt risk, the conservative floor pools (when available) are the appropriate choice. They earn lower yields in exchange for the enhanced safety.

## Where to go next

- [Liquidation risk](/risks/liquidation-risk) — the borrower's view
- [Oracle staleness](/risks/oracle-staleness) — why crashes can outpace the oracle
- [Pool parameters](/parameters/pool-parameters) — LTV and BUFFER configurations
