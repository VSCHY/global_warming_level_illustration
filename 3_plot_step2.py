"""Step 2 — 20-yr rolling anomaly vs 1850–1900."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from _plots import draw_step2
from _style import DATA_DIR, save


def main() -> None:
    df = pd.read_csv(DATA_DIR / "gmst_anomaly_20yr.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    draw_step2(ax, df)
    fig.tight_layout()
    save(fig, "gwl_step2.png")


if __name__ == "__main__":
    main()
