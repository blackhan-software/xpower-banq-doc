# Architecture overview

XPower Banq's on-chain architecture is built around six core contract types: **Pool**, **Acma**, **Oracle**, **Supply Position**, **Borrow Position**, and **Vault**, plus an optional **WSupplyPosition** ERC4626 wrapper for supply positions and two supervised wrapper singletons — **Caps** and **Pols** — that add role separation around cap and POL operations.

![Architecture overview](../diagrams/architecture.svg)

## Pool

The orchestrator. All user-facing operations — supply, borrow, settle, redeem, liquidate, lock, unlock-on-expiry — go through Pool.

The Pool contract:

- Holds references to its Vault, Oracle, Acma, and Position contracts.
- Enforces health-factor invariants.
- Coordinates token movements.
- Implements the cap and lock logic.

A protocol deployment usually has multiple Pools — one per "market" (e.g., XPOW pool, APOW pool). Each pool has its own parameters.

## Vault (ERC4626)

The actual custodian of underlying tokens. Implements the ERC4626 standard, which means:

- `deposit`, `withdraw`, `mint`, `redeem` — standard interface.
- The vault's underlying balance is the pool's redeemable backing.

By using ERC4626, the vault is composable with any ERC4626-aware integration (vault aggregators, yield routers, etc.).

## Position contracts (Supply, Borrow)

Two ERC20 contracts per pool token. Each tracks a side of the market.

- **Supply Position.** Standard ERC20 with proportional lock transfer.
- **Borrow Position.** Inverted ERC20 with proportional lock transfer. Pool is privileged owner and can bypass approvals during liquidation.

Both maintain a global accumulating index, so balances grow with accrued interest without per-user updates.

## Oracle

Quotes prices and spreads. Implements log-space TWAP smoothing with `α = 0.944` decay (12-hour half-life).

The Oracle:

- Reads from enlistable sources. v10c uses AMM TWAPs; Chainlink-style feeds are also supported and can be enlisted later (subject to the standard `DELAY` window).
- Refreshes at most once per `LIMIT` (default 1 hour).
- Stores log-mid-price and log-spread for each supported asset pair.

## Acma (access control)

The role manager. Extends OpenZeppelin's `AccessManager` and adds the protocol's role-ID constants. Each privileged function is gated by a 64-bit role with three companions: a base role (caller), an `_ADMIN_ROLE` (grants/revokes the base role and configures its delay), and a `_GUARD_ROLE` (cancels pending operations within the delay window). Roles are **scoped per pool**: every role accessor takes the pool name (e.g. `POOL_SQUARE_ROLE("P007")`), so grants in one pool never grant access in another. Only `ACMA_RELATE_ROLE()` is global. See [Role hierarchy](/features/lethargic-governance/role-hierarchy) for the full taxonomy and the per-pool derivation.

## WSupplyPosition (optional)

A supply-side-only ERC4626 wrapper that strips the lock-aware-transfer feature for compatibility with non-Banq integrations. Only Supply positions are wrappable; there is no `WBorrowPosition`. See [Wrapped positions](/using-the-protocol/wrapped-positions).

## Caps (cap-limit wrapper)

A minimally-privileged singleton that wraps `Pool.capSupply`/`capBorrow` into delta-based `incSupply` / `decSupply` / `incBorrow` / `decBorrow` calls, each gated by its own ACMA role triple (`INC_SUPPLY`, `DEC_SUPPLY`, `INC_BORROW`, `DEC_BORROW` + admin/guard). Delta moves saturate at `0` and `2¹¹² − 1`. This is the surface the [circuit-breaker bot](/features/position-caps/caps-wrapper-and-circuit-breaker) uses to lower caps safely. See [Caps wrapper and circuit breaker](/features/position-caps/caps-wrapper-and-circuit-breaker).

## Pols (protocol-owned-liquidity wrapper)

A minimally-privileged singleton that wraps `Vault.fetchPol` into three progressively-permissioned `fetch` variants with a stored default `target` and `amount`, each guarded by its own ACMA role triple. This is the surface bots and operators use to extract [protocol-owned liquidity](/features/protocol-owned-liquidity/overview). See [Fetching and roles](/features/protocol-owned-liquidity/fetching-and-roles).

## Reading the contracts

- `Pool` — orchestration, health checks, cap function, liquidation logic.
- `Position` — abstract `Position` (`ERC20Permit`) plus the concrete `SupplyPosition` and `BorrowPosition` (inverted).
- `WPosition` — defines `WSupplyPosition` (the concrete `ERC4626` wrapper for supply positions) and `IWPosition` (the interface).
- `Vault` — `ERC4626` vault custodying the underlying ERC20; also hosts the POL surface (`pol`, `polFetchable`, `polFetched`, `fetchPol`).
- `Caps` — supervised wrapper for delta-based cap moves (`incSupply`/`decSupply`/`incBorrow`/`decBorrow`).
- `Pols` — supervised wrapper for POL fetching (`fetch` variants with stored target/amount).
- `Oracle` — log-space TWAP.
- `Acma` — access control (`AccessManager` extension with the protocol's role IDs).

The full source is at the project's GitHub repository (link in the footer).

## Where to go next

- [Contract addresses](/for-developers/contract-addresses) — per-network deployments
- [Integration guide](/for-developers/integration-guide) — how to compose with Banq
- [ERC20 semantics](/for-developers/erc20-semantics) — Position contract specifics
