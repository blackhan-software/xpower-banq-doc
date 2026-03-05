---
title: "Appendix F: TWAP Simulations"
description: "Simulation results for the log-space EMA smoothing and logarithmic spread scaling mechanisms of the TWAP oracle."
---

# Appendix F: TWAP Oracle Simulations

This appendix presents simulation results for the log-space EMA smoothing and logarithmic spread scaling mechanisms. The oracle stores $\log_2(\text{mid})$ and $\log_2(1 + s_{\text{geo}})$, smoothed via EMA in log space. All simulations use 18-decimal precision ($1\ \text{unit} = 10^{18}$), matching the Solidity implementation.

## Decay Factor Visualization

The EMA decay factor $\lambda = 0.5^{1/h}$ determines how quickly the TWAP responds to price changes, where $h$ is the half-life in refresh periods. $\lambda$ approaches 1.0 asymptotically with increasing half-life. The steep initial rise means that small changes in low $h$ values have large effects on responsiveness, while values above $h = 20$ yield diminishing returns. In practice, $\lambda$ values between 0.9 and 0.98 provide the useful operating range: below 0.9 the oracle becomes too reactive, while above 0.98 response times may be too slow for timely liquidations.

<figure>
  <img src="/images/008-twap-decay.svg" alt="Decay factor λ by half-life">
  <figcaption>Figure 8: Decay factor λ by half-life. Higher half-life values produce decay factors closer to 1.0, making the TWAP more stable but slower to respond. The protocol default uses h=12 periods (λ ≈ 0.944).</figcaption>
</figure>

## Price Shock Response

The following analysis demonstrates how the TWAP mean responds to a sudden price shock (100 to 150) under different half-life configurations.

The half-life $h$ controls the trade-off between responsiveness and manipulation resistance. Shorter half-lives track market movements closely but are more vulnerable to manipulation; longer half-lives filter transient spikes but delay response to genuine shifts. The log-space EMA update $\overline{q}_{n+1} = \lambda \cdot \overline{q}_n + (1{-}\lambda) \cdot q_n$ ensures smooth convergence without overshooting, with the log transform dampening large deviations more aggressively than a linear EMA. Even with HL=24, the TWAP reaches 90% of the new price within approximately 55 periods.

<figure>
  <img src="/images/009-twap-response.svg" alt="TWAP response to a 50% price shock">
  <figcaption>Figure 9: TWAP response to a 50% price shock at period 5. Shorter half-lives (HL=2) converge quickly but offer less manipulation resistance; longer half-lives (HL=24) provide robust smoothing but respond slowly.</figcaption>
</figure>

The memory decay $\lambda^n$ quantifies how quickly historical prices lose influence: after $k$ half-lives the residual weight is $0.5^k$ (12.5% after 3, less than 1% after 7). For $h = 12$, an attacker must sustain artificial prices for approximately 40 periods to shift the TWAP by 90%.

<figure>
  <img src="/images/010-twap-memory.svg" alt="Memory decay over time">
  <figcaption>Figure 10: Memory decay showing the weight on pre-shock price over time. After HL periods, the weight on the old value drops to 50%. Higher half-lives retain more memory of historical prices.</figcaption>
</figure>

## Spread Scaling by Liquidity

The effective spread depends on both position size and market liquidity (captured by the base spread $\sigma$).

<figure>
  <img src="/images/011-twap-liquidity.svg" alt="Spread scaling by liquidity level">
  <figcaption>Figure 11: Spread scaling by liquidity level. Illiquid pairs (high base spread) experience faster spread growth with trade size.</figcaption>
</figure>

The base spread $\sigma$ serves as a proxy for market depth. The formula $\mu = \log_2(2x + 2)$ with $x = n \cdot \sigma$ provides self-calibrating behavior: liquid markets (low $\sigma$) tolerate larger positions before significant spread widening, eliminating the need for per-pair parameter tuning while ensuring conservative valuations in thin markets.

## Complete Spread Analysis

The following analysis provides a comprehensive view of the spread scaling mechanism using a base spread of 2%. Together, these three views illustrate that while large positions incur wider spreads, the logarithmic scaling keeps them economically reasonable.

<figure>
  <img src="/images/012-twap-spread-quotes.svg" alt="Bid/ask quotes vs. trade size">
  <figcaption>Figure 12: Bid/ask quotes diverge from mid-value as trade size increases. The spread between bid and ask widens logarithmically, protecting against large position manipulation.</figcaption>
</figure>

<figure>
  <img src="/images/013-twap-spread-percent.svg" alt="Effective spread percentage vs. trade size">
  <figcaption>Figure 13: Effective spread grows logarithmically from the base spread (2.0%). At 1 unit the spread is 2.0%; at 1,000 units it reaches 10.8%; at 1,000,000 units it reaches 30.6%.</figcaption>
</figure>

<figure>
  <img src="/images/014-twap-spread-multiplier.svg" alt="Spread multiplier function">
  <figcaption>Figure 14: The multiplier μ = log₂(2x + 2) as a function of x = n · s. This function provides bounded logarithmic growth: μ = 1 at x = 0, growing to μ ≈ 21 at x = 10⁶.</figcaption>
</figure>

## On-Chain Scenario Testing

