"""
Examples demonstrating the simplified abstractions for the ADAMS API.

This module shows how to use the abstraction layer to simplify common API usage patterns.
"""

from .abstractions import (
    SimpleADAMSClient,
    QuickSearch,
    SearchTemplate,
    SimpleSearchRequest,
    SearchFilters,
    quick_search,
    find_nureg,
    find_letters,
    find_safety_docs,
    find_recent_docs,
    get_author_stats,
)


def simple_client_examples():
    """Demonstrate the SimpleADAMSClient class."""
    print("\n=== SimpleADAMSClient Examples ===")
    
    # Initialize the simplified client
    client = SimpleADAMSClient()
    
    # 1. Basic document search
    print("\n1. Basic document search:")
    result = client.find_documents("steam generator")
    print(f"Found {result['count']} documents about steam generators")
    
    # 2. Search by document type
    print("\n2. Search by document type:")
    result = client.find_by_type("NUREG", "safety")
    print(f"Found {result['count']} NUREG documents about safety")
    
    # 3. Search by author
    print("\n3. Search by author:")
    result = client.find_by_author("Macfarlane", "nuclear power")
    print(f"Found {result['count']} documents by Macfarlane about nuclear power")
    
    # 4. Search by docket
    print("\n4. Search by docket:")
    result = client.find_by_docket("05000282", "emergency")
    print(f"Found {result['count']} documents for docket 05000282 about emergency")
    
    # 5. Find recent documents
    print("\n5. Find recent documents:")
    result = client.find_recent(days=30, query="safety")
    print(f"Found {result['count']} safety documents from the last 30 days")
    
    # 6. Find documents in date range
    print("\n6. Find documents in date range:")
    from datetime import datetime
    result = client.find_in_date_range(
        "01/01/2023 12:00 AM",
        "12/31/2023 11:59 PM",
        "steam generator"
    )
    print(f"Found {result['count']} steam generator documents from 2023")
    
    # 7. Specialized searches
    print("\n7. Specialized searches:")
    
    nureg_result = client.find_nureg("emergency planning")
    print(f"NUREG documents about emergency planning: {nureg_result['count']}")
    
    letters_result = client.find_letters("safety valve")
    print(f"Letters about safety valves: {letters_result['count']}")
    
    part21_result = client.find_part21("pressure relief")
    print(f"Part 21 documents about pressure relief: {part21_result['count']}")
    
    # 8. Safety and security documents
    print("\n8. Safety and security documents:")
    
    safety_result = client.find_safety_documents("reactor")
    print(f"Safety documents about reactors: {safety_result['count']}")
    
    security_result = client.find_security_documents("access control")
    print(f"Security documents about access control: {security_result['count']}")


def batch_search_examples():
    """Demonstrate batch search functionality."""
    print("\n=== Batch Search Examples ===")
    
    client = SimpleADAMSClient()
    
    # 1. Multiple authors
    print("\n1. Multiple authors:")
    authors = ["Macfarlane", "Smith", "Johnson"]
    author_results = client.find_multiple_authors(authors, "safety")
    
    for author, result in author_results.items():
        print(f"{author}: {result['count']} safety documents")
    
    # 2. Multiple dockets
    print("\n2. Multiple dockets:")
    dockets = ["05000282", "05000300", "05000400"]
    docket_results = client.find_multiple_dockets(dockets, "emergency")
    
    for docket, result in docket_results.items():
        print(f"Docket {docket}: {result['count']} emergency documents")
    
    # 3. Multiple document types
    print("\n3. Multiple document types:")
    doc_types = ["NUREG", "Letter", "Memorandum"]
    type_results = client.find_multiple_types(doc_types, "nuclear power")
    
    for doc_type, result in type_results.items():
        print(f"{doc_type}: {result['count']} nuclear power documents")


def analytics_examples():
    """Demonstrate analytics and statistics functionality."""
    print("\n=== Analytics Examples ===")
    
    client = SimpleADAMSClient()
    
    # 1. Document statistics
    print("\n1. Document statistics:")
    stats = client.get_document_stats("steam generator")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Statistics: {stats['statistics']}")
    
    # 2. Author statistics
    print("\n2. Author statistics:")
    author_stats = client.get_author_stats("safety")
    print(f"Total authors: {author_stats['total_authors']}")
    print(f"Top authors: {author_stats['top_authors'][:3]}")
    
    # 3. Document type statistics
    print("\n3. Document type statistics:")
    type_stats = client.get_type_stats("emergency")
    print(f"Total types: {type_stats['total_types']}")
    print(f"Type distribution: {type_stats['type_distribution'][:3]}")


