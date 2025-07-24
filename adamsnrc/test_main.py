"""
Tests for the ADAMS API client.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import xml.etree.ElementTree as ET

from .main import (
    SearchResult, ADAMSError, ADAMSRequestError, ADAMSValidationError, ADAMSParseError,
    content_search, advanced_search, part21_search_content, part21_search_advanced,
    operating_reactor_ir_search_content, operating_reactor_ir_search_advanced,
    validate_sort_order, validate_sort_field, validate_property_tuple, validate_date_range
)
from .utils import (
    sanitize_string, validate_and_format_date, build_date_range, escape_special_chars,
    normalize_whitespace, truncate_text, validate_docket_number, format_docket_number,
    build_search_query, extract_metadata_from_result, filter_results_by_date,
    group_results_by_field, calculate_result_stats
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
                <result>
                    <title>Test Document 1</title>
                    <author>Test Author</author>
                    <DocumentDate>01/15/2023 02:30 PM</DocumentDate>
                </result>
                <result>
                    <title>Test Document 2</title>
                    <author>Test Author 2</author>
                    <DocumentDate>01/16/2023 03:45 PM</DocumentDate>
                </result>
            </resultset>
        </response>
        """
    
    @patch('adamsnrc.main._do_request')
    def test_content_search(self, mock_request):
        """Test content search function."""
        # Mock the response
        mock_result = SearchResult(
            meta={"count": "2", "matches": "2"},
            results=[{"title": "Test Document"}]
        )
        mock_request.return_value = mock_result
        
        # Test the function
        result = content_search(
            properties_search=[("DocumentType", "eq", "Test")],
            single_content_search="test query"
        )
        
        self.assertEqual(result.count, 2)
        self.assertEqual(len(result.results), 1)
        mock_request.assert_called_once()
    
    @patch('adamsnrc.main._do_request')
    def test_advanced_search(self, mock_request):
        """Test advanced search function."""
        # Mock the response
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Advanced Test Document"}]
        )
        mock_request.return_value = mock_result
        
        # Test the function
        result = advanced_search(
            properties_search_all=[("AuthorName", "starts", "Test")],
            public_library=True
        )
        
        self.assertEqual(result.count, 1)
        self.assertEqual(len(result.results), 1)
        mock_request.assert_called_once()
    
    @patch('adamsnrc.main._do_request')
    def test_part21_search_content(self, mock_request):
        """Test Part 21 content search."""
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Part 21 Document"}]
        )
        mock_request.return_value = mock_result
        
        result = part21_search_content(text="safety")
        
        self.assertEqual(result.count, 1)
        mock_request.assert_called_once()
    
    @patch('adamsnrc.main._do_request')
    def test_operating_reactor_ir_search_content(self, mock_request):
        """Test operating reactor inspection report search."""
        mock_result = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Inspection Report"}]
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
            "Title": "Test Document"
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
            {"DocumentDate": "03/15/2023 02:30 PM", "title": "Doc 3"}
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
            {"AuthorName": "Author 2", "title": "Doc 3"}
        ]
        
        grouped = group_results_by_field(results, "AuthorName")
        
        self.assertEqual(len(grouped["Author 1"]), 2)
        self.assertEqual(len(grouped["Author 2"]), 1)
    
    def test_calculate_result_stats(self):
        """Test calculating result statistics."""
        results = [
            {"AuthorName": "Author 1", "DocumentType": "Type A", "DocumentDate": "01/15/2023 02:30 PM", "Size": "100"},
            {"AuthorName": "Author 2", "DocumentType": "Type B", "DocumentDate": "02/15/2023 02:30 PM", "Size": "200"},
            {"AuthorName": "Author 1", "DocumentType": "Type A", "DocumentDate": "03/15/2023 02:30 PM", "Size": "300"}
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

if __name__ == '__main__':
    unittest.main() 