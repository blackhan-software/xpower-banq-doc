"""
Cross-validate Python interest rate model against Rate.sol.

References:
    source/library/Rate.sol lines 170-183 — piecewise rate
    test/Rate/Rate.t.sol — test vectors
"""
import numpy as np
import pytest

from ..models.interest import rate_by, borrow_rate, supply_rate, accrue
from ..config import YEAR_SECONDS


class TestRateBy:
    """Test the piecewise-linear rate function."""

    def test_zero_util(self):
        """Zero utilization → zero rate."""
        assert rate_by(0.0, 0.90, 0.10) == 0.0

    def test_optimal_util(self):
        """At optimal utilization → optimal rate."""
        assert rate_by(0.90, 0.90, 0.10) == pytest.approx(0.10, rel=1e-10)

    def test_half_optimal(self):
        """At half optimal → half rate (linear)."""
        assert rate_by(0.45, 0.90, 0.10) == pytest.approx(0.05, rel=1e-10)

    def test_above_optimal(self):
        """Above optimal → quadratic growth."""
        r = rate_by(0.95, 0.90, 0.10)
        assert r > 0.10  # above optimal rate
        assert r < 2.0   # below cap

    def test_full_utilization(self):
        """At 100% utilization → high rate."""
        r = rate_by(1.0, 0.90, 0.10)
        assert r > 0.50  # significantly above optimal

    def test_capped_at_200pct(self):
        """Rate cannot exceed 200%."""
        # With util_opt very low, rate at full util should be high but capped
        r = rate_by(1.0, 0.10, 0.05)
        assert r <= 2.0

    def test_linear_region_proportional(self):
        """Rate is proportional to util in the linear region."""
        r1 = rate_by(0.30, 0.90, 0.10)
        r2 = rate_by(0.60, 0.90, 0.10)
        assert r2 == pytest.approx(2 * r1, rel=1e-10)


class TestBorrowSupplyRates:
    """Test spread application."""

    def test_no_spread(self):
        """With zero spread, borrow == supply == base."""
        b = borrow_rate(0.50, 0.90, 0.10, spread=0.0)
        s = supply_rate(0.50, 0.90, 0.10, spread=0.0)
        base = rate_by(0.50, 0.90, 0.10)
        assert b == pytest.approx(base)
        assert s == pytest.approx(base)

    def test_symmetric_spread(self):
        """With spread, borrow > base > supply."""
        spread = 0.10  # 10%
        base = rate_by(0.90, 0.90, 0.10)
        b = borrow_rate(0.90, 0.90, 0.10, spread=spread)
        s = supply_rate(0.90, 0.90, 0.10, spread=spread)
        assert b == pytest.approx(base * 1.10)
        assert s == pytest.approx(base * 0.90)
        assert b > s


class TestAccrue:
    """Test continuous compounding."""

    def test_zero_rate(self):
        """Zero rate → no growth."""
        assert accrue(100.0, 0.0, YEAR_SECONDS) == pytest.approx(100.0)

    def test_one_year_10pct(self):
        """10% annual rate for 1 year: 100 * e^0.10 ≈ 110.517."""
        result = accrue(100.0, 0.10, YEAR_SECONDS)
        assert result == pytest.approx(110.517, rel=1e-3)

    def test_half_year(self):
        """10% for half year: 100 * e^0.05."""
        result = accrue(100.0, 0.10, YEAR_SECONDS / 2)
        assert result == pytest.approx(100.0 * np.exp(0.05), rel=1e-10)
