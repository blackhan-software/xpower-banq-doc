---
title: "2. Related Work"
prev:
  text: "1. Introduction"
  link: /whitepaper/01-introduction
next:
  text: "3. Protocol Architecture"
  link: /whitepaper/03-architecture
---

## Lending Protocols

Compound [\[compound2019\]](/reference/bibliography#compound2019) introduced algorithmic interest rate markets with utilization-based rate curves and 2-day governance timelocks. Aave [\[aave2020\]](/reference/bibliography#aave2020) extended this with flash loans, stable rate borrowing, and credit delegation; V3 introduced E-Mode for correlated assets, though liquidation still requires liquid capital. MakerDAO [\[makerdao2017\]](/reference/bibliography#makerdao2017) pioneered the CDP model, suffering \$8.3M in losses during "Black Thursday" [\[gudgeon2020\]](/reference/bibliography#gudgeon2020). Euler [\[euler2022\]](/reference/bibliography#euler2022) pioneered permissionless asset listing with risk-tiered collateral and a reactive rate model. Liquity [\[liquity2021\]](/reference/bibliography#liquity2021) introduced the Stability Pool where pre-deposited capital absorbs liquidations; XPower Banq instead transfers debt to liquidators. Morpho [\[morpho2022\]](/reference/bibliography#morpho2022) optimizes rates via peer-to-peer matching atop existing protocols.

## Liquidation and MEV

Gudgeon et al. [\[gudgeon2020\]](/reference/bibliography#gudgeon2020) analyzed the March 2020 crisis in which cascade effects drained significant protocol value. Perez et al. [\[perez2021\]](/reference/bibliography#perez2021) showed that liquidation markets are highly concentrated, with the top five liquidators capturing over 80% of value, and Daian et al. [\[daian2020\]](/reference/bibliography#daian2020) and Qin et al. [\[qin2022\]](/reference/bibliography#qin2022) quantified MEV extraction from liquidation events.

## Oracles

Mackinga et al. [\[mackinga2022\]](/reference/bibliography#mackinga2022) demonstrated practical TWAP manipulation, motivating several mitigation approaches. Chainlink [\[chainlink2017\]](/reference/bibliography#chainlink2017) provides off-chain aggregation but carries staleness risks during network congestion [\[werner2022\]](/reference/bibliography#werner2022). Uniswap V3 [\[uniswap2021\]](/reference/bibliography#uniswap2021) introduced geometric mean TWAP computed in ring buffers, and Angeris and Chitra [\[angeris2020\]](/reference/bibliography#angeris2020) formalized manipulation cost bounds for constant function market makers.

## Governance

Beanstalk's \$182M governance attack [\[beanstalk2022\]](/reference/bibliography#beanstalk2022) exploited same-block execution, underscoring the need for rate-bounded governance. Standard timelocks [\[openzeppelin2020\]](/reference/bibliography#openzeppelin2020) constrain the timing of changes but not their magnitude. XPower Banq addresses this with [lethargic governance](/whitepaper/04-mechanisms#lethargic-governance) that requires multiple cycles for any significant parameter change.

## Comparative Analysis

The table below compares protocols across key dimensions. Some features marked absent may be deliberately omitted by design (e.g., Morpho Blue delegates oracle validation to curators), and XPower Banq's advantages carry trade-offs discussed in [Section 9](/whitepaper/09-limitations).

| Feature | Compound | Aave | MakerDAO | Liquity | Euler | **XPower Banq** |
|---|---|---|---|---|---|---|
| Liquidation Model | Repayment | Repayment | Auction | Stability Pool | Repayment | Debt Assumption |
| Liquidator Capital | Required | Required | Required | Pre-deposited | Required | Not Required |
| Cascade Attenuation | None | None | Partial | Yes (pool) | None | Yes (locks)† |
| Position Transfer | Supply only | Supply only | No | No | Supply only | Both (inverted) |
| Governance Bounds | None | None | None | Immutable | None | $0.5\times$–$2\times$ |
| Param. Transitions | Instant | Instant | Instant | N/A | Instant | Asymptotic |
| Oracle Type | Chainlink | Chainlink | CL+OSM | Chainlink | Uniswap | Log TWAP |
| Capacity Rate-Limit | None | None | None | None | None | $\sqrt{n{+}2}$ scaling |
| Spam Protection | Gas price | Gas price | Gas price | Gas price | Gas price | Gas + PoW |
| Position Caps | None | Isolation | Debt ceil. | Debt ceil. | Borrow caps | Beta-distributed |

<small>† Attenuation proportional to lock adoption $\phi$; without locks, cascade risk equals traditional protocols.</small>
