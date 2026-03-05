# Pool parameters

Per-token parameters governing a single Pool (`PoolSupervised`). Each parameter is keyed by *token address* — a single Pool stores independent values for each of its supported tokens.

## Defaults

| ID byte | Parameter | Range | Notes |
|---|---|---|---|
| `0x11` | `MAX_SUPPLY` | 1 second – 1 year | Per-token rate-limit ceiling on the supply side (smoothed across new deposits). |
| `0x12` | `MIN_SUPPLY` | 1 second – 1 year | Per-token rate-limit floor on the supply side. |
| `0x14` | `POW_SUPPLY` | 0–64 | PoW difficulty for permissionless supply calls. |
| `0x21` | `MAX_BORROW` | 1 second – 1 year | Per-token rate-limit ceiling on the borrow side. |
| `0x22` | `MIN_BORROW` | 1 second – 1 year | Per-token rate-limit floor on the borrow side. |
| `0x24` | `POW_BORROW` | 0–64 | PoW difficulty for permissionless borrow calls. |
| `0x44` | `POW_SQUARE` | 0–64 | PoW difficulty for permissionless `liquidate` calls (per `partial_exp`). |
| `0x81` | `WEIGHT_SUPPLY` | 0–255 | Supply-side weight in the health-factor calculation. |
| `0x82` | `WEIGHT_BORROW` | 0–255 | Borrow-side weight in the health-factor calculation. |

The default v10c deployment uses `WEIGHT_SUPPLY = 170` and `WEIGHT_BORROW = 255`, which gives an effective LTV of roughly `170/255 ≈ 66.67%` for a single-asset pair.

## Reading from the contract

```solidity
IPool pool = IPool(0xBEB2fE4e7Db535aE25A08EFac1d523F373435E1D); // APOW/XPOW
(uint256 weightSupply,) = pool.getTarget(pool.WEIGHT_SUPPLY_ID(IERC20(APOW)));
(uint256 powSupply,)    = pool.getTarget(pool.POW_SUPPLY_ID(IERC20(APOW)));
```

Each parameter accessor takes the relevant token (or `partial_exp` for `POW_SQUARE`) and returns a 256-bit ID; pass that ID to `getTarget(id)`.

## Liquidation slice

The fraction of a position taken in a single `liquidate` call is *not* a stored pool parameter — it is the per-call `partial_exp` argument:

```solidity
pool.liquidate(victim, partial_exp); // slice = 2^-partial_exp
```

`partial_exp = 1` slices 50%, `partial_exp = 2` slices 25%, etc. The protocol additionally lets governance set `POW_SQUARE` *per* `partial_exp` value, so a permissionless 50% slice can be tuned to a different difficulty than a permissionless 25% slice.

## Where to go next

- [Position parameters](/parameters/position-parameters)
- [Oracle parameters](/parameters/oracle-parameters)
- [Vault parameters](/parameters/vault-parameters)
- [Change-rate constraints](/parameters/change-rate-constraints)
