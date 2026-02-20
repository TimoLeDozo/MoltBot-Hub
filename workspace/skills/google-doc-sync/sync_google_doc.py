#!/usr/bin/env python3
"""
Placeholder script for future Google Doc synchronization via Service Account.

Current status:
- Parses args
- Verifies that the Service Account file exists
- Prints a TODO result payload
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Placeholder Google Doc sync")
    parser.add_argument(
        "--service-account",
        default="/app/config/google_service_account.json",
        help="Path to Google Service Account JSON key",
    )
    parser.add_argument("--doc-id", default="", help="Google Doc ID (future use)")
    parser.add_argument(
        "--input",
        default="/app/workspace/RELAIS_SOIR.md",
        help="Input file for sync content (future use)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exists = os.path.exists(args.service_account)

    result = {
        "status": "placeholder",
        "serviceAccountPath": args.service_account,
        "serviceAccountExists": exists,
        "docId": args.doc_id,
        "inputPath": args.input,
        "message": (
            "TODO: implement Google Docs API update with Service Account "
            "using google-auth + google-api-python-client."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(result, ensure_ascii=True))

    return 0 if exists else 2


if __name__ == "__main__":
    sys.exit(main())
