"""
Helper functions for common ADAMS API operations.

This module provides convenient helper functions for frequently used
search patterns and operations with the ADAMS API.
"""

from typing import Dict, Optional
import logging

from .client import ADAMSClient, get_default_client
from .builder import SearchQueryBuilder
from .types import SearchOperator, SortField, SortOrder
from .main import ADAMSError


logger = logging.getLogger(__name__)


def search_documents_by_title(search_string: str, 
                            client: Optional[ADAMSClient] = None,
                            max_results: int = 100) -> Dict[str, str]:
    """
    Search for documents that contain a specific string in the title.
    
    This function searches across all document types in the ADAMS library
    for documents whose titles contain the specified search string.
    
    Args:
        search_string (str): The string to search for in document titles
        client (Optional[ADAMSClient], optional): ADAMS client instance to use.
            If None, uses the default client. Defaults to None.
        max_results (int, optional): Maximum number of results to process.
            Defaults to 100.
    
    Returns:
        Dict[str, str]: Dictionary mapping document titles to their AccessionNumbers
            (IDs). Format: {"Document Title": "AccessionNumber"}
    
    Raises:
        ADAMSError: If the search fails
        ValueError: If search_string is empty or None
    
    Example:
        >>> title_id_map = search_documents_by_title("steam generator")
        >>> for title, doc_id in title_id_map.items():
        ...     print(f"Title: {title}")
        ...     print(f"ID: {doc_id}")
        ...     print("---")
    """
    if not search_string or not search_string.strip():
        raise ValueError("search_string cannot be empty or None")
    
    # Use provided client or get default
    if client is None:
        client = get_default_client()
    
    try:
        # Build search query targeting title field
        # Note: This searches specifically in document titles, which may return fewer results
        # than content search. For broader results, use search_documents_by_content()
        builder = SearchQueryBuilder()
        builder.add_property_and("Title", SearchOperator.CONTAINS, search_string.strip())
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        
        # Execute search
        query = builder.build()
        result = client.search_with_retry(query, max_retries=3)
        
        logger.info(f"Found {result.count} documents with '{search_string}' in title")
        
        # Build title to ID mapping
        title_id_map = {}
        processed_count = 0
        
        for doc_data in result.results:
            if processed_count >= max_results:
                logger.warning(f"Reached max_results limit of {max_results}, truncating results")
                break
                
            # Content search results use "DocumentTitle" field instead of "Title"
            title = (doc_data.get("DocumentTitle", "") or 
                    doc_data.get("Title", "") or
                    doc_data.get("title", "") or 
                    f"Document {doc_data.get('AccessionNumber', 'Unknown')}").strip()
            
            doc_id = doc_data.get("AccessionNumber", "").strip()
            
            # Only include documents that have an ID (title might be generated)
            if doc_id:
                # Handle duplicate titles by appending the ID
                if title in title_id_map:
                    # If we already have this title, create a unique key
                    unique_title = f"{title} ({doc_id})"
                    title_id_map[unique_title] = doc_id
                    logger.debug(f"Duplicate title found, using unique key: {unique_title}")
                else:
                    title_id_map[title] = doc_id
                
                processed_count += 1
            else:
                logger.warning(f"Skipping document with missing AccessionNumber: id='{doc_id}', available_fields={list(doc_data.keys())}")
        
        logger.info(f"Processed {processed_count} documents, returning {len(title_id_map)} title-ID mappings")
        return title_id_map
        
    except ADAMSError as e:
        logger.error(f"Search failed for title containing '{search_string}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error searching for '{search_string}': {e}")
        raise ADAMSError(f"Unexpected error in search_documents_by_title: {e}") from e


