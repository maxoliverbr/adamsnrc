import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import quote_plus

import requests
from requests.exceptions import RequestException, Timeout

from .config import (
    BASE_URL,
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
    ERROR_MESSAGES,
    LOG_FORMAT,
    LOG_LEVEL,
    MAX_RETRIES,
    RETRY_DELAY,
    VALID_ORDERS,
    VALID_SORTS,
)

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Container for search results with metadata."""

    meta: dict[str, str]
    results: list[dict[str, str]]

    @property
    def count(self) -> int:
        """Return the count as an integer."""
        try:
            return int(self.meta.get("count", "0"))
        except (ValueError, TypeError):
            return 0

    @property
    def matches(self) -> int:
        """Return the matches as an integer."""
        try:
            return int(self.meta.get("matches", "0"))
        except (ValueError, TypeError):
            return 0


class ADAMSError(Exception):
    """Base exception for ADAMS API errors."""

    pass


class ADAMSRequestError(ADAMSError):
    """Exception raised for request-related errors."""

    pass


class ADAMSValidationError(ADAMSError):
    """Exception raised for validation errors."""

    pass


class ADAMSParseError(ADAMSError):
    """Exception raised for parsing errors."""

    pass


def validate_sort_order(order: str) -> None:
    """Validate sort order parameter."""
    if order not in VALID_ORDERS:
        raise ADAMSValidationError(
            ERROR_MESSAGES["invalid_sort_order"].format(
                order=order, valid_orders=VALID_ORDERS
            )
        )


def validate_sort_field(sort: str) -> None:
    """Validate sort field parameter."""
    if sort not in VALID_SORTS:
        logger.warning(f"Sort field '{sort}' not in known valid fields: {VALID_SORTS}")


def validate_property_tuple(prop_tuple: tuple) -> None:
    """Validate a property search tuple."""
    if not isinstance(prop_tuple, tuple) or len(prop_tuple) != 3:
        raise ADAMSValidationError(
            ERROR_MESSAGES["invalid_property_tuple"].format(tuple=prop_tuple)
        )

    prop, op, value = prop_tuple
    if not isinstance(prop, str) or not isinstance(op, str):
        raise ADAMSValidationError(
            f"Property and operator must be strings: {prop_tuple}"
        )


def validate_date_range(date_range: tuple[str, str]) -> None:
    """Validate date range tuple."""
    if not isinstance(date_range, tuple) or len(date_range) != 2:
        raise ADAMSValidationError(
            ERROR_MESSAGES["invalid_date_range"].format(date_range=date_range)
        )

    start_date, end_date = date_range
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        raise ADAMSValidationError("Date range values must be strings")


# ---------------------------
# Small helpers
# ---------------------------


def _kv(prop: str, op: str, value: Any) -> str:
    """Return one !(prop,op,value,'') item correctly URL-escaped."""
    try:
        # ADAMS expects + instead of spaces, so quote_plus.
        return f"!({prop},{op},{quote_plus(str(value))},'')"
    except Exception as e:
        raise ADAMSValidationError(
            f"Error formatting property tuple ({prop}, {op}, {value}): {e}"
        ) from e


def _join(items: list[str]) -> str:
    """Join items with commas."""
    return ",".join(str(item) for item in items)


def _wrap_list(items: list[str]) -> str:
    """Wrap items in !( ... ) list wrapper."""
    return f"!({_join(items)})" if items else "!()"


def _filters(public_library: bool = True, legacy_library: bool = False) -> str:
    """Generate filters string."""
    flags = []
    if public_library:
        flags.append("public-library:!t")
    else:
        flags.append("public-library:!f")
    if legacy_library:
        flags.append("legacy-library:!t")
    return f"filters:({_join(flags)})"


def _options(
    added_today: bool = False,
    added_this_month: bool = False,
    within_folder_enable: bool = False,
    within_folder_insubfolder: bool = False,
    within_folder_path: str = "",
) -> str:
    """Generate options string."""
    opts = []
    if added_today:
        opts.append("added-today:!t")
    if added_this_month:
        opts.append("added-this-month:!t")

    within = (
        f"within-folder:(enable:{'!t' if within_folder_enable else '!f'},"
        f"insubfolder:{'!t' if within_folder_insubfolder else '!f'},"
        f"path:'{quote_plus(within_folder_path)}')"
    )
    opts.append(within)

    return f"options:({_join(opts)})"


def _mode_sections(inner: str) -> str:
    """Wrap inner content in mode sections."""
    return f"(mode:sections,sections:({inner}))"


def _build_query(
    tab: str, sort: Optional[str] = None, order: Optional[str] = None, qn: str = "New"
) -> dict[str, str]:
    """Build query parameters."""
    params = {
        "tab": tab,
        "qn": qn,
    }
    if sort:
        validate_sort_field(sort)
        params["s"] = sort
    if order:
        validate_sort_order(order)
        params["so"] = order
    return params


def _xml_to_dict(xml_text: str) -> SearchResult:
    """Parse XML response and return structured data."""
    try:
        root = ET.fromstring(xml_text)
        results = []

        for res in root.findall(".//resultset/result"):
            d = {}
            for child in res:
                d[child.tag] = (child.text or "").strip()
            results.append(d)

        meta = {
            "count": (root.findtext("count") or "").strip(),
            "sort": (root.findtext("sort") or "").strip(),
            "sortorder": (root.findtext("sortorder") or "").strip(),
            "matches": (root.findtext("matches") or "").strip(),
        }

        return SearchResult(meta=meta, results=results)

    except ET.ParseError as e:
        raise ADAMSParseError(
            ERROR_MESSAGES["xml_parse_error"].format(error=str(e))
        ) from e
    except Exception as e:
        raise ADAMSParseError(f"Unexpected error parsing XML: {e}") from e


def _do_request(query: str, **params) -> SearchResult:
    """Make HTTP request with retry logic and error handling."""
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Making request (attempt {attempt + 1}/{MAX_RETRIES})")
            r = requests.get(
                BASE_URL,
                params={"q": query, **params},
                headers=DEFAULT_HEADERS,
                timeout=DEFAULT_TIMEOUT,
            )
            r.raise_for_status()
            return _xml_to_dict(r.text)

        except Timeout:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Request timeout, retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
                continue
            else:
                raise ADAMSRequestError(
                    ERROR_MESSAGES["request_timeout"].format(max_retries=MAX_RETRIES)
                ) from None

        except RequestException as e:
            raise ADAMSRequestError(
                ERROR_MESSAGES["request_failed"].format(error=str(e))
            ) from e

        except Exception as e:
            raise ADAMSRequestError(f"Unexpected error during request: {e}") from e


# ---------------------------
# Public API
# ---------------------------


def content_search(
    properties_search: Optional[list[tuple[str, str, Any]]] = None,
    properties_search_any: Optional[list[tuple[str, str, Any]]] = None,
    single_content_search: str = "",
    sort: str = "DocumentDate",
    order: str = "DESC",
) -> SearchResult:
    """
    Content Search (Public Library).

    Args:
        properties_search: List of tuples (prop, op, value) for AND conditions
        properties_search_any: List of tuples (prop, op, value) for OR conditions
        single_content_search: Full-text search string
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results

    Raises:
        ADAMSValidationError: If parameters are invalid
        ADAMSRequestError: If request fails
        ADAMSParseError: If response parsing fails
    """
    try:
        # Validate inputs
        if properties_search:
            for prop_tuple in properties_search:
                validate_property_tuple(prop_tuple)

        if properties_search_any:
            for prop_tuple in properties_search_any:
                validate_property_tuple(prop_tuple)

        validate_sort_order(order)
        validate_sort_field(sort)

        # Build query
        props_and = [_kv(*t) for t in (properties_search or [])]
        props_or = [_kv(*t) for t in (properties_search_any or [])]

        inner_parts = [
            _filters(public_library=True),
            f"properties_search:{_wrap_list(props_and)}",
            f"properties_search_any:{_wrap_list(props_or)}",
            f"single_content_search:'{quote_plus(single_content_search)}'",
        ]
        q = _mode_sections(",".join(inner_parts))

        params = _build_query("content-search-pars", sort, order)
        return _do_request(q, **params)

    except ADAMSError:
        raise
    except Exception as e:
        raise ADAMSError(f"Unexpected error in content_search: {e}") from e


def advanced_search(
    properties_search_all: Optional[list[tuple[str, str, Any]]] = None,
    properties_search_any: Optional[list[tuple[str, str, Any]]] = None,
    public_library: bool = True,
    legacy_library: bool = False,
    added_today: bool = False,
    added_this_month: bool = False,
    within_folder_enable: bool = False,
    within_folder_insubfolder: bool = False,
    within_folder_path: str = "",
    sort: str = "$title",
    order: str = "ASC",
) -> SearchResult:
    """
    Advanced Search (Public library and/or Legacy library + extra options).

    Args:
        properties_search_all: List of tuples (prop, op, value) for AND conditions
        properties_search_any: List of tuples (prop, op, value) for OR conditions
        public_library: Include public library
        legacy_library: Include legacy library
        added_today: Filter for items added today
        added_this_month: Filter for items added this month
        within_folder_enable: Enable within folder search
        within_folder_insubfolder: Include subfolders
        within_folder_path: Folder path to search within
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results

    Raises:
        ADAMSValidationError: If parameters are invalid
        ADAMSRequestError: If request fails
        ADAMSParseError: If response parsing fails
    """
    try:
        # Validate inputs
        if properties_search_all:
            for prop_tuple in properties_search_all:
                validate_property_tuple(prop_tuple)

        if properties_search_any:
            for prop_tuple in properties_search_any:
                validate_property_tuple(prop_tuple)

        validate_sort_order(order)
        validate_sort_field(sort)

        # Build query
        props_all = [_kv(*t) for t in (properties_search_all or [])]
        props_any = [_kv(*t) for t in (properties_search_any or [])]

        inner_parts = [
            _filters(public_library=public_library, legacy_library=legacy_library),
            _options(
                added_today=added_today,
                added_this_month=added_this_month,
                within_folder_enable=within_folder_enable,
                within_folder_insubfolder=within_folder_insubfolder,
                within_folder_path=within_folder_path,
            ),
            f"properties_search_all:{_wrap_list(props_all)}",
            f"properties_search_any:{_wrap_list(props_any)}",
        ]
        q = _mode_sections(",".join(inner_parts))

        params = _build_query("advanced-search-pars", sort, order)
        return _do_request(q, **params)

    except ADAMSError:
        raise
    except Exception as e:
        raise ADAMSError(f"Unexpected error in advanced_search: {e}") from e


def part21_search_content(
    extra_and: Optional[list[tuple[str, str, Any]]] = None,
    extra_or: Optional[list[tuple[str, str, Any]]] = None,
    text: str = "",
    sort: str = "$size",
    order: str = "DESC",
) -> SearchResult:
    """
    Part 21 via Content Search.

    Args:
        extra_and: Additional AND conditions
        extra_or: Additional OR conditions
        text: Full-text search string
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results
    """
    base = [("DocumentType", "ends", "Part 21 Correspondence")]
    return content_search(
        properties_search=(base + (extra_and or [])),
        properties_search_any=extra_or,
        single_content_search=text,
        sort=sort,
        order=order,
    )


def part21_search_advanced(
    extra_all: Optional[list[tuple[str, str, Any]]] = None,
    extra_any: Optional[list[tuple[str, str, Any]]] = None,
    date_range: Optional[tuple[str, str]] = None,
    sort: str = "$title",
    order: str = "ASC",
) -> SearchResult:
    """
    Part 21 via Advanced Search.

    Args:
        extra_all: Additional AND conditions
        extra_any: Additional OR conditions
        date_range: Tuple (start_date, end_date) for date filtering
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results
    """
    try:
        if date_range:
            validate_date_range(date_range)

        base = [("DocumentType", "eq", "Part 21 Correspondence")]
        props = base + (extra_all or [])

        if date_range:
            left, right = date_range
            left = quote_plus(left)
            right = quote_plus(right)
            props.append(
                ("PublishDatePARS", f"range,(left:'{left}',right:'{right}')", "")
            )

        # Handle the range syntax hack:
        formatted = []
        for p, op, v in props:
            if op.startswith("range,("):
                # already formatted, keep literal
                formatted.append(f"!({p},range,{op.split('range,', 1)[1]},'')")
            elif op.startswith("range,(left"):
                formatted.append(f"!({p},range,{op.split('range,', 1)[1]},'')")
            elif op.startswith("range"):
                # If someone passed like ("PublishDatePARS","range",(left,right)), ignore.
                raise ADAMSValidationError(
                    "Use date_range=... or hand-build the range tuple string."
                )
            else:
                formatted.append(_kv(p, op, v))

        any_props = [_kv(*t) for t in (extra_any or [])]

        return advanced_search(
            properties_search_all=None if not formatted else [],
            properties_search_any=any_props,
            sort=sort,
            order=order,
        )

    except ADAMSError:
        raise
    except Exception as e:
        raise ADAMSError(f"Unexpected error in part21_search_advanced: {e}") from e


def operating_reactor_ir_search_content(
    extra_and: Optional[list[tuple[str, str, Any]]] = None,
    extra_or: Optional[list[tuple[str, str, Any]]] = None,
    text: str = "",
    sort: str = "$size",
    order: str = "DESC",
) -> SearchResult:
    """
    Operating Reactor Inspection Reports via Content Search.

    Args:
        extra_and: Additional AND conditions
        extra_or: Additional OR conditions
        text: Full-text search string
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results
    """
    base = [
        ("DocumentType", "infolder", "inspection report"),
        ("DocketNumber", "infolder", "05000"),
    ]
    return content_search(
        properties_search=(base + (extra_and or [])),
        properties_search_any=extra_or,
        single_content_search=text,
        sort=sort,
        order=order,
    )


def operating_reactor_ir_search_advanced(
    extra_all: Optional[list[tuple[str, str, Any]]] = None,
    extra_any: Optional[list[tuple[str, str, Any]]] = None,
    date_range: Optional[tuple[str, str]] = None,
    sort: str = "$title",
    order: str = "ASC",
) -> SearchResult:
    """
    Operating Reactor Inspection Reports via Advanced Search.

    Args:
        extra_all: Additional AND conditions
        extra_any: Additional OR conditions
        date_range: Tuple (start_date, end_date) for date filtering
        sort: Sort field
        order: Sort order (ASC or DESC)

    Returns:
        SearchResult with metadata and results
    """
    try:
        if date_range:
            validate_date_range(date_range)

        base = [
            ("DocumentType", "starts", "inspection report"),
            ("DocketNumber", "starts", "05000"),
        ]
        props = base + (extra_all or [])

        formatted = []
        if date_range:
            left, right = date_range
            left = quote_plus(left)
            right = quote_plus(right)
            formatted.append(
                f"!(PublishDatePARS,range,(left:'{left}',right:'{right}'),'' )"
            )

        # append the normal ones
        formatted += [_kv(*t) for t in props]
        any_props = [_kv(*t) for t in (extra_any or [])]

        inner_parts = [
            _filters(public_library=True),
            _options(within_folder_enable=False),
            f"properties_search_all:!({_join(formatted)})",
            f"properties_search_any:{_wrap_list(any_props)}",
        ]
        q = _mode_sections(",".join(inner_parts))
        params = _build_query("advanced-search-pars", sort, order)
        return _do_request(q, **params)

    except Exception as e:
        raise ADAMSError(
            f"Unexpected error in operating_reactor_ir_search_advanced: {e}"
        ) from e


# ---------------------------
# Quick examples (commented)
# ---------------------------

if __name__ == "__main__":
    try:
        # 1) Simple content search
        result = content_search(
            properties_search=[("DocumentType", "ends", "NUREG")],
            single_content_search="steam generator",
            sort="DocumentDate",
            order="DESC",
        )
        print(f"Content search -> {result.count} results")

        # 2) Advanced search example
        result = advanced_search(
            properties_search_all=[
                ("AuthorName", "starts", "Macfarlane"),
                ("DocumentType", "starts", "Speech"),
            ],
            sort="$title",
            order="ASC",
        )
        print(f"Advanced search -> {result.count} results")

        # 3) Part 21 content search example
        result = part21_search_content(
            extra_and=[("AuthorAffiliation", "infolder", "NRC/NRR")],
            text="safety valve",
            sort="$size",
            order="DESC",
        )
        print(f"Part 21 (content) -> {result.count} results")

        # 4) Operating reactor inspection report content search
        result = operating_reactor_ir_search_content(
            extra_and=[("AuthorAffiliation", "infolder", "NRC/NRR")],
            text="safety valve",
            sort="$size",
            order="DESC",
        )
        print(f"OR IR (content) -> {result.count} results")

    except ADAMSError as e:
        print(f"ADAMS API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
