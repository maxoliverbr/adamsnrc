# PyPI Publishing Setup Guide

This guide explains how to set up PyPI credentials and configure your environment for publishing the ADAMSNRC package.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. **API Tokens**: Generate API tokens for secure uploads

## Setup PyPI Credentials

### Option 1: Using ~/.pypirc file (Recommended)

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

### Option 2: Using Environment Variables

Set environment variables in your shell:

```bash
# For PyPI (production)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here

# For TestPyPI (testing)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-api-token-here
```

### Option 3: Using GitHub Secrets (for automated publishing)

Add these secrets to your GitHub repository:
- `PYPI_API_TOKEN`: Your PyPI API token
- `TESTPYPI_API_TOKEN`: Your TestPyPI API token (optional)

## Getting API Tokens

### 1. PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll down to "API tokens" section
3. Click "Add API token"
4. Give it a name (e.g., "adamsnrc-publishing")
5. Set scope to "Entire account" or "Specific project: adamsnrc"
6. Copy the token (it starts with `pypi-`)

### 2. TestPyPI API Token

1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/)
2. Scroll down to "API tokens" section
3. Click "Add API token"
4. Give it a name (e.g., "adamsnrc-testing")
5. Set scope to "Entire account" or "Specific project: adamsnrc"
6. Copy the token (it starts with `pypi-`)

## Testing Your Setup

### Test TestPyPI Credentials

```bash
# Test upload to TestPyPI
./publish.sh --test --dry-run
```

### Test PyPI Credentials

```bash
# Test upload to PyPI (be careful - this publishes to production!)
./publish.sh --production --dry-run
```

## Publishing Workflow

### 1. Test First (Recommended)

```bash
# Publish to TestPyPI first
./publish.sh --test

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ adamsnrc
```

### 2. Publish to Production

```bash
# Publish to PyPI
./publish.sh --production
```

### 3. Publish to Both

```bash
# Publish to both TestPyPI and PyPI
./publish.sh --test --production
```

## Automated Publishing with GitHub Actions

Your repository already has GitHub Actions configured for automated publishing:

### Setup GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TESTPYPI_API_TOKEN`: Your TestPyPI API token (optional)

### Automated Workflow

The automated workflow triggers when you create a GitHub release:

```bash
# 1. Update version and create release
./bump.sh patch --interactive --auto-git

# 2. GitHub Actions automatically:
#    - Builds the package
#    - Publishes to PyPI
#    - Handles all the complexity
```

## Security Best Practices

### API Token Security

- **Never commit API tokens** to version control
- **Use environment variables** or `~/.pypirc` file
- **Rotate tokens regularly**
- **Use project-specific tokens** when possible
- **Set appropriate scopes** for your tokens

### Package Verification

- **Always test on TestPyPI first**
- **Verify package contents** before upload
- **Test installation** in a clean environment
- **Check package metadata** is correct

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```
   ❌ Failed to publish to PyPI: HTTP 401: Invalid credentials
   ```
   - Verify API token is correct
   - Check token hasn't expired
   - Ensure token has correct scope

2. **Package Already Exists**
   ```
   ❌ Failed to publish to PyPI: HTTP 400: File already exists
   ```
   - Version must be unique
   - Update version number in `pyproject.toml`

3. **Build Errors**
   ```
   ❌ Build failed: ...
   ```
   - Check all required files are present
   - Verify `MANIFEST.in` includes necessary files
   - Run `python -m build` manually to debug

4. **Import Errors After Installation**
   ```
   ModuleNotFoundError: No module named 'adamsnrc'
   ```
   - Check package structure
   - Verify `__init__.py` exports are correct
   - Test in a clean virtual environment

### Getting Help

- **PyPI Help**: https://pypi.org/help/
- **Python Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **GitHub Issues**: Open an issue in the repository

## Quick Reference

### Commands

```bash
# Install build tools
pip install build twine

# Test publishing workflow
./publish.sh --test --dry-run

# Publish to TestPyPI
./publish.sh --test

# Publish to PyPI
./publish.sh --production

# Publish to both
./publish.sh --test --production
```

### File Locations

- **Configuration**: `~/.pypirc`
- **Package Config**: `pyproject.toml`
- **Build Script**: `build_and_publish.py`
- **Publish Script**: `publish.sh`
- **Version Bumper**: `bump.sh`

### URLs

- **PyPI**: https://pypi.org/project/adamsnrc/
- **TestPyPI**: https://test.pypi.org/project/adamsnrc/
- **GitHub**: https://github.com/maxoliverbr/adamsnrc
