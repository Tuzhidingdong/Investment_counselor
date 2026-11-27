#!/usr/bin/env python3
"""Append or list durable investment-decision records in local JSONL."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_record(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    required = ("question", "decision", "rationale")
    missing = [name for name in required if not str(payload.get(name, "")).strip()]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    record = {
        "record_id": str(uuid.uuid4()),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "question": payload["question"],
        "snapshot_ref": payload.get("snapshot_ref"),
        "facts_used": payload.get("facts_used", []),
        "options_considered": payload.get("options_considered", []),
        "decision": payload["decision"],
        "rationale": payload["rationale"],
        "risks": payload.get("risks", []),
        "confidence": payload.get("confidence", "not_stated"),
        "invalidation_conditions": payload.get("invalidation_conditions", []),
        "user_decision": payload.get("user_decision", "not_recorded"),
        "follow_up_date": payload.get("follow_up_date"),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="Append a decision record from a JSON file")
    add.add_argument("payload_json", help="JSON file containing question, decision, rationale, and optional evidence")
    add.add_argument("--journal", default="data/private/decision_journal.jsonl")
    listing = sub.add_parser("list", help="Print recent decision records")
    listing.add_argument("--journal", default="data/private/decision_journal.jsonl")
    listing.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    path = Path(args.journal)

    if args.command == "add":
        payload = json.loads(Path(args.payload_json).read_text(encoding="utf-8"))
        record = append_record(path, payload)
        print(f"Decision recorded: {record['record_id']} ({path})")
        return 0

    if not path.exists():
        print("No decision journal exists yet.")
        return 0
    if args.limit < 1:
        parser.error("--limit must be >= 1")
    lines = path.read_text(encoding="utf-8").splitlines()[-args.limit:]
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
