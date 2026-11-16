"""ADAMSNRC - a typed Python client for the NRC ADAMS API.

Everything else (``helpers``, ``utils``, ``abstractions``, ``cli``) is imported
from its submodule.
"""

__version__ = "2.0.14"

from .builder import SearchQueryBuilder
from .client import ADAMSClient, create_client, get_default_client, set_default_client
from .main import (
    ADAMSError,
    ADAMSParseError,
    ADAMSRequestError,
    ADAMSValidationError,
    SearchResult,
    advanced_search,
    content_search,
    operating_reactor_ir_search_advanced,
    operating_reactor_ir_search_content,
    part21_search_advanced,
    part21_search_content,
)
from .types import (
    DateRange,
    DocumentType,
    PropertySearch,
    SearchOperator,
    SortField,
    SortOrder,
)

__all__ = [
    "ADAMSClient",
    "ADAMSError",
    "ADAMSParseError",
    "ADAMSRequestError",
    "ADAMSValidationError",
    "DateRange",
    "DocumentType",
    "PropertySearch",
    "SearchOperator",
    "SearchQueryBuilder",
    "SearchResult",
    "SortField",
    "SortOrder",
    "advanced_search",
    "content_search",
    "create_client",
    "get_default_client",
    "operating_reactor_ir_search_advanced",
    "operating_reactor_ir_search_content",
    "part21_search_advanced",
    "part21_search_content",
    "set_default_client",
]
