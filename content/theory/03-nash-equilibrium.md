---
title: "3. Nash Equilibrium Analysis"
prev:
  text: "2. Formal Proofs"
  link: /theory/02-formal-proofs
next: false
---

This section analyzes the game-theoretic equilibrium of lock adoption. We model rational actors choosing between locked and unlocked positions, accounting for APY differentials, secondary market dynamics, and liquidation seniority.

## Model Setup

### Position Types and Rates

With spread $s = 10\%$ and $r_{\text{bonus}} = r_{\text{malus}} = s$:

| Position Type | Rate Multiplier | APY vs. Base |
|---|---:|---:|
| Unlocked Supplier | $(1-s) = 0.90$ | $-10\%$ |
| Locked Supplier | $(1+r_{\text{bonus}})(1-s) = 0.99$ | $-1\%$ |
| Unlocked Borrower | $(1+s) = 1.10$ | $+10\%$ |
| Locked Borrower | $(1-r_{\text{malus}})(1+s) = 0.99$ | $-1\%$ |

The **APY differential** between locked and unlocked positions:

$$\Delta r = r_{\text{base}} \times (1-s) \times r_{\text{bonus}} = r_{\text{base}} \times 0.9 \times 0.1 = 0.09 \times r_{\text{base}}.$$

### Secondary Market Dynamics

Position tokens are ERC20-transferable, enabling secondary market trading. However, locked positions trade at a **discount** $D$ relative to NAV because:

1. Locked positions cannot be redeemed for underlying assets.
2. Exit is only possible via secondary market sale.
3. Lock status transfers proportionally with tokens (buyers receive locked tokens).

The discount $D$ is endogenous to market conditions, typically ranging from 3–10% (empirical range observed in secondary markets for illiquid DeFi positions: Lido stETH traded at 6–7% discount during the June 2022 liquidity crisis; Convex cvxCRV has traded at 5–12% discount to CRV due to permanent lock-up), based on:

- Secondary market liquidity depth.
- Expected holding period of market participants.
- Overall lock adoption rate (affecting liquidity).

## Player Utility Functions

### Supplier Utility

For a supplier with lock ratio $\rho \in [0, 1]$ and holding period $T$:

**Unlocked position** ($\rho = 0$):

$$U_{\text{unlocked}} = P \times (1 + r_{\text{unlocked}})^T.$$

**Locked position** ($\rho = 1$):

$$U_{\text{locked}} = P \times (1 + r_{\text{locked}})^T \times (1 - D).$$

The $(1-D)$ factor reflects the secondary market discount on exit.

### Breakeven Condition

Lock adoption is rational when $U_{\text{locked}} > U_{\text{unlocked}}$:

$$(1 + r_{\text{locked}})^T \times (1 - D) > (1 + r_{\text{unlocked}})^T.$$

Solving for the **breakeven holding period** $T^*$:

$$T^* = \frac{\ln(1-D)}{\ln(1 + r_{\text{unlocked}}) - \ln(1 + r_{\text{locked}})} \approx \frac{D}{\Delta r}.$$

## Breakeven Analysis by Utilization

