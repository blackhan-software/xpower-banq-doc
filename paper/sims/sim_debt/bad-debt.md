# Bad Debt Risk Quantification Spec

## XPower Banq — Oracle Staleness & Bad Debt Analysis

---

## 1. Problem Statement

XPower Banq's log-space TWAP oracle with α = 0.944 and hourly refresh intervals absorbs only ~50% of a genuine 2× price move after 13 hours (the 12-hour half-life). During rapid market crashes, this creates a window where the oracle reports near-pre-crash prices, health factors appear healthy, liquidations fail to trigger, and bad debt accumulates silently. The 200% over-collateralization buffer provides margin, but no quantitative bound on bad-debt risk under stale pricing currently exists.

**Goal:** Produce a probabilistic model and historical backtest that bounds the expected bad debt under realistic crash scenarios, parameterized by oracle lag, collateral volatility, LTV, and lock adoption rate.

---

## 2. Scope

### In Scope

- Modeling oracle lag as a function of α, refresh interval, and crash magnitude
- Historical backtesting against real crash events (March 2020 Black Thursday, May 2021 crash, Terra/Luna contagion June 2022, FTX contagion November 2022)
- Monte Carlo simulation of bad debt under parameterized volatility regimes
- Sensitivity analysis across LTV configurations (33%–75%)
- Interaction between oracle staleness and lock adoption rate
- Deriving a closed-form or numerical bound on maximum bad debt as a percentage of TVL

### Out of Scope

- Oracle manipulation attacks (covered separately in existing whitepaper Section 7)
- Smart contract bugs or implementation errors
- Cross-chain oracle failures
- Gas cost optimization for liquidation during congestion

---

## 3. Oracle Lag Model

### 3.1 Formal Lag Characterization

Define the oracle-reported price $\hat{p}(t)$ and the true market price $p(t)$. After a step-function crash at $t_0$ where $p$ drops from $p_0$ to $p_1$:

$$\hat{p}(t) = p_1 + (p_0 - p_1) \cdot \alpha^{n(t)}$$

where $n(t) = \lfloor (t - t_0) / \Delta t_{\text{refresh}} \rfloor$ is the number of refreshes since the crash, and the lag operates in log-space (geometric convergence).

**Deliverable:** Tabulate $\hat{p}(t)$ for crash magnitudes of 20%, 30%, 40%, 50%, 70% at refresh counts $n = 1, 2, \ldots, 72$ (72 hours). Produce a heatmap of oracle deviation vs. (crash magnitude × time elapsed).

### 3.2 Effective Health Factor Under Lag

The *true* health factor $H_{\text{true}}(t)$ diverges from the *oracle-reported* health factor $H_{\text{oracle}}(t)$:

$$H_{\text{oracle}}(t) = \frac{w_s \cdot V_s \cdot \hat{p}(t)}{w_b \cdot V_b}$$

$$H_{\text{true}}(t) = \frac{w_s \cdot V_s \cdot p(t)}{w_b \cdot V_b}$$

A position is *phantom-healthy* when $H_{\text{oracle}} \geq 1$ but $H_{\text{true}} < 1$. The **phantom-healthy window** $W$ is the duration for which this condition holds.

**Deliverable:** For each (LTV, crash magnitude) pair, compute $W$ analytically and verify via simulation.

### 3.3 Refresh Timing Worst Case

The 1-hour refresh limit creates an additional delay. Worst case: crash occurs immediately after a refresh, adding up to $\Delta t_{\text{refresh}}$ of total blindness. Model the combined lag:

$$t_{\text{blind}} = \Delta t_{\text{refresh}} + W(\alpha, \text{crash}, \text{LTV})$$

---

## 4. Historical Backtesting

### 4.1 Data Requirements

Obtain minute-level OHLCV data for the following crash events, sourced from CoinGecko, Binance, or equivalent:

| Event | Date | Asset(s) | Peak Drawdown | Duration to Trough |
|---|---|---|---|---|
| Black Thursday | March 12–13, 2020 | ETH | ~43% | ~26 hours |
| May Crash | May 19, 2021 | ETH | ~40% | ~8 hours |
| Terra Contagion | June 12–18, 2022 | ETH, stETH | ~35% | ~6 days |
| FTX Contagion | Nov 7–9, 2022 | ETH | ~25% | ~48 hours |

For Avalanche-specific analysis, also obtain AVAX price data for the same periods, plus any XPower-token-specific data if available.

### 4.2 Backtest Procedure

For each historical crash:

1. **Initialize** a synthetic pool with 1,000 positions drawn from log-normal sizes and health factors $H \sim \mathcal{N}(1.5, 0.3)$ truncated at $[1.0, 3.0]$ (matching existing simulation parameters).
2. **Replay** minute-level price data through the oracle model (α = 0.944, 1-hour refresh).
3. At each minute, compute:
   - $H_{\text{oracle}}(u)$ and $H_{\text{true}}(u)$ for all positions
   - Count of phantom-healthy positions
   - Accumulated bad debt (positions where $H_{\text{true}} < 0$, i.e., collateral < debt at true price)
4. **Simulate liquidations** triggered by oracle price (not true price), tracking:
   - Liquidation delay (time between $H_{\text{true}} < 1$ and $H_{\text{oracle}} < 1$)
   - Bad debt at point of liquidation vs. bad debt if liquidation were instant
5. **Repeat** with lock fractions $\phi \in \{0\%, 25\%, 50\%, 75\%, 100\%\}$.

### 4.3 Outputs

- **Table:** Per-event bad debt as % of TVL, for each (LTV, $\phi$) combination
- **Chart:** Cumulative bad debt timeline for each crash, overlaid with oracle price vs. true price
- **Worst-case metric:** Maximum instantaneous bad debt across all events and parameter combinations

