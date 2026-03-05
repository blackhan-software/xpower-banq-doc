# Why XPower Banq?

Lending protocols have been a load-bearing piece of DeFi infrastructure since 2018. They also have a track record of failing in correlated, expensive ways. This page explains the specific problems XPower Banq targets, and how it differs from the protocols you may already know.

## The four recurring failure modes

| Failure | What happens | Examples |
|---|---|---|
| **Liquidation cascades** | A price drop triggers liquidations; dumped collateral pushes the price lower; more liquidations follow. | March 2020 across the board; recurring in stressed markets. |
| **Oracle manipulation** | An attacker uses flash loans or thin liquidity to move the price the protocol sees, then exploits the discrepancy. | Numerous, ongoing. |
| **Governance attacks** | An attacker acquires enough governance power (or finds a flaw) to push through a malicious parameter change. | Beanstalk's $182M governance attack, April 2022. |
| **Capital inefficiency at the keeper layer** | Liquidators must hold liquid capital to repay debt. This concentrates liquidation revenue in a small number of well-capitalised actors and slows response during crashes. | Top-5 liquidators capture >80% of value in most lending protocols. |

XPower Banq doesn't claim to solve all of these — but it addresses each one in a measurable way.

## What XPower Banq does differently

### Cascade attenuation through locks

Locked supply can't be redeemed for the underlying asset. If a position is liquidated, the locked tokens transfer to the liquidator — but the underlying assets stay in the vault. Only the unlocked fraction generates sell pressure on the open market.

The protocol formalises this as the **Cascade Attenuation Theorem**: in a pool where fraction ϕ of supply is locked, the maximum cascade amplification is bounded by (1 − ϕ).

Simulation across 1,000 borrowers shows that under a 25% price shock:

- With no locks: **85.7%** of positions get liquidated.
- With full lock adoption: **29.4%**.

That's not a complete fix — locks depend on adoption, and adoption depends on incentives — but it's a meaningful structural improvement.

### Lethargic governance

Most protocols let governance flip a parameter the moment a vote passes. XPower Banq doesn't. Every parameter change is:

- **Bounded multiplicatively** to between 0.5× and 2× the prior value, per cycle.
- **Phased in asymptotically**, so the effective value approaches the new target rather than jumping to it.
- **Rate-limited** to one change per cycle (typically a month).

A 10× change requires 4 months. A genuinely catastrophic 64× change takes 6 months. That's enough time for users to react or exit.

### Debt-assumption liquidation

In a traditional repayment liquidation, the liquidator *pays the debt* in stablecoins and *receives discounted collateral*. They need liquid capital.

In XPower Banq, the liquidator *takes on the debt and the collateral atomically*. They need collateral headroom in their own position — but they don't need to source liquid capital. This is much friendlier to small or distributed keepers.

### Log-space TWAP oracles

Prices are stored as logarithms and smoothed via an exponential moving average. The implementation has a built-in two-tick delay: a new sample enters the running mean only on the next refresh, which makes single-block manipulation impossible. Sustained manipulation across ~40 hours would be required to shift the reported price by 90%.

## How it compares

| Feature | Compound | Aave | MakerDAO | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Liquidation model | Repayment | Repayment | Auction | Stability pool | Repayment | **Debt assumption** |
| Liquidator capital | Required | Required | Required | Pre-deposited | Required | **Not required** |
| Cascade attenuation | None | None | Partial | Yes (pool) | None | **Yes (locks)** |
| Governance bounds | None | None | None | Immutable | None | **0.5×–2× per cycle** |
| Parameter transitions | Instant | Instant | Instant | n/a | Instant | **Asymptotic** |
| Position transfer | Supply only | Supply only | No | No | Supply only | **Both (inverted)** |
| Capacity rate-limit | None | None | None | None | None | **√(n+2) scaling** |

Each of these is a tradeoff. Lethargic governance means slow response; debt-assumption liquidation means liquidators inherit lock structure they may not want; locks fragment the supply side. The right comparison isn't "Banq vs incumbent" but "this set of tradeoffs vs that set of tradeoffs."

## Who XPower Banq is for

- **Suppliers who care about systemic risk** — willing to sacrifice some liquidity for cascade protection.
- **Borrowers with longer time horizons** — happy to lock in rates and reduce effective borrow cost.
- **Keepers without large capital reserves** — debt assumption lowers the bar to participating in liquidations.
- **Protocol integrators** — looking for ERC20 supply/borrow positions and ERC4626 vaults that compose cleanly.

If you need maximum capital efficiency at any cost, or need the ability to repay your loan the moment markets turn, the incumbent protocols may serve you better.

## Where to go next

- **The mechanics, plain-language:** [How it works](/introduction/how-it-works)
- **To start:** [Quickstart](/introduction/quickstart)
- **The full set of caveats:** [Risks](/risks/overview)
