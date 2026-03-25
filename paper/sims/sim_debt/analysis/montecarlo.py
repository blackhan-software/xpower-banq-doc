"""
Section 5: Monte Carlo Simulation

Orchestrates jump-diffusion price generation, oracle simulation, and
pool liquidation tracking across the full parameter sweep.

Architecture:
  1. Generate hourly price paths in chunks (10K paths per chunk)
  2. Run vectorized oracle EMA over all paths simultaneously
  3. Simulate pool liquidation using threshold-crossing approach
  4. Aggregate metrics: E[BD], VaR(99%), CVaR(99%)

References:
  spec/bad-debt-risk-quantification.md §5
"""
import numpy as np
from typing import Optional

from ..config import (
    MC_NUM_PATHS,
    MC_HOURS_PER_YEAR,
    MC_NUM_POSITIONS,
    MC_SEED,
    LTV_SWEEP,
    LOCK_FRACTION_SWEEP,
    REFRESH_INTERVAL_SWEEP,
    ALPHA_SWEEP,
    JD_PARAMS_ETH,
    VAR_CONFIDENCE,
    HOUR,
    DEFAULT_LIQ_EXPONENT,
    DEFAULT_PRICE_IMPACT_K,
)
from ..models.price import generate_paths
from ..models.oracle import run_oracle_over_prices_vectorized
from ..models.position import generate_pool, simulate_pool_batch


def compute_metrics(bad_debt_samples: np.ndarray) -> dict:
    """
    Compute risk metrics from a sample of bad-debt-as-%-of-TVL values.

    Returns:
        expected_bd: mean bad debt %
        var_99: 99th percentile (VaR)
        cvar_99: expected bad debt conditional on exceeding VaR (CVaR/ES)
        max_bd: worst case
        std_bd: standard deviation
        ci_95: 95% confidence interval half-width on the mean
        pct_nonzero: fraction of paths with any bad debt
    """
    n = len(bad_debt_samples)
    if n == 0:
        return {k: 0.0 for k in [
            "expected_bd", "var_99", "cvar_99", "max_bd",
            "std_bd", "ci_95", "pct_nonzero",
        ]}

    sorted_bd = np.sort(bad_debt_samples)
    var_idx = int(VAR_CONFIDENCE * n)
    var_99 = sorted_bd[min(var_idx, n - 1)]
    tail = sorted_bd[var_idx:]
    cvar_99 = tail.mean() if len(tail) > 0 else var_99

    return {
        "expected_bd": float(bad_debt_samples.mean()),
        "var_99": float(var_99),
        "cvar_99": float(cvar_99),
        "max_bd": float(bad_debt_samples.max()),
        "std_bd": float(bad_debt_samples.std()),
        "ci_95": float(1.96 * bad_debt_samples.std() / np.sqrt(n)),
        "pct_nonzero": float((bad_debt_samples > 0).mean() * 100),
    }


def _subsample_to_refresh_points(
    prices: np.ndarray,
    refresh_interval_hours: int,
) -> np.ndarray:
    """
    Subsample hourly prices to match oracle refresh interval.

    If refresh_interval is 2 hours, take every 2nd hourly price.
    If refresh_interval is 15 minutes (0.25 hours), keep all (hourly is coarser).
    """
    if refresh_interval_hours <= 1:
        return prices  # hourly or faster: keep all
    return prices[:, ::refresh_interval_hours]


def run_mc_single(
    n_paths: int,
    ltv: float,
    lock_fraction: float,
    refresh_interval: float,
    decay: float,
    jd_params: dict = JD_PARAMS_ETH,
    n_positions: int = MC_NUM_POSITIONS,
    seed: int = MC_SEED,
    chunk_size: int = 10_000,
    liq_exponent: int = DEFAULT_LIQ_EXPONENT,
    price_impact_k: float = DEFAULT_PRICE_IMPACT_K,
) -> dict:
    """
    Run MC simulation for a single parameter combination.

    Args:
        n_paths: total price paths
        ltv: effective LTV
        lock_fraction: position lock fraction
        refresh_interval: oracle refresh interval (seconds)
        decay: oracle EMA decay factor
        jd_params: jump-diffusion calibration parameters
        n_positions: positions per pool
        seed: base RNG seed
        chunk_size: paths per processing chunk
        liq_exponent: partial liquidation exponent (2^-e per step)
        price_impact_k: price haircut on liquidation recovery

    Returns:
        metrics: dict from compute_metrics
        bad_debt_samples: raw (n_paths,) array
        max_drawdowns: (n_paths,) max drawdown per path
        liquidation_delays: list of all delay values (in steps)
    """
    refresh_hours = max(1, int(refresh_interval / HOUR))
    n_chunks = (n_paths + chunk_size - 1) // chunk_size
    all_bad_debts = []
    all_drawdowns = []
    all_delays = []

    # Generate pool once (same across all paths for this parameter set)
    pool = generate_pool(
        n_positions=n_positions,
        ltv=ltv,
        lock_fraction=lock_fraction,
        seed=seed,
    )

    for chunk_idx in range(n_chunks):
        actual_size = min(chunk_size, n_paths - chunk_idx * chunk_size)
        chunk_seed = seed + chunk_idx * 1000

        # Generate hourly prices
        prices = generate_paths(
            n_paths=actual_size,
            n_hours=MC_HOURS_PER_YEAR,
            p0=1.0,
            seed=chunk_seed,
            **jd_params,
        )

        # Subsample to oracle refresh points
        refresh_prices = _subsample_to_refresh_points(prices, refresh_hours)

        # True price ratios (normalize to initial price = 1)
        true_ratios = refresh_prices / refresh_prices[:, 0:1]

        # Run vectorized oracle EMA
        oracle_ratios = run_oracle_over_prices_vectorized(true_ratios, decay)

        # Simulate pool for this chunk
        chunk_result = simulate_pool_batch(
            pool, oracle_ratios, true_ratios,
            liq_exponent=liq_exponent,
            price_impact_k=price_impact_k,
        )
        all_bad_debts.append(chunk_result["bad_debt_pcts"])
        all_drawdowns.append(chunk_result["max_drawdowns"])
        all_delays.extend(chunk_result["liquidation_delays"])

    bad_debt_samples = np.concatenate(all_bad_debts)
    max_drawdowns = np.concatenate(all_drawdowns)
    metrics = compute_metrics(bad_debt_samples)

    return {
        "metrics": metrics,
        "bad_debt_samples": bad_debt_samples,
        "max_drawdowns": max_drawdowns,
        "liquidation_delays": all_delays,
        "params": {
            "ltv": ltv,
            "lock_fraction": lock_fraction,
            "refresh_interval": refresh_interval,
            "decay": decay,
            "price_impact_k": price_impact_k,
        },
    }


