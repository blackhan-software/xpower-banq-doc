"""
Bad Debt Risk Quantification — CLI Entry Point

Usage:
    python -m paper.simulation.sim_debt oracle-lag     # Section 3
    python -m paper.simulation.sim_debt backtest       # Section 4
    python -m paper.simulation.sim_debt montecarlo     # Section 5
    python -m paper.simulation.sim_debt sensitivity    # Section 6 (requires MC)
    python -m paper.simulation.sim_debt bound          # Section 7
    python -m paper.simulation.sim_debt all            # Full pipeline
    python -m paper.simulation.sim_debt validate       # Cross-validation tests

Run from the repository root.
"""
import argparse
import sys
import json
import numpy as np
from pathlib import Path

from . import config


def _output_dir(args) -> Path:
    return Path(args.output)


def cmd_oracle_lag(args):
    """Section 3: Oracle Lag Model."""
    from .analysis.oracle_lag import run_all
    from .viz.plots import (
        plot_oracle_lag_heatmap,
        plot_oracle_convergence_curves,
        save_phantom_window_table,
        save_blind_time_table,
    )

    print("Section 3: Oracle Lag Model")
    decay = config.ALPHA_SWEEP[args.alpha_index] if args.alpha_index is not None else config.DEFAULT_DECAY
    results = run_all(decay=decay)
    out = _output_dir(args)

    print("  Generating charts...")
    plot_oracle_lag_heatmap(results["lag_heatmap"], out)
    plot_oracle_convergence_curves(results["lag_heatmap"], out)
    save_phantom_window_table(results["phantom_windows"], out)
    save_blind_time_table(results["blind_times"], out)
    print("  Done.")


def cmd_backtest(args):
    """Section 4: Historical Backtesting."""
    from .data.fetch import load_all_crash_data
    from .analysis.backtest import run_all_backtests
    from .viz.plots import plot_backtest_timeline, save_backtest_summary

    print("Section 4: Historical Backtesting")
    print("  Loading crash data...")
    crash_data = load_all_crash_data()

    if not crash_data:
        print("  ERROR: No crash data available. Check network connection or cached data.")
        return

    print(f"  Loaded {len(crash_data)} events.")
    results = run_all_backtests(
        crash_data,
        n_positions=args.positions,
        seed=args.seed,
    )

    out = _output_dir(args)
    print("  Generating charts...")
    save_backtest_summary(results["summaries"], out)

    # Plot timeline for baseline LTV and lock=0 for each event
    for event_name, event_result in results["per_event"].items():
        baseline_ltv = config.LTV_SWEEP[0]
        if baseline_ltv in event_result["details"] and 0.0 in event_result["details"][baseline_ltv]:
            plot_backtest_timeline(
                event_result["details"][baseline_ltv][0.0],
                event_name,
                out,
            )
    print("  Done.")


def cmd_montecarlo(args):
    """Section 5: Monte Carlo Simulation."""
    from .analysis.montecarlo import run_mc_sweep, run_mc_quick
    from .viz.plots import (
        plot_mc_histogram,
        save_mc_summary,
        plot_drawdown_vs_bad_debt,
        plot_time_to_liquidation,
    )

    print("Section 5: Monte Carlo Simulation")
    out = _output_dir(args)

    if args.quick:
        print(f"  Quick mode: {args.paths} paths, single parameter set")
        result = run_mc_quick(
            n_paths=args.paths,
            seed=args.seed,
            verbose=True,
        )
        plot_mc_histogram(result, out, label="quick")
        plot_drawdown_vs_bad_debt(result, out, label="quick")
        plot_time_to_liquidation(result, out, label="quick")
        print(f"  E[BD] = {result['metrics']['expected_bd']:.4f}%")
        print(f"  VaR(99%) = {result['metrics']['var_99']:.4f}%")
        print(f"  CVaR(99%) = {result['metrics']['cvar_99']:.4f}%")

        # Extra runs at higher LTVs for paper figures
        for extra_ltv, tag in [(2/3, "ltv67"), (0.75, "ltv75")]:
            print(f"\n  Extra run: LTV={extra_ltv:.2f}")
            r = run_mc_quick(
                n_paths=args.paths,
                ltv=extra_ltv,
                seed=args.seed,
                verbose=True,
            )
            plot_mc_histogram(r, out, label=tag)
            plot_drawdown_vs_bad_debt(r, out, label=tag)
            print(f"  E[BD] = {r['metrics']['expected_bd']:.4f}%")
            print(f"  VaR(99%) = {r['metrics']['var_99']:.4f}%")
            print(f"  CVaR(99%) = {r['metrics']['cvar_99']:.4f}%")
    else:
        print(f"  Full sweep: {args.paths} paths × 240 parameter combinations")
        results = run_mc_sweep(
            n_paths=args.paths,
            seed=args.seed,
            chunk_size=args.chunk_size,
            verbose=True,
        )
        save_mc_summary(results["summary"], out)

        # Plot histogram + drawdown curve + delay hist for first result
        if results["results"]:
            first = results["results"][0]
            plot_mc_histogram(first, out, label="baseline")
            plot_drawdown_vs_bad_debt(first, out, label="baseline")
            plot_time_to_liquidation(first, out, label="baseline")

        # Save raw results for sensitivity analysis
        summary_path = out / "mc_results.json"
        with open(summary_path, "w") as f:
            serializable = []
            for row in results["summary"]:
                serializable.append({
                    k: float(v) if isinstance(v, (int, float)) else v
                    for k, v in row.items()
                })
            json.dump(serializable, f, indent=2)
        print(f"    Saved: mc_results.json")

    print("  Done.")


