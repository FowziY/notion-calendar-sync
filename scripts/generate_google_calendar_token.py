import json
import os

from google_auth_oauthlib.flow import InstalledAppFlow


# Path to the Google OAuth client credentials downloaded
# from the Google Cloud Console
CREDENTIALS_PATH = "config/credentials.json"

# Path where the generated refresh/access token will be stored
TOKEN_PATH = "config/mycreds.json"

# Google Calendar API scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]


# Ensure the OAuth credentials file exists before starting
def validate_credentials_file():
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_PATH}")


def main():
    # Ensure the config directory exists
    os.makedirs("config", exist_ok=True)

    # Validate required OAuth client credentials
    validate_credentials_file()

    # Start the local OAuth authentication flow
    # This opens a browser window for Google login/consent
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
    )

    # Request offline access so a refresh token is generated
    credentials = flow.run_local_server(
        access_type="offline",
        prompt="consent",
    )

    # Save token information in a reusable JSON format
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    # Write token data to disk
    with open(TOKEN_PATH, "w", encoding="utf-8") as file:
        json.dump(token_data, file, indent=2)

    print(f"Saved token to {TOKEN_PATH}")

    # Confirm refresh token generation
    # Refresh tokens are required for unattended GitHub Actions syncs
    if credentials.refresh_token:
        print("Refresh token generated successfully.")
    else:
        print(
            "Warning: No refresh token received. "
            "Verify OAuth client is configured as a Desktop app."
        )


if __name__ == "__main__":
    main()