The base interest rate $r_{\text{base}}$ varies with utilization $U$ according to the [piecewise-linear model](/whitepaper/04-mechanisms#interest-rates).

| Utilization $U$ | Base Rate $r$ | Differential $\Delta r$ | $T^*$ ($D = 5\%$) | $T^*$ ($D = 3\%$) |
|---:|---:|---:|---:|---:|
| 80% | 8.9% | 0.80% | 6.3 y | 3.8 y |
| 90% | 10% | 0.90% | 5.6 y | 3.3 y |
| 95% | 55% | 4.95% | 12 m | 7 m |
| 98% | 82% | 7.38% | 8 m | 5 m |
| 100% | 100% | 9.0% | 6.7 m | 4 m |

Lock adoption thus becomes economically attractive primarily during high-utilization periods ($U > 95\%$), precisely when cascade prevention is most valuable.

## Liquidation Seniority Value

Locked positions gain *de facto* seniority in liquidations because liquidators prefer unlocked positions (immediate liquidity). The seniority value $S(\bar{\rho})$ depends on aggregate lock adoption $\bar{\rho}$ (denoted $\phi$ in the [Cascade Attenuation Theorem](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation)):

$$S(\bar{\rho}) \approx P(\text{liquidation}) \times (1 - \bar{\rho}) \times L_{\text{loss}}$$

where $P(\text{liquidation})$ is the probability of a liquidation event and $L_{\text{loss}}$ is the expected loss in liquidation.

This creates a **coordination game**: seniority value decreases as lock adoption increases. At $\bar{\rho} = 0$, locked positions have maximum seniority; at $\bar{\rho} = 1$, no differentiation exists.

## Nash Equilibrium Characterization

### Equilibrium Condition

At equilibrium lock adoption $\bar{\rho}^*$, the marginal user is indifferent between locking and not locking:

$$\underbrace{\Delta r \times T}_{\text{APY benefit}} + \underbrace{S(\bar{\rho}^*)}_{\text{Seniority}} = \underbrace{D}_{\text{Discount cost}}.$$

### Utilization-Dependent Equilibria

| Utilization Regime | Base Rate | Expected $\bar{\rho}^*$ | Protocol Margin |
|---|---:|---:|---:|
| Normal ($U \in [0, 90\%)$) | $<10\%$ | 10–20% | 16–18% of $r$ |
| Elevated ($U \in [90\%, 95\%)$) | 10–55% | 20–40% | 12–16% of $r$ |
| Stressed ($U \in [95\%, 100\%]$) | $>55\%$ | 40–70% | 6–12% of $r$ |

The mechanism aligns incentives with protocol needs: under normal conditions, low lock adoption preserves revenue, while under stressed conditions, high adoption provides cascade protection when it is most needed.

## Protocol Margin Analysis

### Margin as Function of Lock Adoption

Protocol margin per unit interest flow:

$$M(\bar{\rho}) = 2s - r_{\text{bonus}} \times \bar{\rho}^S - r_{\text{malus}} \times \bar{\rho}^B.$$

With $r_{\text{bonus}} = r_{\text{malus}} = s$ and assuming $\bar{\rho}^S = \bar{\rho}^B = \bar{\rho}$:

$$M(\bar{\rho}) = 2s(1 - \bar{\rho}).$$

| Lock Adoption $\bar{\rho}$ | Margin | Retention |
|---:|---:|---:|
| 0% | 20% of $r$ | 100% |
| 25% | 15% of $r$ | 75% |
| 50% | 10% of $r$ | 50% |
| 75% | 5% of $r$ | 25% |
| 100% | 0% of $r$ | 0% |

### Solvency at Full Adoption

The default configuration operates at the solvency boundary:

$$r_{\text{bonus}} + r_{\text{malus}} = s + s = 2s \quad \checkmark$$

Protocol solvency is maintained for any $\bar{\rho} \in [0, 1]$, though margin approaches zero as $\bar{\rho} \to 1$.

## Stability Analysis

### Multiple Equilibria

The lock adoption game exhibits **multiple equilibria** due to the endogenous discount:

1. **Low-adoption equilibrium** ($\bar{\rho}^* \approx 10\%$). Thin secondary market ⇒ high discount $D$ ⇒ locking unattractive ⇒ low adoption (self-reinforcing).
2. **High-adoption equilibrium** ($\bar{\rho}^* \approx 60\%$). Deep secondary market ⇒ low discount $D$ ⇒ locking attractive ⇒ high adoption (self-reinforcing).

### Equilibrium Selection

The realized equilibrium depends on:

- **Initial conditions.** Early lock adoption seeds secondary market liquidity.
- **Utilization dynamics.** High-utilization periods push toward high-adoption equilibrium.
- **External liquidity.** Protocol-seeded liquidity can bootstrap the high-adoption equilibrium.

## Summary

The lock mechanism creates a self-regulating system in which rational actors provide cascade protection precisely when the protocol most needs it.

::: theorem
**Theorem 3.1** (Lock Adoption Equilibrium). *With $r_{\text{bonus}} = r_{\text{malus}} = s = 10\%$:*

1. *Lock adoption is utilization-dependent: attractive when $U > 95\%$, marginal otherwise.*
2. *The APY differential $\Delta r = 9\% \times r_{\text{base}}$ provides maximum incentive within solvency constraints.*
3. *Lock adoption self-regulates: increases during stress (cascade protection) and decreases during calm (revenue preservation).*
4. *Protocol margin ranges from 20% of $r$ (no locks) to 0% of $r$ (full locks), with expected operating range 8–16% of $r$.*
:::

The secondary market discount acts as a natural governor — preventing full adoption while ensuring sufficient incentive for meaningful cascade protection — so the mechanism achieves incentive alignment without external intervention.

### Equilibrium Structure

The game exhibits two self-reinforcing equilibria: high adoption ($\bar{\rho} > 40\%$, margin 8–12% of $r$, strong cascade protection) and low adoption ($\bar{\rho} < 15\%$, margin 16–20% of $r$, high cascade exposure). Selection is path-dependent — seeding secondary market liquidity bootstraps the high-adoption regime, while neglect traps the protocol in low adoption. Governance can influence this by initially setting $r_{\text{bonus}}$ above the long-run target, then reducing it via lethargic transition once adoption stabilizes.

Within either regime, the mechanism is countercyclical: lock adoption rises above $U = 95\%$ when cascade prevention is most valuable, then recedes as utilization normalizes, restoring margin. Lethargic governance reinforces this — the $0.5\times$–$2\times$ per-cycle parameter bound ensures that equilibrium shifts occur gradually enough for the secondary market to adjust. During stress, protocol margin decreases as the intended trade-off for cascade protection, and recovers during the subsequent normalization.

The equilibrium is asymmetric across position types. Locked suppliers earn at effective rate $r_{\text{base}}(1{-}s)(1{+}r_{\text{bonus}} \cdot \rho_u)$ but must compensate the secondary market discount $D$, requiring $U > 95\%$ for rational adoption. Locked borrowers pay at effective rate $r_{\text{base}}(1{+}s)(1{-}r_{\text{malus}} \cdot \rho_u)$ — reducing an *obligation* with no redemption friction — making $\bar{\rho}^B > \bar{\rho}^S$ in the normal regime, converging during stress as the supply bonus dominates. A plausible operating point ($\bar{\rho}^S \approx 15\%$, $\bar{\rho}^B \approx 35\%$) yields

$$M = 2s - s \cdot \bar{\rho}^S - s \cdot \bar{\rho}^B = 20\% - 1.5\% - 3.5\% = 15\% \text{ of } r,$$

within the sustainable range.

### Cascade Dynamics and Keeper Sizing

Debt assumption transfers locks proportionally, preserving aggregate $\bar{\rho}$ through cascades — the attenuation bound $(1{-}\phi)$ from the [Cascade Attenuation Theorem](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation) holds dynamically, not merely at a pre-crash snapshot. At $\bar{\rho} \approx 30\%$, this reduces 25%-shock liquidations from 85.7% to $\approx 55\%$ of positions. However, locked supply received by a liquidator cannot be redeemed: absorbing a fully-locked victim at exponent $e$ increases assumed debt by $d = V_b \cdot 2^{-e}$ while adding zero redeemable supply, eroding headroom for subsequent liquidations.

The exponent choice is itself strategic. Choosing $e = 0$ captures the full position — maximizing per-event profit but inheriting the full lock fraction. Choosing $e \geq 1$ halves the position taken, reducing lock inheritance at the cost of leaving the remainder available to competitors. In equilibrium, the optimal $e$ reflects each liquidator's current health factor and the remaining cascade depth: unconstrained liquidators with ample headroom prefer small $e$, while capacity-constrained ones ration across targets. Both effects — lock removal from the liquidation pool and liquidator self-throttling — reinforce cascade attenuation.

Keeper sizing must account for lock propagation. A keeper processing $k$ sequential liquidations needs headroom for both aggregate debt absorbed and the locked fraction that cannot be redeemed. If the expected victim lock fraction is $\bar{\rho}$, the effective headroom requirement per liquidation increases by factor $1/(1 - \bar{\rho})$ relative to the unlocked case, since only $(1{-}\bar{\rho})$ of received supply contributes redeemable collateral. The [cascade simulation](/simulations/02-cascade) quantifies this across varying lock fractions and crash severities.

### Solvency Guarantees

Protocol solvency is enforced algebraically. The supervised contract enforces $r_{\text{bonus}} \leq s$ and $r_{\text{malus}} \leq s$ in *both* directions via `_setTarget` overrides: when setting `LOCK_BONUS_ID`/`LOCK_MALUS_ID`, the new value must be $\leq s$; when setting `SPREAD_ID`, the new spread must remain $\geq \max(r_{\text{bonus}}, r_{\text{malus}})$, so a governance-driven *decrease* of $s$ cannot violate the invariant either. Additionally $s \leq \texttt{Constant.HLF} = 0.5$ is enforced. Since $\bar{\rho}^S, \bar{\rho}^B \in [0, 1]$, the aggregate condition $r_{\text{bonus}} \bar{\rho}^S + r_{\text{malus}} \bar{\rho}^B \leq 2s$ holds without on-chain lock-adoption tracking. The worst case ($\bar{\rho}^S = \bar{\rho}^B = 1$) yields zero margin but never insolvency — avoiding the gas overhead of global lock-adoption statistics by relying on per-parameter bounds enforced at governance time.

Lock adoption also tightens beta-distributed caps indirectly: locked suppliers are persistent holders, inflating the effective $n$ in the $\sqrt{n{+}2}$ divisor, while attackers splitting across $k$ accounts face the $O(\sqrt{k})$ cap-scaling barrier *and* irrevocability — acquiring locked positions via secondary market incurs discount $D$, creating a multiplicative barrier to rapid concentration.

### Welfare

The welfare balance is favorable. Cascade attenuation reduces depth by factor $(1{-}\phi)$, and spread compression rewards committed participants — at full lock with $s = r_{\text{bonus}} = r_{\text{malus}} = 10\%$, both locked suppliers and borrowers face effective rate multiplier $0.99$, approaching a zero-spread market. Against these benefits stands liquidity fragmentation: locked supply raises effective utilization to $U_{\text{eff}} = V_b / (V_s(1{-}\phi))$, potentially triggering kink-rate dynamics at lower borrow volumes. The interest rate curve absorbs this naturally — higher effective utilization raises rates, incentivizing settlement — so the effect narrows the sub-kink operating range without creating instability.

Together, these properties confirm Theorem 3.1: the mechanism is self-regulating, with per-parameter solvency bounds that require no on-chain adoption tracking, cascade dynamics that naturally throttle liquidation velocity, and welfare effects that the interest rate curve absorbs without instability.
