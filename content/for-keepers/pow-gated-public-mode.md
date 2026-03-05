# PoW-gated public mode

`Pool.liquidate(victim, partial_exp)` is **always** callable by anyone — it's a permissionless `external` function. But the call only succeeds if governance has given the pool the right to internally invoke the otherwise permissioned `square` function. Concretely: `liquidate()` ends with `this.square(msg.sender, victim, partial_exp)`, and `msg.sender` for that internal call is the pool address itself. The role check on `square()` therefore tests the *pool*, not the external caller. Granting that pool's `POOL_SQUARE_ROLE` to the pool **enables** the permissionless path; revoking it **disables** the permissionless path while leaving direct `square()` calls by other role-holders unaffected. Because roles are scoped per pool, this on/off switch is per pool — each pool's public-liquidation path is governed independently.

Layered on top of that on/off switch, governance controls how *expensive* the call is, via the `POW_SQUARE` parameter (per `partial_exp`). When `POW_SQUARE` is high, the public path becomes prohibitively expensive and only role-holders (calling `square` directly) liquidate in practice. When `POW_SQUARE = 0`, the PoW gate is disabled and anyone can liquidate freely — provided that pool still holds its own `POOL_SQUARE_ROLE`.

The PoW gate exists for cases where:

- The set of that pool's `POOL_SQUARE_ROLE` holders is too small or too centralised.
- Specific liquidations aren't being picked up by authorised keepers.
- Governance wants to widen liquidation access during stress.

## How the gate works

Internally `liquidate(victim, partial_exp)` is annotated with `powlimited(liquidateDifficultyOf(partial_exp))`. The `powlimited` modifier:

1. Looks up the per-`partial_exp` difficulty `D = parameterOf(POW_SQUARE_ID(partial_exp))`.
2. If `D > 0`, computes `key = keccak256(blockHash, tx.origin, msg.data)` against a recently cached block hash.
3. Counts the leading zero *bits* of `key`. If fewer than `D`, reverts with `PowLimited(key, D)`.
4. Otherwise the call proceeds and `liquidate` invokes `this.square(msg.sender, victim, partial_exp)`.

Notes:

- The PoW input includes `tx.origin` and the full `msg.data`, so the puzzle is bound to a specific caller and a specific (victim, `partial_exp`) target.
- The block hash is cached and refreshed only after `cacheTime`, so a successfully mined nonce is reusable for a window — the puzzle isn't tied to a single block, but it does become invalid after the cache rolls over.
- The "difficulty" is a count of *leading zero bits* in the hash (so `D = 16` means roughly 1 in 65 536 attempts).

## Why PoW?

PoW's primary purpose is to introduce weak *entropy* (i.e. randomness) into the liquidation process, to _reduce_ liquidator centralization (if governance chooses so). Without that randomness, the permissionless path collapses into a priority-gas auction — the fastest, best-tuned bot wins every race and a small oligopoly captures every liquidation, mirroring the MEV-centralization pattern already visible on existing lending markets. Because mining is probabilistic, no single bot can deterministically win on latency and gas-bid alone; governance tunes `POW_SQUARE` per `partial_exp` to widen the field (higher difficulty, more randomness) or favor speed (lower difficulty, faster reaction).

A secondary, incidental effect is that the puzzle makes spamming `liquidate` against still-healthy victims more expensive — but gas already discourages that (the caller pays for the supervisor pre-check before any revert), so spam-resistance is a side benefit rather than the motivation.

## Computing the PoW

The puzzle is small — a few seconds of CPU at default difficulty. A keeper can mine off-chain and submit the result with the call. The `banq-cli` `liquidate` command bundles the mining step automatically (use `-Y` / `--broadcast` to actually submit). See [CLI and tools](/for-keepers/cli-and-tools).

## Failure modes

Same as `square()`, plus:

- **Insufficient PoW.** The on-chain check sees fewer leading zeros than `POW_SQUARE` requires and reverts with `PowLimited(key, D)`.
- **Stale PoW.** The cached block hash rolled over after your nonce was mined — re-mine against the new hash.
- **Permissionless path disabled.** If governance has not (or no longer has) granted that pool's `POOL_SQUARE_ROLE` to the pool address, the inner `this.square(...)` reverts on the role check and the whole `liquidate()` call fails — regardless of the PoW.

## Where to go next

- [Running a liquidator](/for-keepers/running-a-liquidator) — production setup
- [Debt-assumption liquidation](/features/debt-assumption-liquidation/overview) — the underlying mechanism
- [CLI and tools](/for-keepers/cli-and-tools) — `banq-cli liquidate`
