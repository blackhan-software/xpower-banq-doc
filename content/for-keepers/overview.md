# For keepers

Keepers — also called liquidators — keep the protocol solvent by liquidating underwater positions. This section covers how to run a keeper on XPower Banq.

## What's different about Banq liquidation

The major difference: Banq liquidations are **debt-assumption**, not repayment. You don't need liquid stablecoins — you need collateral headroom.

This lowers the barrier to running a keeper. A user with a healthy supply position can liquidate other users without acquiring liquid capital.

## The two entry points

The Pool exposes two related selectors. They do the same liquidation; they differ in *who can call* and *what gating applies*:

| Selector | Caller | Gating | Notes |
|---|---|---|---|---|
| `liquidate(victim, partial_exp)` | Anyone | PoW (difficulty from `POW_SQUARE`) **and** the pool must hold its own `POOL_SQUARE_ROLE` | Public path. Internally invokes `this.square(...)`, so the role check inside `square` tests the pool itself. |
| `square(user, victim, partial_exp)` | Holder of that pool's `POOL_SQUARE_ROLE` | Role check (`restricted`) | Direct path. No PoW. |

Both end up at the same `_square` internals and emit the same `Liquidate` event. Authorised keepers typically call `square` directly to skip PoW; permissionless callers go through `liquidate`.

The `partial_exp` argument controls the slice — `2^-partial_exp` of the position. `partial_exp = 1` means a 50% slice, `partial_exp = 2` means 25%, etc. The PoW difficulty for the public path is configured per `partial_exp` value via `POW_SQUARE`, so governance can tune the difficulty of (e.g.) a public 50% slice independently from a public 25% slice.

Whether the permissionless `liquidate()` path is **available at all** is a **per-pool** governance switch: because the public path calls `this.square(...)`, `msg.sender` on the inner call is the pool address. Granting that pool's `POOL_SQUARE_ROLE` to the pool enables the public path; revoking it disables the public path while leaving direct `square()` calls by other role-holders unaffected. Roles are per-pool, so enabling public liquidations on one pool says nothing about the others. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

## Subsections

- **[Running a liquidator](/for-keepers/running-a-liquidator)** — production setup
- **[PoW-gated public mode](/for-keepers/pow-gated-public-mode)** — the permissionless path
- **[CLI and tools](/for-keepers/cli-and-tools)** — `banq-cli` (dry-run by default)
- **[Monitoring and tooling](/for-keepers/monitoring-and-tooling)** — keeper infrastructure
