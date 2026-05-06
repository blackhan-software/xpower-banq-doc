"""
Protocol constants extracted from Solidity source.
All values use Python float64 semantics (no fixed-point 1e18 scaling).

References:
  source/library/Constant.sol  — time & scale constants
  source/contract/Oracle.sol   — decay constants (lines 250-262)
  source/contract/Pool.sol     — health check, weight application
  test/Pool/Base.t.sol         — default test parameters
  spec/bad-debt-risk-quantification.md — sweep ranges & calibration
"""
import numpy as np

# === Time Constants (from Constant.sol) ===
CENTURY = 365.25 * 24 * 3600        # 31_557_600 seconds
YEAR = CENTURY / 100                # 315_576 seconds -- NOTE: Constant.sol uses CENTURY/100
YEAR_SECONDS = 365.25 * 24 * 3600   # 31_557_600 — for interest accrual
HOUR = 3600
MINUTE = 60

# === Oracle Decay Constants ===
# DECAY_NHL = 0.5^(1/N)  — per-refresh decay for N-refresh half-life
DECAY_06HL = 0.5 ** (1 / 6)    # ~0.8909
DECAY_12HL = 0.5 ** (1 / 12)   # ~0.9439 (default)
DECAY_24HL = 0.5 ** (1 / 24)   # ~0.9715

# === Default Oracle Parameters ===
DEFAULT_DECAY = DECAY_12HL
DEFAULT_REFRESH_INTERVAL = HOUR  # 1 hour in seconds

# === Health Check (from Pool.sol, Weight struct) ===
WEIGHT_MAX = 255
DEFAULT_WEIGHT_SUPPLY = 85    # 85/255 ~ 33.33%
DEFAULT_WEIGHT_BORROW = 255   # 255/255 = 100%
# Effective LTV = w_supply / w_borrow = 85/255 ~ 33.33%
DEFAULT_LTV = DEFAULT_WEIGHT_SUPPLY / DEFAULT_WEIGHT_BORROW

# === Interest Rate Model defaults (from test/Pool/Base.t.sol) ===
DEFAULT_UTIL_OPT = 0.90   # 90% optimal utilization
DEFAULT_RATE_OPT = 0.10   # 10% optimal rate
DEFAULT_SPREAD = 0.00     # 0% spread (test default)

# === Calculator.sol ===
LOG2_ONE = 59.794705707972522245  # log2(1e18) — validation only

# === Sweep Ranges (from spec §5.2) ===
LTV_SWEEP = [1 / 3, 0.50, 2 / 3, 0.75]
LOCK_FRACTION_SWEEP = [0.0, 0.25, 0.50, 0.75, 1.0]
REFRESH_INTERVAL_SWEEP = [900, 1800, 3600, 7200]  # 15m, 30m, 1h, 2h
ALPHA_SWEEP = [DECAY_06HL, DECAY_12HL, DECAY_24HL]

# === Monte Carlo Parameters (from spec §5.2) ===
MC_NUM_PATHS = 100_000
MC_HOURS_PER_YEAR = 8760          # 365 * 24
MC_NUM_POSITIONS = 1_000
MC_SEED = 42

# === Position Distribution (from spec §4.2) ===
HEALTH_MEAN = 1.5
HEALTH_STD = 0.3
HEALTH_MIN = 1.0
HEALTH_MAX = 3.0

# === Jump-Diffusion Calibration (from spec §5.1) ===
JD_PARAMS_ETH = dict(sigma=0.90, lambda_j=6.0, mu_j=-0.15, sigma_j=0.10)
JD_PARAMS_AVAX = dict(sigma=1.20, lambda_j=9.0, mu_j=-0.20, sigma_j=0.15)

# === Crash Magnitudes for §3 Analysis ===
CRASH_MAGNITUDES = [0.20, 0.30, 0.40, 0.50, 0.70]
LAG_REFRESH_COUNT = 72  # 72 hours

# === Historical Crash Events (from spec §4.1) ===
CRASH_EVENTS = [
    {
        "name": "Black Thursday",
        "start": "2020-03-11",
        "end": "2020-03-15",
        "assets": ["ETHUSDT", "AVAXUSDT"],
        "peak_drawdown": 0.43,
        "trough_hours": 26,
    },
    {
        "name": "May 2021 Crash",
        "start": "2021-05-18",
        "end": "2021-05-21",
        "assets": ["ETHUSDT", "AVAXUSDT"],
        "peak_drawdown": 0.40,
        "trough_hours": 8,
    },
    {
        "name": "Terra Contagion",
        "start": "2022-06-10",
        "end": "2022-06-20",
        "assets": ["ETHUSDT", "AVAXUSDT"],
        "peak_drawdown": 0.35,
        "trough_hours": 144,
    },
    {
        "name": "FTX Contagion",
        "start": "2022-11-06",
        "end": "2022-11-12",
        "assets": ["ETHUSDT", "AVAXUSDT"],
        "peak_drawdown": 0.25,
        "trough_hours": 48,
    },
]

# === Additional Sensitivity Parameters (§6.1) ===
PRICE_IMPACT_SWEEP = [0.0, 0.01, 0.02, 0.05, 0.10]  # k: price impact coefficient
JUMP_INTENSITY_SWEEP = [4.0, 6.0, 8.0, 12.0]  # λ_J: jumps per year
DEFAULT_PRICE_IMPACT_K = 0.0
DEFAULT_JUMP_INTENSITY = JD_PARAMS_ETH["lambda_j"]  # 6.0

# === Partial Liquidation (§5.2) ===
DEFAULT_LIQ_EXPONENT = 1  # 2^(-e): fraction retained per liquidation step

# === Risk Thresholds (from spec §9) ===
VAR_CONFIDENCE = 0.99
BAD_DEBT_THRESHOLD = 0.05  # 5% of TVL
CI_TARGET = 0.01           # ±1% of TVL
