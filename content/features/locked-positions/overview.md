# Locked positions

A **locked position** is one whose principal can't be moved out of the protocol until a chosen term elapses (or never, if you choose a permanent lock). In exchange, you earn an interest bonus (suppliers) or pay a reduced rate (borrowers).

Locked positions are XPower Banq's primary defence against liquidation cascades. They also create a secondary asset class — locked positions trade at a discount on the open market, which is itself a useful primitive.

## Why lock?

Three reasons, in roughly the order most users encounter them:

1. **Better rates.** Locked suppliers earn the bonus; locked borrowers pay the malus. At full lock, your effective spread compresses toward zero — the borrow rate approaches the gross rate, and the supply rate approaches U × the gross rate (still utilization-scaled).
2. **Cascade protection.** Aggregate locked positions reduce the protocol-wide cascade depth by factor (1 − ϕ), where ϕ is the locked fraction. Locking is a kind of public good — you protect everyone, including yourself.
3. **Strategic commitment.** If you're confident in your position over a fixed horizon, locking signals that to the protocol and earns you the bonus for it.

## Why not lock?

Two reasons:

1. **Reduced flexibility.** Once locked, your principal stays put. You can't redeem early. Your only exit is a transfer (or sale on the secondary market), and locked positions trade at a discount.
2. **You may want to repay early as a borrower.** If your strategy involves dynamic borrowing, locking your debt position can leave you stuck paying for capital you no longer need.

Locking is reversible only by the calendar. Choose terms you actually intend to commit to.

## Lock types at a glance

| Type | Term | Reversibility | Use case |
|---|---|---|---|
| **Timed lock** | 3 months to ~48 months | Auto-expires | Match a known holding period |
| **Permanent lock** | Forever | Never | Maximum cascade protection, maximum bonus |

See [Timed vs permanent](/features/locked-positions/timed-vs-permanent) for the details.

## What's actually locked

When you lock a position, only the **principal** is locked:

- **Locked supply:** you can't withdraw the principal. Accrued *interest* is freely redeemable.
- **Locked borrow:** you can't repay the principal early. Accrued *interest* can be settled at any time.

This means lock holders can still operate on margin and interact with their accruing yield without touching the locked stake itself.

## How the protocol pays for the bonus

Locked suppliers earn extra interest. Locked borrowers pay less. Both are good for users — but the protocol still has to balance its books.

The mechanism: the protocol's interest spread (default 10%) is the budget. The bonus comes out of that spread. At full lock adoption (everyone locked), the effective spread is zero — the borrow rate equals the gross rate R(U) and the supply rate equals U × R(U) (the supply side keeps its utilization scaling), and the protocol's margin disappears.

In practice, lock adoption fluctuates with utilization: it rises during stress (when cascade protection matters most and bonuses are juicy) and falls during calm (when protocol margin is preserved). See the [Nash equilibrium analysis](/research/papers/theory-and-proofs) in the theory paper for the formal version.

## Subsections

- **[Timed vs permanent](/features/locked-positions/timed-vs-permanent)** — what each type does and when to pick which
- **[Bonus and malus](/features/locked-positions/bonus-and-malus)** — the rate adjustments in detail
- **[Transfers and exits](/features/locked-positions/transfers-and-exits)** — how to move or exit a locked position
- **[Cascade protection](/features/locked-positions/cascade-protection)** — the systemic benefit
