"""
Matplotlib style configuration matching whitepaper aesthetic.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt


def apply_style():
    """Apply publication-quality matplotlib style."""
    plt.rcParams.update({
        # Font
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "DejaVu Serif", "Times New Roman"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        # Figure
        "figure.figsize": (8, 5),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
        # Grid
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
        # Lines
        "lines.linewidth": 1.5,
        "lines.markersize": 5,
        # Axes
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


# Color palette
COLORS = {
    "primary": "#2563eb",    # blue
    "danger": "#dc2626",     # red
    "warning": "#f59e0b",    # amber
    "success": "#16a34a",    # green
    "muted": "#6b7280",      # gray
    "dark": "#1f2937",       # dark gray
}

PALETTE = [
    "#2563eb", "#dc2626", "#16a34a", "#f59e0b",
    "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
]
