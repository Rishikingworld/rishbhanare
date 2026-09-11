"""YouTube publisher for the AI Social Agent.

Uses YouTube Data API v3 + OAuth 2.0. Secrets/tokens are never stored in source.
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = Path(os.getenv("YOUTUBE_TOKEN_FILE", "secrets/youtube_token.json"))
CLIENT_SECRET_FILE = Path(os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "secrets/client_secret.json"))


def get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not CLIENT_SECRET_FILE.exists():
            raise FileNotFoundError(
                f"Missing {CLIENT_SECRET_FILE}. Download your OAuth client JSON from Google Cloud."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def upload_video(
    video_path: str,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
    publish_at: str | None = None,
    made_for_kids: bool = False,
    contains_synthetic_media: bool = True,
) -> dict:
    """Upload a video and return the YouTube video resource."""
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if privacy_status not in {"private", "public", "unlisted"}:
        raise ValueError("privacy_status must be private, public, or unlisted")
    if publish_at and privacy_status != "private":
        raise ValueError("publish_at requires privacy_status='private'")

    youtube = build("youtube", "v3", credentials=get_credentials())
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags or [],
            "categoryId": category_id,
            "defaultLanguage": "hi",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
            "containsSyntheticMedia": contains_synthetic_media,
        },
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at

    media = MediaFileUpload(str(path), chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        try:
            _, response = request.next_chunk()
        except HttpError as exc:
            if exc.resp.status in {500, 502, 503, 504}:
                time.sleep(2)
                continue
            raise

    return response


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a video to YouTube")
    parser.add_argument("video")
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--tags", default="")
    parser.add_argument("--privacy", default="private", choices=["private", "public", "unlisted"])
    parser.add_argument("--publish-at", default=None)
    args = parser.parse_args()
    result = upload_video(
        args.video,
        args.title,
        args.description,
        [x.strip() for x in args.tags.split(",") if x.strip()],
        privacy_status=args.privacy,
        publish_at=args.publish_at,
    )
    print(result)


if __name__ == "__main__":
    main()
