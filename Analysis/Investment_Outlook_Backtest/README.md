# Investment Outlook Backtest

How accurate are the year-ahead predictions from the world's largest investment firms? This project extracts and scores 478 predictions from 55 annual outlook reports published by ten firms between 2018 and 2024.

Full write-up: [article_draft.md](article_draft.md)

## Results at a glance

- **478** predictions extracted, **367** scored numerically
- Median error across all scored predictions: **27.8%**
- Best firm: **Vanguard** (17.1% median error)
- Hardest year to predict: **2020** (114% median error)
- Easiest category: **central bank policy** (15.9% median error)
- Hardest category: **GDP growth** (47.1% median error)

## Firms covered

| Firm | Reports | Years |
|------|---------|-------|
| Amundi | 4 | 2021-2024 |
| BlackRock | 7 | 2018-2024 |
| Fidelity International | 6 | 2018-2019, 2021-2024 |
| JP Morgan Asset Management | 7 | 2018-2024 |
| Morgan Stanley Investment Management | 6 | 2018-2019, 2021-2024 |
| Morningstar | 2 | 2023-2024 |
| PIMCO | 6 | 2019-2024 |
| Schroders | 6 | 2018-2020, 2022-2024 |
| UBS Global Wealth Management | 5 | 2019-2023 |
| Vanguard | 6 | 2018, 2020-2024 |

## Project structure

```
Investment_Outlook_Backtest/
├── article_draft.md                     # The write-up
├── README.md
├── extracted/
│   ├── raw_text/                        # Text extracted from the original PDF reports (57 files)
│   └── raw_json/                        # Structured predictions extracted from the text (57 files, 478 predictions)
├── data/
│   ├── benchmarks/
│   │   └── actuals_reference.json       # Actual outcomes used for scoring (GDP, CPI, rates, markets, etc.)
│   └── results/
│       ├── scored_predictions.json      # Every prediction matched and scored against actuals
│       └── accuracy_rankings.json       # Summary rankings by firm, category, and year
└── scripts/
    └── score_predictions.py             # Scoring script (pure Python, no external dependencies)
```

## How to replicate

1. Clone this repo
2. Run the scoring script:

```bash
cd Investment_Outlook_Backtest
python scripts/score_predictions.py
```

This reads the predictions from `extracted/raw_json/` and the actuals from `data/benchmarks/actuals_reference.json`, then outputs `data/results/scored_predictions.json`.

No external dependencies required (uses only Python standard library: json, os, re, math).

## Data sources for actuals

- **GDP**: BEA (US), Eurostat (Eurozone), ONS (UK), Cabinet Office (Japan), NBS (China), IMF WEO (global aggregates)
- **Inflation**: BLS CPI-U (US), Eurostat HICP (Eurozone), ONS CPI (UK)
- **Policy rates**: Federal Reserve, ECB, Bank of England, Bank of Japan
- **Markets**: Bloomberg, FRED (equities, bonds, FX, commodities, credit spreads)

Actuals reflect the latest available revisions as of April 2026, including the ONS Blue Book 2024 revision for UK GDP.

## Notes

- The original PDF reports are not included (copyrighted material). The raw text extractions are provided so that prediction extractions can be verified against the source.
- This project was carried out with the help of AI tools. While every effort was made to verify the data, it may contain errors.
- Published on [variablethoughts.com](https://variablethoughts.com)
