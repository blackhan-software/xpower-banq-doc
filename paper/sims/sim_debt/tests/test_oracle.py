"""
Cross-validate Python oracle model against Solidity OracleScenario tests.

Verifies exact replication of TWAP.sol EMA update semantics including
the one-refresh-delay behavior.

References:
    test/Oracle/OracleScenario.t.sol — S02_suddenDrift, S04_suddenReversal
    source/library/TWAP.sol lines 35-54
"""
import numpy as np
import pytest

from ..config import DECAY_12HL, HOUR
from ..models.oracle import (
    OracleModel,
    oracle_trajectory_step_crash,
    oracle_deviation_table,
    run_oracle_over_prices_vectorized,
)


class TestOracleS02SuddenDrift:
    """
    Cross-validate against OracleScenario.t.sol test_S02_suddenDrift.

    Setup:
      - DECAY_12HL (α ≈ 0.9439)
      - 1-hour refresh
      - 3 warmup refreshes at price=1.0
      - Then sustained 2x price jump

    Assertions from Solidity test:
      - After tick 4 (1st refresh post-jump): delta < 3%
      - After tick 5 (2nd refresh): delta < 15%
      - After tick 6 (3rd refresh): delta > 0
      - After tick 17 (14th refresh): 15% < delta < 70%
    """

    def setup_method(self):
        self.oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)

        # Warmup: ticks 1, 2, 3 at price=1.0
        self.oracle.init(1.0, 0.001, HOUR * 1)
        self.oracle.refresh(1.0, 0.001, HOUR * 2)
        self.oracle.refresh(1.0, 0.001, HOUR * 3)
        self.baseline = self.oracle.get_oracle_price()

    def _pct_delta(self, a, b):
        """Percentage delta matching Solidity _pctDelta."""
        if a == 0:
            return 0
        return abs(b - a) / a

    def test_1st_refresh_dampened(self):
        """After tick 4 (1st refresh post-2x-jump): delta < 3%."""
        self.oracle.refresh(2.0, 0.001, HOUR * 4)
        delta = self._pct_delta(self.baseline, self.oracle.get_oracle_price())
        assert delta < 0.03, f"S02: 1st refresh delta={delta:.4f} >= 3%"

    def test_2nd_refresh_dampened(self):
        """After tick 5 (2nd refresh): delta < 15%."""
        self.oracle.refresh(2.0, 0.001, HOUR * 4)
        self.oracle.refresh(2.0, 0.001, HOUR * 5)
        delta = self._pct_delta(self.baseline, self.oracle.get_oracle_price())
        assert delta < 0.15, f"S02: 2nd refresh delta={delta:.4f} >= 15%"

    def test_3rd_refresh_shows_effect(self):
        """After tick 6 (3rd refresh): delta > 0."""
        self.oracle.refresh(2.0, 0.001, HOUR * 4)
        self.oracle.refresh(2.0, 0.001, HOUR * 5)
        self.oracle.refresh(2.0, 0.001, HOUR * 6)
        delta = self._pct_delta(self.baseline, self.oracle.get_oracle_price())
        assert delta > 0, f"S02: 3rd refresh delta={delta:.6f} <= 0"

    def test_14th_refresh_partial_absorption(self):
        """After tick 17 (14th refresh): 15% < delta < 70%."""
        for h in range(4, 18):
            self.oracle.refresh(2.0, 0.001, HOUR * h)
        delta = self._pct_delta(self.baseline, self.oracle.get_oracle_price())
        assert delta > 0.15, f"S02: 14th refresh delta={delta:.4f} <= 15%"
        assert delta < 0.70, f"S02: 14th refresh delta={delta:.4f} >= 70%"


