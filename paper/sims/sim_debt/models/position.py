"""
Position pool generation and liquidation simulation.

Vectorized threshold-crossing approach:
  1. Pre-compute critical oracle price ratio for each position
  2. For each MC path, find first time oracle crosses threshold
  3. Compute bad debt at liquidation time using true price

References:
  source/contract/Pool.sol lines 482-498 — health check
  source/contract/Pool.sol lines 432-457 — liquidation (square)
  spec/bad-debt-risk-quantification.md §4.2, §5.2
"""
import numpy as np
from typing import Optional

from ..config import (
    WEIGHT_MAX,
    DEFAULT_WEIGHT_SUPPLY,
    DEFAULT_WEIGHT_BORROW,
    HEALTH_MEAN,
    HEALTH_STD,
    HEALTH_MIN,
    HEALTH_MAX,
    MC_NUM_POSITIONS,
    DEFAULT_LIQ_EXPONENT,
    DEFAULT_PRICE_IMPACT_K,
)


def generate_pool(
    n_positions: int = MC_NUM_POSITIONS,
    ltv: float = DEFAULT_WEIGHT_SUPPLY / DEFAULT_WEIGHT_BORROW,
    lock_fraction: float = 0.0,
    seed: int = 42,
) -> dict:
    """
    Generate a synthetic pool of borrower positions.

    Health factors: H ~ TruncatedNormal(1.5, 0.3, [1.0, 3.0])
    Position sizes: log-normal, normalized to sum to 1 (fraction of TVL)

    For each position, given initial health H and effective LTV:
      supply_value = H * borrow_value / LTV

    The critical oracle price ratio (price / initial_price) at which
    H_oracle = 1 is:
      p_critical = 1 / H
    (i.e., oracle-reported price must drop to 1/H for liquidation trigger)

    Returns dict with vectorized arrays:
      - supply: supply values (n_positions,)
      - borrow: borrow values (n_positions,)
      - health: initial health factors (n_positions,)
      - lock_fraction: lock fraction (scalar)
      - p_critical: critical oracle price ratio for each position (n_positions,)
      - tvl_weights: each position's share of total supply TVL (n_positions,)
    """
    rng = np.random.default_rng(seed)

    # Truncated normal health factors
    healths = np.empty(0)
    while len(healths) < n_positions:
        batch = rng.normal(HEALTH_MEAN, HEALTH_STD, n_positions * 3)
        batch = batch[(batch >= HEALTH_MIN) & (batch <= HEALTH_MAX)]
        healths = np.concatenate([healths, batch])
    healths = healths[:n_positions]

    # Log-normal sizes for borrow amounts (fraction of TVL)
    sizes = rng.lognormal(mean=0.0, sigma=1.5, size=n_positions)
    sizes /= sizes.sum()

    borrow = sizes
    supply = healths * borrow / ltv  # supply = H * borrow / LTV

    # Critical oracle price ratio for liquidation trigger
    # H_oracle = (supply * p_oracle * w_s) / (borrow * w_b)
    #          = (H * borrow / LTV) * p_oracle * w_s / (borrow * w_b)
    #          = H * p_oracle * (w_s / (LTV * w_b))
    #          = H * p_oracle        [since LTV = w_s / w_b]
    # H_oracle < 1 when p_oracle < 1 / H
    p_critical = 1.0 / healths

    # TVL weights (each position's share of total supply value)
    total_supply = supply.sum()
    tvl_weights = supply / total_supply if total_supply > 0 else np.ones(n_positions) / n_positions

    return {
        "supply": supply,
        "borrow": borrow,
        "health": healths,
        "lock_fraction": lock_fraction,
        "p_critical": p_critical,
        "tvl_weights": tvl_weights,
        "n": n_positions,
        "ltv": ltv,
    }


