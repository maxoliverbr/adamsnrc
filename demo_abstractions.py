#!/usr/bin/env python3
"""
Demonstration script for ADAMS API abstractions.

This script shows the different levels of abstraction available and how they
simplify common API usage patterns.
"""

from adamsnrc.abstractions import (
    SimpleADAMSClient,
    QuickSearch,
    SearchTemplate,
    quick_search,
    find_nureg,
    find_letters,
)


def demonstrate_abstraction_levels():
    """Demonstrate different abstraction levels."""
    print("ADAMS API Abstraction Demonstration")
    print("=" * 50)
    
    # Level 1: One-line convenience functions (simplest)
    print("\n1. One-line convenience functions (simplest):")
    
    result = find_nureg("safety analysis")
    print(f"   find_nureg('safety analysis'): {result['count']} documents")
    
    result = find_letters("emergency planning")
    print(f"   find_letters('emergency planning'): {result['count']} documents")
    
    result = quick_search("steam generator", "NUREG")
    print(f"   quick_search('steam generator', 'NUREG'): {result['count']} documents")
    
    # Level 2: QuickSearch static methods
    print("\n2. QuickSearch static methods:")
    
    result = QuickSearch.nureg("safety analysis")
    print(f"   QuickSearch.nureg('safety analysis'): {result['count']} documents")
    
    result = QuickSearch.author("Macfarlane", "nuclear")
    print(f"   QuickSearch.author('Macfarlane', 'nuclear'): {result['count']} documents")
    
    result = QuickSearch.recent(days=30, topic="emergency")
    print(f"   QuickSearch.recent(days=30, topic='emergency'): {result['count']} documents")
    
    # Level 3: SimpleADAMSClient (most flexible)
    print("\n3. SimpleADAMSClient (most flexible):")
    
    client = SimpleADAMSClient()
    
    result = client.find_nureg("safety analysis")
    print(f"   client.find_nureg('safety analysis'): {result['count']} documents")
    
    result = client.find_by_author("Macfarlane", "nuclear")
    print(f"   client.find_by_author('Macfarlane', 'nuclear'): {result['count']} documents")
    
    result = client.find_recent(days=30, query="emergency")
    print(f"   client.find_recent(days=30, query='emergency'): {result['count']} documents")
    
    # Level 4: SearchTemplate (pre-defined patterns)
    print("\n4. SearchTemplate (pre-defined patterns):")
    
    template = SearchTemplate()
    
    result = template.regulatory_letters("safety valve")
    print(f"   template.regulatory_letters('safety valve'): {result['count']} documents")
    
    result = template.emergency_documents(days=14)
    print(f"   template.emergency_documents(days=14): {result['count']} documents")
    
    result = template.plant_specific("05000282", "safety")
    print(f"   template.plant_specific('05000282', 'safety'): {result['count']} documents")


def demonstrate_complex_workflows():
    """Demonstrate complex workflows using abstractions."""
    print("\n" + "=" * 50)
    print("Complex Workflow Demonstration")
    print("=" * 50)
    
    client = SimpleADAMSClient()
    
    # Workflow 1: Emergency response analysis
    print("\n1. Emergency Response Analysis:")
    
    # Find recent emergency documents
    recent_emergency = client.find_recent(days=7, query="emergency")
    print(f"   Recent emergency documents (7 days): {recent_emergency['count']}")
    
    # Find emergency NUREG documents
    emergency_nureg = client.find_nureg("emergency")
    print(f"   Emergency NUREG documents: {emergency_nureg['count']}")
    
    # Get emergency document statistics
    emergency_stats = client.get_document_stats("emergency")
    print(f"   Emergency document statistics: {emergency_stats['statistics']['total_results']} total")
    
    # Workflow 2: Safety analysis by multiple authors
    print("\n2. Safety Analysis by Multiple Authors:")
    
    safety_authors = ["Macfarlane", "Smith", "Johnson"]
    safety_results = client.find_multiple_authors(safety_authors, "safety")
    
    total_safety_docs = sum(result['count'] for result in safety_results.values())
    print(f"   Total safety documents by target authors: {total_safety_docs}")
    
    for author, result in safety_results.items():
        print(f"   {author}: {result['count']} safety documents")
    
    # Workflow 3: Plant-specific analysis
    print("\n3. Plant-Specific Analysis:")
    
    plant_docket = "05000282"
    plant_docs = client.find_by_docket(plant_docket)
    print(f"   Total documents for plant {plant_docket}: {plant_docs['count']}")
    
    # Find recent safety documents for the plant
    recent_plant_safety = client.find_documents(
        query="safety",
        docket=plant_docket
    )
    print(f"   Recent safety documents for plant: {recent_plant_safety['count']}")


