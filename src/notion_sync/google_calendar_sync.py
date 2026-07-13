import json
import os
from datetime import date, datetime, timedelta

from notion_sync.notion_to_ics import (
    extract_event_data,
    get_notion_tasks,
    validate_environment,
)


TOKEN_PATH = "config/mycreds.json"
CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar"
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
CALENDAR_NAME = os.getenv("GOOGLE_CALENDAR_NAME", "Notion Tasks")
SYNC_MARKER = "notion-calendar-sync"


def load_credentials():
    from google.oauth2.credentials import Credentials

    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Missing token file: {TOKEN_PATH}")

    with open(TOKEN_PATH, "r", encoding="utf-8") as file:
        token_data = json.load(file)

    if "token" not in token_data and "access_token" in token_data:
        token_data["token"] = token_data["access_token"]

    return Credentials.from_authorized_user_info(token_data, [CALENDAR_SCOPE])


def find_or_create_calendar(service):
    if CALENDAR_ID:
        service.calendars().get(calendarId=CALENDAR_ID).execute()
        return CALENDAR_ID

    page_token = None
    while True:
        response = service.calendarList().list(pageToken=page_token).execute()
        for calendar in response.get("items", []):
            if calendar.get("summary") == CALENDAR_NAME:
                return calendar["id"]
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    calendar = service.calendars().insert(body={"summary": CALENDAR_NAME}).execute()
    return calendar["id"]


def _event_times(event):
    start_value = event["start"]
    end_value = event.get("end")

    if "T" not in start_value:
        start_date = date.fromisoformat(start_value)
        end_date = (
            date.fromisoformat(end_value) + timedelta(days=1)
            if end_value
            else start_date + timedelta(days=1)
        )
        return {"date": start_date.isoformat()}, {"date": end_date.isoformat()}

    start_datetime = datetime.fromisoformat(start_value.replace("Z", "+00:00"))
    end_datetime = (
        datetime.fromisoformat(end_value.replace("Z", "+00:00"))
        if end_value
        else start_datetime + timedelta(hours=1)
    )
    return {"dateTime": start_datetime.isoformat()}, {"dateTime": end_datetime.isoformat()}


def build_google_event(event):
    start, end = _event_times(event)
    description_parts = [f"Notion status: {event['status']}"]
    if event.get("url"):
        description_parts.append(event["url"])

    return {
        "summary": event["title"],
        "description": "\n\n".join(description_parts),
        "start": start,
        "end": end,
        "extendedProperties": {
            "private": {
                "syncSource": SYNC_MARKER,
                "notionPageId": event["notion_page_id"],
            }
        },
    }


def list_synced_events(service, calendar_id):
    events = {}
    page_token = None
    while True:
        response = (
            service.events()
            .list(
                calendarId=calendar_id,
                privateExtendedProperty=f"syncSource={SYNC_MARKER}",
                pageToken=page_token,
                showDeleted=False,
            )
            .execute()
        )
        for event in response.get("items", []):
            notion_id = (
                event.get("extendedProperties", {})
                .get("private", {})
                .get("notionPageId")
            )
            if notion_id:
                events[notion_id] = event
        page_token = response.get("nextPageToken")
        if not page_token:
            return events


def sync_events(service, calendar_id, notion_events):
    existing = list_synced_events(service, calendar_id)
    active_ids = set()
    created = updated = deleted = 0

    for notion_event in notion_events:
        notion_id = notion_event["notion_page_id"]
        if not notion_id:
            continue
        active_ids.add(notion_id)
        body = build_google_event(notion_event)
        current = existing.get(notion_id)
        if current:
            service.events().update(
                calendarId=calendar_id,
                eventId=current["id"],
                body=body,
            ).execute()
            updated += 1
        else:
            service.events().insert(calendarId=calendar_id, body=body).execute()
            created += 1

    for notion_id, current in existing.items():
        if notion_id not in active_ids:
            service.events().delete(
                calendarId=calendar_id,
                eventId=current["id"],
            ).execute()
            deleted += 1

    return created, updated, deleted


def main():
    from googleapiclient.discovery import build

    validate_environment()
    credentials = load_credentials()
    service = build("calendar", "v3", credentials=credentials)
    calendar_id = find_or_create_calendar(service)
    notion_events = []
    for item in get_notion_tasks():
        event = extract_event_data(item)
        if event:
            notion_events.append(event)

    created, updated, deleted = sync_events(service, calendar_id, notion_events)
    print(
        f"Synced {len(notion_events)} Notion tasks to {CALENDAR_NAME}: "
        f"{created} created, {updated} updated, {deleted} deleted."
    )


if __name__ == "__main__":
    main()