def simulate_pool_vectorized(
    pool: dict,
    oracle_price_ratios: np.ndarray,
    true_price_ratios: np.ndarray,
) -> dict:
    """
    Simulate liquidations for a single price path (vectorized over positions).

    Args:
        pool: dict from generate_pool()
        oracle_price_ratios: (n_steps,) oracle price / initial price
        true_price_ratios: (n_steps,) true price / initial price

    Returns dict:
        - total_bad_debt_pct: bad debt as % of initial TVL
        - bad_debt_per_position: (n_positions,) bad debt per position
        - liquidation_times: (n_positions,) step at which liquidated (-1 if never)
        - phantom_healthy_at: (n_steps,) count of phantom-healthy positions
        - liquidation_delays: list of delays (steps) between true-underwater and oracle-trigger
    """
    n_steps = len(oracle_price_ratios)
    p_crit = pool["p_critical"]          # (n_positions,)
    supply = pool["supply"]              # (n_positions,)
    borrow = pool["borrow"]              # (n_positions,)
    ltv = pool["ltv"]
    n_pos = pool["n"]

    # True underwater threshold: H_true < 1 when p_ratio < 1/H = p_critical
    # (Bad debt occurs when supply * p < borrow, i.e., p_ratio < LTV/H,
    #  but that is computed directly at lines 151-153, not via threshold.)
    p_true_crit = p_crit

    # Find first time oracle crosses each position's threshold
    # oracle_price_ratios: (n_steps,), p_crit: (n_positions,)
    # Broadcast: (n_steps, 1) < (1, n_positions) -> (n_steps, n_positions)
    oracle_below = oracle_price_ratios[:, np.newaxis] < p_crit[np.newaxis, :]
    true_below = true_price_ratios[:, np.newaxis] < p_true_crit[np.newaxis, :]

    # First oracle liquidation time per position
    liq_times = np.full(n_pos, -1, dtype=np.int64)
    oracle_ever_below = oracle_below.any(axis=0)
    liq_times[oracle_ever_below] = np.argmax(oracle_below[:, oracle_ever_below], axis=0)

    # First true-underwater time per position
    true_under_times = np.full(n_pos, -1, dtype=np.int64)
    true_ever_below = true_below.any(axis=0)
    true_under_times[true_ever_below] = np.argmax(true_below[:, true_ever_below], axis=0)

    # Bad debt per position at oracle-triggered liquidation
    bad_debt = np.zeros(n_pos)
    liquidated = liq_times >= 0
    if liquidated.any():
        t_liq = liq_times[liquidated]
        true_p_at_liq = true_price_ratios[t_liq]
        # Bad debt = max(0, borrow - supply * true_price_ratio)
        shortfall = borrow[liquidated] - supply[liquidated] * true_p_at_liq
        bad_debt[liquidated] = np.maximum(0.0, shortfall)

    # Positions that are truly underwater but never oracle-liquidated
    # (oracle never catches up) — these accumulate as permanent bad debt
    stuck = true_ever_below & ~oracle_ever_below
    if stuck.any():
        # Use worst true price as liquidation price
        worst_true = true_price_ratios.min()
        shortfall_stuck = borrow[stuck] - supply[stuck] * worst_true
        bad_debt[stuck] = np.maximum(0.0, shortfall_stuck)

    # Phantom-healthy count at each step
    phantom = np.zeros(n_steps, dtype=np.int64)
    still_alive = np.ones(n_pos, dtype=bool)
    for t in range(n_steps):
        # Remove already-liquidated positions
        just_liquidated = liq_times == t
        still_alive[just_liquidated] = False
        # Phantom: alive, oracle healthy, truly underwater
        alive_mask = still_alive
        phantom[t] = np.sum(
            ~oracle_below[t, alive_mask] & true_below[t, alive_mask]
        )

    # Liquidation delays
    delays = []
    both = liquidated & (true_under_times >= 0)
    if both.any():
        d = liq_times[both] - true_under_times[both]
        delays = d[d >= 0].tolist()

    # Total TVL = sum of supply values (at initial price ratio = 1)
    tvl = supply.sum()

    return {
        "total_bad_debt_pct": bad_debt.sum() / tvl * 100 if tvl > 0 else 0.0,
        "total_bad_debt_abs": bad_debt.sum(),
        "bad_debt_per_position": bad_debt,
        "liquidation_times": liq_times,
        "phantom_healthy_at": phantom,
        "liquidation_delays": delays,
        "n_liquidated": int(liquidated.sum()),
        "n_stuck": int(stuck.sum()),
    }


