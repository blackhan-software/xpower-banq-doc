"""
Section 7: Analytical Bound Derivation

Derives a closed-form upper bound on bad debt as a function of crash
magnitude, oracle decay, and LTV.

Deliverables:
  7. BD_max(δ, α, LTV) ≤ f(δ, α, LTV) × TVL — formula + derivation
  8. 3D safe operating region surface plot

Derivation:
  Consider a step crash of fraction δ at t=0. A position with initial
  health H has:
    H_true = H × (1 - δ)
    H_oracle(n) = H × p̂(n) / p₀

  The position is truly underwater when H × (1 - δ) < 1, i.e., H < 1/(1-δ).
  The oracle triggers liquidation at refresh n* where H × p̂(n*)/p₀ < 1.

  Bad debt per position = max(0, borrow − supply × (1 − δ))
  Since supply = H × borrow / LTV:
    bad_debt = borrow × max(0, 1 − H(1−δ)/LTV)
    bad_debt = borrow × max(0, 1 − H(1−δ)/LTV)

  In the worst case (H → 1/(1−δ), the marginal underwater position):
    bad_debt → borrow × (1 − 1/(LTV×(1−δ)) × (1−δ)/LTV)
    bad_debt → borrow × (1 − 1/LTV)

  But the ADDITIONAL bad debt from oracle lag (beyond instant liquidation)
  is due to interest accrual and further price movement during the phantom
  window. For a static crash (price stays at p₁):

  Oracle-additional bad debt ≈ 0 for static crashes (all positions that
  are underwater get liquidated eventually, same shortfall).

  The risk comes from CONTINUED price decline during the phantom window.
  If price continues falling during the W-hour phantom window, positions
  accumulate MORE bad debt than if liquidated instantly.

References:
  spec/bad-debt-risk-quantification.md §7
"""
import numpy as np
from scipy import stats

from ..config import (
    CRASH_MAGNITUDES,
    ALPHA_SWEEP,
    LTV_SWEEP,
    DEFAULT_DECAY,
    DEFAULT_LTV,
    HEALTH_MEAN,
    HEALTH_STD,
    HEALTH_MIN,
    HEALTH_MAX,
    BAD_DEBT_THRESHOLD,
)
from ..models.oracle import oracle_trajectory_step_crash


def _truncnorm_pdf(x, mu, sigma, lo, hi):
    """Truncated normal PDF."""
    a = (lo - mu) / sigma
    b = (hi - mu) / sigma
    return stats.truncnorm.pdf(x, a, b, loc=mu, scale=sigma)


def _truncnorm_cdf(x, mu, sigma, lo, hi):
    """Truncated normal CDF."""
    a = (lo - mu) / sigma
    b = (hi - mu) / sigma
    return stats.truncnorm.cdf(x, a, b, loc=mu, scale=sigma)


def bad_debt_instant_liquidation(
    crash_frac: float,
    ltv: float,
    mu_h: float = HEALTH_MEAN,
    sigma_h: float = HEALTH_STD,
    lo_h: float = HEALTH_MIN,
    hi_h: float = HEALTH_MAX,
) -> float:
    """
    Expected bad debt (% of TVL) assuming instant liquidation.

    Positions with H < 1/(1-δ) are underwater.
    Bad debt per position = borrow × max(0, 1 - H(1-δ)/LTV)
    Since TVL contribution ∝ supply = H×borrow/LTV, weight by H/LTV.

    Integrate over health distribution:
      E[BD]/TVL = ∫_{1}^{H_crit} [1 - H(1-δ)/LTV] × (H/LTV) / E[H/LTV] × f(H) dH

    Where H_crit = 1/(1-δ) is the underwater threshold.
    """
    h_crit = 1.0 / (1.0 - crash_frac)

    if h_crit <= lo_h:
        return 0.0  # no positions underwater

    # Numerical integration over health distribution
    n_points = 10_000
    h_vals = np.linspace(lo_h, min(h_crit, hi_h), n_points)
    dh = h_vals[1] - h_vals[0] if n_points > 1 else 1.0

    pdf_vals = _truncnorm_pdf(h_vals, mu_h, sigma_h, lo_h, hi_h)

    # Bad debt fraction per position: max(0, 1 - H(1-δ)/LTV)
    # Only for positions with H(1-δ) < LTV (truly have bad debt)
    shortfall = np.maximum(0.0, 1.0 - h_vals * (1.0 - crash_frac) / ltv)

    # Weight by supply contribution: supply = H * borrow / LTV
    # Assuming equal borrow sizes, weight by H
    weighted_shortfall = shortfall * h_vals * pdf_vals

    # Normalize: E[H] for the full distribution
    all_h = np.linspace(lo_h, hi_h, n_points)
    all_pdf = _truncnorm_pdf(all_h, mu_h, sigma_h, lo_h, hi_h)
    e_h = np.trapz(all_h * all_pdf, all_h)

    bd_pct = np.trapz(weighted_shortfall, h_vals) / e_h * 100

    return float(bd_pct)


