"""
Section 3: Oracle Lag Model

Deliverables:
  1. Heatmap of oracle deviation vs (crash magnitude × time elapsed)
  2. Phantom-healthy window tables per (LTV, crash)
  3. Worst-case blind time = refresh_interval + phantom_window
"""
import numpy as np

from ..config import (
    CRASH_MAGNITUDES,
    LAG_REFRESH_COUNT,
    DEFAULT_DECAY,
    DEFAULT_REFRESH_INTERVAL,
    LTV_SWEEP,
    HEALTH_MEAN,
    HEALTH_MIN,
    HEALTH_MAX,
    HOUR,
)
from ..models.oracle import oracle_deviation_table, oracle_trajectory_step_crash


def compute_lag_heatmap(
    crash_magnitudes: list[float] = CRASH_MAGNITUDES,
    n_refreshes: int = LAG_REFRESH_COUNT,
    decay: float = DEFAULT_DECAY,
) -> dict:
    """
    Deliverable 1: Oracle lag heatmap.

    Returns:
        - absorption: (n_crashes, n_refreshes+1) fraction of crash absorbed
        - deviation_pct: (n_crashes, n_refreshes+1) oracle overestimate as % of true price
        - crash_magnitudes: list of crash fractions
        - hours: array of hours [0..n_refreshes]
    """
    magnitudes = np.array(crash_magnitudes)
    absorption = oracle_deviation_table(magnitudes, n_refreshes, decay)

    # Deviation = (oracle_price - true_price) / true_price
    deviation_pct = np.empty_like(absorption)
    for i, δ in enumerate(magnitudes):
        trajectory = oracle_trajectory_step_crash(1.0, δ, decay, n_refreshes)
        true_price = 1.0 - δ
        deviation_pct[i, :] = (trajectory - true_price) / true_price * 100

    return {
        "absorption": absorption,
        "deviation_pct": deviation_pct,
        "crash_magnitudes": magnitudes,
        "hours": np.arange(n_refreshes + 1),
    }


def compute_phantom_window(
    crash_frac: float,
    ltv: float,
    decay: float = DEFAULT_DECAY,
    initial_health: float = HEALTH_MEAN,
    max_refreshes: int = 500,
) -> dict:
    """
    Deliverable 2: Phantom-healthy window for a single (crash, LTV, health) triple.

    A position is phantom-healthy when:
      - H_true < 1  → truly underwater
      - H_oracle ≥ 1 → oracle says healthy

    H_true = H_init * (1 - δ) / 1.0 = H_init * (1 - δ)
      (collateral dropped by δ, debt unchanged, price ratio = 1 - δ)

    For the position to be truly underwater: H_init * (1 - δ) < 1
      → requires δ > 1 - 1/H_init

    H_oracle = H_init * p_oracle / p_initial
      where p_oracle follows the TWAP trajectory.

    Phantom-healthy until H_oracle < 1:
      p_oracle < 1/H_init  (since at initial p_oracle/p_init was 1, now it's the ratio)
      Actually: H_oracle = supply * p_oracle * w_s / (borrow * w_b)
      With p_oracle = oracle_price / initial_price:
        H_oracle = H_init * p_oracle_ratio
        Phantom ends when: H_init * p_oracle_ratio < 1
        → p_oracle_ratio < 1 / H_init

    The oracle ratio starts at 1 and converges toward (1 - δ).
    Oracle ratio at refresh n: trajectory[n] / p0

    Returns:
      - is_underwater: whether the position is truly underwater at all
      - n_phantom: number of refreshes the position remains phantom-healthy
      - phantom_hours: n_phantom * refresh_interval / 3600
      - oracle_ratio_at_liquidation: oracle price ratio when liquidation triggers
    """
    p0 = 1.0
    true_ratio = 1.0 - crash_frac

    # Check if position is truly underwater
    h_true = initial_health * true_ratio
    if h_true >= 1.0:
        return {
            "is_underwater": False,
            "n_phantom": 0,
            "phantom_hours": 0.0,
            "oracle_ratio_at_liquidation": None,
        }

    # Oracle liquidation threshold: p_oracle_ratio < 1/H_init
    threshold = 1.0 / initial_health

    # Compute oracle trajectory
    trajectory = oracle_trajectory_step_crash(p0, crash_frac, decay, max_refreshes)
    oracle_ratios = trajectory / p0

    # Find first refresh where oracle ratio drops below threshold
    below = oracle_ratios < threshold
    if not below.any():
        n_phantom = max_refreshes
    else:
        n_phantom = int(np.argmax(below))

    return {
        "is_underwater": True,
        "n_phantom": n_phantom,
        "phantom_hours": float(n_phantom),  # 1 refresh per hour (default)
        "oracle_ratio_at_liquidation": float(oracle_ratios[n_phantom]) if n_phantom < len(oracle_ratios) else None,
    }


def compute_phantom_window_table(
    crash_magnitudes: list[float] = CRASH_MAGNITUDES,
    ltvs: list[float] = LTV_SWEEP,
    decay: float = DEFAULT_DECAY,
    healths: list[float] = None,
) -> dict:
    """
    Deliverable 2: Full phantom-healthy window table.

    For each (LTV, crash, health) triple, compute the phantom window.

    Args:
        crash_magnitudes: crash fractions to test
        ltvs: effective LTV values
        decay: oracle decay factor
        healths: initial health factors to test (default: [1.1, 1.3, 1.5, 2.0])

    Returns:
        table: nested dict [ltv][crash][health] → phantom window info
        summary: DataFrame-like list of dicts
    """
    if healths is None:
        healths = [1.1, 1.3, 1.5, 2.0]

    results = []
    for ltv in ltvs:
        for δ in crash_magnitudes:
            for h in healths:
                pw = compute_phantom_window(δ, ltv, decay, h)
                results.append({
                    "ltv": ltv,
                    "crash_pct": δ * 100,
                    "initial_health": h,
                    "is_underwater": pw["is_underwater"],
                    "phantom_hours": pw["phantom_hours"],
                    "n_phantom_refreshes": pw["n_phantom"],
                })

    return {"rows": results}


def compute_blind_time_table(
    crash_magnitudes: list[float] = CRASH_MAGNITUDES,
    ltvs: list[float] = LTV_SWEEP,
    decay: float = DEFAULT_DECAY,
    refresh_interval: float = DEFAULT_REFRESH_INTERVAL,
    initial_health: float = HEALTH_MEAN,
) -> dict:
    """
    Worst-case blind time = refresh_interval + phantom_window.

    The worst case occurs when the crash happens immediately after a refresh,
    adding up to one full refresh_interval of total blindness before the
    oracle even sees the new price.

    Returns:
        rows: list of dicts with (ltv, crash, blind_hours)
    """
    results = []
    for ltv in ltvs:
        for δ in crash_magnitudes:
            pw = compute_phantom_window(δ, ltv, decay, initial_health)
            blind_hours = (refresh_interval / 3600.0) + pw["phantom_hours"]
            results.append({
                "ltv": ltv,
                "crash_pct": δ * 100,
                "phantom_hours": pw["phantom_hours"],
                "blind_hours": blind_hours,
                "is_underwater": pw["is_underwater"],
            })

    return {"rows": results}


def run_all(decay: float = DEFAULT_DECAY) -> dict:
    """Run all Section 3 analyses."""
    return {
        "lag_heatmap": compute_lag_heatmap(decay=decay),
        "phantom_windows": compute_phantom_window_table(decay=decay),
        "blind_times": compute_blind_time_table(decay=decay),
    }
