"""
cpu_affinity.py
───────────────
Pins the current process to a single physical CPU core for fair,
noise-free algorithm benchmarking.

Why this matters:
  - OS scheduler normally migrates processes between cores.
  - Migration causes cache invalidation → unpredictable timing noise.
  - Pinning to one core gives consistent, reproducible measurements.
"""

import os
import psutil


def get_core_info() -> dict:
    """Return info about available physical and logical cores."""
    physical = psutil.cpu_count(logical=False)
    logical  = psutil.cpu_count(logical=True)
    ht_ratio = logical // physical if physical else 1

    return {
        "physical_cores": physical,
        "logical_cores":  logical,
        "hyperthreading": ht_ratio > 1,
        "ht_ratio":       ht_ratio,
    }


def pin_to_physical_core(physical_core_id: int = 0) -> dict:
    """
    Pin the current process to a specific physical CPU core.

    On hyperthreaded CPUs, one physical core has 2 logical cores.
    We pin to BOTH logical siblings so the OS stays on that physical core.

    Parameters
    ----------
    physical_core_id : int
        Index of the physical core to pin to (0-based).

    Returns
    -------
    dict with affinity details.
    """
    info = get_core_info()
    p    = psutil.Process(os.getpid())

    physical = info["physical_cores"]

    if physical_core_id >= physical:
        raise ValueError(
            f"Requested physical core {physical_core_id} but only "
            f"{physical} physical cores exist (0–{physical - 1})."
        )

    # Logical core siblings for this physical core
    ht_ratio = info["ht_ratio"]
    logical_siblings = [
        physical_core_id + i * physical
        for i in range(ht_ratio)
    ]

    try:
        p.cpu_affinity(logical_siblings)
        success = True
        error   = None
    except (psutil.AccessDenied, AttributeError, OSError) as exc:
        # macOS doesn't support cpu_affinity; fall back gracefully
        success = False
        error   = str(exc)
        logical_siblings = p.cpu_affinity()   # read current

    result = {
        "requested_physical_core": physical_core_id,
        "pinned_logical_cores":    logical_siblings,
        "success":                 success,
        "error":                   error,
        **info,
    }
    return result


def affinity_for_results_meta(affinity: dict) -> dict:
    """
    Fields to store in benchmark_results.json for the HTML dashboard.
    Documents which physical core was dedicated and which logical CPUs that maps to.
    """
    return {
        "physical_cores": affinity.get("physical_cores"),
        "logical_cores": affinity.get("logical_cores"),
        "hyperthreading": affinity.get("hyperthreading"),
        "ht_ratio": affinity.get("ht_ratio"),
        "requested_physical_core": affinity.get("requested_physical_core"),
        "pinned_logical_cores": list(affinity.get("pinned_logical_cores") or []),
        "affinity_success": bool(affinity.get("success")),
        **({"affinity_error": affinity.get("error")} if not affinity.get("success") else {}),
    }


def release_affinity() -> list:
    """Allow process to run on all logical cores again."""
    p = psutil.Process(os.getpid())
    all_cores = list(range(psutil.cpu_count(logical=True)))
    try:
        p.cpu_affinity(all_cores)
    except (psutil.AccessDenied, AttributeError):
        pass
    return all_cores


# ── Quick self-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    info = get_core_info()
    print("=== CPU Info ===")
    for k, v in info.items():
        print(f"  {k}: {v}")

    print("\n=== Pinning to physical core 0 ===")
    result = pin_to_physical_core(0)
    for k, v in result.items():
        print(f"  {k}: {v}")
