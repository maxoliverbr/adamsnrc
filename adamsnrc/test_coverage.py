"""
Offline regression tests for the CLI, abstractions, helpers, client and examples.

Every test runs against a canned XML response (``requests.get`` is patched), so
nothing touches the network. The opt-in live test is in test_live.py.
"""

import io
import json
import sys
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout

from . import abstraction_examples, abstractions, cli, client as client_mod, examples
from .abstractions import QuickSearch, SearchTemplate, SimpleADAMSClient
from .client import ADAMSClient
from .helpers import (
    search_documents_by_content,
    search_documents_by_title,
    search_documents_by_title_and_type,
    search_documents_by_title_exact,
    search_letters_by_title,
    search_nureg_by_title,
    search_reports_by_title,
)
from .main import (
    ADAMSError,
    ADAMSParseError,
    ADAMSRequestError,
    ADAMSValidationError,
    _xml_to_dict,
    advanced_search,
    content_search,
    operating_reactor_ir_search_advanced,
    operating_reactor_ir_search_content,
    part21_search_advanced,
    part21_search_content,
)

XML = """<?xml version="1.0"?>
<search>
  <count>2</count><sort>$title</sort><sortorder>ASC</sortorder><matches>2</matches>
  <resultset>
    <result>
      <AccessionNumber>ML0001</AccessionNumber>
      <DocumentTitle>Steam Generator Report</DocumentTitle>
      <Title>Steam Generator Report</Title>
      <DocumentType>NUREG</DocumentType>
      <AuthorName>Macfarlane</AuthorName>
      <DocumentDate>01/15/2023 12:00 AM</DocumentDate>
      <DocketNumber>05000123</DocketNumber>
      <Size>1000</Size>
    </result>
    <result>
      <AccessionNumber>ML0002</AccessionNumber>
      <DocumentTitle>Steam Generator Report</DocumentTitle>
      <Title>Steam Generator Report</Title>
      <DocumentType>Letter</DocumentType>
      <AuthorName>Smith</AuthorName>
      <DocumentDate>06/01/2023 12:00 AM</DocumentDate>
      <DocketNumber>05000456</DocketNumber>
      <Size>3000</Size>
    </result>
  </resultset>
</search>"""

EMPTY_XML = "<search><count>0</count><matches>0</matches><resultset/></search>"


def _response(text=XML):
    r = MagicMock()
    r.text = text
    r.raise_for_status.return_value = None
    return r


@pytest.fixture(autouse=True)
def fake_api():
    """Block the network for every test in this module and reset shared state."""
    client_mod.set_default_client(ADAMSClient())
    QuickSearch._client = None  # drop any cached client from a previous test
    with patch("adamsnrc.main.requests.get", return_value=_response()) as get:
        yield get


# ---------------------------------------------------------------- main.py


class TestMainRequests:
    def test_xml_parsing(self):
        r = _xml_to_dict(XML)
        assert r.count == 2 and r.matches == 2
        assert r.results[0]["AccessionNumber"] == "ML0001"

    def test_bad_xml_raises_parse_error(self):
        with pytest.raises(ADAMSParseError):
            _xml_to_dict("<not-closed")

    def test_timeout_retries_then_raises(self, fake_api):
        fake_api.side_effect = Timeout()
        with patch("adamsnrc.main.time.sleep") as sleep, pytest.raises(ADAMSRequestError):
            content_search(single_content_search="x")
        assert fake_api.call_count > 1 and sleep.called

    def test_timeout_then_success(self, fake_api):
        fake_api.side_effect = [Timeout(), _response()]
        with patch("adamsnrc.main.time.sleep"):
            assert content_search(single_content_search="x").count == 2

    def test_connection_error_wrapped(self, fake_api):
        fake_api.side_effect = RequestsConnectionError("boom")
        with pytest.raises(ADAMSRequestError, match="boom"):
            content_search(single_content_search="x")

    def test_unexpected_error_wrapped(self, fake_api):
        fake_api.side_effect = RuntimeError("weird")
        with pytest.raises(ADAMSRequestError, match="weird"):
            content_search(single_content_search="x")

    def test_http_error_wrapped(self, fake_api):
        from requests.exceptions import HTTPError

        bad = _response()
        bad.raise_for_status.side_effect = HTTPError("500")
        fake_api.return_value = bad
        with pytest.raises(ADAMSRequestError):
            content_search(single_content_search="x")

    def test_query_reaches_api(self, fake_api):
        content_search(single_content_search="steam", sort="DocumentDate", order="DESC")
        params = fake_api.call_args.kwargs["params"]
        assert "steam" in params["q"] and params["s"] == "DocumentDate" and params["so"] == "DESC"


