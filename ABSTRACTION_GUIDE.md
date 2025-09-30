# ADAMS API Abstraction Guide

This guide explains how to use the simplified abstractions for the ADAMS API client, making it easier for coding agents to work with the API without understanding its underlying complexity.

## Overview

The abstraction layer provides three levels of simplification:

1. **SimpleADAMSClient** - Simplified object-oriented interface
2. **QuickSearch** - Static methods for ultra-quick searches
3. **SearchTemplate** - Pre-defined search patterns
4. **Convenience Functions** - One-line functions for common operations

## Quick Start

### Basic Usage

```python
from adamsnrc.abstractions import SimpleADAMSClient, QuickSearch

# Option 1: Simple client
client = SimpleADAMSClient()
result = client.find_nureg("safety analysis")

# Option 2: Quick search (no client instantiation needed)
result = QuickSearch.nureg("safety analysis")

# Option 3: One-line function
from adamsnrc.abstractions import find_nureg
result = find_nureg("safety analysis")
```

## SimpleADAMSClient

The `SimpleADAMSClient` provides an intuitive interface that abstracts away the complexity of the underlying API.

### Core Search Methods

```python
client = SimpleADAMSClient()

# Find documents with simple parameters
result = client.find_documents(
    query="steam generator",
    document_type="NUREG",
    author="Macfarlane",
    docket="05000282"
)

# Specialized searches
result = client.find_by_type("Letter", "safety")
result = client.find_by_author("Macfarlane", "nuclear power")
result = client.find_by_docket("05000282", "emergency")

# Time-based searches
result = client.find_recent(days=30, query="safety")
result = client.find_in_date_range("01/01/2023", "12/31/2023", "steam generator")
```

### Document Type Specializations

```python
# Find specific document types
result = client.find_nureg("emergency planning")
result = client.find_letters("safety valve")
result = client.find_part21("pressure relief")
result = client.find_inspection_reports("safety systems")

# Topic-based searches
result = client.find_safety_documents("reactor")
result = client.find_security_documents("access control")
```

### Batch Operations

```python
# Search multiple authors
authors = ["Macfarlane", "Smith", "Johnson"]
results = client.find_multiple_authors(authors, "safety")

# Search multiple dockets
dockets = ["05000282", "05000300", "05000400"]
results = client.find_multiple_dockets(dockets, "emergency")

# Search multiple document types
doc_types = ["NUREG", "Letter", "Memorandum"]
results = client.find_multiple_types(doc_types, "nuclear power")
```

### Analytics and Statistics

```python
# Get document statistics
stats = client.get_document_stats("steam generator")
print(f"Total documents: {stats['total_documents']}")
print(f"Statistics: {stats['statistics']}")

# Get author statistics
author_stats = client.get_author_stats("safety")
print(f"Top authors: {author_stats['top_authors']}")

# Get document type statistics
type_stats = client.get_type_stats("emergency")
print(f"Type distribution: {type_stats['type_distribution']}")
```

## QuickSearch

The `QuickSearch` class provides static methods for ultra-quick searches without needing to instantiate a client.

```python
from adamsnrc.abstractions import QuickSearch

# Quick searches (no client instantiation needed)
result = QuickSearch.nureg("safety analysis")
result = QuickSearch.letters("emergency planning")
result = QuickSearch.part21("valve failure")
result = QuickSearch.inspections("safety systems")
result = QuickSearch.author("Macfarlane", "nuclear")
result = QuickSearch.docket("05000282", "emergency")
result = QuickSearch.safety("reactor")
result = QuickSearch.recent(days=7, topic="emergency")
```

## SearchTemplate

The `SearchTemplate` class provides pre-defined search patterns for common use cases.

```python
from adamsnrc.abstractions import SearchTemplate

template = SearchTemplate()

# Pre-defined templates
result = template.regulatory_letters("safety valve", "Macfarlane")
result = template.safety_reports("steam generator", "05000282")
result = template.emergency_documents(days=14)
result = template.nrc_communications("nuclear power plant")
result = template.plant_specific("05000282", "safety")
```

## Convenience Functions

One-line functions for the most common operations:

