# XPower Banq

**Lending, but the cascades stop here.**

XPower Banq is a permissionless DeFi lending protocol on the Ethereum Virtual Machine. It introduces optionally locked positions, lethargic governance, beta-distributed caps, debt-assumption liquidation, and a log-space TWAP oracle — together yielding 66.67% LTV with a 50% over-collateralisation buffer at default parameters.

## Highlights

- **[Optionally locked positions](features/locked-positions/overview.md)** — lock supply or borrow for a fixed term and earn (or pay) less. Locked supply can't be dumped during a crash, attenuating cascades by factor (1 − ϕ).
- **[Lethargic governance](features/lethargic-governance/overview.md)** — every parameter change is bounded to 0.5×–2× per cycle and phases in asymptotically. A 10× change requires ~4 months.
- **[Debt-assumption liquidation](features/debt-assumption-liquidation/overview.md)** — liquidators don't need liquid capital; they atomically take on the victim's debt and collateral.
- **[Log-space TWAP oracle](features/twap-oracle/overview.md)** — geometric-mean temporal averaging with bidirectional spread computation. Two-tick flash-loan immunity.
- **[Beta-distributed caps](features/position-caps/overview.md)** — Sybil capacity gain rate-limited to O(√n).
- **Composable by design** — supply and borrow positions are ERC20s, vaults are ERC4626. See the [architecture overview](for-developers/architecture-overview.md).

## Defaults you can read in one line

The protocol ships at **66.67% LTV** with a **50% over-collateralisation buffer**, a **10% interest rate spread**, and an oracle decay of **α = 0.944** (12-hour half-life). These defaults are reachable down to a **33% conservative floor** in one lethargic cycle — and at that floor, Monte Carlo simulation shows zero bad debt even for a 50% crash.

## Where to go next

- **New here?** → [What is XPower Banq](introduction/what-is-xpower-banq.md) and [How it works](introduction/how-it-works.md)
- **Want to use it?** → [Quickstart](introduction/quickstart.md) and [Supplying assets](using-the-protocol/supplying-assets.md)
- **Building on top?** → [Architecture overview](for-developers/architecture-overview.md) and the [Integration guide](for-developers/integration-guide.md)
- **Worried about risk?** → Start with [Risks overview](risks/overview.md); we don't bury the limitations
- **Want the math?** → The [Whitepaper](research/whitepaper.md) and the five companion papers
