# Borrowing assets

Borrowing requires existing supply (collateral). You take debt out of the pool against your supply, up to the protocol's LTV.

## Prerequisites

- You have an existing Supply Position in the pool.
- The pool supports the borrow token (it might support a different set of borrow tokens than supply tokens).
- Your post-borrow [health factor](/concepts/health-factor) must be ≥ 100%.

## What you'll do

1. Decide which token to borrow and how much.
2. Call the borrow function.

## What the protocol does

In the same transaction:

1. Verifies your post-borrow health factor would be ≥ 100%.
2. Verifies the pool has enough liquid supply of the borrow token.
3. Mints a corresponding Borrow Position to your address (representing the debt).
4. Transfers the borrow tokens to your wallet.
5. Updates the global borrow index.
6. If your new Borrow Position balance crosses *from below* one whole token unit to *at-or-above* it, increments the protocol-wide `largeHolders()` counter on the Borrow Position (tightening every borrow user's cap slightly).

After the call, you owe `amount` of the borrow token plus accrued interest, ongoing.

## How much can you borrow?

The maximum is `(supply value × LTV) − existing debt value`, where LTV defaults to 66.67%.

- 1,000 XPOW of supplied APOW (at 1,000 XPOW/APOW × LTV 66.67%) → up to 666.67 XPOW borrowable.
- An existing 200 XPOW of debt reduces this to 466.67 XPOW.

The protocol computes this based on its oracle's reported prices, not spot prices. See [Oracle](/features/twap-oracle/overview).

## Health factor headroom

Borrowing right up to the maximum gives you an H of 100%. A small adverse price move will liquidate you. Most users target H ≥ 150% — i.e., borrow only ~⅔ of their max — to absorb normal volatility.

See [Health factor](/concepts/health-factor) and [Monitoring health](/using-the-protocol/monitoring-health) for details.

## Locked borrow

If you lock your borrow position, you cannot repay early. In exchange, your effective borrow rate drops by an amount proportional to your locked fraction. Concretely, the borrow rate paid is `R_base · (1 + s − r_malus · λ)`, where `s` is the spread (default 10%), `λ` is your locked fraction (`lockTotalOf / totalOf`), and `r_malus` is the `LOCK_MALUS` parameter (default 10%, bounded above by `SPREAD`). At full lock and default parameters, the malus exactly cancels the borrow-side spread — see [Bonus and malus](/features/locked-positions/bonus-and-malus).

Be conservative with borrow locks. If you may need to repay early — e.g., if your strategy involves dynamic positioning — locking your debt position is restrictive.

## Where to go next

- [Repaying debt](/using-the-protocol/repaying-debt) — settle your borrow
- [Monitoring health](/using-the-protocol/monitoring-health) — keep H above 100%
- [Locking positions](/using-the-protocol/locking-positions) — for the malus reduction
