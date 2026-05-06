"""
Visualization for all 9 deliverables.

Each function produces one chart/table and saves to the output directory.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

from .style import apply_style, COLORS, PALETTE

apply_style()


def _savefig(fig, output_dir: Path, name: str):
    """Save figure as both PNG and PDF (vector), then close."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{name}.png")
    fig.savefig(output_dir / f"{name}.pdf")
    plt.close(fig)
    print(f"    Saved: {name}.png + .pdf")


# ── Deliverable 1: Oracle Lag Heatmap ────────────────────────────────


def plot_oracle_lag_heatmap(lag_data: dict, output_dir: Path):
    """
    Heatmap of oracle deviation (%) vs (crash magnitude × hours elapsed).
    """
    dev = lag_data["deviation_pct"]
    crashes = lag_data["crash_magnitudes"] * 100
    hours = lag_data["hours"]

    # Subsample hours for readability
    step = max(1, len(hours) // 36)
    h_idx = np.arange(0, len(hours), step)

    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(
        dev[:, h_idx],
        aspect="auto",
        cmap="YlOrRd",
        origin="lower",
        interpolation="nearest",
    )
    ax.set_xticks(range(len(h_idx)))
    ax.set_xticklabels([f"{hours[i]}" for i in h_idx], rotation=45, fontsize=8)
    ax.set_yticks(range(len(crashes)))
    ax.set_yticklabels([f"{c:.0f}%" for c in crashes])
    ax.set_xlabel("Hours After Crash")
    ax.set_ylabel("Crash Magnitude")
    ax.set_title("Oracle Deviation from True Price (%)")
    cb = fig.colorbar(im, ax=ax, label="Deviation %")
    fig.tight_layout()
    _savefig(fig, output_dir, "01_oracle_lag_heatmap")


def plot_oracle_convergence_curves(lag_data: dict, output_dir: Path):
    """Convergence curves: oracle absorption over time per crash magnitude."""
    abs_data = lag_data["absorption"]
    crashes = lag_data["crash_magnitudes"] * 100
    hours = lag_data["hours"]

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, c in enumerate(crashes):
        ax.plot(hours, abs_data[i] * 100, label=f"{c:.0f}% crash", color=PALETTE[i % len(PALETTE)])
    ax.set_xlabel("Hours After Crash")
    ax.set_ylabel("Crash Absorbed by Oracle (%)")
    ax.set_title(f"Oracle Convergence (DECAY_12HL, 1h refresh)")
    ax.legend()
    ax.set_xlim(0, 72)
    ax.axhline(50, ls="--", color=COLORS["muted"], alpha=0.5, label="50% absorbed")
    fig.tight_layout()
    _savefig(fig, output_dir, "01b_oracle_convergence")


# ── Deliverable 2: Phantom-Healthy Window Tables ────────────────────


def save_phantom_window_table(phantom_data: dict, output_dir: Path):
    """Save phantom-healthy window as CSV table."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = phantom_data["rows"]
    path = output_dir / "02_phantom_windows.csv"
    with open(path, "w") as f:
        f.write("LTV,Crash%,InitialHealth,IsUnderwater,PhantomHours,PhantomRefreshes\n")
        for r in rows:
            f.write(
                f"{r['ltv']:.4f},{r['crash_pct']:.0f},{r['initial_health']:.1f},"
                f"{r['is_underwater']},{r['phantom_hours']:.0f},{r['n_phantom_refreshes']}\n"
            )
    print(f"    Saved: 02_phantom_windows.csv")


def save_blind_time_table(blind_data: dict, output_dir: Path):
    """Save worst-case blind time as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = blind_data["rows"]
    path = output_dir / "02b_blind_times.csv"
    with open(path, "w") as f:
        f.write("LTV,Crash%,PhantomHours,BlindHours,IsUnderwater\n")
        for r in rows:
            f.write(
                f"{r['ltv']:.4f},{r['crash_pct']:.0f},"
                f"{r['phantom_hours']:.0f},{r['blind_hours']:.1f},{r['is_underwater']}\n"
            )
    print(f"    Saved: 02b_blind_times.csv")


# ── Deliverable 3: Historical Backtest Results ───────────────────────


def plot_backtest_timeline(
    backtest_result: dict,
    event_name: str,
    output_dir: Path,
):
    """
    Dual-axis chart: oracle vs true price (top) + cumulative bad debt (bottom).
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                    gridspec_kw={"height_ratios": [2, 1]})

    n = len(backtest_result["true_prices"])
    minutes = np.arange(n)
    hours = minutes / 60

    # Top: prices
    ax1.plot(hours, backtest_result["price_ratio"], label="True price",
             color=COLORS["primary"], linewidth=1.2)
    ax1.plot(hours, backtest_result["oracle_ratio"], label="Oracle price",
             color=COLORS["danger"], linewidth=1.2, linestyle="--")
    ax1.set_ylabel("Price Ratio (normalized)")
    ax1.set_title(f"{event_name} — LTV={backtest_result['ltv']:.2f}, "
                  f"lock={backtest_result['lock_fraction']:.0%}")
    ax1.legend(loc="upper right")
    ax1.axhline(1.0, ls=":", color=COLORS["muted"], alpha=0.3)

    # Bottom: cumulative bad debt
    ax2.fill_between(hours, 0, backtest_result["cumulative_bad_debt"],
                      alpha=0.3, color=COLORS["danger"])
    ax2.plot(hours, backtest_result["cumulative_bad_debt"],
             color=COLORS["danger"], linewidth=1.2)
    ax2.set_xlabel("Hours")
    ax2.set_ylabel("Cumulative Bad Debt (% TVL)")
    ax2.set_ylim(bottom=0)

    fig.tight_layout()
    safe_name = event_name.replace(" ", "_").lower()
    _savefig(fig, output_dir, f"03_backtest_{safe_name}")


def save_backtest_summary(summaries: list[dict], output_dir: Path):
    """Save backtest summary table as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "03_backtest_summary.csv"
    if not summaries:
        return
    keys = summaries[0].keys()
    with open(path, "w") as f:
        f.write(",".join(keys) + "\n")
        for row in summaries:
            f.write(",".join(str(row[k]) for k in keys) + "\n")
    print(f"    Saved: 03_backtest_summary.csv")


# ── Deliverable 4: Monte Carlo Bad Debt Distributions ────────────────


def plot_mc_histogram(mc_result: dict, output_dir: Path, label: str = ""):
    """Histogram of bad debt % with VaR/CVaR annotations."""
    bd = mc_result["bad_debt_samples"]
    metrics = mc_result["metrics"]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(bd, bins=100, density=True, alpha=0.7, color=COLORS["primary"],
            edgecolor="white", linewidth=0.3)
    ax.axvline(metrics["var_99"], color=COLORS["danger"], ls="--", linewidth=1.5,
               label=f"VaR(99%) = {metrics['var_99']:.2f}%")
    ax.axvline(metrics["cvar_99"], color=COLORS["warning"], ls="--", linewidth=1.5,
               label=f"CVaR(99%) = {metrics['cvar_99']:.2f}%")
    ax.axvline(metrics["expected_bd"], color=COLORS["success"], ls="-", linewidth=1.5,
               label=f"E[BD] = {metrics['expected_bd']:.3f}%")

    params = mc_result["params"]
    title = (f"Bad Debt Distribution — LTV={params['ltv']:.2f}, "
             f"α={params['decay']:.4f}, Δt={params['refresh_interval']/3600:.1f}h")
    if label:
        title += f" ({label})"
    ax.set_title(title)
    ax.set_xlabel("Bad Debt (% of TVL)")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout()

    safe_label = label.replace(" ", "_") if label else "default"
    _savefig(fig, output_dir, f"04_mc_histogram_{safe_label}")


def save_mc_summary(mc_summary: list[dict], output_dir: Path):
    """Save MC sweep results as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "04_mc_summary.csv"
    if not mc_summary:
        return
    keys = mc_summary[0].keys()
    with open(path, "w") as f:
        f.write(",".join(keys) + "\n")
        for row in mc_summary:
            f.write(",".join(str(row.get(k, "")) for k in keys) + "\n")
    print(f"    Saved: 04_mc_summary.csv")


# ── Deliverable 4b: Drawdown-to-Bad-Debt Curve (§5.3) ───────────────


def plot_drawdown_vs_bad_debt(mc_result: dict, output_dir: Path, label: str = ""):
    """
    Scatter + binned curve: max drawdown vs bad debt per path.
    Shows the relationship between crash severity and resulting bad debt.
    """
    dd = mc_result["max_drawdowns"] * 100  # to %
    bd = mc_result["bad_debt_samples"]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter (subsample if too many points)
    n = len(dd)
    if n > 5000:
        idx = np.random.default_rng(0).choice(n, 5000, replace=False)
        ax.scatter(dd[idx], bd[idx], alpha=0.1, s=4, color=COLORS["primary"])
    else:
        ax.scatter(dd, bd, alpha=0.2, s=6, color=COLORS["primary"])

    # Binned median curve
    bins = np.linspace(0, max(dd.max(), 1), 25)
    bin_idx = np.digitize(dd, bins) - 1
    bin_centers = []
    bin_medians = []
    bin_p95 = []
    for i in range(len(bins) - 1):
        mask = bin_idx == i
        if mask.sum() >= 5:
            bin_centers.append((bins[i] + bins[i + 1]) / 2)
            bin_medians.append(np.median(bd[mask]))
            bin_p95.append(np.percentile(bd[mask], 95))

    if bin_centers:
        ax.plot(bin_centers, bin_medians, color=COLORS["danger"], linewidth=2,
                label="Median BD", marker="o", markersize=4)
        ax.plot(bin_centers, bin_p95, color=COLORS["warning"], linewidth=1.5,
                ls="--", label="95th pctl BD", marker="s", markersize=3)

    params = mc_result.get("params", {})
    title = "Max Drawdown vs Bad Debt"
    if params:
        title += f" — LTV={params.get('ltv', 0):.2f}, α={params.get('decay', 0):.4f}"
    ax.set_title(title)
    ax.set_xlabel("Maximum Drawdown (%)")
    ax.set_ylabel("Bad Debt (% of TVL)")

    ax.legend()
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    fig.tight_layout()

    safe_label = label.replace(" ", "_") if label else "default"
    _savefig(fig, output_dir, f"04b_drawdown_vs_bd_{safe_label}")


# ── Deliverable 4c: Time-to-Liquidation Histogram (§5.3) ────────────


def plot_time_to_liquidation(mc_result: dict, output_dir: Path, label: str = ""):
    """
    Histogram of delay (in hours) between true-underwater and oracle-triggered
    liquidation.
    """
    delays = mc_result.get("liquidation_delays", [])
    if not delays or len(delays) < 10:
        print("    Skipping time-to-liquidation: insufficient delay data")
        return

    delays_hours = np.array(delays, dtype=float)  # steps = hours for 1h refresh

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(delays_hours, bins=min(100, int(delays_hours.max()) + 1),
            density=True, alpha=0.7, color=COLORS["primary"],
            edgecolor="white", linewidth=0.3)

    median_d = np.median(delays_hours)
    mean_d = np.mean(delays_hours)
    ax.axvline(median_d, color=COLORS["danger"], ls="--", linewidth=1.5,
               label=f"Median = {median_d:.1f}h")
    ax.axvline(mean_d, color=COLORS["warning"], ls="--", linewidth=1.5,
               label=f"Mean = {mean_d:.1f}h")

    ax.set_title("Time-to-Liquidation Distribution (oracle delay)")
    ax.set_xlabel("Delay: True Underwater → Oracle Liquidation (hours)")
    ax.set_ylabel("Density")
    ax.legend()
    ax.set_xlim(left=0)
    fig.tight_layout()

    safe_label = label.replace(" ", "_") if label else "default"
    _savefig(fig, output_dir, f"04c_time_to_liquidation_{safe_label}")


# ── Deliverable 5: Tornado Diagrams ─────────────────────────────────


def plot_tornado(tornado_data: dict, output_dir: Path):
    """Horizontal bar chart showing parameter sensitivity."""
    tornado = tornado_data["tornado"]
    baseline = tornado_data["baseline_bd"]

    if not tornado:
        return

    labels = list(tornado.keys())
    lows = [tornado[k][0] for k in labels]
    highs = [tornado[k][2] for k in labels]

    # Sort by range (widest at top)
    ranges = [h - l for l, h in zip(lows, highs)]
    order = np.argsort(ranges)[::-1]
    labels = [labels[i] for i in order]
    lows = [lows[i] for i in order]
    highs = [highs[i] for i in order]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.8)))
    y_pos = np.arange(len(labels))

    # Low side (left of baseline)
    ax.barh(y_pos, [baseline - l for l in lows], left=lows,
            color=COLORS["primary"], alpha=0.6, label="Below baseline")
    # High side (right of baseline)
    ax.barh(y_pos, [h - baseline for h in highs], left=baseline,
            color=COLORS["danger"], alpha=0.6, label="Above baseline")

    ax.axvline(baseline, color=COLORS["dark"], ls="-", linewidth=1.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Expected Bad Debt (% TVL)")
    ax.set_title(f"Parameter Sensitivity (baseline E[BD] = {baseline:.3f}%)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    _savefig(fig, output_dir, "05_tornado")


# ── Deliverable 6: Interaction Heatmaps ──────────────────────────────


def plot_interaction_heatmap(interaction_data: dict, output_dir: Path, name: str = ""):
    """2D heatmap of bad debt for parameter pair."""
    grid = interaction_data["grid"]
    p1 = interaction_data["param1_values"]
    p2 = interaction_data["param2_values"]
    p1_key = interaction_data["param1_key"]
    p2_key = interaction_data["param2_key"]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(grid, aspect="auto", cmap="YlOrRd", origin="lower")
    ax.set_xticks(range(len(p2)))
    ax.set_xticklabels([f"{v:.3g}" for v in p2], rotation=45)
    ax.set_yticks(range(len(p1)))
    ax.set_yticklabels([f"{v:.3g}" for v in p1])
    ax.set_xlabel(p2_key)
    ax.set_ylabel(p1_key)
    ax.set_title(f"E[BD] (% TVL): {p1_key} x {p2_key}")

    # Annotate cells
    for i in range(len(p1)):
        for j in range(len(p2)):
            if not np.isnan(grid[i, j]):
                ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center",
                        fontsize=8, color="white" if grid[i, j] > grid[~np.isnan(grid)].mean() else "black")

    fig.colorbar(im, ax=ax, label="E[BD] % TVL")
    fig.tight_layout()
    safe_name = name or f"{p1_key}_x_{p2_key}".replace(" ", "_")
    _savefig(fig, output_dir, f"06_interaction_{safe_name}")


# ── Deliverable 7: Analytical Bound ──────────────────────────────────


def save_bound_table(bound_data: dict, output_dir: Path):
    """Save analytical bound table as CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "07_analytical_bound.csv"
    rows = bound_data["bound_table"]
    if not rows:
        return
    keys = rows[0].keys()
    with open(path, "w") as f:
        f.write(",".join(keys) + "\n")
        for row in rows:
            f.write(",".join(f"{row[k]:.4f}" if isinstance(row[k], float) else str(row[k]) for k in keys) + "\n")
    print(f"    Saved: 07_analytical_bound.csv")


# ── Deliverable 8: 3D Safe Region Surface ────────────────────────────


def plot_safe_region(surface_data: dict, output_dir: Path):
    """
    3D surface plot of safe operating region.

    Shows BD_max contours in (crash × LTV) space for different α values.
    """
    crash = surface_data["crash_range"]
    ltv = surface_data["ltv_range"]
    bd = surface_data["bd_surface"]
    decay = surface_data["decay_range"]

    # Pick 3 representative α values
    alpha_indices = [0, len(decay) // 2, -1]

    fig, axes = plt.subplots(len(alpha_indices), 1, figsize=(8, 14),
                              sharex=True)

    threshold = 5.0  # % TVL
    for ax_idx, di in enumerate(alpha_indices):
        ax = axes[ax_idx]
        C, L = np.meshgrid(crash * 100, ltv, indexing="ij")
        Z = bd[:, di, :]

        cf = ax.contourf(C, L, Z, levels=20, cmap="RdYlGn_r")
        ax.contour(C, L, Z, levels=[threshold], colors="white", linewidths=2)
        ax.set_ylabel("LTV")
        if ax_idx == len(alpha_indices) - 1:
            ax.set_xlabel("Crash Magnitude (%)")
        ax.set_title(f"α = {decay[di]:.4f}")

    fig.suptitle("BD_max (% TVL) — white contour = 5% threshold", fontsize=13)
    cbar = fig.colorbar(cf, ax=axes, shrink=0.8, location="left")
    cbar.set_label("BD_max (% TVL)", color="white")
    cbar.ax.tick_params(labelcolor="white")
    cbar.outline.set_edgecolor("white")
    for text in cbar.ax.get_yticklabels() + cbar.ax.get_xticklabels():
        text.set_color("white")
    fig.tight_layout()
    _savefig(fig, output_dir, "08_safe_region")


# ── Deliverable 9: Parameter Recommendations ─────────────────────────


def save_recommendations(safe_configs: list[dict], bound_data: dict, output_dir: Path):
    """Save parameter recommendation summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "09_recommendations.txt"
    with open(path, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("Bad Debt Risk Quantification — Parameter Recommendations\n")
        f.write("=" * 60 + "\n\n")

        if safe_configs:
            f.write("Safe configurations (BD bound < 5% for 50% crash):\n\n")
            for cfg in safe_configs:
                f.write(
                    f"  alpha={cfg['decay']:.4f} "
                    f"(HL={cfg['half_life_hours']:.1f}h)  "
                    f"LTV={cfg['ltv']:.4f}  "
                    f"BD_bound={cfg['bd_bound_pct']:.2f}%\n"
                )
        else:
            f.write("No configurations found with BD < 5% for 50% crash.\n")
            f.write("Consider reducing LTV or using faster oracle decay.\n")

        f.write("\n" + "=" * 60 + "\n")
    print(f"    Saved: 09_recommendations.txt")
