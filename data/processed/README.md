# Processed data

`analysis_data.csv` is the processed dataset used for the final analysis.

It is generated automatically by `code/02_prepare_analysis.py` from
`data/raw/public.csv`. The preparation step constructs the full-time-equivalent
(FTE) employment variables and applies the documented closure and missing-value
rules. The later replication scripts read this processed dataset where required.

Do not hand-edit `analysis_data.csv`; regenerate it by running
`python code/run_all.py` from the project root.
