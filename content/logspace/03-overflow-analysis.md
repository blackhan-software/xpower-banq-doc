---
title: "3. Overflow Analysis"
prev:
  text: "2. Related Work"
  link: /logspace/02-related-work
next:
  text: "4. Log-Space Index"
  link: /logspace/04-log-space-index
---

## Budget Computation

::: definition
**Definition 3.1** (Multiplicative Index). The global index $I(t)$ tracks cumulative interest via iterated multiplication:

$$I(t) = I_0 \cdot \prod_{i=1}^{N} \exp(r_i \cdot \Delta t_i)$$

where $I_0 = 10^{27}$ (RAY), $r_i$ is the annualised rate at step $i$, and $\Delta t_i$ is the elapsed time in seconds.
:::

A `uint256` holds $2^{256} \approx 1.16 \times 10^{77}$. Starting at $\text{RAY} = 10^{27}$, the maximum growth factor before overflow is

$$G_{\max} = \frac{2^{256}}{\text{RAY}} \approx 1.16 \times 10^{50}.$$

In terms of natural logarithm,

$$\ln(G_{\max}) = \ln(2^{256}) - \ln(10^{27}) \approx 177.4 - 62.2 = 115.3.$$

The index can accumulate at most $\sim 115$ e-folds of growth.

## Time-to-Overflow

Per-period yield: $r_{\text{wad}} = r_{\text{annual}} \times \Delta t / \text{YEAR}$, where $\text{YEAR} = 365.25 \times 86{,}400 = 31{,}557{,}600$ seconds. Cumulative yield to overflow: $\sim 115.3 \times 10^{18}$ (WAD).

| Annual Rate | Scenario | Time |
|---:|---|---:|
| 10% | Normal operations | $\sim 1{,}154$ yr |
| 50% | Elevated utilization | $\sim 231$ yr |
| 200% | `Rate.by` cap | $\sim 57.7$ yr |
| 400% | 200% + 100% spread | $\sim 28.9$ yr |

The 200% cap originates from `Rate.by()`, which clamps output at `Constant.TWO` ($2 \times 10^{18}$). The borrow-side spread multiplies this further: $r_{\text{borrow}} = r_{\text{base}} \times (1 + s)$, where $s$ is the spread parameter.

## Boundedness of Other Values

Every other protocol value is bounded:

- **Utilization.** $\leq 10^{18}$ by definition.
- **Rates.** Capped at $2 \times 10^{18}$ by `Rate.by`.
- **Parameters.** Governed within $0.5\times$–$2\times$ bands per cycle ([Whitepaper §4.3](/whitepaper/04-mechanisms#lethargic-governance)).
- **Balances.** Linear in token supply, bounded by `uint224` caps.
- **Oracle.** Log-space TWAP stores $\log_2(\text{price})$ ([Whitepaper §4.6](/whitepaper/04-mechanisms#oracle-twap)).
- **Lock intermediates.** Bounded by position size times yield fraction ([Time Locks](/timelocks/01-introduction)).

The compounding index is the sole unbounded exponential.