def quick_search_examples():
    """Demonstrate the QuickSearch static methods."""
    print("\n=== QuickSearch Examples ===")
    
    # 1. Quick NUREG search
    print("\n1. Quick NUREG search:")
    result = QuickSearch.nureg("safety analysis")
    print(f"Found {result['count']} NUREG documents about safety analysis")
    
    # 2. Quick letters search
    print("\n2. Quick letters search:")
    result = QuickSearch.letters("emergency planning")
    print(f"Found {result['count']} letters about emergency planning")
    
    # 3. Quick Part 21 search
    print("\n3. Quick Part 21 search:")
    result = QuickSearch.part21("valve failure")
    print(f"Found {result['count']} Part 21 documents about valve failure")
    
    # 4. Quick inspection reports
    print("\n4. Quick inspection reports:")
    result = QuickSearch.inspections("safety systems")
    print(f"Found {result['count']} inspection reports about safety systems")
    
    # 5. Quick author search
    print("\n5. Quick author search:")
    result = QuickSearch.author("Macfarlane", "nuclear")
    print(f"Found {result['count']} nuclear documents by Macfarlane")
    
    # 6. Quick docket search
    print("\n6. Quick docket search:")
    result = QuickSearch.docket("05000282", "emergency")
    print(f"Found {result['count']} emergency documents for docket 05000282")
    
    # 7. Quick safety documents
    print("\n7. Quick safety documents:")
    result = QuickSearch.safety("reactor")
    print(f"Found {result['count']} safety documents about reactors")
    
    # 8. Quick recent documents
    print("\n8. Quick recent documents:")
    result = QuickSearch.recent(days=7, topic="emergency")
    print(f"Found {result['count']} emergency documents from the last 7 days")


def search_template_examples():
    """Demonstrate the SearchTemplate class."""
    print("\n=== SearchTemplate Examples ===")
    
    template = SearchTemplate()
    
    # 1. Regulatory letters template
    print("\n1. Regulatory letters template:")
    result = template.regulatory_letters("safety valve", "Macfarlane")
    print(f"Found {result['count']} regulatory letters by Macfarlane about safety valves")
    
    # 2. Safety reports template
    print("\n2. Safety reports template:")
    result = template.safety_reports("steam generator", "05000282")
    print(f"Found {result['count']} safety reports about steam generators for docket 05000282")
    
    # 3. Emergency documents template
    print("\n3. Emergency documents template:")
    result = template.emergency_documents(days=14)
    print(f"Found {result['count']} emergency documents from the last 14 days")
    
    # 4. NRC communications template
    print("\n4. NRC communications template:")
    result = template.nrc_communications("nuclear power plant")
    print(f"Found {result['count']} NRC communications about nuclear power plants")
    
    # 5. Plant-specific template
    print("\n5. Plant-specific template:")
    result = template.plant_specific("05000282", "safety")
    print(f"Found {result['count']} safety documents for plant docket 05000282")


def convenience_function_examples():
    """Demonstrate convenience functions."""
    print("\n=== Convenience Function Examples ===")
    
    # 1. Quick search function
    print("\n1. Quick search function:")
    result = quick_search("steam generator", "NUREG")
    print(f"Found {result['count']} NUREG documents about steam generators")
    
    # 2. Find NUREG function
    print("\n2. Find NUREG function:")
    result = find_nureg("safety analysis")
    print(f"Found {result['count']} NUREG documents about safety analysis")
    
    # 3. Find letters function
    print("\n3. Find letters function:")
    result = find_letters("emergency response")
    print(f"Found {result['count']} letters about emergency response")
    
    # 4. Find safety documents function
    print("\n4. Find safety documents function:")
    result = find_safety_docs("reactor safety")
    print(f"Found {result['count']} safety documents about reactor safety")
    
    # 5. Find recent documents function
    print("\n5. Find recent documents function:")
    result = find_recent_docs(days=30, topic="emergency")
    print(f"Found {result['count']} emergency documents from the last 30 days")
    
    # 6. Get author statistics function
    print("\n6. Get author statistics function:")
    stats = get_author_stats("Macfarlane")
    print(f"Author statistics: {stats}")


