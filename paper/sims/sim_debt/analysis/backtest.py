"""
Section 4: Historical Backtesting

Replays minute-level price data through the oracle model with synthetic
position pools, tracking phantom-healthy windows and bad debt accumulation.

Deliverables:
  3. Per-event bad debt as % of TVL, for each (LTV, φ) combination
     Cumulative bad debt timeline charts with oracle vs true price overlay

References:
  spec/bad-debt-risk-quantification.md §4.2-4.3
"""
import numpy as np

from ..config import (
    DEFAULT_DECAY,
    DEFAULT_REFRESH_INTERVAL,
    LTV_SWEEP,
    LOCK_FRACTION_SWEEP,
    MC_NUM_POSITIONS,
    MINUTE,
    HOUR,
)
from ..models.oracle import OracleModel
from ..models.position import generate_pool


def _run_oracle_over_minutes(
    prices: np.ndarray,
    timestamps: np.ndarray,
    decay: float,
    refresh_interval: float,
    spread: float = 0.001,
) -> np.ndarray:
    """
    Run oracle model over minute-level price data.

    Returns oracle-reported prices at each minute (same length as prices).
    Only refreshes when refresh_interval has elapsed.
    """
    n = len(prices)
    oracle = OracleModel(decay=decay, refresh_interval=refresh_interval)
    oracle_prices = np.empty(n)

    for t in range(n):
        ts = timestamps[t] if timestamps is not None else (t + 1) * MINUTE
        if oracle.state is None:
            oracle.init(prices[t], spread, ts)
        else:
            oracle.refresh(prices[t], spread, ts)
        oracle_prices[t] = oracle.get_oracle_price()

    return oracle_prices


def run_single_backtest(
    prices: np.ndarray,
    timestamps: np.ndarray,
    decay: float = DEFAULT_DECAY,
    refresh_interval: float = DEFAULT_REFRESH_INTERVAL,
    ltv: float = 1 / 3,
    lock_fraction: float = 0.0,
    n_positions: int = MC_NUM_POSITIONS,
    seed: int = 42,
) -> dict:
    """
    Run backtest for one crash event with one parameter set.

    Args:
        prices: minute-level close prices
        timestamps: UTC timestamps (seconds)
        decay: oracle EMA decay
        refresh_interval: oracle refresh interval (seconds)
        ltv: effective LTV
        lock_fraction: fraction of positions locked
        n_positions: synthetic positions
        seed: RNG seed

    Returns dict with:
        - oracle_prices: oracle-reported prices at each minute
        - true_prices: actual market prices
        - price_ratio_initial: prices / prices[0]
        - oracle_ratio_initial: oracle / oracle[0]
        - bad_debt_timeline: bad debt as % of TVL at each minute
        - cumulative_bad_debt: cumulative bad debt %
        - phantom_count: phantom-healthy positions at each minute
        - total_bad_debt_pct: final total bad debt as % of TVL
        - liquidation_delays: delays (minutes) between true-underwater and oracle-trigger
    """
    n_minutes = len(prices)

    # Run oracle
    oracle_prices = _run_oracle_over_minutes(
        prices, timestamps, decay, refresh_interval,
    )

    # Normalize to ratios (initial price = 1)
    p0 = prices[0]
    true_ratios = prices / p0
    oracle_ratios = oracle_prices / oracle_prices[0]

    # Generate pool
    pool = generate_pool(
        n_positions=n_positions,
        ltv=ltv,
        lock_fraction=lock_fraction,
        seed=seed,
    )

    p_crit = pool["p_critical"]       # (n_pos,)
    supply = pool["supply"]           # (n_pos,)
    borrow = pool["borrow"]           # (n_pos,)
    n_pos = pool["n"]
    tvl = supply.sum()

    # Track state per position
    alive = np.ones(n_pos, dtype=bool)
    time_true_under = np.full(n_pos, -1, dtype=np.int64)
    bad_debt_timeline = np.zeros(n_minutes)
    phantom_count = np.zeros(n_minutes, dtype=np.int64)
    delays = []

    for t in range(n_minutes):
        if not alive.any():
            break

        oracle_r = oracle_ratios[t]
        true_r = true_ratios[t]

        alive_idx = np.where(alive)[0]

        # True health check
        truly_under = true_r < p_crit[alive_idx]
        # Oracle health check
        oracle_under = oracle_r < p_crit[alive_idx]

        # Track first time truly underwater
        newly_under = truly_under & (time_true_under[alive_idx] < 0)
        time_true_under[alive_idx[newly_under]] = t

        # Phantom healthy: oracle says OK but truly underwater
        phantom = truly_under & ~oracle_under
        phantom_count[t] = int(phantom.sum())

        # Liquidation trigger: oracle says underwater
        to_liquidate = oracle_under
        if to_liquidate.any():
            liq_positions = alive_idx[to_liquidate]

            # Bad debt at liquidation
            shortfall = borrow[liq_positions] - supply[liq_positions] * true_r
            bad_debt = np.maximum(0.0, shortfall)
            bad_debt_timeline[t] = bad_debt.sum()

            # Liquidation delays
            for pos_idx in liq_positions:
                if time_true_under[pos_idx] >= 0:
                    delays.append(t - time_true_under[pos_idx])

            alive[liq_positions] = False

    # Handle positions still alive but truly underwater at end
    still_alive_under = alive & (true_ratios[-1] < p_crit)
    if still_alive_under.any():
        shortfall = borrow[still_alive_under] - supply[still_alive_under] * true_ratios[-1]
        bad_debt_timeline[-1] += np.maximum(0.0, shortfall).sum()

    cumulative = np.cumsum(bad_debt_timeline) / tvl * 100 if tvl > 0 else np.zeros(n_minutes)

    return {
        "oracle_prices": oracle_prices,
        "true_prices": prices,
        "price_ratio": true_ratios,
        "oracle_ratio": oracle_ratios,
        "bad_debt_timeline": bad_debt_timeline / tvl * 100 if tvl > 0 else bad_debt_timeline,
        "cumulative_bad_debt": cumulative,
        "phantom_count": phantom_count,
        "total_bad_debt_pct": cumulative[-1] if len(cumulative) > 0 else 0.0,
        "liquidation_delays_minutes": delays,
        "n_positions": n_pos,
        "ltv": ltv,
        "lock_fraction": lock_fraction,
    }


