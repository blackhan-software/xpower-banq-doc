# How liquidations work

The detailed call flow for a debt-assumption liquidation. This page is for developers, keepers, and anyone curious about the on-chain mechanics.

## The call

A liquidation is a single call to either `liquidate(victim, partial_exp)` (public, PoW-gated by `POW_SQUARE`) or `square(user, victim, partial_exp)` (role-restricted to that pool's `POOL_SQUARE_ROLE`):

- `victim`: the address of the underwater account.
- `partial_exp`: an integer `e ≥ 0`. The slice taken is `2^-e` of the position. The caller chooses `e` on every call — there is no protocol-stored default. `e = 1` slices 50%, `e = 2` slices 25%, `e = 0` is a full liquidation.
- `user` (only on `square`): the address that absorbs the debt and collateral. Must be `msg.sender` or the pool itself.

When invoked through the public `liquidate` path, the pool routes the call internally to `this.square(msg.sender, victim, partial_exp)`, so the original external caller ends up as the absorbing `user`. Because that internal hop is an *external* call back into the same contract, `msg.sender` on the inner `square()` is `address(this)` — the pool. The `restricted` modifier on `square()` therefore tests whether the **pool address itself** holds its own `POOL_SQUARE_ROLE`. That single role grant is the **per-pool** on/off switch governance uses for the permissionless `liquidate()` path: granted → public path enabled for that pool; revoked → public path reverts on the role check, while direct `square()` calls from other role-holders keep working.

## The slice

The protocol computes the slice via right-shift:

```
debt_taken = victim.borrow >> exponent
collateral_taken = victim.supply >> exponent
```

So:

- e = 0 → full position (100%)
- e = 1 → half (50%)
- e = 2 → quarter (25%)
- e = N → 1/2^N

The right-shift is per-token if the victim has positions in multiple supply or borrow tokens — every position is sliced uniformly by the same factor.

## Atomic transfer

Within a single transaction, the protocol:

1. Decrements the victim's borrow position by `debt_taken`.
2. Increments the liquidator's borrow position by `debt_taken`.
3. Decrements the victim's supply position by `collateral_taken`.
4. Increments the liquidator's supply position by `collateral_taken`.

This is a four-way state change happening atomically. The Pool contract is the privileged owner of both Position contracts and bypasses normal approval requirements.

## Health checks

Two health checks bracket the operation:

1. **Pre-check on victim.** The protocol verifies the victim is actually underwater (H < 100%). If they're solvent, the call reverts with `Healthy(victim)`.
2. **Post-check on liquidator.** After the transfer, the protocol verifies the liquidator's health factor is ≥ 100%. If they would become underwater, the call reverts with `Unhealthy(liquidator)`.

The post-check is what makes debt assumption safe. A liquidator who can't absorb the debt without becoming underwater themselves is rejected.

There is **no post-check on the victim**, and no need for one: because `_square` shifts both `borrowed` and `supplied` by the same `partial_exp`, the slice is uniform. For any `partial_exp ≥ 1` (partial liquidation), the victim's H is preserved exactly:

$$
H_\text{victim, after} \;=\; \frac{\alpha \cdot S \cdot (1 - 2^{-e})}{B \cdot (1 - 2^{-e})} \;=\; \frac{\alpha \cdot S}{B} \;=\; H_\text{victim, before}
$$

So a partial liquidation never moves the victim's H — it just shrinks the position. The position stays liquidatable until either H recovers or a `partial_exp = 0` call closes it entirely (after which both sides are zero and H is undefined).

## Lock propagation

If the victim has locked supply or borrow positions, the locks transfer proportionally:

- The liquidator receives **locked** supply tokens (with the same lock terms).
- The liquidator's borrow position inherits the **locked** debt.

This is the same proportional-transfer mechanism as a normal user-initiated transfer. See [Transfers and exits](/features/locked-positions/transfers-and-exits).

## What happens to the vault?

Nothing. The vault's underlying token balances don't change during a liquidation. Only the position-token accounting changes.

This is a key efficiency: the protocol doesn't need to broker liquid capital. The actual underlying tokens stay where they are.

## Choosing the exponent

The exponent is up to the liquidator. Higher e (smaller slice) means:

- Less collateral committed (smaller post-liquidation H impact on the liquidator).
- Less debt absorbed (smaller share of the bonus).
- The remaining position can be liquidated again by the same or another liquidator.

Lower e (bigger slice) means:

- More commitment, more bonus capture.
- One-shot — the position is largely cleared.

In a cascade, optimal e depends on remaining keeper headroom and the depth of the queue. Sophisticated keepers will solve a small optimisation: what slice maximises expected profit given competing keepers and continued price movement?

## What happens if the post-check fails

The whole transaction reverts. The keeper has paid gas but nothing else has happened. They can try again with a smaller slice (higher e), or skip and let another keeper take it.

There's no partial liquidation that "almost works." The post-check is binary.

## What happens if the price moves during the transaction

It can't, in any meaningful sense — the liquidation happens within a single transaction, atomically. The oracle price used is the value cached at the most recent oracle refresh, which can be up to the LIMIT period stale. This is by design (it's what makes flash-loan manipulation hard) but it does mean a liquidation might get triggered against a position whose true price has already recovered.

This is one of the trade-offs of TWAP oracles. See [Oracle staleness](/risks/oracle-staleness).

## Gas costs

From the whitepaper benchmarks (Foundry, optimizer ON):

| Operation | Banq | Aave V3 |
|---|---|---|
| Liquidation (full) | 298,882 | 389,059 |
| Liquidation (16 slots) | 6,746,024 | n/a |

The 16-slot case is a worst-case scenario where the victim has all 16 ring-buffer lock slots active. In practice, most liquidations are far cheaper.

## Where to go next

- [For liquidators](/features/debt-assumption-liquidation/for-liquidators) — running a keeper bot
- [Liquidation](/concepts/liquidation) — the borrower's perspective
- [PoW-gated public mode](/for-keepers/pow-gated-public-mode) — when permissionless liquidation is enabled
