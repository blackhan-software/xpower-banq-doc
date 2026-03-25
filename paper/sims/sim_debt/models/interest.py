"""
Interest rate model — replicates source/library/Rate.sol.

Piecewise-linear rate below optimal utilization, quadratic above, capped at 200%.
Borrow rate = base * (1 + spread), Supply rate = base * (1 - spread).
Continuous compounding via exp(rate * dt / YEAR).

References:
  source/library/Rate.sol lines 58-62, 114-118, 170-183
"""
import numpy as np

from ..config import YEAR_SECONDS


def rate_by(util: float, util_opt: float, rate_opt: float) -> float:
    """
    Base interest rate as a function of utilization.

    Below util_opt: linear interpolation from 0 to rate_opt.
    Above util_opt: quadratic growth, capped at 200% (2.0).

    Replicates Rate.by() from Rate.sol lines 170-183.
    """
    if util <= util_opt and util_opt > 0:
        return util * rate_opt / util_opt
    if util_opt >= 1.0:
        return rate_opt
    d1U = 1.0 - util_opt
    d1R = 1.0 - rate_opt
    dUR = util_opt - rate_opt
    pct = (util * d1R - dUR) / d1U
    return min(pct, 2.0)


def borrow_rate(
    util: float,
    util_opt: float = 0.90,
    rate_opt: float = 0.10,
    spread: float = 0.0,
) -> float:
    """BorrowRate.by(): base_rate * (1 + spread). Rate.sol lines 58-62."""
    return rate_by(util, util_opt, rate_opt) * (1.0 + spread)


def supply_rate(
    util: float,
    util_opt: float = 0.90,
    rate_opt: float = 0.10,
    spread: float = 0.0,
) -> float:
    """SupplyRate.by(): base_rate * (1 - spread). Rate.sol lines 114-118."""
    return rate_by(util, util_opt, rate_opt) * (1.0 - spread)


def accrue(amount: float, rate: float, duration: float) -> float:
    """
    Continuous compounding: amount * exp(rate * duration / YEAR).
    Replicates Rate.accrue() using PRBMath exp().
    """
    return amount * np.exp(rate * duration / YEAR_SECONDS)
