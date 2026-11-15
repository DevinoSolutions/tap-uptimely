"""Stream definitions for the Uptimely tap."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th
from singer_sdk.pagination import SinglePagePaginator

from tap_uptimely.client import UptimelyStream

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

_NAMED_COLOR = th.ObjectType(
    th.Property("name", th.StringType, description="Name shown in the dashboard."),
    th.Property("color", th.StringType, description="Hex color, when configured."),
)

_MONITOR_REF = th.ObjectType(
    th.Property("id", th.StringType),
    th.Property("name", th.StringType),
)


class MonitorsStream(UptimelyStream):
    """Monitors in the project."""

    name = "monitors"
    path = "/v1/monitors"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Monitor id."),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property(
            "monitor_type", th.StringType, description="Website, API, Ping, Port, DNS, ..."
        ),
        th.Property("status", _NAMED_COLOR, description="Current status, e.g. Operational."),
        th.Property("active_monitoring_disabled", th.BooleanType),
        th.Property("failure_threshold", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Context | None) -> dict:
        return {"monitor_id": record["id"]}


class MonitorStatusHistoryStream(UptimelyStream):
    """Status segments (up, down, ...) of each monitor over the look-back window."""

    name = "monitor_status_history"
    path = "/v1/monitors/{monitor_id}/status-history"
    parent_stream_type = MonitorsStream
    primary_keys: t.ClassVar[list[str]] = ["monitor_id", "starts_at"]
    replication_key = None
    ignore_parent_replication_key = True

    schema = th.PropertiesList(
        th.Property("monitor_id", th.StringType),
        th.Property("status", _NAMED_COLOR),
        th.Property("starts_at", th.DateTimeType),
        th.Property("ends_at", th.DateTimeType, description="Null while the status is current."),
        th.Property("root_cause", th.StringType),
    ).to_dict()

    def get_url_params(self, context, next_page_token):  # noqa: ANN001, ANN201
        # One page of segments per monitor: this endpoint takes days and limit, not a cursor.
        return {"days": self.config["status_history_days"], "limit": 200}

    def get_new_paginator(self) -> SinglePagePaginator:  # type: ignore[override]
        return SinglePagePaginator()

    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["monitor_id"] = (context or {})["monitor_id"]
        return row


class IncidentsStream(UptimelyStream):
    """Incidents."""

    name = "incidents"
    path = "/v1/incidents"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("number", th.NumberType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property(
            "state",
            th.ObjectType(
                th.Property("name", th.StringType),
                th.Property("color", th.StringType),
                th.Property("is_resolved", th.BooleanType),
            ),
        ),
        th.Property("severity", _NAMED_COLOR),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class AlertsStream(UptimelyStream):
    """Alerts raised by monitors."""

    name = "alerts"
    path = "/v1/alerts"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("number", th.NumberType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("state", _NAMED_COLOR),
        th.Property("severity", _NAMED_COLOR),
        th.Property("monitor", _MONITOR_REF),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class ScheduledMaintenancesStream(UptimelyStream):
    """Scheduled maintenance windows. The API has no updated_at, so full table."""

    name = "scheduled_maintenances"
    path = "/v1/scheduled-maintenances"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("state", _NAMED_COLOR),
        th.Property("starts_at", th.DateTimeType),
        th.Property("ends_at", th.DateTimeType),
        th.Property("created_at", th.DateTimeType),
    ).to_dict()


class StatusPagesStream(UptimelyStream):
    """Status pages."""

    name = "status_pages"
    path = "/v1/status-pages"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("slug", th.StringType),
        th.Property("is_public", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Context | None) -> dict:
        return {"status_page_id": record["id"]}


class StatusPageResourcesStream(UptimelyStream):
    """Monitors shown on each status page."""

    name = "status_page_resources"
    path = "/v1/status-pages/{status_page_id}/resources"
    parent_stream_type = StatusPagesStream
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    ignore_parent_replication_key = True

    schema = th.PropertiesList(
        th.Property("id", th.StringType),
        th.Property("status_page_id", th.StringType),
        th.Property("monitor", _MONITOR_REF),
        th.Property("display_name", th.StringType),
        th.Property("display_description", th.StringType),
        th.Property("show_uptime_percent", th.BooleanType),
        th.Property("order", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
    ).to_dict()

    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["status_page_id"] = (context or {})["status_page_id"]
        return row
