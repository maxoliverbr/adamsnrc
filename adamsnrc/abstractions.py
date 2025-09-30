"""
Simplified abstractions for the ADAMS API client.

This module provides high-level abstractions that simplify common API usage patterns,
making it easier for coding agents to work with the ADAMS API without needing to
understand the underlying complexity.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date
from dataclasses import dataclass

from .client import ADAMSClient
from .types import (
    SearchQuery,
    SearchQueryBuilder,
    SortField,
    SortOrder,
    SearchOperator,
    DocumentType,
    PropertySearch,
    DateRange,
)
from .utils import build_date_range, calculate_result_stats, group_results_by_field


@dataclass
class SimpleSearchRequest:
    """Simplified search request structure."""
    query: str = ""
    document_type: Optional[str] = None
    author: Optional[str] = None
    docket: Optional[str] = None
    subject: Optional[str] = None
    start_date: Optional[Union[str, datetime]] = None
    end_date: Optional[Union[str, datetime]] = None
    sort_by: str = "date"
    sort_order: str = "desc"
    limit: Optional[int] = None
    include_public: bool = True
    include_legacy: bool = False


@dataclass
class SearchFilters:
    """Simplified search filters."""
    document_types: List[str] = None
    authors: List[str] = None
    dockets: List[str] = None
    subjects: List[str] = None
    date_range: Optional[Tuple[Union[str, datetime], Union[str, datetime]]] = None
    added_today: bool = False
    added_this_month: bool = False
    folder_path: Optional[str] = None


class SimpleADAMSClient:
    """
    Simplified ADAMS API client with intuitive method names and reduced complexity.
    
    This class provides a more user-friendly interface that abstracts away the
    complexity of the underlying API while maintaining full functionality.
    """
    
    def __init__(self, **kwargs):
        """Initialize the simplified client."""
        self.client = ADAMSClient(**kwargs)
    
    # === CORE SEARCH METHODS ===
    
    def find_documents(self, 
                      query: str = "",
                      document_type: Optional[str] = None,
                      author: Optional[str] = None,
                      docket: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Find documents with a simple, intuitive interface.
        
        Args:
            query: Search query text
            document_type: Type of document (NUREG, Letter, etc.)
            author: Author name
            docket: Docket number
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary with search results and metadata
        """
        builder = self._build_simple_query(
            query=query,
            document_type=document_type,
            author=author,
            docket=docket,
            **kwargs
        )
        
        result = self.client.search(builder.build())
        return self._format_result(result)
    
    def find_by_type(self, document_type: str, query: str = "") -> Dict[str, Any]:
        """Find documents by type with optional content search."""
        return self.find_documents(query=query, document_type=document_type)
    
    def find_by_author(self, author: str, query: str = "") -> Dict[str, Any]:
        """Find documents by author with optional content search."""
        return self.find_documents(query=query, author=author)
    
    def find_by_docket(self, docket: str, query: str = "") -> Dict[str, Any]:
        """Find documents by docket with optional content search."""
        return self.find_documents(query=query, docket=docket)
    
    def find_recent(self, days: int = 30, query: str = "") -> Dict[str, Any]:
        """Find documents added in the last N days."""
        end_date = datetime.now()
        start_date = end_date.replace(day=1) if days == 0 else end_date.replace(day=max(1, end_date.day - days))
        
        return self.find_documents(
            query=query,
            start_date=start_date,
            end_date=end_date
        )
    
    def find_in_date_range(self, start_date: Union[str, datetime], 
                          end_date: Union[str, datetime], 
                          query: str = "") -> Dict[str, Any]:
        """Find documents within a specific date range."""
        return self.find_documents(
            query=query,
            start_date=start_date,
            end_date=end_date
        )
    
    # === SPECIALIZED SEARCH METHODS ===
    
    def find_nureg(self, topic: str = "") -> Dict[str, Any]:
        """Find NUREG documents about a specific topic."""
        return self.find_by_type("NUREG", topic)
    
    def find_letters(self, topic: str = "") -> Dict[str, Any]:
        """Find letters about a specific topic."""
        return self.find_by_type("Letter", topic)
    
    def find_part21(self, topic: str = "") -> Dict[str, Any]:
        """Find Part 21 correspondence about a specific topic."""
        return self.find_by_type("Part 21 Correspondence", topic)
    
    def find_inspection_reports(self, topic: str = "") -> Dict[str, Any]:
        """Find inspection reports about a specific topic."""
        return self.find_by_type("inspection report", topic)
    
    def find_safety_documents(self, query: str = "") -> Dict[str, Any]:
        """Find safety-related documents."""
        return self.find_documents(
            query=query,
            subject="safety"
        )
    
    def find_security_documents(self, query: str = "") -> Dict[str, Any]:
        """Find security-related documents."""
        return self.find_documents(
            query=query,
            subject="security"
        )
    
    # === BATCH SEARCH METHODS ===
    
    def find_multiple_authors(self, authors: List[str], query: str = "") -> Dict[str, Dict[str, Any]]:
        """Find documents by multiple authors."""
        results = {}
        for author in authors:
            results[author] = self.find_by_author(author, query)
        return results
    
    def find_multiple_dockets(self, dockets: List[str], query: str = "") -> Dict[str, Dict[str, Any]]:
        """Find documents by multiple dockets."""
        results = {}
        for docket in dockets:
            results[docket] = self.find_by_docket(docket, query)
        return results
    
    def find_multiple_types(self, document_types: List[str], query: str = "") -> Dict[str, Dict[str, Any]]:
        """Find documents of multiple types."""
        results = {}
        for doc_type in document_types:
            results[doc_type] = self.find_by_type(doc_type, query)
        return results
    
    # === ANALYTICS AND STATISTICS ===
    
    def get_document_stats(self, query: str = "", **filters) -> Dict[str, Any]:
        """Get statistics about documents matching criteria."""
        result = self.find_documents(query=query, **filters)
        return {
            "total_documents": result["count"],
            "query": query,
            "filters": filters,
            "statistics": calculate_result_stats(result["results"])
        }
    
    def get_author_stats(self, query: str = "") -> Dict[str, Any]:
        """Get statistics about authors for documents matching query."""
        result = self.find_documents(query=query)
        grouped = group_results_by_field(result["results"], "AuthorName")
        
        return {
            "total_authors": len(grouped),
            "total_documents": result["count"],
            "author_counts": {author: len(docs) for author, docs in grouped.items()},
            "top_authors": sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        }
    
    def get_type_stats(self, query: str = "") -> Dict[str, Any]:
        """Get statistics about document types for documents matching query."""
        result = self.find_documents(query=query)
        grouped = group_results_by_field(result["results"], "DocumentType")
        
        return {
            "total_types": len(grouped),
            "total_documents": result["count"],
            "type_counts": {doc_type: len(docs) for doc_type, docs in grouped.items()},
            "type_distribution": sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)
        }
    
    # === UTILITY METHODS ===
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the client configuration and statistics."""
        stats = self.client.get_statistics()
        return {
            "client_type": "SimpleADAMSClient",
            "underlying_client": "ADAMSClient",
            "statistics": stats,
            "cache_size": self.client._cache_size,
            "base_url": getattr(self.client, '_base_url', None)
        }
    
    def clear_cache(self) -> None:
        """Clear the client cache."""
        self.client.clear_cache()
    
    def set_cache_size(self, size: int) -> None:
        """Set the cache size."""
        self.client.set_cache_size(size)
    
    # === PRIVATE HELPER METHODS ===
    
    def _build_simple_query(self, **kwargs) -> SearchQueryBuilder:
        """Build a SearchQuery from simple parameters."""
        builder = SearchQueryBuilder()
        
        # Content search
        if kwargs.get("query"):
            builder.content_search(kwargs["query"])
        
        # Document type
        if kwargs.get("document_type"):
            builder.add_property_and("DocumentType", SearchOperator.CONTAINS, kwargs["document_type"])
        
        # Author
        if kwargs.get("author"):
            builder.add_property_and("AuthorName", SearchOperator.STARTS_WITH, kwargs["author"])
        
        # Docket
        if kwargs.get("docket"):
            builder.add_property_and("DocketNumber", SearchOperator.EQUALS, kwargs["docket"])
        
        # Subject
        if kwargs.get("subject"):
            builder.add_property_and("Subject", SearchOperator.CONTAINS, kwargs["subject"])
        
        # Date range
        if kwargs.get("start_date") and kwargs.get("end_date"):
            builder.date_range(kwargs["start_date"], kwargs["end_date"])
        
        # Libraries
        if kwargs.get("include_public", True):
            builder.public_library(True)
        if kwargs.get("include_legacy", False):
            builder.legacy_library(True)
        
        # Sorting
        sort_field = kwargs.get("sort_by", "date")
        sort_order = kwargs.get("sort_order", "desc")
        
        if sort_field == "date":
            builder.sort_by(SortField.DOCUMENT_DATE, 
                          SortOrder.DESCENDING if sort_order == "desc" else SortOrder.ASCENDING)
        elif sort_field == "title":
            builder.sort_by(SortField.TITLE, 
                          SortOrder.DESCENDING if sort_order == "desc" else SortOrder.ASCENDING)
        elif sort_field == "author":
            builder.sort_by(SortField.AUTHOR_NAME, 
                          SortOrder.DESCENDING if sort_order == "desc" else SortOrder.ASCENDING)
        
        return builder
    
    def _format_result(self, result) -> Dict[str, Any]:
        """Format a SearchResult into a simple dictionary."""
        return {
            "count": result.count,
            "matches": result.matches,
            "results": result.results,
            "documents": result.documents if hasattr(result, 'documents') else [],
            "statistics": result.statistics if hasattr(result, 'statistics') else None,
            "metadata": result.metadata if hasattr(result, 'metadata') else {}
        }


class QuickSearch:
    """
    Ultra-simplified search interface for the most common use cases.
    
    This class provides static methods for quick, one-line searches without
    needing to instantiate a client.
    """
    
    _client = None
    
    @classmethod
    def _get_client(cls):
        """Get or create the default client."""
        if cls._client is None:
            cls._client = SimpleADAMSClient()
        return cls._client
    
    @classmethod
    def nureg(cls, topic: str) -> Dict[str, Any]:
        """Quick NUREG search."""
        return cls._get_client().find_nureg(topic)
    
    @classmethod
    def letters(cls, topic: str) -> Dict[str, Any]:
        """Quick letters search."""
        return cls._get_client().find_letters(topic)
    
    @classmethod
    def part21(cls, topic: str) -> Dict[str, Any]:
        """Quick Part 21 search."""
        return cls._get_client().find_part21(topic)
    
    @classmethod
    def inspections(cls, topic: str) -> Dict[str, Any]:
        """Quick inspection reports search."""
        return cls._get_client().find_inspection_reports(topic)
    
    @classmethod
    def author(cls, author: str, topic: str = "") -> Dict[str, Any]:
        """Quick author search."""
        return cls._get_client().find_by_author(author, topic)
    
    @classmethod
    def docket(cls, docket: str, topic: str = "") -> Dict[str, Any]:
        """Quick docket search."""
        return cls._get_client().find_by_docket(docket, topic)
    
    @classmethod
    def safety(cls, topic: str = "") -> Dict[str, Any]:
        """Quick safety documents search."""
        return cls._get_client().find_safety_documents(topic)
    
    @classmethod
    def recent(cls, days: int = 30, topic: str = "") -> Dict[str, Any]:
        """Quick recent documents search."""
        return cls._get_client().find_recent(days, topic)


class SearchTemplate:
    """
    Pre-defined search templates for common use cases.
    
    This class provides ready-to-use search patterns that can be customized
    with specific parameters.
    """
    
    def __init__(self, client: Optional[SimpleADAMSClient] = None):
        self.client = client or SimpleADAMSClient()
    
    def regulatory_letters(self, topic: str = "", author: str = "", days: int = 30) -> Dict[str, Any]:
        """Template for regulatory letters."""
        return self.client.find_documents(
            query=topic,
            document_type="Letter",
            author=author
        )
    
    def safety_reports(self, topic: str = "", docket: str = "") -> Dict[str, Any]:
        """Template for safety reports."""
        return self.client.find_documents(
            query=topic,
            subject="safety",
            docket=docket
        )
    
    def emergency_documents(self, days: int = 7) -> Dict[str, Any]:
        """Template for emergency-related documents."""
        return self.client.find_documents(
            query="emergency",
            start_date=datetime.now().replace(day=max(1, datetime.now().day - days)),
            end_date=datetime.now()
        )
    
    def nrc_communications(self, topic: str = "") -> Dict[str, Any]:
        """Template for NRC communications."""
        return self.client.find_documents(
            query=topic,
            document_type="Letter"
        )
    
    def plant_specific(self, docket: str, topic: str = "") -> Dict[str, Any]:
        """Template for plant-specific documents."""
        return self.client.find_documents(
            query=topic,
            docket=docket
        )


# === CONVENIENCE FUNCTIONS ===

def quick_search(query: str, doc_type: str = None) -> Dict[str, Any]:
    """One-line function for quick searches."""
    client = SimpleADAMSClient()
    return client.find_documents(query=query, document_type=doc_type)


def find_nureg(topic: str) -> Dict[str, Any]:
    """One-line function to find NUREG documents."""
    return QuickSearch.nureg(topic)


def find_letters(topic: str) -> Dict[str, Any]:
    """One-line function to find letters."""
    return QuickSearch.letters(topic)


def find_safety_docs(topic: str = "") -> Dict[str, Any]:
    """One-line function to find safety documents."""
    return QuickSearch.safety(topic)


def find_recent_docs(days: int = 30, topic: str = "") -> Dict[str, Any]:
    """One-line function to find recent documents."""
    return QuickSearch.recent(days, topic)


def get_author_stats(author: str) -> Dict[str, Any]:
    """One-line function to get author statistics."""
    client = SimpleADAMSClient()
    return client.get_author_stats(f"author:{author}")


# === EXPORTED CLASSES AND FUNCTIONS ===

__all__ = [
    'SimpleADAMSClient',
    'QuickSearch', 
    'SearchTemplate',
    'SimpleSearchRequest',
    'SearchFilters',
    'quick_search',
    'find_nureg',
    'find_letters', 
    'find_safety_docs',
    'find_recent_docs',
    'get_author_stats'
]
