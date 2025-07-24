#!/usr/bin/env python3
"""
Command-line interface for ADAMSNRC.
"""

import argparse
import json
import sys

from .main import (
    ADAMSError,
    ADAMSValidationError,
    advanced_search,
    content_search,
    operating_reactor_ir_search_advanced,
    operating_reactor_ir_search_content,
    part21_search_advanced,
    part21_search_content,
)
from .utils import build_date_range, calculate_result_stats


def format_output(results: list[dict[str, str]], format_type: str = "table") -> str:
    """Format search results for output."""
    if format_type == "json":
        return json.dumps(results, indent=2)
    elif format_type == "csv":
        if not results:
            return ""

        # Get all unique keys
        all_keys = set()
        for result in results:
            all_keys.update(result.keys())

        # Create CSV header
        keys_list = sorted(all_keys)
        csv_lines = [",".join(f'"{k}"' for k in keys_list)]

        # Add data rows
        for result in results:
            row = [f'"{result.get(k, "")}"' for k in keys_list]
            csv_lines.append(",".join(row))

        return "\n".join(csv_lines)
    else:  # table format
        if not results:
            return "No results found."

        # Get all unique keys
        all_keys = set()
        for result in results:
            all_keys.update(result.keys())

        keys_list = sorted(all_keys)

        # Create table header
        table_lines = ["| " + " | ".join(keys_list) + " |"]
        table_lines.append("|" + "|".join("-" * (len(k) + 2) for k in keys_list) + "|")

        # Add data rows
        for result in results:
            row = [str(result.get(k, "")).replace("|", "\\|") for k in keys_list]
            table_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(table_lines)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="ADAMSNRC - Nuclear Regulatory Commission ADAMS API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for NUREG documents about steam generators
  adamsnrc search --type content --doc-type "NUREG" --text "steam generator"

  # Advanced search with date range
  adamsnrc search --type advanced --author "Macfarlane" --date-start "01/01/2023" --date-end "12/31/2023"

  # Part 21 search
  adamsnrc search --type part21 --text "safety valve"

  # Operating reactor inspection reports
  adamsnrc search --type reactor-ir --text "inspection"

  # Output as JSON
  adamsnrc search --type content --doc-type "NUREG" --output json

  # Show statistics
  adamsnrc search --type content --doc-type "NUREG" --stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search ADAMS documents")
    search_parser.add_argument(
        "--type",
        "-t",
        choices=[
            "content",
            "advanced",
            "part21",
            "part21-advanced",
            "reactor-ir",
            "reactor-ir-advanced",
        ],
        default="content",
        help="Search type (default: content)",
    )
    search_parser.add_argument("--doc-type", "-d", help="Document type filter")
    search_parser.add_argument("--text", "-q", help="Full-text search query")
    search_parser.add_argument("--author", "-a", help="Author name filter")
    search_parser.add_argument(
        "--date-start", help="Start date (MM/DD/YYYY HH:MM AM/PM)"
    )
    search_parser.add_argument("--date-end", help="End date (MM/DD/YYYY HH:MM AM/PM)")
    search_parser.add_argument(
        "--sort",
        "-s",
        default="DocumentDate",
        help="Sort field (default: DocumentDate)",
    )
    search_parser.add_argument(
        "--order",
        "-o",
        choices=["ASC", "DESC"],
        default="DESC",
        help="Sort order (default: DESC)",
    )
    search_parser.add_argument(
        "--output",
        "-f",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    search_parser.add_argument(
        "--stats", action="store_true", help="Show result statistics"
    )
    search_parser.add_argument(
        "--limit", "-l", type=int, help="Limit number of results"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Build search parameters
        properties_search = []
        if args.doc_type:
            properties_search.append(("DocumentType", "ends", args.doc_type))
        if args.author:
            properties_search.append(("AuthorName", "starts", args.author))

        # Build date range if provided
        date_range = None
        if args.date_start and args.date_end:
            date_range = build_date_range(args.date_start, args.date_end)

        # Execute search based on type
        if args.type == "content":
            result = content_search(
                properties_search=properties_search if properties_search else None,
                single_content_search=args.text or "",
                sort=args.sort,
                order=args.order,
            )
        elif args.type == "advanced":
            result = advanced_search(
                properties_search_all=properties_search if properties_search else None,
                date_range=date_range,
                sort=args.sort,
                order=args.order,
            )
        elif args.type == "part21":
            result = part21_search_content(
                extra_and=properties_search if properties_search else None,
                text=args.text or "",
                sort=args.sort,
                order=args.order,
            )
        elif args.type == "part21-advanced":
            result = part21_search_advanced(
                extra_all=properties_search if properties_search else None,
                date_range=date_range,
                sort=args.sort,
                order=args.order,
            )
        elif args.type == "reactor-ir":
            result = operating_reactor_ir_search_content(
                extra_and=properties_search if properties_search else None,
                text=args.text or "",
                sort=args.sort,
                order=args.order,
            )
        elif args.type == "reactor-ir-advanced":
            result = operating_reactor_ir_search_advanced(
                extra_all=properties_search if properties_search else None,
                date_range=date_range,
                sort=args.sort,
                order=args.order,
            )
        else:
            print(f"Unknown search type: {args.type}")
            return 1

        # Limit results if requested
        results = result.results
        if args.limit and len(results) > args.limit:
            results = results[: args.limit]

        # Show statistics if requested
        if args.stats:
            stats = calculate_result_stats(results)
            print("\n📊 Search Statistics:")
            print(f"   Total results: {stats['total_results']}")
            print(f"   Unique authors: {stats['unique_authors']}")
            print(f"   Unique document types: {stats['unique_document_types']}")
            if stats["date_range"]:
                print(
                    f"   Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}"
                )
            if stats["average_size"] > 0:
                print(f"   Average file size: {stats['average_size']:.0f} bytes")
            print()

        # Show results
        print(f"🔍 Found {len(results)} documents")
        print(f"📄 Total matches: {result.matches}")
        print()

        if results:
            formatted_output = format_output(results, args.output)
            print(formatted_output)
        else:
            print("No documents found matching your criteria.")

        return 0

    except ADAMSValidationError as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        return 1
    except ADAMSError as e:
        print(f"❌ ADAMS API error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n⏹️  Search interrupted by user.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
