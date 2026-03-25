#!/usr/bin/env python3
import sys
from numpy import clip, random

def simulate(positions, price_drop, impact_coef):
    """
    Simulates liquidation cascade with market impact.
    Returns percentage of total supply liquidated.
    """
    initial_supply = sum(p[0] for p in positions)
    price = 1.0 - price_drop
    total_liquidated = 0
    while True:
        underwater = [p for p in positions
            if p[0] > 0 and (p[0] * price) / p[1] < 1.0]
        if not underwater:
            break
        round_sold = 0
        for p in underwater:
            unlocked = p[0] * (1 - p[2])
            round_sold += unlocked
            total_liquidated += p[0]
            p[0] = 0
            p[1] = 0
        price -= impact_coef * round_sold
        if price <= 0:
            break
    return (total_liquidated / initial_supply * 100) if initial_supply > 0 else 0

def gen_positions(seed, n, lock):
    """Generate positions with given lock fraction."""
    random.seed(seed)
    sizes = random.lognormal(mean=0, sigma=1, size=n)
    healths = clip(random.normal(1.5, 0.3, n), 1.0, 3.0)
    return [[s, s/h, lock] for s, h in zip(sizes, healths)]

SCENARIOS = [
    ("Liquid",   1e-6,   0.2),
    ("Moderate", 6e-5,  10.1),
    ("Strong",   1.5e-4, 25.2),
    ("Severe",   3e-4,  50.5),
    ("Extreme",  5e-4,  84.1),
]

if __name__ == "__main__":

    idx = int(sys.argv[1]) # select scenario
    name, k, depth = SCENARIOS[idx]
    n_positions = 1000
    seed = 42

    locks = [0.00, 0.25, 0.50, 0.75, 1.00]
    drops = [0.10, 0.15, 0.20, 0.25, 0.30]

    print("lock;drop;liquidated")

    for lock in locks:
        for drop in drops:
            positions = gen_positions(seed, n_positions, lock)
            result = simulate(positions, drop, k)
            print(f"{lock:.2f};{drop:.2f};{result:.3f}")
