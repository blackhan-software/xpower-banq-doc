#!/usr/bin/env python3
"""
Plot 2: TWAP/EWMA Response to Price Shock
Shows how TWAP mean responds to a sudden price change.
Split into two separate figures for better readability.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import common utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _common import decay_factor, C_RED, C_ORANGE, C_GREEN, C_BLUE


def plot_twap_response():
    """Shows how TWAP mean responds to a sudden price change (Figure 1)"""
    n_periods = 30

    # Price shock: jumps from 100 to 150 at period 5
    spot_price = np.array([100]*5 + [150]*25)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Different half-lives
    halflives = [2, 6, 12, 24]
    colors = [C_RED, C_ORANGE, C_GREEN, C_BLUE]

    for hl, color in zip(halflives, colors):
        decay = decay_factor(hl)
        mean = np.zeros(n_periods)
        mean[0] = spot_price[0]

        for i in range(1, n_periods):
            # EWMA: mean[n+1] = λ·mean[n] + (1-λ)·last[n]
            mean[i] = decay * mean[i-1] + (1 - decay) * spot_price[i-1]

        ax.plot(mean, label=r'HL=%d ($\lambda$=%.3f)' % (hl, decay), color=color, linewidth=2)

    ax.step(range(n_periods), spot_price, 'k--', label='Spot Price', linewidth=1.5, alpha=0.7, where='post')
    ax.axvline(x=5, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('Refresh Period')
    ax.set_ylabel('Price')
    ax.set_title(r'TWAP Response to Price Shock (100 $\rightarrow$ 150)')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    ax.set_ylim(95, 155)

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.refresh-response.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


def plot_memory_decay():
    """Shows memory decay over time (Figure 2)"""
    n_periods = 30

    fig, ax = plt.subplots(figsize=(10, 6))

    halflives = [2, 6, 12, 24]
    colors = [C_RED, C_ORANGE, C_GREEN, C_BLUE]

    for hl, color in zip(halflives, colors):
        decay = decay_factor(hl)
        # Weight remaining on old value after n periods
        weights = [decay**n for n in range(n_periods)]
        ax.plot(weights, label=f'HL={hl}', color=color, linewidth=2)

    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Periods After Shock')
    ax.set_ylabel('Weight on Old Value')
    ax.set_title(r'Memory Decay: $\lambda^n$ (weight on pre-shock price)')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.refresh-decay.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


if __name__ == '__main__':
    plot_twap_response()
    plot_memory_decay()
