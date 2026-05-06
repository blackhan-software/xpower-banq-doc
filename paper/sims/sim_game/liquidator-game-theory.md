# Liquidator Game Theory Spec

## XPower Banq — Competitive Liquidation Dynamics Analysis

---

## 1. Problem Statement

XPower Banq introduces debt assumption liquidation (no liquid capital required) gated by optional PoW anti-spam. The whitepaper describes the mechanism but provides no model of competitive liquidator behavior. Key open questions:

- How many liquidators will participate in equilibrium, and what determines their entry/exit?
- Does the PoW gate delay liquidations during cascading events when speed matters most?
- What collateral headroom do rational liquidators maintain?
- How does debt assumption change the MEV extraction landscape compared to repayment-based liquidation?
- Does the keeper/public liquidation duality create strategic asymmetries?

**Goal:** Build a game-theoretic model of liquidator competition under XPower Banq's mechanism, characterize equilibria, and identify parameter configurations that ensure timely liquidation under stress.

---

## 2. Scope

### In Scope

- Equilibrium number of active liquidators under both keeper mode (`square()`) and public mode (`liquidate()`)
- Optimal liquidator strategy (collateral headroom, position selection, exponent $e$ choice)
- PoW gate effects on liquidation latency and welfare
- MEV dynamics specific to debt assumption (sandwich attacks, front-running, backrunning)
- Interaction between liquidation dynamics and lock adoption
- Parameter recommendations for PoW difficulty and keeper selection

### Out of Scope

- Smart contract implementation of liquidation (covered in formal verification spec)
- Oracle manipulation attacks (separate analysis)
- Cross-protocol liquidation arbitrage
- Liquidation bot implementation details

---

## 3. Model Framework

### 3.1 Players

**Liquidators** $L = \{l_1, \ldots, l_m\}$, each characterized by:

- **Collateral endowment** $C_i$: assets already deposited in the protocol
- **Hash rate** $H_i$: computational power for PoW puzzles (relevant only in public mode)
- **Gas budget** $G_i$: willingness to pay for transaction inclusion
- **Monitoring capability** $M_i$: speed of detecting liquidatable positions (latency from mempool observation to action)

**Borrowers** $B = \{b_1, \ldots, b_n\}$: passive; their positions become liquidatable when $H_{\text{oracle}}(b_j) < 1$.

**Validators**: block proposers who can observe and reorder pending transactions.

### 3.2 Liquidation Mechanics

A liquidator $l_i$ executing `square(victim, exponent)` or `liquidate(victim, exponent, nonce)`:

1. Receives supply tokens $s = \text{supply}(V) \gg e$ from the victim
2. Assumes debt tokens $d = \text{borrow}(V) \gg e$ from the victim
3. Post-liquidation health check: $H(l_i) \geq 1$ must hold
4. **No liquid capital exchanged** — only position tokens move

The liquidator's profit $\pi_i$ from liquidating victim $v$:

$$\pi_i(v, e) = \underbrace{V_s(v) \cdot 2^{-e}}_{\text{supply received}} - \underbrace{V_b(v) \cdot 2^{-e}}_{\text{debt assumed}} = 2^{-e} \cdot V_s(v) \cdot \left(1 - \frac{1}{H(v)}\right)$$

Since $H(v) < 1$ at liquidation, this quantity is *negative* in value terms. The liquidator "profits" from the implicit liquidation bonus $\beta = w_b / w_s - 1 \approx 200\%$: the received supply is worth more than the assumed debt at oracle prices, *provided the oracle price reflects true value*.

**Corrected profit (accounting for health weight asymmetry):**

$$\pi_i(v, e) = 2^{-e} \cdot \left(\frac{w_s}{w_b} \cdot V_b(v) - V_b(v)\right) \cdot \frac{1}{H(v)}$$

This simplifies to: the liquidator captures the spread between the weight-adjusted collateral value and the debt value.

### 3.3 Two Regimes

| Regime | Function | Access | Cost | Latency |
|---|---|---|---|---|
| **Keeper** (default) | `square()` | Authorized addresses only | Gas only | Low (direct submission) |
| **Public** (governance-enabled) | `liquidate()` | Anyone with valid PoW | Gas + PoW computation | Higher (PoW solve time) |

---

## 4. Keeper Mode Analysis

### 4.1 Keeper Selection Game

In keeper mode, governance authorizes a set of keeper addresses. This creates a permissioned oligopoly.

**Model as:** Cournot-style competition among $m$ authorized keepers, where each chooses monitoring investment $M_i$ and gas bidding strategy $G_i$.