def complex_workflow_examples():
    """Demonstrate complex workflows using abstractions."""
    print("\n=== Complex Workflow Examples ===")
    
    client = SimpleADAMSClient()
    
    # 1. Emergency response workflow
    print("\n1. Emergency response workflow:")
    
    # Find recent emergency documents
    recent_emergency = client.find_recent(days=7, query="emergency")
    print(f"Recent emergency documents: {recent_emergency['count']}")
    
    # Find emergency NUREG documents
    emergency_nureg = client.find_nureg("emergency")
    print(f"Emergency NUREG documents: {emergency_nureg['count']}")
    
    # Get statistics
    emergency_stats = client.get_document_stats("emergency")
    print(f"Emergency document statistics: {emergency_stats['statistics']}")
    
    # 2. Safety analysis workflow
    print("\n2. Safety analysis workflow:")
    
    # Find safety documents by multiple authors
    safety_authors = ["Macfarlane", "Smith", "Johnson"]
    safety_results = client.find_multiple_authors(safety_authors, "safety")
    
    total_safety_docs = sum(result['count'] for result in safety_results.values())
    print(f"Total safety documents by target authors: {total_safety_docs}")
    
    # Get author statistics for safety documents
    safety_author_stats = client.get_author_stats("safety")
    print(f"Top safety document authors: {safety_author_stats['top_authors'][:3]}")
    
    # 3. Plant-specific analysis workflow
    print("\n3. Plant-specific analysis workflow:")
    
    # Analyze documents for a specific plant
    plant_docket = "05000282"
    plant_docs = client.find_by_docket(plant_docket)
    print(f"Total documents for plant {plant_docket}: {plant_docs['count']}")
    
    # Get document type statistics for the plant
    plant_type_stats = client.get_type_stats(f"docket:{plant_docket}")
    print(f"Document types for plant: {plant_type_stats['type_counts']}")
    
    # Find recent safety documents for the plant
    recent_plant_safety = client.find_documents(
        query="safety",
        docket=plant_docket
    )
    print(f"Recent safety documents for plant: {recent_plant_safety['count']}")


def performance_comparison_examples():
    """Demonstrate performance comparisons between abstraction levels."""
    print("\n=== Performance Comparison Examples ===")
    
    import time
    
    # 1. Simple client vs QuickSearch
    print("\n1. Simple client vs QuickSearch:")
    
    simple_client = SimpleADAMSClient()
    
    # Time SimpleADAMSClient
    start_time = time.time()
    result1 = simple_client.find_nureg("safety")
    simple_time = time.time() - start_time
    
    # Time QuickSearch
    start_time = time.time()
    result2 = QuickSearch.nureg("safety")
    quick_time = time.time() - start_time
    
    print(f"SimpleADAMSClient: {simple_time:.3f}s, found {result1['count']} documents")
    print(f"QuickSearch: {quick_time:.3f}s, found {result2['count']} documents")
    
    # 2. Batch operations
    print("\n2. Batch operations:")
    
    authors = ["Macfarlane", "Smith", "Johnson"]
    
    # Time batch search
    start_time = time.time()
    batch_results = simple_client.find_multiple_authors(authors, "safety")
    batch_time = time.time() - start_time
    
    # Time individual searches
    start_time = time.time()
    individual_results = {}
    for author in authors:
        individual_results[author] = simple_client.find_by_author(author, "safety")
    individual_time = time.time() - start_time
    
    print(f"Batch search: {batch_time:.3f}s")
    print(f"Individual searches: {individual_time:.3f}s")
    print(f"Speed improvement: {individual_time/batch_time:.2f}x faster")


def run_all_abstraction_examples():
    """Run all abstraction examples."""
    print("ADAMS API Abstraction Examples")
    print("=" * 50)
    
    try:
        simple_client_examples()
        batch_search_examples()
        analytics_examples()
        quick_search_examples()
        search_template_examples()
        convenience_function_examples()
        complex_workflow_examples()
        performance_comparison_examples()
        
        print("\n" + "=" * 50)
        print("All abstraction examples completed successfully!")
        
    except Exception as e:
        print(f"\nError running abstraction examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_abstraction_examples()
