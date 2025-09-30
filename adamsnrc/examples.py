"""
Comprehensive examples for the ADAMS API client.

This module provides extensive examples of how to use the ADAMS API client
in various scenarios, making it easier for coding agents to understand
and implement different search patterns.
"""

from datetime import datetime

from .client import ADAMSClient, create_client, get_default_client, set_default_client
from .builder import (
    nureg_search,
    part21_search,
    inspection_report_search,
    author_search,
    docket_search,
)
from .types import (
    SearchQueryBuilder,
    SearchQuery,
    SortField,
    SortOrder,
    SearchOperator,
    DocumentType,
    PropertySearch,
    DateRange,
)
from .utils import (
    build_date_range, 
    calculate_result_stats, 
    group_results_by_field,
    validate_and_format_date,
    escape_special_chars,
    normalize_whitespace,
    truncate_text,
    validate_docket_number,
    format_docket_number,
    filter_results_by_date,
    sanitize_string,
)


def basic_search_examples():
    """Demonstrate basic search functionality."""
    print("=== Basic Search Examples ===")
    
    client = ADAMSClient()
    
    # 1. Simple NUREG search
    print("\n1. Searching for NUREG documents about steam generators:")
    result = client.search_nureg("steam generator")
    print(f"Found {result.count} NUREG documents about steam generators")
    
    # 2. Part 21 correspondence search
    print("\n2. Searching for Part 21 correspondence:")
    result = client.search_part21("safety valve")
    print(f"Found {result.count} Part 21 documents about safety valves")
    
    # 3. Inspection reports search
    print("\n3. Searching for inspection reports:")
    result = client.search_inspection_reports("emergency")
    print(f"Found {result.count} inspection reports mentioning emergency")
    
    # 4. Author search
    print("\n4. Searching for documents by author:")
    result = client.search_by_author("Macfarlane")
    print(f"Found {result.count} documents by Macfarlane")
    
    # 5. Docket search
    print("\n5. Searching for documents by docket:")
    result = client.search_by_docket("05000282")
    print(f"Found {result.count} documents for docket 05000282")


def builder_pattern_examples():
    """Demonstrate the builder pattern for complex queries."""
    print("\n=== Builder Pattern Examples ===")
    
    client = ADAMSClient()
    
    # 1. Complex NUREG search with multiple filters
    print("\n1. Complex NUREG search with multiple filters:")
    builder = SearchQueryBuilder()
    builder.nureg_documents()
    builder.content_search("steam generator")
    builder.add_property_and("AuthorAffiliation", SearchOperator.CONTAINS, "NRC")
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} NUREG documents by NRC authors about steam generators")
    
    # 2. Date range search
    print("\n2. Search with date range:")
    start_date = "01/01/2023 12:00 AM"
    end_date = "12/31/2023 11:59 PM"
    
    builder = SearchQueryBuilder()
    builder.part_21_correspondence()
    builder.date_range(start_date, end_date)
    builder.sort_by(SortField.PUBLISH_DATE, SortOrder.ASCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} Part 21 documents from 2023")
    
    # 3. Advanced search with multiple conditions
    print("\n3. Advanced search with multiple conditions:")
    builder = SearchQueryBuilder()
    builder.add_property_and("DocumentType", SearchOperator.STARTS_WITH, "Letter")
    builder.add_property_and("AuthorName", SearchOperator.STARTS_WITH, "Macfarlane")
    builder.add_property_or("Subject", SearchOperator.CONTAINS, "safety")
    builder.add_property_or("Subject", SearchOperator.CONTAINS, "security")
    builder.content_search("nuclear power")
    builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} letters by Macfarlane about safety/security and nuclear power")


def type_safe_examples():
    """Demonstrate type-safe search using enums."""
    print("\n=== Type-Safe Search Examples ===")
    
    client = ADAMSClient()
    
    # 1. Using enums for document types
    print("\n1. Using enums for document types:")
    builder = SearchQueryBuilder()
    builder.add_property_and("DocumentType", SearchOperator.EQUALS, DocumentType.NUREG)
    builder.add_property_and("DocumentType", SearchOperator.EQUALS, DocumentType.SPEECH)
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} NUREG and Speech documents")
    
    # 2. Using enums for sort fields and orders
    print("\n2. Using enums for sorting:")
    builder = SearchQueryBuilder()
    builder.nureg_documents()
    builder.sort_by(SortField.SIZE, SortOrder.DESCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} NUREG documents, sorted by size (largest first)")
    
    # 3. Using enums for search operators
    print("\n3. Using enums for search operators:")
    builder = SearchQueryBuilder()
    builder.add_property_and("Title", SearchOperator.STARTS_WITH, "Safety")
    builder.add_property_and("Title", SearchOperator.ENDS_WITH, "Report")
    builder.add_property_and("Subject", SearchOperator.CONTAINS, "nuclear")
    
    query = builder.build()
    result = client.search(query)
    print(f"Found {result.count} documents with titles starting with 'Safety' and ending with 'Report'")


