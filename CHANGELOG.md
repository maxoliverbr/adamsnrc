# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.5] - 2025-07-24

### Added
- Ruff linting and formatting integration
- Automated version bumping script with Git integration
- GitHub Actions workflows for CI/CD

### Changed
- Migrated from black/flake8 to ruff for code quality
- Updated Python version requirements to 3.9+
- Improved exception handling with proper chaining

### Fixed
- Python version compatibility issues in CI
- Typing annotations using modern Python syntax
- Code formatting and linting issues

### Removed
- Deprecated typing imports (Dict, List, Tuple)
- Legacy black and flake8 configurations


## [2.0.4] - 2025-07-24

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [2.0.3] - 2025-07-24

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [2.0.2] - 2025-07-24

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [2.0.1] - 2025-07-24

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [Unreleased]

### Added
- Command-line interface (CLI) for easy usage
- GitHub Actions workflows for CI/CD
- Comprehensive test suite
- Type hints throughout the codebase
- Robust error handling with custom exceptions
- Retry logic for network requests
- Configuration management via environment variables
- Utility functions for data processing
- Documentation and examples

### Changed
- Refactored entire codebase for better maintainability
- Improved error messages and validation
- Enhanced logging capabilities
- Better code organization and modularity

### Fixed
- Import issues after package rename
- Test failures and edge cases
- Documentation inconsistencies

## [2.0.0] - 2024-01-XX

### Added
- **Complete refactoring** of the ADAMS API client
- **Type safety** with comprehensive type hints
- **Custom exception hierarchy** for better error handling
- **Input validation** for all parameters
- **Retry logic** for network requests with configurable settings
- **Logging system** for debugging and monitoring
- **Configuration management** via environment variables
- **Utility functions** for date handling, text processing, and result analysis
- **Comprehensive test suite** with high coverage
- **Command-line interface** for easy usage
- **Modern packaging** with pyproject.toml and setup.py
- **GitHub Actions** for continuous integration and deployment
- **Documentation** with examples and API reference

### Changed
- **Package name** from `adams` to `adamsnrc`
- **API structure** with better data encapsulation using dataclasses
- **Error handling** with specific exception types
- **Code organization** with separate modules for different concerns
- **Documentation** with comprehensive examples and guides

### Removed
- Legacy error handling patterns
- Unstructured code organization
- Manual configuration management

## [1.0.0] - 2023-XX-XX

### Added
- Initial release of ADAMS API client
- Basic search functionality
- Support for content and advanced searches
- Part 21 and operating reactor inspection report searches
- XML response parsing
- Basic error handling

---

## Version History

- **2.0.0**: Complete refactoring with modern Python practices
- **1.0.0**: Initial release with basic functionality

## Migration Guide

### From v1.x to v2.0.0

The package has been completely refactored. Here are the key changes:

1. **Package name change**: `adams` → `adamsnrc`
2. **Import changes**:
   ```python
   # Old
   from adams.main import content_search
   
   # New
   from adamsnrc.main import content_search
   ```

3. **Return type changes**:
   ```python
   # Old
   meta, results = content_search(...)
   
   # New
   result = content_search(...)
   count = result.count
   documents = result.results
   ```

4. **Error handling**:
   ```python
   # Old
   try:
       result = content_search(...)
   except Exception as e:
       print(f"Error: {e}")
   
   # New
   try:
       result = content_search(...)
   except ADAMSValidationError as e:
       print(f"Validation error: {e}")
   except ADAMSRequestError as e:
       print(f"Request error: {e}")
   ```

5. **Configuration**:
   ```python
   # Old: Hardcoded values
   # New: Environment variables
   export ADAMS_BASE_URL="https://adams.nrc.gov/wba/services/search/advanced/nrc"
   export ADAMS_TIMEOUT="60"
   export ADAMS_MAX_RETRIES="3"
   ```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project. 