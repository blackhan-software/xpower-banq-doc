# Wrapped positions

The optional **WSupplyPosition** wrapper (interface `IWPosition`) is an **ERC4626 vault** over an XPower Banq *Supply* Position. It exposes a strictly-standard ERC20 share token plus the ERC4626 deposit/redeem surface — useful for composability with protocols that don't understand the lock-aware transfer mechanics of native Supply positions.

Only supply positions can be wrapped. There is no `WBorrowPosition` — borrow positions stay in their native, inverted-ERC20 form.

## Why a wrapper?

Standard ERC20 expects:

- `transfer(to, amount)` always pushes value to `to`.
- No additional checks beyond `balanceOf` arithmetic.

A native XPower Banq Supply position has a **lock-aware transfer** that moves the lock fraction proportionally. Most integrations don't model that hidden state — they'd see the transfer succeed but later be surprised that some fraction of what they hold is non-redeemable.

`WSupplyPosition` shields other protocols from this by routing entry and exit through the standard ERC4626 surface. The share token itself is plain ERC20: no inverted direction, no hidden lock-aware transfer hook.

## How it works

`WSupplyPosition` inherits OpenZeppelin's `ERC4626` and overrides only `decimals()` and `totalAssets()` — everything else (deposit / mint / withdraw / redeem / convertToShares / convertToAssets / preview*/max*) is the standard OZ surface.

- **Wrap by depositing the underlying Supply position.** Call `WSupplyPosition.deposit(assets, receiver)` (or `mint(shares, receiver)`) — the wrapper pulls native Supply Position tokens from `msg.sender` (subject to the usual ERC20 approval) and mints `WSupplyPosition` shares to `receiver`. Shares correspond to assets at a parity that evolves with the underlying position's index over time.
- **Unwrap by redeeming the shares.** Call `WSupplyPosition.redeem(shares, receiver, owner)` (or `withdraw(assets, receiver, owner)`) — the wrapper burns `WSupplyPosition` shares and releases the underlying Supply position tokens to `receiver`.

## When to wrap

- **Using as collateral in another protocol.** Many DeFi protocols accept ERC20 (or ERC4626) collateral. `WSupplyPosition` is the safe form.
- **Trading on AMMs.** Most AMM pools assume standard ERC20.
- **Distributing to non-aware contracts.** Reward systems, vesting contracts, etc.

## When NOT to wrap

- **You want to actively redeem or settle the underlying position.** `WSupplyPosition` has no redemption against the Pool — you must `redeem` shares back into the native Supply position first, then `Pool.redeem(...)` to withdraw the underlying asset.
- **You're transferring within Banq.** Native positions transfer correctly within the protocol.
- **You hold a borrow position.** Borrow positions are not wrappable; there is no `WBorrowPosition`.

## Locks and the wrapper

Wrapping does not change the underlying lock state. Deposited locked tokens remain locked in the underlying Supply position — the wrapper-share holder cannot redeem the locked portion until the underlying lock expires.

In other words: the wrapper normalises the *transfer* surface to plain ERC4626, but it cannot unlock liquidity that isn't there.

## Where to go next

- [Positions as tokens](/concepts/positions-as-tokens) — the native semantics
- [ERC4626 vaults](/for-developers/erc4626-vaults) — the standard reference
- [Integration guide](/for-developers/integration-guide) — composing with Banq
