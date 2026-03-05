---
title: "Appendix G: Bad-Debt Risk Analysis"
description: "Complete risk quantification framework for bad debt under oracle staleness, including oracle lag model, Monte Carlo simulation, analytical bounds, and safe operating region."
---

# Appendix G: Bad-Debt Risk Analysis

*This appendix was originally published as a standalone companion document and is reproduced here for completeness.*

## Introduction

XPower Banq's log-space TWAP oracle provides robust manipulation resistance—approximately 40 hours of sustained artificial pricing are required to achieve 90% deviation (Mackinga et al., 2022). However, the same smoothing that resists manipulation delays response to genuine market crashes. After an instantaneous price crash, only ${\sim}50\%$ of the log-space deviation is absorbed after 13 hourly refreshes (the 12-hour half-life). Combined with the 1-hour rate limit between oracle updates, the protocol can be 2+ hours blind during a crash.

This appendix provides a complete risk quantification framework:

1. **Oracle Lag Model** — Formal characterization of the EMA convergence delay and the resulting phantom-healthy window.
2. **Monte Carlo Simulation** — Jump-diffusion price paths with ETH-calibrated parameters, swept across LTV and oracle decay configurations.
3. **Analytical Bound** — Closed-form upper bound on bad debt as a function of crash magnitude, oracle decay, and LTV.
4. **Safe Operating Region** — Parameter configurations satisfying the $<5\%$ TVL constraint.

All simulations use fixed random seeds for reproducibility.

## Oracle Lag Model

### EMA Update Semantics

The TWAP oracle (`TWAP.sol`) performs an EMA update on each refresh. Critically, the update blends the stored mean with the *previous* observation (`last`), not the current one (`next`):

$$\begin{aligned}
\overline{m}_n &= \alpha \cdot \overline{m}_{n-1} + (1{-}\alpha) \cdot \ell_{n-1} \\
\ell_n &= q_n
\end{aligned}$$

where $\overline{m}_n$ is the smoothed log-price, $\ell_n$ is the stored last observation, and $q_n$ is the current market price (in $\log_2$ space). This creates a *one-refresh delay*: a new price enters the mean only on the *following* refresh.

### Step-Crash Convergence

After an instantaneous crash of fraction $\delta$ at time $t_0$ (price drops from $p_0$ to $p_0(1{-}\delta)$), the oracle-reported price after $n$ refreshes follows:

$$\hat{p}(n) = p_0 \cdot 2^{\overline{m}_n}$$

where the log-space EMA converges geometrically toward the post-crash price. The fraction of the log-space deviation absorbed by the oracle at refresh $n$ is:

$$A(n) = 1 - \alpha^{n-1} \quad (n \geq 2), \qquad A(0) = A(1) = 0$$

Due to the one-refresh delay, the oracle is completely blind for the first refresh after a crash. This log-space absorption is independent of crash magnitude $\delta$—all crashes converge at the same geometric rate $(1{-}\alpha)$ per refresh. The oracle-reported price in linear space is $\hat{p}(n) = p_0 \cdot (1{-}\delta)^{A(n)}$, so linear-space absorption varies with $\delta$.

<figure>
  <img src="/images/015-oracle-convergence.svg" alt="Oracle convergence after step crashes">
  <figcaption>Figure 15: Oracle convergence after step crashes of various magnitudes (α = 0.944, 1 h refresh). The dashed line marks the 12-hour half-life. All crash magnitudes converge at the same geometric rate in log-space, reaching 50% absorption near n = 13 refreshes.</figcaption>
</figure>

| $n$ | 20% | 30% | 40% | 50% | 70% |
|---|---|---|---|---|---|
| 1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | 5.6% | 5.6% | 5.6% | 5.6% | 5.6% |
| 4 | 15.9% | 15.9% | 15.9% | 15.9% | 15.9% |
| 8 | 33.2% | 33.2% | 33.2% | 33.2% | 33.2% |
| 12 | 46.9% | 46.9% | 46.9% | 46.9% | 46.9% |
| 24 | 73.4% | 73.4% | 73.4% | 73.4% | 73.4% |
| 48 | 93.3% | 93.3% | 93.3% | 93.3% | 93.3% |
| 72 | 98.3% | 98.3% | 98.3% | 98.3% | 98.3% |

