# Algorithm Complexity Profiler (Python)

A CPU-pinned algorithm complexity profiler: it benchmarks algorithms across input
sizes, pins the process to a CPU core for stable timings, and visualizes the
results (actual vs. theoretical complexity, heatmaps, dashboards).

## Stack
Python · NumPy · Matplotlib · psutil (CPU affinity)

## Run
```bash
pip install -r requirements.txt
python main.py                 # pin + benchmark + plot
python main.py --skip-bench    # re-plot from existing benchmark_results.json
```

Outputs benchmark plots (`plots/`, `*.png`) and an interactive `dashboard.html`.
