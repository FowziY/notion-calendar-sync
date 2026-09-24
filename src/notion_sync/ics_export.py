import os
from datetime import datetime, timedelta

from ics import Calendar, Event

from notion_sync.notion import (
    extract_event_data,
    get_notion_tasks,
    validate_environment,
)

OUTPUT_FILE = "data/processed/notion_calendar.ics"


def build_calendar(events):
    calendar = Calendar()

    for ev in events:
        event = Event()
        event.name = f"{ev['title']} ({ev['status']})"
        event.begin = ev["start"]
        if ev.get("end"):
            event.end = ev["end"]
        elif "T" not in ev["start"]:
            # All-day event end dates are exclusive, so use the next day.
            event.end = (
                datetime.fromisoformat(ev["start"]).date() + timedelta(days=1)
            ).isoformat()
        calendar.events.add(event)

    return calendar


def main():
    validate_environment()

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

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.writelines(calendar.serialize_iter())

    print(f"Created {OUTPUT_FILE} with {len(events)} tasks.")


if __name__ == "__main__":
    main()
