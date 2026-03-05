---
title: "Glossary"
description: "Comprehensive terminology from the XPower Banq whitepaper and Technical Appendices A–G."
---

# Glossary

This glossary consolidates all terminology from the main paper and Technical Appendices A–G. Entries marked with a dagger ($\dagger$) are specific to the bad-debt risk analysis ([Appendix G](../part-ii-simulations/bad-debt-risk.md)).

## A

**Acma** — Access manager; wrapper around OpenZeppelin's `AccessManager`. Manages three-tier roles (executor, admin, guard).

**$A(n)$** $\dagger$ — Absorption fraction; the share of the log-space deviation absorbed after $n$ oracle refreshes: $A(n) = 1 - \alpha^{n-1}$ for $n \geq 2$, with $A(0) = A(1) = 0$ due to the one-refresh delay.

**$\alpha$** $\dagger$ — EMA decay parameter of the log-space TWAP oracle. Governs tracking speed: $\alpha = 0.5^{1/\text{HL}}$ where HL is the half-life in refreshes. Default $\alpha \approx 0.944$ (12-hour half-life).

**AMM** — Automated Market Maker; decentralized exchange architecture using liquidity pools and mathematical formulas for price discovery.

**APY Differential** — Difference in annual percentage yield between locked and unlocked positions; with spread $s$, supplier differential is $\Delta r \approx 0.09 \times r_{\text{base}}$.

**Asymptotic Transition** — Parameter change mechanism where values approach targets gradually via time-weighted mean rather than discrete jumps. See Lethargic Governance.

## B

**Bad Debt** — Uncollectable debt arising when a position's collateral value falls below its debt value; protocol absorbs the loss. Quantified in [Appendix G](../part-ii-simulations/bad-debt-risk.md).

**$\text{BD}_{\text{inst}}$** $\dagger$ — Bad debt under instant (zero-delay) liquidation. The baseline shortfall when a position's true collateral value $H_0(1{-}\delta)$ falls below LTV.

**$\text{BD}_{\max}$** $\dagger$ — Conservative upper bound on bad debt (Theorem 6), incorporating the oracle delay penalty: $\text{BD}_{\max} \leq \text{BD}_{\text{inst}} \cdot (1 + W_{\max}\,\sigma_h / \delta)$.

**Beta Cap** — Position limit following $12\lambda(1-\lambda)^2$ distribution where $\lambda$ is the user's fraction of total supply; peaks at $\lambda = 1/3$ and vanishes at boundaries.

**Bid/Ask** — Price quotes for selling (bid) vs. buying (ask) an asset; spread provides manipulation resistance.

**Block Stuffing** — Attack filling blocks with transactions to delay or censor others; prevented by PoW requirements.

**Breakeven Period** — Minimum holding period $T^*$ for lock adoption to be profitable; approximately $T^* \approx D / \Delta r$ where $D$ is secondary market discount and $\Delta r$ is APY differential.

**Borrow Position** — ERC20 token representing debt obligation; uses inverted transfer semantics where `transfer` pulls debt.

## C

**Calculator** — Library providing overflow-safe $\log_2$ and $\exp_2$ operations for the oracle pipeline, wrapping PRBMath's UD60x18 functions. Defines the bias constant `LOG2_ONE` $= \log_2(10^{18}) \approx 59.79$, used to convert between raw `uint256` values and UD60x18 fixed-point representation in the paired functions `Log2()`/`Exp2()`.

**Cap Floor** — Minimum position cap ensuring users can enter even when $\lambda \to 0\text{;}$ prevents cold start problem.

**Capital Efficiency** — Borrowing power per unit of collateral; higher LTV ratios provide greater capital efficiency.

**Cascade Amplification** — Ratio of actual liquidations to initial shock-induced liquidations; measures feedback loop severity. Simulated in [Appendix E](../part-ii-simulations/cascade-simulations.md).

**Circuit Breaker** — Mechanism halting cascading failures; locked positions act as circuit breakers during market stress.

**Cold Start** — Problem where first depositor faces zero or minimal cap due to $\lambda \to 0\text{;}$ solved by cap floor mechanism.

**Collateral** — Assets deposited to back borrowed positions; must exceed borrow value by the over-collateralization ratio.

