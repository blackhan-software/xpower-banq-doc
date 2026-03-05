# Supplying assets

Supplying tokens to a pool is the simplest operation in XPower Banq. You deposit, you earn interest, and you receive a Supply Position ERC20 representing your claim.

## What you'll do

1. Choose a pool and a supported token.
2. Approve the protocol to spend that token from your wallet (one-time per token, until the approval is exhausted or revoked).
3. Call the supply function with an amount.

## What the protocol does

In the same transaction:

1. Pulls your tokens into the vault.
2. Mints a corresponding amount of Supply Position tokens to your address.
3. Updates the global supply index to capture interest accrued since the last interaction.
4. If your new balance crosses *from below* one whole token unit to *at-or-above* it for the first time, increments the protocol-wide `largeHolders()` counter by 1 (which slightly tightens *every* user's cap going forward).

The Supply Position ERC20 you receive earns interest continuously. You don't need to claim — your `balanceOf` will grow over time.

## Fees and slippage

- **Entry fee** of 0.1% by default. The fee is deducted from the supplied amount before minting.
- **No slippage** — supplying doesn't trade through any pool, just changes accounting.

## Locked supply

If you pass a non-zero `dt_term` parameter, the protocol locks a portion of your principal for the specified term. See [Locking positions](/using-the-protocol/locking-positions).

## Cap considerations

Your maximum supply per operation is capped by the [position cap function](/features/position-caps/overview). If you try to supply more than the cap allows, the call reverts with a cap error. For most users, the cap floor is generous enough that this isn't a concern; for whales, the cap may require splitting deposits across multiple operations.

## What you can do with your supply position

- **Earn interest passively.** Just hold the tokens. Your balance grows.
- **Borrow against it.** Supplied tokens count toward your collateral.
- **Transfer it.** Send the position tokens to another address; they become the supplier.
- **Lock it later.** You can lock an existing supply position retroactively. Most users supply unlocked first, then decide whether to lock.
- **Wrap it.** For composability with other DeFi protocols, see [Wrapped positions](/using-the-protocol/wrapped-positions).

## Reading your balance

`balanceOf(you)` on the Supply Position contract returns your current claim — principal plus accrued interest. It's a view function, free to call.

You can also call `totalOf(you)` for the same value, plus a breakdown into principal and accrued portions.

## Where to go next

- [Borrowing assets](/using-the-protocol/borrowing-assets) — borrow against your supply
- [Withdrawing assets](/using-the-protocol/withdrawing-assets) — exit your position
- [Locking positions](/using-the-protocol/locking-positions) — lock for the bonus
