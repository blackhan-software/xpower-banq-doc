---
title: "4. Core Mechanisms"
prev:
  text: "3. Protocol Architecture"
  link: /whitepaper/03-architecture
next:
  text: "5. Anti-Spam Protection"
  link: /whitepaper/05-anti-spam
---

## Locked Positions and Cascade Attenuation

::: definition
**Definition 2** (Position Lock). For each user $u$ and position type $p \in \{\text{supply}, \text{borrow}\}$, the protocol maintains $\text{balance}(u,p)$, $\text{lock}(u,p)$, and $\text{liquid}(u,p) = \text{balance} - \text{lock}$. Operations accept a term parameter `dt_term`; when nonzero, supplied assets cannot be redeemed and borrowed amounts cannot be settled until the slot epoch elapses. The sentinel `dt_term = type(uint256).max` produces a permanent (irrevocable) lock; any other term writes into one of 16 quarterly ring slots that expire automatically. Transfers proportionally move locked amounts:

$$\text{transfer}_{\text{lock}}(u_1, u_2, v) = \left\lfloor \frac{\text{lock}(u_1) \cdot v}{\text{balance}(u_1)} \right\rfloor$$
:::

**Lock Terms.** Locks are *time-bound by default*: callers pass a term `dt_term` that pins the principal to one of 16 quarterly ring slots (default slot length `MAX_LOCK_TERM` = 3 months, total horizon ≈ 48 months). Slots expire automatically and are reclaimed by `free()`. Passing `dt_term = type(uint256).max` upgrades the lock to *permanent* (irrevocable); only this path matches the cascade-attenuation analysis below. Cascade attenuation by factor $(1{-}\phi)$ therefore applies only to the *permanent-locked* fraction; timed locks contribute attenuation only until their slot epoch elapses. A user can otherwise exit only via transfer (which proportionally moves the lock) or liquidation. Crucially, only the *principal* is locked: accrued interest on locked supply positions can be redeemed at any time, and accrued interest on locked borrow positions can be settled at any time. Still, the design creates a fundamental tension: cascade protection depends on widespread adoption, yet rational adoption requires holding periods exceeding 5 years at typical utilization (see [Theory: Nash Equilibrium](/theory/03-nash-equilibrium)). The protocol addresses this tension by tying APY incentives to utilization levels.

**Lock Bonus/Malus.** To encourage adoption, locked suppliers earn additional interest $I_{\text{bonus}} = I \cdot \rho_u \cdot r_{\text{bonus}}$, while locked borrowers pay reduced interest $I_{\text{malus}} = I \cdot \rho_u \cdot r_{\text{malus}}$, where $\rho_u = \text{lock}/\text{balance}$ and $r_{\text{bonus}}, r_{\text{malus}} \in [0, s]$. The code enforces $r_{\text{bonus}} \leq s$ and $r_{\text{malus}} \leq s$ independently, where $s$ is the spread parameter. At full lock adoption ($\bar{\rho} = 1$), the combined constraint $r_{\text{bonus}} + r_{\text{malus}} \leq 2s$ holds at the boundary, with protocol margin approaching zero.

::: theorem
**Theorem 1** (Cascade Attenuation). *In a pool where fraction $\phi$ of supply positions are locked, the maximum cascade amplification factor is bounded by $(1{-}\phi)$. Locked positions attenuate sell pressure by preventing immediate redemption of seized collateral; they do not eliminate cascades among unlocked positions.*
:::

Because locked supply tokens cannot be redeemed, liquidation transfers position tokens without underlying assets leaving the vault. Only the unlocked fraction $(1{-}\phi)$ generates sell pressure. A full proof appears in [Theory: Formal Proofs](/theory/02-formal-proofs). Simulation confirms that at a 25% price shock, unlocked positions suffer 85.7% liquidation versus 29.4% when fully locked (see [Cascade Simulation](/simulations/02-cascade)).

<figure>
  <img src="/images/007-cascade.svg" alt="Cascade depth vs. price drop for varying lock fractions">
  <figcaption>Figure 2: Cascade depth versus price drop, swept across lock fractions φ ∈ {0, 25, 50, 75, 100} %.</figcaption>
</figure>

**Liquidation Precedence.** In practice, liquidators prefer unlocked positions for their immediate liquidity, creating *de facto* seniority for locked positions. This ordering is market-driven rather than protocol-enforced.

## Position Transfer Semantics

Supply positions follow standard ERC20 semantics: `transfer` pushes value to the receiver, and the health check is applied to the sender. Borrow positions, by contrast, implement *inverted* semantics that reflect the nature of debt: `transfer(from, amount)` **pulls** debt from the `from` address, `transferFrom` requires *dual* approval from both sender and receiver, and the health check falls on the receiver.

