"""
visualizer.py
─────────────
Generates matplotlib complexity graphs from benchmark_results.json.

Plots produced:
  1. All-algorithms overview   (time vs n, log scale)
  2. Per-complexity-class grid (one subplot per Big-O class)
  3. Complexity class heat map (relative slowdown at max n)
  4. Theoretical vs Actual overlay for each algorithm
"""

import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from collections import defaultdict


# ── Load data ────────────────────────────────────────────────────────────────

RESULTS_FILE = Path(__file__).parent / "benchmark_results.json"
OUTPUT_DIR   = Path(__file__).parent / "plots"

def load_results(path: Path = RESULTS_FILE) -> dict:
    with open(path) as f:
        return json.load(f)


# ── Theoretical curves ───────────────────────────────────────────────────────

def theoretical_curve(complexity: str, n_arr: np.ndarray) -> np.ndarray:
    """Return a normalised theoretical curve for the given Big-O class."""
    n = n_arr.astype(float)
    n = np.where(n < 1, 1, n)

    curves = {
        "O(1)":       np.ones_like(n),
        "O(log n)":   np.log2(n),
        "O(n)":       n,
        "O(n log n)": n * np.log2(n),
        "O(n²)":      n ** 2,
        "O(n³)":      n ** 3,
    }
    raw = curves.get(complexity, n)
    # normalise to [0, 1]
    rng = raw.max() - raw.min()
    return raw / rng if rng > 0 else raw


# ── Plot 1: All-algorithms overview ─────────────────────────────────────────

def plot_overview(data: dict, out: Path):
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    for name, meta in data["algorithms"].items():
        sizes    = np.array(meta["sizes"])
        times    = np.array(meta["times_ms"])
        color    = meta["color"]
        ax.plot(sizes, times, "o-", color=color, linewidth=2,
                markersize=4, label=f"{name}  [{meta['complexity']}]", alpha=0.9)

    ax.set_yscale("log")
    ax.set_xlabel("Input Size  (n)", color="#c9d1d9", fontsize=12)
    ax.set_ylabel("Time  (ms, log scale)", color="#c9d1d9", fontsize=12)
    ax.set_title("Algorithm Complexity — Overview (Log Scale)",
                 color="#e6edf3", fontsize=15, fontweight="bold", pad=16)

    ax.tick_params(colors="#c9d1d9")
    ax.spines[:].set_color("#30363d")
    ax.grid(True, color="#21262d", linestyle="--", alpha=0.7)

    legend = ax.legend(fontsize=9, facecolor="#161b22", edgecolor="#30363d",
                       labelcolor="#c9d1d9", loc="upper left", ncol=2)
    plt.tight_layout()
    fig.savefig(out / "01_overview.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ 01_overview.png")


# ── Plot 2: Per-complexity-class grid ────────────────────────────────────────

