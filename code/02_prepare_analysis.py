"""
Step 2: Prepare analysis data

Read data/raw/public.csv (read-only, without modifying the original data) and
produce two English files:
  1. data/processed/analysis_data.csv  -- cleaned data for later analysis
  2. outputs/tables/04_analysis_sample_summary.csv  -- sample summary

Adds the FTE variables used by the paper, applies the closure treatments, and
does not fill any other missing values.
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Project root: this file lives in code/, so its parent is the project root
ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw" / "public.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
TABLES_DIR = ROOT / "outputs" / "tables"

# Read the data (read-only; the original file is not modified)
df = pd.read_csv(INPUT_FILE)

# ---------- Build the analysis variables ----------
# Full-time-equivalent employment: full-time + managers + 0.5 * part-time
df["fte_before"] = df["EMPFT"] + df["NMGRS"] + 0.5 * df["EMPPT"]
df["fte_after"] = df["EMPFT2"] + df["NMGRS2"] + 0.5 * df["EMPPT2"]

# Apply the paper's closure treatments
df.loc[df["STATUS2"] == 3, "fte_after"] = 0                # permanent closure -> 0 employees
df.loc[df["STATUS2"].isin([2, 4, 5]), "fte_after"] = np.nan  # temporary closure -> missing

df["fte_change"] = df["fte_after"] - df["fte_before"]

df["nj"] = (df["STATE"] == 1).astype(int)
df["status2"] = df["STATUS2"]
df["permanent_closure"] = (df["STATUS2"] == 3).astype(int)
df["temporary_closure"] = (df["STATUS2"].isin([2, 4, 5])).astype(int)

# ---------- Save the analysis data ----------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_DIR / "analysis_data.csv", index=False, encoding="utf-8-sig")

# ---------- Build the sample summary table ----------
summary = pd.DataFrame({
    "metric": [
        "total observations",
        "New Jersey observations",
        "Pennsylvania observations",
        "permanent closures",
        "temporary closures",
        "observations with valid fte_before",
        "observations with valid fte_after",
        "balanced FTE sample",
    ],
    "value": [
        len(df),
        int(df["nj"].sum()),
        int((df["nj"] == 0).sum()),
        int(df["permanent_closure"].sum()),
        int(df["temporary_closure"].sum()),
        int(df["fte_before"].notna().sum()),
        int(df["fte_after"].notna().sum()),
        int((df["fte_before"].notna() & df["fte_after"].notna()).sum()),
    ],
})
summary.to_csv(TABLES_DIR / "04_analysis_sample_summary.csv", index=False, encoding="utf-8-sig")

# ---------- Brief terminal summary ----------
print("=== Step 2: prepare analysis data ===")
print(f"Read {len(df)} rows and saved data/processed/analysis_data.csv.")
print()
for _, row in summary.iterrows():
    print(f"{row['metric']}: {row['value']}")
print()
print("Sample summary saved to outputs/tables/04_analysis_sample_summary.csv.")
