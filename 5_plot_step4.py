"""Step 4 — Distribution of hot_days at each GWL (all scenarios pooled)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from _plots import draw_step4
from _style import DATA_DIR, save


def main() -> None:
    df = pd.read_csv(DATA_DIR / "hot_days_at_gwl.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    draw_step4(ax, df)
    fig.tight_layout()
    save(fig, "gwl_step4.png")


if __name__ == "__main__":
    main()
