"""REST client and pagination for the Uptimely /v1 API."""

from __future__ import annotations

import typing as t

from dateutil import parser
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context


class UptimelyPaginator(BaseAPIPaginator[str | None]):
    """Cursor paginator: pass `next_cursor` back as `after` while `has_more`."""

    def __init__(self) -> None:
        super().__init__(start_value=None)

    def get_next(self, response: requests.Response) -> str | None:
        body = response.json()
        if body.get("has_more") and body.get("next_cursor"):
            return body["next_cursor"]
        return None


class UptimelyStream(RESTStream[str | None]):
    """Base stream for the Uptimely API."""

    records_jsonpath = "$.data[*]"
    next_page_token_jsonpath = None

    @property
    def url_base(self) -> str:
        return self.config["api_url"].rstrip("/")

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        return BearerTokenAuthenticator(token=self.config["api_key"])

    @property
    def http_headers(self) -> dict:
        headers = super().http_headers
        headers["Accept"] = "application/json"
        return headers

    def get_new_paginator(self) -> UptimelyPaginator:
        return UptimelyPaginator()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"limit": self.config["page_size"]}
        if next_page_token:
            params["after"] = next_page_token
        return params

    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        """Skip records older than the bookmark.

        The API has no server-side updated_at filter, so every run still reads
        every page, but unchanged rows are not emitted again.
        """
        key = self.replication_key
        if key:
            start = self.get_starting_replication_key_value(context)
            if start and row.get(key):
                if parser.isoparse(str(row[key])) < parser.isoparse(str(start)):
                    return None
        return row
