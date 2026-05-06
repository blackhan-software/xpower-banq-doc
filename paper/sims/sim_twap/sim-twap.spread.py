#!/usr/bin/env python3
"""
Plot 3: Spread Scaling with Trade Size (LOG SCALE)
Shows how bid/ask spread scales logarithmically with trade size.
Split into three separate figures for better readability.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import common utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _common import ONE, C_BLUE, C_GREEN, C_RED, C_GRAY, C_PURPLE


def _compute_spread_data():
    """Compute common spread data used by all plots"""
    # Base parameters (2% spread)
    bid_base, ask_base = 99 * ONE, 101 * ONE  # in 1e18 units
    unit = ONE

    mid = (bid_base + ask_base) / 2
    rel_spread = (ask_base - bid_base) / mid  # 0.02

    # Trade sizes: 0.001 to 1,000,000 units (1e15 to 1e24 in raw)
    amounts = np.logspace(15, 24, 500)

    # Calculate spreads using Oracle.sol formula
    values = mid * amounts / unit
    x = amounts * rel_spread / unit
    mu = np.log2(2*x + 2)  # log₂(2x + 2)
    rel_scaled = rel_spread * mu
    hlf_spreads = values * rel_scaled / 2

    bids = values - hlf_spreads
    asks = values + hlf_spreads

    return {
        'amounts': amounts,
        'values': values,
        'bids': bids,
        'asks': asks,
        'mu': mu,
        'rel_spread': rel_spread,
    }


def plot_bid_ask_quotes():
    """Figure 1: Bid/Ask Quotes vs Trade Size (log-log)"""
    data = _compute_spread_data()
    amounts, values, bids, asks = data['amounts'], data['values'], data['bids'], data['asks']

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.loglog(amounts/ONE, bids/ONE, color=C_GREEN, linestyle='-', linewidth=2, label='Bid Quote')
    ax.loglog(amounts/ONE, values/ONE, 'k-', linewidth=2, label='Mid Value')
    ax.loglog(amounts/ONE, asks/ONE, color=C_RED, linestyle='-', linewidth=2, label='Ask Quote')
    ax.fill_between(amounts/ONE, bids/ONE, asks/ONE, alpha=0.2, color=C_BLUE)
    ax.set_xlabel('Trade Amount (units, 1 unit = 1e18)')
    ax.set_ylabel('Quote Value (units)')
    ax.set_title('Bid/Ask Quotes vs Trade Size')
    ax.legend()
    ax.grid(alpha=0.3, which='both')

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.spread-quotes.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


def plot_effective_spread():
    """Figure 2: Effective Spread Percent vs Trade Size (semilog-x)"""
    data = _compute_spread_data()
    amounts, values, bids, asks = data['amounts'], data['values'], data['bids'], data['asks']
    rel_spread = data['rel_spread']

    fig, ax = plt.subplots(figsize=(10, 6))

    actual_spread_pct = (asks - bids) / values * 100
    base_spread_pct = rel_spread * 100

    ax.semilogx(amounts/ONE, actual_spread_pct, color=C_BLUE, linestyle='-', linewidth=2, label=r'Effective Spread \%')
    ax.axhline(y=base_spread_pct, color=C_GRAY, linestyle='--',
               label=f'Base Spread ({base_spread_pct:.1f}\\%)')
    ax.set_xlabel('Trade Amount (units)')
    ax.set_ylabel(r'Spread (\%)')
    ax.set_title('Effective Spread Percent vs Trade Size')
    ax.legend()
    ax.grid(alpha=0.3, which='both')

    # Key data points with markers (matching LaTeX figure style)
    key_amounts = [1e-3, 1, 1e3, 1e6]
    key_indices = [np.argmin(np.abs(amounts/ONE - amt)) for amt in key_amounts]
    key_spreads = [actual_spread_pct[idx] for idx in key_indices]
    ax.scatter(key_amounts, key_spreads, color=C_BLUE, s=40, zorder=5)

    # Annotate key points
    for amt, rot, xyoff in [(1e-3, 0, (0, 10)), (1, 0, (0, 10)), (1e3, 45, (0, 7)), (1e6, 50, (-10, -5))]:
        idx = np.argmin(np.abs(amounts/ONE - amt))
        ax.annotate(f'{actual_spread_pct[idx]:.1f}\\%',
                    xy=(amounts[idx]/ONE, actual_spread_pct[idx]),
                    xytext=xyoff, textcoords='offset points',
                    ha='center', rotation=rot)

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.spread-percent.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


def plot_multiplier():
    """Figure 3: The μ scaling factor (semilog-x)"""
    data = _compute_spread_data()
    amounts, mu = data['amounts'], data['mu']

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.semilogx(amounts/ONE, mu, color=C_PURPLE, linewidth=2, label=r'$\mu$ (multiplier)')
    ax.axhline(y=1, color=C_GRAY, linestyle='--', alpha=0.5, label=r'$\mu=1$ (base)')
    ax.set_xlabel('Trade Amount (units)')
    ax.set_ylabel(r'$\mu = \log_2(2x + 2)$')
    ax.set_title(r'Spread Multiplier $\mu$ (Log Impact)')
    ax.grid(alpha=0.3, which='both')
    ax.legend()

    # Key data points with markers (matching LaTeX figure style)
    key_amounts = [1e-3, 1, 1e3, 1e6]
    key_indices = [np.argmin(np.abs(amounts/ONE - amt)) for amt in key_amounts]
    key_mu = [mu[idx] for idx in key_indices]
    ax.scatter(key_amounts, key_mu, color=C_PURPLE, s=40, zorder=5)

    # Annotate key points
    for amt, rot, xyoff in [(1e-3, 0, (0, 10)), (1, 0, (0, 10)), (1e3, 45, (0, 5)), (1e6, 42, (-10, -10))]:
        idx = np.argmin(np.abs(amounts/ONE - amt))
        ax.annotate(r'$\mu$=%.1f' % mu[idx],
                    xy=(amounts[idx]/ONE, mu[idx]),
                    xytext=xyoff, textcoords='offset points',
                    ha='center', rotation=rot)

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.spread-multiplier.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


if __name__ == '__main__':
    plot_bid_ask_quotes()
    plot_effective_spread()
    plot_multiplier()
