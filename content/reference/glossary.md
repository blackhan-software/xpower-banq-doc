# Glossary

Comprehensive terminology for the XPower Banq protocol suite — the consolidated [References & Glossary paper](/research/whitepaper) ported into web form. Entries marked with a dagger (†) are specific to the bad-debt risk analysis in the [simulations paper](/research/papers/simulations).

Where a term names a governable parameter, contract, or feature, the entry links out to its dedicated page rather than restating values. Numeric ranges and per-cycle bounds live in [Parameters](/parameters/pool-parameters) and the [governance parameter catalog](/governance/parameter-catalog).

## A

**Accrual.** The periodic update of the global index to reflect newly earned interest. In the multiplicative form, accrual multiplies the index by $\exp(r)$; in the [log-space form](/research/papers/log-space-index), it adds $r$ to the index.

**Accrual Path.** The code path executed during a [reindex](#reindex) event. Also called the *write path*, since it mutates the stored index.

**Acma.** Access manager — wrapper around OpenZeppelin's `AccessManager`; manages three-tier roles per capability — the bare function-caller role (e.g. `SET_TARGET`), its `_ADMIN` (grants/revokes the caller role), and its `_GUARD` (emergency revoke). Role IDs are **scoped per pool**: derived via `uint64(bytes8(keccak256(<verb>, <domain>, <pool-name>)))` in the `Roles` library, so `POOL_SQUARE_ROLE("P007")` is distinct from `POOL_SQUARE_ROLE("P000")`. The only global role is `ACMA_RELATE_ROLE()`. See [role hierarchy](/features/lethargic-governance/role-hierarchy) and [architecture overview](/for-developers/architecture-overview).

**$A(n)$ †.** Absorption fraction — the share of the log-space deviation absorbed after $n$ oracle refreshes: $A(n) = 1 - \alpha^{n-1}$ for $n \geq 2$, with $A(0) = A(1) = 0$ due to the one-refresh delay.

**Annualised Rate ($r_{\text{annual}}$).** The interest rate expressed per year in WAD. Converted to per-period yield via $r_{\text{annual}} \times \Delta t / \text{year}$.

**$\alpha$ †.** EMA decay parameter of the [log-space TWAP oracle](/parameters/oracle-parameters). Governs tracking speed: $\alpha = 0.5^{1/\text{HL}}$ where HL is the half-life in refreshes. Default $\alpha \approx 0.944$ (12 refreshes; with the default 1-hour refresh interval enforced by `PowLimited(1 hours)` in `Oracle`, this is a 12-hour half-life). Stored on-chain as the `DECAY` parameter.

**AMM.** Automated Market Maker — decentralized exchange architecture using liquidity pools and mathematical formulas for price discovery.

**APY Differential.** Difference in annual percentage yield between [locked](/features/locked-positions/overview) and unlocked positions; with spread $s$, supplier differential is $\Delta r \approx 0.09 \times r_{\text{base}}$.

**Asymptotic Transition.** Parameter change mechanism where values approach targets gradually via [time-weighted mean](#time-weighted-mean) rather than discrete jumps. See [lethargic governance](/features/lethargic-governance/overview) and [transition curves](/features/lethargic-governance/transition-curves).

## B

**Bad Debt.** Uncollectable debt arising when a position's collateral value falls below its debt value; protocol absorbs the loss. See [bad debt scenarios](/risks/bad-debt-scenarios) and the [simulations paper](/research/papers/simulations).

**Base Risk Premium ($b$).** The on-chain `BASE` position parameter: a flat rate added to the [kinked rate](#kink) regardless of utilization, giving $R(U) = \min(R_k(U) + b,\ 200\%)$. Defaults to `0%` (the model then behaves like the classic kinked curve). See [interest rates](/concepts/interest-rates) and [position parameters](/parameters/position-parameters).

**Bitmap.** 16-bit mask tracking which slots contain active locks. Stored in the lower 16 bits of `cache`. See [ring-lock](/research/papers/ring-buffer-locks).

**$\text{BD}_{\text{inst}}$ †.** Bad debt under instant (zero-delay) liquidation. The baseline shortfall when a position's true collateral value $H_0(1{-}\delta)$ falls below LTV.

**$\text{BD}_{\max}$ †.** Conservative upper bound on bad debt, incorporating the oracle delay penalty: $\text{BD}_{\max} \leq \text{BD}_{\text{inst}} \cdot (1 + W_{\max}\,\sigma_h / \delta)$.

**Beta Cap.** Position limit following $12\lambda(1-\lambda)^2$ distribution where $\lambda$ is the user's fraction of total supply; peaks at $\lambda = 1/3$ and vanishes at boundaries. See [position caps](/features/position-caps/overview) and [how caps grow](/features/position-caps/how-caps-grow).

**Bid/Ask.** Price quotes for selling (bid) vs. buying (ask) an asset; spread provides manipulation resistance.

**Block Stuffing.** Attack filling blocks with transactions to delay or censor others; prevented by [PoW](#pow) requirements.

**Breakeven Period.** Minimum holding period $T^*$ for lock adoption to be profitable; approximately $T^* \approx D / \Delta r$ where $D$ is [secondary market discount](#secondary-market-discount) and $\Delta r$ is APY differential.

**Borrow Position.** ERC20 token representing debt obligation; uses [inverted transfer](#inverted-transfer) semantics where `transfer` pulls debt. See [positions as tokens](/concepts/positions-as-tokens) and [ERC20 semantics](/for-developers/erc20-semantics).

**Borrow Rate.** The interest rate charged to borrowers, computed as $R(U) \times (1 + s)$ where $R(U) = R_k(U) + b$ (kinked rate plus [base risk premium](#base-risk-premium)) and $s$ is the spread parameter. Capped at $200\% \times (1 + s)$. See [interest rates](/concepts/interest-rates).

**Break-Even Ratio ($R$).** The on-chain read/write ratio at which the [log-space transformation](/research/papers/log-space-index) is gas-neutral. Computed as $R = 1{,}200 / 1{,}100 \approx 1.09$.

## C

**Calculator.** Library providing overflow-safe $\log_2$ and $\exp_2$ operations for the oracle pipeline, wrapping PRBMath's UD60x18 functions. Defines the bias constant `LOG2_ONE` $= \log_2(10^{18}) \approx 59.79$ (internal `private constant`, scaled $\times 10^{18}$ as a UD60x18 value), used to convert between raw `uint256` values and UD60x18 fixed-point representation in the paired functions `Log2()` / `Exp2()`.

**Cap Floor.** Minimum position cap ensuring users can enter even when $\lambda \to 0$; prevents [cold start](#cold-start) problem. See [new user allocation](/features/position-caps/new-user-allocation).

**Capital Efficiency.** Borrowing power per unit of collateral; higher LTV ratios provide greater capital efficiency.

**Caps (contract).** A minimally-privileged wrapper around `Pool.capSupply`/`capBorrow` exposing `incSupply`, `decSupply`, `incBorrow`, `decBorrow` — each gated by its own ACMA role triple. Delta-based and saturating (at `0` and `2¹¹² − 1`). Used by the [circuit-breaker bot](/features/position-caps/caps-wrapper-and-circuit-breaker) to lower caps safely. Mirrored by the `Pols` contract for POL fetching.

**Cascade Amplification.** Ratio of actual liquidations to initial shock-induced liquidations; measures feedback loop severity. See [bad debt risk](/research/papers/simulations).

**Cascade Attenuation.** Reduction of liquidation-cascade depth by factor $(1{-}\phi)$, where $\phi$ is the locked fraction of the position; the central result of the cascade theorem in the [theory paper](/research/papers/theory-and-proofs). See [cascade protection](/features/locked-positions/cascade-protection).

**Circuit Breaker.** Mechanism halting cascading failures; locked positions act as circuit breakers during market stress.

**Cold Start.** Problem where the first depositor faces zero or minimal cap due to $\lambda \to 0$; solved by [cap floor](#cap-floor) mechanism.

**Collateral.** Assets deposited to back borrowed positions; must exceed borrow value by the [over-collateralization](#over-collateralization) ratio.

**Compounding Index.** A global accumulator tracking cumulative interest. Multiplicative form: $I = I_0 \prod \exp(r_i)$. Log-space form: $L = \sum r_i$. See [log-space index paper](/research/papers/log-space-index).

**Conservation.** The invariant that `totalOf(u)` $= p_u \cdot \exp(L - L_u)$ holds for all users at all times, exact up to WAD rounding.

**Constant Product.** AMM pricing formula ($x \cdot y = k$) used to derive bid/ask quotes from reserve balances.

**Coordination Game.** Strategic interaction where player payoffs depend on aggregate choices; lock adoption exhibits coordination dynamics where seniority value decreases as adoption increases. See the [theory paper](/research/papers/theory-and-proofs).

**$\text{CVaR}(99\%)$ †.** Conditional Value-at-Risk at the 99th percentile — the expected bad debt in the worst 1% of simulated paths.

## D

**Debt Assumption.** Liquidation model where the liquidator assumes the victim's debt rather than repaying it; enables capital-efficient liquidation without requiring liquid capital. See [debt-assumption liquidation overview](/features/debt-assumption-liquidation/overview).

**Decay Factor.** EMA smoothing parameter $\alpha$ — the on-chain `DECAY` parameter; controls how quickly older price observations lose influence. See [oracle parameters](/parameters/oracle-parameters) and [half-life](#half-life).

**$\delta$ †.** Crash fraction. An instantaneous price drop from $p_0$ to $p_0(1{-}\delta)$; e.g. $\delta = 0.50$ is a 50% crash.

**Depth ($\Sigma$).** Cached epoch-weighted sum $\sum v_i(e_i{+}1)$ enabling $O(1)$ token-second reconstruction. See [ring-buffer locks paper](/research/papers/ring-buffer-locks).

**Depth Identity.** The algebraic identity $D = \Sigma Q - Tt + pL$ that converts the $O(k)$ token-seconds sum into an $O(1)$ cached computation. Stated as a theorem in the [ring-buffer locks paper](/research/papers/ring-buffer-locks).

**Difficulty.** PoW puzzle hardness parameter; governance-adjustable per operation type to tune spam resistance. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

**Dual Approval.** Transfer model requiring approval from both sender and receiver; used for borrow position transfers. See [ERC20 semantics](/for-developers/erc20-semantics).

**Dust Extraction.** A theoretical attack exploiting rounding errors to extract small token amounts. Bounded at $\leq 2$ wei per `totalOf` query in the log-space form.

## E

**E-fold.** One unit of natural-logarithmic growth; a factor of $e \approx 2.718$. The RAY index has ${\sim}115$ e-folds before overflow.

**Enlisting.** Governance-approved process to add new tokens to a pool; subject to time delays for existing feed modifications. The relevant role is `POOL_ENLIST_ROLE` (with companion admin/guard).

**EMA.** Exponential Moving Average — smoothing technique giving exponentially decreasing weight to older observations. Applied in log-space for the [TWAP oracle](/features/twap-oracle/overview).

**Entry Fee.** Deposit fee charged when supplying assets to a vault; accrues to existing depositors. The on-chain `FEE_ENTRY` parameter — see [vault parameters](/parameters/vault-parameters).

**Epoch.** Absolute quarter index $e = \lfloor t/Q \rfloor$. Each epoch spans exactly $Q$ seconds.

**ERC20.** Ethereum token standard defining transfer, approve, and balance interfaces; basis for position tokens. See [ERC20 semantics](/for-developers/erc20-semantics).

**ERC4626.** Tokenized vault standard extending ERC20 with deposit/withdraw mechanics; basis for the XPower Banq Vault. See [ERC4626 vaults](/for-developers/erc4626-vaults). Position tokens themselves are `ERC20Permit`, not ERC4626.

**Exit Fee.** Withdrawal fee charged when redeeming assets from a vault; discourages short-term liquidity cycling. The on-chain `FEE_EXIT` parameter — see [vault parameters](/parameters/vault-parameters).

## F

**Fixed Token List.** Architecture requiring predetermined token sets per pool; ensures predictable collateral requirements.

**Flash Loan.** Uncollateralized loan that must be repaid within the same transaction.

**Formal Verification.** Mathematical proof of smart contract correctness; provides stronger guarantees than testing alone. See [audits and reviews](/security/audits-and-reviews) for current status.

**Front-running.** Inserting a transaction before a known pending transaction to profit from its price impact.

## G

**Gas.** Ethereum transaction execution cost; measured in gas units multiplied by gas price. See [gas costs](/for-developers/gas-costs).

**Geomean Spread.** Bidirectional geometric mean of relative spreads from forward and reverse AMM queries; stored in log-space as $\log_2(1 + s_{\text{geo}})$. Provides symmetric, manipulation-resistant spread estimation. See [spread and slippage](/features/twap-oracle/spread-and-slippage).

**Governance Cycle.** Single parameter change period with minimum duration (e.g., monthly); bounds rate of protocol changes. See [parameter bounds](/features/lethargic-governance/parameter-bounds).

**Growth Factor.** The ratio $G = \exp(L - L_u)$ by which a user's principal has grown since their last snapshot.

## H

**$H_0$ †.** Initial health factor of a position: $H_0 = (\text{supply} \times w_s) / (\text{borrow} \times w_b)$. Liquidation triggers when the oracle-observed health $H_{\text{oracle}} < 100\%$.

**Half-Life.** Time for EMA weight to decay to 50%; determines TWAP responsiveness to new price observations.

**Hash Rate.** Computational power for PoW puzzle solving, measured in hashes per second; determines solve time.

**Health Check.** Validation performed after operations ensuring health factor $H \geq 100\%$; reverts if violated.

**Health Factor.** Ratio of weighted supply value to weighted borrow value: $H = \sum w_s V_s / \sum w_b V_b$, expressed as a percentage. Liquidation occurs when $H < 100\%$. See [health factor](/concepts/health-factor) and [monitoring health](/using-the-protocol/monitoring-health).

**Holder-Count Scaling.** Sybil resistance mechanism using the $\sqrt{n+2}$ divisor; creating accounts increases $n$, reducing per-account cap gains. See [position caps](/features/position-caps/overview).

**Holder Floor.** Governable lower bound on the effective holder count used in the cap divisor; `largeHolders()` $= \max(\text{real\_holders},\, n_{\min})$, with $n_{\min}$ a [lethargic governance](#lethargic-governance) parameter capped at `Constant.MIN_HOLDERS` = $10^{18}$. See [position parameters](/parameters/position-parameters) for `MIN_HOLDERS`.

## I

**Index.** Logarithmic accumulated-rate index stored in WAD (18 decimals) inside the packed state word; per-user balance growth is $\exp(I_{\text{global}} - I_{\text{user}})$, the exponential of the log-space delta. See the [log-space index paper](/research/papers/log-space-index).

**Initial Lock Period.** Mandatory delay before first parameter change after deployment; prevents immediate manipulation. See [change-rate constraints](/parameters/change-rate-constraints).

**Integrator.** Library computing $\Delta$-stamp weighted arithmetic means over (timestamp, value) tuples; accumulates area $\sum v_i \cdot \Delta t_i$ and divides by elapsed time. Used by the `Parameterized` base contract to implement [asymptotic parameter transitions](/features/lethargic-governance/transition-curves) in lethargic governance.

**Interest Rate Model.** Utilization-based formula determining borrow/supply APY: a piecewise-linear kinked curve $R_k(U)$ plus a flat [base risk premium](#base-risk-premium) $b$, capped at 200%; slope increases sharply above the [kink](#kink). Formalized in the [theory paper](/research/papers/theory-and-proofs). See [interest rates](/concepts/interest-rates).

**Inverted Transfer.** Borrow position transfer semantics where `transfer(from, amount)` pulls debt FROM the first parameter rather than pushing to it. See [ERC20 semantics](/for-developers/erc20-semantics) and [transferring positions](/using-the-protocol/transferring-positions).

**Iteration Cap.** Maximum capacity gain per governance-defined period (e.g., per week); bounds accumulation rate. See [how caps grow](/features/position-caps/how-caps-grow).

## K

**Kink.** Utilization threshold (e.g., 90%) where interest rate slope increases; incentivizes liquidity retention. See [interest rates](/concepts/interest-rates).

## L

**Lambda ($\lambda$).** Balance fraction $B/S$; user's holdings divided by total supply.

**Large Holder.** Account holding $\geq 1$ full token unit; tracked for cap calculations.

**Leading Zeros.** PoW validation metric counting zero nibbles at start of hash; determines if difficulty threshold is met. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

**Lethargic Governance.** Governance model with time-delayed, bounded parameter transitions. Values approach targets asymptotically, bounded to $0.5\times$–$2\times$ per [governance cycle](#governance-cycle). See [lethargic governance overview](/features/lethargic-governance/overview).

**Liquidation.** Forced closure of an unhealthy position ($H < 100\%$); XPower Banq uses the [debt assumption](#debt-assumption) model. See [liquidation](/concepts/liquidation).

**Liquidation Cascade.** Destructive feedback loop where forced sales depress prices, triggering further liquidations. Modeled in the [simulations paper](/research/papers/simulations).

**Liquidation Seniority.** Priority in liquidation order; locked positions gain *de facto* seniority because liquidators prefer unlocked positions for immediate liquidity.

**Liquidation-Recovery Haircut ($\kappa$) †.** Fraction of collateral value lost to slippage and gas during liquidation; applied to the partial-liquidation recovery model.

**Liquidity Buffer.** Reserve of unutilized assets available for withdrawals; maintained via optimal utilization targeting.

**Lock Adoption.** Aggregate fraction $\bar{\rho}$ of positions that are locked across the protocol; equilibrium adoption varies with utilization regime. Analyzed in the [theory paper](/research/papers/theory-and-proofs).

**Lock Bonus.** Additional interest earned by locked suppliers; percentage of interest accrued, bounded by [spread](#spread). The on-chain `LOCK_BONUS` parameter — see [position parameters](/parameters/position-parameters) and [bonus and malus](/features/locked-positions/bonus-and-malus).

**Lock Depth.** The weighted sum $\sum v_i \times (e_i + 1)$ across a user's time-locked positions, where $v_i$ is the locked value and $e_i$ is the epoch. Used in lock bonus/malus computation.

**Lock Malus.** Interest *reduction* for locked borrowers; percentage of interest owed, bounded by [spread](#spread). The on-chain `LOCK_MALUS` parameter — see [position parameters](/parameters/position-parameters) and [bonus and malus](/features/locked-positions/bonus-and-malus).

**Lock Ratio ($\rho$).** Fraction of position that is locked; $\rho = \text{lock}/\text{balance} \in [0, 1]$.

**Lock Yield.** The `rate` $\times$ `depth` $\times (\exp(\Delta L) - 1) / (10^{18} \times$ `LOCK_TIME`$)$ bonus or malus applied to locked positions, where `LOCK_TIME` is the maximum lock horizon in seconds (16 quarterly slots = 48 months $\approx 1.26 \times 10^{8}$ s; defined in the `Lock` library).

**LOCK_TERM ($Q$).** One quarter $\approx 91.3$ days — the epoch duration and ring-buffer granularity.

**LOCK_TIME ($L$).** $16 \times Q \approx 48$ months — maximum lock duration and permanent lock depth cap.

**Log-Normal Distribution.** Statistical distribution where logarithm is normally distributed; used to model position sizes in simulations.

**Log-Space Index ($L$).** The cumulative sum of per-period WAD yields, stored in `uint256`. Initialised to 0. Grows linearly (additively). See [log-space index paper](/research/papers/log-space-index).

**Log-Space Oracle.** Oracle architecture storing prices as $\log_2(\text{price})$ and spreads as $\log_2(1 + s)$; enables EMA smoothing as geometric-mean temporal averaging.

**Log-Sum-Exp.** The numerical identity $\sum \log x_i = \log \prod x_i$, used classically to avoid overflow in iterated products. The theoretical basis for the [log-space index](#log-space-index-l).

**LTV.** Loan-to-Value ratio — maximum borrowing power as fraction of collateral value. *Not* a stored on-chain parameter; derived from the supply/borrow weights as $w_s/w_b$. Default $170/255 \approx 66.67\%$. See [pool parameters](/parameters/pool-parameters) for the underlying weights.

## M

**Market Depth.** Total volume that can be traded before significantly moving price; inverse of [market impact coefficient](#market-impact-coefficient).

**Market Impact.** Price change from selling assets; coefficient $k$ relates volume to price depression.

**Market Impact Coefficient.** Constant $k$ in linear price impact model $\Delta p = k \cdot V$; relates sell volume to price depression. Used in cascade simulation.

**Memory Decay.** Weight $\lambda^n$ retained by historical price observations in EMA after $n$ refresh periods; after half-life $h$ periods, weight decays to 50%.

**Mempool.** Transaction waiting area before block inclusion; PoW prevents flooding attacks against mempool.

**Merton Jump-Diffusion.** Asset-price model with continuous Brownian motion plus a Poisson-driven jump component; basis for the Monte Carlo bad-debt simulation. See [Merton 1976](/reference/bibliography#merton1976).

**MEV.** Maximal Extractable Value — profit available from transaction ordering, insertion, or censorship.

**Modular Arithmetic.** Solidity's `unchecked` arithmetic where values wrap at $2^{256}$. The additive log-index is compatible with modular subtraction for computing $\Delta L$.

**Monotonicity.** The property that $L(t)$ is non-decreasing: each accrual adds a non-negative yield, so the index never decreases.

**Monte Carlo Simulation.** Randomized numerical method using many simulated paths to estimate statistical distributions; used for [bad-debt risk quantification](/research/papers/simulations) and TWAP analysis.

**Multiplicative Bounds.** Constraint limiting parameter changes to $0.5\times$–$2\times$ per [governance cycle](#governance-cycle); prevents rapid manipulation. See [parameter bounds](/features/lethargic-governance/parameter-bounds).

**Multiplicative Index ($I$).** The running product of exponential growth factors, stored at RAY ($10^{27}$) precision. Grows exponentially.

## N

**Nash Equilibrium.** Stable strategic state where no player can improve their payoff by unilaterally changing strategy; lock adoption exhibits utilization-dependent equilibria. Analyzed in the [theory paper](/research/papers/theory-and-proofs).

**Nonce.** Random value in PoW puzzle; combined with transaction data must hash below difficulty target.

## O

**Observation Window.** Time available for detecting suspicious activity during gradual capacity accumulation; enabled by [iteration caps](#iteration-cap).

**Optimal Utilization.** Target utilization $U^*$ (e.g., 90%) where interest rate curve has its kink; balances efficiency and liquidity. The on-chain `UTIL` parameter — see [position parameters](/parameters/position-parameters).

**Oracle Aggregation.** Combining prices from multiple feeds (TraderJoe, Chainlink) using log-space EMA smoothing with bidirectional geomean spread computation.

**Overflow Horizon.** The time until a stored value exceeds $2^{256}$. For the multiplicative RAY index: ${\sim}29$–$1{,}154$ years depending on rate. For the log-space WAD index: ${\sim}10^{58}$ years.

**Over-collateralization.** Requirement that collateral value exceed borrow value; enforced via health factor $H > 100\%$.

## P

**Partial Liquidation.** Liquidation of $2^{-e}$ fraction of positions rather than full liquidation. The exponent $e$ is the per-call `partial_exp` argument to `liquidate()` — see [pool parameters](/parameters/pool-parameters) and [how liquidations work](/features/debt-assumption-liquidation/how-liquidations-work).

**$p_{\text{crit}}$ †.** Critical oracle price ratio that triggers liquidation: $p_{\text{crit}} = 1 / H_0$. The oracle fires when $\hat{p}(n)/p_0 < p_{\text{crit}}$.

**Permanent Lock.** Irrevocable lock with `dt_term` $= 2^{256}{-}1$. Stored in the upper 120 bits of `cache` (`cache.perma`), not in a ring slot. Contributes $p \cdot L$ to token-seconds at query time. See [timed vs permanent](/features/locked-positions/timed-vs-permanent).

**Phantom-healthy †.** A position state where the oracle reports $H_{\text{oracle}} \geq 1$ (solvent) but the true health $H_{\text{true}} < 1$ (underwater). Arises from oracle staleness during crashes. See [oracle staleness](/risks/oracle-staleness).

**Pool.** Main lending/borrowing contract managing supply, borrow, settle, and redeem operations with health checks. See [architecture overview](/for-developers/architecture-overview) and [contract addresses](/for-developers/contract-addresses).

**Pool-to-Depth Ratio.** Pool size as fraction of [market depth](#market-depth); determines cascade severity under price shocks.

**Position Lock.** Fraction $\phi$ of a position restricted from redemption or sale; prevents [liquidation cascades](#liquidation-cascade). See [locked positions](/features/locked-positions/overview) and [locking positions](/using-the-protocol/locking-positions).

**Position Transfer.** Movement of supply or borrow position tokens between accounts. Supply uses standard ERC20 push; borrow uses [inverted](#inverted-transfer) pull semantics. See [transferring positions](/using-the-protocol/transferring-positions).

**PoW.** Proof-of-Work — computational puzzle required for certain operations to prevent spam. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

**PRBMath.** A Solidity library providing fixed-point `exp()`, `ln()`, `mul()`, and related functions at WAD ($10^{18}$) precision. The `exp()` function reverts when its input exceeds $133.08 \times 10^{18}$. See [PRBMath](/reference/bibliography#prbmath).

**Price Feed.** External data source providing asset prices; XPower Banq supports TraderJoe and Chainlink feeds.

**Price Shock.** Sudden price change used to test TWAP responsiveness; EMA smoothing dampens shock impact based on half-life configuration.

**Principal.** Base position amount before interest accrual; multiplied by index ratio to get current balance.

**Protocol Margin.** Revenue retained by protocol from the interest spread on the *borrowed* flow (the supply side is utilization-scaled); $M(\bar{\rho}) = 2s(1-\bar{\rho})$ where $s$ is spread and $\bar{\rho}$ is lock adoption rate.

**Protocol Parameters.** Governable constants (weights, decay, spread, rates, caps) that control protocol behavior; each transitions [lethargically](#lethargic-governance). See [parameter catalog](/governance/parameter-catalog) for a one-stop list and the per-contract pages under [Parameters](/parameters/pool-parameters).

**POL / Protocol-Owned Liquidity.** The accumulated spread surplus of a vault — the residual between what borrowers pay ($R(U) \times (1{+}s)$) and what suppliers earn ($U \times R(U) \times (1{-}s)$). Tracked position-level via `polAccrued()` and exposed per-vault via `pol()`. Governance can extract it under a lethargic share cap. The on-chain contract that wraps its extraction is named `Pols`. See [protocol-owned liquidity](/features/protocol-owned-liquidity/overview).

**polFetchableShare.** The vault parameter (`POL_FETCHABLE_SHARE_ID`) capping how much of the accumulated [POL](#pol--protocol-owned-liquidity) surplus governance may fetch: `maxFetchable = pol() × polFetchableShare − polFetched()`. Defaults to `0` (locked). See [protocol-owned liquidity](/features/protocol-owned-liquidity/overview) and [vault parameters](/parameters/vault-parameters).

## Q

**Quote / TWAP packed word.** Log-space price representation packed into a `uint256` word with four fields: `mid` ($\log_2(\text{price} \times 10^{18})$, biased by `LOG2_ONE`), `rel` ($\log_2(1 + s_{\text{geo}})$ where $s_{\text{geo}}$ is the bidirectional geomean spread), `utc` (timestamp), and `dec` (decimal-pair packed as `(dec_source << 8) | dec_target` for unit normalisation). The containing struct is `TWAP { uint256 last; uint256 mean; }` with two such words per pair: `last` for the most recent observation and `mean` for the EWMA running mean. Replaces linear bid/ask pairs with a compact log-space encoding suitable for EMA smoothing.

## R

**Rate Limit.** Token-bucket mechanism bounding operation frequency; configured per pool with capacity and regeneration rate. See `MAX_SUPPLY` / `MIN_SUPPLY` / `MAX_BORROW` / `MIN_BORROW` in [pool parameters](/parameters/pool-parameters).

**Ray.** Fixed-point representation with 27 decimal places ($10^{27}$). Defined in the `Constant` library.

**Read Path.** The code path executed when querying a user's balance via `totalOf`. In the log-space form, this is where `exp()` is called.

**Reentrancy Guard.** Protection preventing a contract from being called recursively during execution; uses transient storage.

**Reindex.** Interest compounding mechanism that updates the global log-space index and snapshots per-user indices. The functions `_reindex` and `_reindexWith` advance the global log-space index; lock bonus/malus is applied per-user via `_spreadDiff` consumed by the IR model when computing the position rate. Per-user balance growth is $\exp(I_{\text{global}} - I_{\text{user}})$.

**Reserves.** Token balances held in AMM liquidity pools; used to calculate bid/ask quotes via constant product formula.

**Ring-Lock.** Base mechanism: ring buffer + bitmap + cached total. 9 words per user. See [ring-buffer locks paper](/research/papers/ring-buffer-locks).

**Role Guard.** Contract restricting which addresses can execute role-gated functions; part of access control system. See [role hierarchy](/features/lethargic-governance/role-hierarchy).

## S

**Sandwich Attack.** MEV attack bracketing a victim transaction with front-run and back-run to extract value.

**Secondary Market Discount.** Price reduction $D$ (typically 3–10%) for locked position tokens relative to NAV; reflects inability to redeem for underlying assets. See [secondary market risk](/risks/secondary-market-risk) and [transfers and exits](/features/locked-positions/transfers-and-exits).

**Self-Healing.** `more()` correcting stale slot contributions during overwrite, maintaining `total` and `depth` consistency per-slot. Stated as a theorem in the [ring-buffer locks paper](/research/papers/ring-buffer-locks).

**$\sigma$, $\sigma_h$ †.** Annualized and hourly volatility of the collateral asset. $\sigma_h = \sigma / \sqrt{8760}$. ETH calibration: $\sigma = 90\%$, $\sigma_h \approx 0.96\%$/hour.

**Slippage.** Price deviation from executing a trade against AMM reserves; increases with trade size relative to reserves. See [spread and slippage](/features/twap-oracle/spread-and-slippage).

**Solvency Boundary.** Parameter constraint ensuring protocol can meet all obligations; default configuration satisfies $r_{\text{bonus}} + r_{\text{malus}} = 2s$, maintaining solvency for any lock adoption rate.

**Spread.** (1) Oracle: bidirectional geomean of relative spreads from both AMM query directions, stored as $\log_2(1 + s_{\text{geo}})$; wider spreads indicate lower liquidity or higher manipulation resistance. (2) IRM: symmetric half-spread parameter (e.g., 10%) applied to the gross rate; borrow rate = $R(U) \times (1{+}s)$, supply rate = $U \times R(U) \times (1{-}s)$, where $R(U) = R_k(U) + b$ and $U$ is utilization. The IRM half-spread is the on-chain `SPREAD` parameter — see [position parameters](/parameters/position-parameters).

**Spread Scaling.** Logarithmic widening of bid/ask spreads for large positions via $\mu = \log_2(x + 1) + 1$ where $x = \text{center} \cdot s$ is the notional spread (equivalently $\log_2(2x + 2)$); reflects market impact without governance parameters.

**Square.** Restricted-access liquidation function executing debt assumption: for a given exponent $e$, atomically transfers $\lfloor\text{borrow}/2^e\rfloor$ and $\lfloor\text{supply}/2^e\rfloor$ from victim to liquidator via bit-shift. Reverts if the victim is healthy (`wnav_supply >= wnav_borrow`, equivalently $H \geq 1$, treating the boundary as solvent) or the liquidator's post-transfer health is insufficient. The public entry point is `Pool.liquidate(victim, partial_exp)`, which (after role/PoW checks) calls `Pool.square(msg.sender, victim, partial_exp)`. The `square()` selector is gated by the pool's per-pool `POOL_SQUARE_ROLE`. See [debt assumption](#debt-assumption) and [partial liquidation](#partial-liquidation).

**Staleness.** Age of price data from an oracle; stale prices beyond threshold are rejected to prevent exploitation. See [oracle staleness](/risks/oracle-staleness).

**Supply Position.** ERC20 token representing deposited collateral; uses standard transfer semantics. See [positions as tokens](/concepts/positions-as-tokens).

**Supply Rate.** The interest rate earned by suppliers, computed as $U \times R(U) \times (1 - s)$ where $R(U) = R_k(U) + b$ (kinked rate plus [base risk premium](#base-risk-premium)), $U$ is utilization, and $s$ is the spread. The utilization factor means interest is only earned on the borrowed portion of the pool. Always less than or equal to $R(U)$, equal at $U = 100\%$.

**Sybil Attack.** Creating multiple accounts to gain unfair advantage; XPower Banq defends against rapid capacity monopolization via [holder-count scaling](#holder-count-scaling).

**Sybil Resistance.** Protection against Sybil attacks; in XPower Banq, bounds accumulation *rate* via holder-count scaling, not equilibrium share.

## T

**Time-lock.** Mandatory delay between proposing and executing governance parameter changes; prevents sudden malicious updates. See [proposing changes](/governance/proposing-changes).

**Time-Lock (Lock Extension).** Extension of [Ring-Lock](#ring-lock) adding the `depth` mapping for token-seconds. 10 words per user.

**Time-Weighted Mean.** Integration technique averaging parameter values over time; enables smooth transitions without discrete jumps. See [transition curves](/features/lethargic-governance/transition-curves).

**Token Bucket.** Rate limiting mechanism with capacity $C$, regeneration rate, and per-operation cost; operation allowed iff $C \geq 0$.

**Token-Seconds.** $\sum v_i \times \text{remaining time}$ — integral of locked amount over remaining time. The depth metric that drives graduated commitment.

**Truncation Bias.** The systematic negative error introduced by fixed-point truncation (rounding toward zero). In the multiplicative form, this bias compounds over $N$ accrual steps ($\leq 2N$ ULP). The log-space form has zero truncation during accrual.

**TVL †.** Total Value Locked — the aggregate collateral value in the lending pool. All bad-debt metrics in [bad-debt risk](/research/papers/simulations) are reported as a percentage of TVL.

**tx.origin.** Transaction originator address included in PoW hash; prevents front-runners from reusing others' solutions. See [PoW-gated public mode](/for-keepers/pow-gated-public-mode).

**TWAP.** Time-Weighted Average Price — price smoothed over time via log-space EMA (geometric mean temporal averaging) to resist manipulation. See [TWAP oracle overview](/features/twap-oracle/overview).

## U

**UD60x18.** PRBMath's unsigned 60.18-decimal fixed-point type. 60 integer digits and 18 fractional digits, fitting in `uint256`. Used for `exp()`, `mul()`, and `ln()` operations.

**uint256.** Solidity's 256-bit unsigned integer type, holding values from 0 to $2^{256} - 1 \approx 1.16 \times 10^{77}$. The storage type for both the multiplicative and log-space indices.

**ULP.** Unit in the Last Place — the smallest representable increment at a given precision. At WAD: 1 ULP $= 1$ wei $= 10^{-18}$.

**User Snapshot ($L_u$).** The value of $L$ at the user's last state transition, stored in `_userIndex[user]`.

**Utilization.** Ratio of borrowed assets to supplied assets in a vault; drives interest rates via a piecewise-linear model with a kink at [optimal utilization](#optimal-utilization). See [interest rates](/concepts/interest-rates).

## V

**$\text{VaR}(99\%)$ †.** Value-at-Risk at the 99th percentile — the bad debt level exceeded in only 1% of simulated paths.

**Vault.** ERC4626-compliant custody contract holding deposited assets; tracks utilization for the interest rate model. Distinct from a Position — Position tokens are plain `ERC20Permit`. See [ERC4626 vaults](/for-developers/erc4626-vaults).

## W

**$W$ †.** Phantom-healthy window — the number of oracle refreshes during which a position remains [phantom-healthy](#phantom-healthy) after a crash.

**WAD.** Fixed-point representation with 18 decimal places ($10^{18}$). Defined in the `Constant` library.

**Weight.** Multiplier applied to asset values in health calculations; determines effective LTV. Defaults: $w_s = 170$, $w_b = 255$. See `WEIGHT_SUPPLY` and `WEIGHT_BORROW` in [pool parameters](/parameters/pool-parameters).

**Write Path.** The code path executed during index accrual (`_reindex`). In the log-space form, this is a single addition; in the multiplicative form, it calls `exp()` and `mul()`.

## Where to go next

- [Bibliography](/reference/bibliography) — citations referenced throughout the glossary.
- [FAQ](/reference/faq) — short answers to common questions.
- [Comparison table](/reference/comparison-table) — XPower Banq vs other protocols.
- [Parameter catalog](/governance/parameter-catalog) — every governable parameter with ranges.