**Key questions to answer:**

1. **Optimal keeper count $m^*$:** What number of keepers balances liquidation reliability against rent extraction?
2. **Keeper collateral requirements:** What minimum $C_i$ ensures keepers can always absorb liquidations? This is unique to debt assumption — repayment liquidators need liquid capital, but assumption liquidators need collateral headroom.
3. **Keeper failure modes:**
   - All keepers simultaneously at $H \approx 1$ during a crash (systemic headroom depletion)
   - Keeper collusion to delay liquidation and extract MEV
   - Single keeper with $H < 1$ who cannot liquidate despite being authorized

### 4.2 Collateral Headroom Model

A rational keeper maintains headroom $\Delta_i$ such that:

$$H(l_i) - \frac{2^{-e} \cdot V_b(v)}{V_s(l_i)} \geq 1$$

The maximum victim size a keeper can absorb:

$$V_b^{\max}(v) = 2^e \cdot V_s(l_i) \cdot (H(l_i) - 1)$$

**Deliverable:** For the default parameters ($w_s = 85$, $w_b = 255$), compute the minimum keeper portfolio size needed to absorb the largest plausible liquidation as a function of pool TVL.

### 4.3 Cascading Liquidation Capacity

During a crash, multiple positions become liquidatable simultaneously. Each liquidation the keeper executes *reduces their headroom* for the next:

$$\Delta_i^{(k+1)} = \Delta_i^{(k)} - \frac{V_b^{(k)} \cdot 2^{-e}}{V_s(l_i) + \sum_{j \leq k} s^{(j)}}$$

**Deliverable:** Model the maximum cascade depth a single keeper (and a set of $m$ keepers) can process before running out of headroom. Express as a function of initial keeper portfolio diversification and crash severity.

---

## 5. Public Mode Analysis

### 5.1 PoW Competition Game

In public mode, liquidation requires solving a hash puzzle: `zeros(keccak256(blockHash || tx.origin || msg.data)) >= d`.

**Model as:** An all-pay auction where each liquidator $l_i$ invests hash computation $h_i$ to find a valid nonce. The winner is the first to solve and get their transaction included.

**Expected solve time** for liquidator $l_i$ with hash rate $H_i$:

$$\mathbb{E}[T_i] = \frac{16^d}{H_i}$$

**Key analysis:**

1. **Latency vs. security trade-off:** Higher $d$ increases spam resistance but delays liquidation. Derive the optimal $d$ that minimizes expected bad debt (accounting for liquidation delay) subject to a minimum spam resistance threshold.

2. **Validator advantage quantification:** On Avalanche (PoS), a validator who knows they will propose the next block can:
   - Begin PoW computation $t_{\text{block}}$ seconds early (block time ≈ 2s on Avalanche)
   - Exclude competing liquidation transactions
   - Compute using `blockHash` they control

   Model the effective hash rate advantage:

   $$\frac{H_{\text{validator}}^{\text{effective}}}{H_{\text{honest}}} = \frac{H_{\text{validator}} \cdot t_{\text{block}} + 1}{H_{\text{honest}} \cdot t_{\text{solve}}} \cdot \frac{1}{1 - p_{\text{censor}}}$$

   where $p_{\text{censor}}$ is the probability of successful transaction censorship.

3. **Hash rate arms race:** Does PoW competition converge to an equilibrium where total hash expenditure equals expected liquidation profit? Model as a Tullock contest:

   $$p_i = \frac{H_i}{\sum_j H_j}, \quad \mathbb{E}[\pi_i] = p_i \cdot \pi - c(H_i)$$

   where $\pi$ is the liquidation profit and $c(H_i)$ is the cost of maintaining hash rate $H_i$.

### 5.2 PoW-Induced Liquidation Delay

**Critical concern:** During a cascade, PoW adds latency to each liquidation step. If $n$ positions become liquidatable simultaneously:

- **Sequential liquidation:** Total delay $\approx n \cdot \mathbb{E}[T_{\min}]$ where $T_{\min}$ is the minimum solve time across all liquidators
- **Parallel liquidation:** Different liquidators target different victims, but each still needs a PoW solution
- **Token bucket interaction:** Rate limiter capacity $C$ with regeneration 1/second constrains burst throughput

**Deliverable:** Simulate cascade resolution time under public mode for varying $d$, number of liquidators $m$, and cascade size $n$. Compare against keeper mode (gas-only competition, no PoW delay). Identify the cascade size threshold where PoW delay causes meaningful bad debt increase.

