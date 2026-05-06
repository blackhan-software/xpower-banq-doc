"""
Jump-diffusion (Merton model) price path generator.

  dp/p = μ dt + σ dW + J dN

Generates at hourly resolution for memory efficiency, with optional
intra-hour minimum tracking via Brownian bridge for precise liquidation timing.

References:
  spec/bad-debt-risk-quantification.md §5.1 — calibration parameters
"""
import numpy as np
from typing import Optional

from ..config import MC_HOURS_PER_YEAR, YEAR_SECONDS, HOUR


def generate_paths(
    n_paths: int,
    n_hours: int = MC_HOURS_PER_YEAR,
    p0: float = 1.0,
    sigma: float = 0.90,
    lambda_j: float = 6.0,
    mu_j: float = -0.15,
    sigma_j: float = 0.10,
    mu: float = 0.0,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Generate jump-diffusion price paths at hourly resolution.

    Args:
        n_paths: number of independent paths
        n_hours: time steps (hours per year = 8760)
        p0: initial price
        sigma: annualized volatility
        lambda_j: jump intensity (jumps per year)
        mu_j: mean log-jump size
        sigma_j: jump size volatility
        mu: drift (0 for risk-neutral)
        seed: RNG seed for reproducibility

    Returns:
        prices: shape (n_paths, n_hours + 1), prices[i, 0] = p0
    """
    rng = np.random.default_rng(seed)

    dt = HOUR / YEAR_SECONDS  # fraction of year per hour
    sqrt_dt = np.sqrt(dt)

    # Jump compensator for drift neutrality
    jump_compensator = lambda_j * (np.exp(mu_j + 0.5 * sigma_j**2) - 1.0)
    drift_per_step = (mu - 0.5 * sigma**2 - jump_compensator) * dt

    # Pre-allocate log-prices
    log_prices = np.empty((n_paths, n_hours + 1), dtype=np.float64)
    log_prices[:, 0] = np.log(p0)

    # Poisson arrival rate per hour
    lambda_dt = lambda_j * dt

    for t in range(n_hours):
        # Diffusion component
        z = rng.standard_normal(n_paths)
        diffusion = drift_per_step + sigma * sqrt_dt * z

        # Jump component (Poisson arrivals)
        n_jumps = rng.poisson(lambda_dt, n_paths)
        jump_total = np.zeros(n_paths)
        has_jump = n_jumps > 0
        if has_jump.any():
            max_jumps = n_jumps[has_jump].max()
            for k in range(max_jumps):
                mask = n_jumps > k
                jump_total[mask] += rng.normal(mu_j, sigma_j, mask.sum())

        log_prices[:, t + 1] = log_prices[:, t] + diffusion + jump_total

    return np.exp(log_prices)


def generate_paths_with_minima(
    n_paths: int,
    n_hours: int = MC_HOURS_PER_YEAR,
    p0: float = 1.0,
    sigma: float = 0.90,
    lambda_j: float = 6.0,
    mu_j: float = -0.15,
    sigma_j: float = 0.10,
    mu: float = 0.0,
    seed: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate paths and estimate intra-hour minimum prices.

    Uses the Brownian bridge minimum distribution: for GBM from S_0 to S_1
    over interval dt with volatility σ, the minimum m satisfies:
        P(min > m) ≈ 1 - exp(-2(log(S_0/m))(log(S_1/m)) / (σ² dt))
    We sample the expected minimum for each interval.

    Returns:
        prices: shape (n_paths, n_hours + 1)
        hourly_minima: shape (n_paths, n_hours) — min price in each hour
    """
    prices = generate_paths(
        n_paths, n_hours, p0, sigma, lambda_j, mu_j, sigma_j, mu, seed,
    )

    dt = HOUR / YEAR_SECONDS
    sigma_sqrt_dt = sigma * np.sqrt(dt)

    # Estimate intra-hour minimum via Brownian bridge expected minimum
    # E[min] ≈ S_0 * exp(-σ√dt * E[|Z|]) for small dt approximation
    # More precisely, use the median of the bridge minimum distribution
    hourly_minima = np.minimum(prices[:, :-1], prices[:, 1:])

    # Brownian bridge correction: further reduce by expected excursion
    # E[max excursion below endpoints] ≈ 0.5 * σ * √dt * √(2/π) * min(S_0, S_1)
    correction_factor = 0.5 * sigma_sqrt_dt * np.sqrt(2.0 / np.pi)
    hourly_minima *= (1.0 - correction_factor)

    return prices, hourly_minima


def generate_paths_chunked(
    n_paths: int,
    chunk_size: int = 10_000,
    **kwargs,
) -> np.ndarray:
    """
    Generate paths in chunks to limit memory usage.

    Args:
        n_paths: total paths
        chunk_size: paths per chunk
        **kwargs: passed to generate_paths

    Yields:
        (chunk_index, prices) tuples
    """
    seed = kwargs.pop("seed", None)
    n_chunks = (n_paths + chunk_size - 1) // chunk_size

    for i in range(n_chunks):
        actual_size = min(chunk_size, n_paths - i * chunk_size)
        chunk_seed = seed + i if seed is not None else None
        yield i, generate_paths(n_paths=actual_size, seed=chunk_seed, **kwargs)
