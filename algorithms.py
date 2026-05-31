"""
algorithms.py
─────────────
Algorithm implementations across all major Big-O complexity classes.

Each algorithm is wrapped in a dict entry with:
  - 'fn'         : callable(data) → any
  - 'complexity' : theoretical Big-O label
  - 'color'      : hex color for plotting
  - 'category'   : grouping label

Input convention: every function accepts a single list 'data'.
"""

import math
import random


# ════════════════════════════════════════════════════════════════════════════
#  O(1) — Constant
# ════════════════════════════════════════════════════════════════════════════

def constant_access(data: list):
    """Always accesses the first element. O(1)."""
    if not data:
        return None
    return data[0]


# ════════════════════════════════════════════════════════════════════════════
#  O(log n) — Logarithmic
# ════════════════════════════════════════════════════════════════════════════

def binary_search(data: list):
    """Binary search on a sorted copy. O(log n)."""
    arr = sorted(data)
    target = arr[len(arr) // 2]          # search for median element
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ════════════════════════════════════════════════════════════════════════════
#  O(n) — Linear
# ════════════════════════════════════════════════════════════════════════════

def linear_search(data: list):
    """Find maximum via full scan. O(n)."""
    if not data:
        return None
    max_val = data[0]
    for x in data:
        if x > max_val:
            max_val = x
    return max_val


def prefix_sum(data: list):
    """Build prefix sum array. O(n)."""
    result = []
    total = 0
    for x in data:
        total += x
        result.append(total)
    return result


# ════════════════════════════════════════════════════════════════════════════
#  O(n log n) — Linearithmic
# ════════════════════════════════════════════════════════════════════════════

def merge_sort(data: list) -> list:
    """Classic merge sort. O(n log n) guaranteed."""
    if len(data) <= 1:
        return data[:]
    mid   = len(data) // 2
    left  = merge_sort(data[:mid])
    right = merge_sort(data[mid:])
    # merge
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(data: list) -> list:
    """Heap sort. O(n log n)."""
    import heapq
    h = data[:]
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]


# ════════════════════════════════════════════════════════════════════════════
#  O(n²) — Quadratic
# ════════════════════════════════════════════════════════════════════════════

def bubble_sort(data: list) -> list:
    """Bubble sort. O(n²)."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def selection_sort(data: list) -> list:
    """Selection sort. O(n²)."""
    arr = data[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(data: list) -> list:
    """Insertion sort. O(n²)."""
    arr = data[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


# ════════════════════════════════════════════════════════════════════════════
#  O(n³) — Cubic
# ════════════════════════════════════════════════════════════════════════════

def matrix_multiply(data: list):
    """
    Naïve O(n³) matrix multiplication.
    'data' is treated as a flat list → reshaped to √len × √len matrices.
    """
    n = max(1, int(math.isqrt(len(data))))
    # Build two n×n matrices from data (cycle if needed)
    A = [[data[(i * n + j) % len(data)] for j in range(n)] for i in range(n)]
    B = [[data[(i * n + j + 1) % len(data)] for j in range(n)] for i in range(n)]
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


# ════════════════════════════════════════════════════════════════════════════
#  Registry — add/remove algorithms here
# ════════════════════════════════════════════════════════════════════════════

ALGORITHMS = {
    # name                  fn                 complexity    color       category
    "Constant Access":   {"fn": constant_access,  "complexity": "O(1)",        "color": "#06d6a0", "category": "Search"},
    "Binary Search":     {"fn": binary_search,    "complexity": "O(log n)",    "color": "#118ab2", "category": "Search"},
    "Linear Search":     {"fn": linear_search,    "complexity": "O(n)",        "color": "#ffd166", "category": "Search"},
    "Prefix Sum":        {"fn": prefix_sum,       "complexity": "O(n)",        "color": "#f4a261", "category": "Array"},
    "Merge Sort":        {"fn": merge_sort,       "complexity": "O(n log n)",  "color": "#7b2d8b", "category": "Sorting"},
    "Heap Sort":         {"fn": heap_sort,        "complexity": "O(n log n)",  "color": "#9b5de5", "category": "Sorting"},
    "Insertion Sort":    {"fn": insertion_sort,   "complexity": "O(n²)",       "color": "#ef476f", "category": "Sorting"},
    "Selection Sort":    {"fn": selection_sort,   "complexity": "O(n²)",       "color": "#e63946", "category": "Sorting"},
    "Bubble Sort":       {"fn": bubble_sort,      "complexity": "O(n²)",       "color": "#ff6b6b", "category": "Sorting"},
    "Matrix Multiply":   {"fn": matrix_multiply,  "complexity": "O(n³)",       "color": "#ff4d4d", "category": "Matrix"},
}


def generate_input(n: int, kind: str = "random") -> list:
    """
    Generate benchmark input of size n.

    kind options:
      'random'  — shuffled integers  (avg-case)
      'sorted'  — already sorted     (best-case for some)
      'reverse' — reverse sorted     (worst-case bubble/insertion)
    """
    base = list(range(n))
    if kind == "random":
        random.shuffle(base)
    elif kind == "reverse":
        base = base[::-1]
    # 'sorted' is already sorted
    return base
