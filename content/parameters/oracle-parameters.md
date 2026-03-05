# Oracle parameters

Parameters governing the log-space TWAP oracle (`OracleSupervised`).

## Defaults

| ID | Parameter | Range | Notes |
|---|---|---|---|
| `0x1` | `DECAY` | 0.5–1.0 | EWMA decay factor (the `α` in the math). At a 1-hour `LIMIT` the default `0.944` gives a 12-hour half-life. |
| `0x2` | `DELAY` | 1 week – 3 months | Wait between *enlisting* a feed and that feed becoming live. |
| `0x4` | `LEVEL` | 0–64 | PoW difficulty for permissionless `retwap` calls. |
| `0x8` | `LIMIT` | 1 second – 1 day | Minimum interval between two TWAP refreshes. |

## What each parameter does

- **`DECAY`** — geometric weight on each new sample. Smaller `DECAY` ⇒ faster adaptation, higher manipulation surface; larger `DECAY` ⇒ smoother price, slower reaction to genuine moves.
- **`DELAY`** — gives users a window to react before a newly-enlisted feed influences any pool's risk math. Distinct from `LIMIT`: this is a one-shot enlistment delay, not a rolling rate-limit.
- **`LEVEL`** — proof-of-work difficulty a permissionless caller must satisfy to invoke `retwap`. Permissioned callers (`FEED_RETWAP_ROLE`) bypass this.
- **`LIMIT`** — minimum spacing between consecutive TWAP refreshes. A second sample within `LIMIT` reverts. This is what bounds the per-block manipulation surface.

## Reading from the contract

```solidity
IOracle oracle = IOracle(0x965A5B2e3fe812F0483034b4f0b110F663B09Cd5); // APOW/XPOW
(uint256 decay,) = oracle.getTarget(oracle.DECAY_ID());
(uint256 limit,) = oracle.getTarget(oracle.LIMIT_ID());
```

Every parameter ID is a public constant on the contract (`DECAY_ID`, `DELAY_ID`, `LEVEL_ID`, `LIMIT_ID`). Current and pending values are read with `getTarget(id)`.

## Where to go next

- [TWAP oracle overview](/features/twap-oracle/overview)
- [Manipulation resistance](/features/twap-oracle/manipulation-resistance)
- [Oracle staleness](/risks/oracle-staleness)
