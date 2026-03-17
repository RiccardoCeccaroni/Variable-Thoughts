# Do Buybacks Explain European Stock Returns Better Than Earnings Growth?

## Overview

This project investigates whether stock buybacks — through their mechanical effect on earnings per share — explain stock price returns better than actual earnings growth in European equity markets. The analysis covers 140 companies across four major European indexes: FTSE MIB (Italy), DAX 40 (Germany), CAC 40 (France), and IBEX 35 (Spain), over the period 2015–2025.

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

Stellantis and STMicroelectronics appear in both the FTSE MIB and CAC 40 — included once under FTSE MIB. Two companies (Siemens Energy, Nexi) were dropped due to insufficient trading history for P/E change calculation.

### Sources

All data — net income, weighted average shares outstanding, market capitalisation, and stock price returns — was collected from company filings via Wisesheets.

### Cleaning

All regression variables were winsorized at the 5th/95th percentiles. Company-years with negative or extreme (>200) P/E ratios were excluded. Final sample: **1,036 company-year observations** (2016–2024).

## Methodology

**1. EPS growth decomposition** — For each company-year, split EPS growth into the portion from net income change (income effect) and the portion from share count reduction (buyback effect). Aggregated by index and by year.

**2. Cross-sectional regressions** — Six OLS models with HC1 robust standard errors, run on the pooled sample and each index separately (30 regressions total):

| Model | Specification                                       |
|-------|-----------------------------------------------------|
| M1    | Return ~ NI Growth                                  |
| M2    | Return ~ EPS Growth                                 |
| M3    | Return ~ NI Growth + Share Count Change             |
| M4    | Return ~ NI Growth + PE Change                      |
| M5    | Return ~ NI Growth + Share Count Change + PE Change |
| M6    | Return ~ EPS Growth + PE Change                     |

## Key Results

**Buybacks barely move European EPS.** The average buyback effect on EPS is −0.2% per year, versus +28% from income growth. Even the top repurchasers (Munich Re, Allianz, Saint-Gobain) only get ~2% annual EPS boost from buybacks.

**P/E change dominates returns.** NI growth alone: R² = 5–10%. Adding PE Change: R² = 30–45%. Annual returns are driven far more by valuation expansion/compression than by earnings growth of any kind.

| Sample   | N     | M1 R² | M5 R² | Δ R²  |
|----------|-------|-------|-------|-------|
| Pooled   | 1,036 | 0.067 | 0.335 | 0.268 |
| FTSE MIB | 273   | 0.058 | 0.441 | 0.383 |
| DAX 40   | 274   | 0.053 | 0.312 | 0.258 |
| CAC 40   | 271   | 0.105 | 0.306 | 0.201 |
| IBEX 35  | 218   | 0.067 | 0.356 | 0.289 |

**Buybacks have a small, country-specific effect.** Share count change is significant pooled (p = 0.009), in Spain (p = 0.02), and marginally in Germany (p = 0.09), but insignificant in Italy and France.

**EPS growth ≈ NI growth.** M1 and M2 produce nearly identical R². The market does not reward buyback-inflated EPS over genuine income growth.

## Limitations

1. **Survivorship bias** — current index constituents traced back to 2015; delisted companies excluded.
2. **Price returns only** — dividends excluded, which understates total returns for high-yield sectors.
3. **Index composition changes** — DAX expanded from 30 to 40 in September 2021; other indexes also changed.
4. **Buyback proxy** — measured via share count change (net of new issuance), not gross buyback expenditure.

## Files

| File | Description |
|------|-------------|
| `buyback_analysis_european_markets.xlsx` | Source data: base variables, derived metrics, EPS decomposition |
| `buyback_regression_analysis.py` | Python script reproducing the full analysis |
| `buyback_article.docx` | Research note (~2.5 pages) |

## Tools

- **Data collection**: Wisesheets (Google Sheets add-in)
- **Analysis**: Python (pandas, statsmodels, numpy, openpyxl)
