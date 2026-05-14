import json
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# Path to saved OAuth token
TOKEN_PATH = "config/mycreds.json"

# Generated calendar file
LOCAL_FILE = "data/processed/notion_calendar.ics"

# Target filename on Google Drive
DRIVE_FILE = "notion_calendar.ics"

# Optional flag to make uploaded file public
MAKE_PUBLIC = os.getenv("MAKE_GDRIVE_FILE_PUBLIC", "false").lower() == "true"


# Load saved Google credentials
def load_credentials():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Missing token file: {TOKEN_PATH}")

    with open(TOKEN_PATH, "r", encoding="utf-8") as file:
        token_data = json.load(file)

    return Credentials.from_authorized_user_info(
        token_data,
        ["https://www.googleapis.com/auth/drive"],
    )


# Upload or update file on Google Drive
def upload_to_drive(local_path, drive_filename):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    creds = load_credentials()

    service = build(
        "drive",
        "v3",
        credentials=creds,
    )

    # Check for existing file
    query = f"name='{drive_filename}' and trashed=false"

    results = (
        service.files()
        .list(
            q=query,
            fields="files(id, name)",
        )
        .execute()
    )

    items = results.get("files", [])

    media = MediaFileUpload(
        local_path,
        resumable=True,
    )

    # Update existing file
    if items:
        file_id = items[0]["id"]

        print(f"Updating existing file: {file_id}")

        service.files().update(
            fileId=file_id,
            media_body=media,
        ).execute()

    # Create new file
    else:
        print(f"Uploading new file: {drive_filename}")

        file_metadata = {"name": drive_filename}

        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
            )
            .execute()
        )

        file_id = file.get("id")

    # Optionally make file public
    if MAKE_PUBLIC:
        service.permissions().create(
            fileId=file_id,
            body={
                "type": "anyone",
                "role": "reader",
            },
        ).execute()

        print("Public read access enabled.")

    print(f"Upload complete. File ID: {file_id}")

    print(
        "Public URL:",
        f"https://drive.google.com/uc?id={file_id}&export=download",
    )


if __name__ == "__main__":
    upload_to_drive(LOCAL_FILE, DRIVE_FILE)
