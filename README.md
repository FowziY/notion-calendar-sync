# Notion Calendar Sync

This project converts tasks from a Notion database into an `.ics` calendar file that can be imported into calendar applications such as Apple Calendar.

## Features

- Fetch tasks from a Notion database
- Generate a standard `.ics` calendar file
- Skip completed tasks automatically

## Requirements

- Python 3.10+
- A Notion integration
- Access to a Notion database

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
```

The `.env` file should never be committed.

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run

```bash
python notion_to_ics.py
```

After running, the script generates:

```text
notion_calendar.ics
```

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
notion_calendar.ics
```
