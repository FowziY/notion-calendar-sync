# Notion Calendar Sync

This project synchronizes dated tasks from a Notion database to a dedicated,
private Google Calendar. Add the same Google account to Apple Calendar to see
the synchronized calendar on macOS, iPhone, and iPad without publishing an ICS
file online.

An optional ICS export is included for local backups or one-off imports.

## How it works

```text
Notion database
      ↓
Scheduled Python sync
      ↓
Private Google Calendar
      ↓
Apple Calendar via the authenticated Google account
```

The sync creates and updates events marked as belonging to this integration. Unrelated Google Calendar events are left untouched.

Previously synchronized events are removed when their Notion task no longer appears as active, for example when it is deleted, completed, or no longer has a due date.

As a safety measure, the sync refuses to delete all existing synced events if Notion unexpectedly returns no active tasks.

## Requirements

- Python 3.12+
- A Notion integration with access to the source database
- A Google Cloud project with the Google Calendar API enabled
- Desktop OAuth credentials for the Google project

## Expected Notion properties

| Property | Type |
|---|---|
| Name | Title |
| Due Date | Date |
| Status | Status or Select |

Completed statuses are configured through `NOTION_COMPLETED_STATUSES`.
Tasks without a due date are ignored.

## Local setup

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```
Install the project:
```bash
python -m pip install -e .
```

Copy the example environment file:
```bash
cp .env.example .env
```
Then provide the required values:
```env
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_database_id
GOOGLE_CALENDAR_NAME=Notion Tasks
NOTION_COMPLETED_STATUSES=Done,Completed,Cancelled,Archived
```

`GOOGLE_CALENDAR_ID` is optional. 

If it is not provided, the sync looks for a calendar matching `GOOGLE_CALENDAR_NAME` and creates one if necessary.

Set `GOOGLE_CALENDAR_ID` when you want to target a specific existing calendar.

## Google OAuth setup

1. Enable the Google Calendar API in Google Cloud Console.
2. Create OAuth credentials for a Desktop app.
3. Download the credentials to `config/credentials.json`.
4. Run the local authorization helper:

```bash
python scripts/generate_google_calendar_token.py
```
The helper opens the Google OAuth flow and writes the resulting reusable credentials to `config/mycreds.json`.

Offline access is requested so the generated refresh token can be used by unattended syncs.

Both files are ignored by Git and should remain secret.

## Run the private calendar sync

```bash
python -m notion_sync.google_calendar_sync
```
The sync will find or create the configured private Google Calendar and create, update, or remove integration-owned events as needed.

After the first successful run, the resulting Google Calendar can be enabled in Apple Calendar through the same Google account.

## Optional local ICS export
To generate a local `.ics` file instead of syncing directly to Google Calendar:
```bash
python -m notion_sync.ics_export
```

This writes `data/processed/notion_calendar.ics`. The file is ignored by Git
and is not uploaded or made public by the automated workflow.

## GitHub Actions automation

`.github/workflows/update_calendar.yml` runs manually or every three hours.
Configure these repository secrets:

```text
NOTION_TOKEN
NOTION_DATABASE_ID
GOOGLE_TOKEN_B64
```

`GOOGLE_CALENDAR_ID` can also be configured if the workflow should target a specific existing calendar.
Encode the locally generated token using:

```bash
base64 < config/mycreds.json | tr -d '\n'
```

The workflow reconstructs the token only for the duration of the job and syncs
directly to the private Google Calendar. It does not use Google Drive or create
public permissions.

## Tests

Run the unit tests from the repository root:

```bash
python -m unittest discover -s tests -v
```
The current tests use mocks and local data structures rather than making live requests to the Notion or Google APIs.

They cover:

- Notion task extraction and completed-status filtering
- legacy Notion `select` status properties
- all-day and timed Google Calendar event handling
- create, update, and delete behavior
- protection against deleting all synced events when no active Notion tasks are returned

## Sensitive local files

The following files contain local configuration or credentials and must not be committed:

```text
.env
config/credentials.json
config/mycreds.json
data/processed/notion_calendar.ics
```
The repository includes `.env.example` and `config/credentials.example.json` as safe templates.