---

## 6. MEV and Strategic Behavior

### 6.1 Debt Assumption MEV Landscape

Debt assumption changes the MEV calculus fundamentally:

| Attack Vector | Repayment Liquidation | Debt Assumption |
|---|---|---|
| **Capital requirement** | High (must repay debt) | None (only headroom) |
| **Front-running profit** | Liquidation bonus - gas - capital cost | Liquidation bonus - gas - PoW cost |
| **Sandwich attack** | Manipulate price → liquidate → reverse | Manipulate price → liquidate → cannot immediately profit from assumed position |
| **Back-running** | Buy discounted collateral after liquidation sale | No collateral sale occurs — back-running target is the secondary market for assumed positions |
| **JIT liquidity** | Provide liquidity to capture liquidation flow | Provide headroom to capture liquidation opportunity |

**Key insight:** Because no assets leave the vault during debt assumption liquidation, the traditional liquidation sandwich (manipulate → liquidate → sell seized collateral) is *structurally broken*. The liquidator receives *position tokens*, not underlying assets. This has implications:

1. **Reduced acute MEV:** No immediate sell pressure = no immediate arbitrage opportunity
2. **Deferred MEV:** Profit realization requires either (a) redeeming unlocked positions or (b) secondary market sale of locked positions
3. **Position token MEV:** A new vector emerges — manipulating the *secondary market* for position tokens

### 6.2 Oracle Sandwich Attack Under PoW

The whitepaper notes PoW raises the cost of sandwich attacks but doesn't eliminate them. Model:

1. Attacker observes pending `refresh()` call that will update oracle price
2. Attacker front-runs with transactions that benefit from the stale price
3. Oracle updates
4. Attacker back-runs to realize profit

With PoW: the attacker must solve a PoW puzzle *and* get their transaction ordered before/after the refresh. The `tx.origin` binding prevents solution reuse.

**Deliverable:** Quantify the minimum $d$ that makes oracle sandwich attacks unprofitable as a function of expected profit from the stale-to-fresh price transition.

### 6.3 Exponent Selection Strategy

The liquidation exponent $e$ determines the fraction $2^{-e}$ of positions transferred. Rational liquidators choose $e$ to maximize profit subject to health constraints:

$$e^* = \arg\max_e \left[ 2^{-e} \cdot \pi_{\text{unit}} \right] \quad \text{s.t.} \quad H(l_i) \geq 1 \text{ post-liquidation}$$

Since $\pi_{\text{unit}}$ is constant per unit, the liquidator wants the smallest $e$ (largest fraction) their headroom allows. But:

- **Competition:** Other liquidators may target the same victim; over-bidding on $e$ wastes headroom
- **Cascade dynamics:** Taking a larger fraction reduces the remaining underwater position, potentially preventing further cascade steps
- **Gas efficiency:** Each liquidation has fixed gas overhead; larger fractions are more gas-efficient

**Deliverable:** Derive the Nash equilibrium exponent choice under competition. Is there a race-to-the-bottom where liquidators choose $e = 0$ (full liquidation)?

---

## 7. Equilibrium Analysis

### 7.1 Free Entry Equilibrium (Public Mode)

With free entry, liquidators enter until expected profit equals expected cost:

$$\mathbb{E}[\pi | m \text{ liquidators}] = c_{\text{entry}} + c_{\text{monitoring}} + c_{\text{PoW}} + c_{\text{headroom}}$$

where $c_{\text{headroom}}$ is the opportunity cost of maintaining collateral in the protocol for headroom (unique to debt assumption).

**Derive:**

1. Equilibrium number of liquidators $m^*$ as a function of protocol TVL, crash frequency, and PoW difficulty
2. Expected time-to-liquidation $\mathbb{E}[T_{\text{liq}}]$ at equilibrium
3. Liquidation reliability $P(\text{liq within } k \text{ blocks})$ at equilibrium

### 7.2 Keeper Oligopoly Equilibrium

With $m$ authorized keepers:

1. **Tacit collusion risk:** Can keepers implicitly coordinate to delay liquidation (increasing profit per event at the cost of bad debt)?
2. **Defection incentive:** Is the one-shot gain from liquidating immediately (while others delay) sufficient to prevent collusion?
3. **Governance accountability:** Can governance detect and replace underperforming keepers?

**Model as repeated game with observation.** Derive conditions under which the unique equilibrium is immediate liquidation (no collusive delay).

### 7.3 Regime Comparison

**Central question:** Under what conditions should governance enable public liquidation (`liquidate()`) over keeper-only (`square()`)?

