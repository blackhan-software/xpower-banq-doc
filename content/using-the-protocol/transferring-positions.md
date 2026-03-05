# Transferring positions

Both Supply and Borrow Positions are ERC20 tokens. You can transfer them — but the inversion of borrow semantics means borrow transfers behave differently from supply transfers.

## Supply transfers

Standard ERC20 push semantics:

- `transfer(to, amount)` — sender pushes value to `to`. Sender's balance decreases, `to`'s balance increases.
- `transferFrom(from, to, amount)` — same, but with allowance.

Health-factor implications:

- The **sender** must remain healthy after the transfer (their collateral decreased).
- The **receiver** doesn't need to be healthy (they're gaining collateral).

If the sender has any debt, the protocol verifies their post-transfer H ≥ 100% and reverts otherwise.

## Borrow transfers (inverted)

For Borrow Positions, semantics are inverted — the sender benefits, the receiver suffers:

- `transfer(from, amount)` — caller pulls debt from `from`. `from`'s debt decreases, **caller's** debt increases.
- `transferFrom(from, to, amount)` — pulls debt from `from` to `to`. Requires both parties to approve.

Health-factor implications:

- The **caller** (debt receiver) must remain healthy after the transfer.
- The **source** (debt sender) doesn't need to be healthy (their debt decreased — H rises).

The Pool contract bypasses approvals during liquidation, which is what enables debt assumption.

## Lock proportionality

If the position being transferred is partially locked, the lock fraction transfers proportionally. See [Transfers and exits](/features/locked-positions/transfers-and-exits) for the formula.

## When to use transfers

- **Wallet migration.** Move positions between wallets you control.
- **OTC trades.** Sell a position privately to a buyer.
- **Compose with another protocol.** Transfer position tokens into another DeFi product (with care — see [Wrapped positions](/using-the-protocol/wrapped-positions) for the safer path).

## When NOT to use transfers

- **Liquidation handover.** Don't try to "reroute" a liquidation by transferring out — the protocol's liquidation function operates on the address with H < 100%, and you'd need to make the transfer cause H ≥ 100%, which the protocol verifies. If you can do that with a transfer, you can probably do it with a regular operation.

## Where to go next

- [Wrapped positions](/using-the-protocol/wrapped-positions) — safer composition with non-Banq protocols
- [Positions as tokens](/concepts/positions-as-tokens) — the underlying mechanics
- [ERC20 semantics](/for-developers/erc20-semantics) — full developer-facing detail
