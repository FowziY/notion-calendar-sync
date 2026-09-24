import unittest

from notion_sync.notion import extract_event_data


class ExtractEventDataTests(unittest.TestCase):
    def make_notion_item(self, status_key="status", status_name="In progress"):
        return {
            "id": "notion-page-1",
            "url": "https://notion.so/notion-page-1",
            "properties": {
                "Name": {"title": [{"plain_text": "Write report"}]},
                "Due Date": {"date": {"start": "2026-07-14", "end": None}},
                "Status": {status_key: {"name": status_name}},
            },
        }

    def test_extracts_status_property_and_notion_identity(self):
        event = extract_event_data(self.make_notion_item())

        self.assertEqual(event["notion_page_id"], "notion-page-1")
        self.assertEqual(event["title"], "Write report")
        self.assertEqual(event["start"], "2026-07-14")
        self.assertEqual(event["status"], "In progress")
        self.assertEqual(event["url"], "https://notion.so/notion-page-1")

    def test_supports_legacy_select_property(self):
        event = extract_event_data(self.make_notion_item("select", "Planned"))
        self.assertEqual(event["status"], "Planned")

    def test_skips_done_items(self):
        self.assertIsNone(extract_event_data(self.make_notion_item(status_name="Done")))

    def test_skips_other_completed_statuses(self):
        self.assertIsNone(
            extract_event_data(self.make_notion_item(status_name="Archived"))
        )

    def test_skips_items_without_due_date(self):
        item = self.make_notion_item()
        item["properties"]["Due Date"]["date"] = None
        self.assertIsNone(extract_event_data(item))


if __name__ == "__main__":
    unittest.main()
