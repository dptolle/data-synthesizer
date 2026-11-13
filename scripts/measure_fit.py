"""Measure wall time and peak memory of a fit on a generated FAKE file.

Usage: uv run python scripts/measure_fit.py [rows] [--fit-rows N]
The big file goes to a temp directory and is deleted afterwards.
Peak memory is the child's peak working set (Windows) or max RSS (Linux/macOS).
"""

import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

CHILD = """
import sys
from csv_synth.cli import app
try:
    app()
except SystemExit:
    pass
finally:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class C(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t)] + [
                (n, ctypes.c_size_t) for n in ("WorkingSetSize", "QuotaPeakPagedPoolUsage",
                 "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                 "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        c = C(); c.cb = ctypes.sizeof(C)
        k = ctypes.windll.kernel32
        k.GetCurrentProcess.restype = wintypes.HANDLE
        gp = ctypes.WinDLL("psapi").GetProcessMemoryInfo
        gp.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        gp(k.GetCurrentProcess(), ctypes.byref(c), c.cb)
        peak = c.PeakWorkingSetSize
    else:
        import resource
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    print("PEAK_BYTES", peak)
"""


def fake_csv(path: Path, rows: int) -> None:
    rng = np.random.default_rng(0)
    pd.DataFrame(
        {
            "nights": rng.integers(1, 15, rows),
            "adults": rng.integers(1, 5, rows),
            "room_type": rng.choice(["single", "double", "suite", "family"], rows),
            "country": rng.choice([f"Country{i}" for i in range(8)], rows),
            "total_price": rng.normal(400, 120, rows).round(2),
            "rating": np.where(
                rng.random(rows) < 0.5, np.nan, rng.uniform(1, 5, rows).round(1)
            ),
            "breakfast_included": rng.choice(["yes", "no"], rows),
        }
    ).to_csv(path, index=False)


if __name__ == "__main__":
    args = sys.argv[1:]
    extra = []
    if "--fit-rows" in args:
        i = args.index("--fit-rows")
        extra = args[i : i + 2]
        del args[i : i + 2]
    n = int(args[0]) if args else 100_000
    with tempfile.TemporaryDirectory() as d:
        src, out = Path(d) / "fake.csv", Path(d) / "fake_synthetic.csv"
        fake_csv(src, n)
        t0 = time.perf_counter()
        r = subprocess.run(
            [sys.executable, "-c", CHILD, "generate", str(src), "-o", str(out), "--seed", "1", *extra],
            cwd=d,
            capture_output=True,
            text=True,
        )
        wall = time.perf_counter() - t0
        peak = next(
            (int(l.split()[1]) for l in r.stdout.splitlines() if l.startswith("PEAK_BYTES")), 0
        )
        print(f"rows={n} {' '.join(extra)} exit={r.returncode} wall={wall:.1f}s peak={peak / 2**20:.0f} MiB")
        if r.returncode:
            print(r.stderr[-500:])
