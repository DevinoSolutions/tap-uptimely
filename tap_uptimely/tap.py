"""Uptimely tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_uptimely import streams


class TapUptimely(Tap):
    """Singer tap for Uptimely."""

    name = "tap-uptimely"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            title="API key",
            description="Uptimely public API key, from Settings, API Keys.",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://app.getuptimely.com",
            title="API URL",
            description="Base address of the Uptimely API.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            title="Start date",
            description="Earliest record to read on the first run of the incremental streams.",
        ),
        th.Property(
            "page_size",
            th.IntegerType,
            default=100,
            title="Page size",
            description="Rows per request, 1 to 100.",
        ),
        th.Property(
            "status_history_days",
            th.IntegerType,
            default=30,
            title="Status history days",
            description="Look-back window for monitor_status_history, 1 to 90 days.",
        ),
    ).to_dict()

    def discover_streams(self) -> list:
        return [
            streams.MonitorsStream(self),
            streams.MonitorStatusHistoryStream(self),
            streams.IncidentsStream(self),
            streams.AlertsStream(self),
            streams.ScheduledMaintenancesStream(self),
            streams.StatusPagesStream(self),
            streams.StatusPageResourcesStream(self),
        ]


if __name__ == "__main__":
    TapUptimely.cli()
