"""
Opt-in test against the real NRC ADAMS API (skipped by default, flaky by nature).

    ADAMS_LIVE=1 uv run pytest -m integration
"""

import os

import pytest

from .main import content_search


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("ADAMS_LIVE") != "1", reason="set ADAMS_LIVE=1 to hit the real ADAMS API")
def test_live_adams_api():
    r = content_search(
        properties_search=[("DocumentType", "ends", "NUREG")],
        single_content_search="steam generator",
    )
    assert r.count >= 0 and isinstance(r.results, list)
    if r.results:
        assert "AccessionNumber" in r.results[0]
