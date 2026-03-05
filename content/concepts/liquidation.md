# Liquidation

Liquidation is the mechanism that keeps the protocol solvent when borrowers' collateral falls below a safe level. XPower Banq's liquidation differs from most protocols in one key way: the liquidator **assumes the debt** rather than repaying it.

This page covers liquidation from the borrower's perspective. For liquidators, see [For keepers](/for-keepers/overview).

## When liquidation triggers

Your position becomes liquidatable the moment your [health factor](/concepts/health-factor) drops below 100%. This can happen because:

- Collateral price falls.
- Debt-token price rises.
- Accrued borrow interest pushes your effective debt above the threshold.
- A combination of the above.

The protocol does **not** have a "warning" or "grace period." As soon as H < 100%, any keeper holding that pool's `POOL_SQUARE_ROLE` can liquidate via `square(...)`, and — when governance has enabled the permissionless path by also granting the pool's `POOL_SQUARE_ROLE` to the pool itself — anyone can liquidate via `liquidate(...)` after paying the PoW cost.

## What happens to you

A liquidation transfers a slice of your debt and a slice of your collateral atomically to the liquidator. The slice size is governed by the **partial liquidation exponent** `e`, which is passed in by the caller on every call — there is no protocol-stored default:

- e = 0 → 100% of your position (full liquidation)
- e = 1 → 50%
- e = 2 → 25%
- e = N → 1/2^N

### Health factor under partial liquidation

For any `e ≥ 1` (i.e. any *partial* liquidation), the slice `s = 2^-e` is taken uniformly from your debt **and** your collateral. Uniform slicing preserves the health factor exactly:

$$
H_\text{after} \;=\; \frac{\alpha \cdot C \cdot (1 - s)}{D \cdot (1 - s)} \;=\; \frac{\alpha \cdot C}{D} \;=\; H_\text{before}
$$

So a partial liquidation does **not** restore your H above 100%. If you were at H = 0.95 before a 50% slice, you are still at H = 0.95 after — your position is half the size, but no healthier. Another keeper can call `liquidate(victim, ...)` against you immediately; there is no protocol-imposed cooldown. Your H only rises if prices recover, interest swings, or you top up collateral / settle debt.

### Health factor under full liquidation

`e = 0` clears 100% of both sides at once. Both collateral and debt go to zero, so H = α · 0 / 0 is **undefined** (the position no longer exists in any meaningful accounting sense). From the protocol's point of view, the position is closed.

## What you lose

At the liquidation boundary (H = 100%) with default weights, the **implicit liquidation bonus** is set by the weight ratio: (255/170) − 1 = **50%**. A liquidator who takes debt of value $D$ at the boundary receives collateral worth $D × 1.5$.

Strictly underwater (H < 100%), the realised bonus shrinks: uniform slicing always preserves the *ratio* of seized collateral to seized debt, and that ratio is your live C/D. The longer the keeper waits, the smaller their margin — at the extreme H ≤ α the liquidator breaks even or loses money, which is the bad-debt region.

In effect, at the boundary, liquidation costs you 50% of the debt being cleared, paid in collateral.

::: warning Worked example
You have 300 XPOW of collateral and 200 XPOW of debt. H = (300 × 0.667) / 200 = 100% — right at the edge.

A liquidator calls `liquidate(victim, 1)` (or `square(caller, victim, 1)` if they hold the role), clearing half:

- Debt cleared: 100 XPOW (50% of 200)
- Collateral transferred: 150 XPOW (50% of 300)

After:
- Your remaining collateral: 150 XPOW
- Your remaining debt: 100 XPOW
- New H = (150 × 0.667) / 100 = **100%** — exactly preserved.

The liquidator's profit is 150 − 100 = 50 XPOW (the 50% boundary bonus, captured in collateral). Your position is half the size, but at the same H — and so it remains liquidatable for as long as your H stays under 100%.
:::

## Locked positions and liquidation

Liquidation works on locked positions too — locks don't make you immune. But there's a difference in *what is transferred*:

- For unlocked supply, the liquidator can immediately redeem the underlying tokens from the vault.
- For locked supply, the liquidator receives **locked position tokens** with the lock fraction preserved proportionally. They cannot redeem the underlying until the lock expires.

This is the mechanism behind [cascade attenuation](/features/locked-positions/cascade-protection): only unlocked collateral can hit the open market, so cascade-driven sell pressure is bounded by the unlocked fraction.

In practice, liquidators prefer unlocked positions for the immediate liquidity. This creates de-facto **liquidation seniority** for locked positions: in a cascade, unlocked positions get hit first.

## Two liquidation paths

The protocol has two ways to call liquidation:
1. **`square(user, victim, partial_exp)`** — the role-restricted path. Open only to holders of that pool's `POOL_SQUARE_ROLE`. No PoW gate.

2. **`liquidate(victim, partial_exp)`** — the public path. Anyone can call it, but it carries a per-`partial_exp` PoW cost from the `POW_SQUARE` parameter, and it works only when governance has granted that pool's `POOL_SQUARE_ROLE` to the pool itself. Internally it invokes `this.square(msg.sender, victim, partial_exp)`, so the role check inside `square()` is applied to the pool — not to the external caller. Revoking the role from the pool address turns the public path off for *that pool*; granting it turns the public path on. Direct `square()` calls by other role-holders are unaffected either way.

Both paths use the same debt-assumption mechanics. See [Debt assumption liquidation](/features/debt-assumption-liquidation/overview).

## Avoiding liquidation

Three concrete strategies:

1. **Maintain a safety margin.** A higher H requires larger price moves to liquidate you. H ≥ 150% covers most normal volatility; H ≥ 200% covers most bear markets.
2. **Top up collateral when H drops.** Supply more, or settle some debt.
3. **Set alerts.** Off-chain monitoring tools can ping you when H falls below a threshold of your choosing.

The protocol does not auto-liquidate based on oracle staleness — there's a 12-hour TWAP half-life and a one-hour refresh interval, so the oracle responds slowly to genuine price moves. This works in your favour: a flash crash that recovers won't liquidate you, but a sustained crash will. See [Oracle staleness](/risks/oracle-staleness).

## Bad debt

If liquidation can't fully clear an underwater position — for example, in an extreme crash where the collateral value has fallen *below* the debt value — the protocol absorbs the loss as **bad debt**.

The over-collateralisation buffer (default 50%) is sized to absorb meaningful price moves before bad debt becomes possible. At the conservative governance floor (33% LTV with 200% buffer), simulation shows zero bad debt for crashes up to 50%. At the shipped 66.67% default, bad debt is bounded but non-zero in tail-event scenarios. See [Bad debt scenarios](/risks/bad-debt-scenarios).

## Where to go next

- [Debt-assumption liquidation](/features/debt-assumption-liquidation/overview) — the mechanism in depth
- [Health factor](/concepts/health-factor) — the trigger condition
- [Monitoring health](/using-the-protocol/monitoring-health) — practical tips
- [For keepers](/for-keepers/overview) — running a liquidator
