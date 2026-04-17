#!/usr/bin/env python3
"""
add_post.py - Append a new post row to the content management Google Sheet.

Usage:
    python3 add_post.py                         # uses defaults defined in CURRENT_POST
    python3 add_post.py --json path/to/key.json # specify service account key path

The service account must have Editor access to the sheet.
"""

import argparse
import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

SPREADSHEET_ID = "1Lm_BCv3CUOtJqTh2gedXIqjt96k4jgTFksvMOOeLGTA"
SHEET_NAME = "Sheet1"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Column order matches the header row exactly:
# Post # | Category | Topic | Angle | Style Notes | Image Description | Comments Link | Full Post Text
COLUMNS = [
    "post_number",
    "category",
    "topic",
    "angle",
    "style_notes",
    "image_description",
    "comments_link",
    "full_post_text",
]


def get_service(key_path: str):
    creds = service_account.Credentials.from_service_account_file(
        key_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def append_post(service, post: dict) -> dict:
    row = [post.get(col, "TBD") or "TBD" for col in COLUMNS]
    body = {"values": [row]}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:H",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="Append a post row to the Google Sheet.")
    parser.add_argument(
        "--json",
        dest="key_path",
        default=os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json"),
        help="Path to service account JSON key (default: service_account.json or $GOOGLE_SERVICE_ACCOUNT_JSON)",
    )
    # Optional per-field overrides so the script is easy to call from the CLI
    for col in COLUMNS:
        parser.add_argument(f"--{col.replace('_', '-')}", default=None)

    args = parser.parse_args()

    if not os.path.exists(args.key_path):
        print(f"ERROR: Service account key not found at '{args.key_path}'.")
        print("Provide the path with --json <path> or set $GOOGLE_SERVICE_ACCOUNT_JSON.")
        sys.exit(1)

    # Build post dict: CLI args win over the hardcoded current post below
    current_post = {
        "post_number": "2",
        "category": "Financial advice (stocks)",
        "topic": "Top stocks for AI energy",
        "angle": "TBD",
        "style_notes": "TBD",
        "image_description": "Paste manually",
        "comments_link": "instagram.com/p/DWbeKAWiOdG/",
        "full_post_text": "TBD",
    }

    for col in COLUMNS:
        cli_val = getattr(args, col, None)
        if cli_val is not None:
            current_post[col] = cli_val

    service = get_service(args.key_path)
    result = append_post(service, current_post)

    updates = result.get("updates", {})
    print(f"Row appended successfully.")
    print(f"Updated range : {updates.get('updatedRange', 'n/a')}")
    print(f"Updated rows  : {updates.get('updatedRows', 'n/a')}")
    print(f"Row data      : {[current_post.get(c) for c in COLUMNS]}")


if __name__ == "__main__":
    main()
