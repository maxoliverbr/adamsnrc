"""
ADAMSNRC - A robust Python client for the Nuclear Regulatory Commission's ADAMS API.

This package provides a comprehensive interface to search and retrieve documents
from the Nuclear Regulatory Commission's ADAMS (Agencywide Documents Access and
Management System) database.
"""

__version__ = "2.0.3"
__author__ = "ADAMSNRC Contributors"
__email__ = "your.email@example.com"

# Import main API functions
from .main import (
    # Exception classes
    ADAMSError,
    ADAMSParseError,
    ADAMSRequestError,
    ADAMSValidationError,
    # Data structures
    SearchResult,
    advanced_search,
    # Core search functions
    content_search,
    operating_reactor_ir_search_advanced,
    operating_reactor_ir_search_content,
    part21_search_advanced,
    # Specialized search functions
    part21_search_content,
)

# Import utility functions
from .utils import (
    # Date and time utilities
    build_date_range,
    build_search_query,
    calculate_result_stats,
    escape_special_chars,
    # Result processing
    extract_metadata_from_result,
    filter_results_by_date,
    format_docket_number,
    group_results_by_field,
    normalize_whitespace,
    # Text processing
    sanitize_string,
    truncate_text,
    validate_and_format_date,
    # Document utilities
    validate_docket_number,
)

# Define what gets imported with "from adamsnrc import *"
__all__ = [
    # Core API
    "content_search",
    "advanced_search",
    "part21_search_content",
    "part21_search_advanced",
    "operating_reactor_ir_search_content",
    "operating_reactor_ir_search_advanced",
    # Data structures
    "SearchResult",
    # Exceptions
    "ADAMSError",
    "ADAMSRequestError",
    "ADAMSValidationError",
    "ADAMSParseError",
    # Utilities
    "build_date_range",
    "validate_and_format_date",
    "sanitize_string",
    "escape_special_chars",
    "normalize_whitespace",
    "truncate_text",
    "validate_docket_number",
    "format_docket_number",
    "extract_metadata_from_result",
    "filter_results_by_date",
    "group_results_by_field",
    "calculate_result_stats",
    "build_search_query",
]
