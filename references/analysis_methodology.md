# Portfolio analysis methodology

## 1. Establish a reliable account snapshot

Start with the most recent successful broker report. Record account base currency, statement period, report generation timestamp, local retrieval timestamp, query coverage, and any missing sections. Reconcile NAV, open positions, cash, and transactions before deriving portfolio-level conclusions.

Show at least three views separately:

- **Broker-reported NAV:** the broker's reported total for the relevant date and base currency.
- **Invested positions:** market value of open positions, grouped by their native reporting currency.
- **Cash and cash equivalents:** cash rows by currency and settlement status where available.

Do not add these together when the broker-reported NAV already includes them. Do not equate invested-asset weights with whole-account weights.

## 2. Currency treatment

Never add unlike currencies. For a consolidated SGD view, obtain a dated FX rate for each required currency pair, record the source and timestamp, and show the conversion formula. Distinguish trading currency from fund base currency and underlying exposure currency. A USD-listed or USD-traded share class does not automatically imply that all its underlying exposure is USD-only; conversely, a global equity ETF with substantial US holdings still carries meaningful US-market exposure.

## 3. ETF look-through and overlap

For each ETF, use the issuer's latest available holdings file or factsheet and retain its as-of date. Normalize identifiers (prefer ISIN or a stable security identifier; do not match only on ticker when multiple listings exist). Calculate:

- Weighted exposure by underlying security: `portfolio_weight × ETF_weight_in_security`.
- Pairwise overlap using the sum of the lesser of the two funds' weights for each common security.
- Look-through country, sector, and issuer concentration, retaining the provider's classification method.

Disclose differences in holdings dates, cash/derivative treatment, share classes, and missing constituents. Do not add ETF weights and constituent weights as if they were separate assets. Do not assume all S&P 500 ETFs are tax-, domicile-, or trading-cost-equivalent.

## 4. Risk and drawdown

Distinguish volatility, historical maximum drawdown, current peak-to-trough loss, and the investor's stated tolerance. The approximate 30% tolerance is a user constraint—not a portfolio stop-loss, prediction, or guarantee.

A raw decline in account NAV is not necessarily investment loss: deposits, withdrawals, dividends, currency movements, fees, transfers, and corporate actions can change NAV. To calculate portfolio drawdown, construct a cash-flow-adjusted total-return/unitized series with correctly dated external flows and distributions. If the available data cannot support that calculation, report the observed NAV change and say that drawdown is not established.

For holdings-level stress analysis, shock each asset in its own currency, then convert with separately stated FX scenarios. State that correlations and crisis relationships can change materially.

## 5. DCA and allocation scenarios

The known monthly contribution range is SGD 1,000–2,000. A one-off question using (for example) SGD 1,500 is a scenario, not a permanent profile change. Compare contribution options against the actual portfolio and the investor-approved policy. Show how each option changes equity/bond/cash, US/global equity, currency, and concentration exposures.

No strategic allocation has been approved in the starter policy. Until it is, show conditional scenarios and explain tradeoffs; do not label a model-generated allocation as the user's target. A cash balance also may be earmarked for near-term needs that have not yet been disclosed.

## 6. Product comparison

Compare the exact share classes, not just tickers. Include domicile, legal structure, accumulating/distributing treatment, replication method, index, TER/OCF, fund size, tracking difference where available, securities lending policy, currency exposure, exchange/listing, bid-ask spread, dealing currency, broker commissions, and relevant tax treatment. Tax conclusions require confirmed tax residency and current authoritative material.

## 7. Backtests

A backtest is decision support, not a forecast. Require a common date range, total-return series, correct reinvestment, currency conversion, fees, taxes where applicable, contribution timing, rebalancing assumptions, and survivorship/data-bias checks. Use the same start/end dates and comparable data sources for all alternatives. Label synthetic or proxy data explicitly. Do not compare a price-only series with a total-return series.

## 8. Evidence and recommendation structure

For current facts, prefer issuer/official sources and record the effective/as-of date. Cite sources near the claims they support. A useful recommendation contains:

1. Verified account facts and timestamp.
2. The decision being considered.
3. Two or more viable options, including doing nothing where appropriate.
4. Expected exposure changes and costs.
5. Main downside risks and uncertainty.
6. Conditions that would change the conclusion.
7. A journal entry linking the view to the snapshot and sources.
