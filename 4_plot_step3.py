"""Step 3 — First-crossing year per scenario × GWL."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from _plots import draw_step3
from _style import DATA_DIR, save


def main() -> None:
    anomaly = pd.read_csv(DATA_DIR / "gmst_anomaly_20yr.csv")
    crossings = pd.read_csv(DATA_DIR / "crossings.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    draw_step3(ax, anomaly, crossings)
    fig.tight_layout()
    save(fig, "gwl_step3.png")


if __name__ == "__main__":
    main()