def batch_search_examples():
    """Demonstrate batch search functionality."""
    print("\n=== Batch Search Examples ===")
    
    client = ADAMSClient()
    
    # 1. Multiple document type searches
    print("\n1. Batch search for different document types:")
    queries = [
        SearchQueryBuilder().nureg_documents().build(),
        SearchQueryBuilder().part_21_correspondence().build(),
        SearchQueryBuilder().inspection_reports().build(),
    ]
    
    results = client.batch_search(queries)
    for i, result in enumerate(results):
        if result:
            doc_types = ["NUREG", "Part 21", "Inspection Reports"]
            print(f"{doc_types[i]}: {result.count} documents")
        else:
            print(f"Query {i+1} failed")
    
    # 2. Search across multiple authors
    print("\n2. Batch search for multiple authors:")
    authors = ["Macfarlane", "Smith", "Johnson"]
    queries = [
        SearchQueryBuilder().by_author(author).build()
        for author in authors
    ]
    
    results = client.batch_search(queries)
    for i, result in enumerate(results):
        if result:
            print(f"{authors[i]}: {result.count} documents")
        else:
            print(f"Search for {authors[i]} failed")


def result_processing_examples():
    """Demonstrate result processing and analysis."""
    print("\n=== Result Processing Examples ===")
    
    client = ADAMSClient()
    
    # 1. Basic result analysis
    print("\n1. Basic result analysis:")
    result = client.search_nureg("safety")
    
    # Calculate statistics
    stats = calculate_result_stats(result.results)
    print(f"Total results: {stats['total_results']}")
    print(f"Unique authors: {stats['unique_authors']}")
    print(f"Unique document types: {stats['unique_document_types']}")
    print(f"Average file size: {stats['average_size']:.0f} bytes")
    
    if stats['date_range']:
        print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    
    # 2. Group results by field
    print("\n2. Grouping results by author:")
    grouped = group_results_by_field(result.results, "AuthorName")
    
    # Show top 5 authors
    sorted_authors = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
    for author, docs in sorted_authors[:5]:
        print(f"{author}: {len(docs)} documents")
    
    # 3. Filter results by date
    print("\n3. Filtering results by date:")
    from datetime import datetime
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    from .utils import filter_results_by_date
    filtered = filter_results_by_date(result.results, start_date, end_date)
    print(f"Documents from 2023: {len(filtered)} out of {len(result.results)} total")


def error_handling_examples():
    """Demonstrate error handling patterns."""
    print("\n=== Error Handling Examples ===")
    
    client = ADAMSClient()
    
    # 1. Handling validation errors
    print("\n1. Handling validation errors:")
    try:
        builder = SearchQueryBuilder()
        builder.sort_by("InvalidField", "InvalidOrder")
        query = builder.build()
        result = client.search(query)
    except Exception as e:
        print(f"Caught validation error: {type(e).__name__}: {e}")
    
    # 2. Using retry mechanism
    print("\n2. Using retry mechanism:")
    try:
        builder = SearchQueryBuilder()
        builder.nureg_documents()
        query = builder.build()
        
        # Use retry mechanism
        result = client.search_with_retry(query, max_retries=3)
        print(f"Search successful after retries: {result.count} results")
    except Exception as e:
        print(f"Search failed after retries: {e}")
    
    # 3. Batch search with error handling
    print("\n3. Batch search with error handling:")
    queries = [
        SearchQueryBuilder().nureg_documents().build(),
        SearchQueryBuilder().add_property_and("InvalidField", SearchOperator.EQUALS, "value").build(),
        SearchQueryBuilder().part_21_correspondence().build(),
    ]
    
    results = client.batch_search(queries)
    for i, result in enumerate(results):
        if result:
            print(f"Query {i+1}: {result.count} results")
        else:
            print(f"Query {i+1}: Failed")


def performance_examples():
    """Demonstrate performance optimization techniques."""
    print("\n=== Performance Examples ===")
    
    # 1. Using caching
    print("\n1. Using caching:")
    client = ADAMSClient()
    
    # First search (cache miss)
    start_time = datetime.now()
    result1 = client.search_nureg("steam generator")
    first_search_time = (datetime.now() - start_time).total_seconds()
    
    # Second search (cache hit)
    start_time = datetime.now()
    result2 = client.search_nureg("steam generator")
    second_search_time = (datetime.now() - start_time).total_seconds()
    
    print(f"First search time: {first_search_time:.2f} seconds")
    print(f"Second search time: {second_search_time:.2f} seconds")
    print(f"Cache hit ratio: {result1.count == result2.count}")
    
    # 2. Client statistics
    print("\n2. Client statistics:")
    stats = client.get_statistics()
    print(f"Total searches: {stats['search_count']}")
    print(f"Errors: {stats['error_count']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Cache size: {stats['cache_size']}")
    
    # 3. Optimizing cache size
    print("\n3. Optimizing cache size:")
    client.set_cache_size(50)  # Reduce cache size
    print(f"Cache size set to 50")
    
    # Clear cache
    client.clear_cache()
    print("Cache cleared")


def advanced_query_examples():
    """Demonstrate advanced query construction."""
    print("\n=== Advanced Query Examples ===")
    
    client = ADAMSClient()
    
    # 1. Complex boolean logic
    print("\n1. Complex boolean logic:")
    builder = SearchQueryBuilder()
    
    # AND conditions
    builder.add_property_and("DocumentType", SearchOperator.EQUALS, "Letter")
    builder.add_property_and("AuthorAffiliation", SearchOperator.CONTAINS, "NRC")
    
    # OR conditions
    builder.add_property_or("Subject", SearchOperator.CONTAINS, "safety")
    builder.add_property_or("Subject", SearchOperator.CONTAINS, "security")
    builder.add_property_or("Subject", SearchOperator.CONTAINS, "emergency")
    
    # Content search
    builder.content_search("nuclear power plant")
    
    # Date range
    builder.date_range("01/01/2022 12:00 AM", "12/31/2023 11:59 PM")
    
    # Sorting
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Complex query found {result.count} documents")
    
    # 2. Folder-based search
    print("\n2. Folder-based search:")
    builder = SearchQueryBuilder()
    builder.within_folder("/NRC/Public", include_subfolders=True)
    builder.add_property_and("DocumentType", SearchOperator.ENDS_WITH, "Report")
    
    query = builder.build()
    result = client.search(query)
    print(f"Folder search found {result.count} reports in /NRC/Public")
    
    # 3. Library selection
    print("\n3. Library selection:")
    builder = SearchQueryBuilder()
    builder.public_library(True)
    builder.legacy_library(True)  # Include both libraries
    builder.add_property_and("DocumentType", SearchOperator.EQUALS, "NUREG")
    
    query = builder.build()
    result = client.search(query)
    print(f"Multi-library search found {result.count} NUREG documents")


