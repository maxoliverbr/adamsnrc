#!/bin/bash
# Build and publish script wrapper for ADAMSNRC package
# Usage: ./publish.sh [--test] [--production] [--dry-run] [--help]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ADAMSNRC Package Publisher${NC}"
echo "=================================="

# Show usage if no arguments provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./publish.sh [--test] [--production] [--dry-run] [--help]"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./publish.sh --test                    # Publish to TestPyPI only"
    echo "  ./publish.sh --production              # Publish to PyPI only"
    echo "  ./publish.sh --test --production       # Publish to both"
    echo "  ./publish.sh --dry-run                 # Show what would be done"
    echo "  ./publish.sh --test --dry-run          # Test workflow without publishing"
    echo ""
    echo -e "${YELLOW}Prerequisites:${NC}"
    echo "  1. Install build tools: pip install build twine"
    echo "  2. Configure PyPI credentials in ~/.pypirc or environment variables"
    echo "  3. Run from project root directory"
    echo ""
    exit 1
fi

# Check if Python script exists
if [ ! -f "build_and_publish.py" ]; then
    echo -e "${RED}❌ Error: build_and_publish.py not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if required tools are installed
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    echo "Please install Python 3 first"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ Error: pip not found${NC}"
    echo "Please install pip first"
    exit 1
fi

# Check if build tools are available
if ! python3 -c "import build" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: build package not found${NC}"
    echo "Installing build tools..."
    if ! pip install --user build twine 2>/dev/null; then
        echo -e "${RED}❌ Failed to install with --user flag${NC}"
        echo "Try one of these options:"
        echo "  1. pip install --break-system-packages build twine"
        echo "  2. Create a virtual environment: python3 -m venv venv && source venv/bin/activate"
        echo "  3. Use system packages: sudo apt install python3-build python3-twine"
        exit 1
    fi
fi

if ! python3 -c "import twine" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: twine package not found${NC}"
    echo "Installing twine..."
    if ! pip install --user twine 2>/dev/null; then
        echo -e "${RED}❌ Failed to install twine${NC}"
        echo "Try: pip install --break-system-packages twine"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Run the Python script with all arguments
python3 build_and_publish.py "$@"

# Show additional helpful information
if [ $? -eq 0 ] && [[ "$*" != *"--dry-run"* ]]; then
    echo ""
    echo -e "${GREEN}🎉 Publishing completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "  • Check your package on PyPI: https://pypi.org/project/adamsnrc/"
    echo "  • Test installation: pip install adamsnrc"
    echo "  • Update documentation if needed"
    echo ""
    echo -e "${BLUE}💡 For future releases:${NC}"
    echo "  • Use ./bump.sh for version management"
    echo "  • Use ./publish.sh for publishing"
    echo "  • Consider using GitHub Actions for automated publishing"
fi
