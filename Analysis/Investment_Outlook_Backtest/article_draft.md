# How Accurate Are Wall Street's Year-Ahead Predictions?

Every December and January, the world's largest investment firms publish their annual outlooks. These are ofen long documents where teams of economists and strategists lay out what they think will happen over the next twelve months. Things like where GDP growth will land, how high inflation will go, what the different central banks will do, and where markets will finish the year.

Many investors read these reports, with many news organzation citing them as the source of truth. But it is very often the case that, after the year finished, none goes back and check whether the predictions were actually correct. To the extent that years later, it is very challenging to still find those reports online. 

This article backtests the predictions of some of those investment outlooks. 

## What I did

I collected the year-ahead investment outlook reports from ten major firms, covering the period from 2018 through 2024. From each report, I extracted every concrete, testable prediction I could find — things like "US GDP will grow 2.3%," or "the Fed will cut rates by mid-2024," or "the S&P 500 will reach 4,800." I skipped anything too vague to score ("markets will be volatile") and focused on claims where the firm put a number, a range, or any prediction on something.

In total, I pulled 478 predictions across all ten firms. Not all of them could be scored numerically. Many predictions were directional or qualitative rather than a specific number — things like "recession is our base case" or "the dollar will weaken broadly" or "rates will stay higher for longer than markets expect." These are real predictions, but there is no clean way to calculate a percentage error between "recession" and 2.5% GDP growth. Of the 478, 367 could be directly scored against official data from the BEA, BLS, Eurostat, the ONS, central banks, and Bloomberg. The remaining 111 were either qualitative calls, long-term predictions whose horizon hasn't passed yet, or cases where no directly comparable actual data point exists.

I then measured how far each prediction landed from reality, using percentage error against the actual outcome. A forecast of 3% GDP growth when the actual was 2.5% gives an error of 20%. A forecast of 5,000 for the S&P 500 when it ended at 4,770 gives an error of about 5%.

## The firms and what I covered

| Firm | Reports | Years covered | Predictions |
|------|---------|---------------|-------------|
| Amundi | 4 | 2021-2024 | 118 |
| Vanguard | 6 | 2018, 2020-2024 | 75 |
| PIMCO | 6 | 2019-2024 | 70 |
| UBS Global Wealth Management | 5 | 2019-2023 | 46 |
| JP Morgan Asset Management | 7 | 2018-2024 | 42 |
| Schroders | 6 | 2018-2020, 2022-2024 | 33 |
| Morgan Stanley Investment Management | 6 | 2018-2019, 2021-2024 | 32 |
| BlackRock | 7 | 2018-2024 | 23 |
| Fidelity International | 6 | 2018-2019, 2021-2024 | 20 |
| Morningstar | 2 | 2023-2024 | 19 |

Amundi published the most detailed forecasts, with tables of GDP, inflation, interest rate, and currency projections across dozens of countries. Others like BlackRock and Morningstar focused more on broad themes and made fewer specific numerical calls.

## What they predicted

The 478 predictions covered nine categories:

- **Economic growth** (175 predictions) — GDP growth forecasts for the US, Eurozone, China, Japan, UK, and other economies
- **Inflation** (89) — headline CPI, core CPI, and PCE forecasts
- **Central bank policy** (84) — where the Fed, ECB, BoE, and BoJ would set interest rates
- **Stock markets** (45) — S&P 500 targets, European and emerging market equity calls
- **Bond yields** (33) — US Treasury yields, German Bunds, Japanese government bonds
- **Labour markets** (18) — unemployment rate forecasts
- **Commodities** (17) — oil and gold price targets
- **Currencies** (14) — EUR/USD, USD/JPY, and other exchange rate calls
- **Credit spreads** (3) — investment-grade and high-yield spread forecasts

Most predictions were about the US (133), followed by global aggregates (44), the UK (40), China (29), the Eurozone (25), and Japan (23).

## The findings

All the results below are based on the 367 predictions that could be scored numerically.

### Overall: not great

Across all 367 scored predictions, the median error was 27.8%. That means the typical forecast missed reality by more than a quarter. Nearly one in five predictions (66 out of 367) was off by more than 100% — meaning the forecast was at least double or less than half of what actually happened.

On the brighter side, 44% of predictions landed within 20% of the actual value, and 23% were within 10%. Seventeen predictions were essentially spot-on.

### The rankings

| Rank | Firm | Scored | Median error | Within 20% | Within 10% | Exact | Bias |
|------|------|--------|-------------|------------|------------|-------|------|
| 1 | Vanguard | 65 | 17.1% | 39 (60%) | 15 (23%) | 1 | Balanced |
| 2 | Morgan Stanley IM | 16 | 21.1% | 8 (50%) | 5 (31%) | 1 | Slightly bearish |
| 3 | Amundi | 109 | 22.0% | 51 (47%) | 24 (22%) | 6 | Bearish |
| 4 | Schroders | 30 | 23.9% | 15 (50%) | 9 (30%) | 2 | Balanced |
| 5 | Morningstar | 11 | 31.0% | 4 (36%) | 3 (27%) | 0 | Bearish |
| 6 | PIMCO | 66 | 33.1% | 24 (36%) | 16 (24%) | 4 | Slightly bullish |
| 7 | Fidelity International | 11 | 38.4% | 2 (18%) | 0 (0%) | 0 | Bearish |
| 8 | BlackRock | 5 | 42.9% | 2 (40%) | 2 (40%) | 0 | — |
| 9 | JP Morgan AM | 15 | 45.0% | 5 (33%) | 4 (27%) | 1 | Balanced |
| 10 | UBS GWM | 39 | 52.6% | 12 (31%) | 6 (15%) | 2 | Very bullish |