class TestOracleS04SuddenReversal:
    """
    Cross-validate against test_S04_suddenReversal.

    NOTE: In Solidity, the `delayed()` modifier with LIMIT_ID = 1 hour uses
    strict `>` comparison, so with exact hourly ticks only every OTHER tick
    produces a Refresh (alternating Pending/Refresh pattern). The Solidity
    test achieves 3.74% residual with effectively 1 spike + 2 revert refreshes.

    The Python model processes every refresh attempt, so it does 2 spike +
    4 revert refreshes, producing ~6.6% residual. Both are correct for their
    respective refresh cadences.
    """

    def setup_method(self):
        self.oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)
        self.oracle.init(1.0, 0.001, HOUR * 1)
        self.oracle.refresh(1.0, 0.001, HOUR * 2)
        self.oracle.refresh(1.0, 0.001, HOUR * 3)
        self.baseline = self.oracle.get_oracle_price()

    def test_reversal_recovers(self):
        """After spike+reversal, residual < 7% (Python model, all ticks refresh)."""
        # Spike
        self.oracle.refresh(2.0, 0.001, HOUR * 4)
        self.oracle.refresh(2.0, 0.001, HOUR * 5)
        # Reversal
        self.oracle.refresh(1.0, 0.001, HOUR * 6)
        self.oracle.refresh(1.0, 0.001, HOUR * 7)
        self.oracle.refresh(1.0, 0.001, HOUR * 8)
        self.oracle.refresh(1.0, 0.001, HOUR * 9)

        delta = abs(self.oracle.get_oracle_price() - self.baseline) / self.baseline
        assert delta < 0.07, f"S04: residual={delta:.4f} >= 7%"

    def test_reversal_solidity_cadence(self):
        """Match Solidity's effective cadence: every 2nd tick refreshes.
        Solidity result: ~3.74% residual < 5%."""
        oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)
        oracle.init(1.0, 0.001, HOUR * 2)  # tick 2 = first Refresh

        # tick 4 = spike Refresh (tick 3 is Pending in Solidity)
        oracle.refresh(2.0, 0.001, HOUR * 4)
        # tick 6 = revert Refresh (tick 5 is Pending)
        oracle.refresh(1.0, 0.001, HOUR * 6)
        # tick 8 = revert Refresh (tick 7 is Pending)
        oracle.refresh(1.0, 0.001, HOUR * 8)
        # tick 9 is Pending — not applied

        baseline = 1.0  # 2^0
        delta = abs(oracle.get_oracle_price() - baseline) / baseline
        assert delta < 0.05, f"S04 (Solidity cadence): residual={delta:.4f} >= 5%"


class TestOracleS01BenignMotion:
    """
    Cross-validate against test_S01_benignMotion.

    24 refreshes with ±5% oscillations. Mid drift < 10%.
    """

    def setup_method(self):
        self.oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)
        self.oracle.init(1.0, 0.001, HOUR * 1)
        self.oracle.refresh(1.0, 0.001, HOUR * 2)
        self.oracle.refresh(1.0, 0.001, HOUR * 3)
        self.baseline = self.oracle.get_oracle_price()

    def test_benign_drift_bounded(self):
        """24 small oscillations: drift < 10%."""
        h = 4
        for i in range(24):
            price = 1.05 if i % 2 == 0 else 0.95
            self.oracle.refresh(price, 0.001, HOUR * h)
            h += 1

        delta = abs(self.oracle.get_oracle_price() - self.baseline) / self.baseline
        assert delta < 0.10, f"S01: drift={delta:.4f} >= 10%"


class TestAnalyticalTrajectory:
    """Test the analytical step-crash trajectory function."""

    def test_initial_price_correct(self):
        """At n=0, oracle reports pre-crash price."""
        trajectory = oracle_trajectory_step_crash(100.0, 0.50, DECAY_12HL, 10)
        assert trajectory[0] == pytest.approx(100.0, rel=1e-10)

    def test_converges_to_crash_price(self):
        """After many refreshes, oracle converges to post-crash price."""
        trajectory = oracle_trajectory_step_crash(100.0, 0.50, DECAY_12HL, 200)
        assert trajectory[-1] == pytest.approx(50.0, rel=0.01)

    def test_monotonic_decrease_for_crash(self):
        """Oracle price monotonically decreases after a crash (after initial delay)."""
        trajectory = oracle_trajectory_step_crash(100.0, 0.50, DECAY_12HL, 50)
        # After the 2-refresh delay, should be monotonically decreasing
        for i in range(3, len(trajectory)):
            assert trajectory[i] <= trajectory[i - 1] + 1e-10

    def test_matches_oracle_model(self):
        """Analytical trajectory matches step-by-step OracleModel simulation."""
        analytical = oracle_trajectory_step_crash(1.0, 0.40, DECAY_12HL, 30)

        oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)
        oracle.init(1.0, 0.001, HOUR)

        simulated = [oracle.get_oracle_price()]
        for n in range(1, 31):
            oracle.refresh(0.60, 0.001, HOUR * (n + 1))
            simulated.append(oracle.get_oracle_price())

        # Compare (skip n=0 since warmup differs)
        for n in range(2, 31):
            assert analytical[n] == pytest.approx(simulated[n], rel=1e-6), \
                f"Mismatch at refresh {n}: analytical={analytical[n]:.8f}, simulated={simulated[n]:.8f}"


