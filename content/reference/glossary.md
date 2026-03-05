---
title: Glossary
description: Key terms and definitions for the XPower Banq protocol.
---

# Glossary

A comprehensive glossary with over 120 entries appears in the [Technical Appendices companion document](/appendices/part-iii-reference/glossary). The following terms are central to the whitepaper.

## Beta Cap

Position limit following the 12*lambda*(1 - *lambda*)^2 distribution where *lambda* is the user's fraction of total supply. The cap peaks at *lambda* = 1/3 and vanishes at the boundaries (0 and 1). The sqrt(n + 2) divisor scales the cap inversely with holder count, rate-limiting capacity accumulation.

## Debt Assumption

Liquidation model where the liquidator assumes the victim's debt rather than repaying it. This enables capital-efficient liquidation without requiring liquid capital – the liquidator only needs sufficient collateral headroom. Both supply tokens and debt transfer atomically.

## Health Factor

Ratio of weighted supply value to weighted borrow value:

> H = sum(w_s * V_s) / sum(w_b * V_b)

Liquidation occurs when H < 1. With default weights (w_s = 85, w_b = 255), the effective LTV is approximately 33%.

## Lethargic Governance

Parameter change model where values transition asymptotically toward targets, bounded to 0.5x–2x per governance cycle. The effective value follows a time-weighted mean that never fully reaches the target but approaches it over time. A 10x change requires at least 4 months of consecutive governance actions.

## LTV

Loan-to-Value ratio – maximum borrowing power as a fraction of collateral value. Default is w_s / w_b = 85 / 255, which is approximately 33%. This implies a 200% over-collateralization buffer.

## Position Lock

Irrevocable fraction of a position restricted from redemption. Locked suppliers earn a bonus (additional interest), and locked borrowers receive a malus (reduced interest). Locked positions act as circuit breakers during liquidation cascades by preventing immediate collateral redemption. Only the principal is locked; accrued interest can always be redeemed or settled.

## Spread

Has two meanings depending on context:

1. **Oracle spread:** Bidirectional geomean of relative spreads from both AMM query directions, stored as log2(1 + s_geo). Spread auto-widens with position size.
2. **Interest rate spread:** Symmetric half-spread applied to the base rate. Borrow rate = base x (1 + s), supply rate = base x (1 - s), generating 2s margin on interest flows.

## Supply / Borrow Position

ERC20 tokens representing collateral and debt respectively.

- **Supply Position** follows standard ERC20 transfer semantics (push value to receiver). Health check applies to the sender.
- **Borrow Position** uses inverted semantics: `transfer(from, amount)` pulls debt from the source. `transferFrom` requires dual approval from both sender and receiver. Health check applies to the receiver. The Pool contract bypasses approvals for liquidation.

## TWAP

Time-Weighted Average Price – price smoothed via log-space EMA (geometric mean temporal averaging) to resist manipulation. The log-space computation produces geometric mean averaging, consistent with Uniswap V3's approach. With the default decay (alpha = 0.944) and hourly refreshes, approximately 40 hours of sustained manipulation is needed for 90% price deviation.

## Utilization

Ratio of borrowed to supplied assets in a vault. Drives interest rates via a piecewise-linear model with a kink at optimal utilization (default 90%). Below the kink, rates increase linearly; above the kink, rates increase more steeply to incentivize repayment.