def phantom_window_refreshes(
    crash_frac: float,
    decay: float,
    initial_health: float,
) -> int:
    """
    Number of refreshes the position remains phantom-healthy.

    Oracle triggers when p̂(n)/p₀ < 1/H.
    Returns n* (first refresh where oracle crosses threshold).
    """
    threshold = 1.0 / initial_health
    trajectory = oracle_trajectory_step_crash(1.0, crash_frac, decay, 500)
    below = trajectory / 1.0 < threshold
    if not below.any():
        return 500
    return int(np.argmax(below))


def bad_debt_with_continued_decline(
    crash_frac: float,
    decay: float,
    ltv: float,
    continued_rate: float = 0.0,
    mu_h: float = HEALTH_MEAN,
    sigma_h: float = HEALTH_STD,
    lo_h: float = HEALTH_MIN,
    hi_h: float = HEALTH_MAX,
) -> float:
    """
    Upper bound on bad debt accounting for continued decline during phantom window.

    If price continues falling at `continued_rate` per hour during the
    phantom window of W hours, the true price at liquidation is:
      p_true(t_liq) = p₁ × (1 - continued_rate)^W

    This makes the shortfall worse:
      bad_debt = borrow × max(0, 1 - H × p_true(t_liq) / LTV)

    For the bound, use the WORST-CASE phantom window (position with H just
    above the underwater threshold, which has the longest phantom window).
    """
    if continued_rate <= 0:
        return bad_debt_instant_liquidation(crash_frac, ltv, mu_h, sigma_h, lo_h, hi_h)

    h_crit = 1.0 / (1.0 - crash_frac)
    if h_crit <= lo_h:
        return 0.0

    n_points = 1_000
    h_vals = np.linspace(lo_h, min(h_crit, hi_h), n_points)
    pdf_vals = _truncnorm_pdf(h_vals, mu_h, sigma_h, lo_h, hi_h)

    total_bd = 0.0
    dh = h_vals[1] - h_vals[0] if n_points > 1 else 1.0

    for i, h in enumerate(h_vals):
        w = phantom_window_refreshes(crash_frac, decay, h)
        p_true_at_liq = (1.0 - crash_frac) * (1.0 - continued_rate) ** w
        shortfall = max(0.0, 1.0 - h * p_true_at_liq / ltv)
        total_bd += shortfall * h * pdf_vals[i] * dh

    all_h = np.linspace(lo_h, hi_h, n_points)
    all_pdf = _truncnorm_pdf(all_h, mu_h, sigma_h, lo_h, hi_h)
    e_h = np.trapz(all_h * all_pdf, all_h)

    return float(total_bd / e_h * 100)


