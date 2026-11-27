"""Normalize IBKR Flex XML while preserving currencies and source attributes."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

SECTION_TAGS = {
    "equity_summaries": {"EquitySummaryInBase", "EquitySummaryByReportDateInBase", "NetAssetValue"},
    "cash_reports": {"CashReport", "CashReportCurrency"},
    "open_positions": {"OpenPosition"},
    "trades": {"Trade"},
    "cash_transactions": {"CashTransaction"},
    "corporate_actions": {"CorporateAction"},
    "dividends": {"Dividend"},
    "interest_accruals": {"InterestAccrual"},
    "fees": {"Fee"},
    "forex_positions": {"ForexPosition"},
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def masked_account_id(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    return f"***{value[-4:]}" if len(value) > 4 else "***"


def _safe_attributes(element: ET.Element) -> dict[str, str]:
    safe: dict[str, str] = {}
    for key, value in element.attrib.items():
        name = local_name(key)
        if name.lower() in {"accountid", "acctid", "accountnumber", "acctnumber"}:
            safe["account_id_masked"] = masked_account_id(value) or "***"
        else:
            safe[name] = value
    return safe


def _findall_by_names(root: ET.Element, names: set[str]) -> list[ET.Element]:
    return [element for element in root.iter() if local_name(element.tag) in names]


def normalize_flex_xml(xml_text: str) -> dict[str, Any]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError("Flex report XML could not be parsed.") from exc

    failure = next((element for element in root.iter() if local_name(element.tag) == "Status" and (element.text or "").strip().lower() == "fail"), None)
    if failure is not None:
        raise ValueError("The provided XML is an IBKR error response, not a portfolio report.")

    statements = [element for element in root.iter() if local_name(element.tag) == "FlexStatement"]
    if not statements:
        raise ValueError("No FlexStatement element found. Check the selected Flex Query and XML export format.")

    normalized_statements: list[dict[str, Any]] = []
    aggregate_coverage = {key: False for key in ["account_information", *SECTION_TAGS.keys()]}
    for statement in statements:
        attrs = _safe_attributes(statement)
        account_id = attrs.pop("account_id_masked", None)
        statement_data: dict[str, Any] = {
            "account_id_masked": account_id,
            "statement_metadata": attrs,
            "account_information": [],
        }
        for account_info in _findall_by_names(statement, {"AccountInformation"}):
            statement_data["account_information"].append(_safe_attributes(account_info))

        for output_key, tag_names in SECTION_TAGS.items():
            rows = [_safe_attributes(element) for element in _findall_by_names(statement, tag_names)]
            statement_data[output_key] = rows
            aggregate_coverage[output_key] = aggregate_coverage[output_key] or bool(rows)
        aggregate_coverage["account_information"] = aggregate_coverage["account_information"] or bool(statement_data["account_information"])
        normalized_statements.append(statement_data)

    return {
        "schema_version": 1,
        "source_format": "IBKR Flex XML",
        "query_name": root.attrib.get("queryName") or root.attrib.get("name"),
        "coverage": aggregate_coverage,
        "warnings": [
            "Only sections selected in the configured Flex Query can appear in this snapshot.",
            "Missing sections are unknown, not zero. Verify the statement period and report coverage before analysis.",
            "Amounts remain in their source currencies; no FX conversion or total portfolio valuation is inferred here.",
        ],
        "statements": normalized_statements,
    }