class TestMainSearchVariants:
    DATES = ("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")

    def test_content_with_filters(self):
        r = content_search(
            properties_search=[("DocumentType", "ends", "NUREG")],
            properties_search_any=[("AuthorName", "starts", "Mac")],
            single_content_search="x",
        )
        assert r.count == 2

    def test_advanced_with_all_options(self):
        r = advanced_search(
            properties_search_all=[("AuthorName", "starts", "Mac")],
            properties_search_any=[("DocumentType", "ends", "NUREG"), ("DocumentType", "ends", "Letter")],
            legacy_library=True,
            added_this_month=True,
            within_folder_enable=True,
            within_folder_path="/x",
        )
        assert r.matches == 2

    def test_part21_and_reactor_ir_content(self):
        assert part21_search_content(text="valve").count == 2
        assert part21_search_content(text="valve", extra_and=[("AuthorName", "starts", "S")]).count == 2
        assert operating_reactor_ir_search_content(text="x").count == 2

    def test_part21_and_reactor_ir_advanced_basic(self):
        assert part21_search_advanced().count == 2
        assert part21_search_advanced(date_range=self.DATES).count == 2
        assert part21_search_advanced(extra_all=[("AuthorName", "starts", "S")]).count == 2
        assert operating_reactor_ir_search_advanced().count == 2
        assert operating_reactor_ir_search_advanced(date_range=self.DATES).count == 2

    @pytest.mark.parametrize(
        "bad",
        [
            lambda: content_search(order="SIDEWAYS"),
            lambda: part21_search_advanced(date_range=(1, 2)),
            lambda: operating_reactor_ir_search_advanced(date_range=(1, 2)),
            lambda: part21_search_advanced(extra_all=[("only", "two")]),
            lambda: operating_reactor_ir_search_advanced(extra_all=[("only", "two")]),
        ],
    )
    def test_validation_errors(self, bad):
        with pytest.raises(ADAMSError):
            bad()

    def test_unknown_sort_field_only_warns(self, caplog):
        assert content_search(sort="Nope").count == 2
        assert "Nope" in caplog.text


# Known bugs, pinned as strict xfail: each one flips to a failure (XPASS) once
# fixed, which is the signal to delete the marker.


