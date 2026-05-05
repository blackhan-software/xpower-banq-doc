---
title: Protocol Constants
description: Compile-time constants defined in the XPower Banq protocol's Constant.sol library.
---

All compile-time constants are defined in the protocol's `Constant.sol` library. These values are immutable and cannot be changed via governance.

## Time Constants

All values are in seconds.

| Constant | Value | Definition |
|---|---:|---|
| `CENTURY` | 3,155,760,000 | $365.25 \times 100 \times 86400$ |
| `YEAR` | 31,557,600 | $365.25 \times 86400$ |
| `MONTH` | 2,629,800 | YEAR / 12 |
| `WEEK` | 604,800 | $7 \times 86400$ |
| `DAY` | 86,400 | $24 \times 3600$ |
| `HOUR` | 3,600 | $60 \times 60$ |
| `MINUTE` | 60 | 60 seconds |
| `SECOND` | 1 | 1 second |

## Fixed-Point Representation Constants

| Constant | Value | Meaning |
|---|---:|---|
| `ONE` | $10^{18}$ | WAD unit (1.0) |
| `TWO` | $2 \times 10^{18}$ | WAD unit (2.0) |
| `HLF` | $0.5 \times 10^{18}$ | WAD unit (0.5) |
| `NIL` | 0 | WAD unit (0.0) |
| `PCT` | $10^{16}$ | 1 percentage point |
| `BPS` | $10^{14}$ | 1 basis point |

## Constraint Constants

| Constant | Value | Purpose |
|---|---:|---|
| `MAX_DIFFICULTY` | 64 | Max PoW difficulty |
| `MIN_HOLDERS` | $10^{18}$ | Min holders upper bound |
| `VERSION` | 0x1ba | Protocol version |
