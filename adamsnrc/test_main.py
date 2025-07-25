"""
Tests for the ADAMS API client.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from .main import (
    ADAMSValidationError,
    ADAMSError,
    ADAMSRequestError,
    SearchResult,
    advanced_search,
    content_search,
    operating_reactor_ir_search_content,
    part21_search_content,
    validate_date_range,
    validate_property_tuple,
    validate_sort_field,
    validate_sort_order,
)
from .utils import (
    build_date_range,
    calculate_result_stats,
    escape_special_chars,
    extract_metadata_from_result,
    filter_results_by_date,
    format_docket_number,
    group_results_by_field,
    normalize_whitespace,
    sanitize_string,
    truncate_text,
    validate_and_format_date,
    validate_docket_number,
)
from .helpers import (
    search_documents_by_title,
    search_documents_by_title_exact,
    search_documents_by_title_and_type,
    search_nureg_by_title,
    search_letters_by_title,
    search_reports_by_title,
)
from .client import ADAMSClient, create_client, get_default_client
from .builder import SearchQueryBuilder, nureg_search, part21_search
from .types import (
    SortOrder,
    SortField,
    SearchOperator,
    DocumentType,
    PropertySearch,
    DateRange,
    SearchOptions,
    SearchQuery,
    DocumentMetadata,
)


class TestSearchResult(unittest.TestCase):
    """Test SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        meta = {"count": "10", "matches": "15"}
        results = [{"title": "Test Doc", "author": "Test Author"}]

        result = SearchResult(meta=meta, results=results)

        self.assertEqual(result.meta, meta)
        self.assertEqual(result.results, results)

    def test_count_property(self):
        """Test count property conversion."""
        result = SearchResult(meta={"count": "42"}, results=[])
        self.assertEqual(result.count, 42)

        # Test invalid count
        result = SearchResult(meta={"count": "invalid"}, results=[])
        self.assertEqual(result.count, 0)

    def test_matches_property(self):
        """Test matches property conversion."""
        result = SearchResult(meta={"matches": "100"}, results=[])
        self.assertEqual(result.matches, 100)

        # Test invalid matches
        result = SearchResult(meta={"matches": "invalid"}, results=[])
        self.assertEqual(result.matches, 0)


