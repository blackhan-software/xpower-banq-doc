# Integration guide

How to integrate with XPower Banq from another smart contract or off-chain service.

## Common integration patterns

- **Yield aggregator.** Deposit to Banq, hold the Supply Position, redeem on user request.
- **Liquidation bot.** Watch positions for H < 100%, call `liquidate()` (PoW-gated public path) or `square()` (role-gated path).
- **Wallet UI.** Display position balances, perform supply/borrow/settle/redeem on user action.
- **Risk dashboard.** Read position state, oracle quotes, and protocol parameters; surface aggregate risk.

## Required reads

For most integrations, the minimum read set is:

- `Pool.healthOf(address user)` — health factor of an account.
- `Oracle.getQuote(uint256 amount, IERC20 source, IERC20 target)` — mid price of `amount` `source` in units of `target`. Use `getQuotes(...)` for bid/ask.
- `Position.totalOf(address user)` — supply or borrow balance (the index-aware total for a user; standard `balanceOf` is also available on the Position ERC20 surface).
- `Position.index()` — `(index_log, util_wad, dt)` triple: current log-index, vault utilization, and seconds since the last on-chain reindex. Utilization and interest accrue per side and per token, on the Position contract, not on Pool.
- `Position.model()` — the position's interest-rate model (per-side, per-token).

All of these are view functions — no gas, no state change.

## Required writes

For active integration (signatures from the `Pool` interface):

- `Pool.supply(IERC20 token, uint256 amount)` — supply. Overload `supply(address user, IERC20 token, uint256 amount, uint256 dt_term)` opens a locked position in one call.
- `Pool.borrow(IERC20 token, uint256 assets)` — borrow. Overloads accept `dt_term` and an `(IFlash flash, bytes data)` tail for flash-loan-backed borrows.
- `Pool.settle(IERC20 token, uint256 assets)` — repay.
- `Pool.redeem(IERC20 token, uint256 assets)` — withdraw.
- `Pool.lockSupply(IERC20 token, uint256 amount, uint256 dt_term)` / `Pool.lockBorrow(...)` — lock an existing supply or borrow position retroactively. `dt_term` is a seconds offset; pass `type(uint256).max` for a permanent lock.
- `Pool.rollSupply(IERC20 token, uint256 amount, uint256 dt_term)` / `Pool.rollBorrow(...)` — roll locked tokens from earlier slots into a later target slot.
- `Pool.square(address user, address victim, uint8 partial_exp)` — role-gated liquidation. The public `liquidate(victim, partial_exp)` wrapper is available behind the PoW gate, but only when the pool address itself holds its own `POOL_SQUARE_ROLE` (the `liquidate()` body ends with `this.square(...)`, so the role check applies to the pool). Granting/revoking that role from the pool toggles permissionless liquidations on/off **for that pool** (roles are per-pool).

All writes require ERC20 approvals where the protocol pulls tokens from your contract.

## Approval patterns

Use the standard `approve(spender, amount)` pattern. The protocol pulls tokens via `transferFrom` during deposits and settlements.

For positions you receive as ERC20s (Supply, Borrow), you can transfer them like any ERC20 — but remember the inverted direction for borrow positions.

## Events

Listen to (signatures match the `Pool` interface — see [Events and indexing](/for-developers/events-and-indexing) for the full listing):

- `Supply(user, token, amount, dt_term)`
- `Borrow(user, token, assets, dt_term, flash, data)`
- `Settle(user, token, assets)`
- `Redeem(user, token, assets)`
- `Liquidate(user, victim, partial_exp)` — `user` is the liquidator (caller).
- `LockSupply(user, token, amount, dt_term)` / `LockBorrow(user, token, amount, dt_term)`
- `RollSupply(user, token, rolled, dt_term)` / `RollBorrow(user, token, rolled, dt_term)`
- `Target(id, value, dt)` — emitted from the parameterised-governance contract on each parameter change (no separate propose/commit/veto).

Each event indexes `user` and (where applicable) `token` so you can filter per-account or per-asset.

## Common mistakes

- **Forgetting the lock-aware transfer.** Transferring a partially-locked position transfers the lock proportionally. If you assume the recipient gets unlocked tokens, you'll be surprised.
- **Mismatching index reads.** Always read `Pool.utilization()` and `Pool.rates()` together — they're consistent in the same call.
- **Pricing positions at NAV.** A locked position is *not* worth NAV — it's worth NAV × (1 − discount). Don't price secondary-market positions at NAV.

## Where to go next

- [Architecture overview](/for-developers/architecture-overview) — what each contract does
- [Events and indexing](/for-developers/events-and-indexing) — full event list
- [CLI and tools](/for-keepers/cli-and-tools) — the `banq-cli` reference
