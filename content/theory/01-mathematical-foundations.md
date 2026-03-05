---
title: "1. Mathematical Foundations"
prev: false
next:
  text: "2. Formal Proofs"
  link: /theory/02-formal-proofs
---

## Interest Accrual

Interest accrues via continuous compounding with ray precision (27 decimals).

::: definition
**Definition 1.1** (Position Index). The global index $I_t$ at time $t$ with annual rate $r$ is

$$I_t = I_0 \cdot e^{r \cdot (t - t_0) / T_{\text{year}}}$$

where $T_{\text{year}} = 365.25 \times 86400 = 31{,}557{,}600$ seconds. (`YEAR = CENTURY/100` with `CENTURY = 365_25` days, i.e. $36525 \cdot 86400 / 100 = 31{,}557{,}600$ s, to keep the constant integer-valued in Solidity.)
:::

::: theorem
**Theorem 1.2** (Balance Accrual). *A user's total balance $B_t$ given principal $P$ and checkpoint index $I_u$ is*

$$B_t = P \cdot \frac{I_t}{I_u}.$$
:::

> **Piecewise integration in practice.** In the shipped contracts, $r$ is not a single constant but a function of utilization $r(t) = \hat r(\text{util}(t))$, and the index is integrated piecewise:
>
> $$\log I_t - \log I_0 = \sum_i \hat r(\text{util}_i) \cdot (t_{i+1} - t_i)/T_{\text{year}}$$
>
> with re-indexings driven by every state-changing call. See `Position._indexOf` and `Position._reindex`; this matches the time-weighted framing of [Definition 1.3](#time-weighted-integration). The shipped contract additionally stores the index in log-space rather than as a multiplicative product — see [Log-Space Compounding Index](/logspace/01-introduction).

## Time-Weighted Integration

::: definition
**Definition 1.3** (Time-Weighted Mean). For parameter values $\theta_i$ at times $t_i$,

$$\bar{\theta}(t) = \frac{\sum_{i=0}^{n-1} \theta_i \cdot (t_{i+1} - t_i) + \theta_n \cdot (t - t_n)}{t - t_0}.$$
:::

## Oracle Price Aggregation

::: definition
**Definition 1.4** (Log-Space TWAP Quote). Each refresh queries the AMM bidirectionally and computes

$$m_t = \log_2(\bar{p}_t) \qquad \text{(log mid price)}$$

$$s^{AB}_{t,\log} = \log_2(1 + s^{AB}_t), \quad s^{BA}_{t,\log} = \log_2(1 + s^{BA}_t)$$

$$r_t = \tfrac{1}{2}\bigl(s^{AB}_{t,\log} + s^{BA}_{t,\log}\bigr) \qquad \text{(log geomean spread)}.$$

The EMA smooths in log space with decay $\alpha$, blending the previous mean with the *previously stored* sample (the contract maintains a one-sample buffer: `TWAPLib.update` reads `last_mid = midOf(last)` *before* overwriting `twap_.last` with the new $m_t$, so the new sample enters the mean only at the next refresh):

$$\overline{m}_t = \alpha \cdot \overline{m}_{t-1} + (1{-}\alpha) \cdot m_{t-1}$$

$$\overline{r}_t = \alpha \cdot \overline{r}_{t-1} + (1{-}\alpha) \cdot r_{t-1}$$

where $m_{t-1}$ (resp. $r_{t-1}$) denotes the most recent sample observed strictly *before* the current refresh.
:::

::: definition
**Definition 1.5** (Spread Scaling). Let $n = \texttt{amount}/\texttt{unit\_source}$ be the position expressed in *whole units* of the source asset (so a 1.5 ETH order has $n = 1.5$, not $1.5 \cdot 10^{18}$). With base spread $s = 2^{\overline{r}} - 1$,

$$x = n \cdot s, \quad \mu = \log_2(2x + 2), \quad s' = s \cdot \mu.$$

Final quotes: $\text{bid}(n) = \text{value} - s' \cdot \text{value}/2$, $\text{ask}(n) = \text{value} + s' \cdot \text{value}/2$. Implemented in `Oracle._hlfSpread` / `Oracle._center`.
:::

## Rate Limiting

::: definition
**Definition 1.6** (Token Bucket). A rate limiter with capacity $C_{\max}$, regeneration rate 1 unit per wall-clock second (a hard-coded design choice, not a governable parameter), and per-call cost $c$ supplied by the caller:

$$C'(t) = \min\bigl(C_{\max},\; C(t_{\text{last}}) + (t - t_{\text{last}})\bigr) - c.$$

Operation allowed iff $C'(t) \geq 0$. Implementation: `RateLimited._ratelimitedCheck` regenerates first, reverts if $C(t_{\text{last}}) + (t - t_{\text{last}}) < c$, then commits the post-decrement state — algebraically equivalent to the post-cost residual $C'(t) \geq 0$.
:::
