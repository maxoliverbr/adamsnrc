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

__version__ = "2.0.6"
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
    EXAMPLE_PATTERNS,
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
    "EXAMPLE_PATTERNS",
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
    "build_search_query",
]

# Quick start examples for coding agents
QUICK_START_EXAMPLES = {
    "basic_usage": """
# Basic usage with client
from adamsnrc import ADAMSClient

client = ADAMSClient()
result = client.search_nureg("steam generator")
print(f"Found {result.count} NUREG documents")
    """,
    
    "builder_pattern": """
# Using the builder pattern
from adamsnrc import SearchQueryBuilder, SortField, SortOrder

builder = SearchQueryBuilder()
    .nureg_documents()
    .content_search("steam generator")
    .sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)

query = builder.build()
result = client.search(query)
    """,
    
    "type_safe_search": """
# Type-safe search with enums
from adamsnrc import SearchOperator, DocumentType

builder = SearchQueryBuilder()
    .add_property_and("DocumentType", SearchOperator.EQUALS, DocumentType.NUREG)
    .add_property_and("AuthorName", SearchOperator.STARTS_WITH, "Macfarlane")

result = client.search(builder.build())
    """,
    
    "batch_search": """
# Batch search multiple queries
queries = [
    SearchQueryBuilder().nureg_documents().build(),
    SearchQueryBuilder().part_21_correspondence().build(),
    SearchQueryBuilder().inspection_reports().build(),
]

results = client.batch_search(queries)
for i, result in enumerate(results):
    print(f"Query {i+1}: {result.count} results")
    """
}

# API field reference for coding agents
API_REFERENCE = {
    "search_operators": {
        "eq": "Equals (exact match)",
        "starts": "Starts with",
        "ends": "Ends with",
        "contains": "Contains (substring match)",
        "infolder": "In folder (path-based search)",
        "range": "Range (for dates and numbers)"
    },
    "sort_fields": {
        "DocumentDate": "Sort by document creation date",
        "$title": "Sort by document title", 
        "$size": "Sort by file size",
        "AuthorName": "Sort by author name",
        "DocumentType": "Sort by document type",
        "PublishDatePARS": "Sort by publication date",
        "DocketNumber": "Sort by docket number",
        "AccessionNumber": "Sort by accession number",
        "Subject": "Sort by subject"
    },
    "document_fields": {
        "AccessionNumber": "Unique identifier for the document",
        "Title": "Document title",
        "DocumentType": "Type of document (NUREG, Letter, etc.)",
        "AuthorName": "Name of the document author",
        "AuthorAffiliation": "Author's organizational affiliation",
        "DocketNumber": "NRC docket number",
        "Subject": "Document subject",
        "DocumentDate": "Date the document was created",
        "PublishDatePARS": "Date the document was published",
        "Size": "File size in bytes",
        "FileName": "Original filename",
        "URL": "Direct link to the document"
    }
}