<figure>
  <img src="/images/002-supply-transfer.svg" alt="Supply position — standard ERC20 push semantics">
  <figcaption>Figure 3: Supply position — standard ERC20 push semantics.</figcaption>
</figure>

<figure>
  <img src="/images/003-borrow-transfer.svg" alt="Borrow position — inverted pull semantics with dual approval">
  <figcaption>Figure 4: Borrow position — inverted pull semantics with dual approval.</figcaption>
</figure>

::: definition
**Definition 3** (Debt Transfer). When debt is transferred from user $A$ to user $B$: (1) $A$'s borrow position decreases by $d$; (2) $B$'s borrow position increases by $d$; (3) $B$ must have sufficient collateral; (4) both must approve the intermediary (unless self-transfer).
:::

**Rationale.** Debt transfer differs fundamentally from asset transfer: with assets, the receiver benefits; with debt, the sender benefits by losing an obligation. The inverted semantics reflect this distinction — standard ERC20 pushes value to the receiver, whereas borrow positions pull debt from the source. The Pool contract as owner bypasses approvals (and health checks) to enable liquidations.

## Lethargic Governance

::: definition
**Definition 4** (Parameter Transition). A parameter $\theta$ transitions from $\theta_0$ to $\theta_1$ subject to $0.5 \cdot \theta_0 \leq \theta_1 \leq 2 \cdot \theta_0$. The effective value follows the time-weighted mean

$$\bar{\theta}(t) = \theta_1 - \frac{(\theta_1 - \theta_0)(t_s - t_0)}{t - t_0}$$

which asymptotically approaches $\theta_1$ as $t \to \infty$.
:::

<figure>
  <img src="/images/004-lethargic.svg" alt="Lethargic parameter transition (asymptotic)">
  <figcaption>Figure 5: Lethargic parameter transition — actual trajectory (blue) approaches the target (green) asymptotically from the source (red).</figcaption>
</figure>

**Safety Constraints.** Each single change is bounded to at most $2\times$, overlapping transitions are disallowed, and changes are rate-limited to once per governance period (monthly). Mandatory initial lock periods ranging from 3 months to 1 year (by category) prevent manipulation at deployment. Full parameter tables appear in [Reference: Parameters](/reference/parameters).

## Beta-Distributed Position Caps

<figure>
  <img src="/images/005-beta.svg" alt="Beta distribution cap function 12λ(1−λ)²">
  <figcaption>Figure 6: Beta distribution cap function 12λ(1−λ)², peaking at λ = 1/3.</figcaption>
</figure>

::: definition
**Definition 5** (Position Cap Function). For balance $B$, supply $S$, and $n$ large holders ($\geq 1$ token unit):

$$\text{cap}(B, S, n) = \frac{C_{\max} \cdot 12\lambda(1{-}\lambda)^2}{\sqrt{n + 2}}$$

where $\lambda = B/S$ and $C_{\max}$ is the maximum *relative* cap.
:::

The offset $+2$ prevents degeneracy at low holder counts. In addition, governance sets a holder floor $n_{\min}$ via the `MIN_HOLDERS` parameter; the effective count is $\max(n, n_{\min})$, which tightens per-user caps during the cold-start phase when few holders have joined. When $\lambda = 0$ (a new user with no existing balance), the beta factor is bypassed and the cap reduces to $C_{\max}/\sqrt{n{+}2}$, ensuring a non-zero entry allocation.

The Beta(2,3) shape is a design choice, not a uniquely optimal distribution — any unimodal density vanishing at 0 and 1 achieves similar goals. We chose Beta(2,3) for its mode at $\lambda = 1/3$ (favoring medium positions) and analytic tractability. A simpler $4\lambda(1{-}\lambda)$ (Beta(2,2)) or $\lambda(1{-}\lambda)$ would also penalize extremes; the asymmetry toward smaller positions is a preference, not a theoretical necessity.

**Rate-Limiting, Not Sybil Prevention.** The $\sqrt{n{+}2}$ divisor bounds the *accumulation rate*: $k$ accounts yield $O(\sqrt{k})$ total capacity gain per iteration. This does not, however, penalize long-term equilibrium share — simulation shows that a Sybil attacker retains 48.6% share (versus 50% initial) after 60 weeks, a marginal 1.4% penalty. The mechanism thus prevents rapid capacity monopolization while accepting that patient attackers with sufficient capital can reach similar long-term positions. Combined with a 7 iterations/week cap, capacity growth remains bounded regardless of account splitting. See [Cap Accumulation Simulations](/simulations/01-cap-accumulation) for detailed simulations.

## Health Factor and Liquidation

::: definition
**Definition 6** (Health Factor). For user $u$ with supply values $V_s^i$ and borrow values $V_b^i$ across $n$ tokens:

