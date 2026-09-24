import os

import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_VERSION = "2022-06-28"
REQUEST_TIMEOUT = 30

COMPLETED_STATUSES = {
    status.strip().lower()
    for status in os.getenv(
        "NOTION_COMPLETED_STATUSES", "Done,Completed,Cancelled,Archived"
    ).split(",")
    if status.strip()
}


def validate_environment():
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("DATABASE_ID")
    if not notion_token:
        raise RuntimeError("Missing NOTION_TOKEN in environment.")

    if not database_id:
        raise RuntimeError("Missing DATABASE_ID in environment.")

    return notion_token, database_id


def get_notion_tasks():
    notion_token, database_id = validate_environment()

    notion_api_url = f"https://api.notion.com/v1/databases/{database_id}/query"

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    tasks = []
    payload = {"page_size": 100}

    while True:
        response = requests.post(
            notion_api_url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()
        tasks.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data.get("next_cursor")

    return tasks


def extract_event_data(item):
    properties = item.get("properties", {})

    name = properties.get("Name", {}).get("title", [])
    title = name[0]["plain_text"] if name else "Untitled Task"

    due_date = properties.get("Due Date", {}).get("date", {})
    if not due_date or not due_date.get("start"):
        return None

    status_property = properties.get("Status", {})
    status_value = status_property.get("status") or status_property.get("select") or {}
    status = status_value.get("name", "Unknown")

    if status.strip().lower() in COMPLETED_STATUSES:
        return None

    return {
        "notion_page_id": item.get("id"),
        "title": title,
        "start": due_date["start"],
        "end": due_date.get("end"),
        "status": status,
        "url": item.get("url"),
    }
