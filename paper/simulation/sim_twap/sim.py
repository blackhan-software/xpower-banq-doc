#!/usr/bin/env python3
"""
Oracle.sol Formula Simulations - Main Entry Point
Visualizes TWAP (EWMA) and spread scaling mechanics.
Uses 1e18 as unit (matching Solidity).

Each sub-script can also be run independently:
  python3 sim-twap.decay.py
  python3 sim-twap.liquidity.py
  python3 sim-twap.refresh.py
  python3 sim-twap.spread.py
"""

import subprocess
import sys
import numpy as np
from pathlib import Path

# Sub-scripts to execute
SCRIPTS = [
    'sim-twap.decay.py',
    'sim-twap.liquidity.py',
    'sim-twap.refresh.py',
    'sim-twap.spread.py',
]


def print_insights():
    """Print key insights about the formulas"""
    print("\n" + "="*80)
    print("KEY INSIGHTS (with orders of magnitude):")
    print("="*80)

    # Calculate example values
    rel_spread = 0.02  # 2%
    print(f"\nBase spread: {rel_spread*100}%")
    print(f"{'Amount (units)':<20} {'μ multiplier':<15} {'Effective spread':<15}")
    print("-"*50)
    for amt in [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]:
        x = amt * rel_spread
        mu = np.log2(2*x + 2)
        eff = rel_spread * mu * 100
        print(f"{amt:<20.3f} {mu:<15.2f} {eff:<15.2f}%")

    print("="*80)


def main():
    print("Generating Oracle.sol formula visualizations (1 unit = 1e18)...\n")

    script_dir = Path(__file__).parent

    for script in SCRIPTS:
        script_path = script_dir / script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running {script}:")
            print(result.stderr)
            sys.exit(1)
        print(result.stdout, end='')

    print_insights()


if __name__ == '__main__':
    main()
