"""
benchmarker.py
──────────────
Times every algorithm across a range of input sizes (n) on the
pinned CPU core and saves results to benchmark_results.json.

Key design decisions:
  • Uses time.perf_counter() — highest resolution timer available.
  • Runs each (algo, n) pair TRIALS times and takes the MEDIAN to
    suppress outliers (cache effects, OS interrupts).
  • O(n³) algorithms are capped at smaller n to keep runtime sane.
  • Saves JSON so the HTML dashboard can load it without re-running.
"""

import json
import time
import statistics
from pathlib import Path

from algorithms import ALGORITHMS, generate_input


# ── Configuration ────────────────────────────────────────────────────────────

# Input sizes to benchmark
INPUT_SIZES = [50, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000]

# Sizes used for O(n³) only (very slow — keep small!)
CUBIC_SIZES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Number of repeated trials per (algo, n); median is kept
TRIALS = 7

# Input distribution ('random' | 'sorted' | 'reverse')
INPUT_KIND = "random"

OUTPUT_FILE = Path(__file__).parent / "benchmark_results.json"


# ── Core timing function ─────────────────────────────────────────────────────

def time_algorithm(fn, data: list, trials: int = TRIALS) -> dict:
    """
    Run fn(data) 'trials' times and return timing stats (seconds).
    """
    timings = []
    for _ in range(trials):
        # Fresh copy so in-place sorts don't gain an advantage
        d = data[:]
        t0 = time.perf_counter()
        fn(d)
        t1 = time.perf_counter()
        timings.append(t1 - t0)

    return {
        "median_s":  statistics.median(timings),
        "mean_s":    statistics.mean(timings),
        "min_s":     min(timings),
        "max_s":     max(timings),
        "stdev_s":   statistics.stdev(timings) if len(timings) > 1 else 0.0,
    }


# ── Main benchmark runner ────────────────────────────────────────────────────

def run_benchmarks(verbose: bool = True) -> dict:
    """
    Benchmark all algorithms across all input sizes.
    Returns a dict structured for JSON export.
    """
    results = {}
    total_algos = len(ALGORITHMS)

    for algo_idx, (name, meta) in enumerate(ALGORITHMS.items(), 1):
        fn          = meta["fn"]
        complexity  = meta["complexity"]
        color       = meta["color"]
        category    = meta["category"]

        is_cubic = complexity == "O(n³)"
        sizes    = CUBIC_SIZES if is_cubic else INPUT_SIZES

        if verbose:
            print(f"\n[{algo_idx}/{total_algos}] {name}  ({complexity})")
            print(f"  sizes: {sizes}")

        size_data   = []
        timing_data = []

        for n in sizes:
            data    = generate_input(n, INPUT_KIND)
            stats   = time_algorithm(fn, data, TRIALS)
            elapsed = stats["median_s"] * 1000   # → milliseconds

            size_data.append(n)
            timing_data.append(round(elapsed, 6))

            if verbose:
                print(f"  n={n:>5}  →  {elapsed:>10.4f} ms  "
                      f"(σ={stats['stdev_s']*1000:.4f} ms)")

        results[name] = {
            "complexity": complexity,
            "color":      color,
            "category":   category,
            "sizes":      size_data,
            "times_ms":   timing_data,
        }

    return results


def save_results(
    results: dict,
    path: Path = OUTPUT_FILE,
    cpu_meta: dict | None = None,
) -> Path:
    """Persist benchmark results to JSON. Optional cpu_meta comes from cpu_affinity.affinity_for_results_meta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "trials": TRIALS,
        "input_kind": INPUT_KIND,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if cpu_meta:
        meta["cpu"] = cpu_meta
    payload = {
        "meta": meta,
        "algorithms": results,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\n✅  Results saved → {path}")
    return path


# ── Self-contained run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    import cpu_affinity

    print("=== CPU Affinity Setup ===")
    affinity = cpu_affinity.pin_to_physical_core(0)
    for k, v in affinity.items():
        print(f"  {k}: {v}")

    print("\n=== Running Benchmarks ===")
    results = run_benchmarks(verbose=True)
    save_results(results, cpu_meta=cpu_affinity.affinity_for_results_meta(affinity))