$$H(u) = \frac{\sum_i w_s^i \cdot V_s^i}{\sum_i w_b^i \cdot V_b^i}$$

where $w_s^i, w_b^i \in [0, 255]$ are uint8 weights. The implementation divides each weighted value by `WEIGHT_MAX = 255` and averages across tokens; both normalizations cancel in the ratio.
:::

With the default weights $w_s = 170$ and $w_b = 255$, the effective LTV is $170/255 \approx 66.67\%$. This is standard over-collateralization — the same mechanism underlying Compound's and Aave's LTV parameters, expressed through weight ratios rather than an explicit LTV setting. The resulting implicit liquidation bonus $\beta = w_b/w_s - 1 = 50\%$ incentivizes liquidators.

**Hybrid Liquidation.** The protocol supports both centralized keepers (the default, via `square()`) and governance-enabled public liquidators (PoW-gated, via `liquidate()`). Both paths use a *debt assumption* model in which the liquidator assumes fraction $2^{-e}$ of the victim's positions. For a given exponent $e$, both supply tokens $s = \text{supply}(V) \gg e$ and debt $d = \text{borrow}(V) \gg e$ transfer atomically. No liquid capital is required — only sufficient collateral headroom. The liquidator's health is verified post-liquidation.

## Oracle TWAP

The oracle aggregates prices via a log-space exponential moving average (EMA). Each refresh queries the AMM in both directions (source→target and target→source) and computes a bidirectional geomean spread, which eliminates directional bias in asymmetric pools:

$$\overline{m}_t = \alpha \cdot \overline{m}_{t-1} + (1{-}\alpha) \cdot \log_2(\bar{p}_{t-1})$$

$$\overline{r}_t = \alpha \cdot \overline{r}_{t-1} + (1{-}\alpha) \cdot r_{t-1}$$

where $r_t = \frac{1}{2}(\log_2(1+s^{AB}_t) + \log_2(1+s^{BA}_t))$. Smoothing in $\log_2$ space produces geometric mean temporal averaging (as in Uniswap V3 [\[uniswap2021\]](/reference/bibliography#uniswap2021)). The implementation defers the most recent tick by one period (`twap_.last → twap_.mean` on the next refresh) to provide two-tick flash-loan immunity; see `library/TWAP.sol::update`. With $\alpha = 0.944$ (12-period half-life) and hourly refreshes, approximately 40 hours of sustained manipulation achieves 90% price deviation.

**Spread Scaling.** Large positions incur wider spreads via $\mu = \log_2(2x + 2)$ where $x = n \cdot s$, reflecting market impact without requiring per-pair parameters. The base spread itself serves as sensitivity control: liquid pairs scale slowly, while illiquid pairs scale quickly.

**Bad-Debt Risk from Stale Pricing.** The slow convergence is double-edged. After a genuine $2\times$ price move, only 22.5% is absorbed after 14 hours. Combined with the 1-hour refresh limit, the protocol can be 2+ hours blind during a crash. If collateral drops 50%, the oracle reports near pre-crash prices for hours, potentially delaying liquidations and allowing bad debt to accumulate. The 50% over-collateralization buffer provides margin: at the default 66.67% LTV the protocol sits on the boundary where bad debt begins to emerge under tail-event price crashes ($>$50%); Monte Carlo simulation and analytical bounds quantify the resulting risk profile. The conservative governance floor of 33% LTV retains zero bounded bad debt for crashes up to 50%. See [TWAP Simulations](/simulations/03-twap-oracle) and [Bad-Debt Risk](/simulations/04-bad-debt-risk).

## Interest Rates

<figure>
  <img src="/images/006-interest.svg" alt="Piecewise-linear interest rate curve">
  <figcaption>Figure 7: Piecewise-linear interest rate curve with kink at optimal utilization U*.</figcaption>
</figure>

::: definition
**Definition 7** (Interest Rate Model). For utilization $U$, optimal utilization $U^*$, and optimal rate $R^*$:

$$R(U) = \min\!\left(R_{\text{kink}}(U),\ 2\right),$$

$$R_{\text{kink}}(U) = \begin{cases}
U R^* / U^* & \text{if } U \leq U^* \\[4pt]
\dfrac{U(1{-}R^*) - (U^* - R^*)}{1{-}U^*} & \text{otherwise}
\end{cases}$$

The implementation caps the base rate at 200% to bound interest in the post-kink regime.
:::

The protocol maintains a symmetric spread: $R_{\text{borrow}} = R_{\text{base}} \cdot (1{+}s)$, $R_{\text{supply}} = R_{\text{base}} \cdot (1{-}s)$, generating $2s$ margin on interest flows. See [Mathematical Foundations](/theory/01-mathematical-foundations) for interest accrual and time-weighted integration.
