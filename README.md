# ADAMSNRC API Client

This code was created by ChatGPT and Cursor. On ChatGPT the pdf with the API documentation was uploaded and simple prompt sent: "create simple python code to interface each endpoint on adams library api".

With the code generated I switched to Cursor, set model to Any and started vibe coding.

The result after many interactions and minor code edits is this package. 

A robust Python client for the Nuclear Regulatory Commission's ADAMS (Agencywide Documents Access and Management System) API.

## Features

- **Type Safety**: Full type hints for better IDE support and code clarity
- **Error Handling**: Comprehensive exception handling with custom error types
- **Input Validation**: Robust validation of all input parameters
- **Retry Logic**: Automatic retry mechanism for network requests
- **Logging**: Configurable logging for debugging and monitoring
- **Configuration**: Environment-based configuration management
- **Utilities**: Helper functions for data processing and validation
- **Testing**: Comprehensive test suite

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from adamsnrc.main import content_search, advanced_search

# Simple content search
result = content_search(
    properties_search=[("DocumentType", "ends", "NUREG")],
    single_content_search="steam generator",
    sort="DocumentDate",
    order="DESC"
)

print(f"Found {result.count} documents")
for doc in result.results:
    print(f"- {doc.get('title', 'No title')}")

# Advanced search with date range
from datetime import datetime
from adamsnrc.utils import build_date_range

date_range = build_date_range(
    "01/01/2023 12:00 AM",
    "12/31/2023 11:59 PM"
)

result = advanced_search(
    properties_search_all=[("AuthorName", "starts", "Macfarlane")],
    date_range=date_range,
    sort="$title",
    order="ASC"
)
```

## Configuration

The client can be configured using environment variables:

```bash
# API Configuration
export ADAMS_BASE_URL="https://adams.nrc.gov/wba/services/search/advanced/nrc"
export ADAMS_TIMEOUT="60"
export ADAMS_MAX_RETRIES="3"
export ADAMS_RETRY_DELAY="1.0"

# Logging Configuration
export ADAMS_LOG_LEVEL="INFO"
```

## API Reference

### Main Functions

#### `content_search()`
Content search in the public library.

```python
def content_search(
    properties_search: Optional[List[Tuple[str, str, Any]]] = None,
    properties_search_any: Optional[List[Tuple[str, str, Any]]] = None,
    single_content_search: str = "",
    sort: str = "DocumentDate",
    order: str = "DESC"
) -> SearchResult
```

#### `advanced_search()`
Advanced search with additional options.

```python
def advanced_search(
    properties_search_all: Optional[List[Tuple[str, str, Any]]] = None,
    properties_search_any: Optional[List[Tuple[str, str, Any]]] = None,
    public_library: bool = True,
    legacy_library: bool = False,
    added_today: bool = False,
    added_this_month: bool = False,
    within_folder_enable: bool = False,
    within_folder_insubfolder: bool = False,
    within_folder_path: str = "",
    sort: str = "$title",
    order: str = "ASC"
) -> SearchResult
```

#### `part21_search_content()`
Search for Part 21 correspondence using content search.

#### `part21_search_advanced()`
Search for Part 21 correspondence using advanced search.

#### `operating_reactor_ir_search_content()`
Search for operating reactor inspection reports using content search.

#### `operating_reactor_ir_search_advanced()`
Search for operating reactor inspection reports using advanced search.

### Data Structures

#### `SearchResult`
Container for search results with metadata.

```python
@dataclass
class SearchResult:
    meta: Dict[str, str]      # Metadata (count, matches, etc.)
    results: List[Dict[str, str]]  # List of document results
    
    @property
    def count(self) -> int:   # Number of results as integer
    @property
    def matches(self) -> int: # Number of matches as integer
```

### Exception Types

- `ADAMSError`: Base exception for all ADAMS API errors
- `ADAMSRequestError`: Request-related errors (timeout, network issues)
- `ADAMSValidationError`: Input validation errors
- `ADAMSParseError`: XML parsing errors

### Utility Functions

#### Date and Time Utilities
```python
from adamsnrc.utils import build_date_range, validate_and_format_date

# Build date range
date_range = build_date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")

