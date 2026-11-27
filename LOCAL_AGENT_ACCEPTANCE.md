# Local Agent acceptance plan

This repository is the source of the `investment-counselor` skill. The local agent should sync it into the existing local skill directory, preferably:

`E:\IBKR\.agents\skills\investment-counselor\`

Do not copy account snapshots, Flex tokens, or the existing `.venv` into the repository. Do not replace the user's existing `stock-analysis`, `etf-premium`, `stock-correlation`, or `yfinance-data` skills.

## A. Installation and offline checks

From the skill root:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
python scripts\flex_sync.py --help
python scripts\portfolio_snapshot.py --help
python scripts\decision_journal.py --help
```

Expected: all seven unit tests pass; syntax checks and CLI help complete successfully. These checks do not contact IBKR and do not require credentials.

## B. Secure live Flex check

1. Inspect the local environment/secret manager to establish whether `IBKR_FLEX_TOKEN` and `IBKR_FLEX_QUERY_ID` already exist. Do not print their values or ask the user to paste them into chat.
2. Verify the configured Flex Query is XML and includes account information, NAV/equity summary, cash, open positions, trades, and cash transactions. Report missing sections clearly.
3. Run:

   ```powershell
   python scripts\flex_sync.py --output-dir data\private
   python scripts\portfolio_snapshot.py data\private\latest_flex_snapshot.json
   ```

4. Verify the output has a statement period, retrieval time, account ID masked to its last four characters, position/cash rows, currency labels, and coverage flags. Confirm the token and full account number do not appear in output or logs.
5. If current local access uses a different secret name or an existing secure Flex adapter, do not expose or hardcode the credential. Make a minimal local-only adapter/config mapping or report the exact integration gap; do not modify the upstream repository with machine-specific secrets.
6. Do not run a live sync repeatedly for testing: Flex generation is asynchronous and subject to IBKR request pacing.

## C. Behavioral acceptance scenarios

Test the skill against the live snapshot and current external sources where available:

1. **Current portfolio:** identify holdings, cash, NAV, currencies, statement date, retrieval timestamp, and missing data. Whole-account and invested-asset allocations must not be conflated.
2. **Continue buying VWRA?:** use the actual account, the 20+ year horizon, SGD 1,000–2,000/month contributions, and approximately 30% drawdown tolerance. Do not invent an approved target allocation.
3. **Add CSPX?:** calculate security-level overlap and incremental US/sector exposure with dated issuer holdings; do not infer overlap from fund names alone.
4. **SGD 1,500 monthly contribution:** treat this as a one-month scenario, show conditional options and resulting exposures, and do not modify the standing SGD 1,000–2,000 range.
5. **Market fall impact:** estimate exposure-weighted impact with dated prices and FX. Do not call raw NAV decline a drawdown without cash-flow adjustment.
6. **Why did the view change?:** compare the current snapshot and sources with a prior decision-journal entry and identify the changed facts.

For each scenario, capture the prompt, data timestamp, sources, output, gaps, and whether the answer respected the safety rules. Do not include account identifiers or balances in public GitHub diagnostics.

## D. Final report back to the user

Report only:

- Local skill path and synced branch/commit SHA.
- Offline test result.
- Whether live IBKR Flex sync succeeded and which sections were available (not credentials or account IDs).
- Which of the six behavior scenarios passed, failed, or were blocked by missing data.
- Exact blockers and the smallest next fix.

Do not claim continuous monitoring is active unless a scheduler was separately deployed and an observed successful run is available. Do not place trades or modify the broker account during acceptance.
