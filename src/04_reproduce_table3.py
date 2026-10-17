"""
Step 4: Reproduce Table 3 of Card and Krueger (1994)

"Average employment per store before and after the rise in the New Jersey
minimum wage": the difference-in-differences of FTE employment between New
Jersey and Pennsylvania, plus the New Jersey wage-group comparison.

Reads output/analysis_data.csv and writes:
  1. output/tables/table3_replication.csv  -- tidy long-format table
  2. output/tables/table3_replication.xlsx -- report-ready wide table + Notes sheet

Standard errors for level means are analytic (SD / sqrt(n)). Standard errors for
changes and differences are computed by a store-level bootstrap: restaurants are
resampled with replacement separately within each state, and every statistic is
recomputed on each resample. This is because the paper does not state a
standard-error formula for row 3, whose before/after samples are overlapping but
not identical.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

SEED = 42
N_BOOT = 2000

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "output" / "analysis_data.csv"
OUTPUT_CSV = ROOT / "output" / "tables" / "table3_replication.csv"
OUTPUT_XLSX = ROOT / "output" / "tables" / "table3_replication.xlsx"

df = pd.read_csv(INPUT_FILE)

# ---- Full-sample masks (used for sample sizes and analytic SEs) ----
nj_mask = df["nj"] == 1
pa_mask = df["nj"] == 0
low_mask = nj_mask & (df["WAGE_ST"] == 4.25)
mid_mask = nj_mask & (df["WAGE_ST"] >= 4.26) & (df["WAGE_ST"] <= 4.99)
high_mask = nj_mask & (df["WAGE_ST"] >= 5.00)
group_masks = {"PA": pa_mask, "NJ": nj_mask, "low": low_mask,
               "mid": mid_mask, "high": high_mask}

fte_after_alt = df["fte_after"].where(df["temporary_closure"] == 0, 0.0)
change_alt = fte_after_alt - df["fte_before"]
bal = df["fte_before"].notna() & df["fte_after"].notna()
valid_alt = df["fte_before"].notna() & fte_after_alt.notna()

ROWS = ["before", "after", "change_all", "change_balanced", "change_temp0"]
RESULT_COLS = ["PA", "NJ", "NJ-PA", "low", "mid", "high", "low-high", "mid-high"]
DIRECT = ["PA", "NJ", "low", "mid", "high"]  # columns with a sample size


def compute_cells(d):
    """Every Table 3 cell value for a (possibly resampled) dataframe `d`."""
    dnj = d["nj"] == 1
    groups = {
        "PA": d["nj"] == 0,
        "NJ": dnj,
        "low": dnj & (d["WAGE_ST"] == 4.25),
        "mid": dnj & (d["WAGE_ST"] >= 4.26) & (d["WAGE_ST"] <= 4.99),
        "high": dnj & (d["WAGE_ST"] >= 5.00),
    }
    d_after_alt = d["fte_after"].where(d["temporary_closure"] == 0, 0.0)
    d_change_alt = d_after_alt - d["fte_before"]
    d_bal = d["fte_before"].notna() & d["fte_after"].notna()
    d_valid_alt = d["fte_before"].notna() & d_after_alt.notna()

    cells = {}
    for name, mask in groups.items():
        cells[("before", name)] = d.loc[mask, "fte_before"].mean()
        cells[("after", name)] = d.loc[mask, "fte_after"].mean()
        cells[("change_all", name)] = cells[("after", name)] - cells[("before", name)]
        cells[("change_balanced", name)] = d.loc[d_bal & mask, "fte_change"].mean()
        cells[("change_temp0", name)] = d_change_alt[d_valid_alt & mask].mean()
    for row in ROWS:
        cells[(row, "NJ-PA")] = cells[(row, "NJ")] - cells[(row, "PA")]
        cells[(row, "low-high")] = cells[(row, "low")] - cells[(row, "high")]
        cells[(row, "mid-high")] = cells[(row, "mid")] - cells[(row, "high")]
    return cells


# ---- Point estimates ----
point = compute_cells(df)

# ---- Store-level bootstrap (resample within each state) ----
rng = np.random.default_rng(SEED)
nj_pos = np.flatnonzero(df["nj"].to_numpy() == 1)
pa_pos = np.flatnonzero(df["nj"].to_numpy() == 0)

boot = {cell: np.empty(N_BOOT) for cell in point}
for b in range(N_BOOT):
    idx = np.concatenate([
        rng.choice(nj_pos, size=len(nj_pos), replace=True),
        rng.choice(pa_pos, size=len(pa_pos), replace=True),
    ])
    d = df.iloc[idx].reset_index(drop=True)
    for cell, val in compute_cells(d).items():
        boot[cell][b] = val

se_boot = {cell: float(np.std(boot[cell], ddof=1)) for cell in point}


def analytic_se(series, mask):
    x = series[mask].dropna()
    n = len(x)
    return float(x.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")


def cell_n(row, col):
    if col not in DIRECT:
        return None
    mask = group_masks[col]
    if row == "before":
        return int(df.loc[mask, "fte_before"].notna().sum())
    if row == "after":
        return int(df.loc[mask, "fte_after"].notna().sum())
    if row == "change_balanced":
        return int((bal & mask).sum())
    if row == "change_temp0":
        return int((valid_alt & mask).sum())
    return None  # change_all uses all available observations (two waves differ)


ROW_LABEL = {
    "before": "1. FTE employment before, all available",
    "after": "2. FTE employment after, all available",
    "change_all": "3. Change in mean FTE, all available",
    "change_balanced": "4. Change in mean FTE, balanced sample",
    "change_temp0": "5. Change in mean FTE, temporary closed = 0",
}
COL_LABEL = {
    "PA": "PA", "NJ": "NJ", "NJ-PA": "Difference, NJ - PA",
    "low": "Wage = $4.25", "mid": "Wage = $4.26-$4.99", "high": "Wage >= $5.00",
    "low-high": "Low - High", "mid-high": "Midrange - High",
}

# ---- Assemble every cell (estimate / se / t / n / se_method) ----
cell_data = {}
for row in ROWS:
    for col in RESULT_COLS:
        est = point[(row, col)]
        is_level = (row in ("before", "after")) and (col in DIRECT)
        if is_level:
            series = df["fte_before"] if row == "before" else df["fte_after"]
            se = analytic_se(series, group_masks[col])
            t = None
        else:
            se = se_boot[(row, col)]
            t = float(est / se)
        cell_data[(row, col)] = {
            "estimate": est, "se": se, "t": t,
            "n": cell_n(row, col),
            "se_method": "analytic" if is_level else "bootstrap",
        }

# ---- Tidy CSV ----
records = []
for row in ROWS:
    for col in RESULT_COLS:
        d = cell_data[(row, col)]
        records.append({
            "row": ROW_LABEL[row], "column": COL_LABEL[col],
            "estimate": round(d["estimate"], 3), "se": round(d["se"], 3),
            "t": round(d["t"], 3) if d["t"] is not None else None,
            "n": d["n"], "se_method": d["se_method"],
        })
table3 = pd.DataFrame(records)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
table3.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# ---- Report-ready Excel ----
wb = Workbook()
ws = wb.active
ws.title = "Table 3"

def fmt(d):
    lines = [f"{d['estimate']:.3f}", f"({d['se']:.3f})"]
    if d["t"] is not None:
        lines.append(f"t={d['t']:.3f}")
    if d["n"] is not None:
        lines.append(f"n={d['n']}")
    return "\n".join(lines)

# Title
ws.cell(row=1, column=1, value="Table 3 -- Average Employment per Store Before and "
        "After the Rise in New Jersey Minimum Wage (Card & Krueger 1994, replication)") \
    .font = Font(bold=True, size=12)

# Group header (row 2) and column header (row 3)
ws.cell(row=2, column=1, value="Variable").font = Font(bold=True)
ws.merge_cells(start_row=2, start_column=1, end_row=3, end_column=1)
for (label, c1, c2) in [("Stores by state", 2, 4),
                        ("Stores in New Jersey", 5, 7),
                        ("Differences within NJ", 8, 9)]:
    ws.cell(row=2, column=c1, value=label).font = Font(bold=True)
    ws.merge_cells(start_row=2, start_column=c1, end_row=2, end_column=c2)
for j, col in enumerate(RESULT_COLS, start=2):
    ws.cell(row=3, column=j, value=COL_LABEL[col]).font = Font(bold=True)

# Data rows
r = 4
for row in ROWS:
    ws.cell(row=r, column=1, value=ROW_LABEL[row])
    for j, col in enumerate(RESULT_COLS, start=2):
        cell = ws.cell(row=r, column=j, value=fmt(cell_data[(row, col)]))
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

# Notes below the table
r += 1
notes = [
    "Notes: Standard errors are in parentheses; n is the number of non-missing observations.",
    "Level means use analytic standard errors (SD / sqrt(n)). Changes and differences use a "
    "store-level bootstrap (2,000 replications, seed 42): restaurants are resampled with "
    "replacement separately within NJ and PA, and every statistic is recomputed on each resample.",
    "The bootstrap is used because the paper does not state a standard-error formula for row 3, "
    "whose before and after samples are overlapping but not identical.",
    "t-values are estimate / bootstrap standard error.",
    "FTE = full-time employees + managers + 0.5 x part-time employees; six permanently closed "
    "stores have wave-2 FTE = 0; four temporarily closed stores are missing in rows 1-4 and 0 in row 5.",
    "New Jersey wage groups (wave-1 starting wage): $4.25 (N=101), $4.26-$4.99 (N=140), >= $5.00 (N=73).",
]
for note in notes:
    ws.cell(row=r, column=1, value=note)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    r += 1

# Notes worksheet
nws = wb.create_sheet("Notes")
notes_lines = [
    "Table 3 replication -- notes",
    "",
    "1. FTE employment = full-time employees + managers + 0.5 x part-time employees.",
    "   Employment at six permanently closed stores is set to 0 in wave 2; employment at four",
    "   temporarily closed stores is treated as missing (rows 1-4) and set to 0 in row 5.",
    "",
    "2. Standard errors:",
    "   - Level means (rows 1-2, columns PA/NJ/wage groups): analytic, SD / sqrt(n).",
    "   - Changes and all differences: store-level bootstrap. Within each state, restaurants are",
    "     resampled with replacement; every Table 3 statistic is recomputed on each resample;",
    "     the SE is the standard deviation across 2,000 replications (seed 42).",
    "",
    "3. Why bootstrap: the paper does not give a standard-error formula for row 3 (change over",
    "   all available observations), whose before and after samples overlap but are not identical.",
    "   Row 3 is the main result; row 4 (balanced sample) and row 5 (temporarily closed = 0) are",
    "   robustness checks -- neither is privileged as the 'only' difference-in-differences.",
    "",
    "4. New Jersey wage groups (wave-1 starting wage): $4.25 (N=101), $4.26-$4.99 (N=140),",
    "   >= $5.00 (N=73), matching the paper's note (a).",
    "",
    "5. Comparison with the published paper:",
    "   - DiD (row 4, balanced) = 2.75 with t ~ 2.05, vs the paper's 2.76 (t = 2.03).",
    "   - The paper's text quotes the high-wage change as -2.16 and PA change as -2.28; these",
    "     correspond to the balanced-sample changes here (-2.157 and -2.283), not the row-3",
    "     all-available changes (-2.036 and -2.166).",
]
for i, line in enumerate(notes_lines, start=1):
    nws.cell(row=i, column=1, value=line)

wb.save(OUTPUT_XLSX)

# ---- Terminal summary ----
print("=== Step 4: reproduce Table 3 ===")
print(f"Read {len(df)} rows from output/analysis_data.csv.")
print(f"NJ wage-group sizes (wave-1 wage): $4.25={int(low_mask.sum())}, "
      f"$4.26-$4.99={int(mid_mask.sum())}, >=$5.00={int(high_mask.sum())} "
      f"(paper: 101 / 140 / 73).")
print()
print("Key results (estimate, bootstrap SE, t):")
for row in ROWS:
    d = cell_data[(row, "NJ-PA")]
    tstr = f"t={d['t']:.3f}" if d["t"] is not None else ""
    print(f"  {ROW_LABEL[row]:42s} DiD(NJ-PA) = {d['estimate']:+.3f} (SE {d['se']:.3f}) {tstr}")
print()
print("Row 3 change by NJ wage group (all available):")
for col in ["low", "mid", "high"]:
    d = cell_data[("change_all", col)]
    print(f"  {COL_LABEL[col]:20s} change = {d['estimate']:+.3f} (SE {d['se']:.3f}) t={d['t']:.3f}")
print()
print(f"Saved {OUTPUT_CSV}")
print(f"Saved {OUTPUT_XLSX}")