class TestKnownBugs:
    @pytest.mark.xfail(strict=True, reason="part21_search_advanced: extra_any strings are re-validated as tuples")
    def test_part21_extra_any_supported(self):
        part21_search_advanced(extra_any=[("DocumentType", "ends", "NUREG")])

    @pytest.mark.xfail(strict=True, reason="part21/reactor-ir advanced drop their document-type and date filters")
    @pytest.mark.parametrize(
        "fn,needle",
        [(part21_search_advanced, "Part 21"), (operating_reactor_ir_search_advanced, "Inspection")],
    )
    def test_advanced_sends_doctype_filter(self, fn, needle, fake_api):
        fn()
        assert needle in fake_api.call_args.kwargs["params"]["q"]

    @pytest.mark.xfail(strict=True, reason="advanced_search has no date_range; client.search drops it")
    def test_client_date_range_reaches_api(self, fake_api):
        c = ADAMSClient()
        c.search(c.search_builder().date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM").build())
        assert "2023" in fake_api.call_args.kwargs["params"]["q"]

    @pytest.mark.xfail(strict=True, reason="cli --type advanced passes date_range= to advanced_search, which rejects it")
    def test_cli_advanced_search_runs(self):
        code, out, _ = run_cli("search", "--type", "advanced")
        assert code == 0

    @pytest.mark.xfail(strict=True, reason="ADAMSClient.search writes the cache but never reads it")
    def test_client_cache_is_used(self, fake_api):
        c = ADAMSClient()
        q = c.search_builder().content_search("steam").build()
        c.search(q)
        n = fake_api.call_count
        c.search(q)
        assert fake_api.call_count == n


# ---------------------------------------------------------------- helpers.py


class TestHelpers:
    @pytest.mark.parametrize(
        "fn",
        [
            search_documents_by_title,
            search_documents_by_title_exact,
            search_documents_by_content,
            search_nureg_by_title,
            search_letters_by_title,
            search_reports_by_title,
        ],
    )
    def test_returns_title_to_id_map(self, fn):
        m = fn("steam generator")
        assert set(m.values()) == {"ML0001", "ML0002"}
        # duplicate titles get disambiguated, not dropped
        assert len(m) == 2

    @pytest.mark.parametrize(
        "fn",
        [
            search_documents_by_title,
            search_documents_by_title_exact,
            search_documents_by_content,
            search_nureg_by_title,
            search_letters_by_title,
            search_reports_by_title,
        ],
    )
    def test_empty_string_rejected(self, fn):
        with pytest.raises(ValueError):
            fn("   ")

    def test_by_title_and_type(self):
        assert search_documents_by_title_and_type("steam", "NUREG")

    def test_max_results_truncates(self):
        assert len(search_documents_by_content("steam", max_results=1)) == 1
        assert len(search_documents_by_title("steam", max_results=1)) == 1

    def test_no_results(self, fake_api):
        fake_api.return_value = _response(EMPTY_XML)
        assert search_documents_by_content("steam") == {}
        assert search_documents_by_title("steam") == {}

    def test_missing_accession_number_skipped(self, fake_api):
        fake_api.return_value = _response(
            "<s><count>1</count><matches>1</matches><resultset><result>"
            "<DocumentTitle>No id</DocumentTitle></result></resultset></s>"
        )
        assert search_documents_by_content("x") == {}

    def test_api_failure_propagates(self, fake_api):
        fake_api.side_effect = RequestsConnectionError("down")
        with pytest.raises(ADAMSError):
            search_documents_by_content("x")


# ---------------------------------------------------------------- client.py


class TestClient:
    def test_search_methods(self):
        c = ADAMSClient()
        for r in (
            c.search_nureg("steam"),
            c.search_part21("valve"),
            c.search_inspection_reports("fire"),
            c.search_by_author("Smith"),
            c.search_by_docket("05000123"),
            c.content_search(single_content_search="x"),
            c.advanced_search(),
            c.part21_search_content(text="x"),
            c.part21_search_advanced(),
            c.operating_reactor_ir_search_content(text="x"),
            c.operating_reactor_ir_search_advanced(),
        ):
            assert r.count == 2

    def test_statistics_and_clear_cache(self):
        c = ADAMSClient()
        c.search(c.search_builder().content_search("steam").build())
        assert c.get_statistics()
        c.clear_cache()

    def test_set_cache_size_and_batch(self):
        c = ADAMSClient()
        c.set_cache_size(5)
        qs = [c.search_builder().content_search(w).build() for w in ("a", "b")]
        assert [r.count for r in c.batch_search(qs)] == [2, 2]

    def test_search_with_retry_recovers(self, fake_api):
        c = ADAMSClient()
        q = c.search_builder().content_search("retry-me").build()
        fake_api.side_effect = [RequestsConnectionError("x"), _response()]
        with patch("time.sleep"):
            assert c.search_with_retry(q, max_retries=3).count == 2

    def test_search_with_retry_gives_up(self, fake_api):
        c = ADAMSClient()
        q = c.search_builder().content_search("fail").build()
        fake_api.side_effect = RequestsConnectionError("x")
        with patch("time.sleep"), pytest.raises(ADAMSError):
            c.search_with_retry(q, max_retries=2)

    def test_default_client_helpers(self):
        c = client_mod.create_client()
        client_mod.set_default_client(c)
        assert client_mod.get_default_client() is c


# ---------------------------------------------------------------- abstractions.py


class TestAbstractions:
    def test_simple_client_finders(self):
        c = SimpleADAMSClient()
        calls = [
            c.find_documents("steam"),
            c.find_by_type("NUREG", "x"),
            c.find_by_author("Smith"),
            c.find_by_docket("05000123"),
            c.find_recent(7),
            c.find_in_date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM"),
            c.find_nureg("x"),
            c.find_letters("x"),
            c.find_part21("x"),
            c.find_inspection_reports("x"),
            c.find_safety_documents("x"),
            c.find_security_documents("x"),
        ]
        for r in calls:
            assert r["count"] == 2 and len(r["results"]) == 2

    def test_find_documents_options(self):
        c = SimpleADAMSClient()
        assert c.find_documents("x", document_type="NUREG", author="A", docket="1", limit=1)

    def test_multi_finders_and_stats(self):
        c = SimpleADAMSClient()
        assert set(c.find_multiple_authors(["A", "B"])) == {"A", "B"}
        assert set(c.find_multiple_dockets(["1", "2"])) == {"1", "2"}
        assert set(c.find_multiple_types(["NUREG", "Letter"])) == {"NUREG", "Letter"}
        assert isinstance(c.get_document_stats("x"), dict)
        assert isinstance(c.get_author_stats("x"), dict)
        assert isinstance(c.get_type_stats("x"), dict)
        assert isinstance(c.get_client_info(), dict)
        c.clear_cache()
        c.set_cache_size(10)

    def test_quick_search(self):
        for r in (
            QuickSearch.nureg("x"),
            QuickSearch.letters("x"),
            QuickSearch.part21("x"),
            QuickSearch.inspections("x"),
            QuickSearch.author("Smith"),
            QuickSearch.docket("05000123"),
            QuickSearch.safety("x"),
            QuickSearch.recent(7),
        ):
            assert r["count"] == 2

    def test_templates(self):
        t = SearchTemplate()
        for r in (
            t.regulatory_letters("x", "Smith", 30),
            t.safety_reports("x", "05000123"),
            t.emergency_documents(7),
            t.nrc_communications("x"),
            t.plant_specific("05000123", "x"),
        ):
            assert r["count"] == 2

    def test_convenience_functions(self):
        assert abstractions.quick_search("x")["count"] == 2
        assert abstractions.quick_search("x", "NUREG")["count"] == 2
        assert abstractions.find_nureg("x")["count"] == 2
        assert abstractions.find_letters("x")["count"] == 2
        assert abstractions.find_safety_docs()["count"] == 2
        assert abstractions.find_recent_docs(7)["count"] == 2
        assert isinstance(abstractions.get_author_stats("Smith"), dict)


# ---------------------------------------------------------------- cli.py

ROWS = [{"Title": "a|b", "Author": "X"}, {"Title": "c", "Size": "5"}]


class TestCliFormat:
    def test_json(self):
        assert json.loads(cli.format_output(ROWS, "json")) == ROWS

    def test_csv(self):
        out = cli.format_output(ROWS, "csv").splitlines()
        assert out[0] == '"Author","Size","Title"' and len(out) == 3

    def test_table_escapes_pipes(self):
        assert "a\\|b" in cli.format_output(ROWS, "table")

    def test_empty(self):
        assert cli.format_output([], "csv") == ""
        assert cli.format_output([], "table") == "No results found."


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with patch.object(sys, "argv", ["adamsnrc", *argv]), redirect_stdout(out), patch("sys.stderr", err):
        code = cli.main()
    return code, out.getvalue(), err.getvalue()


class TestCliMain:
    def test_no_command_prints_help(self):
        code, out, _ = run_cli()
        assert code is None and "usage" in out.lower()

    @pytest.mark.parametrize(
        "kind",
        ["content", "part21", "part21-advanced", "reactor-ir", "reactor-ir-advanced"],
    )
    def test_every_search_type(self, kind):
        code, out, _ = run_cli("search", "--type", kind, "--text", "steam")
        assert code == 0 and "Found 2 documents" in out

    @pytest.mark.parametrize("fmt", ["table", "json", "csv"])
    def test_output_formats(self, fmt):
        code, out, _ = run_cli("search", "--output", fmt)
        assert code == 0 and "ML0001" in out

    def test_filters_dates_limit_and_stats(self):
        code, out, err = run_cli(
            "search", "--type", "part21-advanced", "--doc-type", "NUREG", "--author", "Mac",
            "--date-start", "01/01/2023 12:00 AM", "--date-end", "12/31/2023 11:59 PM",
            "--limit", "1", "--stats",
        )
        assert code == 0, err
        assert "Found 1 documents" in out and "Search Statistics" in out

    def test_no_results(self, fake_api):
        fake_api.return_value = _response(EMPTY_XML)
        code, out, _ = run_cli("search")
        assert code == 0 and "No documents found" in out

    def test_api_error_returns_1(self, fake_api):
        fake_api.side_effect = RequestsConnectionError("down")
        code, _, err = run_cli("search")
        assert code == 1 and "ADAMS API error" in err

    def test_validation_error_returns_1(self):
        code, _, err = run_cli("search", "--date-start", "garbage", "--date-end", "garbage")
        assert code == 1 and "Unexpected error" in err or "Validation error" in err

    def test_unexpected_error_returns_1(self):
        with patch("adamsnrc.cli.content_search", side_effect=RuntimeError("oops")):
            code, _, err = run_cli("search")
        assert code == 1 and "oops" in err

    def test_keyboard_interrupt_returns_1(self):
        with patch("adamsnrc.cli.content_search", side_effect=KeyboardInterrupt):
            code, _, err = run_cli("search")
        assert code == 1 and "interrupted" in err


# ---------------------------------------------------------------- examples


def _run(fn):
    buf = io.StringIO()
    with redirect_stdout(buf), patch("adamsnrc.main.time.sleep"), patch("time.sleep"):
        fn()
    return buf.getvalue()


@pytest.mark.parametrize(
    "mod,names",
    [
        (examples, [n for n in dir(examples) if n.endswith("_examples")] + ["run_all_examples"]),
        (
            abstraction_examples,
            [n for n in dir(abstraction_examples) if n.endswith("_examples")]
            + ["run_all_abstraction_examples"],
        ),
    ],
    ids=["examples", "abstraction_examples"],
)
def test_example_functions_run_offline(mod, names):
    """Examples are documentation: they must keep running against the current API."""
    assert names
    for name in names:
        _run(getattr(mod, name))
