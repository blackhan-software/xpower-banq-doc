---
title: Protocol Parameters
description: All governable parameters for XPower Banq, organized by contract domain.
---

# Protocol Parameters

All protocol parameters are governed via the lethargic transition mechanism. They are organized into four contract domains: Pool, Position, Oracle, and Vault. Each parameter transitions asymptotically toward its target, bounded to 0.5x–2x per governance cycle.

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
| `WEIGHT_SUPPLY` | 85 | [0, 255] | Supply health weight |
| `WEIGHT_BORROW` | 255 | [0, 255] | Borrow health weight |

With the default weights, the effective LTV is 85/255 = 33%.

## Position Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `UTIL` | 90% | [0, 100%] | Optimal utilization |
| `RATE` | 10% | [0, 100%] | Rate at kink |
| `SPREAD` | 10% | [0, 50%] | Rate half-spread |
| `LOCK_BONUS` | 10% | [0, `SPREAD`] | Locked supply APY bonus |
| `LOCK_MALUS` | 10% | [0, `SPREAD`] | Locked borrow APY reduction |
| `CAP` | — | [0, 2^224] | Position cap |
| `MIN_HOLDERS` | — | [0, 10^18] | Min large holders |

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

Each single change is bounded to at most 2x. Overlapping transitions are disallowed, and changes are rate-limited to once per governance period (monthly).

| Cycles | Max Increase | Max Decrease |
|---|---|---|
| 1 | 2x | 0.5x |
| 2 | 4x | 0.25x |
| 3 | 8x | 0.125x |
| 6 | 64x | 0.016x |
| 12 | 4096x | 0.00024x |

A 10x change requires at least 4 months (ceil(log2(10)) = 4 cycles).

## Role-Based Access Control

The protocol implements a three-tier role hierarchy per governable function:

| Role | Capability |
|---|---|
| **Executor** | Calls the restricted function |
| **Admin** | Grants and revokes the executor role |
| **Guard** | Veto-only revocation (cannot execute) |

Guard roles serve as a "break glass" mechanism, allowing emergency halts of malicious actions without granting execution power.

### Governance Attack Precautions

- Delayed feed changes require up to 3 months
- Guard role separation prevents escalation
- Gradual parameter migration eliminates arbitrage from sudden changes
- Bounded cumulative change creates predictable worst-case scenarios
- **Immutable constraints:** minimum decimals >= 6, minimum 2 tokens, fixed token list, non-upgradeable contracts
