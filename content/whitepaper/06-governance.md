---
title: Governance and Parameters
prev: '/whitepaper/05-anti-spam'
next: '/whitepaper/07-security'
---

# Governance and Parameters

All protocol parameters are governed via the lethargic transition mechanism ([Definition 4](/whitepaper/04-mechanisms#lethargic-governance)). They are organized into four contract domains: Pool (rate limits, PoW difficulty, health weights), Position (interest rate model, caps), Oracle (TWAP behavior, feed management), and Vault (entry/exit fees). Full parameter tables and role categories appear [below](#protocol-parameters).

::: theorem
**Theorem 2** (Governance Rate Bound). *Under multiplicative bound $\mu = 2$ and minimum cycle $\Delta t_{\min}$, the parameter at time $t$ satisfies:*

$$\mu^{-n} \theta_0 \leq \theta(t) \leq \mu^n \theta_0$$

*where $n = \lfloor(t{-}t_0)/\Delta t_{\min}\rfloor$. A $10\times$ change requires $\lceil\log_2 10\rceil = 4$ months.*
:::

The protocol implements a three-tier role hierarchy per governable function: an executor (who calls the function), an admin (who grants and revokes the executor role), and a guard (who provides veto-only revocation). Guard roles serve as a "break glass" mechanism, allowing emergency halts of malicious actions without granting execution power. The governance rate bound proof is provided in [Appendix B](/appendices/part-i-math/security-proofs).

## Protocol Parameters

### Pool Parameters

| Parameter | Setting | Range | Description |
|---|---|---|---|
| `MAX_SUPPLY` | 1w | [1s, 1y] | Max supply rate-limit |
| `MIN_SUPPLY` | 1d | [1s, 1y] | Min supply rate-limit |
| `POW_SUPPLY` | 0 | [0, 64] | Supply PoW difficulty |
| `MAX_BORROW` | 1w | [1s, 1y] | Max borrow rate-limit |
| `MIN_BORROW` | 1d | [1s, 1y] | Min borrow rate-limit |
| `POW_BORROW` | 0 | [0, 64] | Borrow PoW difficulty |
| `POW_SQUARE` | 0 | [0, 64] | Liquid. PoW difficulty |
| `WEIGHT_SUPPLY` | 85 | [0, 255] | Supply health weight |
| `WEIGHT_BORROW` | 255 | [0, 255] | Borrow health weight |

Time units: s=second, d=day, w=week, m=month, y=year.

### Position Parameters

| Parameter | Setting | Range | Description |
|---|---|---|---|
| `UTIL` | 90% | [0, 100%] | Optimal utilization |
| `RATE` | 10% | [0, 100%] | Rate at kink |
| `SPREAD` | 10% | [0, 50%] | Rate half-spread |
| `LOCK_BONUS` | 10% | [0, `SPREAD`] | Locked supply APY bonus |
| `LOCK_MALUS` | 10% | [0, `SPREAD`] | Locked borrow APY reduction |
| `CAP` | — | [0, $2^{224}$] | Position cap |
| `MIN_HOLDERS` | — | [0, $10^{18}$] | Min large holders |

### Oracle Parameters

| Parameter | Setting | Range | Description |
|---|---|---|---|
| `DECAY` | 0.944 | [0.5, 1.0] | EMA decay |
| `LIMIT` | 1h | [1s, 1d] | Min refresh interval |
| `LEVEL` | 0 | [0, 64] | Refresh PoW difficulty |
| `DELAY` | 14d | [1w, 3m] | Feed enlist timelock |

### Vault Parameters

| Parameter | Setting | Range | Description |
|---|---|---|---|
| `FEE_ENTRY` | 0.1% | [0, 50%] | Deposit fee |
| `FEE_EXIT` | 1.0% | [0, 50%] | Withdrawal fee |

### Change Rate Constraints

**Initial lock periods:**

| Category | Lock Period |
|---|---|
| Interest rate model | 3m |
| Oracle TWAP settings | 3m |
| Oracle feed delay | 1y |
| Vault fees | 3m |
| Pool weights | 3m |
| Pool rate limits | 1y |

**Maximum parameter change over time:**

| Cycles | Max Increase | Max Decrease |
|---|---|---|
| 1 | $2\times$ | $0.5\times$ |
| 2 | $4\times$ | $0.25\times$ |
| 3 | $8\times$ | $0.125\times$ |
| 6 | $64\times$ | $0.016\times$ |
| 12 | $4096\times$ | $0.00024\times$ |

### Role-Based Access Control

The protocol implements a three-tier role hierarchy per governable function: executor (calls the restricted function), admin (grants/revokes the executor role), and guard (veto-only revocation).

**Governance Attack Precautions.** Delayed feed changes require up to 3 months. Guard role separation prevents escalation. Gradual parameter migration eliminates arbitrage from sudden changes. Bounded cumulative change creates predictable worst-case scenarios. Immutable constraints include minimum decimals $\geq 6$, minimum 2 tokens, a fixed token list, and non-upgradeable contracts.

## Protocol Constants

### Time Unit Constants (seconds)

| Constant | Value | Definition |
|---|---|---|
| `CENTURY` | 3,155,760,000 | $365.25 \times 100 \times 86400$ |
| `YEAR` | 31,557,600 | $365.25 \times 86400$ |
| `MONTH` | 2,629,800 | YEAR / 12 |
| `WEEK` | 604,800 | $7 \times 86400$ |
| `DAY` | 86,400 | $24 \times 3600$ |
| `HOUR` | 3,600 | $60 \times 60$ |
| `MINUTE` | 60 | 60 seconds |
| `SECOND` | 1 | 1 second |

### Fixed-Point Representation Constants

| Constant | Value | Meaning |
|---|---|---|
| `RAY` | $10^{27}$ | Ray precision (27 decimals) |
| `ONE` | $10^{18}$ | WAD unit (1.0) |
| `TWO` | $2 \times 10^{18}$ | WAD unit (2.0) |
| `HLF` | $0.5 \times 10^{18}$ | WAD unit (0.5) |
| `NIL` | 0 | WAD unit (0.0) |
| `PCT` | $10^{16}$ | 1 percentage point |
| `BPS` | $10^{14}$ | 1 basis point |

### Protocol Constraints and Limits

| Constant | Value | Purpose |
|---|---|---|
| `MAX_DIFFICULTY` | 64 | Max PoW difficulty |
| `MIN_HOLDERS` | $10^{18}$ | Min holders upper bound |
| `VERSION` | 0x1a5 | Protocol version |

## EMA Decay Factors

Pre-computed EMA decay factors relating half-life (in refresh periods) to the decay coefficient $\alpha$, used for log-space TWAP oracle smoothing:

| Half-life | Decay $\alpha$ | Use Case |
|---|---|---|
| 1 | 0.500000 | Fast response |
| 2 | 0.707107 | Short-term |
| 12 | 0.943874 | Medium-term |
| 24 | 0.971532 | Long-term |
