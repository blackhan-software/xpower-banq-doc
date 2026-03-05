# Oracle staleness

The TWAP oracle smooths prices over time. This is a deliberate security choice — it makes flash-loan manipulation infeasible — but it has a cost.

## The cost: a 2+ hour blind window

In a fast price move, the oracle's reported price lags the true market by hours.

For default parameters (HL = 12 hours, refresh = 1 hour):

- **First oracle update after the move:** the new sample enters the EMA with weight `(1 − α) ≈ 5.6%`. The reported price has moved ~5.6% of the way to the new spot.
- **After ~12 hours:** the reported price is roughly halfway to the new spot (`1 − α¹² ≈ 50%` — the definition of the 12-hour half-life).
- **After ~24 hours:** the reported price is ~75% of the way (`1 − α²⁴ ≈ 75%`).
- **After ~40 hours:** the reported price is ~90% of the way (`1 − α⁴⁰ ≈ 90%`) — matching paper 001's "approximately 40 hours of sustained manipulation achieves 90% price deviation".

So a 30% spot crash takes ~12 hours to be roughly half-reflected and ~40 hours to be ~90% reflected.

## What this means for borrowers

During a crash:

- Your H, computed against the lagged oracle, is **higher than your true H** based on instantaneous prices.
- You won't be liquidated immediately when the spot price crashes.
- The oracle eventually catches up. By then, you may face a liquidation against the catch-up.

This is *good* for you in flash-crash-and-recover scenarios — you survive, the oracle never updates to the dip. It's *bad* for you in sustained crashes — the oracle eventually liquidates you against an oldish reference price.

## What this means for suppliers

The same lag protects the pool from instantaneous bad debt. Liquidations occur against the slower-moving oracle, not the instantaneous spot. This gives keepers time to react and reduces the chance of cascading losses.

## What the buffer is for

The 50% over-collateralisation buffer is sized to absorb up to ~50% of "blind spot" — i.e., if collateral instantaneously crashes 50% before the oracle catches up, the buffer is enough that the protocol can still liquidate without bad debt.

For deeper crashes (60%+ instantaneous), the buffer can be exceeded. See [Bad debt scenarios](/risks/bad-debt-scenarios).

## Mitigations

- **Use conservative LTV.** The 33% conservative floor (vs the 66.67% default) doubles the buffer, making bad-debt-from-staleness essentially impossible.
- **Run high H.** A higher H gives you headroom against the catch-up move.
- **Trust the slow oracle.** The protocol is *designed* for this. Trying to game the oracle or pre-empt it usually loses money.

## Where to go next

- [Bad debt scenarios](/risks/bad-debt-scenarios) — what happens when staleness exceeds the buffer
- [Manipulation resistance](/features/twap-oracle/manipulation-resistance) — why the oracle is slow
- [Pool parameters](/parameters/pool-parameters) — LTV and BUFFER defaults
