"""
Step 1: Data inspection

Read data/raw/public.csv (read-only, without modifying the original data),
produce three tables under outputs/tables/, and print a brief summary:
  1. Data overview table (rows, columns, restaurant counts by state)
  2. STATUS2 counts table (with status meaning)
  3. Missing-value table (missing count and proportion per variable)
"""
import pandas as pd
from pathlib import Path

# Project root: this file lives in code/, so its parent is the project root
ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "raw" / "public.csv"
OUTPUT_DIR = ROOT / "outputs" / "tables"

# Read the data (read-only; the original file is not modified)
df = pd.read_csv(INPUT_FILE)

# Make sure the output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Table 1: data overview ----------
n_rows, n_cols = df.shape
n_nj = (df["STATE"] == 1).sum()  # New Jersey
n_pa = (df["STATE"] == 0).sum()  # Pennsylvania

overview = pd.DataFrame({
    "metric": ["total rows", "total columns",
               "New Jersey restaurants (STATE=1)", "Pennsylvania restaurants (STATE=0)"],
    "value": [n_rows, n_cols, n_nj, n_pa],
})
overview.to_csv(OUTPUT_DIR / "01_data_overview.csv", index=False, encoding="utf-8-sig")

# ---------- Table 2: STATUS2 counts ----------
# Meaning of each second-survey status
status_meaning = {
    0: "refused",
    1: "answered",
    2: "renovation closure",
    3: "permanent closure",
    4: "highway-construction closure",
    5: "mall-fire closure",
}

# value_counts(dropna=False) also counts missing values
status_counts = df["STATUS2"].value_counts(dropna=False).sort_index()

codes = []   # status code ("missing" shown for missing)
labels = []  # status meaning
for code in status_counts.index:
    if pd.isna(code):
        codes.append("missing")
        labels.append("missing")
    else:
        codes.append(int(code))
        labels.append(status_meaning.get(int(code), f"unknown code {code}"))

status_table = pd.DataFrame({
    "status2": codes,
    "status_label": labels,
    "count": status_counts.values,
})
status_table.to_csv(OUTPUT_DIR / "02_status2_counts.csv", index=False, encoding="utf-8-sig")

# ---------- Table 3: missing values ----------
missing_table = pd.DataFrame({
    "variable": df.columns,
    "missing_count": df.isna().sum().values,
    "missing_percentage": df.isna().mean().round(4).values,
})
missing_table.to_csv(OUTPUT_DIR / "03_missing_values.csv", index=False, encoding="utf-8-sig")

# ---------- Brief terminal summary ----------
print("=== Step 1: data inspection results ===")
print(f"The data has {n_rows} rows and {n_cols} columns.")
print(f"New Jersey restaurants: {n_nj}; Pennsylvania restaurants: {n_pa}.")
print()
print("STATUS2 counts by status:")
for _, row in status_table.iterrows():
    print(f"  status {row['status2']} ({row['status_label']}): {row['count']} restaurants")
print()
n_missing_cols = int((df.isna().sum() > 0).sum())
print(f"Of {len(df.columns)} variables, {n_missing_cols} have missing values.")
print("Three tables were saved to outputs/tables/.")