class TestTypeSystem(unittest.TestCase):
    """Test the type system components."""

    def test_sort_order_enum(self):
        """Test SortOrder enum."""
        self.assertEqual(SortOrder.ASCENDING, "ASC")
        self.assertEqual(SortOrder.DESCENDING, "DESC")

    def test_sort_field_enum(self):
        """Test SortField enum."""
        self.assertEqual(SortField.DOCUMENT_DATE, "DocumentDate")
        self.assertEqual(SortField.TITLE, "$title")
        self.assertEqual(SortField.SIZE, "$size")

    def test_search_operator_enum(self):
        """Test SearchOperator enum."""
        self.assertEqual(SearchOperator.EQUALS, "eq")
        self.assertEqual(SearchOperator.STARTS_WITH, "starts")
        self.assertEqual(SearchOperator.CONTAINS, "contains")

    def test_document_type_enum(self):
        """Test DocumentType enum."""
        self.assertEqual(DocumentType.NUREG, "NUREG")
        self.assertEqual(DocumentType.PART_21, "Part 21 Correspondence")

    def test_property_search_dataclass(self):
        """Test PropertySearch dataclass."""
        prop_search = PropertySearch("Title", SearchOperator.CONTAINS, "test")
        self.assertEqual(prop_search.property_name, "Title")
        self.assertEqual(prop_search.operator, SearchOperator.CONTAINS)
        self.assertEqual(prop_search.value, "test")
        
        # Test to_tuple method
        tuple_result = prop_search.to_tuple()
        self.assertEqual(tuple_result, ("Title", "contains", "test"))

    def test_date_range_dataclass(self):
        """Test DateRange dataclass."""
        date_range = DateRange("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
        self.assertEqual(date_range.start_date, "01/01/2023 12:00 AM")
        self.assertEqual(date_range.end_date, "12/31/2023 11:59 PM")

    def test_search_options_dataclass(self):
        """Test SearchOptions dataclass."""
        options = SearchOptions()
        self.assertTrue(options.public_library)
        self.assertFalse(options.legacy_library)
        self.assertEqual(options.sort_field, SortField.DOCUMENT_DATE)
        self.assertEqual(options.sort_order, SortOrder.DESCENDING)

    def test_search_query_dataclass(self):
        """Test SearchQuery dataclass."""
        query = SearchQuery()
        self.assertEqual(len(query.properties_and), 0)
        self.assertEqual(len(query.properties_or), 0)
        self.assertEqual(query.content_search, "")
        
        # Test add methods
        query.add_property_and("Title", SearchOperator.CONTAINS, "test")
        query.add_property_or("Author", SearchOperator.STARTS_WITH, "Smith")
        
        self.assertEqual(len(query.properties_and), 1)
        self.assertEqual(len(query.properties_or), 1)

    def test_document_metadata_dataclass(self):
        """Test DocumentMetadata dataclass."""
        data = {
            "AccessionNumber": "ML12345678901",
            "Title": "Test Document",
            "AuthorName": "Test Author",
            "DocumentDate": "01/15/2023 02:30 PM",
            "Size": "1024"
        }
        
        metadata = DocumentMetadata.from_dict(data)
        self.assertEqual(metadata.accession_number, "ML12345678901")
        self.assertEqual(metadata.title, "Test Document")
        self.assertEqual(metadata.author_name, "Test Author")


class TestSearchQueryBuilder(unittest.TestCase):
    """Test SearchQueryBuilder functionality."""

    def test_builder_creation(self):
        """Test creating a SearchQueryBuilder."""
        builder = SearchQueryBuilder()
        self.assertIsInstance(builder, SearchQueryBuilder)

    def test_builder_chaining(self):
        """Test method chaining in builder."""
        builder = SearchQueryBuilder()
        result = (builder
                 .nureg_documents()
                 .content_search("test")
                 .sort_by(SortField.TITLE, SortOrder.ASCENDING))
        
        self.assertIs(result, builder)  # Should return self for chaining

    def test_builder_nureg_documents(self):
        """Test NUREG documents filter."""
        builder = SearchQueryBuilder()
        builder.nureg_documents()
        
        query = builder.build()
        self.assertEqual(len(query.properties_and), 1)
        self.assertEqual(query.properties_and[0].property_name, "DocumentType")
        self.assertEqual(query.properties_and[0].operator, SearchOperator.ENDS_WITH)
        self.assertEqual(query.properties_and[0].value, "NUREG")

    def test_builder_content_search(self):
        """Test content search setting."""
        builder = SearchQueryBuilder()
        builder.content_search("steam generator")
        
        query = builder.build()
        self.assertEqual(query.content_search, "steam generator")

    def test_builder_date_range(self):
        """Test date range setting."""
        builder = SearchQueryBuilder()
        builder.date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
        
        query = builder.build()
        self.assertIsNotNone(query.date_range)
        self.assertEqual(query.date_range.start_date, "01/01/2023 12:00 AM")

    def test_builder_sort_options(self):
        """Test sort options setting."""
        builder = SearchQueryBuilder()
        builder.sort_by(SortField.SIZE, SortOrder.DESCENDING)
        
        query = builder.build()
        self.assertEqual(query.options.sort_field, SortField.SIZE)
        self.assertEqual(query.options.sort_order, SortOrder.DESCENDING)

    def test_builder_to_dict(self):
        """Test builder to dictionary conversion."""
        builder = SearchQueryBuilder()
        builder.nureg_documents().content_search("test")
        
        query_dict = builder.to_dict()
        self.assertIn("properties_and", query_dict)
        self.assertIn("content_search", query_dict)
        self.assertIn("options", query_dict)
        self.assertEqual(query_dict["content_search"], "test")

    def test_factory_functions(self):
        """Test factory functions for common patterns."""
        # Test nureg_search factory
        builder = nureg_search()
        query = builder.build()
        self.assertEqual(len(query.properties_and), 1)
        
        # Test part21_search factory
        builder = part21_search()
        query = builder.build()
        self.assertEqual(len(query.properties_and), 1)


class TestADAMSClient(unittest.TestCase):
    """Test ADAMSClient functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = ADAMSClient()

    def test_client_creation(self):
        """Test creating an ADAMSClient."""
        client = ADAMSClient()
        self.assertIsInstance(client, ADAMSClient)
        
        # Test with parameters
        client = ADAMSClient(timeout=120, log_level="DEBUG")
        self.assertEqual(client._timeout, 120)
        self.assertEqual(client._log_level, "DEBUG")

    def test_search_builder_method(self):
        """Test search_builder method."""
        builder = self.client.search_builder()
        self.assertIsInstance(builder, SearchQueryBuilder)

    @patch.object(ADAMSClient, 'search')
    def test_convenience_search_methods(self, mock_search):
        """Test convenience search methods."""
        mock_result = SearchResult(meta={"count": "1"}, results=[])
        mock_search.return_value = mock_result
        
        # Test search_nureg
        result = self.client.search_nureg("test")
        self.assertEqual(result, mock_result)
        mock_search.assert_called()
        
        # Test search_part21
        result = self.client.search_part21("test")
        self.assertEqual(result, mock_result)
        
        # Test search_by_author
        result = self.client.search_by_author("Smith")
        self.assertEqual(result, mock_result)

    def test_client_statistics(self):
        """Test client statistics tracking."""
        stats = self.client.get_statistics()
        self.assertIn("search_count", stats)
        self.assertIn("error_count", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("cache_size", stats)

    def test_cache_management(self):
        """Test cache management methods."""
        # Test setting cache size
        self.client.set_cache_size(50)
        self.assertEqual(self.client._cache_size, 50)
        
        # Test clearing cache
        self.client.clear_cache()
        self.assertEqual(len(self.client._cache), 0)

    def test_factory_functions(self):
        """Test client factory functions."""
        client = create_client()
        self.assertIsInstance(client, ADAMSClient)
        
        default_client = get_default_client()
        self.assertIsInstance(default_client, ADAMSClient)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_result = SearchResult(
            meta={"count": "2", "matches": "2"},
            results=[
                {
                    "Title": "Test Document 1 about steam generator",
                    "AccessionNumber": "ML12345678901",
                    "DocumentType": "NUREG"
                },
                {
                    "Title": "Test Document 2 about steam generator",
                    "AccessionNumber": "ML12345678902",
                    "DocumentType": "Letter"
                }
            ]
        )

    @patch('adamsnrc.helpers.get_default_client')
    def test_search_documents_by_title(self, mock_get_client):
        """Test search_documents_by_title function."""
        mock_client = MagicMock()
        mock_client.search_with_retry.return_value = self.mock_result
        mock_get_client.return_value = mock_client
        
        result = search_documents_by_title("steam generator")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertIn("Test Document 1 about steam generator", result)
        self.assertIn("Test Document 2 about steam generator", result)
        self.assertEqual(result["Test Document 1 about steam generator"], "ML12345678901")

    @patch('adamsnrc.helpers.get_default_client')
    def test_search_documents_by_title_exact(self, mock_get_client):
        """Test search_documents_by_title_exact function."""
        mock_client = MagicMock()
        mock_client.search_with_retry.return_value = self.mock_result
        mock_get_client.return_value = mock_client
        
        result = search_documents_by_title_exact("Test Document")
        
        self.assertIsInstance(result, dict)
        mock_client.search_with_retry.assert_called_once()

    @patch('adamsnrc.helpers.get_default_client')
    def test_search_documents_by_title_and_type(self, mock_get_client):
        """Test search_documents_by_title_and_type function."""
        mock_client = MagicMock()
        mock_client.search_with_retry.return_value = self.mock_result
        mock_get_client.return_value = mock_client
        
        result = search_documents_by_title_and_type("steam generator", "NUREG")
        
        self.assertIsInstance(result, dict)
        mock_client.search_with_retry.assert_called_once()

    @patch('adamsnrc.helpers.search_documents_by_title_and_type')
    def test_convenience_helper_functions(self, mock_search):
        """Test convenience helper functions."""
        mock_search.return_value = {"Test NUREG": "ML123"}
        
        # Test search_nureg_by_title
        result = search_nureg_by_title("test")
        mock_search.assert_called_with("test", "NUREG", None, 100)
        self.assertEqual(result, {"Test NUREG": "ML123"})
        
        # Test search_letters_by_title
        result = search_letters_by_title("test")
        mock_search.assert_called_with("test", "Letter", None, 100)
        
        # Test search_reports_by_title
        result = search_reports_by_title("test")
        mock_search.assert_called_with("test", "Report", None, 100)

    def test_helper_function_validation(self):
        """Test validation in helper functions."""
        # Test empty search string
        with self.assertRaises(ValueError):
            search_documents_by_title("")
        
        with self.assertRaises(ValueError):
            search_documents_by_title(None)
        
        # Test empty document type
        with self.assertRaises(ValueError):
            search_documents_by_title_and_type("test", "")

    @patch('adamsnrc.helpers.get_default_client')
    def test_helper_function_duplicate_titles(self, mock_get_client):
        """Test handling of duplicate titles."""
        mock_client = MagicMock()
        duplicate_result = SearchResult(
            meta={"count": "2", "matches": "2"},
            results=[
                {
                    "Title": "Same Title",
                    "AccessionNumber": "ML12345678901",
                },
                {
                    "Title": "Same Title",
                    "AccessionNumber": "ML12345678902",
                }
            ]
        )
        mock_client.search_with_retry.return_value = duplicate_result
        mock_get_client.return_value = mock_client
        
        result = search_documents_by_title("test")
        
        # Should handle duplicates by creating unique keys
        self.assertEqual(len(result), 2)
        self.assertIn("Same Title", result)
        self.assertIn("Same Title (ML12345678902)", result)

    @patch('adamsnrc.helpers.get_default_client')
    def test_helper_function_max_results(self, mock_get_client):
        """Test max_results parameter."""
        mock_client = MagicMock()
        large_result = SearchResult(
            meta={"count": "10", "matches": "10"},
            results=[
                {
                    "Title": f"Document {i}",
                    "AccessionNumber": f"ML{i:012d}",
                }
                for i in range(10)
            ]
        )
        mock_client.search_with_retry.return_value = large_result
        mock_get_client.return_value = mock_client
        
        result = search_documents_by_title("test", max_results=5)
        
        # Should limit results to max_results
        self.assertEqual(len(result), 5)


class TestValidationFunctions(unittest.TestCase):
    """Test validation functions."""

    def test_validate_sort_order_valid(self):
        """Test valid sort order validation."""
        validate_sort_order("ASC")
        validate_sort_order("DESC")

    def test_validate_sort_order_invalid(self):
        """Test invalid sort order validation."""
        with self.assertRaises(ADAMSValidationError):
            validate_sort_order("INVALID")

    def test_validate_sort_field(self):
        """Test sort field validation (should only log warning)."""
        # Should not raise exception, just log warning
        validate_sort_field("ValidField")
        validate_sort_field("InvalidField")

    def test_validate_property_tuple_valid(self):
        """Test valid property tuple validation."""
        validate_property_tuple(("DocumentType", "eq", "Test"))

    def test_validate_property_tuple_invalid(self):
        """Test invalid property tuple validation."""
        with self.assertRaises(ADAMSValidationError):
            validate_property_tuple(("DocumentType", "eq"))  # Missing value

        with self.assertRaises(ADAMSValidationError):
            validate_property_tuple(["DocumentType", "eq", "Test"])  # Not tuple

    def test_validate_date_range_valid(self):
        """Test valid date range validation."""
        validate_date_range(("01/01/2023 12:00 AM", "12/31/2023 11:59 PM"))

    def test_validate_date_range_invalid(self):
        """Test invalid date range validation."""
        with self.assertRaises(ADAMSValidationError):
            validate_date_range(("01/01/2023",))  # Missing end date

        with self.assertRaises(ADAMSValidationError):
            validate_date_range(["01/01/2023", "12/31/2023"])  # Not tuple


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_sanitize_string(self):
        """Test string sanitization."""
        self.assertEqual(sanitize_string("  test  "), "test")
        self.assertEqual(sanitize_string(None), "")
        self.assertEqual(sanitize_string(123), "123")

    def test_validate_and_format_date(self):
        """Test date validation and formatting."""
        formatted = validate_and_format_date("01/15/2023 02:30 PM")
        self.assertEqual(formatted, "01/15/2023 02:30 PM")

        with self.assertRaises(ValueError):
            validate_and_format_date("invalid date")

    def test_build_date_range(self):
        """Test date range building."""
        start, end = build_date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
        self.assertEqual(start, "01/01/2023 12:00 AM")
        self.assertEqual(end, "12/31/2023 11:59 PM")

        # Test with datetime objects
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 12, 31)
        start, end = build_date_range(start_dt, end_dt)
        self.assertEqual(start, "01/01/2023 12:00 AM")
        self.assertEqual(end, "12/31/2023 12:00 AM")

    def test_escape_special_chars(self):
        """Test special character escaping."""
        escaped = escape_special_chars("test (with) [special] {chars}")
        self.assertIn("\\(", escaped)
        self.assertIn("\\)", escaped)
        self.assertIn("\\[", escaped)
        self.assertIn("\\]", escaped)
        self.assertIn("\\{", escaped)
        self.assertIn("\\}", escaped)

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        normalized = normalize_whitespace("  multiple    spaces  ")
        self.assertEqual(normalized, "multiple spaces")

    def test_truncate_text(self):
        """Test text truncation."""
        short_text = "Short text"
        self.assertEqual(truncate_text(short_text, max_length=5), "Short...")

        long_text = "This is a very long text that should be truncated"
        truncated = truncate_text(long_text, max_length=20)
        self.assertLessEqual(len(truncated), 23)  # 20 + "..."

    def test_validate_docket_number(self):
        """Test docket number validation."""
        self.assertTrue(validate_docket_number("05000"))
        self.assertTrue(validate_docket_number("05000123"))
        self.assertFalse(validate_docket_number("invalid"))
        self.assertFalse(validate_docket_number("123"))

    def test_format_docket_number(self):
        """Test docket number formatting."""
        self.assertEqual(format_docket_number("123"), "00123")
        self.assertEqual(format_docket_number("05000"), "05000")
        self.assertEqual(format_docket_number("ABC123DEF"), "00123")


class TestSearchFunctions(unittest.TestCase):
    """Test search functions with mocked requests."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_xml_response = """
        <response>
            <count>2</count>
            <sort>DocumentDate</sort>
            <sortorder>DESC</sortorder>
            <matches>2</matches>
            <resultset>
                <r>
                    <title>Test Document 1</title>
                    <author>Test Author</author>
                    <DocumentDate>01/15/2023 02:30 PM</DocumentDate>
                </r>
                <r>
                    <title>Test Document 2</title>
                    <author>Test Author 2</author>
                    <DocumentDate>01/16/2023 03:45 PM</DocumentDate>
                </r>
            </resultset>
        </response>
        """

    @patch("adamsnrc.main._do_request")
    def test_content_search(self, mock_request):
        """Test content search function."""
        # Mock the response
        mock_result = SearchResult(
            meta={"count": "2", "matches": "2"}, results=[{"title": "Test Document"}]
        )
        mock_request.return_value = mock_result

        # Test the function
        result = content_search(
            properties_search=[("DocumentType", "eq", "Test")],
            single_content_search="test query",
        )

        self.assertEqual(result.count, 2)
        self.assertEqual(len(result.results), 1)
        mock_request.assert_called_once()

    @patch("adamsnrc.main._do_request")
    def test_advanced_search(self, mock_request):
        """Test advanced search function."""
        # Mock the response
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Advanced Test Document"}],
        )
        mock_request.return_value = mock_result

        # Test the function
        result = advanced_search(
            properties_search_all=[("AuthorName", "starts", "Test")],
            public_library=True,
        )

        self.assertEqual(result.count, 1)
        self.assertEqual(len(result.results), 1)
        mock_request.assert_called_once()

    @patch("adamsnrc.main._do_request")
    def test_part21_search_content(self, mock_request):
        """Test Part 21 content search."""
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"}, results=[{"title": "Part 21 Document"}]
        )
        mock_request.return_value = mock_result

        result = part21_search_content(text="safety")

        self.assertEqual(result.count, 1)
        mock_request.assert_called_once()

    @patch("adamsnrc.main._do_request")
    def test_operating_reactor_ir_search_content(self, mock_request):
        """Test operating reactor inspection report search."""
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Inspection Report"}],
        )
        mock_request.return_value = mock_result

        result = operating_reactor_ir_search_content(text="inspection")

        self.assertEqual(result.count, 1)
        mock_request.assert_called_once()


class TestResultProcessing(unittest.TestCase):
    """Test result processing utilities."""

    def test_extract_metadata_from_result(self):
        """Test metadata extraction from results."""
        result = {
            "DocumentDate": "01/15/2023 02:30 PM",
            "Size": "1024",
            "AuthorName": "Test Author",
            "Title": "Test Document",
        }

        metadata = extract_metadata_from_result(result)

        self.assertIsInstance(metadata["DocumentDate_parsed"], datetime)
        self.assertEqual(metadata["Size_parsed"], 1024)
        self.assertEqual(metadata["AuthorName"], "Test Author")

    def test_filter_results_by_date(self):
        """Test filtering results by date."""
        results = [
            {"DocumentDate": "01/15/2023 02:30 PM", "title": "Doc 1"},
            {"DocumentDate": "02/15/2023 02:30 PM", "title": "Doc 2"},
            {"DocumentDate": "03/15/2023 02:30 PM", "title": "Doc 3"},
        ]

        start_date = datetime(2023, 2, 1)
        end_date = datetime(2023, 2, 28)

        filtered = filter_results_by_date(results, start_date, end_date)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["title"], "Doc 2")

    def test_group_results_by_field(self):
        """Test grouping results by field."""
        results = [
            {"AuthorName": "Author 1", "title": "Doc 1"},
            {"AuthorName": "Author 1", "title": "Doc 2"},
            {"AuthorName": "Author 2", "title": "Doc 3"},
        ]

        grouped = group_results_by_field(results, "AuthorName")

        self.assertEqual(len(grouped["Author 1"]), 2)
        self.assertEqual(len(grouped["Author 2"]), 1)

    def test_calculate_result_stats(self):
        """Test calculating result statistics."""
        results = [
            {
                "AuthorName": "Author 1",
                "DocumentType": "Type A",
                "DocumentDate": "01/15/2023 02:30 PM",
                "Size": "100",
            },
            {
                "AuthorName": "Author 2",
                "DocumentType": "Type B",
                "DocumentDate": "02/15/2023 02:30 PM",
                "Size": "200",
            },
            {
                "AuthorName": "Author 1",
                "DocumentType": "Type A",
                "DocumentDate": "03/15/2023 02:30 PM",
                "Size": "300",
            },
        ]

        stats = calculate_result_stats(results)

        self.assertEqual(stats["total_results"], 3)
        self.assertEqual(stats["unique_authors"], 2)
        self.assertEqual(stats["unique_document_types"], 2)
        self.assertEqual(stats["average_size"], 200)
        self.assertIsNotNone(stats["date_range"])


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def test_invalid_sort_order_error(self):
        """Test error handling for invalid sort order."""
        with self.assertRaises(ADAMSValidationError) as context:
            validate_sort_order("INVALID")

        self.assertIn("Invalid sort order", str(context.exception))

    def test_invalid_property_tuple_error(self):
        """Test error handling for invalid property tuple."""
        with self.assertRaises(ADAMSValidationError) as context:
            validate_property_tuple(("prop", "op"))  # Missing value

        self.assertIn("Property tuple must be", str(context.exception))

    def test_invalid_date_range_error(self):
        """Test error handling for invalid date range."""
        with self.assertRaises(ADAMSValidationError) as context:
            validate_date_range(("date1",))  # Missing second date

        self.assertIn("Date range must be", str(context.exception))

    @patch('adamsnrc.helpers.get_default_client')
    def test_helper_function_error_handling(self, mock_get_client):
        """Test error handling in helper functions."""
        mock_client = MagicMock()
        mock_client.search_with_retry.side_effect = ADAMSRequestError("Network error")
        mock_get_client.return_value = mock_client
        
        with self.assertRaises(ADAMSRequestError):
            search_documents_by_title("test")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""

    @patch('adamsnrc.client.content_search')
    @patch('adamsnrc.client.advanced_search')
    def test_client_with_builder_integration(self, mock_advanced, mock_content):
        """Test integration between client and builder."""
        mock_result = SearchResult(meta={"count": "1"}, results=[])
        mock_content.return_value = mock_result
        mock_advanced.return_value = mock_result
        
        client = ADAMSClient()
        
        # Test simple query
        builder = client.search_builder()
        builder.nureg_documents().content_search("test")
        query = builder.build()
        
        result = client.search(query)
        self.assertEqual(result, mock_result)

    def test_type_system_with_builder_integration(self):
        """Test integration between type system and builder."""
        builder = SearchQueryBuilder()
        builder.add_property_and("DocumentType", SearchOperator.EQUALS, DocumentType.NUREG)
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        
        query = builder.build()
        
        # Verify the query structure
        self.assertEqual(len(query.properties_and), 1)
        self.assertEqual(query.properties_and[0].operator, SearchOperator.EQUALS)
        self.assertEqual(query.properties_and[0].value, DocumentType.NUREG)
        self.assertEqual(query.options.sort_field, SortField.TITLE)
        self.assertEqual(query.options.sort_order, SortOrder.ASCENDING)


if __name__ == "__main__":
    # Run specific test classes for debugging
    import sys
    
    if len(sys.argv) > 1:
        # Allow running specific test classes
        test_class = sys.argv[1]
        if hasattr(sys.modules[__name__], test_class):
            suite = unittest.TestLoader().loadTestsFromTestCase(
                getattr(sys.modules[__name__], test_class)
            )
            unittest.TextTestRunner(verbosity=2).run(suite)
        else:
            print(f"Test class {test_class} not found")
    else:
        # Run all tests
        unittest.main(verbosity=2)
