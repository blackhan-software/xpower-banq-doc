#!/usr/bin/env python3
from numpy import sqrt

def beta_cap(balance, max_cap, supply, n_holders):
    """Beta-distributed cap function (Equation 4 in paper)."""
    lam = balance / supply if supply > 0 else 0
    mul = 12 * lam * (1 - lam) ** 2
    div = sqrt(n_holders + 2)  # Correct per Eq. 4
    return max_cap * mul / div

def simulate_equilibrium(
    n_honest,
    k_sybil,
    honest_capital,
    sybil_capital,
    iters_per_week=7,
    weeks=60,
    max_cap=1.0
):
    """
    Simulate equilibrium convergence with iteration cap.
    Returns trajectory of shares over weeks.
    """
    n_total = n_honest + k_sybil
    # Each account starts with its capital share
    honest_bal = [honest_capital / n_honest] * n_honest
    sybil_bal = [sybil_capital / k_sybil] * k_sybil
    total_supply = honest_capital + sybil_capital

    trajectory = []
    for week in range(weeks):
        # Each account gets exactly iters_per_week iterations
        for _ in range(iters_per_week):
            honest_bal = [
                b + beta_cap(b, max_cap, total_supply, n_total)
                for b in honest_bal
            ]
            sybil_bal = [
                b + beta_cap(b, max_cap, total_supply, n_total)
                for b in sybil_bal
            ]
            total_supply = sum(honest_bal) + sum(sybil_bal)

        honest_share = sum(honest_bal) / total_supply
        sybil_share = sum(sybil_bal) / total_supply
        trajectory.append((week, honest_share, sybil_share))

    expected_sybil = k_sybil / n_total
    return trajectory, expected_sybil

if __name__ == "__main__":

    # Test scenarios: (n_honest, k_sybil, honest_capital, sybil_capital)
    scenarios = [
        (100, 50, 0.5, 0.5),      # Equal capital, 2:1 accounts
        (100, 100, 0.5, 0.5),     # Equal capital, equal accounts
        (50, 100, 0.5, 0.5),      # Equal capital, 1:2 accounts
        (100, 50, 0.1, 0.9),      # 10x sybil capital advantage
    ]

    print("n_honest;k_sybil;honest_cap;sybil_cap;expected;week;honest_share;sybil_share")

    for n_honest, k_sybil, honest_cap, sybil_cap in scenarios:
        trajectory, expected = simulate_equilibrium(
            n_honest, k_sybil, honest_cap, sybil_cap,
            iters_per_week=7, weeks=60, max_cap=1.0
        )
        for week, h_share, s_share in trajectory:
            print(f"{n_honest};{k_sybil};{honest_cap};{sybil_cap};{expected:.4f};{week};{h_share:.4f};{s_share:.4f}")
