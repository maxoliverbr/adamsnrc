"""
Utility functions for the ADAMS API client.
"""

import re
from datetime import date, datetime
from typing import Any, Optional, Union


def sanitize_string(value: Any) -> str:
    """Sanitize a value to a safe string representation."""
    if value is None:
        return ""
    return str(value).strip()


def validate_and_format_date(
    date_str: str, format_str: str = "%m/%d/%Y %I:%M %p"
) -> str:
    """
    Validate and format a date string.

    Args:
        date_str: Date string to validate and format
        format_str: Expected format of the date string

    Returns:
        Formatted date string

    Raises:
        ValueError: If date string is invalid
    """
    try:
        parsed_date = datetime.strptime(date_str, format_str)
        return parsed_date.strftime(format_str)
    except ValueError as e:
        raise ValueError(
            f"Invalid date format. Expected {format_str}, got: {date_str}"
        ) from e


def build_date_range(
    start_date: Union[str, date, datetime],
    end_date: Union[str, date, datetime],
    format_str: str = "%m/%d/%Y %I:%M %p",
) -> tuple[str, str]:
    """
    Build a properly formatted date range tuple.

    Args:
        start_date: Start date (string, date, or datetime object)
        end_date: End date (string, date, or datetime object)
        format_str: Format string for date output

    Returns:
        Tuple of (start_date_str, end_date_str)
    """

    def format_date(d: Union[str, date, datetime]) -> str:
        if isinstance(d, str):
            return validate_and_format_date(d, format_str)
        elif isinstance(d, (date, datetime)):
            if isinstance(d, date):
                d = datetime.combine(d, datetime.min.time())
            return d.strftime(format_str)
        else:
            raise ValueError(f"Invalid date type: {type(d)}")

    return format_date(start_date), format_date(end_date)


def escape_special_chars(text: str) -> str:
    """Escape special characters that might cause issues in search queries."""
    # Characters that might need escaping in ADAMS queries
    special_chars = ["(", ")", "[", "]", "{", "}", "\\", "^", "$", "*", "+", "?", "|"]
    escaped_text = text
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text (replace multiple spaces with single space)."""
    return re.sub(r"\s+", " ", text).strip()


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to maximum length, preserving word boundaries."""
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.8:  # Only truncate at space if it's not too far back
        truncated = truncated[:last_space]

    return truncated + "..."


def validate_docket_number(docket: str) -> bool:
    """
    Validate NRC docket number format.

    Args:
        docket: Docket number to validate

    Returns:
        True if valid, False otherwise
    """
    # NRC docket numbers typically follow pattern: 05000XXX or similar
    pattern = r"^\d{5,8}$"
    return bool(re.match(pattern, docket))


def format_docket_number(docket: str) -> str:
    """
    Format docket number to standard format.

    Args:
        docket: Raw docket number

    Returns:
        Formatted docket number
    """
    # Remove any non-digit characters
    digits_only = re.sub(r"\D", "", docket)

    # Pad with zeros if needed
    if len(digits_only) < 5:
        digits_only = digits_only.zfill(5)

    return digits_only


def extract_metadata_from_result(result: dict[str, str]) -> dict[str, Any]:
    """
    Extract and parse metadata from a search result.

    Args:
        result: Raw result dictionary

    Returns:
        Parsed metadata dictionary
    """
    metadata = {}

    # Extract common fields
    for key, value in result.items():
        if key.lower() in ["documentdate", "publishdate", "createdate"]:
            try:
                # Try to parse date
                metadata[f"{key}_parsed"] = datetime.strptime(
                    value, "%m/%d/%Y %I:%M %p"
                )
            except (ValueError, TypeError):
                metadata[f"{key}_parsed"] = None
        elif key.lower() in ["size", "filesize"]:
            try:
                metadata[f"{key}_parsed"] = int(value)
            except (ValueError, TypeError):
                metadata[f"{key}_parsed"] = 0
        else:
            metadata[key] = value

    return metadata


def filter_results_by_date(
    results: list[dict[str, str]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    date_field: str = "DocumentDate",
) -> list[dict[str, str]]:
    """
    Filter search results by date range.

    Args:
        results: List of result dictionaries
        start_date: Start date for filtering
        end_date: End date for filtering
        date_field: Field name containing the date

    Returns:
        Filtered list of results
    """
    if not start_date and not end_date:
        return results

    filtered_results = []

    for result in results:
        date_str = result.get(date_field, "")
        if not date_str:
            continue

        try:
            result_date = datetime.strptime(date_str, "%m/%d/%Y %I:%M %p")

            # Apply filters
            if start_date and result_date < start_date:
                continue
            if end_date and result_date > end_date:
                continue

            filtered_results.append(result)

        except ValueError:
            # Skip results with invalid dates
            continue

    return filtered_results


def group_results_by_field(
    results: list[dict[str, str]], field: str
) -> dict[str, list[dict[str, str]]]:
    """
    Group search results by a specific field.

    Args:
        results: List of result dictionaries
        field: Field name to group by

    Returns:
        Dictionary with field values as keys and lists of results as values
    """
    grouped = {}

    for result in results:
        value = result.get(field, "Unknown")
        if value not in grouped:
            grouped[value] = []
        grouped[value].append(result)

    return grouped


def calculate_result_stats(results: list[dict[str, str]]) -> dict[str, Any]:
    """
    Calculate statistics for search results.

    Args:
        results: List of result dictionaries

    Returns:
        Dictionary with calculated statistics
    """
    if not results:
        return {
            "total_results": 0,
            "unique_authors": 0,
            "unique_document_types": 0,
            "date_range": None,
            "average_size": 0,
        }

    # Extract unique values
    authors = set()
    doc_types = set()
    dates = []
    sizes = []

    for result in results:
        if "AuthorName" in result:
            authors.add(result["AuthorName"])
        if "DocumentType" in result:
            doc_types.add(result["DocumentType"])
        if "DocumentDate" in result:
            try:
                date_obj = datetime.strptime(
                    result["DocumentDate"], "%m/%d/%Y %I:%M %p"
                )
                dates.append(date_obj)
            except ValueError:
                pass
        if "Size" in result:
            try:
                sizes.append(int(result["Size"]))
            except ValueError:
                pass

    # Calculate statistics
    stats = {
        "total_results": len(results),
        "unique_authors": len(authors),
        "unique_document_types": len(doc_types),
        "date_range": None,
        "average_size": 0,
    }

    if dates:
        stats["date_range"] = {"earliest": min(dates), "latest": max(dates)}

    if sizes:
        stats["average_size"] = sum(sizes) / len(sizes)

    return stats
