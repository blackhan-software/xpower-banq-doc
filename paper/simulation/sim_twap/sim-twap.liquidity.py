#!/usr/bin/env python3
"""
Plot: Spread Scaling by Liquidity Level
Shows how base spread σ captures liquidity and affects effective spread.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import common utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _common import ONE, C_RED, C_ORANGE, C_GREEN


def plot_liquidity():
    """Show how liquidity level (base spread) affects effective spread"""

    fig, ax = plt.subplots(figsize=(10, 6))

    # Different liquidity levels (base spreads)
    liquidity_levels = [
        (r"Illiquid ($\sigma$=5.0\%)", 0.05,  C_RED),
        (r"Medium ($\sigma$=2.0\%)", 0.02,  C_ORANGE),
        (r"Liquid ($\sigma$=0.5\%)", 0.005, C_GREEN),
    ]

    usd_values = np.logspace(1, 6, 100)  # $10 to $1M

    # Draw solid lines first (effective spread)
    for name, sigma, color in liquidity_levels:
        x = usd_values * sigma
        mu = np.log2(2*x + 2)
        spreads = sigma * mu * 100
        ax.semilogx(usd_values, spreads, color=color, linewidth=2.5, label=name)

    # Draw dashed base spread lines (legend entries appear after solid lines)
    for name, sigma, color in liquidity_levels:
        ax.axhline(y=sigma*100, color=color, linestyle='--', alpha=0.5,
                   label=r'Base ($\sigma$=%.1f\%%)' % (sigma*100))

    ax.set_xlabel('Trade Value (base units)')
    ax.set_ylabel(r'Effective Spread (\%)')
    ax.set_title('Spread Scaling: Liquidity Matters')
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3, which='both')

    ax.text(0.98, 0.02, r'$x = \mathrm{value} \times \sigma$' + '\n' + r'$\mu = \log_2(2x + 2)$' + '\n' + r'$\mathrm{spread} = \sigma \times \mu$',
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray', alpha=0.8))

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.liquidity.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


if __name__ == '__main__':
    plot_liquidity()
