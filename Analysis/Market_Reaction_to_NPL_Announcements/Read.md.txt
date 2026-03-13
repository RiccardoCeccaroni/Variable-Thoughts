# Cleaning Up the Books: Market Reactions to NPL Disposals by Italian Listed Banks (2015–2022)

## Research Question

Did the stock market reward or punish Italian banks for disposing of non-performing loans (NPLs)? The study tests whether cumulative abnormal returns (CARs) around NPL disposal announcements differ by deal type (GACS-backed securitisation vs. direct sale), deal size, crisis period, and bank identity.

## Sample

Six Italian listed banks on Borsa Italiana: **UniCredit (UCG)**, **Intesa Sanpaolo (ISP)**, **Banco BPM (BAMI)**, **Monte dei Paschi di Siena (BMPS)**, **BPER (BPE)**, and **Banca Popolare di Sondrio (BPSO)**.

**74 clean events** remain after removing 10 problematic observations (weekend/holiday dates, year-end edge cases) and 3 MPS outliers with identical anomalous CAR values.

## Methodology

Standard **event study** using a market model estimated over a 120-day window (days −130 to −11). Abnormal returns are computed as:

```
AR_t = R_t − (α + β × R_market,t)
```

CARs are cumulated over three windows: **[−1, +1]**, **[−1, +3]**, and **[−5, +5]**.

Cross-sectional OLS regression on CARs:

```
CAR_i = β₀ + β₁(GACS_dummy) + β₂(ln_GBV) + β₃(Crisis_Period_dummy) + εᵢ
```

Statistical tests: t-test, sign test, Wilcoxon signed-rank test.

## Key Findings

| Result | Value |
|--------|-------|
| Overall mean CAR[−1,+1] | +0.82% (p = 0.15, not significant) |
| GACS deals | +2.6% (p = 0.09) |
| Non-GACS deals | +0.29% (not significant) |
| OLS R² (primary window) | 5.5% |
| ln(GBV) significance | At 5% in the wider CAR[−5,+5] window |

Bank-level heterogeneity is sharp: BMPS and BPE show positive and significant reactions; ISP is negative and significant.

## Data Sources

| Source | Used For |
|--------|----------|
| PwC "Italian NPL Market" reports (2015–2024) | Event database construction (deal details, GBV, GACS status) |
| Bank investor relations press releases | Announcement dates |
| BeBeez.eu | Deal-level granularity |
| Yahoo Finance / Wisesheets | Daily stock prices (`.MI` suffix for Borsa Italiana tickers) |
| FTSE MIB (FTSEMIB.MI) | Market benchmark |

## Project Files

| File | Description |
|------|-------------|
| `NPL_Event_Database_Master_2.xlsx` | Master event database (74 events after cleaning) |
| `Event_Study_Results.xlsx` | Full statistical output: OLS, descriptive stats, sign test, Wilcoxon |
| Research paper (`.docx`) | 3–4 page write-up with five sections |

## Report Structure

1. **Introduction** — Italian NPL crisis context, GACS scheme, research gap
2. **Data & Sample Construction** — Banks, events, cleaning steps
3. **Methodology** — Market model, event windows, regression specification
4. **Results** — Three tables: descriptive stats by subgroup, CARs by bank/deal type, OLS regression
5. **Discussion & Conclusion** — Interpretation, comparison with prior literature, limitations

## Tools

| Tool | Purpose |
|------|---------|
| Python / pandas | Event study computation, statistical tests |
| Excel | Database management, results workbook |
| Word | Final research paper |
| PwC reports (PDFs) | Primary source for deal identification |

## Known Limitations

- Small sample (74 events) limits statistical power
- Absolute deal size (ln GBV) used instead of relative deal size (GBV / bank's total NPL stock) due to data constraints
- Bank-level fundamentals (NPL ratio, CET1) dropped from regression — S&P Capital IQ access was unavailable
- Low OLS R² suggests unobserved deal-specific factors drive much of the variation
- Information leakage before official announcements may dilute measured reactions

## Event Date Convention

The earliest public disclosure date (binding agreement announcement) is used as the event date — not closing or settlement dates. Markets react to news, not paperwork.