**Constant Product** — AMM pricing formula ($x \cdot y = k$) used to derive bid/ask quotes from reserve balances.

**Coordination Game** — Strategic interaction where player payoffs depend on aggregate choices; lock adoption exhibits coordination dynamics where seniority value decreases as adoption increases.

**$\text{CVaR}(99\%)$** $\dagger$ — Conditional Value-at-Risk at the 99th percentile; the expected bad debt in the worst 1% of simulated paths.

## D

**Debt Assumption** — Liquidation model where the liquidator assumes the victim's debt rather than repaying it; enables capital-efficient liquidation without requiring liquid capital.

**Decay Factor** — EMA smoothing parameter $\alpha\text{;}$ controls how quickly older price observations lose influence. See also Half-Life.

**$\delta$** $\dagger$ — Crash fraction. An instantaneous price drop from $p_0$ to $p_0(1{-}\delta)\text{;}$ e.g. $\delta = 0.50$ is a 50% crash.

**Difficulty** — PoW puzzle hardness parameter; governance-adjustable per operation type to tune spam resistance.

**Dual Approval** — Transfer model requiring approval from both sender and receiver; used for borrow position transfers.

## E

**Enlisting** — Governance-approved process to add new tokens to a pool; subject to time delays for existing feed modifications.

**EMA** — Exponential Moving Average; smoothing technique giving exponentially decreasing weight to older observations. Applied in log-space for TWAP oracle.

**Entry Fee** — Deposit fee charged when supplying assets to a vault; accrues to existing depositors.

**ERC20** — Ethereum token standard defining transfer, approve, and balance interfaces; basis for position tokens.

**ERC4626** — Tokenized vault standard extending ERC20 with deposit/withdraw mechanics; basis for XPower Banq vaults.

**Exit Fee** — Withdrawal fee charged when redeeming assets from a vault; discourages short-term liquidity cycling.

## F

**Fixed Token List** — Architecture requiring predetermined token sets per pool; ensures predictable collateral requirements.

**Flash Loan** — Uncollateralized loan that must be repaid within the same transaction.

**Formal Verification** — Mathematical proof of smart contract correctness; provides stronger guarantees than testing alone.

**Front-running** — Inserting a transaction before a known pending transaction to profit from its price impact.

## G

**Gas** — Ethereum transaction execution cost; measured in gas units multiplied by gas price.

**Geomean Spread** — Bidirectional geometric mean of relative spreads from forward and reverse AMM queries; stored in log-space as $\log_2(1 + s_{\text{geo}})$. Provides symmetric, manipulation-resistant spread estimation.

**Governance Cycle** — Single parameter change period with minimum duration (e.g., monthly); bounds rate of protocol changes.

## H

**$H_0$** $\dagger$ — Initial health factor of a position: $H_0 = (\text{supply} \times w_s) / (\text{borrow} \times w_b)$. Liquidation triggers when the oracle-observed health $H_{\text{oracle}} < 1$.

**Half-Life** — Time for EMA weight to decay to 50%; determines TWAP responsiveness to new price observations. The [Governance and Parameters](/whitepaper/06-governance) chapter tabulates decay factors.

**Hash Rate** — Computational power for PoW puzzle solving, measured in hashes per second; determines solve time.

**Health Check** — Validation performed after operations ensuring health factor $H \geq 1\text{;}$ reverts if violated.

**Health Factor** — Ratio of weighted supply value to weighted borrow value: $H = \sum w_s V_s / \sum w_b V_b$. Liquidation occurs when $H < 1$.

**Holder-Count Scaling** — Sybil resistance mechanism using the $\sqrt{n+2}$ divisor; creating accounts increases $n$, reducing per-account cap gains.

**Holder Floor** — Minimum holder count $n_{\min}$ used in cap divisor; Sybil resistance only activates when real holders exceed this threshold.

## I

**Index** — Accumulated interest multiplier in ray precision (27 decimals); user balances scale with index ratio.

**Initial Lock Period** — Mandatory delay before first parameter change after deployment; prevents immediate manipulation.

