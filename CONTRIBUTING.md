# Contributing to ADAMSNRC

Thank you for your interest in contributing to ADAMSNRC! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/adamsnrc.git
   cd adamsnrc
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style (Black formatting)
- Add type hints to all functions
- Write docstrings for new functions
- Add tests for new functionality

### 3. Run Quality Checks

Before committing, run these checks:

```bash
# Format code
black adamsnrc/

# Lint code
flake8 adamsnrc/

# Type checking
mypy adamsnrc/

# Run tests
pytest

# Run tests with coverage
pytest --cov=adamsnrc --cov-report=html
```

### 4. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new search functionality"
git commit -m "fix: resolve timeout issue in requests"
git commit -m "docs: update API documentation"
```

### 5. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style

### Python Code

- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 88)
- Use type hints for all function parameters and return values
- Write docstrings for all public functions

### Example

```python
from typing import List, Optional, Dict, Any

def search_documents(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100
) -> List[Dict[str, str]]:
    """
    Search for documents in the ADAMS database.
    
    Args:
        query: Search query string
        filters: Optional filters to apply
        limit: Maximum number of results to return
        
    Returns:
        List of document dictionaries
        
    Raises:
        ADAMSValidationError: If query is invalid
        ADAMSRequestError: If API request fails
    """
    # Implementation here
    pass
```

### Testing

- Write unit tests for all new functionality
- Aim for at least 80% code coverage
- Use descriptive test names
- Mock external API calls

### Example Test

```python
import pytest
from unittest.mock import patch
from adamsnrc.main import content_search, ADAMSValidationError

def test_content_search_with_valid_query():
    """Test content search with valid query parameters."""
    with patch('adamsnrc.main._do_request') as mock_request:
        mock_request.return_value = SearchResult(
            meta={"count": "1", "matches": "1"},
            results=[{"title": "Test Document"}]
        )
        
        result = content_search(
            properties_search=[("DocumentType", "eq", "Test")],
            single_content_search="test query"
        )
        
        assert result.count == 1
        assert len(result.results) == 1
        mock_request.assert_called_once()

def test_content_search_with_invalid_sort_order():
    """Test content search raises error with invalid sort order."""
    with pytest.raises(ADAMSValidationError):
        content_search(
            properties_search=[("DocumentType", "eq", "Test")],
            order="INVALID"
        )
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
        TypeError: When wrong type is provided
        
    Example:
        >>> function_name("test", 42)
        True
    """
    pass
```

### README Updates

- Update README.md for new features
- Add usage examples
- Update installation instructions if needed

## Issue Reporting

When reporting issues, please include:

1. **Environment information**
   - Python version
   - Operating system
   - ADAMSNRC version

2. **Steps to reproduce**
   - Clear, step-by-step instructions
   - Minimal code example

3. **Expected vs actual behavior**
   - What you expected to happen
   - What actually happened

4. **Error messages**
   - Full error traceback
   - Any relevant log output

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Release Process

### Versioning

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Creating a Release

1. Update version in:
   - `setup.py`
   - `pyproject.toml`
   - `adamsnrc/__init__.py`

2. Update CHANGELOG.md

3. Create a GitHub release

4. Tag the release

## Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and general discussion
- **Email**: Contact maintainers directly for sensitive issues

## Code of Conduct

Please be respectful and inclusive in all interactions. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## License

By contributing to ADAMSNRC, you agree that your contributions will be licensed under the MIT License. 