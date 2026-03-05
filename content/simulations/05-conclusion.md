---
title: "5. Conclusion"
prev:
  text: "4. Bad-Debt Risk"
  link: /simulations/04-bad-debt-risk
next: false
---

XPower Banq's [log-space TWAP oracle](/whitepaper/04-mechanisms#oracle-twap) creates a quantifiable trade-off between manipulation resistance and bad-debt risk. At the shipped default of 66.67% LTV, the 50% over-collateralization buffer keeps the analytical and Monte Carlo bad-debt bounds tight: $\mathbb{E}[\text{BD}] = 0.00\%$, CVaR(99%) = 0.02%, and 1.3% of jump-diffusion paths producing any bad debt. At the conservative-mode floor of 33% LTV, the 200% over-collateralization fully absorbs oracle staleness: Monte Carlo simulation produces zero bad debt across all 1,000 simulated paths, and the analytical bound confirms zero bad debt for crashes up to 50%. Bad debt grows non-linearly above 67%, reaching $\mathbb{E}[\text{BD}] = 0.01\%$ at the 75% upper sweep point.

## Mechanism

The mechanism underlying this robustness is the gap between the oracle's liquidation trigger ($p_{\text{crit}} = 1/H_0 \approx 0.67$, a 33% decline) and the bad-debt threshold ($p = \text{LTV}/H_0$). At the conservative 33% LTV floor, the threshold sits at $\approx 0.22$ (78% decline) — a 45-percentage-point gap. At the shipped 66.67% default, the threshold rises to $\approx 0.44$ (56% decline), narrowing the gap to 23 percentage points but still preserving multi-hour blind-time tolerance. Even with phantom-healthy windows of 17–30 hours for 40–50% crashes, positions are liquidated long before the true price can traverse this gap. Only when the LTV approaches $1/H_0$ — collapsing the gap — does oracle staleness translate into realised bad debt.

## The LTV Lever

The primary risk lever is the LTV parameter, not the oracle decay rate. [Sensitivity analysis](/simulations/04-bad-debt-risk#sensitivity-analysis) ranks the six model parameters by impact: LTV dominates, followed by exogenous jump intensity $\lambda_J$, with oracle decay $\alpha$ a distant third. At the 33% LTV floor, all three tested decay rates ($\alpha \in \{0.891, 0.944, 0.972\}$) produce identical zero bad debt, confirming that the over-collateralization buffer acts as a binary absorber below a critical LTV. Above that threshold (which the shipped 66.67% default crosses by a small margin), the interaction between $\alpha$ and LTV becomes non-linear: increasing LTV toward 75% amplifies the staleness penalty from $0\times$ to $1.67\times$ the instant-liquidation baseline.

## Governance Implications

Governance should therefore prioritize LTV conservatism over oracle responsiveness. The analytical bound

$$\text{BD}_{\max}(\delta, \alpha, \text{LTV}) \leq \text{BD}_{\text{inst}} \cdot (1 + W_{\max} \cdot \sigma_h / \delta)$$

provides a closed-form, governance-usable formula for evaluating parameter changes against bad-debt tolerance. Combined with the safe-operating-region criterion ($\text{BD}_{\max} < 5\%$ of TVL for $\delta \leq 50\%$), this bound delineates five safe $(\alpha, \text{LTV})$ configurations, all with LTV ≤ 67%.

## Other Simulation Findings

The companion simulation studies in this section ([Capacity Accumulation](/simulations/01-cap-accumulation), [Cascade](/simulations/02-cascade), [TWAP Oracle](/simulations/03-twap-oracle)) confirm three additional properties:

1. **Beta-distributed cap function** scales Sybil resistance as $O(\sqrt{n})$ — $10^4$ accounts require $10\times$ more iterations than $10^2$ accounts to reach full capacity. Multi-account share dynamics do *not* converge to account-proportional equilibrium: initial capital advantages persist (88% retention with $9\times$ initial advantage after 60 weeks).
2. **Liquidation cascades** are attenuated by up to 80% at full lock adoption in the *Extreme* market depth scenario ($k = 5 \times 10^{-4}$). The reduction is monotonic in lock fraction $\phi$ across all five market depth regimes.
3. **TWAP oracle** exhibits two-tick manipulation immunity (60 on-chain Foundry scenarios across 6 token configurations confirm 0% mid-price impact for inter-refresh and single-tick manipulation), with self-calibrating spread widening that requires no per-pair tuning.

## Limitations

The analysis makes several simplifying assumptions:

1. Positions are modelled with a static health distribution $H_0 \sim \mathcal{N}(1.5, 0.3)$ rather than endogenous dynamics from supply/borrow inflows.
2. Oracle refreshes are assumed to occur at exact hourly intervals, whereas the `delayed()` modifier's strict-$>$ comparison can cause alternating Pending/Refresh patterns.
3. Liquidation cascades and their feedback effects on market prices are modelled only via the liquidation-recovery haircut $\kappa$, not through an order-book simulation.
4. Correlated multi-asset crashes are not considered.

The mathematical framework underlying these simulations is developed in the companion [Theory](/theory/01-mathematical-foundations) section.
