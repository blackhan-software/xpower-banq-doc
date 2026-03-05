# Summary

* [Introduction](README.md)

## Introduction

* [What is XPower Banq](introduction/what-is-xpower-banq.md)
* [Why XPower Banq](introduction/why-xpower-banq.md)
* [How it works](introduction/how-it-works.md)
* [Quickstart](introduction/quickstart.md)

## Concepts

* [Lending basics](concepts/lending-basics.md)
* [Health factor](concepts/health-factor.md)
* [Interest rates](concepts/interest-rates.md)
* [Liquidation](concepts/liquidation.md)
* [Positions as tokens](concepts/positions-as-tokens.md)

## Features

### Locked Positions

* [Overview](features/locked-positions/overview.md)
* [Timed vs permanent](features/locked-positions/timed-vs-permanent.md)
* [Bonus and malus](features/locked-positions/bonus-and-malus.md)
* [Transfers and exits](features/locked-positions/transfers-and-exits.md)
* [Cascade protection](features/locked-positions/cascade-protection.md)

### Debt-Assumption Liquidation

* [Overview](features/debt-assumption-liquidation/overview.md)
* [How liquidations work](features/debt-assumption-liquidation/how-liquidations-work.md)
* [For liquidators](features/debt-assumption-liquidation/for-liquidators.md)

### Lethargic Governance

* [Overview](features/lethargic-governance/overview.md)
* [Parameter bounds](features/lethargic-governance/parameter-bounds.md)
* [Transition curves](features/lethargic-governance/transition-curves.md)
* [Role hierarchy](features/lethargic-governance/role-hierarchy.md)

### Position Caps

* [Overview](features/position-caps/overview.md)
* [How caps grow](features/position-caps/how-caps-grow.md)
* [New user allocation](features/position-caps/new-user-allocation.md)
* [Caps wrapper and circuit breaker](features/position-caps/caps-wrapper-and-circuit-breaker.md)

### Protocol-Owned Liquidity

* [Overview](features/protocol-owned-liquidity/overview.md)
* [Fetching and roles](features/protocol-owned-liquidity/fetching-and-roles.md)

### TWAP Oracle

* [Overview](features/twap-oracle/overview.md)
* [Manipulation resistance](features/twap-oracle/manipulation-resistance.md)
* [Spread and slippage](features/twap-oracle/spread-and-slippage.md)

## Using the Protocol

* [Supplying assets](using-the-protocol/supplying-assets.md)
* [Borrowing assets](using-the-protocol/borrowing-assets.md)
* [Repaying debt](using-the-protocol/repaying-debt.md)
* [Withdrawing assets](using-the-protocol/withdrawing-assets.md)
* [Locking positions](using-the-protocol/locking-positions.md)
* [Transferring positions](using-the-protocol/transferring-positions.md)
* [Monitoring health](using-the-protocol/monitoring-health.md)
* [Wrapped positions](using-the-protocol/wrapped-positions.md)

## For Developers

* [Architecture overview](for-developers/architecture-overview.md)
* [Contract addresses](for-developers/contract-addresses.md)
* [Integration guide](for-developers/integration-guide.md)
* [ERC20 semantics](for-developers/erc20-semantics.md)
* [ERC4626 vaults](for-developers/erc4626-vaults.md)
* [Events and indexing](for-developers/events-and-indexing.md)
* [Gas costs](for-developers/gas-costs.md)

## For Keepers

* [Overview](for-keepers/overview.md)
* [Running a liquidator](for-keepers/running-a-liquidator.md)
* [PoW-gated public mode](for-keepers/pow-gated-public-mode.md)
* [CLI and tools](for-keepers/cli-and-tools.md)
* [Monitoring and tooling](for-keepers/monitoring-and-tooling.md)

## Governance

* [Overview](governance/overview.md)
* [Parameter catalog](governance/parameter-catalog.md)
* [Proposing changes](governance/proposing-changes.md)
* [Role management](governance/role-management.md)
* [Emergency procedures](governance/emergency-procedures.md)

## Parameters

* [Pool](parameters/pool-parameters.md)
* [Position](parameters/position-parameters.md)
* [Oracle](parameters/oracle-parameters.md)
* [Vault](parameters/vault-parameters.md)
* [Change-rate constraints](parameters/change-rate-constraints.md)

## Risks

* [Overview](risks/overview.md)
* [Liquidation risk](risks/liquidation-risk.md)
* [Oracle staleness](risks/oracle-staleness.md)
* [Bad debt scenarios](risks/bad-debt-scenarios.md)
* [Governance risk](risks/governance-risk.md)
* [Smart contract risk](risks/smart-contract-risk.md)
* [Secondary market risk](risks/secondary-market-risk.md)

## Security

* [Threat model](security/threat-model.md)
* [Defensive mechanisms](security/defensive-mechanisms.md)
* [Audits and reviews](security/audits-and-reviews.md)

## Research

* [Whitepaper](research/whitepaper.md)

### Companion Papers

* [Protocol](research/papers/protocol.md)
* [Ring-buffer locks](research/papers/ring-buffer-locks.md)
* [Log-space index](research/papers/log-space-index.md)
* [Theory & proofs](research/papers/theory-and-proofs.md)
* [Simulations](research/papers/simulations.md)

## Reference

* [Comparison table](reference/comparison-table.md)
* [Bibliography](reference/bibliography.md)
* [Glossary](reference/glossary.md)
* [FAQ](reference/faq.md)
