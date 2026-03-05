# Liquidation risk

If you borrow, you can be liquidated. This page covers what that costs you and how to avoid it.

## When it happens

The moment your [health factor](/concepts/health-factor) drops below 100%. This can happen because of:

- A drop in collateral price.
- A rise in debt-token price.
- Accrued borrow interest pushing your effective debt above the threshold.
- Some combination of all three.

There is no warning. There is no grace period. Liquidation by holders of a pool's `POOL_SQUARE_ROLE` is always available via `square(...)`; permissionless liquidation via `liquidate(...)` is additionally available whenever governance has granted that pool's `POOL_SQUARE_ROLE` to the pool address itself (the public path runs `this.square(...)` internally, so the role check tests the pool — granting/revoking that role from the pool is the per-pool on/off switch for permissionless liquidations).

## What it costs

At the liquidation boundary (H = 100%) with default weights, the implicit liquidation bonus is (255/170) − 1 = 50%. A liquidation that clears $D of your debt at the boundary takes $D × 1.5 of your collateral — a net cost of **0.5 × D in collateral**, paid to the liquidator on top of clearing the debt.

For a 1,000 XPOW debt being liquidated at the boundary, you lose 500 XPOW of collateral above and beyond the cleared debt. Strictly underwater (H < 100%) the realised bonus is smaller, because uniform slicing seizes collateral in proportion to your live C/D ratio.

## Partial liquidations

The caller passes the **partial liquidation exponent** `e` on every call — `e = 1` slices 50%, `e = 2` slices 25%, and so on. There is no protocol-stored default; the value is the liquidator's choice (subject to the per-`partial_exp` `POW_SQUARE` PoW cost on the public path).

Crucially, **partial liquidation preserves your health factor**: the slice is taken uniformly from debt *and* collateral, so H_after = α·C·(1−s)/(D·(1−s)) = α·C/D = H_before. After a 50% liquidation at H = 0.95, you are at H = 0.95 with half the position size — *not* magically back above 100%. The position remains liquidatable until your H recovers (price move, interest swing, top-up, or settle).

Only `e = 0` — a full liquidation — closes the position outright. H goes from "less than 100%" to "undefined" because both numerator and denominator are zero.

If your H stays underwater, another liquidation can be called immediately. There's no "minimum gap" between liquidations.

In a fast crash, a single position can be liquidated repeatedly in quick succession, each call shrinking it by `2^-e` while leaving H unchanged.

## Avoiding it

Three concrete strategies, in order of how active you need to be:

1. **Maintain healthy H.** H ≥ 150% absorbs most normal volatility. H ≥ 200% absorbs most bear markets. Most casual users should run at H ≥ 200%.
2. **Set alerts.** Use a monitoring service (open-source or commercial) to notify you when H drops below your threshold.
3. **Top up actively.** Supply more or settle some debt the moment H drops below your safe floor.

## What cascade attenuation means for you

If you're a borrower in a pool with high lock adoption, your individual liquidation risk is the same as in any pool — H < 100% means liquidation, regardless of others' lock state. But the *systemic risk* of a cascade pulling you under is reduced.

If you're a supplier, the picture is different: cascade attenuation makes it more likely you keep your full supply through a crash. The pool is more likely to remain solvent.

## Where to go next

- [Health factor](/concepts/health-factor) — the trigger
- [Monitoring health](/using-the-protocol/monitoring-health) — practical tips
- [Cascade protection](/features/locked-positions/cascade-protection) — the systemic protection
