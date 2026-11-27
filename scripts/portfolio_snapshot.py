#!/usr/bin/env python3
"""Summarize a normalized IBKR Flex snapshot without blending currencies."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

VALUE_FIELDS = ("positionValue", "marketValue", "value")


def _decimal(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(value.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None


def summarize(snapshot: dict[str, Any]) -> dict[str, Any]:
    totals: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    excluded = 0
    statement_summaries = []

    for statement in snapshot.get("statements", []):
        for position in statement.get("open_positions", []):
            currency = position.get("currency") or position.get("fxCurrency")
            value_text = next((position.get(field) for field in VALUE_FIELDS if position.get(field) not in (None, "")), None)
            amount = _decimal(value_text)
            if not currency or amount is None:
                excluded += 1
                continue
            totals[currency] += amount
            counts[currency] += 1

        statement_summaries.append({
            "account_id_masked": statement.get("account_id_masked"),
            "statement_metadata": statement.get("statement_metadata", {}),
            "equity_summaries": statement.get("equity_summaries", []),
            "cash_reports": statement.get("cash_reports", []),
            "position_count": len(statement.get("open_positions", [])),
        })

    return {
        "retrieved_at_utc": snapshot.get("retrieved_at_utc"),
        "source": snapshot.get("source", snapshot.get("source_format")),
        "coverage": snapshot.get("coverage", {}),
        "positions_market_value_by_currency": {
            currency: {"amount": str(amount), "position_count": counts[currency]}
            for currency, amount in sorted(totals.items())
        },
        "position_rows_excluded_from_currency_totals": excluded,
        "statements": statement_summaries,
        "warnings": [
            "Position totals are grouped by each position's reported currency; they are not a single base-currency portfolio total.",
            "Cash reports and equity/NAV summaries are shown separately to avoid double counting.",
            "Rows without a recognizable currency or market-value field are excluded from the position totals but remain in the source snapshot.",
            "This summary does not calculate performance or drawdown. Deposits, withdrawals, FX, corporate actions, and reporting coverage must be reconciled first.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="Path to latest_flex_snapshot.json")
    parser.add_argument("--output", help="Optional path to write summary JSON; otherwise print to stdout")
    args = parser.parse_args()
    source = Path(args.snapshot)
    data = json.loads(source.read_text(encoding="utf-8"))
    summary = summarize(data)
    rendered = json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        print(f"Summary saved: {target}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
