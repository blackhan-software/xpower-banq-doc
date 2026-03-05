---
title: Related Work
prev: '/whitepaper/01-introduction'
next: '/whitepaper/03-architecture'
---

# Related Work

**Lending Protocols.** Compound (Leshner & Hayes, 2019) introduced algorithmic interest rate markets with utilization-based rate curves and 2-day governance timelocks. Aave (Aave Protocol, 2020) extended this with flash loans, stable rate borrowing, and credit delegation; V3 introduced E-Mode for correlated assets, though liquidation still requires liquid capital. MakerDAO (MakerDAO Team, 2017) pioneered the CDP model, suffering \$8.3M in losses during "Black Thursday" (Gudgeon et al., 2020). Euler (Euler Labs, 2022) pioneered permissionless asset listing with risk-tiered collateral and a reactive rate model. Liquity (Lauko & Pardoe, 2021) introduced the Stability Pool where pre-deposited capital absorbs liquidations; XPower Banq instead transfers debt to liquidators. Morpho (Frambot & Gontier Delaunay, 2022) optimizes rates via peer-to-peer matching atop existing protocols.

**Liquidation and MEV.** Gudgeon et al. (2020) analyzed the March 2020 crisis in which cascade effects drained significant protocol value. Perez et al. (2021) showed that liquidation markets are highly concentrated, with the top 5 liquidators capturing over 80% of value, and Daian et al. (2020) and Qin et al. (2022) quantified MEV extraction from liquidation events.

**Oracles.** Mackinga et al. (2022) demonstrated practical TWAP manipulation, motivating several mitigation approaches. Chainlink (Ellis et al., 2017) provides off-chain aggregation but carries staleness risks during network congestion (Werner et al., 2022). Uniswap V3 (Adams et al., 2021) introduced geometric mean TWAP computed in ring buffers, and Angeris and Chitra (2020) formalized manipulation cost bounds for constant function market makers.

**Governance.** Beanstalk's \$182M governance attack (2022) exploited same-block execution, underscoring the need for rate-bounded governance. Standard timelocks (OpenZeppelin, 2020) constrain the timing of changes but not their magnitude. XPower Banq addresses this with lethargic governance that requires multiple cycles for any significant parameter change.

**Comparative Analysis.** The table below compares protocols across key dimensions. Some features marked absent may be deliberately omitted by design (e.g., Morpho Blue delegates oracle validation to curators), and XPower Banq's advantages carry trade-offs discussed in [Section 9](/whitepaper/09-limitations).

| Feature | Compound | Aave | MakerDAO | Liquity | Euler | **XPower Banq** |
|---|---|---|---|---|---|---|
| 1. Liquidation Model | Repayment | Repayment | Auction | Stability Pool | Repayment | Debt Assumption |
| 2. Liquidator Capital | Required | Required | Required | Pre-deposited | Required | Not Required |
| 3. Cascade Attenuation | None | None | Partial | Yes (pool) | None | Yes (locks)† |
| 4. Position Transfer | Supply only | Supply only | No | No | Supply only | Both (inverted) |
| 5. Governance Bounds | None | None | None | Immutable | None | $0.5\times$–$2\times$ |
| 6. Param. Transitions | Instant | Instant | Instant | N/A | Instant | Asymptotic |
| 7. Oracle Type | Chainlink | Chainlink | CL+OSM | Chainlink | Uniswap | Log TWAP |
| 8. Capacity Rate-Limit | None | None | None | None | None | $\sqrt{n{+}2}$ scaling |
| 9. Spam Protection | Gas price | Gas price | Gas price | Gas price | Gas price | Gas + PoW |
| 10. Position Caps | None | Isolation | Debt ceil. | Debt ceil. | Borrow caps | Beta-distributed |

† Attenuation proportional to lock adoption $\phi\text{;}$ without locks, cascade risk equals traditional protocols.
