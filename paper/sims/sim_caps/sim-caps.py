#!/usr/bin/env python3
from numpy import sqrt

def my_cap(
    balance,
    max_cap,
    supply,
    n_accounts
) -> float:
    """
    Computes the max. invdividual capacity gain per round
    for given balance, supply, max. capacity and accounts.
    """
    # compute lambda: balance / supply
    lmb = balance / supply
    # compute my capacity gain multiplier
    mul = 12*lmb*(1-lmb)**2
    # compute my capacity gain divisor
    div = sqrt(n_accounts + 2)
    # compute my capacity gain
    return max_cap * mul / div

if __name__ == "__main__":

    # epsilon for stopping criterion
    eps = 1e-3
    # max. capacity (normalized)
    max_cap = 1.00
    # supply (normalized)
    supply = 1.00

    print(f"beg_balance;n_accounts;iterations") # header

    for beg_balance in map(lambda e: 10**(-e), range(1, 9)):
        for n_accounts in map(lambda e: 10**(2*e), range(1, 5)):

            end_balance = beg_balance
            iterations = 0

            # simulate cap gain until close to supply
            while (supply - end_balance) / supply > eps:
                end_balance += my_cap(end_balance, max_cap, supply, n_accounts)
                iterations += 1

            print(f"{beg_balance:.0e};{n_accounts:.0e};{iterations:.3e}")