**Vanguard came out on top**, with a median error of 17.1% and 60% of their calls landing within 20% of the actual value. They were also the most balanced in terms of bias, roughly equally likely to overshoot or undershoot.

**Amundi scored well and also produced the most predictions by far** (109 scored), which makes their 22% median error more impressive: it's easy to look accurate with few predictions than many.

**UBS finished last**, with a median error above 50% and a strong bullish bias — 81% of their misses were overshoots, meaning they consistently expected more growth, higher returns, or tighter spreads than what materialised.

A caveat on sample sizes: BlackRock and Morningstar had very few scoreable predictions (5 and 11), so their rankings should be taken lightly. Their outlooks tended to be more thematic and qualitative rather than numerical.

### Some predictions were easier than others

The category of the prediction mattered:

| Category | Median error | N |
|----------|-------------|---|
| Credit spreads | 2.1% | 3 |
| Currencies | 7.9% | 11 |
| Central bank policy | 15.9% | 41 |
| Labour markets | 17.3% | 16 |
| Equities | 18.2% | 25 |
| Commodities | 19.9% | 14 |
| Bond yields | 20.4% | 24 |
| Inflation | 35.0% | 78 |
| GDP growth | 47.1% | 155 |

Policy rate forecasts were relatively accurate: central banks telegraph their moves, so getting the year-end Fed funds rate roughly right isn't that hard. Exchange rates were also very close, though with only 11 scored predictions (mostly from Amundi), that's a thin sample.

GDP growth was the hardest to get right, with a median error of 47%. Inflation came second.

### Some years were harder than others

| Year | Median error | N |
|------|-------------|---|
| 2018 | 12.4% | 24 |
| 2019 | 15.5% | 38 |
| 2024 | 15.4% | 64 |
| 2021 | 23.1% | 64 |
| 2023 | 31.7% | 69 |
| 2022 | 48.1% | 56 |
| 2020 | 114.3% | 49 |

No surprise here: 2020 was a disaster for forecasters. Nobody in December 2019 saw a pandemic shutting down the global economy. JP Morgan's 2020 outlook predicted US GDP growth of "roughly 2%" — the actual was -2.8%. The median prediction that year missed by 114%.

2022 was also hard to predict. The combination of the war in Ukraine, the inflation spike, and the Fed's aggressive rate hikes blindsided most firms. Predictions made in late 2021 had no way of pricing in a 75bps-per-meeting hiking cycle or 9% inflation in Europe.

The best years for forecasters were the calm ones — 2018 and 2019 — and 2024, when the post-pandemic economy finally started behaving more predictably.

### The recession that never came

One of the most interesting patterns was how many firms predicted a US recession in 2023 that didn't happen.

- **Fidelity International** made a US recession their base case for both 2023 (55% probability) and 2024 (60% probability). US GDP grew 2.5% and 2.8%.
- **BlackRock** forecast "approximately -2%" US GDP growth from Q3 2022 to Q3 2023. Growth was positive throughout.
- **Morningstar** assigned a 30-50% recession probability for 2023.

The consensus going into 2023 was that a recession was more likely than not. It turned out to be one of the most widely shared — and most wrong — macro calls.


## Takeaways

If you read these outlooks to get a general sense of what the big themes might be (which direction rates are heading, whether growth is accelerating or slowing) they have some value. Policy rate predictions had a median error under 16%, and the directional calls were often right even when the magnitudes were off.

But if you're using specific numbers from these reports to make portfolio decisions, like expecting GDP to land at 2.3% or the S&P to finish at 5,200, the track record suggests you shouldn't lean too much on any single forecast. The typical prediction misses by a quarter, and in unusual years, by much more.


I believe these outlooks are worth reading for the reasoning, not for the numbers. The analysis behind the forecast, meaning how a firm arrived at a certain conclusion, is usually more valuable than the specific targets they write. Especially because an investor can more easily agree or disagree on the reasoning as opposed to raw numbers.

---

*Methodology: I collected 55 year-ahead outlook reports published by ten investment firms between late 2017 and early 2024, covering forecast years 2018 through 2024. From each report, I identified every prediction that was specific enough to test: a named variable, a region, a time horizon, and a number or range. Vague or qualitative statements ("we expect volatility to remain elevated") were excluded.*

*In total I extracted 478 predictions. Each was matched against actual outcomes from official sources: GDP figures from the BEA, Eurostat, ONS, and national statistics offices; inflation data from the BLS, Eurostat, and the ONS; policy rates from the Federal Reserve, ECB, BoE, and BoJ; market data (equities, bonds, FX, commodities, credit spreads) from Bloomberg and FRED. Actuals reflect the latest available revisions as of April 2026, including the ONS Blue Book 2024 revision for UK GDP.*

*Error was calculated as the absolute percentage difference between the forecast value and the actual outcome. When a firm gave a range (e.g. "4.7% to 5.3%"), I scored the midpoint of that range (5.0% in that example). Of the 478 predictions, 367 could be scored numerically — meaning both the forecast and the actual were concrete numbers I could compare. The remaining 111 were qualitative or directional calls (e.g. "recession is our base case," "the dollar will weaken"), long-term predictions whose horizon hasn't passed yet, or cases where no directly comparable actual data point exists. All rankings and statistics in the article are based on the 367 numerically scored predictions.*

*This entire project, from extracting predictions out of PDF reports, to matching them against actuals, to scoring and ranking, was carried out with the help of AI tools. While I tried to verify the data, the process may contain errors. If you spot anything that looks off, please reach out.*

*All the data, the scoring script, and the raw text from the reports are available on [GitHub](https://github.com/RiccardoCeccaroni/Variable-Thoughts/tree/main/Analysis/Investment_Outlook_Backtest).*
