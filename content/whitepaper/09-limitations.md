---
title: Limitations and Future Work
prev: '/whitepaper/08-evaluation'
next: '/whitepaper/10-conclusion'
---

# Limitations and Future Work

**Capital Efficiency.** The default 33% LTV requires \$3 of collateral per \$1 borrowed, which is 2.3$\times$ worse than Compound's 75% and 2.8$\times$ worse than Aave V3 E-Mode (93%). Although configurable via lethargic governance, reaching 75% LTV from 33% requires 2 governance cycles (a minimum of 2 months), during which the protocol remains uncompetitive for price-sensitive borrowers. No analysis is provided of what LTV range the target market (XPower tokens on Avalanche) actually requires.

**Formal Verification.** The smart contracts have not undergone formal verification. Given the 10 interacting mechanisms—where locks affect caps, which affect health, which affects liquidation—this represents a significant gap that undermines the security analysis. Formal proofs of health factor correctness, position token conservation, and interest accrual monotonicity are absent. This is the highest-priority future work, recommended via Certora, Halmos, or the K framework.

**Composability Risks.** Wrapped positions (WPosition) interact with external DeFi protocols, yet no analysis addresses how inverted borrow semantics or irrevocable locks behave under composition. External contracts that expect standard ERC20 semantics may mishandle borrow positions.

**Missing Game-Theoretic Analysis.** No model addresses competitive liquidator dynamics under PoW constraints, equilibrium liquidation profit, or oracle sandwich attack quantification. While PoW raises the cost of sandwich attacks, it does not eliminate them.

**Future Directions.** Areas for further development include dynamic parameter adjustment based on market conditions, cross-chain lending via message passing, privacy-preserving positions via zero-knowledge proofs, and integration of additional oracle sources for off-chain price anchoring.