**Integrator** — Library computing $\Delta$-stamp weighted arithmetic means over (timestamp, value) tuples; accumulates area $\sum v_i \cdot \Delta t_i$ and divides by elapsed time. Used by the `Parameterized` base contract to implement asymptotic parameter transitions in lethargic governance ([Section 6](/whitepaper/06-governance)).

**Interest Rate Model** — Utilization-based formula determining borrow/supply APY; slope increases sharply above kink. Formalized in [Appendix A](../part-i-math/mathematical-foundations.md).

**Inverted Transfer** — Borrow position transfer semantics where `transfer(from, amount)` pulls debt FROM the first parameter rather than pushing to it. See [Section 4.2](/whitepaper/04-mechanisms#position-transfer-semantics).

**Iteration Cap** — Maximum capacity gain per governance-defined period (e.g., per week); bounds accumulation rate. Simulated in [Appendix D](../part-ii-simulations/cap-simulations.md).

## K

**Kink** — Utilization threshold (e.g., 90%) where interest rate slope increases; incentivizes liquidity retention.

## L

**Lambda ($\lambda$)** — Balance fraction $B/S\text{;}$ user's holdings divided by total supply.

**Large Holder** — Account holding $\geq 1$ full token unit; tracked for cap calculations.

**Leading Zeros** — PoW validation metric counting zero nibbles at start of hash; determines if difficulty threshold is met.

**Lethargic Governance** — Governance model with time-delayed, bounded parameter transitions. Values approach targets asymptotically, bounded to $0.5\times$–$2\times$ per governance cycle. See [Governance and Parameters](/whitepaper/06-governance).

**Liquidation** — Forced closure of an unhealthy position ($H < 1$); XPower Banq uses debt assumption model.

**Liquidation Cascade** — Destructive feedback loop where forced sales depress prices, triggering further liquidations. Modeled in [Appendix E](../part-ii-simulations/cascade-simulations.md).

**Liquidation Seniority** — Priority in liquidation order; locked positions gain *de facto* seniority because liquidators prefer unlocked positions for immediate liquidity.

**Liquidity Buffer** — Reserve of unutilized assets available for withdrawals; maintained via optimal utilization targeting.

**Lock Adoption** — Aggregate fraction $\bar{\rho}$ of positions that are locked across the protocol; equilibrium adoption varies with utilization regime. Analyzed in [Appendix C](../part-i-math/lock-incentive-analysis.md).

**Lock Bonus** — Additional interest earned by locked suppliers; percentage of interest accrued, bounded by spread.

**Lock Malus** — Interest *reduction* for locked borrowers; percentage of interest owed, bounded by spread.

**Lock Ratio ($\rho$)** — Fraction of position that is locked; $\rho = \text{lock}/\text{balance} \in [0, 1]$.

**Log-Normal Distribution** — Statistical distribution where logarithm is normally distributed; used to model position sizes in simulations (Appendices D, E).

**Log-Space Oracle** — Oracle architecture storing prices as $\log_2(\text{price})$ and spreads as $\log_2(1 + s)\text{;}$ enables EMA smoothing as geometric-mean temporal averaging.

**LTV** — Loan-to-Value ratio; maximum borrowing power as fraction of collateral value. Default $w_s/w_b = 85/255 \approx 33\%$.

## M

**Market Depth** — Total volume that can be traded before significantly moving price; inverse of market impact coefficient.

**Market Impact** — Price change from selling assets; coefficient $k$ relates volume to price depression.

**Market Impact Coefficient** — Constant $k$ in linear price impact model $\Delta p = k \cdot V\text{;}$ relates sell volume to price depression. Used in cascade simulation ([Appendix E](../part-ii-simulations/cascade-simulations.md)).

**Memory Decay** — Weight $\lambda^n$ retained by historical price observations in EMA after $n$ refresh periods; after half-life $h$ periods, weight decays to 50%.

**Mempool** — Transaction waiting area before block inclusion; PoW prevents flooding attacks against mempool.

**MEV** — Maximal Extractable Value; profit available from transaction ordering, insertion, or censorship.

**Monte Carlo Simulation** — Randomized numerical method using many simulated paths to estimate statistical distributions; used for bad-debt risk quantification ([Appendix G](../part-ii-simulations/bad-debt-risk.md)) and TWAP analysis ([Appendix F](../part-ii-simulations/twap-simulations.md)).

**Multiplicative Bounds** — Constraint limiting parameter changes to $0.5\times$–$2\times$ per governance cycle; prevents rapid manipulation.

## N

**Nash Equilibrium** — Stable strategic state where no player can improve their payoff by unilaterally changing strategy; lock adoption exhibits utilization-dependent equilibria. Analyzed in [Appendix C](../part-i-math/lock-incentive-analysis.md).

**Nonce** — Random value in PoW puzzle; combined with transaction data must hash below difficulty target.

## O

**Observation Window** — Time available for detecting suspicious activity during gradual capacity accumulation; enabled by iteration caps.

**Optimal Utilization** — Target utilization $U^*$ (e.g., 90%) where interest rate curve has its kink; balances efficiency and liquidity.

**Oracle Aggregation** — Combining prices from multiple feeds (TraderJoe, Chainlink) using log-space EMA smoothing with bidirectional geomean spread computation.

**Over-collateralization** — Requirement that collateral value exceed borrow value; enforced via health factor $H > 1$.

## P

**Partial Liquidation** — Liquidation of $2^{-e}$ fraction of positions rather than full liquidation.

**$p_{\text{crit}}$** $\dagger$ — Critical oracle price ratio that triggers liquidation: $p_{\text{crit}} = 1 / H_0$. The oracle fires when $\hat{p}(n)/p_0 < p_{\text{crit}}$.

**Phantom-healthy** $\dagger$ — A position state where the oracle reports $H_{\text{oracle}} \geq 1$ (solvent) but the true health $H_{\text{true}} < 1$ (underwater). Arises from oracle staleness during crashes (see [Bad-Debt Risk Analysis](/appendices/part-ii-simulations/bad-debt-risk)).

**Pool** — Main lending/borrowing contract managing supply, borrow, settle, and redeem operations with health checks.

**Pool-to-Depth Ratio** — Pool size as fraction of market depth; determines cascade severity under price shocks.

**Position Lock** — Fraction $\phi$ of a position restricted from redemption or sale; prevents liquidation cascades.

**Position Transfer** — Movement of supply or borrow position tokens between accounts. Supply uses standard ERC20 push; borrow uses inverted pull semantics. Formalized in [Section 4.2](/whitepaper/04-mechanisms#position-transfer-semantics).

**PoW** — Proof-of-Work; computational puzzle required for certain operations to prevent spam.

**Price Feed** — External data source providing asset prices; XPower Banq supports TraderJoe and Chainlink feeds.

**Price Shock** — Sudden price change used to test TWAP responsiveness; EMA smoothing dampens shock impact based on half-life configuration.

**Principal** — Base position amount before interest accrual; multiplied by index ratio to get current balance.

**Protocol Margin** — Revenue retained by protocol from interest spread; $M(\bar{\rho}) = 2s(1-\bar{\rho})$ where $s$ is spread and $\bar{\rho}$ is lock adoption rate.

**Protocol Parameters** — Governable constants (weights, decay, spread, rates, caps) that control protocol behavior; each transitions lethargically. Enumerated in [Governance and Parameters](/whitepaper/06-governance).

## Q

**Quote** — Log-space price representation struct with three fields: `mid` ($\log_2(\text{price} \times 10^{18})$, biased by `LOG2_ONE`), `rel` ($\log_2(1 + s_{\text{geo}})$ where $s_{\text{geo}}$ is the bidirectional geomean spread), and `utc` (timestamp). Replaces linear bid/ask pairs with a compact log-space encoding suitable for EMA smoothing.

## R

**Rate Limit** — Token-bucket mechanism bounding operation frequency; configured per pool with capacity and regeneration rate.

**Ray** — Fixed-point representation with 27 decimal places ($10^{27}$).

**Reentrancy Guard** — Protection preventing a contract from being called recursively during execution; uses transient storage.

**Reindex** — Interest compounding mechanism that updates the global index $I_{\text{ray}}$ and snapshots per-user indices. User balance equals $\text{principal} \times I_{\text{current}} / I_{\text{user}}$. The functions `_reindexMore` and `_reindexLess` apply lock bonus/malus proportionally during position changes.

**Reserves** — Token balances held in AMM liquidity pools; used to calculate bid/ask quotes via constant product formula.

**Role Guard** — Contract restricting which addresses can execute role-gated functions; part of access control system.

## S

**Sandwich Attack** — MEV attack bracketing a victim transaction with front-run and back-run to extract value.

**Secondary Market Discount** — Price reduction $D$ (typically 3–10%) for locked position tokens relative to NAV; reflects inability to redeem for underlying assets.

**$\sigma$, $\sigma_h$** $\dagger$ — Annualized and hourly volatility of the collateral asset. $\sigma_h = \sigma / \sqrt{8760}$. ETH calibration: $\sigma = 90\%$, $\sigma_h \approx 0.96\%$/hour.

**Slippage** — Price deviation from executing a trade against AMM reserves; increases with trade size relative to reserves.

**Solvency Boundary** — Parameter constraint ensuring protocol can meet all obligations; default configuration satisfies $r_{\text{bonus}} + r_{\text{malus}} = 2s$, maintaining solvency for any lock adoption rate.

**Spread** — (1) Oracle: bidirectional geomean of relative spreads from both AMM query directions, stored as $\log_2(1 + s_{\text{geo}})\text{;}$ wider spreads indicate lower liquidity or higher manipulation resistance. (2) IRM: symmetric half-spread parameter (e.g., 10%) applied to base rate; borrow rate = base $\times$ $(1{+}s)$, supply rate = base $\times$ $(1{-}s)$.

**Spread Scaling** — Logarithmic widening of bid/ask spreads for large positions via $\mu = \log_2(2x + 2)$ where $x = n \cdot s$, $n$ is token count and $s$ is relative spread; reflects market impact without governance parameters.

**Square** — Restricted-access liquidation function executing debt assumption: for a given exponent $e$, atomically transfers $\lfloor\text{borrow}/2^e\rfloor$ and $\lfloor\text{supply}/2^e\rfloor$ from victim to liquidator via bit-shift. Reverts if the victim is healthy ($H \geq 1$) or the liquidator's post-transfer health is insufficient. See also Debt Assumption, Partial Liquidation.

**Staleness** — Age of price data from an oracle; stale prices beyond threshold are rejected to prevent exploitation.

**Supply Position** — ERC20 token representing deposited collateral; uses standard transfer semantics.

**Sybil Attack** — Creating multiple accounts to gain unfair advantage; XPower Banq defends against rapid capacity monopolization.

**Sybil Resistance** — Protection against Sybil attacks; in XPower Banq, bounds accumulation *rate* via holder-count scaling, not equilibrium share.

## T

**Time-lock** — Mandatory delay between proposing and executing governance parameter changes; prevents sudden malicious updates.

**Time-Weighted Mean** — Integration technique averaging parameter values over time; enables smooth transitions without discrete jumps.

**Token Bucket** — Rate limiting mechanism with capacity $C$, regeneration rate, and per-operation cost; operation allowed iff $C \geq 0$.

**TVL** $\dagger$ — Total Value Locked; the aggregate collateral value in the lending pool. All bad-debt metrics are reported as a percentage of TVL.

**tx.origin** — Transaction originator address included in PoW hash; prevents front-runners from reusing others' solutions.

**TWAP** — Time-Weighted Average Price; price smoothed over time via log-space EMA (geometric mean temporal averaging) to resist manipulation. Simulated in [Appendix F](../part-ii-simulations/twap-simulations.md).

## U

**Utilization** — Ratio of borrowed assets to supplied assets in a vault; drives interest rates via a piecewise-linear model with a kink at optimal utilization.

## V

**$\text{VaR}(99\%)$** $\dagger$ — Value-at-Risk at the 99th percentile; the bad debt level exceeded in only 1% of simulated paths.

**Vault** — ERC4626-compliant custody contract holding deposited assets; tracks utilization for the interest rate model.

## W

**$W$** $\dagger$ — Phantom-healthy window; the number of oracle refreshes during which a position remains phantom-healthy after a crash.

**WAD** — Fixed-point representation with 18 decimal places ($10^{18}$).

**Weight** — Multiplier applied to asset values in health calculations; determines effective LTV. Default: $w_s = 85$, $w_b = 255$.
