#!/bin/bash
# Version bumping script wrapper
# Usage: ./bump.sh [major|minor|patch] [--dry-run]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ADAMSNRC Version Bumper${NC}"
echo "=================================="

# Show usage if no arguments provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./bump.sh [major|minor|patch] [--dry-run] [--auto-git]"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./bump.sh patch                    # Bump patch version"
    echo "  ./bump.sh minor --dry-run          # Preview minor version bump"
    echo "  ./bump.sh patch --auto-git         # Bump version + run git commands"
    echo "  ./bump.sh major --auto-git         # Complete release workflow"
    echo ""
    exit 1
fi

# Check if Python script exists
if [ ! -f "bump_version.py" ]; then
    echo -e "${RED}❌ Error: bump_version.py not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: pyproject.toml not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Run the Python script with all arguments
python bump_version.py "$@"

# If successful and not a dry run, show additional helpful commands
if [ $? -eq 0 ] && [[ "$*" != *"--dry-run"* ]] && [[ "$*" != *"--auto-git"* ]]; then
    echo ""
    echo -e "${GREEN}🎉 Version bump completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Quick commands for next steps:${NC}"
    echo "  git status                    # Check what changed"
    echo "  git diff                      # Review changes"
    echo "  git add .                     # Stage all changes"
    echo "  git commit -m 'bump version'  # Commit changes"
    echo "  git push origin main          # Push to remote"
    echo ""
    echo -e "${BLUE}💡 Tip: Use --auto-git to automate all git commands!${NC}"
fi 