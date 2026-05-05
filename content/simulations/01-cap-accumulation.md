---
title: "1. Capacity Accumulation"
prev: false
next:
  text: "2. Cascade Simulation"
  link: /simulations/02-cascade
---

The following Python script simulates capacity accumulation under the [beta-distributed cap function](/whitepaper/04-mechanisms#beta-distributed-position-caps).

```python
#!/usr/bin/env python3
from numpy import sqrt

def my_cap(balance, max_cap, supply, n_accounts) -> float:
    """
    Computes the max. individual capacity gain per round
    for given balance, supply, max. capacity and accounts.
    """
    lmb = balance / supply
    mul = 12 * lmb * (1 - lmb) ** 2
    div = sqrt(n_accounts + 2)
    return max_cap * mul / div

if __name__ == "__main__":
    eps = 1e-3
    max_cap = 1.00
    supply = 1.00

    print(f"beg_balance;n_accounts;iterations")
    for beg_balance in map(lambda e: 10**(-e), range(1, 9)):
        for n_accounts in map(lambda e: 10**(2*e), range(1, 5)):
            end_balance = beg_balance
            iterations = 0
            while (supply - end_balance) / supply > eps:
                end_balance += my_cap(end_balance, max_cap, supply, n_accounts)
                iterations += 1
            print(f"{beg_balance:.0e};{n_accounts:.0e};{iterations:.3e}")
```

## Cap Function Components

The `my_cap` function implements the beta cap formula. The balance ratio $\lambda = B/S$ normalizes across token amounts and decimals. The Beta(2,3) multiplier $12\lambda(1{-}\lambda)^2$ vanishes at both boundaries ($\lambda = 0$ and $\lambda = 1$), peaks at $\lambda = 1/3$, and decays quadratically via $(1{-}\lambda)^2$ as holdings approach monopoly. The holder divisor $\sqrt{n{+}2}$ provides sublinear Sybil resistance: creating more accounts increases $n$, reducing per-account cap gains, with the offset of 2 preventing degeneracy at low holder counts. $C_{\max}$ is the governance-configured upper bound on relative capacity.

<figure>
  <img src="/images/005-beta.svg" alt="Beta distribution cap function 12λ(1−λ)²">
  <figcaption>Figure 1: Beta distribution cap function 12λ(1−λ)², peaking at λ = 1/3.</figcaption>
</figure>

## Simulation Algorithm

The simulation sweeps over starting balances and holder counts. For each combination, it iteratively adds the cap gain (via `my_cap`) to the user's balance until the remaining capacity $(1 - \lambda)$ falls below $\varepsilon = 0.1\%$ of total supply, recording the number of iterations required. The stopping threshold avoids infinite loops caused by the asymptotic decay of the cap function as $\lambda \to 1$. The holder count $n$ is held constant throughout each run; in practice, $n$ would fluctuate as users enter and exit.

## Convergence Behavior

Near $\lambda = 0$, the cap gain grows linearly ($\approx 12\lambda / \sqrt{n{+}2}$), producing a fast start. Near $\lambda = 1$, it shrinks quadratically ($\approx 12(1{-}\lambda)^2 / \sqrt{n{+}2}$), producing a slow approach to full capacity. Because most iterations occur in this slow-convergence region, starting balance has minimal impact on total iterations. Since cap gain scales as $1/\sqrt{n}$, iterations scale as $\sqrt{n}$ — explaining the $10\times$ increase when moving from $10^2$ to $10^4$ accounts.

## Representative Output

| Starting $\lambda$ | Accounts ($n$) | Iterations |
|:---:|:---:|---:|
| $10^{-2}$ | $10^2$ | 846 |
| $10^{-2}$ | $10^4$ | 8,417 |
| $10^{-2}$ | $10^6$ | 84,200 |
| $10^{-2}$ | $10^8$ | 842,100 |
| $10^{-4}$ | $10^2$ | 852 |
| $10^{-4}$ | $10^4$ | 8,458 |
| $10^{-4}$ | $10^6$ | 84,590 |
| $10^{-4}$ | $10^8$ | 845,900 |

The results confirm the $O(\sqrt{n})$ scaling: $10^4$ accounts require approximately $10\times$ more iterations than $10^2$ accounts. Starting balance has minimal impact ($<2\%$ across 7 orders of magnitude), confirming that convergence near $\lambda = 1$ dominates. For a protocol with $10^6$ large holders, any user requires approximately 84,000 iterations to reach full capacity, providing predictable growth independent of initial position size.

## Multi-Account Share Dynamics

The following simulation examines how capital shares evolve when multiple accounts compete for capacity under the beta cap function and iteration constraints:

```python
#!/usr/bin/env python3
from numpy import sqrt

def beta_cap(balance, max_cap, supply, n_holders):
    """Beta-distributed cap function."""
    lam = balance / supply if supply > 0 else 0
    mul = 12 * lam * (1 - lam) ** 2
    div = sqrt(n_holders + 2)
    return max_cap * mul / div

def simulate_shares(
    n_honest, k_sybil,
    honest_capital, sybil_capital,
    iters_per_week=7, weeks=60, max_cap=1.0
):
    """Simulate share evolution with iteration cap."""
    n_total = n_honest + k_sybil
    honest_bal = [honest_capital / n_honest] * n_honest
    sybil_bal = [sybil_capital / k_sybil] * k_sybil
    total_supply = honest_capital + sybil_capital

    trajectory = []
    for week in range(weeks):
        for _ in range(iters_per_week):
            honest_bal = [b + beta_cap(b, max_cap, total_supply, n_total) for b in honest_bal]
            sybil_bal = [b + beta_cap(b, max_cap, total_supply, n_total) for b in sybil_bal]
            total_supply = sum(honest_bal) + sum(sybil_bal)

        honest_share = sum(honest_bal) / total_supply
        sybil_share = sum(sybil_bal) / total_supply
        trajectory.append((week, honest_share, sybil_share))

    return trajectory
```

The simulation reveals that capital shares are *persistent*, not convergent: the beta cap function preserves relative capital ratios because capacity gain is proportional to current $\lambda = B/S$.

| Scenario | Initial Share | Week 7 | Week 59 |
|:---:|:---:|:---:|:---:|
| Equal shares | 50% : 50% | 50.9% : 49.1% | 51.4% : 48.6% |
| Unequal shares | 10.5% : 89.5% | 11.2% : 88.8% | 11.9% : 88.1% |

The results show that initial capital distribution strongly influences long-term shares: with a $9\times$ capital advantage, the advantaged party retains 88% share after 60 weeks. Shares change by less than 2% over 420 iterations, and the weekly cap is iteration-count bounded (7 per week), so burst timing is irrelevant. The protocol's Sybil resistance therefore derives from the $\sqrt{n{+}2}$ divisor and iteration caps rather than from equilibrium convergence — early capital advantages persist, and the defense operates through structural constraints.

## Limitations

The simulation assumes static holder count (in practice, $n$ fluctuates), continuous cap gains (real protocols have discrete rounding), no holder floor dynamics (the bootstrap phase with $n_{\text{real}} < n_{\min}$ is unmodeled), and homogeneous iteration timing. Specifically, `Position.largeHolders()` returns $\max(\text{actual},\ \texttt{MIN\_HOLDERS\_ID})$; results above assume `MIN_HOLDERS_ID = 0` (no floor). With the deployed floor, iteration counts at low $n$ are uniformly larger by the ratio $\sqrt{(\texttt{MIN\_HOLDERS\_ID} + 2)/(n + 2)}$.

The simulation validates two key properties: (1) the $O(\sqrt{n})$ iteration scaling, and (2) starting balance independence for single-account accumulation time. It also reveals that multi-account share dynamics do not converge to account-proportional equilibrium — a finding that informs the rate-limiting analysis in the [Whitepaper §4.4](/whitepaper/04-mechanisms#beta-distributed-position-caps).
