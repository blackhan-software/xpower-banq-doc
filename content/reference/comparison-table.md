# Comparison table

XPower Banq compared with major lending protocols across the dimensions that matter most.

## Overall

| Dimension | Compound V3 | Aave V3 | MakerDAO | Liquity | Euler V2 | XPower Banq |
|---|---|---|---|---|---|---|
| Type | Pool | Pool | CDP | CDP | Pool | Pool |
| Liquidation model | Repayment | Repayment | Auction | Stability pool | Repayment | **Debt assumption** |
| Liquidator capital | Required | Required | Required | Pre-deposited | Required | **Not required** |
| Default LTV | 75% | 80% | 75% | 90.91% | up to 95% | 66.67% (`170/255`) |
| Health factor system | Yes | Yes | Yes (CR) | Yes (CR) | Yes | Yes |

## Liquidation cascade resistance

| Mechanism | Compound | Aave | Maker | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Cascade attenuation | None | None | Partial | Yes (pool) | None | **Yes (locks)** |
| Locked positions | No | No | No | No | No | **Yes** |
| Liquidation seniority | None | None | Partial | Yes | None | **De facto (locks)** |

## Governance

| Mechanism | Compound | Aave | Maker | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Parameter bounds | None | None | None | Immutable | None | **0.5×–2× per cycle** |
| Parameter transitions | Instant | Instant | Instant | n/a | Instant | **Asymptotic** |
| Veto mechanism | None | None | Limited | n/a | None | **Yes (`_GUARD_ROLE` per action)** |
| Rate limit | None | None | None | n/a | None | **One change per cycle** |

## Position composability

| Mechanism | Compound | Aave | Maker | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Supply position is ERC20 | Yes | Yes | No | No | Yes | **Yes** |
| Borrow position is ERC20 | No | No | No | No | No | **Yes (inverted)** |
| Borrow position transfer | No | No | No | No | No | **Yes** |
| Vault is ERC4626 | No | No | No | No | Yes | **Yes** |

## Oracle

| Mechanism | Compound | Aave | Maker | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Source | Chainlink | Chainlink | Median | Chainlink | Chainlink + AMM | **AMM or Chainlink per pool** |
| Smoothing | None | None | None | None | TWAP | **Log-space TWAP** |
| Manipulation immunity | Block-level | Block-level | Block-level | Block-level | TWAP-window | **Two-tick** |
| Bidirectional spread | No | No | No | No | No | **Yes** |

## Sybil resistance

| Mechanism | Compound | Aave | Maker | Liquity | Euler | XPower Banq |
|---|---|---|---|---|---|---|
| Per-account caps | No | Yes (debt ceilings) | Yes (DC) | No | Yes | **Yes** |
| Capacity rate-limit | None | None | Static | None | Static | **√(n+2) scaling** |
| Beta-distributed function | No | No | No | No | No | **Yes** |
| Spam protection on public liquidation | Gas | Gas | Gas | Gas | Gas | **Gas + PoW** |

## When XPower Banq is the right choice

- You value cascade protection and are willing to lock for it.
- You want predictable, slow governance — not "fast iteration."
- You're a keeper without large liquid capital.
- You're a developer who wants both supply and borrow as composable ERC20s.
- You're a long-term holder using lending as yield infrastructure.

## When another protocol may serve you better

- You want maximum capital efficiency at any cost.
- You need to be able to repay your loan in the next block.
- You're trading short-term volatility and need fast position changes.
- You depend on flash-loan integrations against the protocol's view of price.

## Where to go next

- [Why XPower Banq](/introduction/why-xpower-banq) — narrative version
- [Risks](/risks/overview) — what the trade-offs cost
