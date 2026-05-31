"""
main.py
───────
Entry point for the CPU-Pinned Algorithm Complexity Profiler.

Usage:
    python main.py                   # full run  (pin + benchmark + plot)
    python main.py --skip-bench      # re-plot from existing results
    python main.py --core 2          # pin to physical core 2
    python main.py --input reverse   # benchmark on reverse-sorted input
"""

import sys
import argparse
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(
        description="CPU-Pinned Algorithm Complexity Profiler"
    )
    p.add_argument("--core",       type=int, default=0,
                   help="Physical core ID to pin to (default: 0)")
    p.add_argument("--trials",     type=int, default=7,
                   help="Timing trials per (algo, n) pair (default: 7)")
    p.add_argument("--input",      choices=["random", "sorted", "reverse"],
                   default="random",
                   help="Input distribution (default: random)")
    p.add_argument("--skip-bench", action="store_true",
                   help="Skip benchmarking; re-use existing results JSON")
    p.add_argument("--no-plot",    action="store_true",
                   help="Skip plot generation")
    return p.parse_args()


def main():
    args = parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║      CPU-Pinned Algorithm Complexity Profiler            ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # ── Step 1: CPU Affinity ─────────────────────────────────────────────────
    import cpu_affinity

    print("▶  Step 1/3 — CPU Core Setup")
    info = cpu_affinity.get_core_info()
    print(f"   Physical cores  : {info['physical_cores']}")
    print(f"   Logical cores   : {info['logical_cores']}")
    print(f"   Hyperthreading  : {info['hyperthreading']}")

    affinity = cpu_affinity.pin_to_physical_core(args.core)
    if affinity["success"]:
        print(f"   ✅  Pinned to physical core {args.core} "
              f"→ logical {affinity['pinned_logical_cores']}")
    else:
        print(f"   ⚠️   Affinity pin failed ({affinity['error']}); "
              f"benchmarks will still run but may have noise.")

    # ── Step 2: Benchmark ────────────────────────────────────────────────────
    results_path = Path(__file__).parent / "benchmark_results.json"

    if not args.skip_bench:
        import benchmarker

        # Override module-level config with CLI args
        benchmarker.TRIALS     = args.trials
        benchmarker.INPUT_KIND = args.input

        print(f"\n▶  Step 2/3 — Benchmarking  "
              f"({args.trials} trials, '{args.input}' input)")
        results = benchmarker.run_benchmarks(verbose=True)
        benchmarker.save_results(
            results,
            results_path,
            cpu_meta=cpu_affinity.affinity_for_results_meta(affinity),
        )
    else:
        print(f"\n▶  Step 2/3 — Skipping benchmark (using {results_path})")
        if not results_path.exists():
            print("   ✗  No results file found. Run without --skip-bench first.")
            sys.exit(1)

    # ── Step 3: Visualise ────────────────────────────────────────────────────
    if not args.no_plot:
        import visualizer

        print("\n▶  Step 3/3 — Generating Plots")
        plot_dir = visualizer.generate_all_plots(results_path)
        print(f"\n   Open   plots/  to view all complexity graphs.")
        print(f"   Or open dashboard.html for the interactive version.\n")
    else:
        print("\n▶  Step 3/3 — Plot generation skipped (--no-plot)")

    # ── Release affinity ─────────────────────────────────────────────────────
    cpu_affinity.release_affinity()
    print("✅  Done!  CPU affinity released.\n")


if __name__ == "__main__":
    main()
