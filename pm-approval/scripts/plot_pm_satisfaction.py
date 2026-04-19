"""
Plot PM net-satisfaction trajectories from the CSV produced by fetch_ipsos.py.

Run:
    python plot_pm_satisfaction.py

Outputs:
    ../out/pm_satisfaction.png
    ../out/pm_satisfaction.svg
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "data" / "pm_satisfaction.csv"
OUT = HERE.parent / "out"

# Order + colours chosen to echo the example plot; not load-bearing.
ORDER = ["blair", "brown", "cameron", "may", "johnson", "truss", "sunak", "starmer"]


def main() -> int:
    if not CSV.exists():
        print(f"ERROR: {CSV} not found. Run fetch_ipsos.py first.", file=sys.stderr)
        return 1

    df = pd.read_csv(CSV)
    OUT.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    for pm in ORDER:
        sub = df[df["pm"] == pm].sort_values("months_in_office")
        if sub.empty:
            print(f"WARN: no rows for {pm}", file=sys.stderr)
            continue
        ax.plot(sub["months_in_office"], sub["net_satisfaction"], label=sub["label"].iloc[0])

    ax.axhline(0, color="#999", linewidth=0.8)
    ax.set_xlabel("Months in office")
    ax.set_ylabel("Net satisfaction (Ipsos: satisfied − dissatisfied)")
    ax.set_title("UK Prime Minister satisfaction trajectories")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    for ext in ("png", "svg"):
        path = OUT / f"pm_satisfaction.{ext}"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
