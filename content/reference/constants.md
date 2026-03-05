---
title: Protocol Constants
description: Compile-time constants defined in the XPower Banq protocol's Constant.sol library.
---

# Protocol Constants

All compile-time constants are defined in the protocol's `Constant.sol` library. These values are immutable and cannot be changed via governance.

## Time Constants

All values are in seconds.

| Constant | Value | Definition |
|---|---|---|
| `CENTURY` | 3,155,760,000 | 365.25 x 100 x 86400 |
| `YEAR` | 31,557,600 | 365.25 x 86400 |
| `MONTH` | 2,629,800 | YEAR / 12 |
| `WEEK` | 604,800 | 7 x 86400 |
| `DAY` | 86,400 | 24 x 3600 |
| `HOUR` | 3,600 | 60 x 60 |
| `MINUTE` | 60 | 60 seconds |
| `SECOND` | 1 | 1 second |

## Fixed-Point Representation Constants

| Constant | Value | Meaning |
|---|---|---|
| `RAY` | 10^27 | Ray precision (27 decimals) |
| `ONE` | 10^18 | WAD unit (1.0) |
| `TWO` | 2 x 10^18 | WAD unit (2.0) |
| `HLF` | 0.5 x 10^18 | WAD unit (0.5) |
| `NIL` | 0 | WAD unit (0.0) |
| `PCT` | 10^16 | 1 percentage point |
| `BPS` | 10^14 | 1 basis point |

## Constraint Constants

| Constant | Value | Purpose |
|---|---|---|
| `MAX_DIFFICULTY` | 64 | Max PoW difficulty |
| `MIN_HOLDERS` | 10^18 | Min holders upper bound |
| `VERSION` | 0x1a5 | Protocol version |

## EMA Decay Factors

Pre-computed EMA decay factors relating half-life (in refresh periods) to the decay coefficient alpha, used for log-space TWAP oracle smoothing.

| Half-life (periods) | Decay alpha | Use Case |
|---|---|---|
| 1 | 0.500000 | Fast response |
| 2 | 0.707107 | Short-term |
| 12 | 0.943874 | Medium-term |
| 24 | 0.971532 | Long-term |

The default oracle decay of 0.944 (approximately 12-period half-life) with hourly refreshes means approximately 40 hours of sustained manipulation is required to achieve 90% price deviation.
