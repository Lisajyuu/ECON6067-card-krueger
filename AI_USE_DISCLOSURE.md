# AI Use Disclosure

This document describes how AI assistance was used in this project, how the
AI-generated material was checked, and which AI errors or suggestions were
corrected or rejected.

## Where and how AI was used

- **Code.** AI assistance drafted the Python scripts that implement the
  replication and the extension (`code/01_inspect_data.py` through
  `code/07_extension_price_did.py`), the reproducibility driver
  (`code/run_all.py`), and the HTML-report generator. The scripts read the raw
  data, compute the statistics and regressions, and write the tables and
  figures.
- **Analysis design.** AI assistance helped identify the relevant variables from
  `docs/DATA_DICTIONARY.md` and the published paper, and helped determine the
  sample rules and model specifications (e.g., the full-time-equivalent
  definition, the wage-gap variable, and the difference-in-differences setup).
- **Writing.** AI assistance drafted the report text (`report/report.md`), the
  HTML version (`report/report.html`), this `README.md`, and this disclosure.

## How AI-generated code, analysis, and writing were checked

- Each script was run, and key numerical entries were compared against the
  published paper's Tables 2–4 and Figure 1 where possible. Any remaining small
  differences are documented in the report and README.
- The full pipeline was run end-to-end with `python code/run_all.py` and
  confirmed to regenerate all tables, figures, and the processed data from
  `data/raw/public.csv`.
- Variable definitions and units were checked against `docs/DATA_DICTIONARY.md`
  rather than assumed.
- The final text and results were reviewed by the author against the original
  paper and the data dictionary, and revised where they did not match.

## Important AI errors or suggestions that were corrected or rejected

1. **Denominator of the wage-proportion variables.** An initial version computed
   the "Wage = $4.25" and "Wage = $5.05" percentages over non-missing wage
   observations. This was corrected to the paper's convention &mdash; the
   denominator is **all stores in each state** (New Jersey = 331, Pennsylvania =
   79), with missing-wage stores excluded from the bin but kept in the
   denominator. This change is reflected in Table 2 and Figure 1.

2. **Figure 1 wage-bin assignment.** The figure uses $0.10-wide wage bins centred
   on $4.25, $4.35, ..., $5.55, with rounding to the nearest bin and top-coding
   above $5.60. The resulting treatment of a store reporting $5.00 (placed into
   the $5.05-centred bin) is disclosed in the figure Notes and in the report,
   rather than hidden.

3. **Standard errors in Table 3.** The changes and differences are not given a
   naive analytic standard error that treats the before and after samples as
   independent. Instead, store-level bootstrap standard errors are used (2,000
   replications, resampling within state), because the paper does not state a
   standard-error formula for the all-available change in row 3. This more
   careful choice is documented in the script and the table Notes.

4. **Table 4 sample rule.** A mechanical "starting wage non-missing in both
   waves" rule would have produced a sample of 351, not the paper's 357. The
   correct rule keeps the **six permanently closed stores** in the sample (their
   wave-2 FTE is set to 0) even though they lack a wave-2 starting wage. This
   non-obvious exception was identified by checking the sample against the
   paper's reported n = 357 and the dependent-variable mean and standard
   deviation, and it is implemented in `code/05_reproduce_table4.py`.

5. **Author review and responsibility.** The author reviewed the AI-generated
   code, the intermediate and final outputs, and the report against the original
   paper and `docs/DATA_DICTIONARY.md`, requested the corrections above, and
   takes responsibility for the final content.
