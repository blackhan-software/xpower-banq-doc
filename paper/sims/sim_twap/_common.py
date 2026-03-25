#!/usr/bin/env python3
"""
Common utilities for Oracle.sol TWAP simulations.
Uses 1e18 as unit (matching Solidity).
"""

import numpy as np
import matplotlib.pyplot as plt

# Configure matplotlib to use LaTeX with Libertinus font (matching the paper)
# Larger sizes to compensate for scaling when embedded in LaTeX
plt.rcParams.update({
    'text.usetex': True,
    'text.latex.preamble': r'\usepackage{libertinus}',
    'font.family': 'serif',
    'font.size': 22,
    'axes.labelsize': 22,
    'axes.titlesize': 24,
    'legend.fontsize': 20,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
})

# Constants (matching Solidity)
ONE = 1e18
UNIT = 1e18

# Color palette matching LaTeX \definecolor definitions in banq.tex
# These ensure visual consistency between tikzpicture plots and Python PDFs
COLORS = {
    'primaryblue': '#2962FF',   # RGB(41, 98, 255)
    'warningred': '#DC3545',    # RGB(220, 53, 69)
    'successgreen': '#28A745',  # RGB(40, 167, 69)
    'orange': '#FD7E14',        # Standard Bootstrap orange (matches LaTeX orange)
    'yellow': '#FFC107',        # Standard Bootstrap yellow
    'gray': '#808080',          # RGB(128, 128, 128)
    'purple': '#800080',        # RGB(128, 0, 128) - codepurple from LaTeX
}

# Shorthand aliases
C_BLUE = COLORS['primaryblue']
C_RED = COLORS['warningred']
C_GREEN = COLORS['successgreen']
C_ORANGE = COLORS['orange']
C_YELLOW = COLORS['yellow']
C_GRAY = COLORS['gray']
C_PURPLE = COLORS['purple']


def decay_factor(halflife):
    """λ = 0.5^(1/h)"""
    return 0.5 ** (1 / halflife)


def format_amount(x, _):
    """Format large numbers nicely"""
    if x >= 1e18:
        return f'{x/1e18:.0f}'
    elif x >= 1e15:
        return f'{x/1e15:.0f}m'
    elif x >= 1e12:
        return f'{x/1e12:.0f}μ'
    elif x >= 1e9:
        return f'{x/1e9:.0f}n'
    elif x >= 1e6:
        return f'{x/1e6:.0f}p'
    else:
        return f'{x:.0f}'