def search_documents_by_title_exact(search_string: str,
                                  client: Optional[ADAMSClient] = None,
                                  max_results: int = 100) -> Dict[str, str]:
    """
    Search for documents with titles that start with a specific string.
    
    This function performs a more precise search for documents whose titles
    start with the specified search string, useful for finding specific
    document series or types.
    
    Args:
        search_string (str): The string that document titles should start with
        client (Optional[ADAMSClient], optional): ADAMS client instance to use.
            If None, uses the default client. Defaults to None.
        max_results (int, optional): Maximum number of results to process.
            Defaults to 100.
    
    Returns:
        Dict[str, str]: Dictionary mapping document titles to their AccessionNumbers
    
    Raises:
        ADAMSError: If the search fails
        ValueError: If search_string is empty or None
    
    Example:
        >>> title_id_map = search_documents_by_title_exact("NUREG")
        >>> for title, doc_id in title_id_map.items():
        ...     print(f"Title: {title}")
        ...     print(f"ID: {doc_id}")
    """
    if not search_string or not search_string.strip():
        raise ValueError("search_string cannot be empty or None")
    
    # Use provided client or get default
    if client is None:
        client = get_default_client()
    
    try:
        # Build search query targeting title field with "starts with" operator
        builder = SearchQueryBuilder()
        builder.add_property_and("Title", SearchOperator.STARTS_WITH, search_string.strip())
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        
        # Execute search
        query = builder.build()
        result = client.search_with_retry(query, max_retries=3)
        
        logger.info(f"Found {result.count} documents with titles starting with '{search_string}'")
        
        # Build title to ID mapping
        title_id_map = {}
        processed_count = 0
        
        for doc_data in result.results:
            if processed_count >= max_results:
                logger.warning(f"Reached max_results limit of {max_results}, truncating results")
                break
                
            title = doc_data.get("Title", "").strip()
            doc_id = doc_data.get("AccessionNumber", "").strip()
            
            # Only include documents that have both title and ID
            if title and doc_id:
                # Handle duplicate titles by appending the ID
                if title in title_id_map:
                    unique_title = f"{title} ({doc_id})"
                    title_id_map[unique_title] = doc_id
                    logger.debug(f"Duplicate title found, using unique key: {unique_title}")
                else:
                    title_id_map[title] = doc_id
                
                processed_count += 1
            else:
                logger.debug(f"Skipping document with missing title or ID: title='{title}', id='{doc_id}'")
        
        logger.info(f"Processed {processed_count} documents, returning {len(title_id_map)} title-ID mappings")
        return title_id_map
        
    except ADAMSError as e:
        logger.error(f"Search failed for titles starting with '{search_string}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error searching for titles starting with '{search_string}': {e}")
        raise ADAMSError(f"Unexpected error in search_documents_by_title_exact: {e}") from e


def search_documents_by_title_and_type(search_string: str,
                                     document_type: str,
                                     client: Optional[ADAMSClient] = None,
                                     max_results: int = 100) -> Dict[str, str]:
    """
    Search for documents of a specific type that contain a string in the title.
    
    This function combines document type filtering with title search to provide
    more targeted results.
    
    Args:
        search_string (str): The string to search for in document titles
        document_type (str): The type of document to filter by (e.g., "NUREG", "Letter")
        client (Optional[ADAMSClient], optional): ADAMS client instance to use.
            If None, uses the default client. Defaults to None.
        max_results (int, optional): Maximum number of results to process.
            Defaults to 100.
    
    Returns:
        Dict[str, str]: Dictionary mapping document titles to their AccessionNumbers
    
    Raises:
        ADAMSError: If the search fails
        ValueError: If search_string or document_type is empty or None
    
    Example:
        >>> title_id_map = search_documents_by_title_and_type("steam generator", "NUREG")
        >>> for title, doc_id in title_id_map.items():
        ...     print(f"NUREG Title: {title}")
        ...     print(f"ID: {doc_id}")
    """
    if not search_string or not search_string.strip():
        raise ValueError("search_string cannot be empty or None")
    
    if not document_type or not document_type.strip():
        raise ValueError("document_type cannot be empty or None")
    
    # Use provided client or get default
    if client is None:
        client = get_default_client()
    
    try:
        # Build search query with both title and document type filters
        builder = SearchQueryBuilder()
        builder.add_property_and("Title", SearchOperator.CONTAINS, search_string.strip())
        builder.add_property_and("DocumentType", SearchOperator.CONTAINS, document_type.strip())
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        
        # Execute search
        query = builder.build()
        result = client.search_with_retry(query, max_retries=3)
        
        logger.info(f"Found {result.count} {document_type} documents with '{search_string}' in title")
        
        # Build title to ID mapping
        title_id_map = {}
        processed_count = 0
        
        for doc_data in result.results:
            if processed_count >= max_results:
                logger.warning(f"Reached max_results limit of {max_results}, truncating results")
                break
                
            title = doc_data.get("Title", "").strip()
            doc_id = doc_data.get("AccessionNumber", "").strip()
            
            # Only include documents that have both title and ID
            if title and doc_id:
                # Handle duplicate titles by appending the ID
                if title in title_id_map:
                    unique_title = f"{title} ({doc_id})"
                    title_id_map[unique_title] = doc_id
                    logger.debug(f"Duplicate title found, using unique key: {unique_title}")
                else:
                    title_id_map[title] = doc_id
                
                processed_count += 1
            else:
                logger.debug(f"Skipping document with missing title or ID: title='{title}', id='{doc_id}'")
        
        logger.info(f"Processed {processed_count} documents, returning {len(title_id_map)} title-ID mappings")
        return title_id_map
        
    except ADAMSError as e:
        logger.error(f"Search failed for {document_type} documents with '{search_string}' in title: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error searching for {document_type} documents with '{search_string}': {e}")
        raise ADAMSError(f"Unexpected error in search_documents_by_title_and_type: {e}") from e


