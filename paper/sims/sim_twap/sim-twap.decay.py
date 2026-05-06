#!/usr/bin/env python3
"""
Plot 1: Decay Factors by Half-Life
Visualizes λ = 0.5^(1/halflife) for different half-life values.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import common utilities
import sys
sys.path.insert(0, str(Path(__file__).parent))
from _common import decay_factor, C_BLUE, C_GREEN, C_RED


def plot_decay_factors():
    halflives = np.arange(1, 25)
    decays = [decay_factor(h) for h in halflives]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(halflives, decays, color=C_BLUE, alpha=0.8)
    ax.set_xlabel('Half-Life (refresh periods)')
    ax.set_ylabel(r'Decay Factor ($\lambda$)')
    ax.set_title(r'TWAP Decay Factor: $\lambda = 0.5^{1/h}$')
    ax.set_ylim(0.4, 1.02)
    ax.axhline(y=1.0, color=C_GREEN, linestyle='--', alpha=0.5, label=r'$\lambda=1.0$ (half-life=$\infty$)')
    ax.axhline(y=0.5, color=C_RED, linestyle='--', alpha=0.5, label=r'$\lambda=0.5$ (half-life=1)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    output = Path(__file__).parent / 'plt-twap.decay.pdf'
    plt.savefig(output, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"Saved: {output}")


if __name__ == '__main__':
    plot_decay_factors()
