# Monitoring health

If you have a borrow position, your health factor matters more than any other number. This page covers practical monitoring strategies.

## Reading H

Three places you can read your H:

1. **The XPower Banq app** at [app.xpowerbanq.com](https://app.xpowerbanq.com). Live H displayed prominently.
2. **The Pool contract.** `healthOf(you)` returns your current H as a view function.
3. **Block explorer.** Call the same view function via Etherscan or similar.

H is computed against the *current oracle prices*. It doesn't anticipate price moves; it reflects the present.

## Why H drifts down

Three reasons your H falls without you doing anything:

1. **Borrow interest accrues.** Your debt grows continuously at the borrow rate.
2. **Supply interest accrues, slower.** Your collateral grows at the (lower) supply rate.
3. **Net drift is downward.** Borrow rate > supply rate (because the spread is positive). So H drifts down by approximately `(borrow_rate − supply_rate) × time`.

For default parameters at 50% utilization, this is roughly 1% per year. Slow but real — and faster at higher utilization.

## Setting alerts

Most serious users run off-chain monitoring with thresholds:

- **Notification at H = 150%.** "Position is approaching attention."
- **Alert at H = 120%.** "Top up or repay soon."
- **Emergency at H = 105%.** "You will be liquidated on the next adverse tick."

Several open-source bots and commercial services watch positions and ping users via webhook, email, or Telegram.

## Topping up

Two ways to raise H:

- **Supply more.** Increases your collateral; raises H.
- **Settle some debt.** Reduces your borrow; raises H.

Either is fine. Settling reduces capital efficiency but is more direct.

## What about during a crash?

In a crash, the oracle is *slow* — it lags spot prices by hours. Your reported H may be higher than your "true" H based on instantaneous prices.

This works in your favour: you have hours to react. But it also means a crash that's already happened may not yet be visible in your H — by the time the oracle updates, your position may be liquidatable.

The right response is to keep H comfortable enough that an oracle catch-up doesn't immediately liquidate you. H ≥ 150% is comfortable; H ≥ 200% is cautious; H ≥ 300% is paranoid.

## Where to go next

- [Health factor](/concepts/health-factor) — the formula and interpretation
- [Liquidation](/concepts/liquidation) — what happens at H < 100%
- [Oracle staleness](/risks/oracle-staleness) — why the oracle is slow
