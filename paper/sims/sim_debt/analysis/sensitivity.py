"""
Section 6: Sensitivity Analysis

Deliverables:
  5. Tornado diagrams showing bad debt sensitivity to each parameter
  6. Pairwise interaction heatmaps

References:
  spec/bad-debt-risk-quantification.md §6
"""
import numpy as np
from typing import Optional

from ..config import (
    DEFAULT_DECAY,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_LTV,
    DECAY_06HL,
    DECAY_12HL,
    DECAY_24HL,
    LTV_SWEEP,
    REFRESH_INTERVAL_SWEEP,
    ALPHA_SWEEP,
    LOCK_FRACTION_SWEEP,
    JD_PARAMS_ETH,
    MC_SEED,
    PRICE_IMPACT_SWEEP,
    JUMP_INTENSITY_SWEEP,
    DEFAULT_PRICE_IMPACT_K,
    DEFAULT_JUMP_INTENSITY,
)


def extract_tornado_data(mc_summary: list[dict]) -> dict:
    """
    Compute tornado diagram data from MC sweep results.

    For each parameter, find the range of E[BD] across all values of that
    parameter while holding others at baseline.

    Args:
        mc_summary: list of flat dicts from montecarlo.run_mc_sweep()

    Returns:
        tornado: dict[param_name] → (low_bd, base_bd, high_bd)
    """
    import itertools

    # Baseline values
    base = {
        "decay": DECAY_12HL,
        "refresh_interval": DEFAULT_REFRESH_INTERVAL,
        "ltv": DEFAULT_LTV,
        "lock_fraction": 0.0,
    }

    # Find baseline result
    base_bd = _find_closest(mc_summary, base)

    # For each parameter, find extremes
    params_to_sweep = {
        "decay (α)": ("decay", ALPHA_SWEEP),
        "refresh interval": ("refresh_interval", REFRESH_INTERVAL_SWEEP),
        "LTV": ("ltv", LTV_SWEEP),
        "lock fraction (φ)": ("lock_fraction", LOCK_FRACTION_SWEEP),
    }

    tornado = {}
    for label, (key, values) in params_to_sweep.items():
        bds = []
        for v in values:
            query = {**base, key: v}
            bd = _find_closest(mc_summary, query)
            if bd is not None:
                bds.append(bd)
        if bds:
            tornado[label] = (min(bds), base_bd, max(bds))

    return {"tornado": tornado, "baseline_bd": base_bd}


def _find_closest(summary: list[dict], query: dict) -> Optional[float]:
    """Find the E[BD] for the closest matching parameter set."""
    best = None
    best_dist = float("inf")
    for row in summary:
        dist = sum(
            abs(row.get(k, 0) - v) / max(abs(v), 1e-10)
            for k, v in query.items()
        )
        if dist < best_dist:
            best_dist = dist
            best = row.get("expected_bd", 0.0)
    return best


def extract_interaction_heatmap(
    mc_summary: list[dict],
    param1_key: str,
    param2_key: str,
    metric: str = "expected_bd",
) -> dict:
    """
    Extract 2D interaction heatmap from MC results.

    Filters mc_summary for entries where all OTHER parameters are at baseline,
    then creates a 2D grid of the metric.

    Args:
        mc_summary: list of flat dicts
        param1_key: first parameter (rows)
        param2_key: second parameter (columns)
        metric: which metric to plot (default: expected_bd)

    Returns:
        grid: 2D ndarray of metric values
        param1_values: sorted unique values of param1
        param2_values: sorted unique values of param2
    """
    base = {
        "decay": DECAY_12HL,
        "refresh_interval": DEFAULT_REFRESH_INTERVAL,
        "ltv": DEFAULT_LTV,
        "lock_fraction": 0.0,
    }

    # Get unique values for the two parameters
    p1_vals = sorted(set(r[param1_key] for r in mc_summary))
    p2_vals = sorted(set(r[param2_key] for r in mc_summary))

    grid = np.full((len(p1_vals), len(p2_vals)), np.nan)

    for row in mc_summary:
        # Check if other params are at baseline
        other_params = {k: v for k, v in base.items() if k not in (param1_key, param2_key)}
        is_baseline = all(
            abs(row.get(k, 0) - v) / max(abs(v), 1e-10) < 0.01
            for k, v in other_params.items()
        )
        if not is_baseline:
            continue

        try:
            i = p1_vals.index(row[param1_key])
            j = p2_vals.index(row[param2_key])
            grid[i, j] = row.get(metric, np.nan)
        except (ValueError, KeyError):
            continue

    return {
        "grid": grid,
        "param1_values": p1_vals,
        "param2_values": p2_vals,
        "param1_key": param1_key,
        "param2_key": param2_key,
        "metric": metric,
    }


def extract_tornado_extended(
    mc_summary: list[dict],
    extra_runs: dict = None,
) -> dict:
    """
    Tornado diagram data including price impact k and jump intensity λ_J.

    extra_runs should be a dict:
        "price_impact_k": [(k_value, expected_bd), ...]
        "jump_intensity": [(lambda_j, expected_bd), ...]

    These are computed separately because they require re-running MC with
    modified parameters (not part of the standard sweep grid).
    """
    base_tornado = extract_tornado_data(mc_summary)
    tornado = base_tornado["tornado"]
    baseline_bd = base_tornado["baseline_bd"]

    if extra_runs:
        if "price_impact_k" in extra_runs and extra_runs["price_impact_k"]:
            bds = [bd for _, bd in extra_runs["price_impact_k"]]
            tornado["price impact (k)"] = (min(bds), baseline_bd, max(bds))

        if "jump_intensity" in extra_runs and extra_runs["jump_intensity"]:
            bds = [bd for _, bd in extra_runs["jump_intensity"]]
            tornado["jump intensity (λ_J)"] = (min(bds), baseline_bd, max(bds))

    return {"tornado": tornado, "baseline_bd": baseline_bd}


def compute_all_interactions(
    mc_summary: list[dict],
    extra_interactions: dict = None,
) -> dict:
    """
    Compute all specified pairwise interactions from spec §6.2.

    Returns dict with keys:
        - alpha_x_ltv
        - alpha_x_refresh
        - lock_x_price_impact (if extra_interactions provided)
    """
    result = {
        "alpha_x_ltv": extract_interaction_heatmap(
            mc_summary, "decay", "ltv",
        ),
        "alpha_x_refresh": extract_interaction_heatmap(
            mc_summary, "decay", "refresh_interval",
        ),
    }

    # Lock × price impact from extra runs (not in standard grid)
    if extra_interactions and "lock_x_price_impact" in extra_interactions:
        result["lock_x_price_impact"] = extra_interactions["lock_x_price_impact"]
    else:
        # Fallback: lock × LTV from standard grid
        result["lock_x_ltv"] = extract_interaction_heatmap(
            mc_summary, "lock_fraction", "ltv",
        )

    return result
