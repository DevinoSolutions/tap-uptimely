"""Tests that need no network or API key."""

from unittest.mock import Mock

from tap_uptimely.client import UptimelyPaginator
from tap_uptimely.tap import TapUptimely

EXPECTED_STREAMS = {
    "monitors",
    "monitor_status_history",
    "incidents",
    "alerts",
    "scheduled_maintenances",
    "status_pages",
    "status_page_resources",
}


def _tap() -> TapUptimely:
    return TapUptimely(config={"api_key": "test"}, parse_env_config=False)


def test_discovers_all_streams():
    catalog = _tap().catalog_dict
    assert {s["tap_stream_id"] for s in catalog["streams"]} == EXPECTED_STREAMS


def test_incremental_streams():
    streams = _tap().streams
    assert streams["incidents"].replication_key == "updated_at"
    assert streams["alerts"].replication_key == "updated_at"
    assert streams["monitors"].replication_key is None


def test_paginator_follows_cursor():
    paginator = UptimelyPaginator()
    page = Mock()
    page.json.return_value = {"has_more": True, "next_cursor": "abc"}
    assert paginator.get_next(page) == "abc"
    page.json.return_value = {"has_more": False, "next_cursor": None}
    assert paginator.get_next(page) is None
