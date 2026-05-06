"""
Historical price data fetcher.

Downloads minute-level OHLCV from Binance public API (no key required).
Caches results as CSV for reproducibility.

References:
  spec/bad-debt-risk-quantification.md §4.1 — crash events and data sources
"""
import time
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ..config import CRASH_EVENTS

CACHE_DIR = Path(__file__).parent / "cache"
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
BINANCE_LIMIT = 1000  # max candles per request


def _ts_ms(date_str: str) -> int:
    """Convert YYYY-MM-DD to millisecond timestamp."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def _cache_path(symbol: str, start: str, end: str) -> Path:
    """Cache file path for a (symbol, start, end) query."""
    return CACHE_DIR / f"{symbol}_{start}_{end}.csv"


def fetch_binance_klines(
    symbol: str,
    start: str,
    end: str,
    interval: str = "1m",
) -> np.ndarray:
    """
    Download minute-level klines from Binance public API.

    Args:
        symbol: e.g. "ETHUSDT"
        start: "YYYY-MM-DD"
        end: "YYYY-MM-DD"
        interval: candle interval (default "1m")

    Returns:
        ndarray with columns: [timestamp_s, open, high, low, close, volume]
    """
    if not HAS_REQUESTS:
        raise ImportError("requests package required for data download: pip install requests")

    cache = _cache_path(symbol, start, end)
    if cache.exists():
        data = np.loadtxt(cache, delimiter=",", skiprows=1)
        if len(data) > 0:
            return data

    start_ms = _ts_ms(start)
    end_ms = _ts_ms(end)
    all_rows = []

    current_ms = start_ms
    while current_ms < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_ms,
            "endTime": end_ms,
            "limit": BINANCE_LIMIT,
        }
        resp = requests.get(BINANCE_KLINES_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break

        for row in data:
            all_rows.append([
                row[0] / 1000,    # timestamp (seconds)
                float(row[1]),    # open
                float(row[2]),    # high
                float(row[3]),    # low
                float(row[4]),    # close
                float(row[5]),    # volume
            ])

        current_ms = int(data[-1][0]) + 60_000  # next minute
        time.sleep(0.1)  # rate limit courtesy

    result = np.array(all_rows)

    # Cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    header = "timestamp_s,open,high,low,close,volume"
    np.savetxt(cache, result, delimiter=",", header=header, comments="")

    return result


def load_crash_prices(
    event_index: int = 0,
    asset_index: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load minute-level close prices for a crash event.

    Returns:
        timestamps: (n_minutes,) UTC timestamps in seconds
        prices: (n_minutes,) close prices
    """
    event = CRASH_EVENTS[event_index]
    symbol = event["assets"][asset_index]
    data = fetch_binance_klines(symbol, event["start"], event["end"])
    return data[:, 0], data[:, 4]  # timestamps, close prices


def load_all_crash_data() -> dict:
    """
    Load all crash event data. Returns dict keyed by event name.
    Each value is dict with 'timestamps', 'prices', 'symbol'.
    """
    results = {}
    for i, event in enumerate(CRASH_EVENTS):
        symbol = event["assets"][0]  # primary asset (ETH)
        try:
            timestamps, prices = load_crash_prices(i, 0)
            results[event["name"]] = {
                "timestamps": timestamps,
                "prices": prices,
                "symbol": symbol,
                "event": event,
            }
        except Exception as e:
            print(f"Warning: could not load {event['name']} ({symbol}): {e}")
    return results
