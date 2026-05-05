---
title: "4. Bad-Debt Risk"
prev:
  text: "3. TWAP Oracle"
  link: /simulations/03-twap-oracle
next:
  text: "5. Conclusion"
  link: /simulations/05-conclusion
---

## Introduction

XPower Banq's [log-space TWAP oracle](/whitepaper/04-mechanisms#oracle-twap) provides robust manipulation resistance — approximately 40 hours of sustained artificial pricing are required to achieve 90% deviation [\[mackinga2022\]](/reference/bibliography#mackinga2022). However, the same smoothing that resists manipulation delays response to genuine market crashes. After an instantaneous price crash, only $\sim 50\%$ of the log-space deviation is absorbed after 13 hourly refreshes (the 12-hour half-life). Combined with the 1-hour rate limit between oracle updates, the protocol can be 2+ hours blind during a crash.

This section provides a complete risk quantification framework:

1. **Oracle Lag Model** — formal characterization of the EMA convergence delay and the resulting phantom-healthy window.
2. **Monte Carlo Simulation** — jump-diffusion price paths with ETH-calibrated parameters, swept across LTV and oracle decay configurations.
3. **Analytical Bound** — closed-form upper bound on bad debt as a function of crash magnitude, oracle decay, and LTV.
4. **Safe Operating Region** — parameter configurations satisfying the $<5\%$ TVL constraint.

All simulations use fixed random seeds for reproducibility.

## Oracle Lag Model

### EMA Update Semantics

The TWAP oracle (`TWAP.sol`) performs an EMA update on each refresh. Critically, the update blends the stored mean with the *previous* observation (`last`), not the current one (`next`):

$$\overline{m}_n = \alpha \cdot \overline{m}_{n-1} + (1 - \alpha) \cdot \ell_{n-1}$$

$$\ell_n = q_n$$

where $\overline{m}_n$ is the smoothed log-price, $\ell_n$ is the stored last observation, and $q_n$ is the current market price (in $\log_2$ space). This creates a *one-refresh delay*: a new price enters the mean only on the *following* refresh.

### Step-Crash Convergence

After an instantaneous crash of fraction $\delta$ at time $t_0$ (price drops from $p_0$ to $p_0(1-\delta)$), the oracle-reported price after $n$ refreshes follows

$$\hat{p}(n) = p_0 \cdot 2^{\overline{m}_n}$$

where the log-space EMA converges geometrically toward the post-crash price. The fraction of the log-space deviation absorbed by the oracle at refresh $n$ is

$$A(n) = 1 - \alpha^{n-1} \quad (n \geq 2), \qquad A(0) = A(1) = 0.$$

Due to the one-refresh delay, the oracle is completely blind for the first refresh after a crash. This log-space absorption is independent of crash magnitude $\delta$ — all crashes converge at the same geometric rate $(1-\alpha)$ per refresh.

<figure>
  <img src="/images/015-oracle-convergence.svg" alt="Oracle convergence after step crashes">
  <figcaption>Figure 10: Oracle convergence after step crashes of various magnitudes (α = 0.944, 1 h refresh). The dashed line marks the 12-hour half-life. All crash magnitudes converge at the same geometric rate in log-space, reaching 50% absorption near n = 13 refreshes (accounting for the one-refresh delay).</figcaption>
</figure>

| $n$ | 20% | 30% | 40% | 50% | 70% |
|---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | 5.6% | 5.6% | 5.6% | 5.6% | 5.6% |
| 4 | 15.9% | 15.9% | 15.9% | 15.9% | 15.9% |
| 8 | 33.2% | 33.2% | 33.2% | 33.2% | 33.2% |
| 12 | 46.9% | 46.9% | 46.9% | 46.9% | 46.9% |
| 24 | 73.4% | 73.4% | 73.4% | 73.4% | 73.4% |
| 48 | 93.3% | 93.3% | 93.3% | 93.3% | 93.3% |
| 72 | 98.3% | 98.3% | 98.3% | 98.3% | 98.3% |