def demonstrate_analytics():
    """Demonstrate analytics capabilities."""
    print("\n" + "=" * 50)
    print("Analytics Demonstration")
    print("=" * 50)
    
    client = SimpleADAMSClient()
    
    # Author statistics
    print("\n1. Author Statistics for Safety Documents:")
    author_stats = client.get_author_stats("safety")
    print(f"   Total authors: {author_stats['total_authors']}")
    print(f"   Total documents: {author_stats['total_documents']}")
    print("   Top authors:")
    for author, docs in author_stats['top_authors'][:3]:
        print(f"     {author}: {len(docs)} documents")
    
    # Document type statistics
    print("\n2. Document Type Statistics for Emergency Documents:")
    type_stats = client.get_type_stats("emergency")
    print(f"   Total types: {type_stats['total_types']}")
    print(f"   Total documents: {type_stats['total_documents']}")
    print("   Type distribution:")
    for doc_type, docs in type_stats['type_distribution'][:3]:
        print(f"     {doc_type}: {len(docs)} documents")


def demonstrate_performance():
    """Demonstrate performance considerations."""
    print("\n" + "=" * 50)
    print("Performance Demonstration")
    print("=" * 50)
    
    import time
    
    # Compare QuickSearch vs SimpleADAMSClient
    print("\n1. QuickSearch vs SimpleADAMSClient Performance:")
    
    # Time QuickSearch
    start_time = time.time()
    result1 = QuickSearch.nureg("safety")
    quick_time = time.time() - start_time
    
    # Time SimpleADAMSClient
    client = SimpleADAMSClient()
    start_time = time.time()
    result2 = client.find_nureg("safety")
    simple_time = time.time() - start_time
    
    print(f"   QuickSearch: {quick_time:.3f}s, found {result1['count']} documents")
    print(f"   SimpleADAMSClient: {simple_time:.3f}s, found {result2['count']} documents")
    print(f"   Performance difference: {abs(quick_time - simple_time):.3f}s")
    
    # Compare batch vs individual searches
    print("\n2. Batch vs Individual Search Performance:")
    
    authors = ["Macfarlane", "Smith"]
    
    # Time batch search
    start_time = time.time()
    batch_results = client.find_multiple_authors(authors, "safety")
    batch_time = time.time() - start_time
    
    # Time individual searches
    start_time = time.time()
    individual_results = {}
    for author in authors:
        individual_results[author] = client.find_by_author(author, "safety")
    individual_time = time.time() - start_time
    
    print(f"   Batch search: {batch_time:.3f}s")
    print(f"   Individual searches: {individual_time:.3f}s")
    print(f"   Speed improvement: {individual_time/batch_time:.2f}x faster with batch")


def main():
    """Run all demonstrations."""
    try:
        demonstrate_abstraction_levels()
        demonstrate_complex_workflows()
        demonstrate_analytics()
        demonstrate_performance()
        
        print("\n" + "=" * 50)
        print("Demonstration completed successfully!")
        print("\nKey Benefits of Abstractions:")
        print("1. Simplicity: Complex API calls become simple method calls")
        print("2. Consistency: Uniform interfaces across different operations")
        print("3. Efficiency: Optimized patterns and batch operations")
        print("4. Flexibility: Multiple abstraction levels for different needs")
        
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
