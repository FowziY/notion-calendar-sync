import unittest
from unittest.mock import MagicMock, patch

from notion_sync.google_calendar_sync import build_google_event, sync_events


class GoogleCalendarSyncTests(unittest.TestCase):
    def make_notion_event(self, page_id="page-1", start="2026-07-14", end=None):
        return {
            "notion_page_id": page_id,
            "title": "Write report",
            "start": start,
            "end": end,
            "status": "In progress",
            "url": f"https://notion.so/{page_id}",
        }

    def test_builds_exclusive_end_for_all_day_event(self):
        body = build_google_event(self.make_notion_event())
        self.assertEqual(body["start"], {"date": "2026-07-14"})
        self.assertEqual(body["end"], {"date": "2026-07-15"})
        self.assertEqual(
            body["extendedProperties"]["private"]["notionPageId"], "page-1"
        )

    def test_defaults_timed_event_to_one_hour(self):
        body = build_google_event(
            self.make_notion_event(start="2026-07-14T09:30:00+01:00")
        )
        self.assertEqual(body["end"]["dateTime"], "2026-07-14T10:30:00+01:00")

    def test_converts_inclusive_notion_date_range_to_exclusive_google_end(self):
        body = build_google_event(
            self.make_notion_event(start="2026-07-14", end="2026-07-16")
        )
        self.assertEqual(body["end"], {"date": "2026-07-17"})

    @patch("notion_sync.google_calendar_sync.list_synced_events")
    def test_creates_updates_and_deletes_only_synced_events(self, list_events):
        list_events.return_value = {
            "page-1": {"id": "google-1"},
            "removed-page": {"id": "google-removed"},
        }
        service = MagicMock()

        counts = sync_events(
            service,
            "calendar-id",
            [self.make_notion_event("page-1"), self.make_notion_event("page-2")],
        )

        self.assertEqual(counts, (1, 1, 1))
        service.events.return_value.update.assert_called_once()
        service.events.return_value.insert.assert_called_once()
        service.events.return_value.delete.assert_called_once_with(
            calendarId="calendar-id", eventId="google-removed"
        )

    @patch("notion_sync.google_calendar_sync.list_synced_events")
    def test_empty_notion_result_does_not_delete_existing_events(self, list_events):
        list_events.return_value = {"old-page": {"id": "google-old"}}
        service = MagicMock()

        with self.assertRaises(RuntimeError) as context:
            sync_events(service, "calendar-id", [])

        self.assertIn(
            "Refusing to delete all synced events",
            str(context.exception),
        )
        service.events.return_value.delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
