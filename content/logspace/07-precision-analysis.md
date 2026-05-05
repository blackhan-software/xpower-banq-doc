---
title: "7. Precision Analysis"
prev:
  text: "6. Gas Analysis"
  link: /logspace/06-gas-analysis
next:
  text: "8. Adversarial Analysis"
  link: /logspace/08-adversarial-analysis
---

## Theoretical Bound

The multiplicative form performs two rounding steps per accrual:

$$I_{n+1} = \underbrace{\texttt{ud}(I_n).\texttt{mul}}_{\text{round 2}}\bigl(\underbrace{\exp(\texttt{ud}(r))}_{\text{round 1}}\bigr).$$

Both `exp()` and `mul()` truncate toward zero. Over $N$ accrual steps, the systematic negative bias compounds: each truncated intermediate becomes the input to the next multiplication.

The log-space form accumulates yields by exact integer addition:

$$L_{n+1} = L_n + r_n \qquad \text{(exact, no overflow)}.$$

At read-time, a single `exp()` operates on the exact cumulative sum:

$$\text{total} = \texttt{mulDiv}\bigl(p_u,\; \exp(L - L_u),\; 10^{18}\bigr).$$

Two independent rounding steps on the exact sum vs. $2N$ compounded rounding steps on intermediate products.

::: theorem
**Theorem 7.1** (Precision Advantage). *The log-space index accumulates zero rounding error during accrual. The total read-time error is bounded by 2 ULP (units in the last place) at WAD precision — at most 2 wei per $10^{18}$ tokens. The multiplicative index accumulates up to $2N$ ULP of compounded truncation bias over $N$ accrual steps.*
:::

## Empirical Measurement

Measured against a 12-month accrual scenario at 10% APR, 90% utilization:

| Value | RAY result | Log result |
|---|---:|---:|
| `supply.totalOf` (12M) | …647**609** | …647**619** |
| `borrow.totalOf` (12M) | …082**848** | …082**857** |
| supply (2nd accr.) | …130**615** | …130**635** |

<small>Analytical value: $\exp(0.1) = 1.1051\ldots 7624 \times 10^{18}$.</small>

The analytical value confirms the log-space result (…619) is closer than the RAY result (…609). The log-space form is consistently $+10$–$20$ wei closer to the true value.

## Root Cause

The precision advantage is a direct consequence of the identity $\sum \log x_i = \log \prod x_i$: summation in log-space is exact where repeated multiplication in linear-space compounds truncation errors. This property — well-known in numerical analysis as the advantage of log-sum-exp over iterated products [\[higham2002\]](/reference/bibliography#higham2002) — translates directly to on-chain interest index design.

The worst-case truncation error growth is bounded as follows:

| Index | Worst-case error after $N$ accruals |
|---|---|
| Multiplicative | $\leq 2N$ ULP |
| Log-space | $\leq 2$ ULP (constant) |
