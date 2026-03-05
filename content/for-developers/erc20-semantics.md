# ERC20 semantics

XPower Banq's Position contracts implement ERC20, but the Borrow Position inverts the direction. This page is the precise specification.

## Supply Position (standard ERC20)

Behaviour matches OpenZeppelin's reference ERC20, with the following additions:

- **Index-aware balances.** `balanceOf(account)` returns principal × (current_index / account_index). Balance grows with interest accrual.
- **Proportional lock transfer.** `transfer` and `transferFrom` move the lock fraction proportionally.
- **Health check on sender.** If the sender has any debt, post-transfer H must be ≥ 100%.

## Borrow Position (inverted ERC20)

Inverted direction. The semantics:

- `balanceOf(account)` returns the account's *debt* — what they owe.
- `transfer(from, amount)` moves debt **from** `from` to **the caller**. The caller's debt increases. The source's debt decreases. The naming is unusual: think of it as "I'm pulling debt from you."
- `transferFrom(from, to, amount)` moves debt from `from` to `to`. Both parties must approve.
- **Health check on receiver.** Post-transfer, the debt receiver must have H ≥ 100%.

The protocol bypasses approvals when the caller is the Pool contract — this is what enables debt-assumption liquidation.

### Why inverted?

Because debt has inverted utility. Pushing debt from sender to receiver harms the receiver. Standard ERC20 push semantics would let anyone dump debt onto unwilling counterparties. Pull semantics with two-sided approval makes debt transfers genuinely consensual.

## Common operations

### Read your supply

```solidity
uint256 myBalance = supplyPosition.balanceOf(msg.sender);
```

### Transfer your supply

```solidity
supplyPosition.transfer(recipient, amount); // standard ERC20 transfer
```

### Read your debt

```solidity
uint256 myDebt = borrowPosition.balanceOf(msg.sender);
```

### Take on someone else's debt (with approval)

```solidity
// Source has previously called: borrowPosition.approve(msg.sender, amount);
borrowPosition.transfer(source, amount); // pull debt FROM source TO caller (msg.sender)
```

### Read aggregated state

```solidity
uint256 supplyAccountIndex = supplyPosition.indexOf(account);
uint256 supplyGlobalIndex = supplyPosition.index();
```

## Decimals

Position tokens have decimals matching the underlying asset, with a minimum of 6. So a XPOW supply position has 6 decimals; a WAPOW supply position has 18.

## Names and symbols

The standard `name()` and `symbol()` strings are derived from the underlying token's `name()` and `symbol()`, plus the "buddy" token of the pool pair:

- **Supply name:** `"<token.name()> Supply"` — e.g. an XPOW supply position renders as `"XPower Supply"`.
- **Supply symbol:** `"s<TOKEN>:<BUDDY>"` — e.g. `"sXPOW:USDC"` for the XPOW side of an XPOW/USDC pool.
- **Borrow name:** `"<token.name()> Borrow"` — e.g. an XPOW borrow position renders as `"XPower Borrow"`.
- **Borrow symbol:** `"b<TOKEN>:<BUDDY>"` — e.g. `"bUSDC:XPOW"` for the USDC side of an XPOW/USDC pool.

Two special-cases apply (see the `Position` constructors):

- The native **APOW/XPOW pair** collapses to a single-token suffix: `sAPOW` / `sXPOW` (not `sAPOW:XPOW`) and likewise `bAPOW` / `bXPOW`.
- **`WAVAX` is renamed to `AVAX`** in either side of the pair: e.g. `sAVAX:APOW` rather than `sWAVAX:APOW`.

## Where to go next

- [Positions as tokens](/concepts/positions-as-tokens) — conceptual overview
- [Architecture overview](/for-developers/architecture-overview) — the broader contract picture