*Table: Oracle absorption $A(n)$ after $n$ hourly refreshes ($\alpha = 0.944$). Log-space absorption $A(n) = 1 - \alpha^{n-1}$ is independent of crash magnitude; linear-space absorption varies with $\delta$.*

<figure>
  <img src="/images/016-oracle-lag-heatmap.svg" alt="Oracle deviation heatmap">
  <figcaption>Figure 16: Oracle deviation from true price (%) as a function of crash magnitude and hours elapsed. The heatmap shows the full convergence surface; larger crashes produce higher absolute deviations but the same geometric decay rate.</figcaption>
</figure>

### Phantom-Healthy Windows

::: definition
**Definition 7** (Phantom-Healthy Position). A position is *phantom-healthy* at time $t$ when:

$$\begin{aligned}
H_{\text{oracle}}(t) &= H_0 \cdot \frac{\hat{p}(t)}{p_0} \geq 1 \\
H_{\text{true}}(t) &= H_0 \cdot (1 - \delta) < 1
\end{aligned}$$

where $H_0$ is the initial health factor.
:::

For a position to be truly underwater, the crash must satisfy $\delta > 1 - 1/H_0$. The oracle triggers liquidation when $\hat{p}(n)/p_0 < 1/H_0$, i.e., the oracle price ratio drops below the inverse of the initial health.

::: definition
**Definition 8** (Phantom-Healthy Window). The *phantom-healthy window* $W$ is the number of oracle refreshes during which a position remains phantom-healthy:

$$W = \min\left\{n \geq 0 \;\middle|\; \frac{\hat{p}(n)}{p_0} < \frac{1}{H_0}\right\}$$
:::

The following table shows phantom-healthy windows for representative (crash, initial health) pairs with $\alpha = 0.944$.

| Crash | | $H_0 = 1.1$ | $H_0 = 1.3$ | $H_0 = 1.5$ | $H_0 = 2.0$ |
|---|---|---|---|---|---|
| 20% | $W$ | 11 | — | — | — |
| 30% | $W$ | 7 | 25 | — | — |
| 40% | $W$ | 5 | 14 | 29 | — |
| 50% | $W$ | 4 | 10 | 17 | — |
| 70% | $W$ | 3 | 6 | 9 | 16 |

*"—" indicates the position remains solvent (not underwater). Values verified against step-by-step OracleModel simulation (match within +/- 1 refresh).*

### Worst-Case Blind Time

The worst case occurs when a crash happens immediately after a refresh, adding one full refresh interval of blindness. The total blind time is:

$$t_{\text{blind}} = \Delta t_{\text{refresh}} + W \cdot \Delta t_{\text{refresh}}$$

For the default 33% LTV configuration (positions initialized near $H_0 = 1.5$):

- **40% crash**: $W = 29$ refreshes, $t_{\text{blind}} = 30$ hours
- **50% crash**: $W = 17$ refreshes, $t_{\text{blind}} = 18$ hours
- **70% crash**: $W = 9$ refreshes, $t_{\text{blind}} = 10$ hours

Larger crashes produce shorter phantom windows because the true price diverges more rapidly from the oracle threshold. Positions with higher initial health (further from the liquidation boundary) require more refreshes before the oracle detects their distress.

## Monte Carlo Simulation

### Price Process

Collateral prices follow a Merton jump-diffusion model (Merton, 1976):

$$\frac{dp}{p} = \mu\,dt + \sigma\,dW + J\,dN$$

where $W$ is a Wiener process, $N$ is a Poisson process with intensity $\lambda_J$, and $J \sim \mathcal{N}(\mu_J, \sigma_J^2)$ are i.i.d. jump magnitudes. Parameters are calibrated to ETH historical data:

| Parameter | Value |
|---|---|
| Annual volatility $\sigma$ | 90% |
| Jump intensity $\lambda_J$ (jumps/year) | 6.0 |
| Mean jump $\mu_J$ | $-15\%$ |
| Jump volatility $\sigma_J$ | 10% |
| Drift $\mu$ | compensated |

