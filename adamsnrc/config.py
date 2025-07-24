"""
Configuration settings for the ADAMS API client.
"""

import os
from typing import Any

# API Configuration
BASE_URL = os.getenv(
    "ADAMS_BASE_URL", "https://adams.nrc.gov/wba/services/search/advanced/nrc"
)
DEFAULT_TIMEOUT = int(os.getenv("ADAMS_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("ADAMS_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("ADAMS_RETRY_DELAY", "1.0"))

# Logging Configuration
LOG_LEVEL = os.getenv("ADAMS_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Validation Configuration
VALID_ORDERS = {"ASC", "DESC"}
VALID_SORTS = {
    "DocumentDate",
    "$title",
    "$size",
    "AuthorName",
    "DocumentType",
    "PublishDatePARS",
    "DocketNumber",
    "AccessionNumber",
    "Subject",
}

# Search Configuration
DEFAULT_SORT = "DocumentDate"
DEFAULT_ORDER = "DESC"
DEFAULT_TAB = "content-search-pars"
DEFAULT_QN = "New"

# Request Headers
DEFAULT_HEADERS = {
    "User-Agent": "ADAMSNRC-Python-Client/1.0",
    "Accept": "application/xml, text/xml, */*",
    "Accept-Encoding": "gzip, deflate",
}

# Error Messages
ERROR_MESSAGES = {
    "invalid_sort_order": "Invalid sort order: {order}. Must be one of {valid_orders}",
    "invalid_property_tuple": "Property tuple must be (prop, op, value), got: {tuple}",
    "invalid_date_range": "Date range must be (start_date, end_date), got: {date_range}",
    "request_timeout": "Request timed out after {max_retries} attempts",
    "request_failed": "Request failed: {error}",
    "xml_parse_error": "Failed to parse XML response: {error}",
    "validation_error": "Validation error: {error}",
}


def get_config() -> dict[str, Any]:
    """Get all configuration settings as a dictionary."""
    return {
        "base_url": BASE_URL,
        "default_timeout": DEFAULT_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "log_level": LOG_LEVEL,
        "log_format": LOG_FORMAT,
        "valid_orders": VALID_ORDERS,
        "valid_sorts": VALID_SORTS,
        "default_sort": DEFAULT_SORT,
        "default_order": DEFAULT_ORDER,
        "default_tab": DEFAULT_TAB,
        "default_qn": DEFAULT_QN,
        "default_headers": DEFAULT_HEADERS,
        "error_messages": ERROR_MESSAGES,
    }
