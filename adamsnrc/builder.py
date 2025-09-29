"""
Builder pattern for constructing ADAMS API search queries.

This module provides a fluent interface for building complex search queries
that is more intuitive for coding agents and human developers.
"""

from typing import Any, List, Optional, Union
from datetime import datetime

from .types import (
    SearchQuery,
    PropertySearch,
    DateRange,
    SearchOptions,
    SearchOperator,
    SortField,
    SortOrder,
    DocumentType,
    LibraryType,
)


class SearchQueryBuilder:
    """
    Fluent builder for constructing ADAMS API search queries.
    
    This builder provides a more intuitive interface for creating complex
    search queries, especially useful for coding agents that need to
    construct queries step by step.
    """
    
    def __init__(self):
        """Initialize a new search query builder."""
        self._query = SearchQuery()
    
    def add_property_and(self, property_name: str, operator: Union[str, SearchOperator], value: Any) -> "SearchQueryBuilder":
        """
        Add a property search condition with AND logic.
        
        Args:
            property_name: The property to search on
            operator: The search operator (string or SearchOperator enum)
            value: The value to search for
            
        Returns:
            Self for method chaining
        """
        if isinstance(operator, str):
            operator = SearchOperator(operator)
        
        self._query.add_property_and(property_name, operator, value)
        return self
    
    def add_property_or(self, property_name: str, operator: Union[str, SearchOperator], value: Any) -> "SearchQueryBuilder":
        """
        Add a property search condition with OR logic.
        
        Args:
            property_name: The property to search on
            operator: The search operator (string or SearchOperator enum)
            value: The value to search for
            
        Returns:
            Self for method chaining
        """
        if isinstance(operator, str):
            operator = SearchOperator(operator)
        
        self._query.add_property_or(property_name, operator, value)
        return self
    
    def content_search(self, text: str) -> "SearchQueryBuilder":
        """
        Set the full-text content search.
        
        Args:
            text: The text to search for in document content
            
        Returns:
            Self for method chaining
        """
        self._query.content_search = text
        return self
    
    def date_range(self, start_date: Union[str, datetime], end_date: Union[str, datetime], 
                   format_str: str = "%m/%d/%Y %I:%M %p") -> "SearchQueryBuilder":
        """
        Set a date range filter.
        
        Args:
            start_date: Start date (string or datetime)
            end_date: End date (string or datetime)
            format_str: Date format string (if using string dates)
            
        Returns:
            Self for method chaining
        """
        self._query.date_range = DateRange(start_date, end_date, format_str)
        return self
    
    def public_library(self, include: bool = True) -> "SearchQueryBuilder":
        """
        Configure public library inclusion.
        
        Args:
            include: Whether to include public library
            
        Returns:
            Self for method chaining
        """
        self._query.options.public_library = include
        return self
    
    def legacy_library(self, include: bool = True) -> "SearchQueryBuilder":
        """
        Configure legacy library inclusion.
        
        Args:
            include: Whether to include legacy library
            
        Returns:
            Self for method chaining
        """
        self._query.options.legacy_library = include
        return self
    
    def added_today(self, filter_today: bool = True) -> "SearchQueryBuilder":
        """
        Filter for items added today.
        
        Args:
            filter_today: Whether to filter for items added today
            
        Returns:
            Self for method chaining
        """
        self._query.options.added_today = filter_today
        return self
    
    def added_this_month(self, filter_month: bool = True) -> "SearchQueryBuilder":
        """
        Filter for items added this month.
        
        Args:
            filter_month: Whether to filter for items added this month
            
        Returns:
            Self for method chaining
        """
        self._query.options.added_this_month = filter_month
        return self
    
    def within_folder(self, path: str, include_subfolders: bool = False) -> "SearchQueryBuilder":
        """
        Configure within folder search.
        
        Args:
            path: Folder path to search within
            include_subfolders: Whether to include subfolders
            
        Returns:
            Self for method chaining
        """
        self._query.options.within_folder_enable = True
        self._query.options.within_folder_path = path
        self._query.options.within_folder_insubfolder = include_subfolders
        return self
    
    def sort_by(self, field: Union[str, SortField], order: Union[str, SortOrder] = SortOrder.DESCENDING) -> "SearchQueryBuilder":
        """
        Set sort field and order.
        
        Args:
            field: Sort field (string or SortField enum)
            order: Sort order (string or SortOrder enum)
            
        Returns:
            Self for method chaining
        """
        if isinstance(field, str):
            field = SortField(field)
        if isinstance(order, str):
            order = SortOrder(order)
        
        self._query.options.sort_field = field
        self._query.options.sort_order = order
        return self
    
    # Convenience methods for common search patterns
    
    def nureg_documents(self) -> "SearchQueryBuilder":
        """Filter for NUREG documents."""
        return self.add_property_and("DocumentType", SearchOperator.ENDS_WITH, "NUREG")
    
    def part_21_correspondence(self) -> "SearchQueryBuilder":
        """Filter for Part 21 correspondence."""
        return self.add_property_and("DocumentType", SearchOperator.EQUALS, "Part 21 Correspondence")
    
    def inspection_reports(self) -> "SearchQueryBuilder":
        """Filter for inspection reports."""
        return (self.add_property_and("DocumentType", SearchOperator.CONTAINS, "inspection report")
                .add_property_and("DocketNumber", SearchOperator.STARTS_WITH, "05000"))
    
    def by_author(self, author_name: str) -> "SearchQueryBuilder":
        """Filter by author name."""
        return self.add_property_and("AuthorName", SearchOperator.STARTS_WITH, author_name)
    
    def by_docket(self, docket_number: str) -> "SearchQueryBuilder":
        """Filter by docket number."""
        return self.add_property_and("DocketNumber", SearchOperator.EQUALS, docket_number)
    
    def by_document_type(self, doc_type: Union[str, DocumentType]) -> "SearchQueryBuilder":
        """Filter by document type."""
        if isinstance(doc_type, DocumentType):
            doc_type = doc_type.value
        return self.add_property_and("DocumentType", SearchOperator.EQUALS, doc_type)
    
    def by_subject(self, subject: str) -> "SearchQueryBuilder":
        """Filter by subject."""
        return self.add_property_and("Subject", SearchOperator.CONTAINS, subject)
    
    def build(self) -> SearchQuery:
        """
        Build and return the final search query.
        
        Returns:
            The constructed SearchQuery object
        """
        return self._query
    
    def to_dict(self) -> dict:
        """
        Convert the query to a dictionary format for debugging.
        
        Returns:
            Dictionary representation of the query
        """
        return {
            "properties_and": [prop.to_tuple() for prop in self._query.properties_and],
            "properties_or": [prop.to_tuple() for prop in self._query.properties_or],
            "content_search": self._query.content_search,
            "date_range": self._query.date_range.to_tuple() if self._query.date_range else None,
            "options": {
                "public_library": self._query.options.public_library,
                "legacy_library": self._query.options.legacy_library,
                "added_today": self._query.options.added_today,
                "added_this_month": self._query.options.added_this_month,
                "within_folder_enable": self._query.options.within_folder_enable,
                "within_folder_insubfolder": self._query.options.within_folder_insubfolder,
                "within_folder_path": self._query.options.within_folder_path,
                "sort_field": self._query.options.sort_field.value,
                "sort_order": self._query.options.sort_order.value,
            }
        }


# Factory functions for common query patterns
def nureg_search() -> SearchQueryBuilder:
    """Create a builder for NUREG document searches."""
    return SearchQueryBuilder().nureg_documents()


def part21_search() -> SearchQueryBuilder:
    """Create a builder for Part 21 correspondence searches."""
    return SearchQueryBuilder().part_21_correspondence()


def inspection_report_search() -> SearchQueryBuilder:
    """Create a builder for inspection report searches."""
    return SearchQueryBuilder().inspection_reports()


def author_search(author_name: str) -> SearchQueryBuilder:
    """Create a builder for author-based searches."""
    return SearchQueryBuilder().by_author(author_name)


def docket_search(docket_number: str) -> SearchQueryBuilder:
    """Create a builder for docket-based searches."""
    return SearchQueryBuilder().by_docket(docket_number)

