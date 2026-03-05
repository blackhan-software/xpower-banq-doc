---
layout: home
description: Permissionless DeFi lending on Avalanche — locked positions, lethargic governance, capital-efficient liquidation.

hero:
  name: "XPower Banq"
  # text: "Lending, but the cascades stop here."
  tagline: DeFi Lending with Locked Positions, Lethargic Governance, and Capital-Efficient Liquidation.
  actions:
    # `link` is filled at build time from BANQ_APP_URL (see
    # `.vitepress/config/seo.ts` transformPageData); matched by `target: _blank`.
    - theme: brand
      text: Launch App
      link: ""
      target: _blank
      rel: noopener
    - theme: alt
      text: What is XPower Banq?
      link: /introduction/what-is-xpower-banq

features:
  - title: <i class="bi bi-lock"></i> Optionally Locked Positions
    details: Lock your supply or borrow position for a fixed term to earn more (or pay less). Locked supply cannot be dumped during a crash, attenuating cascades by a factor of (1 − ϕ).
    link: /features/locked-positions/overview
    linkText: Read more
  - title: <i class="bi bi-hourglass-split"></i> Lethargic Governance
    details: Every parameter change is bounded to 0.5×–2× per cycle and phased in asymptotically. A 10× change requires 4 months — you always have time to react.
    link: /features/lethargic-governance/overview
    linkText: Read more
  - title: <i class="bi bi-fire"></i> Debt-Assumption Liquidation
    details: Liquidators don't need liquid capital — they just take on the victim's debt and collateral. More capital-efficient and friendlier to keepers.
    link: /features/debt-assumption-liquidation/overview
    linkText: Read more
  - title: <i class="bi bi-currency-exchange"></i> Log-Space TWAP Oracle
    details: Geometric-mean temporal averaging with bidirectional spread computation. Two-tick flash-loan immunity, ~40 hours of sustained manipulation needed for 90% deviation.
    link: /features/twap-oracle/overview
    linkText: Read more
  - title: <i class="bi bi-shield-shaded"></i> Beta-Distributed Caps
    details: Sybil capacity gain rate-limited to O(√n). Patient attackers can still accumulate, but no one monopolises the pool overnight.
    link: /features/position-caps/overview
    linkText: Read more
  - title: <i class="bi bi-bricks"></i> Composable by Design
    details: Supply and borrow positions are ERC20s. Vaults are ERC4626. An optional WSupplyPosition ERC4626 wrapper integrates cleanly with the broader DeFi stack.
    link: /for-developers/architecture-overview
    linkText: Read more
---

<div style="max-width: 1152px; margin: 64px auto 0; padding: 0 24px;">

##

<div class="toc-grid">

<div>

### <i class="bi bi-book"></i> [Introduction](/introduction/what-is-xpower-banq)

- [What is XPower Banq](/introduction/what-is-xpower-banq)
- [Why XPower Banq](/introduction/why-xpower-banq)
- [How it works](/introduction/how-it-works)
- [Quickstart](/introduction/quickstart)

</div>

<div>

### <i class="bi bi-lightbulb"></i> [Concepts](/concepts/lending-basics)

- [Lending basics](/concepts/lending-basics)
- [Health factor](/concepts/health-factor)
- [Interest rates](/concepts/interest-rates)
- [Liquidation](/concepts/liquidation)
- [Positions as tokens](/concepts/positions-as-tokens)

</div>

<div>

### <i class="bi bi-stars"></i> [Features](/features/locked-positions/overview)

- [Locked positions](/features/locked-positions/overview)
- [Debt-assumption liquidation](/features/debt-assumption-liquidation/overview)
- [Lethargic governance](/features/lethargic-governance/overview)
- [Position caps](/features/position-caps/overview)
- [TWAP oracle](/features/twap-oracle/overview)

</div>

<div>

### <i class="bi bi-tools"></i> [Using the Protocol](/using-the-protocol/supplying-assets)

- [Supplying assets](/using-the-protocol/supplying-assets)
- [Borrowing assets](/using-the-protocol/borrowing-assets)
- [Repaying debt](/using-the-protocol/repaying-debt)
- [Withdrawing assets](/using-the-protocol/withdrawing-assets)
- [Locking positions](/using-the-protocol/locking-positions)
- [Transferring positions](/using-the-protocol/transferring-positions)
- [Monitoring health](/using-the-protocol/monitoring-health)
- [Wrapped positions](/using-the-protocol/wrapped-positions)

</div>

<div>

### <i class="bi bi-code-slash"></i> [For Developers](/for-developers/architecture-overview)

- [Architecture overview](/for-developers/architecture-overview)
- [Contract addresses](/for-developers/contract-addresses)
- [Integration guide](/for-developers/integration-guide)
- [ERC20 semantics](/for-developers/erc20-semantics)
- [ERC4626 vaults](/for-developers/erc4626-vaults)
- [Events and indexing](/for-developers/events-and-indexing)
- [Gas costs](/for-developers/gas-costs)

</div>

<div>

### <i class="bi bi-robot"></i> [For Keepers](/for-keepers/overview)

- [Overview](/for-keepers/overview)
- [Running a liquidator](/for-keepers/running-a-liquidator)
- [PoW-gated public mode](/for-keepers/pow-gated-public-mode)
- [CLI and tools](/for-keepers/cli-and-tools)
- [Monitoring and tooling](/for-keepers/monitoring-and-tooling)

</div>

<div>

### <i class="bi bi-bank"></i> [Governance](/governance/overview)

- [Overview](/governance/overview)
- [Parameter catalog](/governance/parameter-catalog)
- [Proposing changes](/governance/proposing-changes)
- [Role management](/governance/role-management)
- [Emergency procedures](/governance/emergency-procedures)

</div>

<div>

### <i class="bi bi-sliders"></i> [Parameters](/parameters/pool-parameters)

- [Pool](/parameters/pool-parameters)
- [Position](/parameters/position-parameters)
- [Oracle](/parameters/oracle-parameters)
- [Vault](/parameters/vault-parameters)
- [Change-rate constraints](/parameters/change-rate-constraints)

</div>

<div>

### <i class="bi bi-exclamation-triangle"></i> [Risks](/risks/overview)

- [Overview](/risks/overview)
- [Liquidation risk](/risks/liquidation-risk)
- [Oracle staleness](/risks/oracle-staleness)
- [Bad debt scenarios](/risks/bad-debt-scenarios)
- [Governance risk](/risks/governance-risk)
- [Smart contract risk](/risks/smart-contract-risk)
- [Secondary market risk](/risks/secondary-market-risk)

</div>

<div>

### <i class="bi bi-shield-check"></i> [Security](/security/threat-model)

- [Threat model](/security/threat-model)
- [Defensive mechanisms](/security/defensive-mechanisms)
- [Audits and reviews](/security/audits-and-reviews)

</div>

<div>

### <i class="bi bi-binoculars"></i> [Research](/research/whitepaper)

- [Whitepaper](/research/whitepaper)
- [Protocol paper](/research/papers/protocol)
- [Ring-buffer locks](/research/papers/ring-buffer-locks)
- [Log-space index](/research/papers/log-space-index)
- [Theory & proofs](/research/papers/theory-and-proofs)
- [Simulations](/research/papers/simulations)

</div>

<div>

### <i class="bi bi-journals"></i> [Reference](/reference/comparison-table)

- [Comparison table](/reference/comparison-table)
- [Bibliography](/reference/bibliography)
- [Glossary](/reference/glossary)
- [FAQ](/reference/faq)

</div>

</div>

</div>
