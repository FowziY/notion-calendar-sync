import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

CREDENTIALS_PATH = "config/credentials.json"
TOKEN_PATH = "config/mycreds.json"
LOCAL_FILE = "data/processed/notion_calendar.ics"
DRIVE_FILE = "notion_calendar.ics"


# Authenticate with Google Drive
def authenticate_drive():
    gauth = GoogleAuth()

    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_PATH}")

    gauth.LoadClientConfigFile(CREDENTIALS_PATH)
    gauth.LoadCredentialsFile(TOKEN_PATH)

    if gauth.credentials is None:
        print("No credentials found. Opening browser for authentication.")
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        print("Token expired. Refreshing credentials.")
        gauth.Refresh()
    else:
        print("Credentials loaded successfully.")
        gauth.Authorize()

    gauth.SaveCredentialsFile(TOKEN_PATH)

    return GoogleDrive(gauth)


# Upload or update a single file on Google Drive
def upload_to_drive(local_path, drive_filename):
    drive = authenticate_drive()

    print(f"Searching for existing file named '{drive_filename}'.")
    existing_files = drive.ListFile(
        {"q": f"title='{drive_filename}' and trashed=false"}
    ).GetList()

    if existing_files:
        file = existing_files[0]
        print(f"Found existing file. Updating: {file['id']}")
    else:
        file = drive.CreateFile({"title": drive_filename})
        print(f"Uploading new file: {drive_filename}")

    file.SetContentFile(local_path)
    file.Upload()

    print(f"Upload complete. File ID: {file['id']}")
    print(f"View in Drive: https://drive.google.com/file/d/{file['id']}/view")


# Main workflow
def main():
    if not os.path.exists(LOCAL_FILE):
        raise FileNotFoundError(f"File not found: {LOCAL_FILE}")

    upload_to_drive(LOCAL_FILE, DRIVE_FILE)


if __name__ == "__main__":
    main()
