#!/usr/bin/env python3
"""Fetch an IBKR Flex Web Service v3 report and save a sanitized JSON snapshot.

Credentials are read exclusively from IBKR_FLEX_TOKEN and IBKR_FLEX_QUERY_ID.
No third-party dependencies are required.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

try:
    from .flex_parser import normalize_flex_xml
except ImportError:  # Support direct execution: python scripts/flex_sync.py
    from flex_parser import normalize_flex_xml

BASE_URL = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"
USER_AGENT = "InvestmentCounselor/0.1 Python-urllib"
TRANSIENT_ERROR_CODES = {"1003", "1004", "1005", "1006", "1007", "1008", "1009", "1018", "1019", "1021"}


class FlexServiceError(RuntimeError):
    """Safe-to-display error that never includes request URLs or credentials."""


def _request_xml(endpoint: str, params: dict[str, str], timeout: int) -> bytes:
    url = f"{BASE_URL}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/xml,text/xml,*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        # Do not stringify the exception: urllib errors can contain the credential-bearing URL.
        raise FlexServiceError(f"IBKR Flex request failed with HTTP status {exc.code}.") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise FlexServiceError("Could not reach the IBKR Flex Web Service. Check connectivity and try again.") from None


def _child_text(node: ET.Element, name: str) -> str | None:
    for child in list(node):
        if child.tag.rsplit("}", 1)[-1].lower() == name.lower():
            return (child.text or "").strip()
    return None


def _parse_service_error(payload: bytes) -> tuple[str, str, str] | None:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        return None
    status = _child_text(root, "Status")
    if status and status.lower() == "fail":
        return (
            _child_text(root, "ErrorCode") or "unknown",
            _child_text(root, "ErrorMessage") or "IBKR returned an unspecified Flex error",
            status,
        )
    return None


def _send_request(token: str, query_id: str, timeout: int) -> str:
    payload = _request_xml("SendRequest", {"t": token, "q": query_id, "v": "3"}, timeout)
    try:
        root = ET.fromstring(payload)
    except ET.ParseError:
        raise FlexServiceError("IBKR returned an unreadable SendRequest response (expected XML).") from None
    status = _child_text(root, "Status")
    if status != "Success":
        code = _child_text(root, "ErrorCode") or "unknown"
        message = _child_text(root, "ErrorMessage") or "IBKR did not confirm report generation"
        raise FlexServiceError(f"IBKR SendRequest failed (code {code}): {message}")
    reference = _child_text(root, "ReferenceCode")
    if not reference or not reference.isdigit():
        raise FlexServiceError("IBKR SendRequest succeeded but returned no valid report reference code.")
    return reference


def _get_statement(token: str, reference_code: str, timeout: int) -> bytes:
    return _request_xml("GetStatement", {"t": token, "q": reference_code, "v": "3"}, timeout)


def fetch_flex_report(token: str, query_id: str, timeout: int = 30, max_attempts: int = 6) -> bytes:
    """Fetch report bytes using the documented two-step Flex v3 protocol."""
    if not token.strip() or not query_id.strip():
        raise FlexServiceError("IBKR_FLEX_TOKEN and IBKR_FLEX_QUERY_ID must both be set.")

    reference_code = _send_request(token, query_id, timeout)
    # Report generation is asynchronous. Poll GetStatement at a conservative
    # interval; do not repeat SendRequest when the report is still processing.
    for attempt in range(max_attempts):
        time.sleep(2 if attempt == 0 else min(2 * (attempt + 1), 10))
        payload = _get_statement(token, reference_code, timeout)
        service_error = _parse_service_error(payload)
        if service_error is None:
            try:
                ET.fromstring(payload)
            except ET.ParseError:
                raise FlexServiceError("IBKR returned a non-XML report. Configure this Flex Query to export XML.") from None
            return payload
        code, message, _ = service_error
        if code not in TRANSIENT_ERROR_CODES or attempt == max_attempts - 1:
            raise FlexServiceError(f"IBKR GetStatement failed (code {code}): {message}")
    raise FlexServiceError("IBKR report was not ready after the allowed polling attempts.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="data/private", help="Local directory for private snapshots (default: data/private)")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds (default: 30)")
    parser.add_argument("--max-attempts", type=int, default=6, help="GetStatement polling attempts (default: 6)")
    args = parser.parse_args(argv)

    token = os.environ.get("IBKR_FLEX_TOKEN", "")
    query_id = os.environ.get("IBKR_FLEX_QUERY_ID", "")
    if not token or not query_id:
        print("ERROR: Set IBKR_FLEX_TOKEN and IBKR_FLEX_QUERY_ID in the local process environment.", file=sys.stderr)
        return 2

    try:
        xml_bytes = fetch_flex_report(token, query_id, timeout=args.timeout, max_attempts=args.max_attempts)
        snapshot = normalize_flex_xml(xml_bytes.decode("utf-8-sig"))
    except (FlexServiceError, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    snapshot["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    snapshot["source"] = "IBKR Flex Web Service v3"
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "latest_flex_snapshot.json"
    temp_path = output_path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_path.replace(output_path)

    coverage = snapshot.get("coverage", {})
    available = ", ".join(name for name, present in coverage.items() if present) or "no recognized sections"
    print(f"Snapshot saved: {output_path}")
    print(f"Statement(s): {len(snapshot.get('statements', []))}; available sections: {available}")
    print("Privacy: account identifiers masked; Flex token not written to the snapshot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
