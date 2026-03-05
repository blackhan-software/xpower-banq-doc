---
title: Introduction
prev: false
next: '/whitepaper/02-related-work'
---

<img src="/images/banq-cover.webp" alt="" style="border-radius: 12px; width: 100%; margin-bottom: 1.5rem;" />

# Introduction

Decentralized lending protocols—Compound (Leshner & Hayes, 2019), Aave (Aave Protocol, 2020), MakerDAO (MakerDAO Team, 2017)—have established algorithmic interest rate markets as foundational DeFi infrastructure (Bartoletti et al., 2021). Persistent challenges remain: oracle manipulation (Mackinga et al., 2022), governance attacks (Beanstalk, 2022), capital inefficiency, and systemic liquidation cascades (Gudgeon et al., 2020).

XPower Banq addresses these through five design choices:

1. **Locked Positions**: Irrevocable position locks attenuate liquidation cascades by factor $(1{-}\phi)$ through preventing immediate collateral redemption ([Section 4.1](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation)).

2. **Lethargic Governance**: Multiplicative bounds ($0.5\times$–$2\times$) with asymptotic transitions prevent governance shocks ([Section 4.3](/whitepaper/04-mechanisms#lethargic-governance)).

3. **Beta-Distributed Caps**: The $12\lambda(1{-}\lambda)^2/\sqrt{n{+}2}$ cap function rate-limits capacity accumulation sublinearly ([Section 4.4](/whitepaper/04-mechanisms#beta-distributed-position-caps)).

4. **Debt Assumption Liquidation**: Transferable debt positions with inverted ERC20 semantics eliminate liquidator capital requirements ([Section 4.5](/whitepaper/04-mechanisms#health-factor-and-liquidation)).

5. **Log-Space TWAP Oracle**: Geometric mean temporal averaging with bidirectional spread computation resists flash loan manipulation ([Section 4.6](/whitepaper/04-mechanisms#oracle-twap)).

The remainder of this paper is organized as follows. [Section 2](/whitepaper/02-related-work) surveys related work and positions our contributions against existing protocols. [Section 3](/whitepaper/03-architecture) presents the contract architecture, followed by [Section 4](/whitepaper/04-mechanisms) which details the core mechanisms. [Section 5](/whitepaper/05-anti-spam) describes anti-spam protection, and [Section 6](/whitepaper/06-governance) covers the governance model. [Section 7](/whitepaper/07-security) provides a security analysis under an explicit adversary model. [Section 8](/whitepaper/08-evaluation) presents simulation and gas evaluation results, [Section 9](/whitepaper/09-limitations) discusses limitations, and [Section 10](/whitepaper/10-conclusion) concludes. Appendices A–C provide specifications and reference tables. A companion document (Karun The Rich, 2026) provides extended mathematical analysis, formal proofs, simulation implementations, and reference material.
