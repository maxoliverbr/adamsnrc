"""
Helpers that search ADAMS and return ``{title: AccessionNumber}`` maps.

Duplicate titles are disambiguated as ``"Title (ML123)"`` instead of dropped.
"""

import logging
from typing import Dict, Optional

from .builder import SearchQueryBuilder
from .client import ADAMSClient, get_default_client
from .main import ADAMSError
from .types import SearchOperator, SortField, SortOrder

logger = logging.getLogger(__name__)


def _title_map(
    search_string: str,
    client: Optional[ADAMSClient],
    max_results: int,
    build,
    lenient: bool,
) -> Dict[str, str]:
    """Run ``build(builder)`` and map result titles to accession numbers.

    lenient: accept the content-search title fields and synthesise a title for
    untitled documents; otherwise rows need both ``Title`` and an id.
    """
    if not search_string or not search_string.strip():
        raise ValueError("search_string cannot be empty or None")
    client = client or get_default_client()

    try:
        builder = SearchQueryBuilder()
        build(builder)
        builder.sort_by(SortField.TITLE, SortOrder.ASCENDING)
        result = client.search_with_retry(builder.build(), max_retries=3)

        title_id_map: Dict[str, str] = {}
        for doc in result.results:
            if len(title_id_map) >= max_results:
                logger.warning(f"Reached max_results limit of {max_results}, truncating results")
                break
            doc_id = doc.get("AccessionNumber", "").strip()
            if lenient:
                title = (
                    doc.get("DocumentTitle") or doc.get("Title") or doc.get("title")
                    or f"Document {doc_id or 'Unknown'}"
                ).strip()
            else:
                title = doc.get("Title", "").strip()
            if not (doc_id and title):
                logger.debug(f"Skipping row without id/title: {list(doc)}")
                continue
            key = f"{title} ({doc_id})" if title in title_id_map else title
            title_id_map[key] = doc_id
        return title_id_map

    except ADAMSError:
        raise
    except Exception as e:
        raise ADAMSError(f"Unexpected error searching for '{search_string}': {e}") from e


def search_documents_by_title(
    search_string: str, client: Optional[ADAMSClient] = None, max_results: int = 100
) -> Dict[str, str]:
    """Documents whose title contains ``search_string``."""
    return _title_map(
        search_string, client, max_results,
        lambda b: b.add_property_and("Title", SearchOperator.CONTAINS, search_string.strip()),
        lenient=True,
    )


def search_documents_by_title_exact(
    search_string: str, client: Optional[ADAMSClient] = None, max_results: int = 100
) -> Dict[str, str]:
    """Documents whose title starts with ``search_string``."""
    return _title_map(
        search_string, client, max_results,
        lambda b: b.add_property_and("Title", SearchOperator.STARTS_WITH, search_string.strip()),
        lenient=False,
    )


def search_documents_by_title_and_type(
    search_string: str,
    document_type: str,
    client: Optional[ADAMSClient] = None,
    max_results: int = 100,
) -> Dict[str, str]:
    """Documents of ``document_type`` whose title contains ``search_string``."""
    if not document_type or not document_type.strip():
        raise ValueError("document_type cannot be empty or None")

    def build(b):
        b.add_property_and("Title", SearchOperator.CONTAINS, search_string.strip())
        b.add_property_and("DocumentType", SearchOperator.CONTAINS, document_type.strip())

    return _title_map(search_string, client, max_results, build, lenient=False)


def search_documents_by_content(
    search_string: str, client: Optional[ADAMSClient] = None, max_results: int = 100
) -> Dict[str, str]:
    """Documents that mention ``search_string`` anywhere in their text."""
    return _title_map(
        search_string, client, max_results,
        lambda b: b.content_search(search_string.strip()),
        lenient=True,
    )


def search_nureg_by_title(search_string, client=None, max_results=100):
    return search_documents_by_title_and_type(search_string, "NUREG", client, max_results)


def search_letters_by_title(search_string, client=None, max_results=100):
    return search_documents_by_title_and_type(search_string, "Letter", client, max_results)


def search_reports_by_title(search_string, client=None, max_results=100):
    return search_documents_by_title_and_type(search_string, "Report", client, max_results)