---

## 5. Monte Carlo Simulation

### 5.1 Price Process

Model collateral price as geometric Brownian motion with jump-diffusion (Merton model):

$$\frac{dp}{p} = \mu \, dt + \sigma \, dW + J \, dN$$

where $N$ is a Poisson process with intensity $\lambda_J$ and $J \sim \mathcal{N}(\mu_J, \sigma_J^2)$.

Calibrate parameters to ETH and AVAX historical data:

| Parameter | ETH Estimate | AVAX Estimate |
|---|---|---|
| $\sigma$ (annual vol) | 80–100% | 100–140% |
| $\lambda_J$ (jumps/year) | 4–8 | 6–12 |
| $\mu_J$ (mean jump) | -15% | -20% |
| $\sigma_J$ (jump vol) | 10% | 15% |

### 5.2 Simulation Design

- **Paths:** 100,000 price paths, each 1 year at 1-minute resolution
- **Pool:** 1,000 positions per path, re-initialized at each path start
- **Oracle:** Log-space EMA with α = 0.944, 1-hour refresh
- **Liquidations:** Triggered at $H_{\text{oracle}} < 1$, debt assumption model with $2^{-e}$ partial liquidation
- **Parameters to sweep:**
  - LTV ∈ {33%, 50%, 67%, 75%}
  - Lock fraction $\phi$ ∈ {0%, 25%, 50%, 75%, 100%}
  - Oracle refresh interval ∈ {15min, 30min, 1hr, 2hr}
  - α ∈ {0.891, 0.944, 0.972} (half-lives 6, 12, 24)

### 5.3 Metrics

For each parameter combination, compute:

- **Expected bad debt** $\mathbb{E}[\text{BD}]$ as % of TVL per year
- **VaR(99%):** Bad debt level exceeded with 1% probability
- **CVaR(99%):** Expected bad debt conditional on exceeding VaR(99%)
- **Maximum drawdown-to-bad-debt curve:** Relationship between peak crash severity and resulting bad debt
- **Time-to-liquidation distribution:** Histogram of delay between true underwater and oracle-triggered liquidation

---

## 6. Sensitivity Analysis

### 6.1 Critical Parameters

Produce tornado diagrams showing bad debt sensitivity to:

1. **Oracle decay α** — the primary control lever
2. **Refresh interval** — operational parameter, potentially adjustable
3. **LTV (weight ratio)** — governance-controlled
4. **Lock fraction** — emergent, not directly controlled
5. **Price impact coefficient $k$** — exogenous market condition
6. **Jump intensity $\lambda_J$** — tail risk frequency

### 6.2 Interaction Effects

Test pairwise interactions, particularly:

- **α × LTV:** Does higher LTV amplify the staleness problem non-linearly?
- **α × refresh interval:** Are there diminishing returns to faster refreshes?
- **Lock fraction × price impact $k$:** Do locks reduce bad debt from staleness (not just cascades)?

---

## 7. Analytical Bound Derivation

### 7.1 Worst-Case Bad Debt Bound

Derive an upper bound on bad debt under the following assumptions:

- Price drops by fraction $\delta$ instantaneously
- Oracle absorbs at rate $(1 - \alpha^n)$ per $n$ refreshes
- Position becomes liquidatable when $H_{\text{oracle}} < 1$
- Bad debt equals the shortfall at time of oracle-triggered liquidation

The bound should take the form:

$$\text{BD}_{\max}(\delta, \alpha, \text{LTV}) \leq f(\delta, \alpha, \text{LTV}) \cdot \text{TVL}$$

This provides a governance-usable formula: for a given target maximum bad debt tolerance (e.g., 5% of TVL), what combinations of (α, LTV, refresh interval) satisfy the constraint?

### 7.2 Safety Region

Produce a 3D surface plot of the *safe operating region* in (α, LTV, max tolerable crash) space where expected bad debt stays below a configurable threshold.

---

## 8. Deliverables

| # | Deliverable | Format |
|---|---|---|
| 1 | Oracle lag heatmap (crash magnitude × time → deviation %) | Chart + data table |
| 2 | Phantom-healthy window tables per (LTV, crash) | Data tables |
| 3 | Historical backtest results with bad debt timelines | Charts + summary tables |
| 4 | Monte Carlo bad debt distributions per parameter set | Histograms + VaR/CVaR tables |
| 5 | Sensitivity tornado diagrams | Charts |
| 6 | Interaction effect matrices | Heatmaps |
| 7 | Closed-form or numerical bad debt bound | Formula + proof/derivation |
| 8 | Safe operating region visualization | 3D surface plot |
| 9 | Parameter recommendation for deployment | Summary document |

---

## 9. Acceptance Criteria

1. Historical backtests reproduce known bad-debt events within 20% of reported figures where comparable data exists (e.g., MakerDAO Black Thursday $8.3M)
2. Monte Carlo confidence intervals at 95% level are narrow enough for decision-making (< ±1% of TVL on expected bad debt)
3. Analytical bound is provably conservative (simulation results never exceed the bound across all tested parameters)
4. At least one parameter configuration exists where VaR(99%) bad debt < 5% of TVL for crash magnitudes up to 50%
5. Results are reproducible from provided code with fixed random seeds

---

## 10. Recommended Tools & Frameworks

- **Price data:** CoinGecko API, Binance historical klines, or Kaiko for institutional-grade data
- **Simulation:** Python with NumPy/SciPy for Monte Carlo, Rust for performance-critical inner loops if 100K paths × 525K minutes is too slow in Python
- **Visualization:** Matplotlib/Seaborn for publication-quality charts matching whitepaper style
- **Validation:** Cross-check oracle model against on-chain Foundry test results from Appendix J