```python
from adamsnrc.abstractions import (
    quick_search,
    find_nureg,
    find_letters,
    find_safety_docs,
    find_recent_docs,
    get_author_stats
)

# One-line searches
result = quick_search("steam generator", "NUREG")
result = find_nureg("safety analysis")
result = find_letters("emergency response")
result = find_safety_docs("reactor safety")
result = find_recent_docs(days=30, topic="emergency")

# Statistics
stats = get_author_stats("Macfarlane")
```

## Complex Workflows

### Emergency Response Workflow

```python
client = SimpleADAMSClient()

# Find recent emergency documents
recent_emergency = client.find_recent(days=7, query="emergency")

# Find emergency NUREG documents
emergency_nureg = client.find_nureg("emergency")

# Get statistics
emergency_stats = client.get_document_stats("emergency")
```

### Safety Analysis Workflow

```python
# Find safety documents by multiple authors
safety_authors = ["Macfarlane", "Smith", "Johnson"]
safety_results = client.find_multiple_authors(safety_authors, "safety")

# Get author statistics for safety documents
safety_author_stats = client.get_author_stats("safety")
```

### Plant-Specific Analysis Workflow

```python
# Analyze documents for a specific plant
plant_docket = "05000282"
plant_docs = client.find_by_docket(plant_docket)

# Get document type statistics for the plant
plant_type_stats = client.get_type_stats(f"docket:{plant_docket}")

# Find recent safety documents for the plant
recent_plant_safety = client.find_documents(
    query="safety",
    docket=plant_docket
)
```

## Performance Considerations

### Caching

The abstraction layer automatically uses the underlying client's caching mechanism:

```python
client = SimpleADAMSClient()

# First search (cache miss)
result1 = client.find_nureg("safety")

# Second search (cache hit - faster)
result2 = client.find_nureg("safety")

# Clear cache if needed
client.clear_cache()

# Adjust cache size
client.set_cache_size(200)
```

### Batch vs Individual Searches

Batch operations are generally faster than individual searches:

```python
# Faster: Batch search
authors = ["Macfarlane", "Smith", "Johnson"]
results = client.find_multiple_authors(authors, "safety")

# Slower: Individual searches
results = {}
for author in authors:
    results[author] = client.find_by_author(author, "safety")
```

## Error Handling

The abstraction layer provides consistent error handling:

```python
try:
    result = client.find_documents("steam generator")
    print(f"Found {result['count']} documents")
except Exception as e:
    print(f"Search failed: {e}")
```

## Configuration

You can still access the underlying client for advanced configuration:

```python
# Create client with custom configuration
client = SimpleADAMSClient(
    timeout=30,
    max_retries=5,
    log_level="INFO"
)

# Get client information
info = client.get_client_info()
print(f"Client statistics: {info['statistics']}")
```

## Migration from Direct API

### Before (Direct API)

```python
from adamsnrc.client import ADAMSClient
from adamsnrc.types import SearchQueryBuilder, SearchOperator, SortField, SortOrder

client = ADAMSClient()
builder = SearchQueryBuilder()
builder.add_property_and("DocumentType", SearchOperator.ENDS_WITH, "NUREG")
builder.content_search("safety analysis")
builder.sort_by(SortField.DOCUMENT_DATE, SortOrder.DESCENDING)
query = builder.build()
result = client.search(query)
```

### After (Abstraction)

```python
from adamsnrc.abstractions import SimpleADAMSClient

client = SimpleADAMSClient()
result = client.find_nureg("safety analysis")
```

## Best Practices

1. **Use the appropriate abstraction level**:
   - Use `QuickSearch` for one-off searches
   - Use `SimpleADAMSClient` for multiple operations
   - Use `SearchTemplate` for repeated patterns

2. **Leverage batch operations** for multiple similar searches

3. **Use analytics methods** for insights rather than manual processing

4. **Cache results** when performing repeated searches

5. **Handle errors gracefully** with try-catch blocks

## Examples

See `abstraction_examples.py` for comprehensive examples of all abstraction features.

Run the examples:

```python
from adamsnrc.abstraction_examples import run_all_abstraction_examples
run_all_abstraction_examples()
```

## Summary

The abstraction layer provides three main benefits:

1. **Simplicity**: Reduces complex API calls to simple method calls
2. **Consistency**: Provides uniform interfaces across different operations
3. **Efficiency**: Optimizes common patterns and provides batch operations

Choose the abstraction level that best fits your needs, from ultra-simple one-line functions to comprehensive client objects with full functionality.