def run_mc_sweep(
    n_paths: int = MC_NUM_PATHS,
    ltv_sweep: list[float] = LTV_SWEEP,
    lock_sweep: list[float] = LOCK_FRACTION_SWEEP,
    refresh_sweep: list[float] = REFRESH_INTERVAL_SWEEP,
    alpha_sweep: list[float] = ALPHA_SWEEP,
    jd_params: dict = JD_PARAMS_ETH,
    n_positions: int = MC_NUM_POSITIONS,
    seed: int = MC_SEED,
    chunk_size: int = 10_000,
    verbose: bool = True,
) -> dict:
    """
    Full MC sweep over parameter grid.

    Total combinations: len(ltv) × len(lock) × len(refresh) × len(alpha)
    Default: 4 × 5 × 4 × 3 = 240 combinations.

    Returns:
        results: list of dicts, each containing metrics and params
        summary_table: list of flat dicts for tabulation
    """
    total = len(ltv_sweep) * len(lock_sweep) * len(refresh_sweep) * len(alpha_sweep)
    results = []
    summary = []
    count = 0

    for alpha in alpha_sweep:
        for refresh in refresh_sweep:
            for ltv in ltv_sweep:
                for lock in lock_sweep:
                    count += 1
                    if verbose:
                        print(
                            f"  MC [{count}/{total}]: "
                            f"α={alpha:.4f} Δt={refresh/3600:.1f}h "
                            f"LTV={ltv:.2f} φ={lock:.2f}"
                        )

                    result = run_mc_single(
                        n_paths=n_paths,
                        ltv=ltv,
                        lock_fraction=lock,
                        refresh_interval=refresh,
                        decay=alpha,
                        jd_params=jd_params,
                        n_positions=n_positions,
                        seed=seed,
                        chunk_size=chunk_size,
                    )
                    results.append(result)

                    row = {**result["params"], **result["metrics"]}
                    summary.append(row)

    return {"results": results, "summary": summary}


def run_mc_with_params(
    n_paths: int,
    jd_params: dict,
    seed: int = MC_SEED,
    **kwargs,
) -> dict:
    """Run MC with explicit jump-diffusion parameters (for sensitivity sweeps)."""
    defaults = {
        "ltv": 1 / 3,
        "lock_fraction": 0.0,
        "refresh_interval": 3600.0,
        "decay": 0.5 ** (1 / 12),
        "n_positions": MC_NUM_POSITIONS,
        "chunk_size": 10_000,
        "liq_exponent": DEFAULT_LIQ_EXPONENT,
        "price_impact_k": DEFAULT_PRICE_IMPACT_K,
    }
    defaults.update(kwargs)
    return run_mc_single(
        n_paths=n_paths,
        jd_params=jd_params,
        seed=seed,
        **defaults,
    )


def run_mc_quick(
    n_paths: int = 1_000,
    ltv: float = 1 / 3,
    lock_fraction: float = 0.0,
    refresh_interval: float = 3600.0,
    decay: float = 0.5 ** (1 / 12),
    jd_params: dict = JD_PARAMS_ETH,
    seed: int = MC_SEED,
    verbose: bool = True,
) -> dict:
    """Quick MC run with a single parameter set (for testing/validation)."""
    if verbose:
        print(f"  Quick MC: {n_paths} paths, LTV={ltv:.2f}, α={decay:.4f}")
    return run_mc_single(
        n_paths=n_paths,
        ltv=ltv,
        lock_fraction=lock_fraction,
        refresh_interval=refresh_interval,
        decay=decay,
        jd_params=jd_params,
        seed=seed,
        chunk_size=n_paths,
    )
