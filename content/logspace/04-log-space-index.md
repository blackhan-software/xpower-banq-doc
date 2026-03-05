---
title: "4. Log-Space Index"
prev:
  text: "3. Overflow Analysis"
  link: /logspace/03-overflow-analysis
next:
  text: "5. Code Transformation"
  link: /logspace/05-code-transformation
---

## Core Insight

The multiplicative index is a running product of exponentials:

$$I(t) = I_0 \cdot \exp(r_1) \cdot \exp(r_2) \cdots \exp(r_N) = I_0 \cdot \exp\!\Bigl(\sum_{i=1}^N r_i\Bigr).$$

Taking the natural logarithm of both sides,

$$\ln I(t) = \ln I_0 + \sum_{i=1}^N r_i.$$

The sum $\sum r_i$ is exactly the quantity computed in the accrual path and passed to `exp()` inside `Rate.accrue`. By storing this cumulative sum directly, accrual becomes addition, and the exponential growth that threatens overflow is never materialised in storage.

## Formal Definition

::: definition
**Definition 4.1** (Log-Space Index). The global log-space index at time $t$ is

$$L(t) = \sum_{i=1}^{N(t)} r_i \cdot \Delta t_i / \text{YEAR}$$

stored at WAD precision ($10^{18}$), initialised to $L(0) = 0$.
:::

::: definition
**Definition 4.2** (User Snapshot). For each user $u$, $L_u$ denotes the value of $L(t)$ at $u$'s last state transition (mint, burn, or transfer).
:::

::: definition
**Definition 4.3** (Growth Factor). The growth factor between user snapshot and current time is

$$G(L_u, t) = \exp\bigl(L(t) - L_u\bigr).$$
:::

This is mathematically identical to the multiplicative ratio:

$$\frac{I(t)}{I(t_u)} = \frac{I_0 \cdot \exp(L(t))}{I_0 \cdot \exp(L_u)} = \exp\bigl(L(t) - L_u\bigr).$$

The RAY scale factor $I_0$ cancels — it exists only as a precision anchor for the multiplicative representation and has no analogue in log-space.

## Storage Transformation

```solidity
// Multiplicative RAY index (before)
uint256 internal _index_ray = Constant.RAY;
mapping(address => uint256) internal _userIndex;

// Log-space WAD index (after)
uint256 internal _index_wad;       // starts at 0
mapping(address => uint256) internal _userIndex;
```

Starting at zero is natural: $\ln(1) = 0$, and a fresh index with no accrual represents a $1\times$ growth factor.

## Shipped Storage Layout

The conceptual `uint256 _index_wad` and `mapping(address => uint256) _userIndex` are not allocated as separate storage in production. The shipped `Position.sol` packs the global index into the existing `_state` word and the per-user index into the `_stateOf[user]` word, alongside fields that would otherwise occupy independent slots:

```solidity
// Global state (1 word):
// _state:[u80 index_log|u64 stamp|u112 large_holders]
uint256 private _state;

// Per-user state (1 word per user):
// _stateOf[user]:[u80 index_log|u64 depth_wad|u112 money]
mapping(address user => uint256) internal _stateOf;

// Shared bit positions (LHS_FROM = 176, MID_FROM = 112)
uint256 private constant LHS_MASK = type(uint80).max;
uint256 private constant MID_MASK = type(uint64).max;
uint256 private constant RHS_MASK = type(uint112).max;
```

Field budgets:

- **`index_log`.** 80 bits, WAD scale → $\sim 1.7 \times 10^6$ years at 100% APR (per-user) and $\sim 5 \times 10^5$ years at 1000% APR (global) before saturation.
- **`stamp`.** 64 bits, seconds → $5.8 \times 10^{11}$ years (42× the age of the universe).
- **`depth_wad`.** 64 bits, dimensionless WAD ratio (`lock.depthOf(user)` / `balanceOf(user)`) → 18× the $[0, 10^{18}]$ WAD range.
- **`money`.** 112 bits, token units → $5 \times 10^{15}$ tokens at 18 decimals.

This packing is the source of much of the gas saving documented in [Section 6](/logspace/06-gas-analysis): every `_indexOf` write that would have been a separate `SSTORE` becomes part of the same word as `stamp` and `large_holders`, and every per-user accrual snapshot writes `index_log` alongside `depth_wad` and `money` in a single `SSTORE`. All mathematical content of the formal definitions and snapshot invariants applies unchanged; only the storage names differ.

## Overflow Elimination

::: theorem
**Theorem 4.4** (Log-Index Overflow Freedom). *Treated as a full `uint256`, the log-space index $L(t)$ cannot overflow within $2.9 \times 10^{58}$ years at 400%/year. In the shipped storage, where `index_log` occupies the upper 80 bits of `_state`, the index saturates after $\sim 5 \times 10^5$ years at 1000%/year (global) and $\sim 1.7 \times 10^6$ years at 100%/year (per-user) — both unreachable in practice and dwarfing the $\sim 29$ year horizon of the multiplicative RAY index.*
:::

::: proof
**Proof.** $L(t)$ grows linearly at rate $r_{\text{annual}}$ (WAD). At $r = 4 \times 10^{18}$:

$$\text{rate}_{\text{sec}} = 4 \times 10^{18} / 31{,}557{,}600 \approx 1.27 \times 10^{11},$$

$$t_{\text{wrap}} = 2^{256} / (1.27 \times 10^{11}) \approx 9.1 \times 10^{65}\ \text{s} \approx 2.9 \times 10^{58}\ \text{years}.$$

At 10%/year: $\sim 1.16 \times 10^{60}$ years. The age of the universe is $\sim 1.4 \times 10^{10}$ years. The problem is eliminated, not deferred. $\blacksquare$
:::

## Invariants

**Monotonicity.** $L(t)$ is non-decreasing. Each accrual adds a non-negative $r \cdot \Delta t / \text{YEAR} \geq 0$.

**Conservation.** For all users $u$ at any time $t$:

$$\texttt{totalOf}(u) = p_u \cdot \exp\bigl(L(t) - L_u\bigr)$$

where $p_u$ is the stored principal, exact up to WAD rounding.

**Snapshot Consistency.** $L_u$ is set to $L(t)$ during `_snapUser`. The difference $L(t) - L_u$ accumulates only yields since $u$'s last state transition.

**Zero-Start Correctness.** $L(0) = 0$. A user snapshotted at $L_u = 0$ with $L(t) = 0$ gets $\exp(0) = 10^{18}$, producing $p_u \times 10^{18} / 10^{18} = p_u$. Correct.

> **Wrap behaviour.** In the shipped contract, the global `index_log` field occupies the upper 80 bits of `_state` and is masked, not modular-added, on every write. The read-time delta `index_log - user_index` is *checked* and guarded by `index_log > user_index`; after a hypothetical wrap, the guard fails and the function returns the user's principal without accrued interest, rather than recovering $\Delta L$ via modular subtraction. The 80-bit budget makes wrap unreachable, so this is a documentation point, not a soundness issue.
