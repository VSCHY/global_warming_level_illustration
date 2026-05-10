"""Step 1 — Annual mean GMST per scenario."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from _plots import draw_step1
from _style import DATA_DIR, save


def main() -> None:
    df = pd.read_csv(DATA_DIR / "gmst_annual.csv")
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    draw_step1(ax, df)
    fig.tight_layout()
    save(fig, "gwl_step1.png")


if __name__ == "__main__":
    main()
