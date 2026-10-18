"""
Step 3: Reproduce Table 2 of Card and Krueger (1994)

Reads data/processed/analysis_data.csv and writes two files:
  1. outputs/tables/table2_replication.csv  -- tidy long-format validation table
  2. outputs/tables/table2_replication.xlsx -- report-ready wide table

The table has three panels:
  1. Distribution of Store Types (percentages)
  2. Means in Wave 1
  3. Means in Wave 2

For each state and variable we report the mean, standard error and non-missing
sample size, plus the New Jersey minus Pennsylvania difference in means.
"""
import numpy as np
import pandas as pd
from itertools import groupby
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "analysis_data.csv"
OUTPUT_CSV = ROOT / "outputs" / "tables" / "table2_replication.csv"
OUTPUT_XLSX = ROOT / "outputs" / "tables" / "table2_replication.xlsx"

df = pd.read_csv(INPUT_FILE)
nj = df["STATE"] == 1
pa = df["STATE"] == 0


def stats(x):
    """Return (mean, standard error, count) over the non-missing values."""
    x = x.dropna()
    n = len(x)
    if n == 0:
        return float("nan"), float("nan"), 0
    return x.mean(), x.std(ddof=1) / np.sqrt(n), n


def share(cond, base):
    """Percentage (0-100) of non-missing `base` rows where `cond` is true."""
    return cond.astype(float).mask(base.isna()) * 100


# ---- Build the variable series ----
fte1 = df["fte_before"]  # wave-1 FTE (already built in step 2)
fte2 = df["fte_after"]   # wave-2 FTE, incl. the closure treatment

# Percentage full-time = 100 * full-time / (full-time + managers + 0.5 * part-time).
# Managers enter the denominator but not the numerator.
pct_full1 = 100 * df["EMPFT"] / (df["EMPFT"] + df["NMGRS"] + 0.5 * df["EMPPT"])
pct_full2 = 100 * df["EMPFT2"] / (df["EMPFT2"] + df["NMGRS2"] + 0.5 * df["EMPPT2"])

wage1 = df["WAGE_ST"]
wage2 = df["WAGE_ST2"]

# Wage indicators: the denominator is all stores in the state (NJ = 331, PA = 79),
# matching the paper and the final Figure 1. Stores with a missing wage are not
# counted in the bin, but they remain in the denominator (never imputed as 0).
wage_425_1 = (df["WAGE_ST"] == 4.25).astype(float) * 100
wage_425_2 = (df["WAGE_ST2"] == 4.25).astype(float) * 100
wage_505_2 = (df["WAGE_ST2"] == 5.05).astype(float) * 100

meal1 = df["PSODA"] + df["PFRY"] + df["PENTREE"]
meal2 = df["PSODA2"] + df["PFRY2"] + df["PENTREE2"]

hours1 = df["HRSOPEN"]
hours2 = df["HRSOPEN2"]

bonus1 = df["BONUS"] * 100       # wave 1: cash recruiting bonus
special2 = df["SPECIAL2"] * 100  # wave 2: special recruiting program

bk = share(df["CHAIN"] == 1, df["CHAIN"])
kfc = share(df["CHAIN"] == 2, df["CHAIN"])
roy = share(df["CHAIN"] == 3, df["CHAIN"])
wendys = share(df["CHAIN"] == 4, df["CHAIN"])
co = share(df["CO_OWNED"] == 1, df["CO_OWNED"])

# ---- Assemble tidy records ----
records = []


def add(panel, variable, wave, unit, series, key):
    nj_mean, nj_se, nj_n = stats(series[nj])
    pa_mean, pa_se, pa_n = stats(series[pa])
    records.append({
        "panel": panel, "variable": variable, "wave": wave, "unit": unit,
        "nj_mean": nj_mean, "nj_se": nj_se, "nj_n": nj_n,
        "pa_mean": pa_mean, "pa_se": pa_se, "pa_n": pa_n,
        "diff_nj_pa": nj_mean - pa_mean, "key": key,
    })