def property_search_examples():
    """Demonstrate direct usage of PropertySearch class."""
    print("\n=== PropertySearch Examples ===")
    
    client = ADAMSClient()
    
    # 1. Creating PropertySearch objects directly
    print("\n1. Creating PropertySearch objects directly:")
    
    # Create individual property searches
    doc_type_search = PropertySearch("DocumentType", SearchOperator.ENDS_WITH, "NUREG")
    author_search = PropertySearch("AuthorName", SearchOperator.STARTS_WITH, "Macfarlane")
    subject_search = PropertySearch("Subject", SearchOperator.CONTAINS, "safety")
    
    print(f"Document type search: {doc_type_search.to_tuple()}")
    print(f"Author search: {author_search.to_tuple()}")
    print(f"Subject search: {subject_search.to_tuple()}")
    
    # 2. Using PropertySearch with SearchQuery directly
    print("\n2. Using PropertySearch with SearchQuery directly:")
    
    query = SearchQuery()
    
    # Add property searches using PropertySearch objects
    query.properties_and.append(doc_type_search)
    query.properties_or.append(author_search)
    query.properties_or.append(subject_search)
    
    query.content_search = "steam generator"
    query.options.sort_field = SortField.DOCUMENT_DATE
    query.options.sort_order = SortOrder.DESCENDING
    
    result = client.search(query)
    print(f"Found {result.count} documents using PropertySearch objects")
    
    # 3. Advanced PropertySearch combinations
    print("\n3. Advanced PropertySearch combinations:")
    
    # Create multiple property searches for complex logic
    property_searches_and = [
        PropertySearch("DocumentType", SearchOperator.EQUALS, "Letter"),
        PropertySearch("AuthorAffiliation", SearchOperator.CONTAINS, "NRC"),
        PropertySearch("DocumentDate", SearchOperator.RANGE, "01/01/2023 12:00 AM,12/31/2023 11:59 PM")
    ]
    
    property_searches_or = [
        PropertySearch("Subject", SearchOperator.CONTAINS, "safety"),
        PropertySearch("Subject", SearchOperator.CONTAINS, "security"),
        PropertySearch("Title", SearchOperator.STARTS_WITH, "Emergency")
    ]
    
    # Build query with multiple PropertySearch objects
    complex_query = SearchQuery()
    complex_query.properties_and.extend(property_searches_and)
    complex_query.properties_or.extend(property_searches_or)
    complex_query.content_search = "nuclear power plant"
    
    result = client.search(complex_query)
    print(f"Complex PropertySearch query found {result.count} documents")
    
    # 4. PropertySearch for specific document types
    print("\n4. PropertySearch for specific document types:")
    
    # Create property searches for different document types
    nureg_search = PropertySearch("DocumentType", SearchOperator.EQUALS, "NUREG")
    part21_search = PropertySearch("DocumentType", SearchOperator.EQUALS, "Part 21 Correspondence")
    inspection_search = PropertySearch("DocumentType", SearchOperator.CONTAINS, "inspection report")
    
    # Test each document type
    for search_name, prop_search in [
        ("NUREG", nureg_search),
        ("Part 21", part21_search),
        ("Inspection Reports", inspection_search)
    ]:
        test_query = SearchQuery()
        test_query.properties_and.append(prop_search)
        test_query.content_search = "emergency"
        
        result = client.search(test_query)
        print(f"{search_name}: {result.count} documents about emergency")
    
    # 5. PropertySearch with date ranges
    print("\n5. PropertySearch with date ranges:")
    
    # Create date range property searches
    recent_docs = PropertySearch("DocumentDate", SearchOperator.RANGE, "01/01/2024 12:00 AM,12/31/2024 11:59 PM")
    old_docs = PropertySearch("DocumentDate", SearchOperator.RANGE, "01/01/2020 12:00 AM,12/31/2020 11:59 PM")
    
    for period_name, date_search in [
        ("2024", recent_docs),
        ("2020", old_docs)
    ]:
        date_query = SearchQuery()
        date_query.properties_and.append(date_search)
        date_query.properties_and.append(PropertySearch("DocumentType", SearchOperator.ENDS_WITH, "NUREG"))
        
        result = client.search(date_query)
        print(f"NUREG documents from {period_name}: {result.count} documents")
    
    # 6. PropertySearch with folder-based searches
    print("\n6. PropertySearch with folder-based searches:")
    
    # Create folder-based property searches
    public_folder = PropertySearch("FilePath", SearchOperator.IN_FOLDER, "/NRC/Public")
    legacy_folder = PropertySearch("FilePath", SearchOperator.IN_FOLDER, "/NRC/Legacy")
    
    for folder_name, folder_search in [
        ("Public", public_folder),
        ("Legacy", legacy_folder)
    ]:
        folder_query = SearchQuery()
        folder_query.properties_and.append(folder_search)
        folder_query.properties_and.append(PropertySearch("DocumentType", SearchOperator.EQUALS, "Letter"))
        
        result = client.search(folder_query)
        print(f"Letters in {folder_name} folder: {result.count} documents")
    
    # 7. PropertySearch validation and error handling
    print("\n7. PropertySearch validation and error handling:")
    
    try:
        # Valid PropertySearch
        valid_search = PropertySearch("Title", SearchOperator.CONTAINS, "Safety")
        print(f"Valid PropertySearch: {valid_search.to_tuple()}")
        
        # Test with custom operator
        custom_search = PropertySearch("CustomField", "custom_op", "value")
        print(f"Custom PropertySearch: {custom_search.to_tuple()}")
        
    except Exception as e:
        print(f"PropertySearch validation error: {e}")


