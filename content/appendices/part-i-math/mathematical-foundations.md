---
title: "Appendix A: Mathematical Foundations"
description: "Formal definitions for interest accrual, time-weighted integration, oracle price aggregation, rate limiting, and spread scaling."
---

# Appendix A: Mathematical Foundations

## Interest Accrual

Interest accrues via continuous compounding with ray precision (27 decimals).

::: definition
**Definition 1** (Position Index). The global index $I_t$ at time $t$ with annual rate $r\text{:}$

$$I_t = I_0 \cdot e^{r \cdot (t - t_0) / T_{\text{year}}}$$

where $T_{\text{year}} = 365.25 \times 86400 = 31{,}557{,}600$ seconds.
:::

::: theorem
**Theorem 1** (Balance Accrual). *A user's total balance $B_t$ given principal $P$ and checkpoint index $I_u\text{:}$*

$$B_t = P \cdot \frac{I_t}{I_u}$$
:::

## Time-Weighted Integration

::: definition
**Definition 2** (Time-Weighted Mean). For parameter values $\theta_i$ at times $t_i\text{:}$

$$\bar{\theta}(t) = \frac{\sum_{i=0}^{n-1} \theta_i \cdot (t_{i+1} - t_i) + \theta_n \cdot (t - t_n)}{t - t_0}$$
:::

## Oracle Price Aggregation

::: definition
**Definition 3** (Log-Space TWAP Quote). Each refresh queries the AMM bidirectionally and computes:

$$\begin{aligned}
m_t &= \log_2(\bar{p}_t) && \text{(log mid price)} \\
s^{AB}_{t,log} &= \log_2(1 + s^{AB}_t) && \text{(log spread AB)} \\
s^{BA}_{t,log} &= \log_2(1 + s^{BA}_t) && \text{(log spread BA)} \\
r_t &= \tfrac{1}{2}\bigl(s^{AB}_{t,log} + s^{BA}_{t,log}\bigr) && \text{(log geomean spread)}
\end{aligned}$$

The EMA smooths in log space with decay $\alpha\text{:}$

$$\begin{aligned}
\overline{m}_t &= \alpha \cdot \overline{m}_{t-1} + (1{-}\alpha) \cdot m_{t} \\
\overline{r}_t &= \alpha \cdot \overline{r}_{t-1} + (1{-}\alpha) \cdot r_{t}
\end{aligned}$$
:::

::: definition
**Definition 4** (Spread Scaling). For position size $n$ tokens and base spread $s = 2^{\overline{r}} - 1\text{:}$

$$x = n \cdot s, \quad \mu = \log_2(2x + 2), \quad s' = s \cdot \mu$$

Final quotes: $\text{bid}(n) = \text{value} - s' \cdot \text{value}/2$, $\text{ask}(n) = \text{value} + s' \cdot \text{value}/2$.
:::

## Rate Limiting

::: definition
**Definition 5** (Token Bucket). A rate limiter with capacity $C$, regeneration rate 1/second, and cost $c\text{:}$

$$C'(t) = \min\left(C_{\max}, C(t_{\text{last}}) + (t - t_{\text{last}})\right) - c$$

Operation allowed iff $C'(t) \geq 0$.
:::