def _run_extra_sensitivity(args, n_paths: int) -> dict:
    """Run MC with varied price impact k and jump intensity for tornado."""
    from .analysis.montecarlo import run_mc_with_params

    extra = {"price_impact_k": [], "jump_intensity": []}

    print("  Running price impact k sweep...")
    for k in config.PRICE_IMPACT_SWEEP:
        result = run_mc_with_params(
            n_paths=n_paths,
            jd_params=config.JD_PARAMS_ETH,
            seed=args.seed,
            price_impact_k=k,
        )
        extra["price_impact_k"].append((k, result["metrics"]["expected_bd"]))
        print(f"    k={k:.2f}: E[BD]={result['metrics']['expected_bd']:.4f}%")

    print("  Running jump intensity λ_J sweep...")
    for lj in config.JUMP_INTENSITY_SWEEP:
        jd = {**config.JD_PARAMS_ETH, "lambda_j": lj}
        result = run_mc_with_params(
            n_paths=n_paths,
            jd_params=jd,
            seed=args.seed,
        )
        extra["jump_intensity"].append((lj, result["metrics"]["expected_bd"]))
        print(f"    λ_J={lj:.1f}: E[BD]={result['metrics']['expected_bd']:.4f}%")

    return extra


def _run_lock_x_price_impact(args, n_paths: int) -> dict:
    """Run MC for lock fraction × price impact k interaction grid."""
    from .analysis.montecarlo import run_mc_with_params

    locks = config.LOCK_FRACTION_SWEEP
    ks = config.PRICE_IMPACT_SWEEP

    grid = np.full((len(locks), len(ks)), np.nan)
    print("  Running lock × price impact grid...")
    for i, lock in enumerate(locks):
        for j, k in enumerate(ks):
            result = run_mc_with_params(
                n_paths=n_paths,
                jd_params=config.JD_PARAMS_ETH,
                seed=args.seed,
                lock_fraction=lock,
                price_impact_k=k,
            )
            grid[i, j] = result["metrics"]["expected_bd"]

    return {
        "grid": grid,
        "param1_values": locks,
        "param2_values": ks,
        "param1_key": "lock_fraction",
        "param2_key": "price_impact_k",
        "metric": "expected_bd",
    }


def cmd_sensitivity(args):
    """Section 6: Sensitivity Analysis (requires MC results)."""
    from .analysis.sensitivity import (
        extract_tornado_extended,
        compute_all_interactions,
    )
    from .viz.plots import plot_tornado, plot_interaction_heatmap

    print("Section 6: Sensitivity Analysis")
    out = _output_dir(args)
    results_path = out / "mc_results.json"

    if not results_path.exists():
        print(f"  ERROR: MC results not found at {results_path}")
        print("  Run 'montecarlo' first.")
        return

    with open(results_path) as f:
        mc_summary = json.load(f)

    # Extra sensitivity runs for k and λ_J (use fewer paths for speed)
    sens_paths = min(args.paths, 1000)
    extra_runs = _run_extra_sensitivity(args, sens_paths)
    lock_k_interaction = _run_lock_x_price_impact(args, sens_paths)

    print("  Computing tornado diagram...")
    tornado = extract_tornado_extended(mc_summary, extra_runs)
    plot_tornado(tornado, out)

    print("  Computing interaction heatmaps...")
    interactions = compute_all_interactions(
        mc_summary,
        extra_interactions={"lock_x_price_impact": lock_k_interaction},
    )
    for name, data in interactions.items():
        plot_interaction_heatmap(data, out, name=name)

    print("  Done.")


