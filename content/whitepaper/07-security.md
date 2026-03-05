---
title: Security Analysis
prev: '/whitepaper/06-governance'
next: '/whitepaper/08-evaluation'
---

# Security Analysis

## Adversary Model

We consider an adversary $\mathcal{A}$ who controls capital $K$, hash rate $H$, arbitrarily many accounts, governance access with probability $p_g$, and same-block front-running capability. We assume that $\mathcal{A}$ cannot break cryptographic primitives or control more than 50% of consensus.

## Core Security Properties

**Cascade Attenuation ([Theorem 1](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation)).** Because locked supply positions cannot be redeemed, cascade sell pressure is bounded to $(1{-}\phi)$ of the unlocked pool. This attenuates—but does not prevent—cascades. Simulation confirms that at a 25% price shock, unlocked positions suffer 85.7% liquidation versus 29.4% when fully locked ([Section 8](/whitepaper/08-evaluation)).

**Rate-Limited Accumulation.** The $\sqrt{n{+}2}$ divisor bounds per-iteration capacity gain sublinearly. Combined with 7 iterations/week, reaching 99% capacity requires approximately $850\sqrt{n/100}$ iterations. This constitutes rate-limiting rather than Sybil prevention: the long-term share distribution is ultimately determined by initial capital.

**Governance Rate Bound ([Theorem 2](/whitepaper/06-governance)).** Catastrophic parameter changes require 6+ months of sustained malicious governance, providing ample time for detection and response.

**Solvency.** The code enforces $r_{\text{bonus}} \leq s$ and $r_{\text{malus}} \leq s$ independently per parameter. At full lock adoption, the combined constraint $r_{\text{bonus}} + r_{\text{malus}} \leq 2s$ holds at the boundary, with margin approaching zero. The aggregate solvency formula ($r_{\text{bonus}} \cdot \bar{\rho}^S + r_{\text{malus}} \cdot \bar{\rho}^B \leq 2s$) is a sufficient condition that is not directly enforced on-chain; the per-parameter bounds serve as the operative constraints.

## Risk Assessment

| Risk Category | Likelihood | Impact |
|---|---|---|
| Oracle Manipulation | Medium | High |
| Governance Attack | Low | High |
| Liquidation Cascade† | Medium | High |
| Smart Contract Bug | Medium | Critical |
| Keeper Centralization | Medium | High |
| Bad Debt (Extreme Vol.) | Low | Critical |
| Lock Mechanism Abuse | Low | Medium |
| PoW Resource Advantage | Medium | Low |
| Oracle Staleness | Medium | Medium |

† Impact conditional on lock adoption; without locks, impact is High.

**Oracle.** The log-space TWAP with $\alpha = 0.944$ requires approximately 40 hours of sustained manipulation to achieve 90% deviation, and flash loans are ineffective due to the two-tick immunity window. However, the 2+ hour blindness during genuine crashes creates bad-debt risk ([Section 4.6](/whitepaper/04-mechanisms#oracle-twap)).

**Governance.** Parameter changes are bounded by $0.5\times$–$2\times$ per cycle, and guard roles enable emergency revocation. Nevertheless, an attacker who sustains control for 6+ months can achieve significant cumulative drift.

**Smart Contracts.** The implementation uses reentrancy protection via `ReentrancyGuardTransient`, Solidity 0.8+ overflow checks, and OpenZeppelin access control. No formal verification has been performed ([Section 9](/whitepaper/09-limitations)).

Full proofs of the above properties are provided in [Appendix B](/appendices/part-i-math/security-proofs).
