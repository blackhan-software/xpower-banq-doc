#!/usr/bin/env python3
"""
Plot: Middle panel of spread scaling - Effective Spread % vs Trade Size
For inclusion in the paper's core content.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import common utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _common import ONE, C_BLUE, C_GRAY


def plot_spread_mid():
    """Shows effective spread percentage vs trade size"""

    # Base parameters (2% spread)
    bid_base, ask_base = 99 * ONE, 101 * ONE  # in 1e18 units
    unit = ONE

    mid = (bid_base + ask_base) / 2
    rel_spread = (ask_base - bid_base) / mid  # 0.02

    # Trade sizes: 0.001 to 1,000,000 units
    amounts = np.logspace(15, 24, 500)  # 0.001 to 1,000,000 units

    fig, ax = plt.subplots(figsize=(8, 5))

    # Calculate spreads using Oracle.sol formula
    values = mid * amounts / unit
    x = amounts * rel_spread / unit
    mu = np.log2(2*x + 2)  # log₂(2x + 2)
    rel_scaled = rel_spread * mu
    hlf_spreads = values * rel_scaled / 2

    bids = values - hlf_spreads
    asks = values + hlf_spreads

    # Relative spread vs Amount (log-x)
    actual_spread_pct = (asks - bids) / values * 100
    base_spread_pct = rel_spread * 100

    ax.semilogx(amounts/ONE, actual_spread_pct, color=C_BLUE, linestyle='-', linewidth=2.5, label=r'Effective Spread \%')
    ax.axhline(y=base_spread_pct, color=C_GRAY, linestyle='--', linewidth=1.5,
               label=f'Base Spread ({base_spread_pct:.1f}\\%)')
    ax.set_xlabel('Trade Amount (tokens)', fontsize=12)
    ax.set_ylabel(r'Spread (\%)', fontsize=12)
    ax.set_title('Effective Spread vs Trade Size', fontsize=14)
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3, which='both')

    # Annotate key points
    for amt, rot, xyoff in [(1e-3, 0, (0, 10)), (1, 0, (0, 10)), (1e3, 50, (0, 10)), (1e6, 55, (-15, -20))]:
        idx = np.argmin(np.abs(amounts/ONE - amt))
        ax.annotate(f'{actual_spread_pct[idx]:.1f}\\%',
                    xy=(amounts[idx]/ONE, actual_spread_pct[idx]),
                    xytext=xyoff, textcoords='offset points',
                    ha='center', fontsize=10, rotation=rot)

    # Formula box
    ax.text(0.98, 0.02, r'$x = n \cdot s$' + '\n' + r'$\mu = \log_2(2x + 2)$' + '\n' + r"$s' = s \times \mu$",
            transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.spread-mid.png'
    plt.savefig(output, dpi=150)
    plt.close()
    print(f"Saved: {output}")


if __name__ == '__main__':
    plot_spread_mid()
