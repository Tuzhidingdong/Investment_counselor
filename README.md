# Investment Counselor

A local-first, read-only personal investment-advisor skill for an agent that can access the user's IBKR Flex Web Service and current market-data sources.

This repository provides reusable decision procedures and deterministic account-data helpers. It does **not** place orders, move money, change broker permissions, or claim continuous monitoring unless a scheduler is separately configured and verified.

## What it does

- Refreshes account statements from IBKR Flex Web Service v3 using credentials supplied only through environment variables.
- Normalizes XML Flex statements into a local JSON snapshot while preserving currency boundaries and data timestamps.
- Summarizes holdings and cash by currency without inventing FX conversions or treating incomplete reports as complete.
- Maintains an investor profile, explicit investment policy, monitoring thresholds, and a durable decision journal.
- Guides the agent through account-aware analysis of VWRA, S&P 500 ETFs, DCA, overlap, drawdown, costs, currency, and relevant market developments.
- Can optionally orchestrate already-installed `yfinance-data`, `etf-premium`, `stock-correlation`, and `stock-analysis` specialist skills without making them hard dependencies.

## Quick start

1. Copy `config/investor_profile.yaml`, `config/investment_policy.yaml`, and `config/alert_rules.yaml` into the agent's local writable skill data directory. Keep account-specific data outside Git.
2. In IBKR Client Portal, enable Flex Web Service and create an Activity Flex Query in **XML** format. Include account information, net asset value/equity summary, cash report, open positions, trades, cash transactions, dividends, interest, fees, and corporate actions as applicable.
3. Set `IBKR_FLEX_TOKEN` and `IBKR_FLEX_QUERY_ID` as environment variables. Do not paste credentials into prompts, YAML files, shell history, logs, or Git.
4. Run:

   ```bash
   python scripts/flex_sync.py --output-dir data/private
   python scripts/portfolio_snapshot.py data/private/latest_flex_snapshot.json
   ```

The scripts use only the Python standard library. The agent should still inspect `coverage` and `warnings` in each snapshot before drawing conclusions.

## Local data and privacy

`data/private/`, raw statements, snapshots, exports, logs, and `.env` files are intentionally ignored by Git. Do not commit them. The Flex token can grant access to financial reporting data; protect it as a secret and rotate it in IBKR if exposed.

## Current investor constraints encoded in the starter profile

- Investment horizon: 20+ years.
- Planned monthly contributions: SGD 1,000–2,000.
- Maximum acceptable portfolio drawdown: approximately 30%.
- Broker: IBKR; account access: read-only.
- Main interests: VWRA and S&P 500 ETFs.

No strategic asset-allocation target, tax residency, household balance sheet, emergency-fund status, or risk capacity beyond the stated drawdown tolerance is assumed. Those remain explicitly unset until the investor confirms them.

## Local acceptance

See [`LOCAL_AGENT_ACCEPTANCE.md`](LOCAL_AGENT_ACCEPTANCE.md) for the recommended local sync, offline tests, secure live Flex check, and six user-facing scenarios.

## Skill entrypoint

See [`SKILL.md`](SKILL.md). The skill is designed for local agents that discover `SKILL.md` skills. For other agent runtimes, adapt the entrypoint while retaining the same safety and data-quality rules.
