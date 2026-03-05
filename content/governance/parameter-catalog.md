# Parameter catalog

Every governable on-chain parameter, with its default, absolute range, and per-cycle rate limit. Names match the IDs exposed by the supervisory contracts (`PoolSupervised`, `PositionSupervised`, `OracleSupervised`, `VaultSupervised`).

## Pool parameters (per token)

| Parameter | Default | Range | Per cycle | Notes |
|---|---|---|---|---|
| `MAX_SUPPLY` | 1 week | 1s – 1y | 0.5×–2× | Supply rate-limit ceiling |
| `MIN_SUPPLY` | 1 day | 1s – 1y | 0.5×–2× | Supply rate-limit floor |
| `POW_SUPPLY` | per token | 0–64 | 0.5×–2× | PoW difficulty for permissionless supply |
| `MAX_BORROW` | 1 week | 1s – 1y | 0.5×–2× | Borrow rate-limit ceiling |
| `MIN_BORROW` | 1 day | 1s – 1y | 0.5×–2× | Borrow rate-limit floor |
| `POW_BORROW` | per token | 0–64 | 0.5×–2× | PoW difficulty for permissionless borrow |
| `POW_SQUARE` | per `partial_exp` | 0–64 | 0.5×–2× | PoW difficulty for permissionless `liquidate` |
| `WEIGHT_SUPPLY` | 170 | 0–255 | 0.5×–2× | Supply-side weight in the health calculation |
| `WEIGHT_BORROW` | 255 | 0–255 | 0.5×–2× | Borrow-side weight in the health calculation |

The effective LTV emerges from the default ratio of `WEIGHT_SUPPLY / WEIGHT_BORROW = 170/255 ≈ 66.67%`. Similarly, the effective supply (or borrow) rate-limit emerges from the default ratio of `MAX_SUPPLY / MIN_SUPPLY = 1w/1d = 7` (or `MAX_BORROW / MIN_BORROW`); i.e. the supply (or borrow) frequency is rate-limited to at most seven actions in a week — per account.

## Position parameters

| Parameter | Default | Range | Per cycle | Notes |
|---|---|---|---|---|
| `CAP` | per pool | 0 – 2¹¹² | 0 – 2¹¹² | Cap limit |
| `BASE` | 0% | 0 – 50% | 0.5×–2× | Base risk premium: flat rate added to the kinked curve |
| `UTIL` | 90% | 0 – &lt;100% | 0.5×–2× | Target utilisation |
| `RATE` | 10% | 0 – &lt;100% | 0.5×–2× | Target interest rate at `UTIL` |
| `SPREAD` | 10% | 0 – 50% | 0.5×–2× | Half-spread between supply and borrow APR |
| `MIN_HOLDERS` | per pool | 0 – `MIN_HOLDERS` | 0.5×–2× | Minimum holder threshold |
| `LOCK_BONUS` | 10% | 0 – `SPREAD` | 0.5×–2× | Supply-rate increase for full lock |
| `LOCK_MALUS` | 10% | 0 – `SPREAD` | 0.5×–2× | Borrow-rate decrease for full lock |

Note, that `CAP` *target* management is **not** subject to the usual per cycle change limits in the range of 0.5×–2×! Further, while the actual cap *value* approaches an arbitrarily increased *target* asymptotically, a decreased *target* below the current cap *value* is applied immediately — which can act as a circuit breaker.

## Vault parameters

| Parameter | Default | Range | Per cycle | Notes |
|---|---|---|---|---|
| `FEE_ENTRY` | 0.1% | 0 – 50% | 0.5×–2× | Skim on `depositAssets` |
| `FEE_EXIT` | 1.0% | 0 – 50% | 0.5×–2× | Skim on `redeemAssets` |
| `POL_FETCHABLE_SHARE` | 0% | 0 – 100% | 0.5×–2× | Max share of accumulated POL surplus that may be fetched (see [protocol-owned liquidity](/features/protocol-owned-liquidity/overview)) |

## Oracle parameters

| Parameter | Default | Range | Per cycle | Notes |
|---|---|---|---|---|
| `DECAY` | 0.944 | 0.5 – 1.0 | 0.5×–2× | EWMA decay (the `α` in the math); 12-hour half-life at `LIMIT = 1h` |
| `DELAY` | 14 days | 1w – 3m | 0.5×–2× | Delay before a newly-enlisted feed becomes live |
| `LEVEL` | per feed | 0 – 64 | 0.5×–2× | PoW difficulty for permissionless `retwap` |
| `LIMIT` | 1 hour | 1s – 1d | 0.5×–2× | Minimum spacing between two TWAP refreshes |

## Per-call arguments (not parameters)

Some quantities the documentation calls out are *call arguments*, not stored parameters:

- `partial_exp` — passed to `liquidate(victim, partial_exp)`. Slice = `2^-partial_exp` of the position. `POW_SQUARE` is the *parameter* that gates difficulty per-`partial_exp`.

## Where to go next

- [Pool parameters](/parameters/pool-parameters)
- [Position parameters](/parameters/position-parameters)
- [Oracle parameters](/parameters/oracle-parameters)
- [Vault parameters](/parameters/vault-parameters)
- [Change-rate constraints](/parameters/change-rate-constraints)
