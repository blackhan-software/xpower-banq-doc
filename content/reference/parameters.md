---
title: Protocol Parameters
description: All governable parameters for XPower Banq, organized by contract domain.
---

All protocol parameters are governed via the [lethargic transition mechanism](/whitepaper/04-mechanisms#lethargic-governance). They are organized into four contract domains: Pool, Position, Oracle, and Vault. Each parameter transitions asymptotically toward its target, bounded to $0.5\times$–$2\times$ per governance cycle.

## Pool Parameters

Time units: s = second, d = day, w = week, m = month, y = year.

| Parameter | Default | Range | Description |
|---|---|---|---|
| `MAX_SUPPLY` | 1w | [1s, 1y] | Max supply rate-limit |
| `MIN_SUPPLY` | 1d | [1s, 1y] | Min supply rate-limit |
| `POW_SUPPLY` | 0 | [0, 64] | Supply PoW difficulty |
| `MAX_BORROW` | 1w | [1s, 1y] | Max borrow rate-limit |
| `MIN_BORROW` | 1d | [1s, 1y] | Min borrow rate-limit |
| `POW_BORROW` | 0 | [0, 64] | Borrow PoW difficulty |
| `POW_SQUARE` | 0 | [0, 64] | Liquidation PoW difficulty |
| `WEIGHT_SUPPLY` | 170 | [0, 255] | Supply health weight† |
| `WEIGHT_BORROW` | 255 | [0, 255] | Borrow health weight |

<small>† Deployer-set; reference deployments use 170/255 ≈ 66.67% LTV.</small>

With the default weights, the effective LTV is $170/255 \approx 66.67\%$ and the implicit liquidation bonus is $\beta = w_b/w_s - 1 = 50\%$.

## Position Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `UTIL` | 90% | [0, 100%] | Optimal utilization |
| `RATE` | 10% | [0, 100%] | Rate at kink |
| `SPREAD` | 10% | [0, 50%] | Rate half-spread‡ |
| `LOCK_BONUS` | 10% | [0, `SPREAD`] | Locked supply APY bonus |
| `LOCK_MALUS` | 10% | [0, `SPREAD`] | Locked borrow APY reduction |
| `CAP` | — | [0, $2^{112}{-}1$] | Position cap (≈ $5.19 \times 10^{15}$ at 18 decimals) |
| `MIN_HOLDERS` | — | [0, $10^{18}$] | Min large holders |

<small>‡ Lower-bounded by `LOCK_BONUS` and `LOCK_MALUS`.</small>

## Oracle Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `DECAY` | 0.944 | [0.5, 1.0] | EMA decay factor |
| `LIMIT` | 1h | [1s, 1d] | Min refresh interval |
| `LEVEL` | 0 | [0, 64] | Refresh PoW difficulty |
| `DELAY` | 14d | [1w, 3m] | Feed enlist timelock |

## Vault Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `FEE_ENTRY` | 0.1% | [0, 50%] | Deposit fee |
| `FEE_EXIT` | 1.0% | [0, 50%] | Withdrawal fee |

## Change Rate Constraints

### Initial Lock Periods

Mandatory initial lock periods prevent manipulation at deployment. No parameter changes are permitted during the lock period.

| Category | Lock Period |
|---|---|
| Interest rate model | 3m |
| Oracle TWAP settings | 3m |
| Oracle feed delay | 1y |
| Vault fees | 3m |
| Pool weights | 3m |
| Pool rate limits | 1y |

### Maximum Parameter Change Over Time

Each single change is bounded to at most $2\times$. Overlapping transitions are disallowed, and changes are rate-limited to once per governance period (monthly).

| Cycles | Max Increase | Max Decrease |
|---:|---:|---:|
| 1 | $2\times$ | $0.5\times$ |
| 2 | $4\times$ | $0.25\times$ |
| 3 | $8\times$ | $0.125\times$ |
| 6 | $64\times$ | $0.016\times$ |
| 12 | $4096\times$ | $0.00024\times$ |

A $10\times$ change requires at least 4 months ($\lceil \log_2 10 \rceil = 4$ cycles).

## Role-Based Access Control

The protocol implements a three-tier role hierarchy per governable function:

| Role | Capability |
|---|---|
| **Executor** | Calls the restricted function |
| **Admin** | Grants and revokes the executor role |
| **Guard** | Veto-only revocation (cannot execute) |

Guard roles serve as a "break glass" mechanism, allowing emergency halts of malicious actions without granting execution power.

### Governance Attack Precautions

- Delayed feed changes require up to 3 months.
- Guard role separation prevents escalation.
- Gradual parameter migration eliminates arbitrage from sudden changes.
- Bounded cumulative change creates predictable worst-case scenarios.
- **Immutable constraints.** Minimum decimals ≥ 6, minimum 2 tokens, fixed token list, non-upgradeable contracts.
