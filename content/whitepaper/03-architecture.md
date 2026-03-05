---
title: Protocol Architecture
prev: '/whitepaper/02-related-work'
next: '/whitepaper/04-mechanisms'
---

# Protocol Architecture

The protocol comprises five core contracts, depicted in the architecture diagram below:

<figure>
  <img src="/images/001-architecture.svg" alt="XPower Banq contract architecture">
  <figcaption>Figure 1: XPower Banq contract architecture</figcaption>
</figure>

1. **Pool**: The main contract, managing supply, borrow, settle, and redeem operations with health checks and liquidation logic.

2. **Position**: ERC20 (Vogelsteller & Buterin, 2015) tokens representing supply and borrow positions, each with distinct transfer semantics ([Section 4.2](/whitepaper/04-mechanisms#position-transfer-semantics)).

3. **Vault**: An ERC4626-compliant (Santoro et al., 2022) custody contract that tracks deposited assets and utilization.

4. **Oracle**: A log-space TWAP aggregator with bidirectional geomean spread computation.

5. **Acma**: An access control wrapper around OpenZeppelin's `AccessManager` (OpenZeppelin, 2020).

::: definition
**Definition 1** (Minimum Token Requirements). $|\mathcal{T}| \geq 2 \land \text{decimals}(T_i) \geq 6$, ensuring sufficient precision for interest calculations and cross-collateralization.
:::
