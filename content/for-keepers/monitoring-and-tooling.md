# Monitoring and tooling

A keeper bot is only as good as its observation. This page covers what to monitor and what tooling is available.

## What to monitor

- **All positions with H < 150%.** These are within range of becoming liquidatable on a small adverse move.
- **Pending oracle updates.** A new oracle reading can shift many positions' H simultaneously.
- **Pool utilization.** High utilization means high stress; opportunities appear faster.
- **Your own H.** Don't liquidate yourself out of solvency.
- **Gas prices.** A liquidation profitable at 30 gwei may not be profitable at 300 gwei.

## How to monitor

`banq-cli` covers the basics out of the box: `health-of` queries an account's health factor, `rates-of` reports the current supply/borrow rates (and historical trajectories), and `retwap --watch` streams TWAP-refresh events live. See [CLI and tools](/for-keepers/cli-and-tools) for the full command set.

For sub-second latency (relevant in high-volatility regimes), you'd run your own indexer that listens to the on-chain events and reads `healthOf` periodically — `banq-cli` is a reference, not a production keeper.

## Position prioritisation

Sort underwater positions by:

- **Expected profit** = bonus − gas cost.
- **Time pressure** = how fast H is moving.
- **Liquidity** = whether the absorbed collateral is locked or unlocked.

Sophisticated keepers run an optimisation: they pick the best slice exponent given competing keepers, lock structure, and gas economics.

## Open-source tools

- **`banq-cli`** — the official Deno CLI (dry-run by default). Covers liquidation, oracle refresh, health/rate queries, and ACMA inspection. See [CLI and tools](/for-keepers/cli-and-tools).

`banq-cli` is a starting point. Production keepers typically add proprietary monitoring, private mempool integration, and custom risk management.

## What sophistication actually buys you

The whitepaper acknowledges that liquidation revenue concentrates at the top of the distribution: top-5 keepers in established protocols capture >80% of value. Banq's debt-assumption mechanism widens the pool of *possible* keepers, but not the distribution of *captured* value.

If you want to compete with sophisticated keepers, expect to invest in:

- **Sub-block latency monitoring.**
- **Private mempool integration.**
- **Lock-state-aware accounting** (locked positions are worth less than NAV).
- **MEV protection.**

If you want to participate at the margin without competing for the top tier, the reference implementation is enough.

## Where to go next

- [Running a liquidator](/for-keepers/running-a-liquidator) — production setup
- [CLI and tools](/for-keepers/cli-and-tools) — the `banq-cli` reference
