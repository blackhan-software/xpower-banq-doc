# Transfers and exits

Locked positions can't be redeemed (supply) or settled (borrow) until the lock expires. But you have other ways out: **transfers** and **secondary-market sales**. This page covers both.

## The two ways to exit a lock early

1. **Wait it out.** Timed locks expire automatically. Permanent locks never do.
2. **Transfer.** Move the position to another address — your own or a buyer's. The lock follows.

Anything else (forced redemption, governance unlock, expiration override) is **not** supported. Locks are a credible commitment.

## Transferring a locked position

A locked Supply Position transfers like a regular ERC20 — the lock fraction transfers proportionally.

If you have 100 supply tokens with 60 locked, and you transfer 50 to Bob:

- Bob receives 50 tokens with 30 locked (60% lock ratio).
- You retain 50 tokens with 30 locked (60% ratio preserved).

The recipient inherits the lock; they can't redeem the locked portion until the original term expires.

For Borrow Positions, the [inverted semantics](/concepts/positions-as-tokens) apply: `transfer(from, amount)` *pulls* the debt **from** `from`, with both parties needing to approve. The lock fraction transfers proportionally just as with supply.

## Selling on a secondary market

Because locked positions are ERC20 tokens, they can be sold on secondary markets. A buyer who acquires your locked supply receives a position that earns interest but can't be redeemed until the lock expires.

Naturally, locked positions trade at a **discount** to their NAV. The discount reflects:

- Inability to redeem for the underlying (locked principal stays put).
- Time-value of the locked period.
- Secondary market liquidity (thinner = larger discount).

Empirically, comparable products (Lido stETH during stress, Convex cvxCRV) have traded at 3–12% discounts. XPower Banq locked positions are expected to fall in a similar range, with the discount tightening as adoption grows and market depth improves.

## What this means in practice

The discount creates a real economic tradeoff:

- **Lock and hold:** earn the bonus, accept the illiquidity.
- **Lock and sell:** earn the bonus until you sell, take the discount on exit.
- **Don't lock:** earn the lower rate, retain full liquidity.

The breakeven horizon — how long you need to hold the lock for the bonus to compensate the discount — is roughly D / Δr, where D is the secondary-market discount and Δr is the APY differential. At default parameters, this is several years in calm markets and under a year in stressed markets. See [the theory paper](/research/papers/theory-and-proofs) for the formal analysis.

## Liquidation and locked positions

A liquidation can take a slice of your locked position. The lock transfers proportionally to the liquidator: they receive locked supply tokens, with the lock fraction preserved.

This is the core mechanism behind cascade attenuation — liquidators can't immediately dump locked collateral on the open market. They have two options: hold the locked tokens until expiry, or sell them at a discount on the secondary market. Either way, the locked portion doesn't generate immediate spot-market sell pressure.

In practice, liquidators prefer unlocked positions for the immediate liquidity. This creates de-facto **liquidation seniority** for locked positions — they get hit later in a cascade, not earlier.

## Permanent locks: there is no exit

Permanent locks have no expiry. The only way to part with permanent-locked tokens is to transfer them to another address.

If no one wants to buy them at any price, you're stuck with them — earning interest, but unable to redeem the principal. This is the explicit deal: you trade redemption rights for the maximum bonus and the strongest cascade-protection contribution.

::: warning Don't permanently lock more than you can afford to lose access to
This sounds dramatic, but it's the realistic framing. Permanent means permanent. If your circumstances change in 5 years, the protocol won't accommodate you.
:::

## Where to go next

- [Locking positions](/using-the-protocol/locking-positions) — how to create a lock
- [Transferring positions](/using-the-protocol/transferring-positions) — the practical mechanics
- [Secondary market risk](/risks/secondary-market-risk) — what could go wrong with the discount