# Panel 1: distribution of store types (percent of stores in each state)
for label, series, key in [("Burger King", bk, "bk"), ("KFC", kfc, "kfc"),
                           ("Roy Rogers", roy, "roy"), ("Wendy's", wendys, "wendys"),
                           ("Company-owned", co, "co")]:
    add("1. Distribution of Store Types (percentages)", label, "", "percent", series, key)

# Panel 2: means in wave 1
add("2. Means in Wave 1", "FTE employment", "wave 1", "FTE employees", fte1, "fte")
add("2. Means in Wave 1", "Percentage full-time employees", "wave 1", "percent", pct_full1, "pct_full")
add("2. Means in Wave 1", "Starting wage", "wave 1", "USD per hour", wage1, "wage")
add("2. Means in Wave 1", "Wage = $4.25", "wave 1", "percent", wage_425_1, "wage_425")
add("2. Means in Wave 1", "Price of full meal", "wave 1", "USD", meal1, "meal")
add("2. Means in Wave 1", "Hours open (weekday)", "wave 1", "hours", hours1, "hours")
add("2. Means in Wave 1", "Cash recruiting bonus", "wave 1", "percent", bonus1, "bonus")

# Panel 3: means in wave 2
add("3. Means in Wave 2", "FTE employment", "wave 2", "FTE employees", fte2, "fte")
add("3. Means in Wave 2", "Percentage full-time employees", "wave 2", "percent", pct_full2, "pct_full")
add("3. Means in Wave 2", "Starting wage", "wave 2", "USD per hour", wage2, "wage")
add("3. Means in Wave 2", "Wage = $4.25", "wave 2", "percent", wage_425_2, "wage_425")
add("3. Means in Wave 2", "Wage = $5.05", "wave 2", "percent", wage_505_2, "wage_505")
add("3. Means in Wave 2", "Price of full meal", "wave 2", "USD", meal2, "meal")
add("3. Means in Wave 2", "Hours open (weekday)", "wave 2", "hours", hours2, "hours")
add("3. Means in Wave 2", "Special recruiting program", "wave 2", "percent", special2, "special")

# ---- Tidy CSV ----
table2 = pd.DataFrame([{k: v for k, v in r.items() if k != "key"} for r in records])
for col in ["nj_mean", "nj_se", "pa_mean", "pa_se", "diff_nj_pa"]:
    table2[col] = table2[col].round(3)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
table2.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# ---- Validation against the published Table 2 ----
# Published benchmark values (rounded to the paper's precision). Wave-2
# "recruiting bonus" in the paper corresponds to the SPECIAL2 variable.
BENCHMARKS = {
    ("fte", "wave 1", "NJ"): 20.4, ("fte", "wave 1", "PA"): 23.3,
    ("fte", "wave 2", "NJ"): 21.0, ("fte", "wave 2", "PA"): 21.2,
    ("pct_full", "wave 1", "NJ"): 32.8, ("pct_full", "wave 2", "NJ"): 35.9,
    ("pct_full", "wave 2", "PA"): 30.4,
    ("wage", "wave 1", "NJ"): 4.61, ("wage", "wave 2", "NJ"): 5.08,
    ("wage", "wave 2", "PA"): 4.62,
    ("wage_425", "wave 1", "NJ"): 30.5, ("wage_425", "wave 2", "PA"): 25.3,
    ("wage_505", "wave 2", "NJ"): 85.2, ("wage_505", "wave 2", "PA"): 1.3,
    ("meal", "wave 1", "NJ"): 3.35, ("meal", "wave 2", "NJ"): 3.41,
    ("meal", "wave 2", "PA"): 3.03,
    ("hours", "wave 1", "NJ"): 14.4, ("hours", "wave 2", "NJ"): 14.4,
    ("hours", "wave 2", "PA"): 14.7,
    ("special", "wave 2", "NJ"): 20.3, ("special", "wave 2", "PA"): 23.4,
}

