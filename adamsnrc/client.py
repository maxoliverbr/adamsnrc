"""
ADAMS API Client class for better state management and configuration.

This module provides a client class that encapsulates the ADAMS API functionality
and provides a more object-oriented interface for coding agents.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .main import (
    content_search,
    advanced_search,
    part21_search_content,
    part21_search_advanced,
    operating_reactor_ir_search_content,
    operating_reactor_ir_search_advanced,
    SearchResult,
    ADAMSError,
    ADAMSRequestError,
    ADAMSValidationError,
    ADAMSParseError,
)
from .types import (
    SearchQuery,
    PropertySearch,
    DateRange,
    SearchOptions,
    SearchOperator,
    SortField,
    SortOrder,
    DocumentType,
    PropertyTuple,
    DateRangeTuple,
)
from .builder import SearchQueryBuilder
from .utils import build_date_range, calculate_result_stats, group_results_by_field


class ADAMSClient:
    """
    Client class for interacting with the ADAMS API.
    
    This class provides a more object-oriented interface to the ADAMS API,
    with built-in configuration management, caching, and convenience methods
    that make it easier for coding agents to work with the API.
    """
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 timeout: Optional[int] = None,
                 max_retries: Optional[int] = None,
                 log_level: Optional[str] = None):
        """
        Initialize the ADAMS client.
        
        Args:
            base_url: Custom base URL for the ADAMS API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._log_level = log_level
        
        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if log_level:
            self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Cache for recent search results
        self._cache: Dict[str, SearchResult] = {}
        self._cache_size = 100
        
        # Statistics tracking
        self._search_count = 0
        self._error_count = 0
        self._last_search_time: Optional[datetime] = None
    
    def search(self, query: SearchQuery) -> SearchResult:
        """
        Execute a search using a SearchQuery object.
        
        Args:
            query: The SearchQuery object to execute
            
        Returns:
            SearchResult containing the search results
            
        Raises:
            ADAMSError: If the search fails
        """
        try:
            # Convert SearchQuery to API parameters
            properties_and = [prop.to_tuple() for prop in query.properties_and]
            properties_or = [prop.to_tuple() for prop in query.properties_or]
            date_range = query.date_range.to_tuple() if query.date_range else None
            
            # Determine which search function to use
            if query.date_range or query.options.legacy_library or query.options.added_today or query.options.added_this_month or query.options.within_folder_enable:
                # Use advanced search
                result = advanced_search(
                    properties_search_all=properties_and if properties_and else None,
                    properties_search_any=properties_or if properties_or else None,
                    public_library=query.options.public_library,
                    legacy_library=query.options.legacy_library,
                    added_today=query.options.added_today,
                    added_this_month=query.options.added_this_month,
                    within_folder_enable=query.options.within_folder_enable,
                    within_folder_insubfolder=query.options.within_folder_insubfolder,
                    within_folder_path=query.options.within_folder_path,
                    sort=query.options.sort_field.value,
                    order=query.options.sort_order.value,
                )
            else:
                # Use content search
                result = content_search(
                    properties_search=properties_and if properties_and else None,
                    properties_search_any=properties_or if properties_or else None,
                    single_content_search=query.content_search,
                    sort=query.options.sort_field.value,
                    order=query.options.sort_order.value,
                )
            
            # Update statistics
            self._search_count += 1
            self._last_search_time = datetime.now()
            
            # Cache the result
            cache_key = self._generate_cache_key(query)
            self._cache[cache_key] = result
            
            # Maintain cache size
            if len(self._cache) > self._cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            
            return result
            
        except ADAMSError:
            self._error_count += 1
            raise
        except Exception as e:
            self._error_count += 1
            raise ADAMSError(f"Unexpected error in search: {e}") from e
    
    def search_builder(self) -> SearchQueryBuilder:
        """
        Get a new SearchQueryBuilder instance.
        
        Returns:
            SearchQueryBuilder for constructing search queries
        """
        return SearchQueryBuilder()
    
    # Convenience methods for common search patterns
    
    def search_nureg(self, content: str = "", **kwargs) -> SearchResult:
        """
        Search for NUREG documents.
        
        Args:
            content: Content search text
            **kwargs: Additional search parameters
            
        Returns:
            SearchResult containing NUREG documents
        """
        builder = self.search_builder().nureg_documents()
        if content:
            builder.content_search(content)
        
        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
        
        return self.search(builder.build())
    
    def search_part21(self, content: str = "", **kwargs) -> SearchResult:
        """
        Search for Part 21 correspondence.
        
        Args:
            content: Content search text
            **kwargs: Additional search parameters
            
        Returns:
            SearchResult containing Part 21 documents
        """
        builder = self.search_builder().part_21_correspondence()
        if content:
            builder.content_search(content)
        
        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
        
        return self.search(builder.build())
    
    def search_inspection_reports(self, content: str = "", **kwargs) -> SearchResult:
        """
        Search for inspection reports.
        
        Args:
            content: Content search text
            **kwargs: Additional search parameters
            
        Returns:
            SearchResult containing inspection reports
        """
        builder = self.search_builder().inspection_reports()
        if content:
            builder.content_search(content)
        
        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
        
        return self.search(builder.build())
    
    def search_by_author(self, author: str, **kwargs) -> SearchResult:
        """
        Search for documents by author.
        
        Args:
            author: Author name to search for
            **kwargs: Additional search parameters
            
        Returns:
            SearchResult containing documents by the author
        """
        builder = self.search_builder().by_author(author)
        
        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
        
        return self.search(builder.build())
    
    def search_by_docket(self, docket: str, **kwargs) -> SearchResult:
        """
        Search for documents by docket number.
        
        Args:
            docket: Docket number to search for
            **kwargs: Additional search parameters
            
        Returns:
            SearchResult containing documents for the docket
        """
        builder = self.search_builder().by_docket(docket)
        
        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(builder, key):
                getattr(builder, key)(value)
        
        return self.search(builder.build())
    
    # Legacy method compatibility
    def content_search(self, *args, **kwargs) -> SearchResult:
        """Legacy content_search method for backward compatibility."""
        return content_search(*args, **kwargs)
    
    def advanced_search(self, *args, **kwargs) -> SearchResult:
        """Legacy advanced_search method for backward compatibility."""
        return advanced_search(*args, **kwargs)
    
    def part21_search_content(self, *args, **kwargs) -> SearchResult:
        """Legacy part21_search_content method for backward compatibility."""
        return part21_search_content(*args, **kwargs)
    
    def part21_search_advanced(self, *args, **kwargs) -> SearchResult:
        """Legacy part21_search_advanced method for backward compatibility."""
        return part21_search_advanced(*args, **kwargs)
    
    def operating_reactor_ir_search_content(self, *args, **kwargs) -> SearchResult:
        """Legacy operating_reactor_ir_search_content method for backward compatibility."""
        return operating_reactor_ir_search_content(*args, **kwargs)
    
    def operating_reactor_ir_search_advanced(self, *args, **kwargs) -> SearchResult:
        """Legacy operating_reactor_ir_search_advanced method for backward compatibility."""
        return operating_reactor_ir_search_advanced(*args, **kwargs)
    
    # Utility methods
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get client usage statistics.
        
        Returns:
            Dictionary containing usage statistics
        """
        return {
            "search_count": self._search_count,
            "error_count": self._error_count,
            "success_rate": (self._search_count - self._error_count) / max(self._search_count, 1),
            "cache_size": len(self._cache),
            "last_search_time": self._last_search_time.isoformat() if self._last_search_time else None,
        }
    
    def clear_cache(self) -> None:
        """Clear the search result cache."""
        self._cache.clear()
        self.logger.info("Search cache cleared")
    
    def set_cache_size(self, size: int) -> None:
        """
        Set the maximum cache size.
        
        Args:
            size: Maximum number of cached results
        """
        self._cache_size = size
        # Trim cache if necessary
        while len(self._cache) > self._cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """
        Generate a cache key for a search query.
        
        Args:
            query: The SearchQuery object
            
        Returns:
            String cache key
        """
        # Create a simple hash of the query parameters
        query_dict = query.to_dict()
        return str(hash(str(query_dict)))
    
    def batch_search(self, queries: List[SearchQuery]) -> List[SearchResult]:
        """
        Execute multiple searches in batch.
        
        Args:
            queries: List of SearchQuery objects to execute
            
        Returns:
            List of SearchResult objects
        """
        results = []
        for i, query in enumerate(queries):
            try:
                self.logger.info(f"Executing batch search {i+1}/{len(queries)}")
                result = self.search(query)
                results.append(result)
            except ADAMSError as e:
                self.logger.error(f"Batch search {i+1} failed: {e}")
                results.append(None)  # Use None to indicate failure
        
        return results
    
    def search_with_retry(self, query: SearchQuery, max_retries: int = 3) -> SearchResult:
        """
        Execute a search with automatic retry on failure.
        
        Args:
            query: The SearchQuery object to execute
            max_retries: Maximum number of retry attempts
            
        Returns:
            SearchResult containing the search results
            
        Raises:
            ADAMSError: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return self.search(query)
            except ADAMSRequestError as e:
                last_error = e
                if attempt < max_retries:
                    self.logger.warning(f"Search attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    break
            except ADAMSError as e:
                # Don't retry validation or parsing errors
                raise e
        
        raise last_error or ADAMSError("Search failed after all retry attempts")


# Factory function for creating clients
def create_client(**kwargs) -> ADAMSClient:
    """
    Create a new ADAMS client with the specified configuration.
    
    Args:
        **kwargs: Configuration parameters for the client
        
    Returns:
        Configured ADAMSClient instance
    """
    return ADAMSClient(**kwargs)


# Default client instance
_default_client: Optional[ADAMSClient] = None


def get_default_client() -> ADAMSClient:
    """
    Get the default client instance, creating it if necessary.
    
    Returns:
        Default ADAMSClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = ADAMSClient()
    return _default_client


def set_default_client(client: ADAMSClient) -> None:
    """
    Set the default client instance.
    
    Args:
        client: The ADAMSClient instance to use as default
    """
    global _default_client
    _default_client = client 