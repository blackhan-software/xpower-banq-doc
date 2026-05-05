---
title: "3. Protocol Architecture"
prev:
  text: "2. Related Work"
  link: /whitepaper/02-related-work
next:
  text: "4. Core Mechanisms"
  link: /whitepaper/04-mechanisms
---

The protocol comprises six core contracts:

<figure>
  <img src="/images/001-architecture.svg" alt="XPower Banq contract architecture">
  <figcaption>Figure 1: XPower Banq contract architecture — Pool routes operations through Position, Vault, and Oracle, with Acma supplying access control.</figcaption>
</figure>

1. **Pool** — the main contract, managing supply, borrow, settle, and redeem operations with health checks and liquidation logic.
2. **Position** — ERC20 [\[erc20\]](/reference/bibliography#erc20) tokens representing supply and borrow positions, each with distinct transfer semantics ([Section 4.2](/whitepaper/04-mechanisms#position-transfer-semantics)).
3. **Vault** — an ERC4626-compliant [\[erc4626\]](/reference/bibliography#erc4626) custody contract that tracks deposited assets and utilization.
4. **Oracle** — a log-space TWAP aggregator with bidirectional geomean spread computation.
5. **Acma** — an access-control contract extending OpenZeppelin's `AccessManager` [\[openzeppelin2020\]](/reference/bibliography#openzeppelin2020) with the protocol-specific role catalogue and the `relate()` selector-to-role binder.
6. **WPosition** — optional ERC20 wrappers for supply/borrow positions, registered per-token via `Pool.enwrap()`; enable composition with external DeFi protocols that expect plain ERC20 transfer semantics (see [Section 9](/whitepaper/09-limitations)).

::: definition
**Definition 1** (Minimum Token Requirements). $|\mathcal{T}| \geq 2 \land \text{decimals}(T_i) \geq 6$, ensuring sufficient precision for interest calculations and cross-collateralization.
:::
