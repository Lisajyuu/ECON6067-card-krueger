---
name: reproduce-card-krueger-results
description: Reproduce the main tables, figures, processed data, and extension results for the Card and Krueger minimum-wage replication project. Use when the required public.csv input data have been placed in the documented input folder.
---

# Reproduce Card and Krueger results

1. **Required input.** The raw data must be present at `data/raw/public.csv` (the
   Card and Krueger store-level survey, 410 fast-food restaurants). Do not start
   until this file is in place.
2. **Run the workflow.** From the project root, run:

   ```bash
   python code/run_all.py
   ```

3. **What it does.** The workflow runs `code/01_inspect_data.py` through
   `code/07_extension_price_did.py` in order, and stops immediately if any step
   fails.
4. **Main outputs.** On success it generates:
   - `data/processed/analysis_data.csv` (processed data)
   - Table 2: `outputs/tables/table2_replication.xlsx`
   - Table 3: `outputs/tables/table3_replication.xlsx`
   - Table 4: `outputs/tables/table4_replication.xlsx`
   - Figure 1: `outputs/figures/figure1_replication.png`
   - extension price-DiD table: `outputs/tables/extension_price_did.xlsx`
   - extension price-DiD figure: `outputs/figures/extension_price_did.png`
5. **Do not hand-edit.** While reproducing the results, do not manually edit the
   raw data, the analysis scripts, or the generated outputs.
6. **Validation checks.** After a successful run, confirm that:
   - the Table 3 balanced-sample DiD is approximately **+2.75 FTE** (row 4);
   - the extension price DiD is approximately **+$0.10**.