To complement the preceding simulations, comprehensive on-chain scenario testing of the deployed oracle contract was conducted using Foundry. The test suite exercises 10 attack and stress scenarios across 6 token/liquidity configurations (60 total tests), measuring mid-price deviation and spread response under adversarial conditions. All tests use the production `DECAY_12HL` ($\alpha \approx 0.944$, half-life $h{=}12$ refreshes) with 1-hour refresh intervals.

### Token/Liquidity Configurations

The test matrix covers symmetric and asymmetric reserves across all supported decimal combinations:

| Decimals | Reserves | Profile |
|---|---|---|
| 18/18 | 100/100 | Symmetric standard |
| 18/18 | 180k/50 | Asymmetric standard |
| 6/6 | 100/100 | Symmetric stablecoin |
| 6/6 | 180k/50 | Asymmetric stablecoin |
| 18/6 | 100/100 | Mixed (18 to 6) |
| 6/18 | 100/100 | Mixed (6 to 18) |

### Mid-Price Manipulation Resistance

The following table records the mid-price deviation $\Delta\%$ from baseline after each scenario, measuring how far an attacker (or legitimate market move) can shift the oracle's reported price.

| Scenario | Description | $\Delta\%$ |
|---|---|---|
| S01 | Benign +/-5% oscillations, 24 refreshes | 2.3% |
| S02 | Instant 2x jump, 14 sustained refreshes | 22.5% |
| S03 | Gradual 2x drift over 12 refreshes | 9.1% |
| S04 | 2x spike, immediate return to baseline | 3.7% |
| S05 | 2x spike, gradual return over 12 refreshes | 14.9% |
| S06 | 10x liquidity increase (same ratio) | $<0.01$% |
| S07 | Gradual 10x liquidity increase | $<0.01$% |
| S08 | 90% liquidity drain (same ratio) | $<0.06$% |
| S09 | Gradual 90% liquidity drain | $<0.01$% |
| S10a | 3x manipulation between refreshes | **0%** |
| S10b | 3x manipulation at single refresh | **0%** |

#### Key observations

The delayed EMA provides a *two-tick immunity window*: the first two refreshes after any price spike produce exactly 0% mid-price impact (S02, ticks 4–5), because the spike enters the `last` slot on the first refresh and only propagates into `mean` on the third (${\sim}4\%$ absorption per tick). After 14 sustained refreshes, only 22.5% of a $2\times$ move has been absorbed, consistent with the theoretical bound from the Whitepaper (Section 4.6). Inter-refresh manipulation (S10a) has exactly zero effect, as does single-tick manipulation at refresh time (S10b). Liquidity changes at constant price ratio (S06–S09) produce negligible mid-price deviation ($<0.06\%$), confirming that the log-space mid tracks price independently of pool depth.

### Spread Auto-Widening Response

The following table records the spread percentage for a 1-unit query before and after liquidity changes. The spread correctly reflects pool depth without manual parameterization.

| Scenario | Description | Before | After |
|---|---|---|---|
| S06 | Sudden 10x liquidity | 2.53% | 2.37% |
| S07 | Gradual 10x liquidity | 2.53% | 1.98% |
| S08 | Sudden 90% drain | 2.06% | 3.06% |
| S09 | Gradual 90% drain | 2.06% | 2.52% |

EMA smoothing of the log-space spread produces an asymmetry between sudden and gradual changes: sudden liquidity addition yields approximately 2.37% after 3 ticks (partial absorption), while gradual addition over 12 ticks converges to approximately 1.98%. Sudden removal produces ~50% spread widening (2.06% to 3.06%), providing immediate protection against thin-pool manipulation.

### Decimal Invariance

All scenarios produce identical behavior (to within rounding) across the 6 token configurations. The sole exception is the (6/6, 180k/50) configuration, where integer truncation in 6-decimal arithmetic produces slightly coarser values (e.g., S04 residual of 3.99% vs. 3.74% elsewhere). This confirms that the log-space design is fundamentally decimal-agnostic.

### Strengths and Weaknesses

#### Strengths

1. *Two-tick delay buffer*: The first two refreshes after a spike show 0% mid-price impact, providing strong flash manipulation resistance.
2. *Inter-refresh immunity*: Price changes between refresh windows have exactly zero effect on the oracle.
3. *Self-calibrating spread*: The spread correctly widens and tightens with pool depth changes while keeping the mid stable, without per-pair configuration.
4. *Decimal invariance*: Behavior is consistent across all token decimal combinations (6, 18, and mixed).

#### Weaknesses (inherent to DECAY_12HL)

1. *Slow convergence*: After a legitimate $2\times$ price move, only ${\sim}22.5\%$ is absorbed after 14 hours, potentially enabling arbitrage against stale prices.
2. *EMA reversal lag*: After a $2\times$ spike and full return to baseline, ${\sim}15\%$ residual remains, as the EMA retains memory of past spikes beyond their market relevance.
3. *Slow drift undertracking*: A gradual $2\times$ move over 12 hours shows only 9.1% oracle movement, creating a persistent gap between reported and actual price.

These weaknesses are the intentional cost of heavy smoothing ($\alpha \approx 0.944$). The design prioritizes manipulation resistance over responsiveness—appropriate for a lending protocol where the cost of oracle manipulation (bad debt) exceeds the cost of lagging genuine price moves (delayed liquidations). The hourly refresh cadence further limits the attack surface, as an attacker cannot increase the sampling rate to accelerate EMA convergence toward a manipulated price.
