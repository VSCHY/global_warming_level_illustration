# Global Warming Levels, Explained with Data & Code

Code and data for the article:
<https://medium.com/p/0322f9f8fdb3>

Reproduces every figure for **Toulouse** (lat 43.6, lon 1.4) from CMIP6
projections, using a tiny pandas + matplotlib pipeline.

## Layout

```
data/
  tasmax_daily.csv     raw — date, scenario, tasmax_C        (shipped)
  gmst_annual.csv      raw — year, scenario, gmst_C          (shipped)
  hot_days_annual.csv     ─┐
  gmst_anomaly_20yr.csv    ├─ derived by 1_calculate_indicators.py
  crossings.csv            │
  hot_days_at_gwl.csv     ─┘
1_calculate_indicators.py    raw CSVs → derived CSVs
2_plot_step1.py              annual GMST
3_plot_step2.py              20-yr rolling anomaly vs 1850–1900
4_plot_step3.py              first-crossing year per GWL
5_plot_step4.py              hot-days distribution at each GWL
6_plot_combined.py           2×2 combined figure
_plots.py / _style.py        shared helpers
figures/                     PNG outputs
```

Only `tasmax_daily.csv` and `gmst_annual.csv` ship with the repo. Run
script 1 to generate the four derived CSVs, then any of the plot scripts.

## Run

```bash
uv run python 1_calculate_indicators.py
uv run python 2_plot_step1.py
uv run python 3_plot_step2.py
uv run python 4_plot_step3.py
uv run python 5_plot_step4.py
uv run python 6_plot_combined.py
```

Optional — pick a custom GWL list:

```bash
uv run python 1_calculate_indicators.py --gwls 1.0 1.5 2.0 3.0 4.0
```

## What script 1 computes

| Function                               | What it does                                       |
|----------------------------------------|----------------------------------------------------|
| `hot_days_annual(tasmax_daily)`        | count days > 35 °C per calendar year               |
| `gmst_anomaly_20yr(gmst_annual)`       | 20-yr centred rolling mean − 1850–1900 mean        |
| `crossings(anomaly_df, gwls)`          | first year where ΔT ≥ each GWL                     |
| `hot_days_at_gwl(hot_days, crossings)` | 20-yr window of hot_days centred on each crossing  |

## Notes

- Default GWLs: 1.0, 1.5, 2.0, 3.0 °C.
- Baseline 1850–1900; rolling window 20 years (centred).
- Scenarios: ssp1_2_6, ssp2_4_5, ssp3_7_0, ssp5_8_5 (whichever are present).
- Reference CMIP6 model: `cnrm_cm6_1`.
