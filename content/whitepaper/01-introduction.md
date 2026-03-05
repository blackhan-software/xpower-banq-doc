---
title: "1. Introduction"
prev: false
next:
  text: "2. Related Work"
  link: /whitepaper/02-related-work
---

<img src="/images/banq-cover.webp" alt="" style="border-radius: 12px; width: 100%; margin-bottom: 1.5rem;" />

We present **XPower Banq**, a permissionless DeFi lending protocol on the Ethereum Virtual Machine. The protocol introduces:

1. *Optionally locked positions* that attenuate liquidation cascades by factor $(1{-}\phi)$.
2. *Lethargic governance* with time-weighted parameter transitions bounded by $0.5\times$–$2\times$ per cycle.
3. *Beta-distributed position caps* with holder-count scaling that rate-limits capacity accumulation to $O(\sqrt{k})$ for $k$ accounts.
4. *Transferable debt positions* with inverted ERC20 semantics enabling capital-efficient debt-assumption liquidation.
5. *Log-space TWAP oracles* with bidirectional geometric-mean spread computation and logarithmic spread scaling.

The protocol balances capital efficiency against bounded bad-debt risk: default parameters yield 66.67% LTV with a 50% over-collateralization buffer, adjustable via [lethargic governance](/whitepaper/04-mechanisms#lethargic-governance).

## Background

Decentralized lending protocols — Compound [\[compound2019\]](/reference/bibliography#compound2019), Aave [\[aave2020\]](/reference/bibliography#aave2020), MakerDAO [\[makerdao2017\]](/reference/bibliography#makerdao2017) — have established algorithmic interest rate markets as foundational DeFi infrastructure [\[bartoletti2021\]](/reference/bibliography#bartoletti2021). Persistent challenges remain: oracle manipulation [\[mackinga2022\]](/reference/bibliography#mackinga2022), governance attacks [\[beanstalk2022\]](/reference/bibliography#beanstalk2022), capital inefficiency, and systemic liquidation cascades [\[gudgeon2020\]](/reference/bibliography#gudgeon2020).

## Five Design Choices

XPower Banq addresses these through five design choices:

1. **Locked Positions.** Irrevocable position locks attenuate liquidation cascades by factor $(1{-}\phi)$ through preventing immediate collateral redemption ([Section 4.1](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation)).
2. **Lethargic Governance.** Multiplicative bounds ($0.5\times$–$2\times$) with asymptotic transitions prevent governance shocks ([Section 4.3](/whitepaper/04-mechanisms#lethargic-governance)).
3. **Beta-Distributed Caps.** The $12\lambda(1{-}\lambda)^2/\sqrt{n{+}2}$ cap function rate-limits capacity accumulation sublinearly ([Section 4.4](/whitepaper/04-mechanisms#beta-distributed-position-caps)).
4. **Debt Assumption Liquidation.** Transferable debt positions with inverted ERC20 semantics eliminate liquidator capital requirements ([Section 4.5](/whitepaper/04-mechanisms#health-factor-and-liquidation)).
5. **Log-Space TWAP Oracle.** Geometric mean temporal averaging with bidirectional spread computation resists flash-loan manipulation ([Section 4.6](/whitepaper/04-mechanisms#oracle-twap)).

## Roadmap

[Section 2](/whitepaper/02-related-work) surveys related work and positions our contributions against existing protocols. [Section 3](/whitepaper/03-architecture) presents the contract architecture, followed by [Section 4](/whitepaper/04-mechanisms) which details the core mechanisms. [Section 5](/whitepaper/05-anti-spam) describes anti-spam protection, and [Section 6](/whitepaper/06-governance) covers the governance model. [Section 7](/whitepaper/07-security) provides a security analysis under an explicit adversary model. [Section 8](/whitepaper/08-evaluation) presents simulation and gas evaluation results, [Section 9](/whitepaper/09-limitations) discusses limitations, and [Section 10](/whitepaper/10-conclusion) concludes.

Companion documents provide extended treatment: [Mathematical Theory & Proofs](/theory/01-mathematical-foundations), [Simulations & Risk](/simulations/01-cap-accumulation), and the [Reference](/reference/parameters) (parameters, constants, bibliography, glossary). The two engineering primitives are documented separately as [Ring-Buffer Time Locks](/timelocks/01-introduction) and the [Log-Space Compounding Index](/logspace/01-introduction).
