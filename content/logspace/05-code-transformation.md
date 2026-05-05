---
title: "5. Code Transformation"
prev:
  text: "4. Log-Space Index"
  link: /logspace/04-log-space-index
next:
  text: "6. Gas Analysis"
  link: /logspace/06-gas-analysis
---

This section presents the complete transformation of each affected code path. Unaffected paths (oracle, lock ring-buffer, governance) are omitted.

## Accrual: `_indexOf`

The accrual function computes the updated index given elapsed time $\Delta t$.

```solidity
// Multiplicative accrual (before)
function _indexOf(uint256 dt)
    internal view override
    returns (uint256 index_ray, uint256 util_wad)
{
    util_wad = _pool.vaultOf(_asset).util();
    if (dt > 0) {
        uint256 annum_wad = _model().by(util_wad);
        uint256 yield_wad = Math.mulDiv(
            annum_wad, dt, Constant.YEAR);
        index_ray = Rate.accrue(
            _index_ray, yield_wad); // exp * mul
    } else {
        index_ray = _index_ray;
    }
}
```

```solidity
// Log-space accrual (after)
function _indexOf(uint256 dt)
    internal view override
    returns (uint256 index_wad, uint256 util_wad)
{
    util_wad = _pool.vaultOf(_asset).util();
    if (dt > 0) {
        uint256 annum_wad = _model().by(util_wad);
        uint256 yield_wad = Math.mulDiv(
            annum_wad, dt, Constant.YEAR);
        index_wad = _index_wad + yield_wad;
    } else {
        index_wad = _index_wad;
    }
}
```

The `Rate.accrue` call — wrapping `ud().mul(exp(ud()))` — is eliminated. The `yield_wad` computation is unchanged; it is already the per-period log-increment.

## Balance Query: `totalOf`

```solidity
// Multiplicative balance query (before)
function totalOf(address user)
    public view returns (uint256)
{
    uint256 principal = _principalOf[user];
    if (principal > 0) {
        uint256 user_index = _userIndex[user];
        if (user_index > 0) {
            (uint256 time_index,) =
                _indexOf(block.timestamp - _stamp);
            return Math.mulDiv(
                principal, time_index, user_index);
        }
        return principal;
    }
    return 0;
}
```

```solidity
// Log-space balance query (after)
function totalOf(address user)
    public view returns (uint256)
{
    uint256 principal = _principalOf[user];
    if (principal > 0) {
        (uint256 index_wad,) =
            _indexOf(block.timestamp - _stamp);
        uint256 user_index = _userIndex[user];
        if (index_wad > user_index) {
            uint256 growth = exp(
                ud(index_wad - user_index)
            ).intoUint256();
            return Math.mulDiv(
                principal, growth, Constant.ONE);
        }
        return principal;
    }
    return 0;
}
```

The `exp()` call moves from the write path (every accrual, affecting all users) to the read path (per-user, on demand). The guard `index_wad > user_index` replaces `user_index > 0`: a zero log-index means no accrual since deposit, so $\exp(0) = 1$ and the principal is returned directly.

## Lock Yield: `_lockYieldOf`

The lock bonus/malus computation ([Time Locks §8.2](/timelocks/08-integration#graduated-lock-bonus-malus)) requires the yield fraction $\exp(\Delta L) - 1$.

```solidity
// Lock yield in log-space
function _lockYieldOf(
    address user, uint256 rate_param_id
) internal view returns (uint256) {
    uint256 depth = _lock.depthOf(user);
    if (depth > 0) {
        uint256 user_index = _userIndex[user];
        if (_index_wad > user_index) {
            uint256 rate_param =
                parameterOf(rate_param_id);
            if (rate_param > 0) {
                uint256 growth = exp(ud(
                    _index_wad - user_index
                )).intoUint256();
                uint256 moment = Math.mulDiv(
                    depth, growth - Constant.ONE,
                    Constant.ONE);
                return Math.mulDiv(rate_param,
                    moment,
                    Constant.ONE * LockLib.LOCK_TIME
                );
            }
        }
    }
    return 0;
}
```

The term `growth - Constant.ONE` is the yield fraction $\exp(\Delta L) - 1$, which in the multiplicative form was $(I - I_u) / I_u$. The subtraction is exact because $\exp(x) \geq 10^{18}$ for all $x \geq 0$ in UD60x18.

**Unit analysis.** `growth - ONE` is dimensionless [WAD]. $\texttt{depth} \times (\texttt{growth} - 1) / 10^{18}$ gives token-seconds [WAD·s]. The second `mulDiv` divides by $10^{18} \times \texttt{LOCK\_TIME}$ [WAD·s], producing tokens [WAD]. Identical to the multiplicative form.

> **Shipped lock-yield path.** The shipped `Position.sol` does not expose `_lockYieldOf` as a separate helper. The bonus/malus is instead applied through a per-user spread differential (`_spreadDiff` / `_model(user, rate_param_id)`) that lowers the effective spread in `_indexOf` for users with non-zero lock depth. The yield-fraction identity $\exp(\Delta L) - 1$ presented above is preserved mathematically: it is now absorbed into the additive log-increment rather than computed as a separate `growth - 1` term at read time.

## Per-User Snapshots

```solidity
function _reindexMore(
    address user, uint256 amount
) internal virtual {
    _principalOf[user] = add256(
        _principalOf[user], amount);
    _userIndex[user] = _index_wad;
}

function _reindexLess(
    address user, uint256 amount
) internal virtual {
    _principalOf[user] = sub256(
        _principalOf[user], amount);
    _userIndex[user] = _index_wad;
}
```

No structural change — the snapshot is a scalar copy in both representations.