class TestVectorizedOracle:
    """Test the vectorized oracle EMA implementation."""

    def test_matches_scalar(self):
        """Vectorized oracle matches scalar OracleModel for multiple paths."""
        rng = np.random.default_rng(42)
        n_paths, n_steps = 5, 50
        prices = rng.lognormal(0, 0.1, (n_paths, n_steps))
        prices[:, 0] = 1.0

        # Vectorized
        oracle_vec = run_oracle_over_prices_vectorized(prices, DECAY_12HL)

        # Scalar (per-path)
        for i in range(n_paths):
            oracle = OracleModel(decay=DECAY_12HL, refresh_interval=HOUR)
            for t in range(n_steps):
                if t == 0:
                    oracle.init(prices[i, t], 0.001, HOUR)
                else:
                    oracle.refresh(prices[i, t], 0.001, HOUR * (t + 1))
                expected = oracle.get_oracle_price()
                assert oracle_vec[i, t] == pytest.approx(expected, rel=1e-6), \
                    f"Path {i}, step {t}: vec={oracle_vec[i, t]:.8f}, scalar={expected:.8f}"


class TestPhantomWindowSimVerification:
    """
    Spec §3.2: Verify phantom-healthy window analytical computation
    matches step-by-step OracleModel simulation.
    """

    def setup_method(self):
        self.decay = DECAY_12HL
        self.oracle = OracleModel(decay=self.decay, refresh_interval=HOUR)

    def _simulate_phantom_window(self, crash_frac, initial_health, max_refreshes=200):
        """Run OracleModel and count phantom-healthy refreshes."""
        oracle = OracleModel(decay=self.decay, refresh_interval=HOUR)
        oracle.init(1.0, 0.001, HOUR)

        true_price = 1.0 - crash_frac
        h_true = initial_health * true_price
        if h_true >= 1.0:
            return 0  # not underwater

        # Oracle liquidation threshold: p_oracle < 1/H
        threshold = 1.0 / initial_health

        n_phantom = 0
        for n in range(1, max_refreshes + 1):
            oracle.refresh(true_price, 0.001, HOUR * (n + 1))
            oracle_ratio = oracle.get_oracle_price() / 1.0
            if oracle_ratio < threshold:
                break
            n_phantom = n

        return n_phantom

    def test_phantom_matches_analytical_50pct_h1_1(self):
        """50% crash, H=1.1: analytical phantom window matches simulation."""
        from ..analysis.oracle_lag import compute_phantom_window
        analytical = compute_phantom_window(0.50, 1/3, self.decay, 1.1)
        simulated = self._simulate_phantom_window(0.50, 1.1)
        assert abs(analytical["n_phantom"] - simulated) <= 1, \
            f"Mismatch: analytical={analytical['n_phantom']}, simulated={simulated}"

    def test_phantom_matches_analytical_30pct_h1_3(self):
        """30% crash, H=1.3: analytical phantom window matches simulation."""
        from ..analysis.oracle_lag import compute_phantom_window
        analytical = compute_phantom_window(0.30, 1/3, self.decay, 1.3)
        simulated = self._simulate_phantom_window(0.30, 1.3)
        assert abs(analytical["n_phantom"] - simulated) <= 1, \
            f"Mismatch: analytical={analytical['n_phantom']}, simulated={simulated}"

    def test_phantom_matches_analytical_70pct_h2_0(self):
        """70% crash, H=2.0: analytical phantom window matches simulation."""
        from ..analysis.oracle_lag import compute_phantom_window
        analytical = compute_phantom_window(0.70, 1/3, self.decay, 2.0)
        simulated = self._simulate_phantom_window(0.70, 2.0)
        assert abs(analytical["n_phantom"] - simulated) <= 1, \
            f"Mismatch: analytical={analytical['n_phantom']}, simulated={simulated}"

    def test_not_underwater_returns_zero(self):
        """20% crash, H=2.0: not underwater, phantom window = 0."""
        from ..analysis.oracle_lag import compute_phantom_window
        analytical = compute_phantom_window(0.20, 1/3, self.decay, 2.0)
        assert not analytical["is_underwater"]
        assert analytical["n_phantom"] == 0


class TestDeviationTable:
    """Test the oracle deviation heatmap computation."""

    def test_shape(self):
        magnitudes = np.array([0.2, 0.5, 0.7])
        table = oracle_deviation_table(magnitudes, 72, DECAY_12HL)
        assert table.shape == (3, 73)

    def test_initial_no_absorption(self):
        """At n=0, nothing absorbed."""
        magnitudes = np.array([0.3])
        table = oracle_deviation_table(magnitudes, 10, DECAY_12HL)
        assert table[0, 0] == pytest.approx(0.0, abs=0.01)

    def test_eventual_full_absorption(self):
        """After many refreshes, nearly fully absorbed."""
        magnitudes = np.array([0.5])
        table = oracle_deviation_table(magnitudes, 200, DECAY_12HL)
        assert table[0, -1] > 0.99
