"""
Comprehensive examples for the ADAMS API client.

This module provides extensive examples of how to use the ADAMS API client
in various scenarios, making it easier for coding agents to understand
and implement different search patterns.
"""

from datetime import datetime

from .client import ADAMSClient
from .types import (
    SearchQueryBuilder,
    SortField,
    SortOrder,
    SearchOperator,
    DocumentType,
    PropertySearch,
    DateRange,
)
from .utils import build_date_range, calculate_result_stats, group_results_by_field


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


def run_all_examples():
    """Run all example functions."""
    print("ADAMS API Client Examples")
    print("=" * 50)
    
    try:
        basic_search_examples()
        builder_pattern_examples()
        type_safe_examples()
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