# Validate and format date
formatted_date = validate_and_format_date("01/15/2023 02:30 PM")
```

#### Text Processing
```python
from adamsnrc.utils import escape_special_chars, normalize_whitespace, truncate_text

# Escape special characters
escaped = escape_special_chars("test (with) [special] {chars}")

# Normalize whitespace
normalized = normalize_whitespace("  multiple    spaces  ")

# Truncate text
truncated = truncate_text("Very long text...", max_length=50)
```

#### Result Processing
```python
from adamsnrc.utils import (
    extract_metadata_from_result,
    filter_results_by_date,
    group_results_by_field,
    calculate_result_stats
)

# Extract metadata
metadata = extract_metadata_from_result(result_dict)

# Filter by date
filtered = filter_results_by_date(results, start_date, end_date)

# Group by field
grouped = group_results_by_field(results, "AuthorName")

# Calculate statistics
stats = calculate_result_stats(results)
```

## Examples

### Basic Search
```python
from adamsnrc.main import content_search

# Search for NUREG documents about steam generators
result = content_search(
    properties_search=[("DocumentType", "ends", "NUREG")],
    single_content_search="steam generator",
    sort="DocumentDate",
    order="DESC"
)

print(f"Found {result.count} NUREG documents about steam generators")
```

### Advanced Search with Date Range
```python
from adamsnrc.main import advanced_search
from adamsnrc.utils import build_date_range

# Search for documents by a specific author in a date range
date_range = build_date_range("01/01/2023 12:00 AM", "12/31/2023 11:59 PM")

result = advanced_search(
    properties_search_all=[
        ("AuthorName", "starts", "Macfarlane"),
        ("DocumentType", "starts", "Speech")
    ],
    date_range=date_range,
    sort="$title",
    order="ASC"
)
```

### Part 21 Search
```python
from adamsnrc.main import part21_search_content

# Search for Part 21 correspondence about safety valves
result = part21_search_content(
    extra_and=[("AuthorAffiliation", "infolder", "NRC/NRR")],
    text="safety valve",
    sort="$size",
    order="DESC"
)
```

### Result Processing
```python
from adamsnrc.utils import calculate_result_stats, group_results_by_field

# Get search results
result = content_search(properties_search=[("DocumentType", "ends", "NUREG")])

# Calculate statistics
stats = calculate_result_stats(result.results)
print(f"Total results: {stats['total_results']}")
print(f"Unique authors: {stats['unique_authors']}")
print(f"Average file size: {stats['average_size']} bytes")

# Group by author
grouped = group_results_by_field(result.results, "AuthorName")
for author, docs in grouped.items():
    print(f"{author}: {len(docs)} documents")
```

## Error Handling

```python
from adamsnrc.main import content_search, ADAMSError, ADAMSValidationError

try:
    result = content_search(
        properties_search=[("DocumentType", "ends", "NUREG")],
        order="INVALID"  # This will raise an error
    )
except ADAMSValidationError as e:
    print(f"Validation error: {e}")
