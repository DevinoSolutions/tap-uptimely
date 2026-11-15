"""Standard Singer SDK tap tests, run against the live API.

They need a real key in TAP_UPTIMELY_API_KEY and use a few requests of the monthly
quota. Without a key they are skipped; tests/test_offline.py always runs.
"""

import os

import pytest
from singer_sdk.testing import get_tap_test_class

from tap_uptimely.tap import TapUptimely

API_KEY = os.environ.get("TAP_UPTIMELY_API_KEY", "")

SAMPLE_CONFIG = {
    "api_key": API_KEY,
    "page_size": 25,
}

TestTapUptimely = get_tap_test_class(
    tap_class=TapUptimely,
    config=SAMPLE_CONFIG,
)

if not API_KEY:
    TestTapUptimely = pytest.mark.skip(reason="TAP_UPTIMELY_API_KEY is not set")(
        TestTapUptimely
    )
