"""
Step 1 — Derive every indicator the article uses, from the two raw CSVs.

Inputs (produced by 0_export_raw.py):
    data/tasmax_daily.csv     date, scenario, tasmax_C
    data/gmst_annual.csv      year, scenario, gmst_C

Outputs (this script):
    data/hot_days_annual.csv     ← from tasmax_daily
    data/gmst_anomaly_20yr.csv   ← from gmst_annual
    data/crossings.csv           ← from gmst_anomaly_20yr
    data/hot_days_at_gwl.csv     ← from hot_days_annual + crossings

Pure pandas. No xarray, no `src/`, no `.workdir/`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

# Method constants (match src/gwl_analysis.py)
BASELINE = (1850, 1900)
ROLLING_WINDOW = 20
DEFAULT_GWLS = (1.0, 1.5, 2.0, 3.0)
THRESHOLD_C = 35.0


# ---------------------------------------------------------------------------
# Step 1a — annual count of days above 35 °C (from daily tasmax)
# ---------------------------------------------------------------------------
def hot_days_annual(tasmax_daily: pd.DataFrame, threshold_c: float = THRESHOLD_C) -> pd.DataFrame:
    df = tasmax_daily.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    out = (
        (df["tasmax_C"] > threshold_c)
        .groupby([df["scenario"], df["year"]])
        .sum()
        .rename("hot_days")
        .reset_index()[["year", "scenario", "hot_days"]]
        .astype({"hot_days": int})
        .sort_values(["scenario", "year"])
        .reset_index(drop=True)
    )
    return out


# ---------------------------------------------------------------------------
# Step 1b — 20-yr rolling anomaly vs 1850–1900 (from annual GMST)
# ---------------------------------------------------------------------------
def gmst_anomaly_20yr(
    gmst_annual: pd.DataFrame,
    baseline: tuple[int, int] = BASELINE,
    window: int = ROLLING_WINDOW,
) -> pd.DataFrame:
    """
    ΔT(t) = mean of yearly GMST over [t - window/2, t + window/2 - 1]
            minus the 1850–1900 mean.
    Computed per scenario.
    """
    out = []
    for scenario, sub in gmst_annual.groupby("scenario"):
        sub = sub.sort_values("year").set_index("year")
        ref = sub.loc[baseline[0]:baseline[1], "gmst_C"].mean()
        rolled = (
            sub["gmst_C"]
            .rolling(window=window, center=True, min_periods=window)
            .mean()
        )
        out.append(pd.DataFrame({
            "year": rolled.index.astype(int),
            "scenario": scenario,
            "anomaly_C": (rolled - ref).round(4).values,
        }))
    return (
        pd.concat(out, ignore_index=True)
        .dropna(subset=["anomaly_C"])
        .sort_values(["scenario", "year"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Step 1c — first-crossing year per (scenario, GWL)
# ---------------------------------------------------------------------------
def crossings(anomaly_df: pd.DataFrame, gwls: tuple[float, ...]) -> pd.DataFrame:
    rows = []
    for scenario, sub in anomaly_df.groupby("scenario"):
        sub = sub.sort_values("year")
        for g in gwls:
            mask = sub["anomaly_C"].values >= g
            yr = int(sub["year"].values[mask][0]) if mask.any() else None
            rows.append({"scenario": scenario, "gwl": float(g), "crossing_year": yr})
    return (
        pd.DataFrame(rows)
        .sort_values(["gwl", "scenario"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Step 1d — 20-yr window of hot_days centered on each crossing year
# ---------------------------------------------------------------------------
def hot_days_at_gwl(
    hot_days_df: pd.DataFrame,
    crossings_df: pd.DataFrame,
    window: int = ROLLING_WINDOW,
) -> pd.DataFrame:
    half = window // 2
    rows = []
    for _, row in crossings_df.dropna(subset=["crossing_year"]).iterrows():
        yr = int(row["crossing_year"])
        sub = hot_days_df[
            (hot_days_df["scenario"] == row["scenario"])
            & (hot_days_df["year"] >= yr - half)
            & (hot_days_df["year"] <= yr + half - 1)
        ]
        for _, r in sub.iterrows():
            rows.append({
                "gwl": float(row["gwl"]),
                "scenario": row["scenario"],
                "year": int(r["year"]),
                "hot_days": int(r["hot_days"]),
            })
    return (
        pd.DataFrame(rows)
        .sort_values(["gwl", "scenario", "year"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gwls", type=float, nargs="+", default=list(DEFAULT_GWLS))
    args = p.parse_args()
    gwls = tuple(sorted(set(args.gwls)))

    print(f"Calculating indicators (baseline {BASELINE[0]}–{BASELINE[1]}, "
          f"window {ROLLING_WINDOW} yr, GWLs {list(gwls)})")

    tasmax_daily = pd.read_csv(DATA_DIR / "tasmax_daily.csv")
    gmst_annual = pd.read_csv(DATA_DIR / "gmst_annual.csv")

    print("[1/4] hot_days_annual ← tasmax_daily")
    hd = hot_days_annual(tasmax_daily)
    hd.to_csv(DATA_DIR / "hot_days_annual.csv", index=False)

    print("[2/4] gmst_anomaly_20yr ← gmst_annual")
    anom = gmst_anomaly_20yr(gmst_annual)
    anom.to_csv(DATA_DIR / "gmst_anomaly_20yr.csv", index=False)

    print("[3/4] crossings ← gmst_anomaly_20yr")
    cr = crossings(anom, gwls)
    cr.to_csv(DATA_DIR / "crossings.csv", index=False)

    print("[4/4] hot_days_at_gwl ← hot_days_annual + crossings")
    win = hot_days_at_gwl(hd, cr)
    win.to_csv(DATA_DIR / "hot_days_at_gwl.csv", index=False)

    print("Done. Run any `2_plot_*.py` next.")


if __name__ == "__main__":
    main()
