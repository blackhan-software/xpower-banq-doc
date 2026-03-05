# Protocol paper

The first paper in the XPower Banq bundle covers the user-facing protocol mechanics in academic detail.

## Topics

- The Pool / Vault / Position / Oracle / Acma architecture.
- The five core innovations: locked positions, debt-assumption liquidation, lethargic governance, beta-distributed caps, log-space TWAP.
- The default parameter set (66.67% LTV, 50% buffer, 10% spread, etc.) with derivations.
- The 33% conservative floor configuration with derivation.
- ERC20 supply-side and inverted ERC20 borrow-side semantics.
- ERC4626 vault interaction.
- The PoW-gated public liquidation path.

## Companion product docs

The product documentation in this site is built on this paper. The mapping:

- [Concepts](/concepts/lending-basics) → §3 *Protocol Architecture* (Section 2 is *Related Work*; lending fundamentals are spread across §3 and §4).
- [Locked positions](/features/locked-positions/overview) → §4.1 *Locked Positions and Cascade Attenuation*.
- [Debt-assumption liquidation](/features/debt-assumption-liquidation/overview) → §4.2 *Position Transfer Semantics* + §4.5 *Health Factor and Liquidation*.
- [Lethargic governance](/features/lethargic-governance/overview) → §4.3 *Lethargic Governance*.
- [Position caps](/features/position-caps/overview) → §4.4 *Beta-Distributed Position Caps*.
- [TWAP oracle](/features/twap-oracle/overview) → §4.6 *Oracle TWAP*.

For the formal proofs, see [Theory and proofs](/research/papers/theory-and-proofs).

## Where to find the paper

- **PDF:** [`banq-pro.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-pro.pdf) (latest release)
- **Unified bundle:** [`banq-all.pdf`](https://github.com/blackhan-software/xpower-banq-doc/releases/latest/download/banq-all.pdf) — this paper is Part I.
- **All releases:** [github.com/blackhan-software/xpower-banq-doc/releases](https://github.com/blackhan-software/xpower-banq-doc/releases)
