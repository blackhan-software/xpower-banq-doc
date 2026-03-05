# Repaying debt

To close out (or reduce) a borrow position, you **settle** your debt. The protocol pulls the owed amount from your wallet and burns the corresponding Borrow Position tokens.

## What you'll do

1. Approve the protocol to spend the borrow token from your wallet (if you haven't already).
2. Call the settle function with the amount you want to repay (or `MAX_UINT256` for the full balance).

## What the protocol does

In the same transaction:

1. Pulls the repaid amount of the borrow token from your wallet into the vault.
2. Burns the corresponding Borrow Position tokens.
3. Updates the global borrow index.
4. If the burn drops your Borrow Position balance back below one whole token unit (when it had been at-or-above), decrements the protocol-wide `largeHolders()` counter on the Borrow Position.

## Repaying full vs partial

- **Partial settle.** Repay any amount up to your current debt. Useful for adjusting your position without exiting.
- **Full settle.** Repay your entire debt. The protocol uses the post-accrual balance to ensure you don't leave dust.

For a full settle, pass `MAX_UINT256`. The protocol substitutes your actual balance, ensuring you don't accidentally over-pay.

## Locked debt

If your debt is locked, you cannot repay the principal until the lock expires. You **can** still repay accrued *interest* — interest is always settleable, even on locked positions.

## Repayment fee

There is no settlement fee. Settling debt is free (gas excluded).

## After settling

Your borrow position balance decreases. Your health factor rises. Your supply position is untouched — you still hold the collateral. To remove the collateral, see [Withdrawing assets](/using-the-protocol/withdrawing-assets).

## Common gotchas

- **Forgetting the approval.** ERC20 approvals are needed before settle.
- **Settling more than you owe.** The protocol caps the actual pull at your balance, so over-approving and calling MAX_UINT256 is safe.
- **Settling locked principal.** This will revert. Settle only the unlocked or interest portion.

## Where to go next

- [Withdrawing assets](/using-the-protocol/withdrawing-assets) — remove your collateral after repaying
- [Monitoring health](/using-the-protocol/monitoring-health) — settling raises H
