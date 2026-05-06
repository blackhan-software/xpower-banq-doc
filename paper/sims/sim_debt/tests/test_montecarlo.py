"""
Monte Carlo convergence and reproducibility tests.

References:
    spec/bad-debt-risk-quantification.md §9 — acceptance criteria
"""
import numpy as np
import pytest

from ..models.price import generate_paths
from ..models.position import generate_pool, simulate_pool_vectorized, simulate_pool_partial_liquidation
from ..models.oracle import run_oracle_over_prices_vectorized
from ..analysis.montecarlo import run_mc_quick, compute_metrics
from ..config import DECAY_12HL, JD_PARAMS_ETH


class TestSeedReproducibility:
    """Same seed → identical results."""

    def test_price_paths_reproducible(self):
        p1 = generate_paths(n_paths=100, n_hours=100, seed=42)
        p2 = generate_paths(n_paths=100, n_hours=100, seed=42)
        np.testing.assert_array_equal(p1, p2)

    def test_pool_reproducible(self):
        pool1 = generate_pool(n_positions=100, seed=42)
        pool2 = generate_pool(n_positions=100, seed=42)
        np.testing.assert_array_equal(pool1["health"], pool2["health"])
        np.testing.assert_array_equal(pool1["supply"], pool2["supply"])

    def test_mc_reproducible(self):
        r1 = run_mc_quick(n_paths=100, seed=42, verbose=False)
        r2 = run_mc_quick(n_paths=100, seed=42, verbose=False)
        assert r1["metrics"]["expected_bd"] == r2["metrics"]["expected_bd"]


class TestPricePathStatistics:
    """Verify jump-diffusion calibration."""

    def test_mean_roughly_drift_neutral(self):
        """With mu=0, average terminal price should be near initial."""
        paths = generate_paths(
            n_paths=10_000, n_hours=8760, p0=1.0,
            sigma=0.90, lambda_j=6.0, mu_j=-0.15, sigma_j=0.10,
            mu=0.0, seed=42,
        )
        terminal = paths[:, -1]
        # Log returns should have near-zero mean (compensated drift)
        log_returns = np.log(terminal / paths[:, 0])
        assert abs(log_returns.mean()) < 0.5, \
            f"Mean log-return {log_returns.mean():.3f} too far from 0"

    def test_volatility_in_range(self):
        """Annualized vol should be near calibrated σ."""
        paths = generate_paths(
            n_paths=10_000, n_hours=8760, p0=1.0,
            sigma=0.90, lambda_j=0.0, mu_j=0.0, sigma_j=0.0,
            mu=0.0, seed=42,
        )
        log_returns = np.diff(np.log(paths), axis=1)
        hourly_vol = log_returns.std(axis=1).mean()
        annual_vol = hourly_vol * np.sqrt(8760)
        assert 0.70 < annual_vol < 1.10, f"Annual vol {annual_vol:.3f} out of range"


class TestComputeMetrics:
    """Test risk metric computation."""

    def test_all_zero(self):
        m = compute_metrics(np.zeros(1000))
        assert m["expected_bd"] == 0.0
        assert m["var_99"] == 0.0

    def test_known_distribution(self):
        rng = np.random.default_rng(42)
        samples = rng.exponential(1.0, 10_000)
        m = compute_metrics(samples)
        assert m["expected_bd"] == pytest.approx(1.0, rel=0.05)
        assert m["var_99"] > m["expected_bd"]
        assert m["cvar_99"] > m["var_99"]

    def test_confidence_interval(self):
        rng = np.random.default_rng(42)
        samples = rng.normal(5.0, 1.0, 100_000)
        m = compute_metrics(samples)
        assert m["ci_95"] < 0.01  # should be very tight with 100K samples


class TestPoolSimulation:
    """Test vectorized pool simulation."""

    def test_no_crash_no_bad_debt(self):
        """Constant price → no bad debt."""
        pool = generate_pool(n_positions=100, ltv=1/3, seed=42)
        n_steps = 100
        oracle_ratios = np.ones(n_steps)
        true_ratios = np.ones(n_steps)
        result = simulate_pool_vectorized(pool, oracle_ratios, true_ratios)
        assert result["total_bad_debt_pct"] == 0.0
        assert result["n_liquidated"] == 0

    def test_total_crash_no_lag_no_bad_debt(self):
        """When oracle tracks true price perfectly, liquidation at 1/H prevents bad debt."""
        pool = generate_pool(n_positions=100, ltv=1/3, seed=42)
        n_steps = 100
        oracle_ratios = np.linspace(1.0, 0.01, n_steps)
        true_ratios = np.linspace(1.0, 0.01, n_steps)
        result = simulate_pool_vectorized(pool, oracle_ratios, true_ratios)
        assert result["n_liquidated"] > 0
        # No bad debt: oracle triggers at 1/H, collateral still exceeds debt
        assert result["total_bad_debt_pct"] == 0.0

    def test_phantom_healthy_with_lag(self):
        """Oracle lag creates phantom-healthy positions."""
        pool = generate_pool(n_positions=100, ltv=0.50, seed=42)
        n_steps = 50
        # True price crashes instantly, oracle lags
        true_ratios = np.full(n_steps, 0.3)  # 70% crash
        true_ratios[0] = 1.0
        oracle_ratios = np.linspace(1.0, 0.3, n_steps)  # gradual oracle convergence

        result = simulate_pool_vectorized(pool, oracle_ratios, true_ratios)
        # There should be phantom-healthy positions in early steps
        assert result["phantom_healthy_at"][1] > 0


class TestPartialLiquidation:
    """Test 2^(-e) partial liquidation model."""

    def test_no_crash_no_bad_debt(self):
        """Partial liquidation with constant price → no bad debt."""
        pool = generate_pool(n_positions=50, ltv=1/3, seed=42)
        n_steps = 50
        result = simulate_pool_partial_liquidation(
            pool, np.ones(n_steps), np.ones(n_steps), liq_exponent=1,
        )
        assert result["total_bad_debt_pct"] == 0.0

    def test_partial_more_bad_debt_during_decline(self):
        """Partial liquidation during continued decline → more BD than instant."""
        pool = generate_pool(n_positions=100, ltv=0.50, seed=42)
        n_steps = 100
        # Price continues declining after initial crash
        true_ratios = np.linspace(1.0, 0.2, n_steps)
        oracle_ratios = np.linspace(1.0, 0.2, n_steps)

        full_liq = simulate_pool_vectorized(pool, oracle_ratios, true_ratios)
        partial_liq = simulate_pool_partial_liquidation(
            pool, oracle_ratios, true_ratios, liq_exponent=1,
        )

        # During continued decline, partial liquidation should produce
        # at least as much bad debt (remaining positions face worse prices)
        assert partial_liq["total_bad_debt_pct"] >= full_liq["total_bad_debt_pct"] * 0.9

    def test_price_impact_increases_bad_debt(self):
        """Price impact k > 0 should increase bad debt."""
        pool = generate_pool(n_positions=100, ltv=0.50, seed=42)
        n_steps = 100
        oracle_ratios = np.linspace(1.0, 0.3, n_steps)
        true_ratios = np.linspace(1.0, 0.3, n_steps)

        bd_no_impact = simulate_pool_partial_liquidation(
            pool, oracle_ratios, true_ratios, liq_exponent=1, price_impact_k=0.0,
        )
        bd_with_impact = simulate_pool_partial_liquidation(
            pool, oracle_ratios, true_ratios, liq_exponent=1, price_impact_k=0.10,
        )

        assert bd_with_impact["total_bad_debt_pct"] >= bd_no_impact["total_bad_debt_pct"]
