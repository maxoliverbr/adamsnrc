"""
Type definitions and data models for the ADAMS API client.

This module provides comprehensive type hints, enums, and data models
that help coding agents understand the API structure and provide better
autocomplete and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class SortOrder(str, Enum):
    """Valid sort orders for ADAMS API queries."""
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class SortField(str, Enum):
    """Valid sort fields for ADAMS API queries."""
    DOCUMENT_DATE = "DocumentDate"
    TITLE = "$title"
    SIZE = "$size"
    AUTHOR_NAME = "AuthorName"
    DOCUMENT_TYPE = "DocumentType"
    PUBLISH_DATE = "PublishDatePARS"
    DOCKET_NUMBER = "DocketNumber"
    ACCESSION_NUMBER = "AccessionNumber"
    SUBJECT = "Subject"


class SearchOperator(str, Enum):
    """Valid search operators for property searches."""
    EQUALS = "eq"
    STARTS_WITH = "starts"
    ENDS_WITH = "ends"
    CONTAINS = "contains"
    IN_FOLDER = "infolder"
    RANGE = "range"


class DocumentType(str, Enum):
    """Common document types in ADAMS."""
    NUREG = "NUREG"
    PART_21 = "Part 21 Correspondence"
    INSPECTION_REPORT = "inspection report"
    SPEECH = "Speech"
    LETTER = "Letter"
    MEMORANDUM = "Memorandum"
    ORDER = "Order"
    LICENSE = "License"


class LibraryType(str, Enum):
    """Available library types."""
    PUBLIC = "public"
    LEGACY = "legacy"


@dataclass
class PropertySearch:
    """Represents a property search condition."""
    property_name: str
    operator: SearchOperator
    value: Any
    
    def to_tuple(self) -> tuple[str, str, Any]:
        """Convert to tuple format for API calls."""
        return (self.property_name, self.operator.value, self.value)


@dataclass
class DateRange:
    """Represents a date range for filtering."""
    start_date: Union[str, datetime]
    end_date: Union[str, datetime]
    format_str: str = "%m/%d/%Y %I:%M %p"
    
    def to_tuple(self) -> tuple[str, str]:
        """Convert to tuple format for API calls."""
        from .utils import build_date_range
        return build_date_range(self.start_date, self.end_date, self.format_str)


@dataclass
class SearchOptions:
    """Configuration options for search queries."""
    public_library: bool = True
    legacy_library: bool = False
    added_today: bool = False
    added_this_month: bool = False
    within_folder_enable: bool = False
    within_folder_insubfolder: bool = False
    within_folder_path: str = ""
    sort_field: SortField = SortField.DOCUMENT_DATE
    sort_order: SortOrder = SortOrder.DESCENDING


@dataclass
class SearchQuery:
    """Represents a complete search query."""
    properties_and: List[PropertySearch] = field(default_factory=list)
    properties_or: List[PropertySearch] = field(default_factory=list)
    content_search: str = ""
    date_range: Optional[DateRange] = None
    options: SearchOptions = field(default_factory=SearchOptions)
    
    def add_property_and(self, prop: str, op: SearchOperator, value: Any) -> None:
        """Add a property search with AND logic."""
        self.properties_and.append(PropertySearch(prop, op, value))
    
    def add_property_or(self, prop: str, op: SearchOperator, value: Any) -> None:
        """Add a property search with OR logic."""
        self.properties_or.append(PropertySearch(prop, op, value))
    
    def to_dict(self) -> dict:
        """
        Convert the search query to a dictionary format.
        
        Returns:
            dict: Dictionary representation of the search query
        """
        return {
            "properties_and": [prop.to_tuple() for prop in self.properties_and],
            "properties_or": [prop.to_tuple() for prop in self.properties_or],
            "content_search": self.content_search,
            "date_range": self.date_range.to_tuple() if self.date_range else None,
            "options": {
                "public_library": self.options.public_library,
                "legacy_library": self.options.legacy_library,
                "added_today": self.options.added_today,
                "added_this_month": self.options.added_this_month,
                "within_folder_enable": self.options.within_folder_enable,
                "within_folder_insubfolder": self.options.within_folder_insubfolder,
                "within_folder_path": self.options.within_folder_path,
                "sort_field": self.options.sort_field.value,
                "sort_order": self.options.sort_order.value,
            }
        }


@dataclass
class DocumentMetadata:
    """Structured metadata for a document."""
    accession_number: Optional[str] = None
    title: Optional[str] = None
    document_type: Optional[str] = None
    author_name: Optional[str] = None
    author_affiliation: Optional[str] = None
    docket_number: Optional[str] = None
    subject: Optional[str] = None
    document_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None
    size: Optional[int] = None
    file_name: Optional[str] = None
    url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "DocumentMetadata":
        """Create DocumentMetadata from API response dictionary."""
        from .utils import extract_metadata_from_result
        metadata = extract_metadata_from_result(data)
        
        return cls(
            accession_number=data.get("AccessionNumber"),
            title=data.get("Title"),
            document_type=data.get("DocumentType"),
            author_name=data.get("AuthorName"),
            author_affiliation=data.get("AuthorAffiliation"),
            docket_number=data.get("DocketNumber"),
            subject=data.get("Subject"),
            document_date=metadata.get("DocumentDate_parsed"),
            publish_date=metadata.get("PublishDate_parsed"),
            size=metadata.get("Size_parsed", 0),
            file_name=data.get("FileName"),
            url=data.get("URL"),
        )


@dataclass
class SearchStatistics:
    """Statistics about search results."""
    total_results: int
    unique_authors: int
    unique_document_types: int
    date_range: Optional[Dict[str, datetime]] = None
    average_size: float = 0.0
    size_distribution: Dict[str, int] = field(default_factory=dict)
    document_type_distribution: Dict[str, int] = field(default_factory=dict)
    author_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Enhanced search result with structured data."""
    metadata: Dict[str, str]
    results: List[Dict[str, str]]
    documents: List[DocumentMetadata] = field(default_factory=list)
    statistics: Optional[SearchStatistics] = None
    
    def __post_init__(self) -> None:
        """Initialize structured data after creation."""
        # Convert raw results to DocumentMetadata objects
        self.documents = [DocumentMetadata.from_dict(result) for result in self.results]
        
        # Calculate statistics
        from .utils import calculate_result_stats
        stats_data = calculate_result_stats(self.results)
        self.statistics = SearchStatistics(
            total_results=stats_data["total_results"],
            unique_authors=stats_data["unique_authors"],
            unique_document_types=stats_data["unique_document_types"],
            date_range=stats_data["date_range"],
            average_size=stats_data["average_size"],
        )
    
    @property
    def count(self) -> int:
        """Return the count as an integer."""
        try:
            return int(self.metadata.get("count", "0"))
        except (ValueError, TypeError):
            return 0

    @property
    def matches(self) -> int:
        """Return the matches as an integer."""
        try:
            return int(self.metadata.get("matches", "0"))
        except (ValueError, TypeError):
            return 0


