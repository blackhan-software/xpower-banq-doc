# For liquidators

A short orientation for users thinking about running a liquidation bot. The deeper how-to lives in [For keepers](/for-keepers/overview); this page is the conceptual primer.

## What you need

- A position on the protocol with **healthy collateral headroom** — enough that you can absorb the debt of a liquidation without dropping your own H below 100%.
- An off-chain monitoring system watching positions for H < 100%.
- An on-chain account holding that pool's `POOL_SQUARE_ROLE` (for direct `square` calls) or the ability to mine the PoW puzzle (for the public `liquidate` path).

You do **not** need:

- Liquid stablecoins or any specific asset to repay debt.
- A flash-loan integration.
- Pre-deposited capital in a stability pool.

## The economics

At the H = 100% boundary, you take on debt of value $D$ and receive collateral of value $D × (255/170) = D × 1.5$ — the implicit 50% bonus, captured in collateral. Strictly underwater (H < 100%), the realised bonus is smaller: uniform slicing seizes collateral in proportion to the victim's live C/D ratio, which is below 1/α once H drops below 100%. The "boundary 50%" is the upper bound; the closer to bad-debt territory you let the victim drift, the less you make on the call.

The catches:

- **Your post-liquidation H must remain ≥ 1.** This caps how much debt you can absorb in any single liquidation.
- **If the absorbed position is locked**, you can't immediately redeem the collateral. You'll need to wait or sell at a discount.
- **Gas costs.** A simple liquidation is ~300k gas; a worst-case (16-slot lock) liquidation is ~6.7M gas.
- **No protocol-stored slice default.** You pass `partial_exp` on every call. Because partial liquidation preserves the victim's H, the position remains liquidatable after each slice — you can size the bite to your headroom rather than feeling forced into one big call.

In practice, most keepers run a position roughly 2–3× the size of the average liquidation they expect to capture, with conservative H targeting (≥ 2.0) so they're not themselves liquidatable.

## Two paths

`square()` is role-restricted (that pool's `POOL_SQUARE_ROLE`) and free of PoW. `liquidate()` is public but pays a per-`partial_exp` PoW cost from the `POW_SQUARE` parameter — and only works when the **pool address** itself holds its own `POOL_SQUARE_ROLE`, since the public path ultimately runs `this.square(...)` and the role check applies to the pool, not to the external caller. Granting or revoking that role from the pool is governance's **per-pool** on/off switch for permissionless liquidations. Most production keepers will use `square()` directly; `liquidate()` is the permissionless alternative for callers without the role, when governance has enabled it for the pool.

See [Running a liquidator](/for-keepers/running-a-liquidator) for the production setup.

## What to read next

- [How liquidations work](/features/debt-assumption-liquidation/how-liquidations-work) — the on-chain call flow
- [Running a liquidator](/for-keepers/running-a-liquidator) — production setup
- [PoW-gated public mode](/for-keepers/pow-gated-public-mode) — the permissionless path
