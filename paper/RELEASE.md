> XPower Banq protocol documentation; see also [docs.xpowerbanq.com]! 📖👀

[docs.xpowerbanq.com]: https://docs.xpowerbanq.com

## 📄 Whitepaper

The whitepaper presents **XPower Banq**, a permissionless DeFi lending protocol on the Ethereum Virtual Machine (deployed on Avalanche). It covers protocol architecture, core mechanisms, security analysis, and empirical evaluation. Key contributions include optionally locked positions, lethargic governance, beta-distributed position caps, debt assumption liquidation, and log-space TWAP oracles.

## 📐 Appendices

The companion appendices document provides extended technical material in three parts:

- **Part I — Mathematical Theory & Proofs**: formal foundations for interest accrual, oracle price aggregation, and Nash equilibrium analysis of lock adoption incentives.

- **Part II — Simulations & Risk Analysis**: capacity accumulation, liquidation cascade, TWAP oracle, and bad debt risk simulations with implementation details.

- **Part III — References & Glossary**: protocol parameters, constants, and terminology.

## 🔒 Ring-Buffer Time Locks

The lock paper presents a 16-slot quarterly ring buffer for managing time-locked DeFi positions in constant per-slot storage with bitmap-guided O(k) sweep (k ≤ 16). The key contribution is an O(1) cached depth metric: by storing the epoch-weighted sum, exact token-seconds can be reconstructed via an algebraic identity using three SLOADs and no iteration. Each lock requires 2–3 SSTOREs; each query requires 1–3 SLOADs; proportional transfer runs in O(k). The mechanism drives graduated lock bonus/malus on interest rates in the XPower Banq lending protocol.

## 📊 Log-Space Compounding Index

The log-index paper presents an overflow-free interest index via additive log-space accumulation. By storing the cumulative sum of per-period yields instead of the exponentiated product, accrual becomes addition — eliminating the ~115 e-fold overflow horizon of the multiplicative RAY index. The paper provides the mathematical foundation, complete Solidity code transformation, gas benchmarks (−114,447 gas net across 23 operations), and precision analysis showing the log-space form is numerically closer to analytical values.

## 📦 Downloads

| PDF            | Description             |
| -------------- | ----------------------- |
| `banq-pro.pdf` | Protocol Whitepaper     |
| `banq-apx.pdf` | Technical Appendices    |
| `banq-lck.pdf` | Ring-Buffer Time Locks  |
| `banq-log.pdf` | Log-Space Compounding   |
| `banq-all.pdf` | All Papers Combined     |
