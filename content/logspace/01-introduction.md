---
title: "1. Introduction"
prev: false
next:
  text: "2. Related Work"
  link: /logspace/02-related-work
---

Compounding interest indices in DeFi lending protocols grow exponentially and eventually overflow fixed-width integer storage. The standard multiplicative index — a running product of $\exp(r_i)$ factors stored in `uint256` at RAY precision ($10^{27}$) — exhausts its 115.3 e-folds of headroom in as few as 29 years under worst-case rate assumptions.

We present a **log-space compounding index** that replaces the stored product with its logarithm: accrual becomes addition ($L \leftarrow L + r$), and the growth factor is reconstructed on demand via $\exp(L - L_u)$. The transformation eliminates overflow entirely (linear accumulation: $\sim 5\times 10^{5}$–$10^{58}$ years depending on the chosen field width), replaces write-path exponentiation with addition, and defers `exp()` to individual read paths. Counter-intuitively, it *improves* numerical precision by avoiding the compounded truncation bias inherent in iterated fixed-point multiplication.

## Background

Interest-bearing positions in DeFi lending protocols — Compound [\[compound2019\]](/reference/bibliography#compound2019), Aave [\[aave2020\]](/reference/bibliography#aave2020), Euler [\[euler2022\]](/reference/bibliography#euler2022) — track accrued interest via a *global compounding index*. On each accrual event, the index is multiplied by a growth factor $\exp(r \cdot \Delta t)$, where $r$ is the current interest rate. A user's accrued balance is recovered as $\text{principal} \times I(t) / I(t_u)$, where $I(t_u)$ is the index value snapshotted at the user's last interaction.

This design, while mathematically clean, stores the cumulative product of exponentials in a fixed-width integer. In Solidity's `uint256` at RAY precision ($10^{27}$), the index has approximately 115.3 e-folds of growth before overflow. At the XPower Banq protocol's maximum rate of 200% (the `Rate.by` cap [\[wp\]](/whitepaper/01-introduction)), this budget is exhausted in $\sim 57.7$ years; with borrow-side spread at 100% utilization, in $\sim 28.9$ years.

## Observation

The index is the *only* unbounded value in the protocol. Utilization is bounded by 1, rates are capped at $2 \times 10^{18}$, balances and principals are bounded by token supply, and oracle prices are stored in log-space. The compounding index is the sole exponential.

## Contribution

We observe that the logarithm of the multiplicative index is exactly the cumulative sum of per-period yields — a quantity already computed in the accrual path. By storing this sum directly, accrual becomes addition (overflow-free for $\sim 10^{58}$ years), the expensive `exp()` call moves from the global write path to individual read paths, and truncation error is reduced from $O(N)$ compounded rounding steps to a single rounding at query time.

## Roadmap

[Section 2](/logspace/02-related-work) surveys related work on interest index design and fixed-point overflow. [Section 3](/logspace/03-overflow-analysis) quantifies the overflow horizon. [Section 4](/logspace/04-log-space-index) presents the log-space index with formal definitions and invariants. [Section 5](/logspace/05-code-transformation) details the code transformation. [Section 6](/logspace/06-gas-analysis) provides gas benchmarks. [Section 7](/logspace/07-precision-analysis) analyses precision. [Section 8](/logspace/08-adversarial-analysis) examines adversarial considerations. [Section 9](/logspace/09-limitations) discusses limitations and future work. [Section 10](/logspace/10-conclusion) concludes.