def cmd_bound(args):
    """Section 7: Analytical Bound."""
    from .analysis.analytical_bound import run_all
    from .viz.plots import save_bound_table, plot_safe_region, save_recommendations

    print("Section 7: Analytical Bound")
    results = run_all()
    out = _output_dir(args)

    print("  Generating outputs...")
    save_bound_table(results, out)
    plot_safe_region(results["surface"], out)
    save_recommendations(results["safe_configs"], results, out)

    n_safe = len(results["safe_configs"])
    print(f"  Found {n_safe} safe configurations (BD < 5% for 50% crash).")
    print("  Done.")


def cmd_check_bound(args):
    """Verify analytical bound exceeds all MC results (§9 acceptance criterion 3)."""
    from .analysis.analytical_bound import bad_debt_bound

    print("Bound Conservatism Check")
    out = _output_dir(args)
    results_path = out / "mc_results.json"

    if not results_path.exists():
        print(f"  ERROR: MC results not found at {results_path}")
        print("  Run 'montecarlo' first.")
        return

    with open(results_path) as f:
        mc_summary = json.load(f)

    violations = []
    checked = 0
    for row in mc_summary:
        ltv = row.get("ltv", 0)
        decay = row.get("decay", 0)
        mc_max_bd = row.get("max_bd", 0)

        # Bound for the worst crash the MC paths experienced
        # Use the max drawdown from MC as proxy for crash magnitude
        # (conservative: use 50% as reference crash)
        for crash in [0.30, 0.50, 0.70]:
            bound = bad_debt_bound(crash, decay, ltv)
            checked += 1
            if mc_max_bd > bound:
                violations.append({
                    "ltv": ltv,
                    "decay": decay,
                    "crash": crash,
                    "mc_max": mc_max_bd,
                    "bound": bound,
                })

    if violations:
        print(f"  WARNING: {len(violations)} violations found (bound < MC max):")
        for v in violations[:10]:
            print(f"    LTV={v['ltv']:.2f} α={v['decay']:.4f} crash={v['crash']:.0%}: "
                  f"MC_max={v['mc_max']:.2f}% > bound={v['bound']:.2f}%")
    else:
        print(f"  PASS: All {checked} bound checks satisfied (bound >= MC max).")

    print("  Done.")


def cmd_all(args):
    """Run full pipeline."""
    print("=" * 60)
    print("Bad Debt Risk Quantification — Full Pipeline")
    print("=" * 60)

    cmd_oracle_lag(args)
    print()

    cmd_bound(args)
    print()

    cmd_backtest(args)
    print()

    cmd_montecarlo(args)
    print()

    cmd_sensitivity(args)
    print()

    cmd_check_bound(args)
    print()

    print("=" * 60)
    print("All deliverables generated.")
    print("=" * 60)


def cmd_validate(args):
    """Run cross-validation tests."""
    import subprocess
    test_dir = Path(__file__).parent / "tests"
    print(f"Running tests in {test_dir}...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir), "-v"],
        cwd=Path(__file__).parent.parent.parent.parent,
    )
    sys.exit(result.returncode)


def main():
    default_output = str(Path(__file__).parent / "output")

    parser = argparse.ArgumentParser(
        description="Bad Debt Risk Quantification — XPower Banq",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=[
            "oracle-lag", "backtest", "montecarlo", "sensitivity",
            "bound", "check-bound", "all", "validate",
        ],
        help="Analysis to run",
    )
    parser.add_argument("--seed", type=int, default=config.MC_SEED, help="Random seed")
    parser.add_argument("--paths", type=int, default=config.MC_NUM_PATHS, help="MC paths")
    parser.add_argument("--positions", type=int, default=config.MC_NUM_POSITIONS, help="Positions per pool")
    parser.add_argument("--output", type=str, default=default_output, help="Output directory")
    parser.add_argument("--chunk-size", type=int, default=10_000, help="MC chunk size")
    parser.add_argument("--quick", action="store_true", help="Quick MC (single param set)")
    parser.add_argument("--alpha-index", type=int, default=None, help="Index into ALPHA_SWEEP")

    args = parser.parse_args()

    commands = {
        "oracle-lag": cmd_oracle_lag,
        "backtest": cmd_backtest,
        "montecarlo": cmd_montecarlo,
        "sensitivity": cmd_sensitivity,
        "bound": cmd_bound,
        "check-bound": cmd_check_bound,
        "all": cmd_all,
        "validate": cmd_validate,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
