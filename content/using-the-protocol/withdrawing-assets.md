# Withdrawing assets

To exit your supply position (or reduce it), you **redeem**. The protocol burns your Supply Position tokens and returns the corresponding underlying tokens from the vault.

## What you'll do

1. Call the redeem function with an amount (or `MAX_UINT256` for the full balance).

## What the protocol does

In the same transaction:

1. Verifies your post-redeem health factor would still be ≥ 100% (if you have debt). If you have no debt, no health check.
2. Burns the corresponding Supply Position tokens.
3. Transfers the underlying tokens from the vault to your wallet.
4. Deducts the exit fee (default 1%).
5. Updates the global supply index.
6. If the burn drops your Supply Position balance back below one whole token unit (when it had been at-or-above), decrements the protocol-wide `largeHolders()` counter on the Supply Position.

## Fees

- **Exit fee** of 1% by default. Deducted from the redeemed amount before transfer.
- No slippage.

## Locked supply

If your supply is locked, you cannot redeem the principal until the lock expires. You **can** still redeem accrued *interest* — interest is always redeemable.

For permanent locks, the principal is redeemable... never. The exit path is transfer or sale, not redemption.

## Health factor constraint

If you have any debt, redeeming reduces your collateral, which reduces H. The protocol verifies your post-redeem H ≥ 100% and reverts otherwise.

If you want to fully exit and have outstanding debt, settle the debt first, then redeem.

## Common gotchas

- **Trying to redeem with debt.** If your post-redeem H < 100%, the call reverts. Either settle some debt first, or reduce the redeem amount.
- **Trying to redeem locked principal.** This reverts. Wait for the lock to expire, or transfer the position.
- **The exit fee.** It's 1%, deducted on the way out. A 1,000 XPOW supply nets you 990 XPOW on full redemption (plus interest, minus fee).

## Where to go next

- [Repaying debt](/using-the-protocol/repaying-debt) — clear debt before redeeming
- [Locking positions](/using-the-protocol/locking-positions) — what locking changes about exit