# Convenience functions for common document types
def search_nureg_by_title(search_string: str,
                         client: Optional[ADAMSClient] = None,
                         max_results: int = 100) -> Dict[str, str]:
    """
    Search for NUREG documents that contain a specific string in the title.
    
    Args:
        search_string (str): The string to search for in NUREG titles
        client (Optional[ADAMSClient], optional): ADAMS client instance to use
        max_results (int, optional): Maximum number of results to process
    
    Returns:
        Dict[str, str]: Dictionary mapping NUREG titles to their AccessionNumbers
    """
    return search_documents_by_title_and_type(search_string, "NUREG", client, max_results)


def search_letters_by_title(search_string: str,
                           client: Optional[ADAMSClient] = None,
                           max_results: int = 100) -> Dict[str, str]:
    """
    Search for Letter documents that contain a specific string in the title.
    
    Args:
        search_string (str): The string to search for in letter titles
        client (Optional[ADAMSClient], optional): ADAMS client instance to use
        max_results (int, optional): Maximum number of results to process
    
    Returns:
        Dict[str, str]: Dictionary mapping letter titles to their AccessionNumbers
    """
    return search_documents_by_title_and_type(search_string, "Letter", client, max_results)


def search_reports_by_title(search_string: str,
                           client: Optional[ADAMSClient] = None,
                           max_results: int = 100) -> Dict[str, str]:
    """
    Search for Report documents that contain a specific string in the title.
    
    Args:
        search_string (str): The string to search for in report titles
        client (Optional[ADAMSClient], optional): ADAMS client instance to use
        max_results (int, optional): Maximum number of results to process
    
    Returns:
        Dict[str, str]: Dictionary mapping report titles to their AccessionNumbers
    """
    return search_documents_by_title_and_type(search_string, "Report", client, max_results)


def search_documents_by_content(search_string: str, 
                               client: Optional[ADAMSClient] = None,
                               max_results: int = 100) -> Dict[str, str]:
    """
    Search for documents that contain a specific string in their content (not just title).
    
    This function performs a full-text content search, which is more likely to return
    results than title-only searches. Use this when you want to find documents that
    mention a topic anywhere in their content.
    
    Args:
        search_string (str): The string to search for in document content
        client (Optional[ADAMSClient], optional): ADAMS client instance to use.
            If None, uses the default client. Defaults to None.
        max_results (int, optional): Maximum number of results to process.
            Defaults to 100.
    
    Returns:
        Dict[str, str]: Dictionary mapping document titles to their AccessionNumbers
            (IDs). Format: {"Document Title": "AccessionNumber"}
    
    Raises:
        ADAMSError: If the search fails
        ValueError: If search_string is empty or None
    
    Example:
        >>> title_id_map = search_documents_by_content("steam generator")
        >>> for title, doc_id in title_id_map.items():
        ...     print(f"Title: {title}")
        ...     print(f"ID: {doc_id}")
        ...     print("---")
    """
    if not search_string or not search_string.strip():
        raise ValueError("search_string cannot be empty or None")
    
    # Use provided client or get default
    if client is None:
        client = get_default_client()
    
    try:
        # Build search query using content search (searches within document content)
        builder = SearchQueryBuilder()
        builder.content_search(search_string.strip())
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        
        # Execute search
        query = builder.build()
        result = client.search_with_retry(query, max_retries=3)
        
        logger.info(f"Found {result.count} documents with '{search_string}' in content")
        
        # Build title to ID mapping
        title_id_map = {}
        processed_count = 0
        
        for doc_data in result.results:
            if processed_count >= max_results:
                logger.warning(f"Reached max_results limit of {max_results}, truncating results")
                break
                
            # Content search results use "DocumentTitle" field instead of "Title"
            title = (doc_data.get("DocumentTitle", "") or 
                    doc_data.get("Title", "") or
                    doc_data.get("title", "") or 
                    f"Document {doc_data.get('AccessionNumber', 'Unknown')}").strip()
            
            doc_id = doc_data.get("AccessionNumber", "").strip()
            
            # Only include documents that have an ID (title might be generated)
            if doc_id:
                # Handle duplicate titles by appending the ID
                if title in title_id_map:
                    # If we already have this title, create a unique key
                    unique_title = f"{title} ({doc_id})"
                    title_id_map[unique_title] = doc_id
                    logger.debug(f"Duplicate title found, using unique key: {unique_title}")
                else:
                    title_id_map[title] = doc_id
                
                processed_count += 1
            else:
                logger.warning(f"Skipping document with missing AccessionNumber: id='{doc_id}', available_fields={list(doc_data.keys())}")
        
        logger.info(f"Processed {processed_count} documents, returning {len(title_id_map)} title-ID mappings")
        return title_id_map
        
    except ADAMSError as e:
        logger.error(f"Content search failed for '{search_string}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in content search for '{search_string}': {e}")
        raise ADAMSError(f"Unexpected error in search_documents_by_content: {e}") from e 