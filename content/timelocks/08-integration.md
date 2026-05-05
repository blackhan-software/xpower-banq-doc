---
title: "8. Integration"
prev:
  text: "7. Gas Analysis"
  link: /timelocks/07-gas-analysis
next:
  text: "9. Conclusion"
  link: /timelocks/09-conclusion
---

## Position Layer

The `Position` contract wraps the `Lock` library, maintaining a parallel lock as a global total tracker:

- **`_lockMore(user, amount, dt_term)`.** Calls `lock.more()` for `user` *and* the global total.
- **`_lockFree(from, to)`.** Sweeps expired slots for source, target, *and* the global total before any transfer — enforcing the `free(tgt)` precondition of [Theorem 6.9](/timelocks/06-proofs#stale-slot-corruption-without-free).
- **`_lockPush(from, to, amount)`.** Proportional lock transfer during position transfer, with fraction $m/d = \texttt{amount}/\texttt{balance}$.

## Graduated Lock Bonus/Malus

The protocol uses the token-second depth to scale interest rates ([Whitepaper §4.7](/whitepaper/04-mechanisms#interest-rates)):

::: definition
**Definition 8.1** (Lock Ratio).

$$\lambda(u) = \frac{\texttt{depthOf}(u)}{\texttt{balanceOf}(u)}$$

where $\lambda \in [0, 1]$ measures normalized commitment depth (since `depthOf` is already normalized to token units by division through $L$, see [§5.7](/timelocks/05-time-lock#_5-7-depthof-user-o-1-cached-depth)).
:::

The implementation reduces the kinked-IR-model spread by an amount proportional to a time-averaged $\lambda$:

$$\overline{\lambda}(u) = \tfrac{1}{2}\bigl(\lambda_{\text{now}}(u) + \lambda_{\text{snap}}(u)\bigr)$$

$$\text{Supply spread:} \quad s_{\text{eff}} = s_0 - \min\!\bigl(s_0,\; \beta_s \cdot \overline{\lambda}(u)\bigr)$$

$$\text{Borrow spread:} \quad s_{\text{eff}} = s_0 - \min\!\bigl(s_0,\; \beta_b \cdot \overline{\lambda}(u)\bigr)$$

where $\lambda_{\text{snap}}$ is the user's lock ratio at the last snapshot, $\beta_s = \texttt{LOCK\_BONUS}$ and $\beta_b = \texttt{LOCK\_MALUS}$ are governance parameters, and $s_0$ is the model's base spread. The supply and borrow rates are then derived from the kinked IR model with the reduced spread; see [Whitepaper §4.7](/whitepaper/04-mechanisms#interest-rates) for the full rate composition.

Supply positions benefit: locked suppliers earn bonus interest proportional to their commitment depth. Borrow positions also benefit: locked borrowers receive a malus that *reduces* their effective borrowing cost, incentivizing long-term commitment on both sides of the market.

For a full game-theoretic analysis of lock adoption incentives, see [Theory: Nash Equilibrium](/theory/03-nash-equilibrium).
