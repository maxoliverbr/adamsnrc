# Publishing ADAMSNRC to PyPI

This guide explains how to publish the ADAMSNRC package to the Python Package Index (PyPI).

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. **API Token**: Generate an API token on PyPI for secure uploads

## Setup

### 1. Install Publishing Tools

```bash
pip install build twine
```

### 2. Configure PyPI Credentials

Create a `~/.pypirc` file:

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

## Publishing Process

### 1. Update Version

Before publishing, update the version in:
- `setup.py`
- `pyproject.toml`
- `adamsnrc/__init__.py`
- `CHANGELOG.md`

### 2. Build the Package

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/adamsnrc-X.X.X.tar.gz` (source distribution)
- `dist/adamsnrc-X.X.X-py3-none-any.whl` (wheel distribution)

### 3. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ adamsnrc
```

### 4. Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

### 5. Verify Installation

```bash
# Install from PyPI
pip install adamsnrc

# Test the package
python -c "import adamsnrc; print(adamsnrc.__version__)"
```

## GitHub Actions Publishing

The repository includes GitHub Actions workflows for automated publishing:

### CI Workflow (`.github/workflows/ci.yml`)
- Runs on push to main/develop and pull requests
- Tests on multiple Python versions
- Runs linting and type checking
- Builds the package

### Publish Workflow (`.github/workflows/publish.yml`)
- Runs when a GitHub release is published
- Automatically builds and publishes to PyPI
- Uses `PYPI_API_TOKEN` secret

### Setup GitHub Secrets

1. Go to your repository settings
2. Navigate to Secrets and variables → Actions
3. Add `PYPI_API_TOKEN` with your PyPI API token

## Version Management

### Semantic Versioning

Follow [semantic versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. **Update version** in all files
2. **Update CHANGELOG.md** with new changes
3. **Commit changes** with conventional commit message
4. **Create GitHub release** with tag (e.g., `v2.0.0`)
5. **GitHub Actions** automatically publishes to PyPI

### Example Release

```bash
# Update version to 2.1.0
sed -i 's/version = "2.0.0"/version = "2.1.0"/' pyproject.toml
sed -i 's/version="2.0.0"/version="2.1.0"/' setup.py
sed -i 's/__version__ = "2.0.0"/__version__ = "2.1.0"/' adamsnrc/__init__.py

# Commit and tag
git add .
git commit -m "feat: release version 2.1.0"
git tag v2.1.0
git push origin main --tags

# Create GitHub release (manually or via GitHub CLI)
gh release create v2.1.0 --title "Version 2.1.0" --notes "New features and improvements"
```

## Package Information

### PyPI Page
Once published, the package will be available at:
https://pypi.org/project/adamsnrc/

### Installation
```bash
pip install adamsnrc
```

### Usage
```python
from adamsnrc import content_search, SearchResult

# Search for documents
result = content_search(
    properties_search=[("DocumentType", "ends", "NUREG")],
    single_content_search="steam generator"
)

print(f"Found {result.count} documents")
```

### CLI Usage
```bash
# Install with CLI
pip install adamsnrc

# Use CLI
adamsnrc search --type content --doc-type "NUREG" --text "steam generator"
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify API token is correct
   - Check `~/.pypirc` configuration

2. **Package Already Exists**
   - Version must be unique
   - Update version number

3. **Build Errors**
   - Check all required files are present
   - Verify `MANIFEST.in` includes necessary files

4. **Import Errors After Installation**
   - Check package structure
   - Verify `__init__.py` exports are correct

### Support

For issues with publishing:
- Check [PyPI Help](https://pypi.org/help/)
- Review [Python Packaging User Guide](https://packaging.python.org/)
- Open an issue in the repository

## Security

### API Token Security
- Never commit API tokens to version control
- Use environment variables or `~/.pypirc`
- Rotate tokens regularly

### Package Verification
- Verify package contents before upload
- Test installation in clean environment
- Check package metadata

## Maintenance

### Regular Tasks
- Monitor package downloads and issues
- Update dependencies as needed
- Maintain documentation
- Respond to user feedback

### Deprecation
- Follow deprecation policy
- Provide migration guides
- Maintain backward compatibility when possible 