<small>Oracle absorption $A(n)$ after $n$ hourly refreshes ($\alpha = 0.944$). Log-space absorption is independent of crash magnitude; linear-space absorption varies with $\delta$.</small>

<figure>
  <img src="/images/016-oracle-lag-heatmap.svg" alt="Oracle deviation heatmap">
  <figcaption>Figure 11: Oracle deviation from true price (%) as a function of crash magnitude and hours elapsed. The heatmap shows the full convergence surface; larger crashes produce higher absolute deviations but the same geometric decay rate.</figcaption>
</figure>

### Phantom-Healthy Windows

::: definition
**Definition 4.1** (Phantom-Healthy Position). A position is *phantom-healthy* at time $t$ when

$$H_{\text{oracle}}(t) = H_0 \cdot \frac{\hat{p}(t)}{p_0} \geq 1$$

$$H_{\text{true}}(t) = H_0 \cdot (1 - \delta) < 1$$

where $H_0$ is the initial health factor.
:::

For a position to be truly underwater, the crash must satisfy $\delta > 1 - 1/H_0$. The oracle triggers liquidation when $\hat{p}(n)/p_0 < 1/H_0$, i.e., the oracle price ratio drops below the inverse of the initial health.

::: definition
**Definition 4.2** (Phantom-Healthy Window). The *phantom-healthy window* $W$ is the number of oracle refreshes during which a position remains phantom-healthy:

$$W = \min\left\{n \geq 0 \;\middle|\; \frac{\hat{p}(n)}{p_0} < \frac{1}{H_0}\right\}.$$
:::

|  |  | $H_0 = 1.1$ | $H_0 = 1.3$ | $H_0 = 1.5$ | $H_0 = 2.0$ |
|---:|---|:---:|:---:|:---:|:---:|
| 20% | $W$ | 11 | — | — | — |
| 30% | $W$ | 7 | 25 | — | — |
| 40% | $W$ | 5 | 14 | 29 | — |
| 50% | $W$ | 4 | 10 | 17 | — |
| 70% | $W$ | 3 | 6 | 9 | 16 |

<small>Phantom-healthy window $W$ (hours) by crash magnitude and initial health, $\alpha = 0.944$. "—" indicates the position remains solvent (not underwater).</small>

### Worst-Case Blind Time

The worst case occurs when a crash happens immediately after a refresh, adding one full refresh interval of blindness. The total blind time is

$$t_{\text{blind}} = \Delta t_{\text{refresh}} + W \cdot \Delta t_{\text{refresh}}.$$

For the conservative-mode floor (33% LTV) configuration with positions initialized near $H_0 = 1.5$:

- **40% crash.** $W = 29$ refreshes ⇒ $t_{\text{blind}} = 30$ hours.
- **50% crash.** $W = 17$ refreshes ⇒ $t_{\text{blind}} = 18$ hours.
- **70% crash.** $W = 9$ refreshes ⇒ $t_{\text{blind}} = 10$ hours.

Larger crashes produce shorter phantom windows because the true price diverges more rapidly from the oracle threshold. Positions with higher initial health (further from the liquidation boundary) require more refreshes before the oracle detects their distress.

## Monte Carlo Simulation

### Price Process

Collateral prices follow a Merton jump-diffusion model:

$$\frac{dp}{p} = \mu \,dt + \sigma \,dW + J \,dN$$

where $W$ is a Wiener process, $N$ is a Poisson process with intensity $\lambda_J$, and $J \sim \mathcal{N}(\mu_J, \sigma_J^2)$ are i.i.d. jump magnitudes. Parameters are calibrated to ETH historical data:

| Parameter | Value |
|---|---:|
| Annual volatility $\sigma$ | 90% |
| Jump intensity $\lambda_J$ (jumps/year) | 6.0 |
| Mean jump $\mu_J$ | $-15\%$ |
| Jump volatility $\sigma_J$ | 10% |
| Drift $\mu$ | compensated |

