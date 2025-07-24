# ADAMS API Client - Coding Agent Guide

This guide is specifically designed for coding agents to quickly understand and effectively use the ADAMS API client package.

## Quick Start

### 1. Basic Import and Setup

```python
from adamsnrc import ADAMSClient, SearchQueryBuilder, SortField, SortOrder

# Create a client instance
client = ADAMSClient()

# Or use the default client
from adamsnrc import get_default_client
client = get_default_client()
```

### 2. Simple Searches

```python
# Search for NUREG documents
result = client.search_nureg("steam generator")
print(f"Found {result.count} NUREG documents")

# Search for Part 21 correspondence
result = client.search_part21("safety valve")
print(f"Found {result.count} Part 21 documents")

# Search for inspection reports
result = client.search_inspection_reports("emergency")
print(f"Found {result.count} inspection reports")

# Search by author
result = client.search_by_author("Macfarlane")
print(f"Found {result.count} documents by Macfarlane")

# Search by docket
result = client.search_by_docket("05000282")
print(f"Found {result.count} documents for docket 05000282")
```

### 3. Using the Builder Pattern

```python
# Build complex queries step by step
builder = SearchQueryBuilder()
builder.nureg_documents()
builder.content_search("steam generator")
builder.add_property_and("AuthorAffiliation", "contains", "NRC")
builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)

query = builder.build()
result = client.search(query)
```

### 4. Type-Safe Search with Enums

```python
from adamsnrc import SearchOperator, DocumentType

# Use enums for type safety
builder = SearchQueryBuilder()
builder.add_property_and("DocumentType", SearchOperator.EQUALS, DocumentType.NUREG)
builder.add_property_and("AuthorName", SearchOperator.STARTS_WITH, "Macfarlane")
builder.sort_by(SortField.SIZE, SortOrder.DESCENDING)

result = client.search(builder.build())
```

## Common Patterns

### 1. Date Range Searches

```python
# Search with date range
builder = SearchQueryBuilder()
builder.part_21_correspondence()
builder.date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")
builder.sort_by(SortField.PUBLISH_DATE, SortOrder.ASCENDING)

result = client.search(builder.build())
```

### 2. Complex Boolean Logic

```python
# AND conditions
builder.add_property_and("DocumentType", SearchOperator.EQUALS, "Letter")
builder.add_property_and("AuthorAffiliation", SearchOperator.CONTAINS, "NRC")

# OR conditions
builder.add_property_or("Subject", SearchOperator.CONTAINS, "safety")
builder.add_property_or("Subject", SearchOperator.CONTAINS, "security")

# Content search
builder.content_search("nuclear power")
```

### 3. Batch Searches

```python
# Execute multiple searches
queries = [
    SearchQueryBuilder().nureg_documents().build(),
    SearchQueryBuilder().part_21_correspondence().build(),
    SearchQueryBuilder().inspection_reports().build(),
]

results = client.batch_search(queries)
for i, result in enumerate(results):
    if result:
        print(f"Query {i+1}: {result.count} results")
```

## Result Processing

### 1. Basic Result Analysis

```python
from adamsnrc.utils import calculate_result_stats, group_results_by_field

result = client.search_nureg("safety")

# Calculate statistics
stats = calculate_result_stats(result.results)
print(f"Total: {stats['total_results']}")
print(f"Unique authors: {stats['unique_authors']}")
print(f"Average size: {stats['average_size']:.0f} bytes")

# Group by author
grouped = group_results_by_field(result.results, "AuthorName")
for author, docs in grouped.items():
    print(f"{author}: {len(docs)} documents")
```

### 2. Accessing Document Metadata

```python
# Access structured document data
for doc in result.documents:
    print(f"Title: {doc.title}")
    print(f"Author: {doc.author_name}")
    print(f"Date: {doc.document_date}")
    print(f"Size: {doc.size} bytes")
    print(f"URL: {doc.url}")
    print("---")
```

### 3. Filtering Results

```python
from adamsnrc.utils import filter_results_by_date
from datetime import datetime

# Filter by date
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
filtered = filter_results_by_date(result.results, start_date, end_date)
print(f"Documents from 2023: {len(filtered)}")
```

## Error Handling

### 1. Basic Error Handling

```python
from adamsnrc import ADAMSError, ADAMSValidationError, ADAMSRequestError

try:
    result = client.search_nureg("steam generator")
    print(f"Found {result.count} documents")
except ADAMSValidationError as e:
    print(f"Validation error: {e}")
except ADAMSRequestError as e:
    print(f"Request error: {e}")
except ADAMSError as e:
    print(f"ADAMS error: {e}")
```

### 2. Retry Mechanism

```python
# Use retry mechanism for network issues
builder = SearchQueryBuilder()
builder.nureg_documents()
query = builder.build()

try:
    result = client.search_with_retry(query, max_retries=3)
    print(f"Search successful: {result.count} results")
except ADAMSError as e:
    print(f"Search failed after retries: {e}")
```

### 3. Batch Search Error Handling

```python
# Handle errors in batch searches
results = client.batch_search(queries)
for i, result in enumerate(results):
    if result:
        print(f"Query {i+1}: {result.count} results")
    else:
        print(f"Query {i+1}: Failed")
```

## Performance Optimization

### 1. Caching

```python
# The client automatically caches results
client = ADAMSClient()

# First search (cache miss)
result1 = client.search_nureg("steam generator")

# Second search (cache hit - faster)
result2 = client.search_nureg("steam generator")

# Clear cache if needed
client.clear_cache()

# Adjust cache size
client.set_cache_size(200)
```

