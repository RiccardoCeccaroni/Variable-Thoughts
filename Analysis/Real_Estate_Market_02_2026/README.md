# Italian Real Estate Market — Rent vs Buy Analysis

An empirical analysis of rental and purchase prices across 104 Italian provinces, based on ~190K sale and ~67K rental listings scraped from immobiliare.it (February 2026).

## What This Project Does

This project investigates two questions:

1. **What drives property prices in Italy?** Using multiple linear regression on both rental and sale data, we identify the key determinants of price — including property size, location, distance from city center, and macro-region.
2. **Is it better to rent or to buy?** Using the *unrecoverable cost method*, we convert each sale listing into an equivalent monthly cost and compare it against local rents across eight financing scenarios.

## Key Findings

**Buying is generally cheaper than renting in Italy** — but with important exceptions:

- The advantage is strongest for **larger properties** and in the **Centre and South**, where purchase prices are low relative to rents.
- For **small flats**, especially in the North and coastal/tourist areas, the result approaches a coin flip under conservative assumptions.
- **Liguria** is the region most hostile to buyers; **Calabria, Sicilia, and Umbria** are among the most favorable.
- Even under the most pessimistic scenario (5.0% rate, 30% equity), buying still wins for ~60% of listings nationally.

On price determinants, the North-South divide dominates the rental market far more than the sale market, where property characteristics like bathrooms and size matter most.

## Method: Unrecoverable Costs

Rather than comparing rent to the full mortgage payment, we compare rent to the portion of ownership costs that builds no equity:

- Cost of capital (debt interest + equity opportunity cost)
- Property taxes, maintenance, condo fees, insurance
- Transaction costs (notary, agent fees), annualized over a 10-year holding period

Eight scenarios are tested: four mortgage rates (3.5%-5.0%) combined with two equity/debt splits (20/80 and 30/70).

## Data

- **Source:** immobiliare.it, supplemented with idealista.it for internet rent benchmarks
- **Coverage:** 104 Italian provinces, ~190K sale + ~67K rental listings
- **Variables:** price, square meters, rooms, bathrooms, floor, lift, distance from city center

**Limitations:** data comes from a single platform and is subject to its ranking bias (first 2,000 results per province for sales). Tourist areas may be overrepresented. Listings may contain inaccuracies.

## Dashboard

The interactive Streamlit dashboard lets you explore the results by scenario, region, and property size.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Author

Riccardo Ceccaroni
