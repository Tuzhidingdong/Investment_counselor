# IBKR Flex Web Service setup

## Required Client Portal configuration

1. In IBKR Client Portal, open **Performance & Reports → Flex Queries → Flex Web Service Configuration** and enable Flex Web Service.
2. Create or select an **Activity Flex Query** with XML output. At minimum, include sections available in the account that cover:
   - Account Information and account base currency
   - Net Asset Value / Equity Summary
   - Cash Report
   - Open Positions (including symbol, description, asset category, quantity, mark price, position value, currency, cost basis, and listing/exchange where available)
   - Trades / executions
   - Cash Transactions (deposits, withdrawals, dividends, interest, fees, taxes, and other cash movements)
   - Corporate Actions and transfers, where available
3. Copy the Flex Web Service token and the relevant Flex Query ID into the local secret/environment configuration. Do not paste the token into the agent conversation or save it in this repository.
4. Confirm that the query includes the intended account(s). Linked-account visibility and query selection are controlled by IBKR.

IBKR's Flex Web Service is a two-step reporting API: `/SendRequest` generates a report and returns a `ReferenceCode`; `/GetStatement` retrieves that report. Use API version 3. The report format is determined by the saved Flex Query, so this implementation requires XML.

## Local environment

The scripts read exactly these process environment variables:

- `IBKR_FLEX_TOKEN`
- `IBKR_FLEX_QUERY_ID`

Then run from the repository root:

```bash
python scripts/flex_sync.py --output-dir data/private
python scripts/portfolio_snapshot.py data/private/latest_flex_snapshot.json
```

No credentials are accepted as command-line arguments. The client does not print request URLs, because the token is transmitted as a query parameter in IBKR's documented interface.

## Query coverage caveats

- A section omitted from the configured Flex Query will not appear in the downloaded XML. The normalizer reports section presence in `coverage`; absence is not interpreted as a zero balance.
- Flex statement period and `whenGenerated` are separate from local retrieval time. Record all of them when discussing account freshness.
- A statement may report settled and unsettled cash, multiple currencies, and multiple NAV components. Do not sum all cash-report columns or NAV fields without understanding their definitions.
- Some IBKR statement fields can be delayed until settlement/FIFO calculations are ready. The client retries a small set of report-generation errors and fails visibly rather than treating an error XML payload as an empty portfolio.
- A query that produces CSV instead of XML must be reconfigured in Client Portal; the script intentionally rejects non-XML output.

## Official references

- [IBKR Flex Web Service introduction](https://www.interactivebrokers.com/docs/web-api/flex-web-service/introduction)
- [Enable and create an access token](https://www.interactivebrokers.com/docs/web-api/flex-web-service/client-portal-configuration/enable-and-create-access-token)
- [Generate a report](https://www.interactivebrokers.com/docs/web-api/flex-web-service/using-flex-web-service/generate-the-report)
- [Retrieve generated report](https://www.interactivebrokers.com/docs/web-api/api-reference/get-statement)
