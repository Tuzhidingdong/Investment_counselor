# Data security and privacy

## Secrets

- Keep `IBKR_FLEX_TOKEN` in the operating system's environment/secret manager, not in chat, source files, YAML, `.env` committed to Git, screenshots, or logs.
- Keep `IBKR_FLEX_QUERY_ID` in the local environment as well. It is less sensitive than the token but should still remain local.
- Never print request URLs containing query parameters because the token is part of those parameters.
- If a token is exposed, disable/rotate it in IBKR Client Portal.

## Account data

- Flex reports contain financial and potentially identifying account information. Store only on a user-controlled local disk with appropriate OS access controls.
- The provided scripts save a normalized snapshot, not the original XML response. The normalized snapshot still contains financial data and must remain local.
- Never upload snapshots, raw statements, positions, trades, or account IDs to this repository or a public issue/PR.
- The default snapshot masks account IDs to their last four characters. Do not add full account IDs to logs or filenames.
- The repository `.gitignore` excludes local private data directories and snapshot files as a second line of defense; it is not a substitute for checking `git status` before pushing.

## Permissions

- Use a dedicated Flex Query containing only the required read/reporting sections.
- Keep the skill's broker access strictly read-only. It must not use the trading API or invoke order, transfer, withdrawal, or account-configuration methods.
