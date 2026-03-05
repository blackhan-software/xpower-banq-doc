# How caps grow

The cap function `12λ(1−λ)² · C_max / √(n+2)` is dynamic. It depends on:

- **λ**, your current share of the position's total supply — i.e. `balanceOf(you) / totalSupply()`.
- **n**, the protocol-wide count of *large holders* in the position — i.e. addresses currently holding **at least one whole token unit**. Computed on-chain by `Position.largeHolders()` (the max of the live count and the governance parameter `MIN_HOLDERS_ID`). The parameter defaults to `0` at construction — `Constant.MIN_HOLDERS` (1e18) is only the governance ceiling.
- **C_max**, the absolute pool cap (governance parameter `CAP_ID`), and **S**, the position's total supply, which both move as others deposit and withdraw.

As any of these change, your effective cap moves too. This page covers the dynamics.

## Holder-count semantics

`n = largeHolders()` is a **global** counter, not a per-user iteration count. It increments when an address crosses **from below one whole token unit** to **at-or-above one unit** (`Position::_update` tracks `+1` on cross-up, `−1` on cross-down). The floor is `MIN_HOLDERS_ID` so caps don't blow up in an empty pool.

What this means in practice:

- **Your own operations don't directly raise `n`** unless they push *your* balance through the unit threshold. Trickling small amounts in or out of an already-large balance leaves `n` unchanged.
- **New users coming in raise `n`** once their balance crosses the unit threshold. Each new large holder shrinks every existing user's cap by an additional `√(n+2) → √(n+3)` factor.
- **`n` can shrink.** When a large holder's balance drops back below one unit (full redemption, lock transfer that brings them under, etc.) the count ticks down — and remaining users' caps loosen accordingly.

There is no separate per-user counter, no reset mechanism for any per-user state, and no governance lever to clear `n` — it's a direct read of the population of large holders, floored by `MIN_HOLDERS_ID`.

## What "growing the cap" requires

To increase the absolute size of your position over time, you need:

1. **Pool growth.** As `S` rises, the absolute cap `λ · C_max` rises, even at fixed `λ`.
2. **Avoiding the 1/3 peak.** The beta factor `12λ(1−λ)²` peaks at `λ = 1/3`. Past that point, *adding* more share *shrinks* your incremental mint room; you can't meaningfully grow past 1/3 of the pool through normal supply/borrow operations.
3. **Tolerating a growing `n`.** As more users join the position, `√(n+2)` increases and divides everyone's cap down. There's no individual workaround for this.

## Can `n` be reset?

No — and there's nothing to reset on a per-user basis either. `n` reflects the *current* population of large holders; the only way it falls is if some large holder reduces their balance below one unit. There is no governance call (privileged or otherwise) that zeroes `n` or affects any per-user state in the cap formula.

## Sybil dynamics

If you split a balance across `k` Sybil addresses, each one above the unit threshold raises `largeHolders` by 1. So `n` increases by roughly `k`, and the cap divisor goes from `√(n+2)` to `√(n+k+2)`. The aggregate mint room across all `k` Sybils is:

$$
\sum_{i=1}^k \text{cap}(\lambda_i) \;\le\; \frac{C_\text{max}\,\sum_i 12\lambda_i(1-\lambda_i)^2}{\sqrt{n+k+2}}
$$

Splitting reduces each `λ_i`, which moves each one toward the favorable side of the `12λ(1−λ)²` curve (peak at `λ = 1/3`), but the shared `√(n+k+2)` divisor grows. The net Sybil advantage scales as `O(√k)` — sublinear in the number of fake addresses, which is the point of the mechanism.

This is why the design is called Sybil **rate-limiting** rather than Sybil prevention. Splitting capital across more addresses *does* let an attacker accumulate share faster than from a single address, but the gain shrinks per address as `k` grows.

## Where to go next

- [New user allocation](/features/position-caps/new-user-allocation) — your starting cap on a fresh address
- [Risks → Smart contract risk](/risks/smart-contract-risk) — the limits of what caps can do
