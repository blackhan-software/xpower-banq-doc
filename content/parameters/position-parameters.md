# Position parameters

Parameters governing each Position contract — supply or borrow (`PositionSupervised`).

## Defaults

| ID | Parameter | Range | Notes |
|---|---|---|---|
| `0x0` | `CAP` | 0 – 2¹¹² − 1 | Cap limit for the position. Setting above `type(uint112).max` reverts with `TooLarge`. |
| `0x1` | `BASE` | 0 – 50% | Base risk premium: flat rate added to the kinked interest-rate curve. |
| `0x2` | `UTIL` | 0 – &lt;100% | Target utilisation rate. Must be ≥ `RATE`. |
| `0x4` | `RATE` | 0 – &lt;100% | Target interest rate at `UTIL`. Must be ≤ `UTIL`. |
| `0x8` | `SPREAD` | 0 – 50% | Half-spread between supply and borrow APR. Caps `LOCK_BONUS` and `LOCK_MALUS`. |
| `0x10` | `MIN_HOLDERS` | 0 – `Constant.MIN_HOLDERS` | Floor on the large-holder count used in the cap divisor (`largeHolders()` = max of the live count and this parameter). `Constant.MIN_HOLDERS` is the governance ceiling. |
| `0x20` | `LOCK_BONUS` | 0 – `SPREAD` | Supply-rate **increase** for locked supply. |
| `0x40` | `LOCK_MALUS` | 0 – `SPREAD` | Borrow-rate **decrease** for locked borrow. |

## How LOCK_BONUS / LOCK_MALUS interact with SPREAD

Both bonus and malus are bounded above by the current `SPREAD`. Reducing `SPREAD` automatically caps these (the supervisor refuses any new `SPREAD` value below either bonus or malus). At `LOCK_BONUS = LOCK_MALUS = SPREAD`, full lock adoption produces zero protocol margin (solvent but unprofitable).

## Reading from the contract

```solidity
ISupplyPosition supply = pool.supplyOf(IERC20(APOW));
(uint256 base,)   = supply.getTarget(supply.BASE_ID());
(uint256 spread,) = supply.getTarget(supply.SPREAD_ID());
(uint256 bonus,)  = supply.getTarget(supply.LOCK_BONUS_ID());
```

`UTIL` and `RATE` together define the kink of the IR-model curve; `BASE` is the flat risk premium that lifts the whole curve. The borrow/supply spread (`SPREAD`) and lock adjustments (`LOCK_BONUS`/`LOCK_MALUS`) are separate parameters, not coefficients of the kink.

## Where to go next

- [Pool parameters](/parameters/pool-parameters)
- [Bonus and malus](/features/locked-positions/bonus-and-malus)
- [Position caps](/features/position-caps/overview)
