"""
ADAMSNRC - A robust Python client for the Nuclear Regulatory Commission's ADAMS API.

This package provides a comprehensive interface to search and retrieve documents
from the Nuclear Regulatory Commission's ADAMS (Agencywide Documents Access and
Management System) database.

The package is designed to be coding agent-friendly with:
- Comprehensive type hints and enums
- Builder pattern for query construction
- Client class for state management
- Extensive documentation and examples
"""

__version__ = "2.0.13"

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

# Import type definitions and enums
from .types import (
    # Enums
    SortOrder,
    SortField,
    SearchOperator,
    DocumentType,
    LibraryType,
    # Data classes
    PropertySearch,
    DateRange,
    SearchOptions,
    SearchQuery,
    DocumentMetadata,
    SearchStatistics,
    # Type aliases
    PropertyTuple,
    PropertyList,
    DateRangeTuple,
    SearchResultDict,
    SearchResultList,
    # Constants for coding agents
    COMMON_SEARCH_PATTERNS,
    API_FIELDS,
)

# Import builder pattern
from .builder import (
    SearchQueryBuilder,
    nureg_search,
    part21_search,
    inspection_report_search,
    author_search,
    docket_search,
)

# Import client class
from .client import (
    ADAMSClient,
    create_client,
    get_default_client,
    set_default_client,
)

# Import utility functions
from .utils import (
    # Date and time utilities
    build_date_range,
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

# Import helper functions
from .helpers import (
    search_documents_by_title,
    search_documents_by_title_exact,
    search_documents_by_title_and_type,
    search_documents_by_content,
    search_nureg_by_title,
    search_letters_by_title,
    search_reports_by_title,
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
    # Type definitions and enums
    "SortOrder",
    "SortField", 
    "SearchOperator",
    "DocumentType",
    "LibraryType",
    "PropertySearch",
    "DateRange",
    "SearchOptions",
    "SearchQuery",
    "DocumentMetadata",
    "SearchStatistics",
    "PropertyTuple",
    "PropertyList",
    "DateRangeTuple",
    "SearchResultDict",
    "SearchResultList",
    "COMMON_SEARCH_PATTERNS",
    "API_FIELDS",
    # Builder pattern
    "SearchQueryBuilder",
    "nureg_search",
    "part21_search",
    "inspection_report_search",
    "author_search",
    "docket_search",
    # Client class
    "ADAMSClient",
    "create_client",
    "get_default_client",
    "set_default_client",
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
    # Helper functions
    "search_documents_by_title",
    "search_documents_by_title_exact", 
    "search_documents_by_title_and_type",
    "search_documents_by_content",
    "search_nureg_by_title",
    "search_letters_by_title",
    "search_reports_by_title",
]

