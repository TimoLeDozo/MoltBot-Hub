#!/usr/bin/env python3
"""
Create a Google Doc from a local Markdown file using User OAuth 2.0.

This script is native and standalone:
- no third-party SaaS wrappers
- official Google auth + API clients only
"""

import argparse
import json
import os
import pathlib
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CLIENT_SECRETS_FILE = "/app/config/client_secret.json"
TOKEN_FILE = "/app/config/token.json"
PARENT_FOLDER_ID = "1Phx9MyQNae77TlxMkjSv0YmhMCNOuCgD"
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


def build_clients():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            # IMPORTANT: Use run_console() for headless Docker.
            if hasattr(flow, "run_console"):
                creds = flow.run_console()
            else:
                auth_url, _ = flow.authorization_url(
                    access_type="offline", prompt="consent"
                )
                print(
                    "Open this URL to authorize access, then paste the code:",
                    file=sys.stderr,
                )
                print(auth_url, file=sys.stderr)
                code = os.environ.get("GOOGLE_OAUTH_CODE")
                if not code:
                    code = input("Enter verification code: ").strip()
                flow.fetch_token(code=code)
                creds = flow.credentials
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return docs_service, drive_service


def create_doc_with_content(docs_service, drive_service, title: str, content: str) -> str:
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [PARENT_FOLDER_ID],
    }
    doc = (
        drive_service.files()
        .create(body=file_metadata, fields="id", supportsAllDrives=True)
        .execute()
    )
    doc_id = doc.get("id")

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
        .get(fileId=doc_id, fields="webViewLink", supportsAllDrives=True)
        .execute()
    )
    return file_meta.get("webViewLink") or f"https://docs.google.com/document/d/{doc_id}/edit"


def main() -> int:
    args = parse_args()
    md_path = pathlib.Path(args.markdown_path)
    doc_title = args.title.strip() or md_path.stem

    try:
        markdown_content = load_markdown(md_path)
        docs_service, drive_service = build_clients()
        doc_id = create_doc_with_content(
            docs_service, drive_service, doc_title, markdown_content
        )
        doc_url = get_doc_url(drive_service, doc_id)
        print(
            json.dumps(
                {
                    "status": "success",
                    "url": doc_url,
                    "documentId": doc_id,
                }
            )
        )
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": str(exc),
                    "code": "INVALID_INPUT",
                }
            )
        )
        print(str(exc), file=sys.stderr)
        return 2
    except HttpError as exc:
        message = f"Google API error: {exc}"
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": message,
                    "code": "GOOGLE_API_ERROR",
                }
            )
        )
        print(message, file=sys.stderr)
        return 3
    except Exception as exc:
        message = f"Unexpected error: {exc}"
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": message,
                    "code": "UNEXPECTED_ERROR",
                }
            )
        )
        print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