def daterange_examples():
    """Demonstrate usage of DateRange class."""
    print("\n=== DateRange Examples ===")
    
    client = ADAMSClient()
    
    # 1. Creating DateRange objects with string dates
    print("\n1. Creating DateRange objects with string dates:")
    
    # String dates with default format
    date_range_2023 = DateRange("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
    print(f"2023 DateRange: {date_range_2023.to_tuple()}")
    
    # String dates with custom format
    date_range_2024 = DateRange(
        "2024-01-01 00:00:00", 
        "2024-12-31 23:59:59",
        format_str="%Y-%m-%d %H:%M:%S"
    )
    print(f"2024 DateRange (custom format): {date_range_2024.to_tuple()}")
    
    # 2. Creating DateRange objects with datetime objects
    print("\n2. Creating DateRange objects with datetime objects:")
    
    from datetime import datetime, timedelta
    
    # Using datetime objects
    start_date = datetime(2023, 6, 1)
    end_date = datetime(2023, 6, 30, 23, 59, 59)
    
    june_2023_range = DateRange(start_date, end_date)
    print(f"June 2023 DateRange: {june_2023_range.to_tuple()}")
    
    # Using relative dates
    today = datetime.now()
    last_month = today - timedelta(days=30)
    
    last_month_range = DateRange(last_month, today)
    print(f"Last 30 days DateRange: {last_month_range.to_tuple()}")
    
    # 3. Using DateRange with SearchQuery
    print("\n3. Using DateRange with SearchQuery:")
    
    # Create a search query with date range
    query = SearchQuery()
    query.properties_and.append(PropertySearch("DocumentType", SearchOperator.ENDS_WITH, "NUREG"))
    query.date_range = date_range_2023
    query.content_search = "safety"
    
    result = client.search(query)
    print(f"NUREG documents about safety from 2023: {result.count} documents")
    
    # 4. Multiple date ranges for comparison
    print("\n4. Multiple date ranges for comparison:")
    
    # Create different date ranges
    date_ranges = [
        ("2020", DateRange("01/01/2020 12:00 AM", "12/31/2020 11:59 PM")),
        ("2021", DateRange("01/01/2021 12:00 AM", "12/31/2021 11:59 PM")),
        ("2022", DateRange("01/01/2022 12:00 AM", "12/31/2022 11:59 PM")),
        ("2023", DateRange("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")),
    ]
    
    for year, date_range in date_ranges:
        query = SearchQuery()
        query.properties_and.append(PropertySearch("DocumentType", SearchOperator.EQUALS, "Letter"))
        query.date_range = date_range
        
        result = client.search(query)
        print(f"Letters from {year}: {result.count} documents")
    
    # 5. DateRange with different formats
    print("\n5. DateRange with different formats:")
    
    # ISO format
    iso_range = DateRange(
        "2023-01-01T00:00:00", 
        "2023-12-31T23:59:59",
        format_str="%Y-%m-%dT%H:%M:%S"
    )
    print(f"ISO format DateRange: {iso_range.to_tuple()}")
    
    # European format
    euro_range = DateRange(
        "01/01/2023 00:00", 
        "31/12/2023 23:59",
        format_str="%d/%m/%Y %H:%M"
    )
    print(f"European format DateRange: {euro_range.to_tuple()}")
    
    # 6. DateRange for specific months
    print("\n6. DateRange for specific months:")
    
    months_2023 = [
        ("January", "01/01/2023 12:00 AM", "01/31/2023 11:59 PM"),
        ("June", "06/01/2023 12:00 AM", "06/30/2023 11:59 PM"),
        ("December", "12/01/2023 12:00 AM", "12/31/2023 11:59 PM"),
    ]
    
    for month_name, start, end in months_2023:
        month_range = DateRange(start, end)
        
        query = SearchQuery()
        query.properties_and.append(PropertySearch("DocumentType", SearchOperator.CONTAINS, "inspection"))
        query.date_range = month_range
        
        result = client.search(query)
        print(f"Inspection documents from {month_name} 2023: {result.count} documents")
    
    # 7. DateRange with time-based searches
    print("\n7. DateRange with time-based searches:")
    
    # Business hours only (9 AM to 5 PM)
    business_hours_start = datetime(2023, 1, 1, 9, 0, 0)
    business_hours_end = datetime(2023, 12, 31, 17, 0, 0)
    
    business_hours_range = DateRange(business_hours_start, business_hours_end)
    print(f"Business hours DateRange: {business_hours_range.to_tuple()}")
    
    # 8. DateRange validation and error handling
    print("\n8. DateRange validation and error handling:")
    
    try:
        # Valid DateRange
        valid_range = DateRange("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
        print(f"Valid DateRange: {valid_range.to_tuple()}")
        
        # DateRange with mixed types
        mixed_range = DateRange(
            datetime(2023, 1, 1), 
            "12/31/2023 11:59 PM"
        )
        print(f"Mixed types DateRange: {mixed_range.to_tuple()}")
        
    except Exception as e:
        print(f"DateRange validation error: {e}")
    
    # 9. DateRange for recent documents
    print("\n9. DateRange for recent documents:")
    
    # Last week
    last_week_start = datetime.now() - timedelta(weeks=1)
    last_week_range = DateRange(last_week_start, datetime.now())
    
    query = SearchQuery()
    query.properties_and.append(PropertySearch("DocumentType", SearchOperator.EQUALS, "NUREG"))
    query.date_range = last_week_range
    
    result = client.search(query)
    print(f"NUREG documents from last week: {result.count} documents")
    
    # 10. DateRange with SearchQueryBuilder
    print("\n10. DateRange with SearchQueryBuilder:")
    
    # Using DateRange with the builder pattern
    builder = SearchQueryBuilder()
    builder.part_21_correspondence()
    builder.date_range("01/01/2024 12:00 AM", "03/31/2024 11:59 PM")
    builder.content_search("safety valve")
    
    query = builder.build()
    result = client.search(query)
    print(f"Part 21 correspondence about safety valves Q1 2024: {result.count} documents")


def build_date_range_examples():
    """Demonstrate usage of build_date_range utility function."""
    print("\n=== build_date_range Examples ===")
    
    # 1. Basic build_date_range usage with string dates
    print("\n1. Basic build_date_range usage with string dates:")
    
    # Default format
    date_range = build_date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
    print(f"Default format: {date_range}")
    
    # Custom format
    iso_range = build_date_range(
        "2023-01-01 00:00:00", 
        "2023-12-31 23:59:59",
        format_str="%Y-%m-%d %H:%M:%S"
    )
    print(f"ISO format: {iso_range}")
    
    # 2. build_date_range with datetime objects
    print("\n2. build_date_range with datetime objects:")
    
    from datetime import datetime, date
    
    # Using datetime objects
    start_dt = datetime(2023, 6, 1, 9, 0, 0)
    end_dt = datetime(2023, 6, 30, 17, 0, 0)
    
    dt_range = build_date_range(start_dt, end_dt)
    print(f"Datetime objects: {dt_range}")
    
    # Using date objects (converted to datetime automatically)
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    
    date_range = build_date_range(start_date, end_date)
    print(f"Date objects: {date_range}")
    
    # 3. Mixed input types
    print("\n3. Mixed input types:")
    
    # String and datetime
    mixed_range1 = build_date_range("01/01/2023 12:00 AM", datetime(2023, 12, 31, 23, 59, 59))
    print(f"String + datetime: {mixed_range1}")
    
    # Date and string
    mixed_range2 = build_date_range(date(2023, 1, 1), "12/31/2023 11:59 PM")
    print(f"Date + string: {mixed_range2}")
    
    # 4. Different date formats
    print("\n4. Different date formats:")
    
    formats_and_examples = [
        ("%Y-%m-%d", "2023-01-01", "2023-12-31"),
        ("%d/%m/%Y", "01/01/2023", "31/12/2023"),
        ("%Y-%m-%d %H:%M:%S", "2023-01-01 00:00:00", "2023-12-31 23:59:59"),
        ("%Y-%m-%dT%H:%M:%S", "2023-01-01T00:00:00", "2023-12-31T23:59:59"),
        ("%B %d, %Y", "January 01, 2023", "December 31, 2023"),
    ]
    
    for fmt, start_str, end_str in formats_and_examples:
        try:
            formatted_range = build_date_range(start_str, end_str, format_str=fmt)
            print(f"Format {fmt}: {formatted_range}")
        except ValueError as e:
            print(f"Format {fmt}: Error - {e}")
    
    # 5. Time-specific ranges
    print("\n5. Time-specific ranges:")
    
    # Business hours
    business_start = datetime(2023, 1, 1, 9, 0, 0)
    business_end = datetime(2023, 12, 31, 17, 0, 0)
    business_range = build_date_range(business_start, business_end)
    print(f"Business hours (9 AM - 5 PM): {business_range}")
    
    # Midnight to midnight
    midnight_start = datetime(2023, 1, 1, 0, 0, 0)
    midnight_end = datetime(2023, 12, 31, 23, 59, 59)
    midnight_range = build_date_range(midnight_start, midnight_end)
    print(f"Full day range: {midnight_range}")
    
    # 6. Relative date ranges
    print("\n6. Relative date ranges:")
    
    from datetime import timedelta
    
    # Last 30 days
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    last_30_days = build_date_range(thirty_days_ago, today)
    print(f"Last 30 days: {last_30_days}")
    
    # Last week
    last_week_start = today - timedelta(weeks=1)
    last_week = build_date_range(last_week_start, today)
    print(f"Last week: {last_week}")
    
    # Current month
    month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month = build_date_range(month_start, today)
    print(f"Current month: {current_month}")
    
    # 7. Quarter ranges
    print("\n7. Quarter ranges:")
    
    quarters_2023 = [
        ("Q1", datetime(2023, 1, 1), datetime(2023, 3, 31, 23, 59, 59)),
        ("Q2", datetime(2023, 4, 1), datetime(2023, 6, 30, 23, 59, 59)),
        ("Q3", datetime(2023, 7, 1), datetime(2023, 9, 30, 23, 59, 59)),
        ("Q4", datetime(2023, 10, 1), datetime(2023, 12, 31, 23, 59, 59)),
    ]
    
    for quarter_name, start_dt, end_dt in quarters_2023:
        quarter_range = build_date_range(start_dt, end_dt)
        print(f"{quarter_name} 2023: {quarter_range}")
    
    # 8. Using build_date_range with SearchQuery
    print("\n8. Using build_date_range with SearchQuery:")
    
    # Create a date range and use it in a search
    search_start = "01/01/2023 12:00 AM"
    search_end = "12/31/2023 11:59 PM"
    search_date_range = build_date_range(search_start, search_end)
    
    # Create SearchQuery with the date range
    query = SearchQuery()
    query.properties_and.append(PropertySearch("DocumentType", SearchOperator.EQUALS, "NUREG"))
    query.date_range = DateRange(search_start, search_end)  # DateRange uses build_date_range internally
    query.content_search = "safety"
    
    print(f"Search date range: {search_date_range}")
    print("This would be used in a SearchQuery for NUREG documents about safety from 2023")
    
    # 9. Error handling with build_date_range
    print("\n9. Error handling with build_date_range:")
    
    error_examples = [
        ("Invalid date format", "2023-13-01", "2023-12-31"),  # Invalid month
        ("Wrong format string", "01/01/2023", "12/31/2023", "%Y-%m-%d"),  # Format mismatch
        ("Invalid date", "2023-02-30", "2023-12-31"),  # Feb 30th doesn't exist
    ]
    
    for description, start, end, *fmt in error_examples:
        try:
            format_str = fmt[0] if fmt else "%m/%d/%Y %I:%M %p"
            result = build_date_range(start, end, format_str=format_str)
            print(f"{description}: Success - {result}")
        except ValueError as e:
            print(f"{description}: Error - {e}")
    
    # 10. Performance comparison
    print("\n10. Performance comparison:")
    
    import time
    
    # Test with different input types
    test_cases = [
        ("String dates", "01/01/2023 12:00 AM", "12/31/2023 11:59 PM"),
        ("Datetime objects", datetime(2023, 1, 1), datetime(2023, 12, 31, 23, 59, 59)),
        ("Date objects", date(2023, 1, 1), date(2023, 12, 31)),
    ]
    
    for test_name, start, end in test_cases:
        start_time = time.time()
        for _ in range(1000):  # Run 1000 times
            build_date_range(start, end)
        end_time = time.time()
        print(f"{test_name}: {(end_time - start_time) * 1000:.2f}ms for 1000 calls")
    
    # 11. Integration with PropertySearch
    print("\n11. Integration with PropertySearch:")
    
    # Create date range for PropertySearch
    prop_start = "01/01/2024 12:00 AM"
    prop_end = "03/31/2024 11:59 PM"
    prop_range = build_date_range(prop_start, prop_end)
    
    # Use with PropertySearch
    date_property = PropertySearch("DocumentDate", SearchOperator.RANGE, prop_range)
    print(f"PropertySearch with date range: {date_property.to_tuple()}")
    
    # 12. Custom format examples
    print("\n12. Custom format examples:")
    
    custom_formats = [
        ("%m/%d/%Y", "01/01/2023", "12/31/2023"),
        ("%Y-%m-%d %H:%M", "2023-01-01 00:00", "2023-12-31 23:59"),
        ("%A, %B %d, %Y", "Sunday, January 01, 2023", "Sunday, December 31, 2023"),
        ("%Y-%j", "2023-001", "2023-365"),  # Julian day format
    ]
    
    for fmt, start_str, end_str in custom_formats:
        try:
            custom_range = build_date_range(start_str, end_str, format_str=fmt)
            print(f"Custom format {fmt}: {custom_range}")
        except ValueError as e:
            print(f"Custom format {fmt}: Error - {e}")


def utility_functions_examples():
    """Demonstrate utility functions from utils.py."""
    print("\n=== Utility Functions Examples ===")
    
    # 1. validate_and_format_date
    print("\n1. validate_and_format_date:")
    
    date_examples = [
        ("01/01/2023 12:00 AM", "%m/%d/%Y %I:%M %p"),
        ("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
        ("January 01, 2023", "%B %d, %Y"),
    ]
    
    for date_str, format_str in date_examples:
        try:
            formatted = validate_and_format_date(date_str, format_str)
            print(f"Input: '{date_str}' -> Output: '{formatted}'")
        except ValueError as e:
            print(f"Input: '{date_str}' -> Error: {e}")
    
    # 2. escape_special_chars
    print("\n2. escape_special_chars:")
    
    text_examples = [
        "Nuclear (power) plant",
        "Safety [report] analysis",
        "Emergency response & recovery",
        "Document with $special characters^",
    ]
    
    for text in text_examples:
        escaped = escape_special_chars(text)
        print(f"Original: '{text}' -> Escaped: '{escaped}'")
    
    # 3. normalize_whitespace
    print("\n3. normalize_whitespace:")
    
    whitespace_examples = [
        "  Multiple   spaces   between   words  ",
        "Tabs\t\tand\nnewlines\n\n\nhere",
        "  Leading and trailing  ",
    ]
    
    for text in whitespace_examples:
        normalized = normalize_whitespace(text)
        print(f"Original: '{repr(text)}' -> Normalized: '{normalized}'")
    
    # 4. truncate_text
    print("\n4. truncate_text:")
    
    long_text = "This is a very long text that needs to be truncated because it exceeds the maximum length limit."
    
    for max_len in [20, 50, 100]:
        truncated = truncate_text(long_text, max_len)
        print(f"Max length {max_len}: '{truncated}'")
    
    # 5. validate_docket_number
    print("\n5. validate_docket_number:")
    
    docket_examples = [
        "05000282",
        "05000300",
        "invalid",
        "05000",
        "050002821",  # Too long
    ]
    
    for docket in docket_examples:
        is_valid = validate_docket_number(docket)
        print(f"Docket '{docket}': {'Valid' if is_valid else 'Invalid'}")
    
    # 6. format_docket_number
    print("\n6. format_docket_number:")
    
    for docket in ["05000282", "05000300", "5000282"]:  # Last one missing leading zero
        formatted = format_docket_number(docket)
        print(f"Input: '{docket}' -> Formatted: '{formatted}'")
    
    # 7. sanitize_string
    print("\n7. sanitize_string:")
    
    sanitize_examples = [
        "Regular text",
        12345,  # Number
        None,   # None value
        ["list", "of", "strings"],
        {"key": "value"},
    ]
    
    for value in sanitize_examples:
        sanitized = sanitize_string(value)
        print(f"Input: {repr(value)} -> Sanitized: '{sanitized}'")


def builder_method_examples():
    """Demonstrate missing builder pattern methods."""
    print("\n=== Builder Method Examples ===")
    
    client = ADAMSClient()
    
    # 1. added_today
    print("\n1. added_today:")
    
    builder = SearchQueryBuilder()
    builder.added_today(True)
    builder.add_property_and("DocumentType", SearchOperator.EQUALS, "Letter")
    
    query = builder.build()
    result = client.search(query)
    print(f"Letters added today: {result.count} documents")
    
    # 2. added_this_month
    print("\n2. added_this_month:")
    
    builder = SearchQueryBuilder()
    builder.added_this_month(True)
    builder.add_property_and("DocumentType", SearchOperator.ENDS_WITH, "NUREG")
    
    query = builder.build()
    result = client.search(query)
    print(f"NUREG documents added this month: {result.count} documents")
    
    # 3. within_folder (comprehensive)
    print("\n3. within_folder:")
    
    folder_examples = [
        ("/NRC/Public", False, "Public folder only"),
        ("/NRC/Public", True, "Public folder with subfolders"),
        ("/NRC/Legacy", False, "Legacy folder only"),
    ]
    
    for path, include_subfolders, description in folder_examples:
        builder = SearchQueryBuilder()
        builder.within_folder(path, include_subfolders)
        builder.add_property_and("DocumentType", SearchOperator.EQUALS, "Letter")
        
        query = builder.build()
        result = client.search(query)
        print(f"{description}: {result.count} letters")
    
    # 4. by_subject
    print("\n4. by_subject:")
    
    subjects = ["safety", "security", "emergency"]
    
    for subject in subjects:
        builder = SearchQueryBuilder()
        builder.by_subject(subject)
        builder.add_property_and("DocumentType", SearchOperator.ENDS_WITH, "NUREG")
        
        query = builder.build()
        result = client.search(query)
        print(f"NUREG documents about '{subject}': {result.count} documents")
    
    # 5. by_document_type
    print("\n5. by_document_type:")
    
    doc_types = [DocumentType.LETTER, DocumentType.MEMORANDUM, DocumentType.SPEECH]
    
    for doc_type in doc_types:
        builder = SearchQueryBuilder()
        builder.by_document_type(doc_type)
        
        query = builder.build()
        result = client.search(query)
        print(f"{doc_type.value} documents: {result.count} documents")


def direct_api_wrapper_examples():
    """Demonstrate direct API wrapper methods."""
    print("\n=== Direct API Wrapper Examples ===")
    
    client = ADAMSClient()
    
    # 1. content_search (direct wrapper)
    print("\n1. content_search (direct wrapper):")
    
    result = client.content_search(
        content="steam generator",
        properties_search=[("DocumentType", "ends", "NUREG")]
    )
    print(f"Direct content_search found {result.count} NUREG documents about steam generators")
    
    # 2. advanced_search (direct wrapper)
    print("\n2. advanced_search (direct wrapper):")
    
    result = client.advanced_search(
        properties_and=[("DocumentType", "equals", "Letter")],
        properties_or=[("Subject", "contains", "safety")],
        content_search="nuclear power"
    )
    print(f"Direct advanced_search found {result.count} letters about safety and nuclear power")
    
    # 3. part21_search_content (direct wrapper)
    print("\n3. part21_search_content (direct wrapper):")
    
    result = client.part21_search_content("safety valve")
    print(f"Direct part21_search_content found {result.count} Part 21 documents about safety valves")
    
    # 4. part21_search_advanced (direct wrapper)
    print("\n4. part21_search_advanced (direct wrapper):")
    
    result = client.part21_search_advanced(
        properties_and=[("AuthorAffiliation", "contains", "NRC")],
        content_search="pressure relief"
    )
    print(f"Direct part21_search_advanced found {result.count} NRC Part 21 documents about pressure relief")
    
    # 5. operating_reactor_ir_search_content (direct wrapper)
    print("\n5. operating_reactor_ir_search_content (direct wrapper):")
    
    result = client.operating_reactor_ir_search_content("emergency")
    print(f"Direct operating_reactor_ir_search_content found {result.count} inspection reports about emergency")
    
    # 6. operating_reactor_ir_search_advanced (direct wrapper)
    print("\n6. operating_reactor_ir_search_advanced (direct wrapper):")
    
    result = client.operating_reactor_ir_search_advanced(
        properties_and=[("DocketNumber", "starts", "05000")],
        content_search="safety systems"
    )
    print(f"Direct operating_reactor_ir_search_advanced found {result.count} inspection reports about safety systems")


def client_factory_examples():
    """Demonstrate client factory functions."""
    print("\n=== Client Factory Examples ===")
    
    # 1. create_client
    print("\n1. create_client:")
    
    # Create client with custom configuration
    custom_client = create_client(
        timeout=30,
        max_retries=5,
        log_level="INFO"
    )
    
    result = custom_client.search_nureg("test")
    print(f"Custom client found {result.count} NUREG documents")
    
    # 2. get_default_client
    print("\n2. get_default_client:")
    
    default_client = get_default_client()
    result = default_client.search_part21("test")
    print(f"Default client found {result.count} Part 21 documents")
    
    # 3. set_default_client
    print("\n3. set_default_client:")
    
    # Set a new default client
    new_default = create_client(timeout=60)
    set_default_client(new_default)
    
    # Verify it's set as default
    current_default = get_default_client()
    result = current_default.search_inspection_reports("test")
    print(f"New default client found {result.count} inspection reports")


def builder_factory_examples():
    """Demonstrate builder factory functions."""
    print("\n=== Builder Factory Examples ===")
    
    client = ADAMSClient()
    
    # 1. nureg_search
    print("\n1. nureg_search:")
    
    builder = nureg_search()
    builder.content_search("safety")
    query = builder.build()
    
    result = client.search(query)
    print(f"Factory nureg_search found {result.count} NUREG documents about safety")
    
    # 2. part21_search
    print("\n2. part21_search:")
    
    builder = part21_search()
    builder.content_search("valve")
    query = builder.build()
    
    result = client.search(query)
    print(f"Factory part21_search found {result.count} Part 21 documents about valves")
    
    # 3. inspection_report_search
    print("\n3. inspection_report_search:")
    
    builder = inspection_report_search()
    builder.content_search("emergency")
    query = builder.build()
    
    result = client.search(query)
    print(f"Factory inspection_report_search found {result.count} inspection reports about emergency")
    
    # 4. author_search
    print("\n4. author_search:")
    
    builder = author_search("Macfarlane")
    query = builder.build()
    
    result = client.search(query)
    print(f"Factory author_search found {result.count} documents by Macfarlane")
    
    # 5. docket_search
    print("\n5. docket_search:")
    
    builder = docket_search("05000282")
    query = builder.build()
    
    result = client.search(query)
    print(f"Factory docket_search found {result.count} documents for docket 05000282")


def search_builder_examples():
    """Demonstrate the search_builder method."""
    print("\n=== Search Builder Examples ===")
    
    client = ADAMSClient()
    
    # 1. Basic search_builder usage
    print("\n1. Basic search_builder usage:")
    
    builder = client.search_builder()
    builder.nureg_documents()
    builder.content_search("steam generator")
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    
    query = builder.build()
    result = client.search(query)
    print(f"Search builder found {result.count} NUREG documents about steam generators")
    
    # 2. Chaining with search_builder
    print("\n2. Chaining with search_builder:")
    
    builder = client.search_builder()
    result = builder.part_21_correspondence().content_search("safety").sort_by(SortField.TITLE).build()
    
    final_result = client.search(result)
    print(f"Chained search builder found {final_result.count} Part 21 documents about safety")


def advanced_utility_examples():
    """Demonstrate advanced utility function usage."""
    print("\n=== Advanced Utility Examples ===")
    
    client = ADAMSClient()
    
    # 1. filter_results_by_date
    print("\n1. filter_results_by_date:")
    
    # Get some results first
    result = client.search_nureg("safety")
    
    # Filter by date range
    from datetime import datetime, timedelta
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    filtered = filter_results_by_date(result.results, start_date, end_date)
    print(f"Original results: {len(result.results)}, Filtered (2023): {len(filtered)}")
    
    # 2. Complex utility combinations
    print("\n2. Complex utility combinations:")
    
    # Search and process results
    search_result = client.search_part21("valve")
    
    # Calculate statistics
    stats = calculate_result_stats(search_result.results)
    print(f"Search statistics: {stats}")
    
    # Group by author
    grouped = group_results_by_field(search_result.results, "AuthorName")
    print(f"Documents grouped by {len(grouped)} unique authors")
    
    # Show top authors
    sorted_authors = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
    for author, docs in sorted_authors[:3]:
        print(f"  {author}: {len(docs)} documents")


def run_all_examples():
    """Run all example functions."""
    print("ADAMS API Client Examples")
    print("=" * 50)
    
    try:
        basic_search_examples()
        builder_pattern_examples()
        type_safe_examples()
        property_search_examples()
        daterange_examples()
        build_date_range_examples()
        utility_functions_examples()
        builder_method_examples()
        direct_api_wrapper_examples()
        client_factory_examples()
        builder_factory_examples()
        search_builder_examples()
        advanced_utility_examples()
        batch_search_examples()
        result_processing_examples()
        error_handling_examples()
        performance_examples()
        advanced_query_examples()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples() 