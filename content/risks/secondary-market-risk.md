# Secondary market risk

Locked positions can be sold on secondary markets — but at a discount, sometimes a wide one.

## Why a discount?

A locked position can't be redeemed for the underlying. A buyer of a locked position is buying:

- Future yield (interest accrual continues).
- A claim on the underlying *at lock expiry*.
- The lock-bonus differential vs unlocked equivalent.

In exchange, they accept:

- No liquidity until lock expiry.
- Lock-state mechanics on transfer.

The discount is the price the market clears for these constraints.

## Empirical reference

Comparable products have traded at 3–12% discounts during stress:

- Lido stETH discount during June 2022 liquidity crisis: 6–7%.
- Convex cvxCRV discount during 2022 stress: 5–12%.
- 4-year locked Curve veCRV equivalents: 3–10% historically.

Banq locked positions are expected to fall in a similar range, with discounts widening during stress and tightening as on-chain liquidity deepens.

## When it bites you

- **Forced exit.** If you need liquidity from a locked position, you sell at a discount. The longer the remaining lock, the larger the discount.
- **Liquidation of locked collateral.** If your position is partially locked and gets liquidated, the keeper receives locked tokens — they may sell to the secondary market at a discount, eating into the bonus they'd have earned.
- **Bootstrap markets.** Early on, secondary markets for locked positions may be thin. Discounts may be wide and volatile until liquidity deepens.

## When it helps you

- **Buying a locked position at a discount** is positive expected value if you can hold to expiry. The discount is essentially yield to the holder.
- **Cascade protection.** The mere existence of a discount-friendly secondary market means cascade dynamics are softer — keepers can sell rather than holding. This is part of the cascade-attenuation story, not a flaw.

## Where to go next

- [Transfers and exits](/features/locked-positions/transfers-and-exits) — how to sell on secondary
- [Cascade protection](/features/locked-positions/cascade-protection) — the systemic context