### Simulation Design

**Resolution.** Paths are generated at hourly resolution (8,760 steps per year), matching the oracle refresh cadence. This is a deliberate trade-off: minute-level resolution would require $100\text{K} \times 525\text{K} = 52.5$B data points (${\sim}210$ GB at float32), while hourly resolution requires only 875M points (${\sim}3.5$ GB). Since the oracle can only update hourly, intra-hour price movements do not affect oracle-triggered liquidations.

**Pool.** Each path initializes 1,000 synthetic positions with health factors $H_0 \sim \mathcal{N}(1.5, 0.3)$ truncated at $[1.0, 3.0]$ and uniform unit borrow size.

**Oracle.** The log-space EMA replicates `TWAP.sol` semantics exactly, including the one-refresh delay. The oracle processes hourly price snapshots and produces oracle-price-ratio time series.

**Liquidation.** Two models are implemented: (1) *full liquidation* via vectorized threshold crossing—for each position, pre-compute the critical oracle price ratio $p_{\text{crit}} = 1/H_0$ and detect the first crossing with `np.argmax`; (2) *partial liquidation* with $2^{-e}$ fraction per step (matching the protocol's debt assumption model), simulated step-by-step with optional price impact $k$.

**Parameters.** Default run: 1,000 paths, LTV = 1/3, $\alpha = 0.944$, 1-hour refresh, seed = 42.

### Results

The following table presents Monte Carlo results across LTV configurations. At the default 33% LTV, expected bad debt is 0.00% of TVL per year—the 200% over-collateralization ensures the oracle triggers liquidation (at $p_{\text{crit}} = 1/H_0$) well before any shortfall accumulates. Bad debt emerges only at LTV $\geq 67\%$ where the over-collateralization margin is thinner.

| LTV | $\mathbb{E}[\text{BD}]$ | VaR(99%) | CVaR(99%) | Nonzero |
|---|---|---|---|---|
| 33% | 0.00% | 0.00% | 0.00% | 0.0% |
| 50% | 0.00% | 0.00% | 0.00% | 0.0% |
| 67% | 0.00% | 0.00% | 0.02% | 1.3% |
| 75% | 0.01% | 0.32% | 0.69% | 10.7% |

*All values as % of TVL per year. "Nonzero" is the fraction of paths producing any bad debt. 95% CI on $\mathbb{E}[\text{BD}]$ is $< \pm 0.10\%$ at 1,000 paths.*

The following table shows the effect of oracle decay rate. At 33% LTV, all decay rates produce zero bad debt—the over-collateralization margin dominates.

| $\alpha$ | HL | $\mathbb{E}[\text{BD}]$ | VaR(99%) | CVaR(99%) |
|---|---|---|---|---|
| 0.891 | 6 h | 0.00% | 0.00% | 0.00% |
| 0.944 | 12 h | 0.00% | 0.00% | 0.00% |
| 0.972 | 24 h | 0.00% | 0.00% | 0.00% |

*HL = half-life in hours. At 33% LTV, the 200% over-collateralization absorbs all oracle staleness regardless of decay rate.*

### Bad Debt Distribution

All 1,000 simulated paths produce exactly zero bad debt for the default configuration, confirming that the 200% over-collateralization at 33% LTV fully absorbs oracle staleness. The oracle triggers liquidation at $p_{\text{crit}} = 1/H_0 \approx 0.67$ (33% price decline), well before the bad-debt threshold at $p = \text{LTV}/H_0 \approx 0.22$ (78% decline).

<figure>
  <img src="/images/017-mc-histogram.svg" alt="Bad debt distribution histogram">
  <figcaption>Figure 17: Bad debt distribution (default configuration: LTV = 33%, α = 0.944). All paths produce zero bad debt: the 200% over-collateralization ensures liquidation triggers well before any shortfall accumulates.</figcaption>
</figure>

### Drawdown–Bad Debt Relationship

At 33% LTV, even paths with extreme drawdowns ($>90\%$) produce zero bad debt. Bad debt requires the *true* price to drop below $\text{LTV}/H_0 \approx 0.22$ *and* the oracle to fail to trigger liquidation in time—the corrected liquidation threshold ($1/H_0 \approx 0.67$) catches positions long before this point.

<figure>
  <img src="/images/018-drawdown-bd.svg" alt="Drawdown vs. bad debt scatter plot">
  <figcaption>Figure 18: Maximum drawdown vs. bad debt per simulated path (LTV = 33%, α = 0.944). At 33% LTV all paths produce zero bad debt regardless of drawdown severity, confirming the analytical bound.</figcaption>
</figure>

### Liquidation Delay Distribution

For paths that produce liquidations, the delay between a position becoming truly underwater ($H_{\text{true}} < 1$) and the oracle triggering liquidation ($H_{\text{oracle}} < 1$) has the following characteristics (baseline configuration, 1,000 paths):

- **Median delay**: 30 hours
- **Mean delay**: $>218$ hours (skewed by long tails)
- **99th percentile**: ${\sim}3{,}800$ hours

The heavy right tail reflects paths where positions hover near the liquidation boundary during gradual declines, maintaining phantom-healthy status for extended periods.

<figure>
  <img src="/images/019-liquidation-delay.svg" alt="Liquidation delay distribution">
  <figcaption>Figure 19: Distribution of oracle-induced liquidation delay (hours from true underwater to oracle-triggered liquidation). The distribution is extremely heavy-tailed: median delay is 30 h but the mean exceeds 218 h due to paths where positions hover near the liquidation boundary.</figcaption>
</figure>

## Analytical Bound

### Instant Liquidation Baseline

As a baseline, consider bad debt under instant liquidation (no oracle delay). A position with initial health $H_0$ experiencing crash fraction $\delta$ has:

$$\text{BD}_{\text{inst}} = \text{borrow} \cdot \max\!\left(0,\; 1 - \frac{H_0(1{-}\delta)}{\text{LTV}}\right)$$

Positions are underwater when $H_0 < 1/(1{-}\delta)$, and produce bad debt when $H_0(1{-}\delta) < \text{LTV}$ (shortfall exceeds collateral value at true price). Integrating over the health distribution $H_0 \sim \text{TruncNorm}(1.5, 0.3, [1.0, 3.0])$ and weighting by TVL contribution:

$$\frac{\mathbb{E}[\text{BD}_{\text{inst}}]}{\text{TVL}} = \frac{\int_{1}^{H_{\text{crit}}} \max\!\left(0,\; 1 - \frac{H(1{-}\delta)}{\text{LTV}}\right) H \cdot f(H)\,dH}{\mathbb{E}[H]}$$

where $H_{\text{crit}} = 1/(1{-}\delta)$ and $f(H)$ is the truncated normal PDF.

### Oracle Delay Penalty

The additional bad debt from oracle staleness arises when price continues declining during the phantom-healthy window. For a position with phantom window $W$ refreshes and hourly volatility $\sigma_h = \sigma/\sqrt{8760}$, the expected additional decline is:

$$\Delta_W = W \cdot \sigma_h \approx W \cdot \frac{0.90}{\sqrt{8760}} \approx 0.0096 \cdot W$$

### Conservative Upper Bound

::: theorem
**Theorem 6** (Bad Debt Upper Bound). *For a step crash of fraction $\delta$, oracle decay $\alpha$, and effective LTV, the maximum bad debt as a fraction of TVL is bounded by:*

$$\text{BD}_{\max}(\delta, \alpha, \text{LTV}) \leq \text{BD}_{\text{inst}} \cdot \left(1 + \frac{W_{\max} \cdot \sigma_h}{\delta}\right)$$

*where $W_{\max}$ is the phantom window for the marginal underwater position (health just below $1/(1{-}\delta)$) and $\sigma_h \approx 0.96\%$/hour is the ETH hourly volatility.*
:::

::: proof
**Proof.** The bound follows from three observations: (1) all positions that are underwater under instant liquidation are also underwater under delayed liquidation, establishing $\text{BD}_{\text{inst}}$ as a lower bound; (2) positions with longer phantom windows experience additional price movement of order $W \cdot \sigma_h$ during the delay; (3) the marginal underwater position (highest $H_0$ still underwater) has the longest phantom window $W_{\max}$.

The multiplicative penalty $W_{\max} \cdot \sigma_h / \delta$ represents the worst-case fractional increase in bad debt due to continued decline during the phantom window, normalized by the initial crash magnitude. This is conservative because: (a) it assumes all positions experience $W_{\max}$ rather than their individual (shorter) windows, and (b) it assumes continued decline at full volatility rather than zero-drift random walk.
:::

The following table presents the bound for selected parameter combinations.

| Crash | LTV | BD_inst | $\alpha{=}0.944$ | $\alpha{=}0.891$ |
|---|---|---|---|---|
| 30% | 33% | 0.00 | 0.00 | 0.00 |
| 30% | 75% | 0.06 | 0.20 | 0.13 |
| 40% | 67% | 0.16 | 0.46 | 0.32 |
| 40% | 75% | 0.97 | 2.79 | 1.90 |
| 50% | 33% | 0.00 | 0.00 | 0.00 |
| 50% | 50% | 0.00 | 0.00 | 0.00 |
| 50% | 67% | 1.90 | 5.08 | 3.51 |
| 50% | 75% | 4.98 | 13.32 | 9.20 |
| 70% | 33% | 0.16 | 0.26 | 0.21 |
| 70% | 50% | 9.67 | 15.52 | 12.73 |
| 70% | 67% | 29.00 | 46.52 | 38.15 |

*Table: Analytical bad debt bound (% of TVL). BD_inst is the baseline under instant liquidation. Bounds are computed with ETH hourly volatility $\sigma_h \approx 0.96\%$.*

## Safe Operating Region

### Safety Criterion

We define a parameter configuration $(\alpha, \text{LTV})$ as *safe* if the analytical bad debt bound satisfies $\text{BD}_{\max} < 5\%$ of TVL for crash magnitudes up to 50%. This corresponds to Acceptance Criterion 4 from the specification.

### Safe Configurations

| $\alpha$ | Half-Life | LTV | BD Bound |
|---|---|---|---|
| 0.891 | 6 h | 33% | 0.00% |
| 0.891 | 6 h | 50% | 0.00% |
| 0.891 | 6 h | 67% | 3.51% |
| 0.944 | 12 h | 33% | 0.00% |
| 0.944 | 12 h | 50% | 0.00% |
| 0.972 | 24 h | 33% | 0.00% |
| 0.972 | 24 h | 50% | 0.00% |

*The default configuration ($\alpha = 0.944$, LTV = 33%) produces zero bounded bad debt for any crash up to 50%.*

<figure>
  <img src="/images/020-safe-region.svg" alt="Safe operating region">
  <figcaption>Figure 20: Safe operating region in (α, LTV, crash) space. The surface separates configurations where BD_max &lt; 5% (below) from those exceeding the threshold (above).</figcaption>
</figure>

### Key Observations

1. **33% LTV is zero-bad-debt for crashes up to 50%.** At the default 33% LTV, positions require a $>50\%$ crash before any become underwater. With 200% over-collateralization, even a 50% crash leaves the average position ($H_0 = 1.5$) with $H_{\text{true}} = 0.75 > \text{LTV} = 0.33\text{:}$ still solvent.

2. **LTV is the dominant risk parameter.** Bad debt is zero for LTV $\leq 50\%$ and emerges only at LTV $\geq 67\%$, reaching $\mathbb{E}[\text{BD}] = 0.01\%$ at 75% LTV. The oracle decay rate has no observable effect at 33% LTV.

3. **The 200% buffer fully absorbs oracle staleness.** The oracle triggers liquidation at $p_{\text{crit}} = 1/H_0 \approx 0.67$ (33% price decline), while bad debt requires the true price to reach $\text{LTV}/H_0 \approx 0.22$ (78% decline). This 45-percentage-point gap renders oracle delay harmless at the default LTV.

4. **Tail risk is negligible at default LTV.** At 33% LTV, all risk metrics (E[BD], VaR, CVaR) are zero. At 75% LTV, CVaR(99%) reaches 0.69% of TVL.

## Sensitivity Analysis

### Parameter Rankings

The following parameters are ranked by their impact on expected bad debt (based on tornado diagram analysis over the MC sweep):

1. **LTV (weight ratio)** — governance-controlled, dominant effect. Moving from 33% to 75% increases $\mathbb{E}[\text{BD}]$ from 0.00% to 0.01%, and CVaR(99%) from 0.00% to 0.69%.

2. **Jump intensity $\lambda_J$** — exogenous market condition. Higher jump frequency (12 vs. 4 per year) increases tail risk by amplifying crash-like events.

3. **Oracle decay $\alpha$** — secondary effect. At 33% LTV, all decay rates produce zero bad debt. At higher LTV, faster decay reduces phantom-healthy windows, but the effect is dominated by the LTV choice.

4. **Refresh interval** — operational parameter. Faster refreshes (15 min vs. 2 h) reduce the initial blind period but have diminishing returns once below the half-life.

5. **Lock fraction $\phi$** — emergent, not directly controlled. Locks reduce cascade-induced bad debt but have minimal effect on oracle-staleness-driven bad debt.

6. **Price impact $k$** — exogenous. Increases bad debt during liquidation cascades but does not affect oracle staleness.

### Interaction Effects

Two notable interaction effects emerge from pairwise analysis:

**$\alpha \times$ LTV.** Higher LTV *amplifies* the staleness problem non-linearly. At 33% LTV, changing $\alpha$ from 0.891 to 0.972 has zero observable effect; at 75% LTV, the same change measurably increases bad debt. The over-collateralization buffer acts as a threshold: below a critical LTV, oracle delay is completely absorbed.

**$\alpha \times$ Refresh interval.** Diminishing returns to faster refreshes when $\alpha$ is already responsive. At $\alpha = 0.891$ (6 h HL), reducing refresh interval from 2 h to 15 min has minimal effect because the EMA already converges rapidly.

## Partial Liquidation

The protocol uses a $2^{-e}$ partial liquidation model: each liquidation step transfers fraction $(1 - 2^{-e})$ of the position. With the default $e = 1$, 50% of a position is cleared per step.

During continued price declines, partial liquidation can produce *more* bad debt than instant full liquidation, because remaining position fractions face increasingly adverse prices. The price impact coefficient $k$ further increases bad debt by modeling the market impact of forced liquidation sales:

$$p_{\text{effective}} = p_{\text{true}} \cdot (1 - k)$$

Monte Carlo tests confirm that price impact $k = 0.10$ (10% haircut) measurably increases bad debt relative to $k = 0$ in declining markets. However, the effect is secondary to the LTV choice and primarily affects already-distressed positions.

## Cross-Validation

### Oracle Model vs. Solidity

The Python oracle model is cross-validated against three Foundry scenario tests from `test/Oracle/OracleScenario.t.sol`:

- **S01 (Benign Motion)**: 24 refreshes with +/-5% oscillations. Mid drift $< 10\%$.
- **S02 (Sudden Drift)**: 2x price jump. After 1st refresh: $\delta < 3\%\text{;}$ after 2nd: $\delta < 15\%\text{;}$ after 14th: $15\% < \delta < 70\%$.
- **S04 (Sudden Reversal)**: 2x spike then revert. Residual $< 5\%$ (Solidity cadence) or $< 7\%$ (Python all-tick cadence).

The discrepancy in S04 arises from Solidity's `delayed()` modifier using strict $>$ comparison, causing only every other hourly tick to produce a Refresh event (alternating Pending/Refresh). Both models produce correct results for their respective refresh cadences.

### Phantom Window Verification

Analytical phantom window computations are verified against step-by-step OracleModel simulations for 4 representative (crash, health) pairs. All match within +/- 1 refresh.

### Bound Conservatism

The analytical bound (Theorem 6) is verified to exceed all MC simulation results across all tested parameter combinations. The `check-bound` CLI command automates this check for each (LTV, $\alpha$, crash) triple in the MC results.

## Deployment Recommendations

Based on the analysis, we recommend the following parameter configurations for deployment:

1. **Default configuration** ($\alpha = 0.944$, LTV = 33%): Zero bounded bad debt for crashes up to 50%. This is the recommended production setting, balancing oracle manipulation resistance with bad debt containment.

2. **Higher capital efficiency** ($\alpha = 0.891$, LTV = 50%): Zero bounded bad debt for 50% crashes. Requires reducing half-life to 6 hours, which weakens manipulation resistance (20 hours sustained manipulation for 90% deviation).

3. **Maximum responsiveness** ($\alpha = 0.891$, LTV = 67%): Bounded bad debt of 3.51% for 50% crash. Suitable only for highly liquid pairs where manipulation risk is low and faster oracle response is prioritized.

**Configurations to avoid:**

- LTV $\geq 75\%$ at any $\alpha\text{:}$ Bounded bad debt exceeds 9% for 50% crashes.
- $\alpha = 0.972$ (24 h HL) with LTV $> 50\%\text{:}$ Excessive staleness compounds with thin over-collateralization margin.

## Conclusion

XPower Banq's log-space TWAP oracle creates a quantifiable trade-off between manipulation resistance and bad-debt risk. The 200% over-collateralization buffer at the default 33% LTV fully absorbs oracle staleness: Monte Carlo simulation produces zero bad debt across all 1,000 simulated paths, and the analytical bound confirms zero bad debt for crashes up to 50%. Bad debt emerges only at LTV $\geq 67\%$, reaching $\mathbb{E}[\text{BD}] = 0.01\%$ at 75% LTV.

The mechanism underlying this robustness is the 45-percentage-point gap between the oracle's liquidation trigger and the bad-debt threshold. At 33% LTV with typical $H_0 = 1.5$, the oracle triggers liquidation when the reported price drops to $1/H_0 \approx 0.67$ (a 33% decline), whereas bad debt requires the true price to reach $\text{LTV}/H_0 \approx 0.22$ (a 78% decline). Even with phantom-healthy windows of 17–30 hours for 40–50% crashes, positions are liquidated long before the true price can traverse this gap. Only when the LTV approaches $1/H_0$—collapsing the gap—does oracle staleness translate into realised bad debt.

The primary risk lever is the LTV parameter, not the oracle decay rate. Sensitivity analysis ranks the six model parameters by impact: LTV dominates, followed by exogenous jump intensity $\lambda_J$, with oracle decay $\alpha$ a distant third. At 33% LTV, all three tested decay rates ($\alpha \in \{0.891, 0.944, 0.972\}$) produce identical zero bad debt, confirming that the over-collateralization buffer acts as a binary absorber below a critical LTV. Above that threshold, the interaction between $\alpha$ and LTV becomes non-linear: increasing LTV from 33% to 75% amplifies the staleness penalty from $0\times$ to $1.67\times$ the instant-liquidation baseline.

Governance should therefore prioritize LTV conservatism over oracle responsiveness. The analytical bound $\text{BD}_{\max}(\delta, \alpha, \text{LTV}) \leq \text{BD}_{\text{inst}} \cdot (1 + W_{\max} \cdot \sigma_h / \delta)$ (Theorem 6) provides a closed-form, governance-usable formula for evaluating parameter changes against bad-debt tolerance. Combined with the safe-operating-region criterion ($\text{BD}_{\max} < 5\%$ of TVL for $\delta \leq 50\%$), this bound delineates five safe $(\alpha, \text{LTV})$ configurations, all with LTV $\leq 67\%$.

**Limitations.** The analysis makes several simplifying assumptions. First, positions are modelled with a static health distribution $H_0 \sim \mathcal{N}(1.5, 0.3)$ rather than endogenous dynamics from supply/borrow inflows. Second, oracle refreshes are assumed to occur at exact hourly intervals, whereas the `delayed()` modifier's strict-$>$ comparison can cause alternating Pending/Refresh patterns that effectively double the refresh interval. Third, liquidation cascades and their feedback effects on market prices are modelled only via the price-impact coefficient $k$, not through an order-book simulation. Fourth, correlated multi-asset crashes are not considered.