# Type aliases for better code readability
PropertyTuple = tuple[str, str, Any]
PropertyList = List[PropertyTuple]
DateRangeTuple = tuple[str, str]
SearchResultDict = Dict[str, str]
SearchResultList = List[SearchResultDict]


# Common search patterns for coding agents
COMMON_SEARCH_PATTERNS = {
    "nureg_documents": {
        "description": "Search for NUREG documents",
        "properties": [PropertySearch("DocumentType", SearchOperator.ENDS_WITH, "NUREG")],
        "example": "content_search(properties_search=[('DocumentType', 'ends', 'NUREG')])"
    },
    "part_21_correspondence": {
        "description": "Search for Part 21 correspondence",
        "properties": [PropertySearch("DocumentType", SearchOperator.EQUALS, "Part 21 Correspondence")],
        "example": "part21_search_content()"
    },
    "inspection_reports": {
        "description": "Search for inspection reports",
        "properties": [
            PropertySearch("DocumentType", SearchOperator.CONTAINS, "inspection report"),
            PropertySearch("DocketNumber", SearchOperator.STARTS_WITH, "05000")
        ],
        "example": "operating_reactor_ir_search_content()"
    },
    "by_author": {
        "description": "Search by specific author",
        "properties": [PropertySearch("AuthorName", SearchOperator.STARTS_WITH, "")],
        "example": "content_search(properties_search=[('AuthorName', 'starts', 'Macfarlane')])"
    },
    "by_docket": {
        "description": "Search by docket number",
        "properties": [PropertySearch("DocketNumber", SearchOperator.EQUALS, "")],
        "example": "content_search(properties_search=[('DocketNumber', 'eq', '05000282')])"
    }
}


# API field mappings for better autocomplete
API_FIELDS = {
    "document_metadata": {
        "AccessionNumber": "Unique identifier for the document",
        "Title": "Document title",
        "DocumentType": "Type of document (NUREG, Letter, etc.)",
        "AuthorName": "Name of the document author",
        "AuthorAffiliation": "Author's organizational affiliation",
        "DocketNumber": "NRC docket number",
        "Subject": "Document subject",
        "DocumentDate": "Date the document was created",
        "PublishDatePARS": "Date the document was published",
        "Size": "File size in bytes",
        "FileName": "Original filename",
        "URL": "Direct link to the document"
    },
    "search_operators": {
        "eq": "Equals (exact match)",
        "starts": "Starts with",
        "ends": "Ends with", 
        "contains": "Contains (substring match)",
        "infolder": "In folder (path-based search)",
        "range": "Range (for dates and numbers)"
    },
    "sort_fields": {
        "DocumentDate": "Sort by document creation date",
        "$title": "Sort by document title",
        "$size": "Sort by file size",
        "AuthorName": "Sort by author name",
        "DocumentType": "Sort by document type",
        "PublishDatePARS": "Sort by publication date",
        "DocketNumber": "Sort by docket number",
        "AccessionNumber": "Sort by accession number",
        "Subject": "Sort by subject"
    }
} 