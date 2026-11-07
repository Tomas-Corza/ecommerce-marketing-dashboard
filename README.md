# E-commerce Marketing Dashboard

**Prepared by Tomas Corza** · Python / Streamlit / pandas

Interactive portfolio dashboard combining fictional Shopify-style store data with Google Ads and Meta Ads campaign reporting. This is a **demonstration project**, not an official Shopify, Google, or Meta integration. No production data, credentials, or employer information is included.

## Features
- Daily store sales, orders, average order value (AOV), and new customers
- Ad spend, marketing efficiency ratio (MER), blended customer acquisition cost (CAC), and platform-reported return on ad spend (ROAS)
- Interactive date range and ad-platform filters
- Daily sales and spend charts, campaign comparison table, CSV exports
- CSV upload for datasets following the documented column formats
- Automated unit tests for core calculations and validation

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The application opens in your browser (usually `http://localhost:8501`). It starts with fictional sample data, so no API credentials are needed.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Input schemas

`data/sample/shopify_sales.csv` — one row per **date** (or additive date-level rows):

| Column | Meaning |
| --- | --- |
| `date` | ISO date (`YYYY-MM-DD`) |
| `orders` | Number of orders |
| `revenue` | Store sales in USD, using one consistent sales definition |
| `new_customers` | First-time purchasing customers counted by store reporting |

`data/sample/paid_ads.csv` — one row per **date + platform + campaign**:

| Column | Meaning |
| --- | --- |
| `date` | ISO date |
| `platform` | For example, `Google Ads` or `Meta Ads` |
| `campaign` | Campaign name |
| `spend` | Ad spend in USD |
| `attributed_revenue` | Platform-reported attributed revenue in USD |
| `attributed_orders` | Platform-reported attributed orders |
| `attributed_new_customers` | New customers attributed to ads **only if the source actually supplies this metric** |

For a real export, aggregate orders carefully and map the actual field names into these schemas first. **Do not invent attributed new-customer counts**. If that metric is unavailable, the upload schema currently requires a numeric placeholder (use 0); attributed CAC will then appear N/A. This limitation is intentional and documented.

## Metric definitions

- **AOV** = store revenue ÷ store orders.
- **MER** = store revenue ÷ selected ad spend. Note the ad-platform filter only affects spend, not total store sales; interpret MER with that caveat.
- **Blended CAC** = selected ad spend ÷ *all store new customers*. This is an operational ratio, **not** proof of paid-acquired customers. With platform filtering, its meaning changes.
- **Platform ROAS** = sum of platform-attributed revenue ÷ selected ad spend. Multiple platforms may claim the same sale, so the numerator is **not deduplicated**.
- **Campaign attributed CAC** = campaign spend ÷ platform-reported attributed new customers; **CPA** = spend ÷ platform-reported attributed orders.

Ratios with zero denominators display `N/A`. All examples use USD; conversion to other currencies is not implemented.

## Data privacy

The included data is entirely synthetic. Uploaded files are processed in the running Streamlit process. Do not upload client/customer data to an unprotected, publicly hosted app. Never commit private exports, tokens, or secrets to GitHub. For confidential usage, run locally or behind access controls. `data/private/` and `.env` are ignored by Git.

## Limitations

- CSV-based; no live API connectors or automatic timezone/currency reconciliation.
- Assumes nonnegative aggregated financial metrics and a consistent revenue definition. Refund-specific adjustments need preprocessing.
- Dates are treated as calendar dates without timezone conversion.
- No multi-touch deduplication or causal attribution.
- The app is for descriptive analysis, not statistical forecasting.

## Project status and provenance

This is a newly authored general-purpose demonstration dashboard inspired by common e-commerce marketing analysis workflows. All included records are fictional. Automated unit tests cover calculation functions; browser/deployment testing should be performed separately.

Copyright © 2026 Tomas Corza. All rights reserved. No open-source license is granted.
