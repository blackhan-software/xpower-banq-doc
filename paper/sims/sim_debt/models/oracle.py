"""
TWAP Oracle model — exact replica of source/library/TWAP.sol (lines 35-54).

Critical one-refresh-delay semantic:
  The EMA blends `mean` with `last` (PREVIOUS observation), NOT the current
  `next`. The current observation is stored as `last` and only enters the
  mean on the FOLLOWING refresh.

  After a step crash at t=0:
    refresh 1: mean = mean*α + last*(1-α)  where last = pre-crash price
               then last := crash_price
    refresh 2: mean = mean*α + last*(1-α)  where last = crash_price  ← first tracking
    refresh n: convergence continues geometrically in log₂ space

All internal state is in log₂ space (matching Solidity Quote.mid = log₂(price)).
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class Quote:
    """Log₂-space quote (mirrors Solidity Quote struct)."""
    mid: float  # log₂(price)
    rel: float  # log₂(1 + geomean_spread)
    utc: float  # timestamp (seconds)


@dataclass
class TWAPState:
    """Mirrors Solidity TWAP struct: {last, mean}."""
    last: Quote
    mean: Quote


class OracleModel:
    """
    Simulates the XPower Banq TWAP oracle.

    Parameters:
        decay: EMA decay factor per refresh (e.g. 0.9439 for DECAY_12HL)
        refresh_interval: minimum seconds between refreshes (default 3600)
    """

    def __init__(self, decay: float, refresh_interval: float = 3600.0):
        self.decay = decay
        self.refresh_interval = refresh_interval
        self.state: Optional[TWAPState] = None
        self.last_refresh_time: float = -np.inf

    def init(self, price: float, spread: float, timestamp: float) -> None:
        """Initialize oracle with first observation (mirrors TWAPLib.init)."""
        q = Quote(
            mid=np.log2(price),
            rel=np.log2(1.0 + spread),
            utc=timestamp,
        )
        self.state = TWAPState(
            last=Quote(mid=q.mid, rel=q.rel, utc=q.utc),
            mean=Quote(mid=q.mid, rel=q.rel, utc=q.utc),
        )
        self.last_refresh_time = timestamp

    def refresh(self, price: float, spread: float, timestamp: float) -> bool:
        """
        Attempt a TWAP refresh. Returns True if refresh occurred.

        Replicates TWAP.sol update() exactly:
          1. Blend mean with PREVIOUS last (not current next)
          2. Store current observation as new last
        """
        if timestamp < self.last_refresh_time + self.refresh_interval:
            return False

        next_q = Quote(
            mid=np.log2(price),
            rel=np.log2(1.0 + spread),
            utc=timestamp,
        )

        if self.state is None:
            self.init(price, spread, timestamp)
            return True

        if next_q.utc > self.state.last.utc:
            # EMA update: blend mean with PREVIOUS last
            α = self.decay
            if self.state.mean.utc == 0:
                self.state.mean.mid = next_q.mid
                self.state.mean.rel = next_q.rel
            else:
                self.state.mean.mid = (
                    self.state.mean.mid * α
                    + self.state.last.mid * (1.0 - α)
                )
                self.state.mean.rel = (
                    self.state.mean.rel * α
                    + self.state.last.rel * (1.0 - α)
                )
            self.state.mean.utc = next_q.utc

        # Store current observation as last
        self.state.last = next_q
        self.last_refresh_time = timestamp
        return True

    def get_oracle_price(self) -> float:
        """Oracle-reported mid price in linear space: 2^(mean.mid)."""
        if self.state is None:
            return 0.0
        return 2.0 ** self.state.mean.mid

    def get_log2_mid(self) -> float:
        """Raw mean.mid in log₂ space."""
        if self.state is None:
            return 0.0
        return self.state.mean.mid

    def reset(self) -> None:
        """Clear oracle state."""
        self.state = None
        self.last_refresh_time = -np.inf


# ── Analytical helpers ──────────────────────────────────────────────


def oracle_trajectory_step_crash(
    p0: float,
    crash_frac: float,
    decay: float,
    n_refreshes: int,
) -> np.ndarray:
    """
    Analytical oracle price trajectory after an instantaneous step crash.

    The price drops from p0 to p0*(1 - crash_frac) at t=0. Returns the
    oracle-reported price after each of n=0..n_refreshes refreshes.

    Accounts for the one-refresh delay: at refresh 1, the mean still blends
    with the pre-crash `last`; crash price enters mean starting at refresh 2.
    """
    p1 = p0 * (1.0 - crash_frac)
    log_p0 = np.log2(p0)
    log_p1 = np.log2(p1)

    prices = np.empty(n_refreshes + 1)
    mean_mid = log_p0
    last_mid = log_p0  # pre-crash

    for n in range(n_refreshes + 1):
        if n == 0:
            # Initial state: oracle reports pre-crash price, no EMA update
            prices[0] = 2.0 ** mean_mid
            continue

        # EMA update: blend mean with PREVIOUS last, then update last
        mean_mid = mean_mid * decay + last_mid * (1.0 - decay)
        last_mid = log_p1  # crash price is now the observed value

        # Oracle reports price AFTER EMA update
        prices[n] = 2.0 ** mean_mid

    return prices


def oracle_deviation_table(
    crash_magnitudes: np.ndarray,
    n_refreshes: int,
    decay: float,
) -> np.ndarray:
    """
    Compute oracle deviation (%) for each (crash_magnitude, refresh_count).

    Returns shape (len(crash_magnitudes), n_refreshes + 1) where each entry
    is the percentage of the crash already absorbed by the oracle:
        absorbed[i, n] = 1 - (oracle_price[n] - p1) / (p0 - p1)
    """
    p0 = 1.0
    table = np.empty((len(crash_magnitudes), n_refreshes + 1))

    for i, δ in enumerate(crash_magnitudes):
        trajectory = oracle_trajectory_step_crash(p0, δ, decay, n_refreshes)
        p1 = p0 * (1.0 - δ)
        if p0 == p1:
            table[i, :] = 1.0
        else:
            table[i, :] = 1.0 - (trajectory - p1) / (p0 - p1)

    return table


def run_oracle_over_prices(
    prices: np.ndarray,
    decay: float,
    refresh_interval: float,
    warmup: int = 3,
    spread: float = 0.001,
) -> np.ndarray:
    """
    Run the oracle model over a price time-series sampled at refresh_interval.

    Args:
        prices: 1D array of market prices at each refresh point
        decay: EMA decay factor
        refresh_interval: seconds between samples (for timestamp generation)
        warmup: number of initial refreshes before tracking starts
        spread: fixed spread for all observations

    Returns:
        oracle_prices: 1D array of oracle-reported prices (same length as prices)
    """
    n = len(prices)
    oracle = OracleModel(decay=decay, refresh_interval=refresh_interval)
    oracle_prices = np.empty(n)

    for t in range(n):
        ts = (t + 1) * refresh_interval
        if oracle.state is None:
            oracle.init(prices[t], spread, ts)
        else:
            oracle.refresh(prices[t], spread, ts)
        oracle_prices[t] = oracle.get_oracle_price()

    return oracle_prices


def run_oracle_over_prices_vectorized(
    price_matrix: np.ndarray,
    decay: float,
) -> np.ndarray:
    """
    Vectorized oracle EMA over multiple price paths simultaneously.

    Args:
        price_matrix: shape (n_paths, n_steps) — market prices at each refresh
        decay: EMA decay factor

    Returns:
        oracle_matrix: shape (n_paths, n_steps) — oracle-reported prices

    The vectorized EMA in log₂ space:
        log_mean[t] = log_mean[t-1] * α + log_last[t-1] * (1-α)
        log_last[t] = log₂(price[t])
    """
    n_paths, n_steps = price_matrix.shape
    log_prices = np.log2(price_matrix)

    log_mean = np.empty_like(log_prices)
    log_last = np.empty((n_paths,))

    # Initialize: first observation sets both mean and last
    log_mean[:, 0] = log_prices[:, 0]
    log_last[:] = log_prices[:, 0]

    α = decay
    one_minus_α = 1.0 - decay

    for t in range(1, n_steps):
        # EMA update: blend mean with PREVIOUS last
        log_mean[:, t] = log_mean[:, t - 1] * α + log_last * one_minus_α
        # Store current observation as new last
        log_last[:] = log_prices[:, t]

    return np.power(2.0, log_mean)