def simulate_pool_partial_liquidation(
    pool: dict,
    oracle_price_ratios: np.ndarray,
    true_price_ratios: np.ndarray,
    liq_exponent: int = DEFAULT_LIQ_EXPONENT,
    price_impact_k: float = DEFAULT_PRICE_IMPACT_K,
) -> dict:
    """
    Simulate with 2^(-e) partial liquidation per oracle refresh step.

    Each step where H_oracle < 1, a fraction (1 - 2^(-e)) of remaining
    position is liquidated. With e=1 (default), 50% per step.

    Args:
        liq_exponent: e in 2^(-e); higher e = slower liquidation
        price_impact_k: price haircut on liquidation recovery
    """
    n_steps = len(oracle_price_ratios)
    n_pos = pool["n"]
    p_crit = pool["p_critical"]
    supply = pool["supply"]
    borrow = pool["borrow"]

    liq_frac = 1.0 - 2.0 ** (-liq_exponent)  # fraction liquidated per step
    remaining = np.ones(n_pos)
    total_bad_debt = np.zeros(n_pos)
    liq_times = np.full(n_pos, -1, dtype=np.int64)
    all_delays = []

    # Pre-compute true underwater times
    p_true_crit = p_crit
    true_below = true_price_ratios[:, np.newaxis] < p_true_crit[np.newaxis, :]
    true_under_times = np.full(n_pos, -1, dtype=np.int64)
    true_ever_below = true_below.any(axis=0)
    true_under_times[true_ever_below] = np.argmax(
        true_below[:, true_ever_below], axis=0
    )

    for t in range(n_steps):
        # Which positions are oracle-unhealthy and have remaining fraction?
        oracle_unhealthy = oracle_price_ratios[t] < p_crit
        can_liq = oracle_unhealthy & (remaining > 0.001)

        if not can_liq.any():
            continue

        # Record first liquidation time
        first_liq = can_liq & (liq_times < 0)
        liq_times[first_liq] = t

        # Fraction liquidated this step
        liq_amount = liq_frac * remaining[can_liq]

        # Effective true price with market impact haircut
        effective_true_p = true_price_ratios[t] * (1.0 - price_impact_k)

        # Bad debt on liquidated fraction
        shortfall = (
            liq_amount * borrow[can_liq]
            - liq_amount * supply[can_liq] * effective_true_p
        )
        total_bad_debt[can_liq] += np.maximum(0.0, shortfall)
        remaining[can_liq] -= liq_amount

    # Positions never fully liquidated but truly underwater
    stuck = (remaining > 0.001) & true_ever_below
    if stuck.any():
        worst_true = true_price_ratios.min() * (1.0 - price_impact_k)
        shortfall_stuck = (
            remaining[stuck] * borrow[stuck]
            - remaining[stuck] * supply[stuck] * worst_true
        )
        total_bad_debt[stuck] += np.maximum(0.0, shortfall_stuck)

    # Liquidation delays
    both = (liq_times >= 0) & (true_under_times >= 0)
    if both.any():
        d = liq_times[both] - true_under_times[both]
        all_delays = d[d >= 0].tolist()

    tvl = supply.sum()

    return {
        "total_bad_debt_pct": total_bad_debt.sum() / tvl * 100 if tvl > 0 else 0.0,
        "total_bad_debt_abs": total_bad_debt.sum(),
        "bad_debt_per_position": total_bad_debt,
        "liquidation_times": liq_times,
        "liquidation_delays": all_delays,
        "n_liquidated": int((liq_times >= 0).sum()),
        "n_stuck": int(stuck.sum()),
    }


def simulate_pool_batch(
    pool: dict,
    oracle_matrix: np.ndarray,
    true_matrix: np.ndarray,
    liq_exponent: int = None,
    price_impact_k: float = DEFAULT_PRICE_IMPACT_K,
) -> dict:
    """
    Simulate pool across multiple price paths.

    Args:
        pool: dict from generate_pool()
        oracle_matrix: (n_paths, n_steps) oracle price ratios
        true_matrix: (n_paths, n_steps) true price ratios
        liq_exponent: if set, use partial liquidation (2^-e per step)
        price_impact_k: price haircut on liquidation recovery

    Returns dict:
        bad_debt_pcts: (n_paths,) bad debt as % of TVL
        liquidation_delays: list of all delays (steps) across all paths
        max_drawdowns: (n_paths,) max drawdown per path
    """
    n_paths = oracle_matrix.shape[0]
    bad_debts = np.empty(n_paths)
    all_delays = []

    # Max drawdown per path (from true prices)
    running_max = np.maximum.accumulate(true_matrix, axis=1)
    drawdowns = 1.0 - true_matrix / np.maximum(running_max, 1e-20)
    max_drawdowns = drawdowns.max(axis=1)

    use_partial = liq_exponent is not None

    for i in range(n_paths):
        if use_partial:
            result = simulate_pool_partial_liquidation(
                pool,
                oracle_matrix[i],
                true_matrix[i],
                liq_exponent=liq_exponent,
                price_impact_k=price_impact_k,
            )
        else:
            result = simulate_pool_vectorized(
                pool,
                oracle_matrix[i],
                true_matrix[i],
            )
        bad_debts[i] = result["total_bad_debt_pct"]
        all_delays.extend(result["liquidation_delays"])

    return {
        "bad_debt_pcts": bad_debts,
        "liquidation_delays": all_delays,
        "max_drawdowns": max_drawdowns,
    }
