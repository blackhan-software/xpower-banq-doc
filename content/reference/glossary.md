---
title: Glossary
description: Consolidated glossary across the XPower Banq protocol, time locks, log-space index, theory, and simulations.
---

Consolidated glossary across the six XPower Banq papers. Terms are alphabetised across the union of [Whitepaper](/whitepaper/01-introduction), [Time Locks](/timelocks/01-introduction), [Log-Space Compounding Index](/logspace/01-introduction), [Theory](/theory/01-mathematical-foundations), [Simulations](/simulations/01-cap-accumulation), and Reference.

## A

**Absorption ($A(n)$).** Share of the log-space oracle deviation absorbed after $n$ refreshes: $A(n) = 1 - \alpha^{n-1}$ for $n \geq 2$, with $A(0) = A(1) = 0$ due to the one-refresh delay.

**Accrual.** The periodic update of the global index to reflect newly earned interest. Multiplicative: multiplies the index by $\exp(r)$. Log-space: adds $r$ to the index.

**Active Slot.** A ring-buffer slot whose epoch $e_i \geq e_{\text{now}}$. Included in `stateAt` queries and not yet eligible for sweep.

**Asymptotic Transition.** Parameter change mechanism where values approach targets gradually via time-weighted mean rather than discrete jumps. See *Lethargic Governance*.

## B

**Bad Debt.** Uncollectable debt arising when a position's collateral value falls below its debt value; the protocol absorbs the loss. Quantified in [Bad-Debt Risk](/simulations/04-bad-debt-risk).

**$\text{BD}_{\text{inst}}$.** Bad debt under instant (zero-delay) liquidation. Baseline shortfall when a position's true collateral value $H_0(1{-}\delta)$ falls below LTV.

**$\text{BD}_{\max}$.** Conservative upper bound on bad debt (Theorem 4.3 of the Bad-Debt Risk page), incorporating the oracle delay penalty: $\text{BD}_{\max} \leq \text{BD}_{\text{inst}} \cdot (1 + W_{\max} \, \sigma_h / \delta)$.

**Beta Cap.** Position limit following $12\lambda(1-\lambda)^2$ where $\lambda$ is the user's fraction of total supply; peaks at $\lambda = 1/3$ and vanishes at the boundaries (0 and 1). The $\sqrt{n+2}$ divisor scales the cap inversely with holder count, rate-limiting capacity accumulation.

**Bitmap.** 16-bit mask tracking which ring-buffer slots contain active locks. Stored in the lower 16 bits of the `cache` word.

**Borrow Position.** ERC20 token representing debt obligation; uses inverted transfer semantics where `transfer` pulls debt.

## C

**Cache.** Single storage word in the time-lock layer packing `[uint120 perma | uint120 total | uint16 bits]`. Decoded via shift and mask.

