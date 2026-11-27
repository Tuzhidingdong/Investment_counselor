# Monitoring operations

## What this skill can and cannot do

A Skill supplies reusable procedures and local scripts. It does not run continuously by itself. Background checks require a separately configured scheduler, automation, or agent runtime that can invoke the skill and retrieve fresh market/account data. Until a scheduled run has been tested and its last-success timestamp is visible, report background monitoring as **not enabled**.

## Suggested monitoring cadence

The investor or local agent may choose a cadence after testing data access and rate limits. A practical starting point is:

- Account snapshot: on user request and after meaningful account activity; avoid unnecessary repeated Flex report generation.
- Allocation / concentration review: monthly, after a contribution, or when a major position/fund change occurs.
- Fund factsheet / holdings / fee review: monthly or after an issuer announcement.
- Macro and FX context: when a material event affects held assets, not as an automatic trade signal.
- Policy review: when the investor's time horizon, contribution amount, risk tolerance, liquidity needs, or tax residency changes.

These are suggested operating intervals, not an active schedule.

## Alert rules

Use `config/alert_rules.yaml` as a set of review thresholds. Before raising an alert, verify:

1. The broker snapshot is fresh enough for the specific alert.
2. Required statement sections and prices are present.
3. Currency conversions use a dated source.
4. The alert is not driven by a data error, stale holding, duplicate transaction, or unadjusted cash flow.

The 15%, 20%, and 25% drawdown values are review prompts, with 30% as the investor's stated tolerance reference. Do not calculate them from raw NAV changes. A cash-flow-adjusted total-return series is required.

Allocation drift alerts remain disabled until the investor approves target weights and tolerance bands. Concentration thresholds remain unset until confirmed. Do not convert market volatility or a central-bank announcement into an automatic buy/sell alert.

## Operational status to report

When asked about monitoring status, report:

- Is the scheduler configured? (yes/no)
- What invokes the check and how often?
- Last successful account sync and its statement period.
- Last successful market-data update and the source.
- Last run result and any gaps.
- Which alert classes are actually active versus merely configured as review prompts.

Never state “24/7 monitoring” unless the user-controlled scheduler and all required data sources have been deployed, tested, and observed running.
