---
title: "2. Related Work"
prev:
  text: "1. Introduction"
  link: /logspace/01-introduction
next:
  text: "3. Overflow Analysis"
  link: /logspace/03-overflow-analysis
---

**Compound cToken Index** [\[compound2019\]](/reference/bibliography#compound2019)**.** Compound introduced the `exchangeRate` index for cTokens, compounded per block via $I_{n+1} = I_n \times (1 + r \cdot \Delta t)$. The linear approximation $(1+x)$ avoids the `exp()` call but introduces compounding error that grows with block frequency. The index shares the same overflow exposure as any multiplicative accumulator.

**Aave Liquidity Index** [\[aave2020\]](/reference/bibliography#aave2020)**.** Aave uses a RAY-precision ($10^{27}$) liquidity index with the same multiplicative structure: $I_{n+1} = I_n \times (1 + r \cdot \Delta t / \text{YEAR})$. The RAY scale provides 62.2 e-folds of precision overhead, leaving 115.3 e-folds for growth — the same budget analysed in this paper.

**PRBMath UD60x18** [\[prbmath\]](/reference/bibliography#prbmath)**.** The PRBMath library provides fixed-point `exp()` and `mul()` at WAD precision ($10^{18}$). The `exp()` function reverts when the input exceeds $133.08 \times 10^{18}$, imposing a secondary constraint on single-step yield that is not reachable under normal reindexing. The XPower Banq multiplicative index uses PRBMath for its `Rate.accrue` computation.

**Log-Sum-Exp in Numerical Analysis.** The identity $\sum \log x_i = \log \prod x_i$ is a classical tool for avoiding floating-point overflow in iterated products [\[higham2002\]](/reference/bibliography#higham2002). The log-sum-exp trick [\[blanchard2021\]](/reference/bibliography#blanchard2021) stabilises softmax computation in machine learning by shifting to log-space. Our contribution applies this well-known principle to on-chain interest index design, where the constraint is not floating-point range but `uint256` capacity.

**Uniswap v3 Tick Accumulators** [\[uniswap2021\]](/reference/bibliography#uniswap2021)**.** Uniswap v3 stores cumulative $\log_{1.0001}(\text{price})$ in `int56` accumulators that grow additively and support modular-arithmetic subtraction for TWAP computation. The XPower Banq oracle similarly stores $\log_2(\text{price})$ additively. Our log-space interest index extends this pattern from price accumulators to compounding interest.

## Comparison of Interest Index Representations

|  | Multiplicative (RAY) | Log-Space (WAD) |
|---|---|---|
| Accrual op. | $I \times \exp(r)$ | $L + r$ |
| Storage | $10^{27}$ scale | $10^{18}$ scale |
| Growth | Exponential | Linear |
| Overflow | $\sim 115$ e-folds | $\sim 10^{58}$ yr |
| Write gas | $\sim 1{,}200$ | $\sim 3$ |
| Read gas | $\sim 100$ | $\sim 1{,}200$ |
| Rounding | $2N$ steps | $2$ steps |