### Simulation Design

**Resolution.** Paths are generated at hourly resolution (8,760 steps per year), matching the oracle refresh cadence. Since the oracle can only update hourly, intra-hour price movements do not affect oracle-triggered liquidations.

**Pool.** Each path initializes 1,000 synthetic positions with health factors $H_0 \sim \mathcal{N}(1.5, 0.3)$ truncated at $[1.0, 3.0]$ and uniform unit borrow size.

**Oracle.** The log-space EMA replicates `TWAP.sol` semantics exactly, including the one-refresh delay.

**Refresh.** The 1-hour cadence is the deployed value of the governance parameter `LIMIT_ID`; it is not a hard-coded constant. The conservative-mode parameter set scales linearly with $\Delta t_{\text{refresh}}$ and is contingent on this cadence not being shortened materially.

**Liquidation.** Two models are implemented: (1) *full liquidation* via vectorized threshold crossing; (2) *partial liquidation* that transfers fraction $2^{-e}$ per step (matching `Pool.sol`'s right-shift by `partial_exp`; $e = 1$ gives the default 50%-per-step), with optional dimensionless liquidation-recovery haircut $\kappa$.

**Parameters.** Default run: 1,000 paths, LTV = 1/3 (the conservative-mode governance floor), $\alpha = 0.944$, 1-hour refresh, seed = 42.

### Results: LTV Sweep

| LTV | $\mathbb{E}[\text{BD}]$ | VaR(99%) | CVaR(99%) | Nonzero |
|---:|:---:|:---:|:---:|:---:|
| 33% | 0.00% | 0.00% | 0.00% | 0.0% |
| 50% | 0.00% | 0.00% | 0.00% | 0.0% |
| 67% | 0.00% | 0.00% | 0.02% | 1.3% |
| 75% | 0.01% | 0.32% | 0.69% | 10.7% |

<small>All values as % of TVL per year. "Nonzero" is the fraction of paths producing any bad debt. 95% CI on $\mathbb{E}[\text{BD}]$ is $< \pm 0.10\%$ at 1,000 paths.</small>

The shipped default of 66.67% LTV sits at the 67% row, with $\mathbb{E}[\text{BD}] = 0.00\%$, CVaR(99%) = 0.02%, and 1.3% of paths producing any bad debt — bounded but non-zero risk under tail-event jump-diffusion paths. The conservative-mode floor of 33% LTV produces zero bad debt across all paths and metrics.

### Results: Oracle Decay Sweep (at 33% LTV)

| $\alpha$ | HL | $\mathbb{E}[\text{BD}]$ | VaR(99%) | CVaR(99%) |
|---:|---:|:---:|:---:|:---:|
| 0.891 | 6 h | 0.00% | 0.00% | 0.00% |
| 0.944 | 12 h | 0.00% | 0.00% | 0.00% |
| 0.972 | 24 h | 0.00% | 0.00% | 0.00% |

At the 33% LTV floor, all decay rates produce zero bad debt — the over-collateralization margin dominates. Oracle decay becomes relevant only at higher LTV (including the shipped 66.67% default) where the liquidation-to-bad-debt gap is narrower.

### Bad Debt Distribution

<figure>
  <img src="/images/017-mc-histogram.svg" alt="Bad debt distribution at 33% LTV">
  <figcaption>Figure 12: Bad debt distribution at the conservative-mode floor (LTV = 33%, α = 0.944). All paths produce zero bad debt: the 200% over-collateralization ensures liquidation triggers well before any shortfall accumulates.</figcaption>
</figure>

### Drawdown vs. Bad Debt

<figure>
  <img src="/images/018-drawdown-bd.svg" alt="Maximum drawdown vs. bad debt">
  <figcaption>Figure 13: Maximum drawdown vs. bad debt per simulated path at the conservative-mode floor (LTV = 33%, α = 0.944). All paths produce zero bad debt regardless of drawdown severity, confirming the analytical bound.</figcaption>
</figure>

### Liquidation Delay Distribution

For paths that produce liquidations, the delay between a position becoming truly underwater and the oracle triggering liquidation has the following characteristics (baseline configuration, 1,000 paths):

- **Median delay.** 30 hours.
- **Mean delay.** $>218$ hours (skewed by long tails).
- **99th percentile.** $\sim 3{,}800$ hours.

<figure>
  <img src="/images/019-liquidation-delay.svg" alt="Distribution of oracle-induced liquidation delay">
  <figcaption>Figure 14: Distribution of oracle-induced liquidation delay (hours from true underwater to oracle-triggered liquidation). The distribution is extremely heavy-tailed: median delay is 30 h but the mean exceeds 218 h due to paths where positions hover near the liquidation boundary.</figcaption>
</figure>

## Analytical Bound

### Instant Liquidation Baseline

A position with initial health $H_0$ experiencing crash fraction $\delta$ has

$$\text{BD}_{\text{inst}} = \text{borrow} \cdot \max\!\left(0,\; 1 - \frac{H_0(1-\delta)}{\text{LTV}}\right).$$

Integrating over the health distribution $H_0 \sim \text{TruncNorm}(1.5, 0.3, [1.0, 3.0])$ and weighting by TVL contribution:

$$\frac{\mathbb{E}[\text{BD}_{\text{inst}}]}{\text{TVL}} = \frac{\int_{1}^{H_{\text{crit}}} \max\!\left(0,\; 1 - \frac{H(1-\delta)}{\text{LTV}}\right) H \cdot f(H)\,dH}{\mathbb{E}[H]}$$

where $H_{\text{crit}} = 1/(1-\delta)$ and $f(H)$ is the truncated normal PDF.

### Oracle Delay Penalty

For a position with phantom window $W$ refreshes and hourly volatility $\sigma_h = \sigma/\sqrt{8760}$, the expected additional decline is

$$\Delta_W = W \cdot \sigma_h \approx W \cdot \frac{0.90}{\sqrt{8760}} \approx 0.0096 \cdot W.$$

### Conservative Upper Bound

::: theorem
**Theorem 4.3** (Bad Debt Upper Bound). *For a step crash of fraction $\delta$, oracle decay $\alpha$, and effective LTV, the maximum bad debt as a fraction of TVL is bounded by*

$$\text{BD}_{\max}(\delta, \alpha, \text{LTV}) \leq \text{BD}_{\text{inst}} \cdot \left(1 + \frac{W_{\max} \cdot \sigma_h}{\delta}\right)$$

*where $W_{\max}$ is the phantom window for the marginal underwater position (health just below $1/(1-\delta)$) and $\sigma_h \approx 0.96\%/\text{hour}$ is the ETH hourly volatility.*
:::

::: proof
**Proof.** The bound follows from three observations: (1) all positions that are underwater under instant liquidation are also underwater under delayed liquidation, establishing $\text{BD}_{\text{inst}}$ as a lower bound; (2) positions with longer phantom windows experience additional price movement of order $W \cdot \sigma_h$ during the delay; (3) the marginal underwater position (highest $H_0$ still underwater) has the longest phantom window $W_{\max}$.

The multiplicative penalty $W_{\max} \cdot \sigma_h / \delta$ represents the worst-case fractional increase in bad debt due to continued decline during the phantom window, normalized by the initial crash magnitude. This is conservative because: (a) it assumes all positions experience $W_{\max}$ rather than their individual (shorter) windows, and (b) it assumes continued decline at full volatility rather than zero-drift random walk. $\blacksquare$
:::

| Crash | LTV | $\text{BD}_{\text{inst}}$ | $\alpha = 0.944$ | $\alpha = 0.891$ |
|---:|---:|:---:|:---:|:---:|
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

<small>Analytical bad debt bound (% of TVL). $\text{BD}_{\text{inst}}$ is the baseline under instant liquidation. Bounds are computed with ETH hourly volatility $\sigma_h \approx 0.96\%$.</small>

## Safe Operating Region

We define a parameter configuration $(\alpha, \text{LTV})$ as *safe* if the analytical bad debt bound satisfies $\text{BD}_{\max} < 5\%$ of TVL for crash magnitudes up to 50%.

| $\alpha$ | Half-Life | LTV | BD Bound |
|---:|---:|:---:|---:|
| 0.891 | 6 h | 33% | 0.00% |
| 0.891 | 6 h | 50% | 0.00% |
| 0.891 | 6 h | 67% | 3.51% |
| 0.944 | 12 h | 33% | 0.00% |
| 0.944 | 12 h | 50% | 0.00% |
| 0.972 | 24 h | 33% | 0.00% |
| 0.972 | 24 h | 50% | 0.00% |

The conservative-mode floor ($\alpha = 0.944$, LTV = 33%) produces zero bounded bad debt for any crash up to 50%. The shipped default ($\alpha = 0.944$, LTV = 66.67%) sits between the 50% and 67% rows and is governable down to 33% in one lethargic cycle.

<figure>
  <img src="/images/020-safe-region.svg" alt="Safe operating region in (α, LTV, crash) space">
  <figcaption>Figure 15: Safe operating region in (α, LTV, crash) space. The surface separates configurations where BD_max < 5% (below) from those exceeding the threshold (above).</figcaption>
</figure>

### Key Observations

1. **The 33% LTV floor is zero-bad-debt for ≤50% crashes.** With 200% over-collateralization, even a 50% crash leaves the average position ($H_0 = 1.5$) with $H_{\text{true}} = 0.75 > \text{LTV} = 0.33$: still solvent.
2. **LTV is the dominant risk parameter.** Bad debt is zero for LTV ≤ 50%, bounded but non-zero at the shipped 66.67% default ($\mathbb{E}[\text{BD}] = 0.00\%$, CVaR(99%) = 0.02%), and grows non-linearly above.
3. **The 50% buffer absorbs oracle staleness within tolerance at the shipped default.** The oracle triggers liquidation at $p_{\text{crit}} = 1/H_0 \approx 0.67$ (33% price decline). At the shipped 66.67% LTV, bad debt requires the true price to reach $\text{LTV}/H_0 \approx 0.44$ (56% decline) — a 23-percentage-point gap.
4. **Tail risk is bounded at the shipped default and negligible at the floor.** At the shipped 66.67% LTV, CVaR(99%) = 0.02%; at the 33% floor, all risk metrics are zero.

## Sensitivity Analysis

Parameters ranked by impact on expected bad debt (tornado diagram analysis):

1. **LTV (weight ratio).** Governance-controlled, dominant effect. Moving from the 33% floor through the shipped 66.67% default to the 75% upper sweep point increases $\mathbb{E}[\text{BD}]$ from 0.00% to 0.01% and CVaR(99%) from 0.00% through 0.02% to 0.69%.
2. **Jump intensity $\lambda_J$.** Exogenous market condition. Higher jump frequency increases tail risk by amplifying crash-like events.
3. **Oracle decay $\alpha$.** Secondary effect. At the 33% LTV floor, all decay rates produce zero bad debt. At the shipped default and above, faster decay reduces phantom-healthy windows, but the effect is dominated by the LTV choice.
4. **Refresh interval.** Operational parameter. Faster refreshes reduce the initial blind period but have diminishing returns once below the half-life.
5. **Lock fraction $\phi$.** Emergent, not directly controlled. Locks reduce cascade-induced bad debt but have minimal effect on oracle-staleness-driven bad debt.
6. **Liquidation-recovery haircut $\kappa$.** Exogenous. Increases bad debt during partial-liquidation steps in declining markets.

### Interaction Effects

**$\alpha \times$ LTV.** Higher LTV *amplifies* the staleness problem non-linearly. At the 33% LTV floor, changing $\alpha$ from 0.891 to 0.972 has zero observable effect; at the 75% upper sweep point, the same change measurably increases bad debt. The over-collateralization buffer acts as a threshold: below a critical LTV, oracle delay is completely absorbed; the shipped 66.67% default sits just above this threshold.

**$\alpha \times$ Refresh interval.** Diminishing returns to faster refreshes when $\alpha$ is already responsive. At $\alpha = 0.891$ (6 h HL), reducing refresh interval from 2 h to 15 min has minimal effect because the EMA already converges rapidly.

## Partial Liquidation

The protocol uses a $2^{-e}$ partial liquidation model. `Pool.sol` computes `borrowed_total >> partial_exp` and `supplied_total >> partial_exp`, transferring fraction $2^{-e}$ of the position per liquidation call. Thus $e = 0$ corresponds to full liquidation (100%), $e = 1$ clears 50% per step (the default), $e = 2$ clears 25%, and increasing $e$ liquidates a *smaller* share each step, leaving more residual debt to be wound down across subsequent calls.

During continued price declines, partial liquidation can produce *more* bad debt than instant full liquidation, because remaining position fractions face increasingly adverse prices. A dimensionless liquidation-recovery haircut $\kappa$ further increases bad debt by modeling the proceeds shortfall of forced liquidation sales:

$$p_{\text{effective}} = p_{\text{true}} \cdot (1 - \kappa).$$

Monte Carlo tests confirm that a haircut $\kappa = 0.10$ (10%) measurably increases bad debt relative to $\kappa = 0$ in declining markets. However, the effect is secondary to the LTV choice and primarily affects already-distressed positions.

## Cross-Validation

**Oracle Model vs. Solidity.** The Python oracle model is cross-validated against three Foundry scenario tests from `test/Oracle/OracleScenario.t.sol`:

- **S01 (Benign Motion).** 24 refreshes with ±5% oscillations. Mid drift $< 10\%$. ✓
- **S02 (Sudden Drift).** $2\times$ price jump. After 1st refresh: $\delta < 3\%$; after 2nd: $\delta < 15\%$; after 14th: $15\% < \delta < 70\%$. ✓
- **S04 (Sudden Reversal).** $2\times$ spike then revert. Residual $< 5\%$ (Solidity cadence) or $< 7\%$ (Python all-tick cadence). ✓

**Phantom Window Verification.** Analytical phantom window computations are verified against step-by-step OracleModel simulations for 4 representative (crash, health) pairs. All match within ±1 refresh.

**Bound Conservatism.** The analytical bound (Theorem 4.3) is verified to exceed all MC simulation results across all tested parameter combinations.

## Deployment Recommendations

1. **Shipped default** ($\alpha = 0.944$, LTV = 66.67%). Bounded bad debt of $\mathbb{E}[\text{BD}] = 0.00\%$ and CVaR(99%) = 0.02% under empirical jump-diffusion paths; analytical bound 1.90% for 50% crashes. The production setting, balancing capital efficiency against bad-debt containment.
2. **Conservative mode** ($\alpha = 0.944$, LTV = 33%). Zero bounded bad debt for crashes up to 50% — the governance-reachable floor for protocol-level conservatism, two lethargic cycles below the shipped default.
3. **Higher capital efficiency** ($\alpha = 0.891$, LTV = 50%). Zero bounded bad debt for 50% crashes. Requires reducing half-life to 6 hours, which weakens manipulation resistance.
4. **Maximum responsiveness** ($\alpha = 0.891$, LTV = 67%). Bounded bad debt of 3.51% for 50% crash. Suitable only for highly liquid pairs.

**Configurations to avoid:**

- LTV ≥ 75% at any $\alpha$: bounded bad debt exceeds 9% for 50% crashes.
- $\alpha = 0.972$ (24 h HL) with LTV $> 50\%$: excessive staleness compounds with thin over-collateralization margin.