def plot_class_grid(data: dict, out: Path):
    # Group algorithms by complexity class
    groups = defaultdict(list)
    for name, meta in data["algorithms"].items():
        groups[meta["complexity"]].append((name, meta))

    n_groups = len(groups)
    cols = 3
    rows = math.ceil(n_groups / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    fig.patch.set_facecolor("#0d1117")
    axes_flat = axes.flatten() if n_groups > 1 else [axes]

    for ax_idx, (complexity, members) in enumerate(sorted(groups.items())):
        ax = axes_flat[ax_idx]
        ax.set_facecolor("#161b22")

        for name, meta in members:
            sizes = np.array(meta["sizes"])
            times = np.array(meta["times_ms"])
            ax.plot(sizes, times, "o-", color=meta["color"],
                    linewidth=2, markersize=4, label=name, alpha=0.9)

        ax.set_title(complexity, color="#e6edf3", fontsize=13, fontweight="bold")
        ax.set_xlabel("n", color="#8b949e", fontsize=9)
        ax.set_ylabel("ms", color="#8b949e", fontsize=9)
        ax.tick_params(colors="#8b949e", labelsize=8)
        ax.spines[:].set_color("#30363d")
        ax.grid(True, color="#21262d", linestyle="--", alpha=0.6)
        ax.legend(fontsize=8, facecolor="#0d1117", edgecolor="#30363d",
                  labelcolor="#c9d1d9")

    # Hide unused subplots
    for i in range(ax_idx + 1, len(axes_flat)):
        axes_flat[i].set_visible(False)

    fig.suptitle("Complexity Classes — Grouped", color="#e6edf3",
                 fontsize=16, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "02_class_grid.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ 02_class_grid.png")


# ── Plot 3: Theoretical vs Actual overlay ────────────────────────────────────

def plot_theoretical_overlay(data: dict, out: Path):
    algos = data["algorithms"]
    n_algos = len(algos)
    cols = 3
    rows = math.ceil(n_algos / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    fig.patch.set_facecolor("#0d1117")
    axes_flat = axes.flatten()

    for ax_idx, (name, meta) in enumerate(algos.items()):
        ax = axes_flat[ax_idx]
        ax.set_facecolor("#161b22")

        sizes    = np.array(meta["sizes"], dtype=float)
        times    = np.array(meta["times_ms"])

        # Normalise actual times to [0,1]
        t_range = times.max() - times.min()
        t_norm  = (times - times.min()) / t_range if t_range > 0 else times

        # Theoretical curve
        theo = theoretical_curve(meta["complexity"], sizes)

        ax.plot(sizes, t_norm, "o-", color=meta["color"],
                linewidth=2, markersize=5, label="Actual (normalised)", alpha=0.9)
        ax.plot(sizes, theo, "--", color="#ffffff",
                linewidth=1.5, alpha=0.5, label=f"Theory {meta['complexity']}")

        ax.set_title(name, color="#e6edf3", fontsize=10, fontweight="bold")
        ax.set_xlabel("n", color="#8b949e", fontsize=8)
        ax.set_ylabel("Normalised time", color="#8b949e", fontsize=8)
        ax.tick_params(colors="#8b949e", labelsize=7)
        ax.spines[:].set_color("#30363d")
        ax.grid(True, color="#21262d", linestyle="--", alpha=0.6)
        ax.legend(fontsize=7, facecolor="#0d1117", edgecolor="#30363d",
                  labelcolor="#c9d1d9")

    for i in range(ax_idx + 1, len(axes_flat)):
        axes_flat[i].set_visible(False)

    fig.suptitle("Actual vs Theoretical Complexity", color="#e6edf3",
                 fontsize=16, fontweight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig(out / "03_actual_vs_theoretical.png", dpi=150,
                bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ 03_actual_vs_theoretical.png")


# ── Plot 4: Heatmap — relative slowdown ──────────────────────────────────────

def plot_heatmap(data: dict, out: Path):
    algos = data["algorithms"]
    names = list(algos.keys())
    # Max-n time for each algo
    max_times = [meta["times_ms"][-1] for meta in algos.values()]
    baseline  = min(t for t in max_times if t > 0)

    # Slowdown factors
    slowdowns = [t / baseline for t in max_times]
    log_slow  = [math.log10(max(s, 1)) for s in slowdowns]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    cmap = plt.cm.RdYlGn_r
    bars = ax.barh(names, log_slow, color=[algos[n]["color"] for n in names],
                   edgecolor="#30363d", linewidth=0.8)

    for bar, sd in zip(bars, slowdowns):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"×{sd:.1f}", va="center", color="#e6edf3", fontsize=9)

    ax.set_xlabel("log₁₀(Slowdown vs fastest at max n)", color="#c9d1d9", fontsize=11)
    ax.set_title("Relative Slowdown at Largest Input Size",
                 color="#e6edf3", fontsize=14, fontweight="bold")
    ax.tick_params(colors="#c9d1d9")
    ax.spines[:].set_color("#30363d")
    ax.grid(True, axis="x", color="#21262d", linestyle="--", alpha=0.6)

    plt.tight_layout()
    fig.savefig(out / "04_heatmap.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  ✓ 04_heatmap.png")


# ── Entry point ──────────────────────────────────────────────────────────────

def generate_all_plots(results_path: Path = RESULTS_FILE,
                       output_dir:   Path = OUTPUT_DIR):
    data = load_results(results_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Generating Plots ===")
    plot_overview(data, output_dir)
    plot_class_grid(data, output_dir)
    plot_theoretical_overlay(data, output_dir)
    plot_heatmap(data, output_dir)

    print(f"\n✅  All plots saved → {output_dir}/")
    return output_dir


if __name__ == "__main__":
    generate_all_plots()
