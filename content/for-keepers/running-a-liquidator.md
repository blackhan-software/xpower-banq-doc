# Running a liquidator

Practical setup for an Banq liquidation bot.

## What you'll need

1. **An on-chain account** — usually a smart contract you control. Plain EOAs work but contracts give you more flexibility (atomic decision-making, custom slicing).
2. **Capital deposited as supply** — enough that you can absorb liquidation debts without dropping H below 100% yourself.
3. **`POOL_SQUARE_ROLE`** — granted via Acma, **per pool** (each pool's role is separate). Without it `square()` reverts; you can still call `liquidate()` (the public path) provided the **pool itself** also holds its own `POOL_SQUARE_ROLE` (governance's per-pool on/off switch for the permissionless path) and you can satisfy the per-`partial_exp` PoW gate.
4. **An off-chain monitor** — a process watching positions for H < 100% and submitting transactions when opportunities appear.
5. **Robust tx submission** — most production keepers use private mempools (Flashbots, MEV-Share) to avoid frontrunning.

## The decision loop

For each underwater position:

1. **Pick the slice.** Choose an exponent `e` (the protocol does not store a default — you pass it on every call). `e = 1` slices 50%, `e = 2` slices 25%, `e = 0` is a full liquidation that closes the position outright.
2. **Estimate the bonus.** At the H = 100% boundary with default weights, bonus ≈ `0.5 × debt_taken_value`. Strictly underwater, the realised bonus is smaller — it tracks the victim's live C/D ratio, not the boundary value. Subtract gas costs.
3. **Check your H post-liquidation.** Ensure post-tx H ≥ 100% with margin.
4. **Submit.**

For competitive cases, you may want to bid in a private mempool to win over other keepers.

## Sizing your position

A keeper running on a 100k XPOW supply with H ≥ 200% can absorb roughly 50k XPOW of additional debt before dropping to H = 100%. So per-liquidation, you can take on debts up to ~25k XPOW (a 50% slice — `e = 1` — with safety margin).

For larger positions, scale up your supply. Or use higher exponents (`e = 2` → 25% slice) to fit smaller bites. Because partial liquidation preserves the victim's H, you can repeatedly slice the same underwater position; nothing in the protocol forces you to take it in one bite.

## Locked-position absorption

If the victim has locked supply, you receive locked supply tokens — un-redeemable until the lock expires. This affects your real economics:

- You hold debt that accrues interest.
- You hold collateral you can't immediately redeem.
- Your effective return is the bonus minus the carry cost of the locked period.

For long-locked positions, the absorbed value can be negative if you can't sell the locked tokens. Some keepers refuse to liquidate fully-locked positions, leaving them for others.

## Failure modes

- **Frontrunning.** Another keeper sees the same opportunity and lands first. You pay gas for nothing.
- **H rebound.** The victim's H rises above 100% between your tx submission and inclusion (e.g., due to oracle price update). Your tx reverts.
- **Insufficient headroom.** Your post-tx H falls below 100%. The protocol rejects.
- **Lock economics.** You absorb a heavily-locked position and can't recover the bonus on the secondary market.

## Where to go next

- [Monitoring and tooling](/for-keepers/monitoring-and-tooling) — what to watch
- [PoW-gated public mode](/for-keepers/pow-gated-public-mode) — the alternative path