| Dimension | Keeper Mode | Public Mode |
|---|---|---|
| Latency | Lower (no PoW) | Higher (PoW delay) |
| Censorship resistance | Low (few authorized) | High (permissionless) |
| MEV extraction | Concentrated | Distributed |
| Capital efficiency | Keepers hold headroom | Anyone can participate |
| Cascade throughput | Limited by $m$ keepers' headroom | Limited by PoW throughput |

**Deliverable:** Decision framework parameterized by TVL, expected crash severity, and validator set concentration that recommends the optimal regime.

---

## 8. Simulation Design

### 8.1 Agent-Based Model

Simulate a population of heterogeneous liquidators competing over liquidation opportunities.

**Agent types:**

| Type | Hash Rate | Monitoring | Capital | Strategy |
|---|---|---|---|---|
| Professional keeper | High | Low latency | Large | Maximize throughput |
| MEV searcher | Medium | Very low latency | Medium | Extract maximum per-event profit |
| Validator | Medium + censorship | Block-level | Variable | Exploit proposer advantage |
| Retail liquidator | Low | High latency | Small | Opportunistic participation |

**Simulation loop:**

1. Generate positions with stochastic health factor evolution
2. Apply price shocks (drawn from calibrated jump-diffusion)
3. Positions cross $H < 1$ threshold
4. Liquidators observe and compete (PoW race, gas auction, or keeper priority)
5. Liquidations execute; headroom and health factors update
6. Repeat until cascade resolves or bad debt accumulates

### 8.2 Parameter Sweeps

- PoW difficulty $d \in \{0, 1, 2, 3, 4\}$
- Number of keepers $m \in \{1, 3, 5, 10, 20\}$
- Crash severity $\delta \in \{10\%, 20\%, 30\%, 40\%, 50\%\}$
- Lock fraction $\phi \in \{0\%, 25\%, 50\%, 75\%\}$
- Protocol TVL ∈ {\$1M, \$10M, \$100M, \$1B}
- Token bucket capacity $C \in \{1, 5, 10, 20\}$

### 8.3 Metrics

| Metric | Definition | Target |
|---|---|---|
| Time-to-first-liquidation | Blocks from $H < 1$ to first successful `square()` or `liquidate()` | < 3 blocks (95th percentile) |
| Cascade resolution time | Time from first liquidation to no remaining underwater positions | < 1 hour for 30% crash |
| Bad debt from delay | Additional bad debt attributable to liquidation delay vs. instantaneous | < 0.5% of TVL |
| Liquidator profit Gini | Concentration of liquidation profit across liquidators | < 0.7 (moderate concentration) |
| Liquidation throughput | Liquidations per block during cascade | Sufficient to clear cascade before bad debt threshold |
| Headroom utilization | Fraction of keeper headroom consumed during cascade | < 80% (ensures buffer) |

---

## 9. Deliverables

| # | Deliverable | Description |
|---|---|---|
| 1 | Formal game-theoretic model | Player definitions, strategy spaces, payoff functions, equilibrium characterization |
| 2 | Equilibrium analysis | Number of liquidators, expected latency, profit distribution for keeper and public modes |
| 3 | PoW difficulty recommendation | Optimal $d$ balancing spam resistance and liquidation latency |
| 4 | MEV analysis | Quantified MEV vectors specific to debt assumption, comparison with repayment models |
| 5 | Agent-based simulation code | Reproducible Python/Rust simulation with parameterized sweeps |
| 6 | Simulation results | Tables and charts for all parameter sweep combinations |
| 7 | Keeper sizing guide | Minimum keeper portfolio requirements as function of TVL and crash scenarios |
| 8 | Regime selection framework | Decision criteria for keeper vs. public mode |
| 9 | Parameter recommendations | Concrete values for PoW difficulty, keeper count, token bucket capacity |

---

## 10. Acceptance Criteria

1. Equilibrium existence proven for both keeper and public mode under stated assumptions
2. Simulation demonstrates that recommended parameters achieve < 3 block liquidation latency at 95th percentile for crashes ≤ 30%
3. Bad debt from liquidation delay quantified with confidence intervals
4. MEV analysis identifies all vectors unique to debt assumption and proposes mitigations for each
5. Keeper sizing guide is validated: simulated keepers following the guide never run out of headroom for crashes ≤ 40%
6. PoW difficulty recommendation is supported by both analytical bounds and simulation
7. Results are consistent with the cascade simulation in Appendix I (same parameter regime reproduces comparable liquidation rates)