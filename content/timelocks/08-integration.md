---
title: "8. Integration"
prev:
  text: "7. Gas Analysis"
  link: /timelocks/07-gas-analysis
next:
  text: "9. Conclusion"
  link: /timelocks/09-conclusion
---

# 8. Integration

## Position Layer

The `Position` contract wraps the `Lock` library:

- **`_lockMore(user, amount, dt_term)`**: calls `lock.more()` for `user`.
- **`_lockFree(from, to)`**: sweeps expired slots for source and target before any transfer—enforcing the `free(tgt)` precondition of [Theorem 6.9](/timelocks/06-proofs#stale-slot-corruption-without-free).
- **`_lockPush(from, to, amount)`**: proportional lock transfer during position transfer, with fraction $m/d = \texttt{amount}/\texttt{balance}$.

## Graduated Lock Bonus/Malus

The protocol uses the token-second depth to scale interest rates:

::: definition
**Definition 8.1** (Lock Ratio).

$$\lambda(u) = \frac{\texttt{depthOf}(u)}{\texttt{balanceOf}(u) \cdot L}$$

where $\lambda \in [0,1]$ measures normalized commitment depth.
:::

Interest rate adjustments:

$$\text{Supply:} \quad r_{\text{eff}} = r_{\text{base}} \cdot (1 + \beta_s \cdot \lambda)$$

$$\text{Borrow:} \quad r_{\text{eff}} = r_{\text{base}} \cdot (1 - \beta_b \cdot \lambda)$$

where $\beta_s = \texttt{LOCK\_BONUS}$ and $\beta_b = \texttt{LOCK\_MALUS}$ are governance parameters bounded by the spread.

Supply positions benefit: locked suppliers earn bonus interest proportional to their commitment depth. Borrow positions also benefit: locked borrowers receive a malus that *reduces* their effective borrowing cost, incentivizing long-term commitment on both sides of the market.

For a full game-theoretic analysis of lock adoption incentives, see [Appendix C: Lock Incentive Analysis](/appendices/part-i-math/lock-incentive-analysis).
