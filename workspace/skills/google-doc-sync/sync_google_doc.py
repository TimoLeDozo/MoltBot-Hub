#!/usr/bin/env python3
"""
Create a Google Doc from a local Markdown file using a Service Account.

This script is native and standalone:
- no third-party SaaS wrappers
- official Google auth + API clients only
"""

import argparse
import pathlib
import sys

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


DEFAULT_SERVICE_ACCOUNT = "/app/config/google_service_account.json"
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Google Doc from a Markdown file."
    )
    parser.add_argument(
        "markdown_path",
        help="Local path to a Markdown file to upload into a new Google Doc.",
    )
    parser.add_argument(
        "--service-account",
        default=DEFAULT_SERVICE_ACCOUNT,
        help="Path to Service Account JSON key.",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Optional Google Doc title. Defaults to markdown filename stem.",
    )
    return parser.parse_args()


def load_markdown(path: pathlib.Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Markdown path is not a file: {path}")
    return path.read_text(encoding="utf-8")


def build_clients(service_account_path: str):
    credentials = Credentials.from_service_account_file(
        service_account_path, scopes=SCOPES
    )
    docs_service = build("docs", "v1", credentials=credentials, cache_discovery=False)
    drive_service = build(
        "drive", "v3", credentials=credentials, cache_discovery=False
    )
    return docs_service, drive_service


def create_doc_with_content(docs_service, title: str, content: str) -> str:
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    if content:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": content,
                        }
                    }
                ]
            },
        ).execute()
    return doc_id


def get_doc_url(drive_service, doc_id: str) -> str:
    file_meta = (
        drive_service.files()
        .get(fileId=doc_id, fields="webViewLink")
        .execute()
    )
    return file_meta.get("webViewLink") or f"https://docs.google.com/document/d/{doc_id}/edit"


def main() -> int:
    args = parse_args()
    md_path = pathlib.Path(args.markdown_path)
    doc_title = args.title.strip() or md_path.stem

    try:
        markdown_content = load_markdown(md_path)
        docs_service, drive_service = build_clients(args.service_account)
        doc_id = create_doc_with_content(docs_service, doc_title, markdown_content)
        doc_url = get_doc_url(drive_service, doc_id)
        # Print URL only so OpenClaw can consume directly.
        print(doc_url)
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except HttpError as exc:
        print(f"Google API error: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
