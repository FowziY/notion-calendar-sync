# Notion Calendar Sync

This project converts tasks from a Notion database into an `.ics` calendar file that can be imported into calendar applications such as Apple Calendar.

## Features

- Fetch tasks from a Notion database
- Generate a standard `.ics` calendar file
- Skip completed tasks automatically
- Support paginated Notion databases (100+ tasks)
- Optionally upload the generated `.ics` file to Google Drive
- Optional GitHub Actions automation for scheduled updates

```text
Notion Database
      ↓
Python sync script
      ↓
ICS calendar file
      ↓
Google Drive hosted file
      ↓
Calendar subscription
```

## Requirements

- Python 3.10+
- A Notion integration
- Access to a Notion database

## Repository Structure

```text
src/                  Core sync and upload logic
scripts/              Helper utilities
config/               Credential templates
data/processed/       Generated calendar files
.github/workflows/    GitHub Actions automation
tests/                Test suite
```

## Setup

### 1. Create a Notion Integration

Go to:

https://www.notion.so/my-integrations

Then:

1. Create a new integration
2. Copy the internal integration token
3. Share your Notion database with the integration

### 2. Create Environment File

Create a `.env` file in the project root:

```env
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_database_id

# Optional
MAKE_GDRIVE_FILE_PUBLIC=true
```

The `.env` file should never be committed.

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run

Generate the calendar file:

```bash
PYTHONPATH=src python -m notion_sync.notion_to_ics
```

After running, the script generates:

```text
data/processed/notion_calendar.ics
```

## Optional Google Drive Upload

This project includes an optional script for uploading or updating the generated `.ics` file on Google Drive.

Before using it, place your Google OAuth credentials file at:

```text
config/credentials.json
```

You can create OAuth credentials from the Google Cloud Console. A safe template is included at:

```text
config/credentials.example.json
```

Generate a refresh token locally:

```bash
python scripts/generate_gdrive_refresh_token.py
```

Then upload the generated calendar file:

```bash
PYTHONPATH=src python -m notion_sync.upload_to_gdrive
```

The script expects the generated calendar file at:

```text
data/processed/notion_calendar.ics
```

If `MAKE_GDRIVE_FILE_PUBLIC=true` is set, the uploaded `.ics` file will be publicly readable. This can be useful for subscribing to the calendar from calendar applications.
Do not enable public sharing for calendars containing:
- personal schedules
- research timelines
- confidential work
- client information
- lab or institutional data

## GitHub Actions Automation

The workflow in `.github/workflows/update_calendar.yml` can run manually or automatically every 3 hours.

Required repository secrets:

```text
NOTION_TOKEN
NOTION_DATABASE_ID
GOOGLE_CREDENTIALS_B64
GOOGLE_TOKEN_B64
```

The Google credentials and token files are stored as base64-encoded GitHub secrets and recreated during the workflow run.

## Expected Notion Properties

The database should contain the following properties:

| Property | Type |
|---|---|
| Name | Title |
| Due Date | Date |
| Status | Select |

Tasks with a status of `Done` are ignored.

## Local Files

The following files are generated locally and are ignored by Git:

```text
.env
config/credentials.json
config/mycreds.json
data/processed/notion_calendar.ics
```