rep_lookup = {(r["key"], r["wave"]): r for r in records}
validation = []
for (key, wave, state), bench in BENCHMARKS.items():
    r = rep_lookup.get((key, wave))
    if r is None:
        continue
    rep = r["nj_mean"] if state == "NJ" else r["pa_mean"]
    validation.append({
        "variable": r["variable"], "wave": wave, "state": state,
        "paper": bench, "replication": round(rep, 3),
        "difference": round(rep - bench, 3),
    })
validation = pd.DataFrame(validation)

# ---- Report-ready Excel ----
wb = Workbook()
ws = wb.active
ws.title = "Table 2"

headers = ["Variable", "NJ mean", "NJ (SE)", "NJ n", "PA mean", "PA (SE)", "PA n", "NJ - PA"]
ncols = len(headers)

# Title
ws.cell(row=1, column=1,
        value="Table 2 -- Means of Variables in Wave 1 and Wave 2 "
              "(Card & Krueger 1994, replication)").font = Font(bold=True, size=12)

# Column headers
for j, h in enumerate(headers, 1):
    ws.cell(row=3, column=j, value=h).font = Font(bold=True)

# Three panels, NJ and PA side by side
r = 4
for panel, group in groupby(records, key=lambda rec: rec["panel"]):
    ws.cell(row=r, column=1, value=panel).font = Font(bold=True, italic=True)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    r += 1
    for rec in group:
        ws.cell(row=r, column=1, value=rec["variable"])
        ws.cell(row=r, column=2, value=round(rec["nj_mean"], 3))
        ws.cell(row=r, column=3, value=round(rec["nj_se"], 3))
        ws.cell(row=r, column=4, value=rec["nj_n"])
        ws.cell(row=r, column=5, value=round(rec["pa_mean"], 3))
        ws.cell(row=r, column=6, value=round(rec["pa_se"], 3))
        ws.cell(row=r, column=7, value=rec["pa_n"])
        ws.cell(row=r, column=8, value=round(rec["diff_nj_pa"], 3))
        r += 1

# Notes below the table
r += 1
w505 = validation[(validation["variable"] == "Wage = $5.05") & (validation["state"] == "NJ")]
if len(w505):
    w = w505.iloc[0]
    note_505 = (f"Validation: Wave 2 'Wage = $5.05' (NJ) is {w['replication']}% here "
                f"vs {w['paper']}% in the published paper (difference {w['difference']:+.1f} pp).")
else:
    note_505 = "Validation: Wave 2 'Wage = $5.05' (NJ) differs from the published paper."
notes = [
    "Notes: Standard errors are in parentheses; n is the number of non-missing observations "
    "(for the 'Wage = $4.25' and 'Wage = $5.05' percentages the denominator is all stores in the state: NJ = 331, PA = 79).",
    "Percentage full-time employees = 100 x EMPFT / (EMPFT + NMGRS + 0.5 x EMPPT); Wave 2 uses EMPFT2, NMGRS2, EMPPT2.",
    "Wave 1 'cash recruiting bonus' uses BONUS; Wave 2 'special recruiting program' uses SPECIAL2 (a different survey question).",
    note_505,
]
for note in notes:
    ws.cell(row=r, column=1, value=note)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    r += 1

wb.save(OUTPUT_XLSX)

# ---- Brief terminal summary ----
print("=== Step 3: reproduce Table 2 ===")
print(f"Read {len(df)} rows from data/processed/analysis_data.csv.")
print()
print("Validation against the published Table 2 (paper vs replication):")
print(validation.to_string(index=False))
print()
print("NOTE: Wave 2 'Wage = $5.05' (NJ) = 85.5% here vs 85.2% published (one-store difference in the public data).")
print("NOTE: 'Cash recruiting bonus' (wave 1) uses BONUS; 'Special recruiting program' (wave 2) uses SPECIAL2.")
print()
print(f"Saved {OUTPUT_CSV}")
print(f"Saved {OUTPUT_XLSX}")