**Cascade Attenuation.** Reduction of liquidation-cascade depth by factor $(1{-}\phi)$, where $\phi$ is the locked fraction. The central result of [Whitepaper §4.1](/whitepaper/04-mechanisms#locked-positions-and-cascade-attenuation).

**Collision.** Two distinct active epochs mapping to the same ring-buffer slot index ($e_i \bmod 16 = e_j \bmod 16$ with $e_i \neq e_j$). Proven impossible by [Theorem 6.1](/timelocks/06-proofs#collision-freedom).

**Compounding Index.** A global accumulator tracking cumulative interest. Multiplicative form: $I = I_0 \prod \exp(r_i)$. Log-space form: $L = \sum r_i$.

**Conservation.** Invariant that $\texttt{totalOf}(u) = p_u \cdot \exp(L - L_u)$ holds for all users at all times, exact up to WAD rounding.

**Coordination Game.** Strategic interaction where player payoffs depend on aggregate choices; lock adoption exhibits coordination dynamics where seniority value decreases as adoption increases.

**Crash Fraction ($\delta$).** Instantaneous price drop from $p_0$ to $p_0(1-\delta)$; e.g. $\delta = 0.50$ is a 50% crash.

**CVaR(99%).** Conditional Value-at-Risk at the 99th percentile — the expected bad debt in the worst 1% of simulated paths.

## D

**Debt Assumption.** Liquidation model where the liquidator assumes the victim's debt rather than repaying it; enables capital-efficient liquidation without requiring liquid capital.

**Decay ($\alpha$).** EMA decay parameter of the log-space TWAP oracle. Governs tracking speed: $\alpha = 0.5^{1/h}$ where $h$ is the half-life in refreshes. Default $\alpha \approx 0.944$ (12 refreshes; 12-hour half-life with the default 1-hour refresh interval).

**Depth ($\Sigma$).** Cached epoch-weighted sum $\sum v_i(e_i+1)$ enabling $O(1)$ token-second reconstruction.

**Depth Identity.** The algebraic identity $D = \Sigma Q - Tt + pL$ ([Theorem 5.1](/timelocks/05-time-lock#_5-2-the-o-1-depth-identity)) that converts the $O(k)$ token-seconds sum into an $O(1)$ cached computation.

**Dust Extraction.** Theoretical attack exploiting rounding errors to extract small token amounts. Bounded at ≤2 wei per `totalOf` query in the log-space form.

## E

**EMA Decay Factors.** See [EMA Decay Factors](/reference/ema-decay).

**Epoch.** Absolute quarter index $e = \lfloor t / Q \rfloor$. Each epoch spans exactly $Q$ seconds.

## G

**Geomean Spread.** Bidirectional geometric mean of relative spreads from forward and reverse AMM queries; stored in log-space as $\log_2(1 + s_{\text{geo}})$. Provides symmetric, manipulation-resistant spread estimation.

**Growth Factor.** Ratio $G = \exp(L - L_u)$ by which a user's principal has grown since their last snapshot.

## H

**Half-Life.** Time for EMA weight to decay to 50%; determines TWAP responsiveness to new price observations.

**Health Factor ($H$).** Ratio of weighted supply value to weighted borrow value: $H = \sum w_s V_s / \sum w_b V_b$. Liquidation occurs when $H < 1$. With default weights ($w_s = 170$, $w_b = 255$), the effective LTV is $\approx 66.67\%$.

**$H_0$.** Initial health factor of a position. Liquidation triggers when the oracle-observed health $H_{\text{oracle}} < 1$.

## I

**Inverted Transfer.** Borrow-position transfer semantics where `transfer(from, amount)` pulls debt FROM the first parameter rather than pushing to it. See [Whitepaper §4.2](/whitepaper/04-mechanisms#position-transfer-semantics).

## K

**Kink.** Utilization threshold (e.g. 90%) where interest-rate slope increases; incentivizes liquidity retention.

## L

**Lethargic Governance.** Governance model with time-delayed, bounded parameter transitions. Values approach targets asymptotically, bounded to $0.5\times$–$2\times$ per governance cycle.

**Liquidation.** Forced closure of an unhealthy position ($H < 1$); XPower Banq uses a debt-assumption model.

**Liquidation Cascade.** Destructive feedback loop where forced sales depress prices, triggering further liquidations. Modeled in [Cascade Simulations](/simulations/02-cascade).

**Liquidation-Recovery Haircut ($\kappa$).** Fraction of collateral value lost to slippage and gas during liquidation; applied to the partial-liquidation recovery model.

**Liquidation Seniority.** Priority in liquidation order; locked positions gain *de facto* seniority because liquidators prefer unlocked positions for immediate liquidity.

**Lock Adoption ($\bar{\rho}$).** Aggregate fraction of positions that are locked across the protocol; equilibrium adoption varies with utilization regime. Analyzed in [Theory: Nash Equilibrium](/theory/03-nash-equilibrium).

**Lock Bonus.** Additional interest earned by locked suppliers; percentage of interest accrued, bounded by spread.

**Lock Depth.** Weighted sum $\sum v_i \times (e_i + 1)$ across a user's time-locked positions, where $v_i$ is the locked value and $e_i$ is the epoch. Used in lock bonus/malus computation.

**Lock Malus.** Interest *reduction* for locked borrowers; percentage of interest owed, bounded by spread.

**Lock Ratio ($\rho$ or $\lambda$).** Fraction of position that is locked; $\rho = \texttt{lock}/\texttt{balance} \in [0, 1]$. In time-lock context: $\lambda(u) = \texttt{depthOf}(u) / \texttt{balanceOf}(u)$ measures normalized commitment depth.

**Lock Yield.** Term `rate × depth × (exp(ΔL) − 1) / (10^18 × LOCK_TIME)` bonus or malus applied to locked positions.

**`LOCK_TERM` ($Q$).** One quarter ≈ 91.3 days — the epoch duration and ring-buffer granularity.

**`LOCK_TIME` ($L$).** $16 \times Q \approx 48$ months — maximum lock duration and permanent-lock depth cap.

**Log-Space Index ($L$).** Cumulative sum of per-period WAD yields, stored in `uint256`. Initialised to 0. Grows linearly (additively).

**Log-Space Oracle.** Oracle architecture storing prices as $\log_2(\text{price})$ and spreads as $\log_2(1 + s)$; enables EMA smoothing as geometric-mean temporal averaging.

**Log-Sum-Exp.** Numerical identity $\sum \log x_i = \log \prod x_i$, used classically to avoid overflow in iterated products.

**LTV.** Loan-to-Value ratio — maximum borrowing power as a fraction of collateral value; default $w_s/w_b = 170/255 \approx 66.67\%$.

## M

**Merton Jump-Diffusion.** Asset-price model with continuous Brownian motion plus a Poisson-driven jump component; basis for the [Monte Carlo bad-debt simulation](/simulations/04-bad-debt-risk).

**Monotonicity.** Property that $L(t)$ is non-decreasing: each accrual adds a non-negative yield.

**Monte Carlo Simulation.** Randomized numerical method using many simulated paths to estimate statistical distributions; used for bad-debt risk quantification and TWAP analysis.

**Multiplicative Bounds.** Constraint limiting parameter changes to $0.5\times$–$2\times$ per governance cycle; prevents rapid manipulation.

**Multiplicative Index ($I$).** Running product of exponential growth factors, stored at RAY ($10^{27}$) precision. Grows exponentially.

## N

**Nash Equilibrium.** Stable strategic state where no player can improve their payoff by unilaterally changing strategy; lock adoption exhibits utilization-dependent equilibria.

## O

**Overflow Horizon.** Time until a stored value exceeds $2^{256}$. For the multiplicative RAY index: ~29–1,154 years depending on rate. For the log-space WAD index: ~$10^{58}$ years.

## P

**Permanent Lock.** Irrevocable lock with `dt_term = 2^256 − 1`. Stored in the upper 120 bits of `cache` (`cache.perma`), not in a ring slot. Contributes $p \cdot L$ to token-seconds at query time.

**Phantom-Healthy.** Position state where the oracle reports $H_{\text{oracle}} \geq 1$ (solvent) but the true health $H_{\text{true}} < 1$ (underwater). Arises from oracle staleness during crashes.

**Position Lock.** Fraction $\phi$ of a position restricted from redemption or sale; prevents liquidation cascades.

**$p_{\text{crit}}$.** Critical oracle price ratio that triggers liquidation: $p_{\text{crit}} = 1 / H_0$. The oracle fires when $\hat{p}(n)/p_0 < p_{\text{crit}}$.

**Position Layer.** The `Position` contract that wraps the `Lock` library, enforcing the `free(tgt)` precondition.

**PRBMath.** A Solidity library providing fixed-point `exp()`, `ln()`, `mul()`, and related functions at WAD ($10^{18}$) precision. The `exp()` function reverts when its input exceeds $133.08 \times 10^{18}$.

**Protocol Margin.** Revenue retained by protocol from interest spread; $M(\bar{\rho}) = 2s(1 - \bar{\rho})$ where $s$ is spread and $\bar{\rho}$ is lock adoption rate.

## R

**Read Path.** Code path executed when querying a user's balance via `totalOf`. In the log-space form, this is where `exp()` is called.

**Reindex.** Interest compounding mechanism that updates the global log-space index and snapshots per-user indices.

**Ring Buffer.** Circular array of 16 slots indexed by $e \bmod 16$. Overwrites stale entries automatically when epochs advance beyond the window.

**Ring-Lock.** Base mechanism: ring buffer + bitmap + cached total. 9 words per user.

## S

**Self-Healing.** `more()` correcting stale slot contributions during overwrite, maintaining `total` and `depth` consistency per-slot ([Theorem 6.7](/timelocks/06-proofs#self-healing-correctness)).

**$\sigma$, $\sigma_h$.** Annualized and hourly volatility of the collateral asset. $\sigma_h = \sigma / \sqrt{8760}$. ETH calibration: $\sigma = 90\%$, $\sigma_h \approx 0.96\%$/hour.

**Slot.** One of 16 ring-buffer entries, indexed by $e \bmod 16$. Packs `uint16 epoch` and `uint112 value` in one storage half-word.

**Solvency Boundary.** Parameter constraint ensuring the protocol can meet all obligations; default configuration satisfies $r_{\text{bonus}} + r_{\text{malus}} = 2s$, maintaining solvency for any lock adoption rate.

**Spread.** (1) **Oracle:** bidirectional geomean of relative spreads from both AMM query directions, stored as $\log_2(1 + s_{\text{geo}})$; wider spreads indicate lower liquidity or higher manipulation resistance. (2) **IRM:** symmetric half-spread parameter (e.g., 10%) applied to base rate; borrow rate = base × (1 + s), supply rate = base × (1 − s).

**Stale Slot.** Slot with $e < e_{\text{now}}$ — expired but not yet swept by `free()`. Causes `totalOf` inflation and `depthOf` deflation until cleared.

**Supply Position.** ERC20 token representing deposited collateral; uses standard transfer semantics.

## T

**Time-Lock (Lock Extension).** Extension of Ring-Lock adding the `depth` mapping for token-seconds. 10 words per user.

**Time-Weighted Mean.** Integration technique averaging parameter values over time; enables smooth transitions without discrete jumps.

**Token Bucket.** Rate-limiting mechanism with capacity $C$, regeneration rate, and per-operation cost; operation allowed iff $C \geq 0$.

**Token-Seconds.** $\sum v_i \times \text{remaining time}$ — integral of locked amount over remaining time. The depth metric that drives graduated commitment.

**Truncation Bias.** Systematic negative error introduced by fixed-point truncation (rounding toward zero). In the multiplicative form, this bias compounds over $N$ accrual steps ($\leq 2N$ ULP). The log-space form has zero truncation during accrual.

**TVL.** Total Value Locked — the aggregate collateral value in the lending pool. All bad-debt metrics are reported as a percentage of TVL.

**TWAP.** Time-Weighted Average Price — price smoothed over time via log-space EMA (geometric mean temporal averaging) to resist manipulation.

## U

**UD60x18.** PRBMath's unsigned 60.18-decimal fixed-point type. 60 integer digits and 18 fractional digits, fitting in `uint256`. Used for `exp()`, `mul()`, and `ln()` operations.

**`uint256`.** Solidity's 256-bit unsigned integer type, holding values from 0 to $2^{256} - 1 \approx 1.16 \times 10^{77}$. The storage type for both the multiplicative and log-space indices.

**ULP.** Unit in the Last Place — the smallest representable increment at a given precision. At WAD: 1 ULP = 1 wei = $10^{-18}$.

**User Snapshot ($L_u$).** Value of $L$ at the user's last state transition, stored in `_userIndex[user]`.

**Utilization.** Ratio of borrowed assets to supplied assets in a vault; drives interest rates via a piecewise-linear model with a kink at optimal utilization.

## V

**VaR(99%).** Value-at-Risk at the 99th percentile — the bad debt level exceeded in only 1% of simulated paths.

**Vault.** ERC4626-compliant custody contract holding deposited assets; tracks utilization for the interest rate model.

## W

**WAD.** Fixed-point representation with 18 decimal places ($10^{18}$).

**Window ($W$).** (1) Phantom-healthy window — the number of oracle refreshes during which a position remains phantom-healthy after a crash. (2) The 16-epoch span $[e_{\text{now}}, e_{\text{now}}+15]$ of valid future ring-buffer slots.

**Write Path.** Code path executed during index accrual (`_reindex`). In the log-space form, this is a single addition; in the multiplicative form, it calls `exp()` and `mul()`.
