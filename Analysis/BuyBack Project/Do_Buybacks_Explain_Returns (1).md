# Do Buybacks Explain European Stock Returns Better Than Earnings Growth?

## Overview

This project investigates whether stock buybacks — through their mechanical effect on earnings per share — explain stock price returns better than actual earnings growth in European equity markets. The analysis covers 140 companies across four major European indexes: FTSE MIB (Italy), DAX 40 (Germany), CAC 40 (France), and IBEX 35 (Spain), over the period 2015–2024.

When a company buys back its own shares, the number of shares outstanding decreases. Even if net income stays flat, EPS goes up — the same profit is divided among fewer shares. Since investors evaluate companies largely on EPS growth, buybacks can make a company look more profitable than it actually became. The question is: does the market reward this financial engineering the same way it rewards genuine profit growth?

## Data

### Universe

| Index     | Country | Companies |
|-----------|---------|-----------|
| FTSE MIB  | Italy   | 36        |
| DAX 40    | Germany | 38        |
| CAC 40    | France  | 35        |
| IBEX 35   | Spain   | 31        |
| **Total** |         | **140**   |

Stellantis and STMicroelectronics appear in both the FTSE MIB and CAC 40 — included once under FTSE MIB to avoid double counting.

### Sources

All data — net income, weighted average shares outstanding, market capitalisation, and stock price returns — was collected from company filings via Wisesheets.

### Cleaning

All regression variables were winsorized at the 5th/95th percentiles. Final sample: **1,036 company-year observations** (2016–2024).

## Methodology

**1. EPS growth decomposition** — For each company-year, split EPS growth into the portion from net income change (income effect) and the portion from share count reduction (buyback effect). Aggregated by index and by year.

**2. Cross-sectional regressions** — Three OLS models with HC1 robust standard errors, run on the pooled sample and each index separately:

| Model | Specification                                       |
|-------|-----------------------------------------------------|
| M1    | Return ~ NI Growth                                  |
| M2    | Return ~ EPS Growth                                 |
| M3    | Return ~ NI Growth + Share Count Change             |

An earlier version of this analysis also included P/E change as a control. Those specifications were dropped: since Return ≈ Earnings Growth + P/E Change by construction, regressing returns on P/E change is a decomposition rather than an explanation, and its high R² would reflect an accounting identity rather than a finding.

## Key Results

**Buybacks barely move European EPS.** The average buyback effect on EPS is −0.2% per year, versus a median income effect of around +11%. Even the top repurchasers (Munich Re, Allianz, Saint-Gobain) only get ~2% annual EPS boost from buybacks.

**Earnings growth alone is a weak predictor of annual returns.** NI growth explains only 5–11% of return variation depending on the market. EPS growth does essentially the same. Adding share count change barely moves the R².

| Sample   | N     | M1 R² | M2 R² | M3 R² |
|----------|-------|-------|-------|-------|
| Pooled   | 1,036 | 0.067 | 0.067 | 0.068 |
| FTSE MIB | 273   | 0.058 | 0.060 | 0.059 |
| DAX 40   | 274   | 0.053 | 0.055 | 0.055 |
| CAC 40   | 271   | 0.105 | 0.101 | 0.109 |
| IBEX 35  | 218   | 0.067 | 0.064 | 0.071 |

**Buybacks add a small signal in the pooled sample.** In M3, the share count change coefficient is negative and significant pooled (coefficient = −0.84, p = 0.010). The negative sign is correct: a decrease in shares corresponds to higher returns.

**Country-level results are not robust.** Coefficient signs and significance shift depending on which sample filters are used. With only 220–330 observations per country and small buyback effects to begin with, individual country coefficients are not stable enough to support country-by-country conclusions. Only the pooled result is reported.

**EPS growth ≈ NI growth.** M1 and M2 produce nearly identical R². The market does not reward buyback-inflated EPS over genuine income growth — mostly because European buybacks are too small to create a meaningful wedge between the two in the first place.

## Limitations

1. **Survivorship bias** — current index constituents traced back to 2015; delisted companies excluded.
2. **Price returns only** — dividends excluded, which understates total returns for high-yield sectors.
3. **Buyback proxy** — share count change captures net buybacks (repurchases minus new issuance), not gross buyback expenditure. To limit the risk that share count movements reflect non-buyback events such as equity issuance for M&A, capital raises, or stock splits, weighted average shares outstanding (rather than end-of-period share counts) were used, and all variables were winsorized at the 5th/95th percentiles.
4. **Dropped P/E specifications** — a previous version of this analysis included P/E change as a regressor; those specifications were dropped because the resulting models amount to a decomposition of returns rather than a test of what drives them.

## Files

| File | Description |
|------|-------------|
| `buyback_analysis_european_markets.xlsx` | Source data: base variables, derived metrics, EPS decomposition |
| `buyback_regression_analysis.py` | Python script reproducing the full analysis |
| `buyback_article.docx` | Research note |

## Tools

- **Data collection**: Wisesheets (Google Sheets add-in)
- **Analysis**: Python (pandas, statsmodels, numpy, openpyxl)