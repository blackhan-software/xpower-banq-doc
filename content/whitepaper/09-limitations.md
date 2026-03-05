---
title: "9. Limitations & Future Work"
prev:
  text: "8. Evaluation"
  link: /whitepaper/08-evaluation
next:
  text: "10. Conclusion"
  link: /whitepaper/10-conclusion
---

## Capital Efficiency

The default 66.67% LTV requires \$1.50 of collateral per \$1 borrowed — comparable to Compound's 75% and within 25 percentage points of Aave V3 E-Mode (93%). [Lethargic governance](/whitepaper/04-mechanisms#lethargic-governance) bounds each cycle to $0.5\times$–$2\times$ the prior target, so the default is reachable down to a 33% conservative floor in one cycle, and the [bad-debt analysis](/simulations/04-bad-debt-risk) characterises the risk profile across the LTV configurations swept therein; no analysis is provided of what LTV range the target market (XPower tokens on Avalanche) actually requires.

## Formal Verification

The smart contracts have not undergone formal verification. Given the 10 interacting mechanisms — where locks affect caps, which affect health, which affects liquidation — this represents a significant gap that undermines the security analysis. Formal proofs of health factor correctness, position token conservation, and interest accrual monotonicity are absent. This is the highest-priority future work, recommended via Certora, Halmos, or the K framework.

## Composability Risks

Wrapped positions (WPosition) interact with external DeFi protocols, yet no analysis addresses how inverted borrow semantics or irrevocable locks behave under composition. External contracts that expect standard ERC20 semantics may mishandle borrow positions.

## Missing Game-Theoretic Analysis

No model addresses competitive liquidator dynamics under PoW constraints, equilibrium liquidation profit, or oracle sandwich attack quantification. While PoW raises the cost of sandwich attacks, it does not eliminate them.

## Future Directions

Areas for further development include dynamic parameter adjustment based on market conditions, cross-chain lending via message passing, privacy-preserving positions via zero-knowledge proofs, and integration of additional oracle sources for off-chain price anchoring.