def run_event_sweep(
    prices: np.ndarray,
    timestamps: np.ndarray,
    event_name: str,
    decay: float = DEFAULT_DECAY,
    refresh_interval: float = DEFAULT_REFRESH_INTERVAL,
    ltv_sweep: list[float] = LTV_SWEEP,
    lock_sweep: list[float] = LOCK_FRACTION_SWEEP,
    n_positions: int = MC_NUM_POSITIONS,
    seed: int = 42,
) -> dict:
    """
    Run backtest sweep over all (LTV, lock_fraction) combinations for one event.

    Returns:
        summary: list of dicts with (event, ltv, lock, total_bad_debt_pct, ...)
        details: nested dict [ltv][lock] → full backtest result
    """
    summary = []
    details = {}

    for ltv in ltv_sweep:
        details[ltv] = {}
        for φ in lock_sweep:
            result = run_single_backtest(
                prices=prices,
                timestamps=timestamps,
                decay=decay,
                refresh_interval=refresh_interval,
                ltv=ltv,
                lock_fraction=φ,
                n_positions=n_positions,
                seed=seed,
            )
            details[ltv][φ] = result
            summary.append({
                "event": event_name,
                "ltv": ltv,
                "lock_fraction": φ,
                "total_bad_debt_pct": result["total_bad_debt_pct"],
                "n_liquidated": len(result["liquidation_delays_minutes"]),
                "mean_delay_min": (
                    np.mean(result["liquidation_delays_minutes"])
                    if result["liquidation_delays_minutes"]
                    else 0.0
                ),
                "max_phantom": int(result["phantom_count"].max()),
            })

    return {"summary": summary, "details": details}


def run_all_backtests(
    crash_data: dict,
    decay: float = DEFAULT_DECAY,
    refresh_interval: float = DEFAULT_REFRESH_INTERVAL,
    ltv_sweep: list[float] = LTV_SWEEP,
    lock_sweep: list[float] = LOCK_FRACTION_SWEEP,
    n_positions: int = MC_NUM_POSITIONS,
    seed: int = 42,
) -> dict:
    """
    Run backtests for all crash events.

    Args:
        crash_data: dict from data.fetch.load_all_crash_data()

    Returns:
        all_summaries: list of summary dicts across all events
        per_event: dict[event_name] → full sweep result
    """
    all_summaries = []
    per_event = {}

    for event_name, data in crash_data.items():
        print(f"  Backtesting: {event_name} ({data['symbol']})...")
        result = run_event_sweep(
            prices=data["prices"],
            timestamps=data["timestamps"],
            event_name=event_name,
            decay=decay,
            refresh_interval=refresh_interval,
            ltv_sweep=ltv_sweep,
            lock_sweep=lock_sweep,
            n_positions=n_positions,
            seed=seed,
        )
        all_summaries.extend(result["summary"])
        per_event[event_name] = result

    return {"summaries": all_summaries, "per_event": per_event}
