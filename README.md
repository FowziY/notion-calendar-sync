# Notion Calendar Sync

This project synchronizes dated tasks from a Notion database to a dedicated,
private Google Calendar. Add the same Google account to Apple Calendar to see
the synchronized calendar on macOS, iPhone, and iPad without publishing an ICS
file on the web.

An optional local ICS export remains available for backups or one-off imports.

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

The sync creates or updates events marked as belonging to this integration. It
does not modify unrelated events. Previously synchronized events are removed
when their Notion page is deleted, completed, loses its due date, or otherwise
stops appearing in the source database.

## Requirements

- Python 3.10+
- A Notion integration with access to the source database
- A Google Cloud project with the Google Calendar API enabled
- Desktop OAuth credentials for the Google project

## Expected Notion properties

| Property | Type |
|---|---|
| Name | Title |
| Due Date | Date |
| Status | Status or Select |

Completed statuses are configured through `NOTION_COMPLETED_STATUSES`. Tasks
without a due date are also excluded.

## Local setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and supply:

```env
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_database_id
GOOGLE_CALENDAR_NAME=Notion Tasks
NOTION_COMPLETED_STATUSES=Done,Completed,Cancelled,Archived
```

`GOOGLE_CALENDAR_ID` is optional. If it is omitted, the sync finds a calendar
with the configured name or creates a new private calendar. Set the ID when you
want to target a specific existing calendar.

## Google OAuth setup

1. Enable the Google Calendar API in Google Cloud Console.
2. Create Desktop app OAuth credentials.
3. Download the credentials to `config/credentials.json`.
4. Run the local authorization helper:

```bash
python scripts/generate_google_calendar_token.py
```

The helper requests Google Calendar access and saves the reusable token to
`config/mycreds.json`. Both files are ignored by Git and must remain secret.

If an older token was generated for the Google Drive version of this project,
delete it locally and authorize again so the new token has Calendar scope.

## Run the private calendar sync

```bash
PYTHONPATH=src python -m notion_sync.google_calendar_sync
```

After the first successful run, enable the resulting Google calendar in Apple
Calendar. On macOS, add or enable the Google account in Calendar settings and
select the `Notion Tasks` calendar.

## Optional local ICS export

```bash
PYTHONPATH=src python -m notion_sync.notion_to_ics
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

Optionally configure `GOOGLE_CALENDAR_ID`. Encode the locally generated token
for `GOOGLE_TOKEN_B64` using:

```bash
base64 < config/mycreds.json | tr -d '\n'
```

The workflow reconstructs the token only for the duration of the job and syncs
directly to the private Google Calendar. It does not use Google Drive or create
public permissions.

## Tests

Run the unit tests from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The tests do not call Notion or Google APIs.

## Sensitive local files

Never commit:

```text
.env
config/credentials.json
config/mycreds.json
data/processed/notion_calendar.ics
```
