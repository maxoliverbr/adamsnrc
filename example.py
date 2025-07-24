#!/usr/bin/env python3
"""
Example usage of the ADAMSNRC API client.
"""
from adamsnrc.main import content_search, SearchResult
from adamsnrc.utils import build_date_range, calculate_result_stats
from adamsnrc.main import ADAMSError, ADAMSValidationError

def main():
    """Demonstrate basic usage of the ADAMSNRC API client."""
    print("ADAMSNRC API Client Example")
    print("=" * 40)
    
    try:
        # Example 1: Simple content search
        print("\n1. Simple content search:")
        result = content_search(
            properties_search=[("DocumentType", "ends", "NUREG")],
            single_content_search="steam generator",
            sort="DocumentDate",
            order="DESC"
        )
        print(f"   Found {result.count} NUREG documents about steam generators")
        
        # Example 2: Show result structure
        print("\n2. Result structure:")
        print(f"   Metadata: {result.meta}")
        if result.results:
            print(f"   First result: {result.results[0]}")
        
        # Example 3: Date range utility
        print("\n3. Date range utility:")
        date_range = build_date_range(
            "01/01/2023 12:00 AM",
            "12/31/2023 11:59 PM"
        )
        print(f"   Date range: {date_range}")
        
        # Example 4: Statistics utility
        print("\n4. Result statistics:")
        if result.results:
            stats = calculate_result_stats(result.results)
            print(f"   Total results: {stats['total_results']}")
            print(f"   Unique authors: {stats['unique_authors']}")
            print(f"   Unique document types: {stats['unique_document_types']}")
        
        print("\n✅ All examples completed successfully!")
        
    except ADAMSValidationError as e:
        print(f"❌ Validation error: {e}")
    except ADAMSError as e:
        print(f"❌ ADAMS API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 