def bad_debt_bound(
    crash_frac: float,
    decay: float,
    ltv: float,
) -> float:
    """
    Conservative upper bound: BD_max(δ, α, LTV).

    Uses instant liquidation as baseline plus a penalty for the phantom
    window. The bound assumes all positions at the underwater threshold
    experience the maximum phantom delay.

    BD_max ≈ BD_instant + (phantom_window_hours / 24) × BD_instant
    This is conservative because it assumes phantom window compounds losses.
    """
    bd_instant = bad_debt_instant_liquidation(crash_frac, ltv)

    # Worst-case phantom window: position with H just above 1/(1-δ)
    h_marginal = min(1.0 / (1.0 - crash_frac) - 0.01, HEALTH_MAX)
    if h_marginal < HEALTH_MIN:
        return bd_instant

    w_max = phantom_window_refreshes(crash_frac, decay, max(h_marginal, HEALTH_MIN + 0.01))

    # Conservative multiplier: assume additional losses proportional to window
    # Each hour of delay allows ~σ_hourly additional price movement
    # σ_hourly ≈ 0.90 / √8760 ≈ 0.0096 (≈1% per hour for ETH)
    sigma_hourly = 0.90 / np.sqrt(8760)
    additional_decline = w_max * sigma_hourly
    bound = bd_instant * (1.0 + additional_decline / max(crash_frac, 0.01))

    return float(bound)


def compute_bound_surface(
    crash_range: np.ndarray = None,
    decay_range: np.ndarray = None,
    ltv_range: np.ndarray = None,
) -> dict:
    """
    Deliverable 8: 3D surface of BD_max over (crash, decay, LTV) space.

    Returns:
        crash_grid, decay_grid, ltv_grid: meshgrid arrays
        bd_surface: 3D array of BD_max values
        safe_region: boolean 3D array (True where BD < threshold)
    """
    if crash_range is None:
        crash_range = np.linspace(0.10, 0.70, 13)
    if decay_range is None:
        decay_range = np.linspace(0.85, 0.98, 14)
    if ltv_range is None:
        ltv_range = np.linspace(0.25, 0.80, 12)

    nc, nd, nl = len(crash_range), len(decay_range), len(ltv_range)
    bd_surface = np.empty((nc, nd, nl))

    for i, δ in enumerate(crash_range):
        for j, α in enumerate(decay_range):
            for k, ltv in enumerate(ltv_range):
                bd_surface[i, j, k] = bad_debt_bound(δ, α, ltv)

    safe_region = bd_surface < BAD_DEBT_THRESHOLD * 100  # threshold is fraction, bd is %

    return {
        "crash_range": crash_range,
        "decay_range": decay_range,
        "ltv_range": ltv_range,
        "bd_surface": bd_surface,
        "safe_region": safe_region,
    }


def find_safe_configurations(
    max_crash: float = 0.50,
    threshold_pct: float = 5.0,
) -> list[dict]:
    """
    Deliverable 9 (partial): Find parameter combinations where
    VaR(99%) < threshold_pct for crashes up to max_crash.

    Uses the analytical bound as a proxy.
    """
    safe = []
    for α in ALPHA_SWEEP:
        for ltv in LTV_SWEEP:
            bd = bad_debt_bound(max_crash, α, ltv)
            if bd < threshold_pct:
                safe.append({
                    "decay": α,
                    "ltv": ltv,
                    "bd_bound_pct": bd,
                    "half_life_hours": np.log(0.5) / np.log(α),
                })
    return safe


def run_all() -> dict:
    """Run all Section 7 analyses."""
    # Bound table for specific crash/LTV combos
    bound_table = []
    for δ in CRASH_MAGNITUDES:
        for ltv in LTV_SWEEP:
            for α in ALPHA_SWEEP:
                bound_table.append({
                    "crash_pct": δ * 100,
                    "ltv": ltv,
                    "decay": α,
                    "bd_instant_pct": bad_debt_instant_liquidation(δ, ltv),
                    "bd_bound_pct": bad_debt_bound(δ, α, ltv),
                })

    return {
        "bound_table": bound_table,
        "surface": compute_bound_surface(),
        "safe_configs": find_safe_configurations(),
    }
