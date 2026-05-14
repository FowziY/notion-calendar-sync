import os

import requests
from dotenv import load_dotenv
from ics import Calendar, Event

# Load environment variables from .env
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
OUTPUT_FILE = "notion_calendar.ics"
NOTION_VERSION = "2022-06-28"


# Query Notion database for tasks
def get_notion_tasks():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    payload = {"page_size": 100}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json().get("results", [])


# Extract relevant task information
def extract_event_data(item):
    properties = item["properties"]

    name = properties.get("Name", {}).get("title", [])
    title = name[0]["plain_text"] if name else "Untitled Task"

    due_date = properties.get("Due Date", {}).get("date", {})
    if not due_date or not due_date.get("start"):
        return None

    status = properties.get("Status", {}).get("select", {}).get("name", "Unknown")
    if status.lower() == "done":
        return None

    return {
        "title": title,
        "date": due_date["start"],
        "status": status,
    }


# Build calendar events from task list
def build_calendar(events):
    calendar = Calendar()

    for ev in events:
        event = Event()
        event.name = f"{ev['title']} ({ev['status']})"
        event.begin = ev["date"]
        calendar.events.add(event)

    return calendar


# Main workflow
def main():
    notion_items = get_notion_tasks()
    events = []

    for item in notion_items:
        event = extract_event_data(item)
        if event:
            events.append(event)

    if not events:
        print("No upcoming tasks found.")
        return

    calendar = build_calendar(events)

    # Save generated calendar to disk
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.writelines(calendar.serialize_iter())

    print(f"Created {OUTPUT_FILE} with {len(events)} tasks.")


if __name__ == "__main__":
    main()