except ADAMSError as e:
    print(f"ADAMS API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing

Run the test suite:

```bash
python -m pytest adamsnrc/test_main.py -v
```

Or run specific test classes:

```bash
python -m pytest adamsnrc/test_main.py::TestSearchFunctions -v
```

## Logging

The client uses Python's standard logging module. Configure logging level:

```python
import logging
logging.getLogger('adamsnrc').setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 2.0.0 (Refactored)
- Added comprehensive type hints
- Implemented robust error handling with custom exceptions
- Added input validation for all parameters
- Implemented retry logic for network requests
- Added configuration management
- Created utility functions for data processing
- Added comprehensive test suite
- Improved documentation and examples
- Added logging support
- Made the code more maintainable and robust 

## How to Build and Publish Your Package to PyPI

Your project is already well-prepared for PyPI distribution! Here's the complete process:

### 1. **Prerequisites Setup**

First, ensure you have the necessary tools and accounts:

```bash
# Install build tools
pip install build twine

# Create PyPI account at https://pypi.org/account/register/
# Create TestPyPI account at https://test.pypi.org/account/register/
```

### 2. **Configure PyPI Credentials**

Create a `~/.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 3. **Update Package Information**

Before publishing, you need to update the placeholder information in your configuration files:

**In `pyproject.toml`:**
```toml
authors = [
    {name = "Your Actual Name", email = "your.actual.email@example.com"}
]
maintainers = [
    {name = "Your Actual Name", email = "your.actual.email@example.com"}
]
```

**In `setup.py`:**
```python
author="Your Actual Name",
author_email="your.actual.email@example.com",
url="https://github.com/your-actual-username/adamsnrc",
```

**Update URLs in both files:**
- Replace `yourusername` with your actual GitHub username
- Update documentation URLs if you have them

### 4. **Build the Package**

```bash
# Clean previous builds (optional)
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build
```

This will create:
- `dist/adamsnrc-2.0.0.tar.gz` (source distribution)
- `dist/adamsnrc-2.0.0-py3-none-any.whl` (wheel distribution)

### 5. **Test on TestPyPI (Recommended)**

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ adamsnrc

# Test the package
python -c "import adamsnrc; print(adamsnrc.__version__)"
```

### 6. **Publish to PyPI**

```bash
# Upload to PyPI
twine upload dist/*

# Or upload specific files
twine upload dist/adamsnrc-2.0.0.tar.gz dist/adamsnrc-2.0.0-py3-none-any.whl
```

### 7. **Verify the Publication**

```bash
# Install from PyPI
pip install adamsnrc

# Test the package
python -c "import adamsnrc; print(adamsnrc.__version__)"
```

## Automated Publishing with GitHub Actions

Your project already has GitHub Actions configured! Here's how to use them:

### 1. **Set up GitHub Secrets**

1. Go to your repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Add `PYPI_API_TOKEN` with your PyPI API token

### 2. **Bump Version (Automated)**

Use the included version bumping script to automatically update all version numbers:

```bash
# Bump patch version (2.0.0 -> 2.0.1)
./bump.sh patch

# Bump minor version (2.0.0 -> 2.1.0)
./bump.sh minor

# Bump major version (2.0.0 -> 3.0.0)
./bump.sh major

# Dry run to see what would change
./bump.sh patch --dry-run

# Complete release workflow (bump + git + GitHub release)
./bump.sh patch --auto-git
```

The script automatically updates:
- `pyproject.toml`
- `setup.py`
- `adamsnrc/__init__.py`
- `CHANGELOG.md` (adds new version entry)

**With `--auto-git` flag, it also:**
- Commits all changes with descriptive message
- Pushes to main branch
- Creates and pushes git tag
- Creates GitHub release (if gh CLI is available)

### 3. **Create a Release (Manual)**

If you didn't use `--auto-git`, run these commands manually:

```bash
# Commit version changes
git add .
git commit -m "bump: version 2.0.0 -> 2.0.1"
git push origin main

# Create and push a tag
git tag v2.0.1
git push origin v2.0.1

# Create GitHub release (this triggers automatic publishing)
gh release create v2.0.1 --title "Version 2.0.1" --notes "Bug fixes and improvements"
```

**Or use the automated workflow:**
```bash
# Complete release workflow in one command
./bump.sh patch --auto-git
```

## Package Quality Checklist

Before publishing, ensure:

✅ **Configuration Files**: `pyproject.toml`, `setup.py`, `MANIFEST.in` are properly configured  
✅ **Documentation**: README.md is comprehensive and up-to-date  
✅ **Dependencies**: All required packages are listed in dependencies  
✅ **Version**: Version is consistent across all files  
✅ **License**: MIT license is included  
✅ **Tests**: Test suite passes  
✅ **Code Quality**: Ruff linting and formatting pass  

## Your Package is Ready!

Your package is already well-structured with:

- ✅ Modern `pyproject.toml` configuration
- ✅ Comprehensive `setup.py` 
- ✅ Proper `MANIFEST.in` for file inclusion
- ✅ Automated version bumping script (`bump.sh` and `bump_version.py`)
- ✅ Detailed `PUBLISHING.md` guide
- ✅ GitHub Actions workflows
- ✅ Built distributions in `dist/` directory
- ✅ Professional README.md
- ✅ Proper package structure

The main steps you need to take are:
1. Update the placeholder information (name, email, URLs)
2. Get PyPI API tokens
3. Configure `~/.pypirc`
4. Build and upload

Your package will be available at `https://pypi.org/project/adamsnrc/` once published! 