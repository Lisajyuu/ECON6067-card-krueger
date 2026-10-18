# Replication and Extension of Card and Krueger (1994): Minimum Wages and Fast-Food Employment

## 1. Introduction

In "Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania," Card and Krueger (1994) exploit a natural experiment created by New Jersey's increase in its state minimum wage from $4.25 to $5.05 per hour on April 1, 1992. Because neighboring Pennsylvania did not raise its minimum wage, fast-food restaurants in eastern Pennsylvania serve as a comparison group. Contrary to the standard competitive-model prediction that a binding minimum wage reduces employment, the paper found no evidence of job loss; if anything, employment in New Jersey rose relative to Pennsylvania.

This report reproduces the paper's main descriptive and regression results (Tables 2–4 and Figure 1) using the publicly distributed store-level data, and then presents a short extension that asks whether New Jersey restaurants passed the higher labor cost through to menu prices. All figures reported here are computed from the project's scripts and output files, and no results have been re-estimated for this report.

## 2. Data and Research Design

The data come from the publicly distributed Card and Krueger store-level dataset (`data/raw/public.csv`), with variable definitions in the project data dictionary (`docs/DATA_DICTIONARY.md`). They are two waves of a survey of 410 fast-food restaurants — 331 in New Jersey and 79 in eastern Pennsylvania — drawn from four chains (Burger King, KFC, Roy Rogers, and Wendy's). Wave 1 was collected in February and March 1992, before the minimum-wage increase, and Wave 2 in November and December 1992, after it. The store-level survey records employment, starting wages, prices, hours, and other characteristics in both waves.

The main outcome is full-time-equivalent (FTE) employment, defined as full-time employees plus managers plus one-half of part-time employees. Employment at the six permanently closed stores is set to zero in Wave 2, while employment at the four temporarily closed stores is treated as missing.

The identifying design is difference-in-differences (DiD). The simplest estimate compares the change in mean FTE employment between the two waves in New Jersey with the corresponding change in Pennsylvania. The key assumption is that, absent the minimum-wage increase, employment in the two states would have followed parallel trends. Regression-adjusted versions of this comparison add controls for chain, company ownership, and region.

Several subsamples are defined by data availability: the balanced employment sample underlying Table 3 has 384 stores, the employment-and-wage regression sample in Table 4 has 357 stores, and the balanced full-meal-price sample in the extension has 356 stores.

## 3. Replication Results

### 3.1 Table 2: Sample means

Table 2 (`outputs/tables/table2_replication.xlsx`) reports means of key variables by state and wave. In Wave 1, average FTE employment was 20.4 in New Jersey and 23.3 in Pennsylvania, and starting wages were similar across the two states (about $4.61 in New Jersey). By Wave 2, New Jersey's average starting wage had risen to $5.08, while Pennsylvania's remained near $4.62. Average FTE employment in Wave 2 was 21.0 in New Jersey and 21.2 in Pennsylvania. One minor discrepancy is worth noting: the replication finds that 85.5 percent of New Jersey stores in Wave 2 report a starting wage of exactly $5.05, whereas the published paper reports 85.2 percent.

### 3.2 Figure 1: The distribution of starting wages

Figure 1 (`outputs/figures/figure1_replication.png`) shows the distribution of starting wages by state and wave. In February 1992 both states are concentrated at the old minimum wage of $4.25 (about 30.5 percent of New Jersey stores and 25.3 percent of Pennsylvania stores). In November 1992 the New Jersey distribution shifts sharply to the new minimum of $5.05, while the Pennsylvania distribution is essentially unchanged. In this replication, 85.8 percent of New Jersey stores appear in the $5.05-centered wage bin in Wave 2, slightly above the paper's 85.2 percent. The gap has two sources: the public dataset contains one additional New Jersey store at exactly $5.05 relative to the data used in the published figure, and the figure's $0.10-wide wage bins place one store reporting $5.00 into the $5.05-centered bin.

### 3.3 Table 3: Average employment before and after

Table 3 (`outputs/tables/table3_replication.xlsx`) reports average FTE employment by state and wave, together with the difference-in-differences estimates. Using all available observations, mean FTE employment in New Jersey rose from 20.44 to 21.03 while Pennsylvania's fell from 23.33 to 21.17. The resulting DiD estimate is about +2.75 FTE workers per store (row 3: +2.754, standard error 1.303, t = 2.11). The balanced-sample estimate (row 4) is +2.750 (standard error 1.333, t = 2.06), essentially matching the paper's reported 2.76 (t = 2.03). Decomposing the change by initial wage, the employment gains are concentrated among low-wage New Jersey stores, while high-wage stores and Pennsylvania stores contracted.

### 3.4 Table 4: Regression-adjusted models

Table 4 (`outputs/tables/table4_replication.xlsx`) reports reduced-form regressions of the change in FTE employment on the New Jersey dummy or on an initial-wage "gap" measure. The sample is the 357 stores with employment and starting wages in both waves. The New Jersey dummy coefficient is 2.33 (standard error 1.19) without controls and 2.30 (1.20) with chain and ownership controls, both matching the paper. The wage-gap coefficient is 15.65 (6.08) without controls and 14.92 (6.21) with chain and ownership controls, again matching the paper. Adding region controls attenuates the wage-gap coefficient to 11.98 (7.42), slightly higher than the paper's 11.91 (7.39); this small difference is confined to the region-augmented specification and most likely reflects minor differences in region coding between the public data and the version used in the published table.

## 4. Extension: Full-Meal Prices

The extension asks a related question: did New Jersey restaurants raise full-meal prices relative to Pennsylvania after the minimum-wage increase? The full-meal price is the sum of the medium soda, small fries, and entrée prices (each including tax), defined identically to the "price of full meal" in Table 2. The sample is restricted to the 356 stores with non-missing full-meal prices in both waves (288 in New Jersey, 68 in Pennsylvania); no price is imputed for closed or missing stores.

Average full-meal prices in New Jersey rose from $3.359 before the increase to $3.425 after, a change of +$0.066, while Pennsylvania prices fell from $3.088 to $3.054, a change of −$0.034. The difference-in-differences estimate is therefore +$0.100 (see `outputs/tables/extension_price_did.csv`). A simple OLS regression of the store-level price change on a New Jersey dummy returns exactly this DiD as its coefficient: 0.100 with a standard error of 0.049 (t = 2.03, p = 0.043). Adding chain dummies and a company-owned dummy yields a slightly larger and still significant coefficient of 0.111 (standard error 0.049, t = 2.28, p = 0.023). These results are consistent with partial pass-through of the higher minimum wage into menu prices, but they do not by themselves establish the mechanism or a causal effect of the minimum wage on prices.

## 5. Validation

The project's scripts (`code/01_inspect_data.py` through `code/07_extension_price_did.py`) are run in sequence and regenerate, from the raw `data/raw/public.csv`, the analysis data, the replication tables and figures, and the extension outputs. The key checks are the Table 3 difference-in-differences estimate (+2.754 for the change in mean FTE employment), the Table 4 coefficients in models (i)–(iv) (which agree with the paper to two decimal places), and the Pennsylvania wave-2 $4.25 share in Figure 1 (25.3 percent, matching the paper). Two small differences are recorded and explained above: the New Jersey $5.05 share in Table 2 and Figure 1 (85.5 and 85.8 percent here versus 85.2 percent in the paper), and the Table 4 model (v) wage-gap coefficient (11.98 versus 11.91). These are attributed to minor differences between the public dataset and the version used in the published paper rather than to a specification error. The replication therefore reproduces the paper's central findings, though not every cell is identical.

## 6. Limitations

Several limitations qualify these findings. First, the analysis relies on only two survey waves, so it cannot distinguish the minimum-wage effect from state-specific shocks that happened to coincide with the April 1992 increase. Second, the price variables measure only three menu items and are subject to the same survey error as the employment data. Third, the small Pennsylvania price sample (68 stores) limits the precision of the extension. Fourth, region-level demand shocks could confound both the employment and price comparisons. Finally, the public dataset differs in small ways from the exact data used in the published paper, most visibly in the Wave 2 New Jersey wage distribution and the region-augmented model in Table 4; these differences do not change the substantive conclusions but are reported here for transparency.

## 7. Conclusion

The replication reproduces the central finding of Card and Krueger (1994): the rise in New Jersey's minimum wage was not associated with a fall in fast-food employment. On the contrary, employment in New Jersey rose by roughly 2.75 FTE workers per store relative to Pennsylvania, a result that is stable across the descriptive and regression-adjusted specifications. The extension offers complementary evidence that New Jersey restaurants raised full-meal prices by about $0.10 relative to Pennsylvania, consistent with partial pass-through of the higher labor cost. Taken together, the project illustrates both the mechanics of a difference-in-differences design and the importance of transparent reporting when replicated results differ slightly from the published originals.

## 8. References

- Card, David, and Alan B. Krueger. 1994. "Minimum Wages and Employment: A Case Study of the Fast-Food Industry in New Jersey and Pennsylvania." *American Economic Review* 84 (4): 772–793. (`docs/njmin-aer.pdf`)
- Card and Krueger public dataset and project data dictionary. (`data/raw/public.csv`, `docs/DATA_DICTIONARY.md`)

---

### Figures and tables

- [Insert Table 2 here] — `outputs/tables/table2_replication.xlsx`
- [Insert Figure 1 here] — `outputs/figures/figure1_replication.png`
- [Insert Table 3 here] — `outputs/tables/table3_replication.xlsx`
- [Insert Table 4 here] — `outputs/tables/table4_replication.xlsx`
- [Insert Extension table here] — `outputs/tables/extension_price_did.xlsx`
- [Insert Extension figure here] — `outputs/figures/extension_price_did.png`