### 2. Client Statistics

```python
# Monitor client performance
stats = client.get_statistics()
print(f"Total searches: {stats['search_count']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Cache size: {stats['cache_size']}")
```

## API Reference for Coding Agents

### Search Operators

```python
SearchOperator.EQUALS      # Exact match
SearchOperator.STARTS_WITH # Starts with
SearchOperator.ENDS_WITH   # Ends with
SearchOperator.CONTAINS    # Contains (substring)
SearchOperator.IN_FOLDER   # In folder (path-based)
SearchOperator.RANGE       # Range (for dates/numbers)
```

### Sort Fields

```python
SortField.DOCUMENT_DATE    # Document creation date
SortField.TITLE           # Document title
SortField.SIZE            # File size
SortField.AUTHOR_NAME     # Author name
SortField.DOCUMENT_TYPE   # Document type
SortField.PUBLISH_DATE    # Publication date
SortField.DOCKET_NUMBER   # Docket number
SortField.ACCESSION_NUMBER # Accession number
SortField.SUBJECT         # Subject
```

### Sort Orders

```python
SortOrder.ASCENDING  # Ascending order
SortOrder.DESCENDING # Descending order
```

### Document Types

```python
DocumentType.NUREG              # NUREG documents
DocumentType.PART_21            # Part 21 correspondence
DocumentType.INSPECTION_REPORT  # Inspection reports
DocumentType.SPEECH             # Speeches
DocumentType.LETTER             # Letters
DocumentType.MEMORANDUM         # Memoranda
DocumentType.ORDER              # Orders
DocumentType.LICENSE            # Licenses
```

### Document Fields

```python
# Available fields in search results
"AccessionNumber"    # Unique identifier
"Title"             # Document title
"DocumentType"      # Type of document
"AuthorName"        # Author name
"AuthorAffiliation" # Author's organization
"DocketNumber"      # NRC docket number
"Subject"           # Document subject
"DocumentDate"      # Creation date
"PublishDatePARS"   # Publication date
"Size"              # File size in bytes
"FileName"          # Original filename
"URL"               # Direct link to document
```

## Common Search Patterns

### 1. NUREG Documents by Topic

```python
def search_nureg_by_topic(topic: str, author: str = None):
    builder = SearchQueryBuilder()
    builder.nureg_documents()
    builder.content_search(topic)
    if author:
        builder.add_property_and("AuthorName", SearchOperator.STARTS_WITH, author)
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    return client.search(builder.build())
```

### 2. Part 21 Correspondence by Date Range

```python
def search_part21_by_date_range(start_date: str, end_date: str, topic: str = None):
    builder = SearchQueryBuilder()
    builder.part_21_correspondence()
    builder.date_range(start_date, end_date)
    if topic:
        builder.content_search(topic)
    builder.sort_by(SortField.PUBLISH_DATE, SortOrder.ASCENDING)
    return client.search(builder.build())
```

### 3. Inspection Reports by Facility

```python
def search_inspection_reports_by_facility(docket: str, topic: str = None):
    builder = SearchQueryBuilder()
    builder.inspection_reports()
    builder.add_property_and("DocketNumber", SearchOperator.STARTS_WITH, docket)
    if topic:
        builder.content_search(topic)
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    return client.search(builder.build())
```

### 4. Documents by Author and Date

```python
def search_by_author_and_date(author: str, start_date: str, end_date: str):
    builder = SearchQueryBuilder()
    builder.by_author(author)
    builder.date_range(start_date, end_date)
    builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
    return client.search(builder.build())
```

## Best Practices for Coding Agents

### 1. Use Type Hints

```python
from typing import List, Optional
from adamsnrc.types import SearchResult, DocumentMetadata

def analyze_documents(result: SearchResult) -> List[DocumentMetadata]:
    """Analyze search results and return structured data."""
    return result.documents
```

### 2. Handle Errors Gracefully

```python
def safe_search(client: ADAMSClient, query_builder: SearchQueryBuilder) -> Optional[SearchResult]:
    """Safely execute a search with error handling."""
    try:
        query = query_builder.build()
        return client.search(query)
    except ADAMSError as e:
        print(f"Search failed: {e}")
        return None
```

### 3. Use Batch Operations for Multiple Searches

```python
def search_multiple_topics(client: ADAMSClient, topics: List[str]) -> List[SearchResult]:
    """Search for multiple topics efficiently."""
    queries = [
        SearchQueryBuilder().nureg_documents().content_search(topic).build()
        for topic in topics
    ]
    return client.batch_search(queries)
```

### 4. Cache Frequently Used Results

```python
def get_cached_or_search(client: ADAMSClient, query_builder: SearchQueryBuilder) -> SearchResult:
    """Get cached result or perform new search."""
    query = query_builder.build()
    # The client automatically handles caching
    return client.search(query)
```

## Troubleshooting

### Common Issues

1. **Validation Errors**: Check that search operators and field names are valid
2. **Network Errors**: Use retry mechanism for temporary network issues
3. **Empty Results**: Verify search terms and date ranges
4. **Performance Issues**: Monitor cache usage and adjust cache size

### Debug Information

```python
# Enable debug logging
import logging
logging.getLogger('adamsnrc').setLevel(logging.DEBUG)

# Get client statistics
stats = client.get_statistics()
print(f"Client stats: {stats}")

# Check query structure
query = builder.build()
print(f"Query structure: {query.to_dict()}")
```

This guide provides coding agents with the essential information needed to effectively use the ADAMS API client package. The examples and patterns can be adapted and combined to create more complex search scenarios as needed. 