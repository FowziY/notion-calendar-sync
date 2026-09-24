import json
import os

from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_PATH = "config/credentials.json"
TOKEN_PATH = "config/mycreds.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def validate_credentials_file():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_PATH}")


def main():
    os.makedirs("config", exist_ok=True)
    validate_credentials_file()

    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
    )

    # Offline access provides the refresh token needed for unattended syncs.
    credentials = flow.run_local_server(
        access_type="offline",
        prompt="consent",
    )

    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    with open(TOKEN_PATH, "w", encoding="utf-8") as file:
        json.dump(token_data, file, indent=2)

    print(f"Saved token to {TOKEN_PATH}")

    if credentials.refresh_token:
        print("Refresh token generated successfully.")
    else:
        print(
            "Warning: No refresh token received. "
            "Verify OAuth client is configured as a Desktop app."
        )


if __name__ == "__main__":
    main()
