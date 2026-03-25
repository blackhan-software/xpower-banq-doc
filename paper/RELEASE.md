> 🏦 XPower Banq protocol documentation; see also [docs.xpowerbanq.com]! 📖👀

[docs.xpowerbanq.com]: https://docs.xpowerbanq.com

## 📄 Whitepaper

The whitepaper presents **XPower Banq**, a permissionless DeFi lending protocol on the Ethereum Virtual Machine (deployed on Avalanche). It covers protocol architecture, core mechanisms, security analysis, and empirical evaluation. Key contributions include optionally locked positions, lethargic governance, beta-distributed position caps, debt assumption liquidation, and log-space TWAP oracles.

## 🔒 Ring-Buffer Time Locks

The lock paper presents a 16-slot quarterly ring buffer for managing time-locked DeFi positions in constant per-slot storage with bitmap-guided O(k) sweep (k ≤ 16). The key contribution is an O(1) cached depth metric: by storing the epoch-weighted sum, exact token commitments can be reconstructed via an algebraic identity without iteration. Lock writes are constant-cost; queries are O(1) or O(k); proportional transfer runs in O(k). The mechanism drives graduated lock bonus/malus on interest rates in the XPower Banq lending protocol.

## ⚙️ Log-Space Compounding Index

The log-index paper presents an overflow-free interest index via additive log-space accumulation. By storing the cumulative sum of per-period yields instead of the exponentiated product, accrual becomes addition — eliminating the overflow horizon of the multiplicative RAY index. The paper provides the mathematical foundation, complete Solidity code transformation, gas benchmarks, and precision analysis showing the log-space form is numerically closer to analytical values.

## 📐 Mathematical Theory & Proofs

The theory paper provides the formal foundations of the protocol: interest accrual, oracle price aggregation, and Nash equilibrium analysis of lock adoption incentives. It collects the lemmas, theorems, and proofs underpinning the whitepaper's design claims.

## 📊 Simulations & Risk Analysis

The simulation paper documents the empirical evaluation: capacity accumulation, liquidation cascade, TWAP oracle, and bad-debt risk simulations, along with implementation details and parameter sensitivity studies.

## 📚 References & Glossary

The reference paper consolidates protocol parameters, constants, terminology, and bibliographic references shared across the suite. It is included in the unified bundle and is not intended to stand alone.

## 📦 Downloads

| PDF            | Description                  |
| -------------- | ---------------------------- |
| `banq-all.pdf` | All Papers Combined          |
| `banq-pro.pdf` | Protocol Whitepaper          |
| `banq-lck.pdf` | Ring-Buffer Time Locks       |
| `banq-log.pdf` | Log-Space Compounding Index  |
| `banq-mtp.pdf` | Mathematical Theory & Proofs |
| `banq-sim.pdf` | Simulations & Risk Analysis  |
| `banq-ref.pdf` | References & Glossary        |
