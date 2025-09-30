#!/usr/bin/env python3
"""
Build and publish script for ADAMSNRC package.

This script handles building and publishing the package to both TestPyPI and PyPI.
It includes safety checks, validation, and interactive prompts.

Usage:
    python build_and_publish.py [--test] [--production] [--dry-run] [--help]

Examples:
    python build_and_publish.py --test                    # Publish to TestPyPI
    python build_and_publish.py --production              # Publish to PyPI
    python build_and_publish.py --test --production      # Publish to both
    python build_and_publish.py --dry-run                 # Show what would be done
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class PackagePublisher:
    """Handles building and publishing Python packages to PyPI."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"
        self.egg_info_dir = project_root / "adamsnrc.egg-info"

    def check_prerequisites(self) -> bool:
        """Check if all required tools and configurations are available."""
        print("🔍 Checking prerequisites...")
        
        # Check if we're in the right directory
        if not (self.project_root / "pyproject.toml").exists():
            print("❌ Error: pyproject.toml not found")
            print("   Please run this script from the project root directory")
            return False

        # Check if required tools are installed
        required_tools = ["python3", "pip"]
        for tool in required_tools:
            if not self._command_exists(tool):
                print(f"❌ Error: {tool} not found")
                print(f"   Please install {tool} first")
                return False

        # Check if build tools are available
        try:
            subprocess.run(["python3", "-c", "import build"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("❌ Error: build package not found")
            print("   Please install build tools:")
            print("   Option 1: pip install --user build twine")
            print("   Option 2: pip install --break-system-packages build twine")
            print("   Option 3: Create a virtual environment")
            return False

        # Check if twine is available
        try:
            subprocess.run(["python3", "-c", "import twine"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("❌ Error: twine package not found")
            print("   Please install twine:")
            print("   Option 1: pip install --user build twine")
            print("   Option 2: pip install --break-system-packages build twine")
            print("   Option 3: Create a virtual environment")
            return False

        print("✅ All prerequisites met")
        return True

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        try:
            subprocess.run([command, "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def clean_build_artifacts(self, dry_run: bool = False) -> None:
        """Clean previous build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        artifacts = [self.dist_dir, self.build_dir, self.egg_info_dir]
        
        for artifact in artifacts:
            if artifact.exists():
                if dry_run:
                    print(f"   [DRY RUN] Would remove: {artifact}")
                else:
                    shutil.rmtree(artifact)
                    print(f"   ✅ Removed: {artifact}")
            else:
                print(f"   ℹ️  Not found: {artifact}")

    def build_package(self, dry_run: bool = False) -> bool:
        """Build the package using python -m build."""
        print("🔨 Building package...")
        
        if dry_run:
            print("   [DRY RUN] Would run: python -m build")
            return True

        try:
            # Run the build command
            result = subprocess.run(
                ["python3", "-m", "build"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            print("   ✅ Package built successfully")
            
            # List built files
            if self.dist_dir.exists():
                files = list(self.dist_dir.glob("*"))
                print(f"   📦 Built files:")
                for file in files:
                    print(f"      - {file.name}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Build failed: {e.stderr}")
            return False

    def validate_package(self, dry_run: bool = False) -> bool:
        """Validate the built package using twine check."""
        print("🔍 Validating package...")
        
        if not self.dist_dir.exists():
            print("   ❌ No dist directory found. Run build first.")
            return False

        dist_files = list(self.dist_dir.glob("*"))
        if not dist_files:
            print("   ❌ No files found in dist directory")
            return False

        if dry_run:
            print("   [DRY RUN] Would run: twine check dist/*")
            return True

        try:
            result = subprocess.run(
                ["twine", "check", "dist/*"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            print("   ✅ Package validation passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Package validation failed: {e.stderr}")
            return False

    def check_pypi_credentials(self, repository: str = "pypi") -> bool:
        """Check if PyPI credentials are configured."""
        print(f"🔐 Checking {repository} credentials...")
        
        # Check for .pypirc file
        pypirc_path = Path.home() / ".pypirc"
        if pypirc_path.exists():
            print(f"   ✅ Found ~/.pypirc")
            return True
        
        # Check for environment variables
        if repository == "testpypi":
            if os.getenv("TWINE_USERNAME") and os.getenv("TWINE_PASSWORD"):
                print("   ✅ Found TWINE_USERNAME and TWINE_PASSWORD environment variables")
                return True
        else:
            if os.getenv("TWINE_USERNAME") and os.getenv("TWINE_PASSWORD"):
                print("   ✅ Found TWINE_USERNAME and TWINE_PASSWORD environment variables")
                return True
        
        print(f"   ⚠️  No credentials found for {repository}")
        print("   💡 Configure credentials using:")
        print("      - ~/.pypirc file, or")
        print("      - TWINE_USERNAME and TWINE_PASSWORD environment variables")
        return False

    def publish_to_testpypi(self, dry_run: bool = False) -> bool:
        """Publish package to TestPyPI."""
        print("🧪 Publishing to TestPyPI...")
        
        if not self.dist_dir.exists():
            print("   ❌ No dist directory found. Run build first.")
            return False

        if dry_run:
            print("   [DRY RUN] Would run: twine upload --repository testpypi dist/*")
            return True

        try:
            result = subprocess.run(
                ["twine", "upload", "--repository", "testpypi", "dist/*"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            print("   ✅ Successfully published to TestPyPI")
            print("   🌐 Package available at: https://test.pypi.org/project/adamsnrc/")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to publish to TestPyPI: {e.stderr}")
            return False

    def publish_to_pypi(self, dry_run: bool = False) -> bool:
        """Publish package to PyPI."""
        print("🚀 Publishing to PyPI...")
        
        if not self.dist_dir.exists():
            print("   ❌ No dist directory found. Run build first.")
            return False

        if dry_run:
            print("   [DRY RUN] Would run: twine upload dist/*")
            return True

        try:
            result = subprocess.run(
                ["twine", "upload", "dist/*"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            print("   ✅ Successfully published to PyPI")
            print("   🌐 Package available at: https://pypi.org/project/adamsnrc/")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to publish to PyPI: {e.stderr}")
            return False

    def test_installation(self, repository: str = "testpypi", dry_run: bool = False) -> bool:
        """Test package installation from the specified repository."""
        print(f"🧪 Testing installation from {repository}...")
        
        if dry_run:
            print(f"   [DRY RUN] Would test installation from {repository}")
            return True

        try:
            if repository == "testpypi":
                cmd = [
                    "pip", "install", 
                    "--index-url", "https://test.pypi.org/simple/",
                    "--extra-index-url", "https://pypi.org/simple/",
                    "adamsnrc"
                ]
            else:
                cmd = ["pip", "install", "adamsnrc"]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("   ✅ Installation test passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Installation test failed: {e.stderr}")
            return False

    def get_package_info(self) -> dict:
        """Get package information from pyproject.toml."""
        import tomllib
        
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        
        return {
            "name": data["project"]["name"],
            "version": data["project"]["version"],
            "description": data["project"]["description"]
        }

    def publish(self, test: bool = False, production: bool = False, dry_run: bool = False) -> bool:
        """Main publishing workflow."""
        print("🚀 ADAMSNRC Package Publisher")
        print("=" * 40)
        
        # Get package info
        try:
            info = self.get_package_info()
            print(f"📦 Package: {info['name']}")
            print(f"📦 Version: {info['version']}")
            print(f"📦 Description: {info['description']}")
        except Exception as e:
            print(f"⚠️  Could not read package info: {e}")
        
        print()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Clean build artifacts
        self.clean_build_artifacts(dry_run)
        
        # Build package
        if not self.build_package(dry_run):
            return False
        
        # Validate package
        if not self.validate_package(dry_run):
            return False
        
        success = True
        
        # Publish to TestPyPI
        if test:
            if not self.check_pypi_credentials("testpypi"):
                print("   ⚠️  Skipping TestPyPI due to missing credentials")
            else:
                if not self.publish_to_testpypi(dry_run):
                    success = False
                else:
                    # Test installation from TestPyPI
                    if not dry_run:
                        self.test_installation("testpypi", dry_run)
        
        # Publish to PyPI
        if production:
            if not self.check_pypi_credentials("pypi"):
                print("   ⚠️  Skipping PyPI due to missing credentials")
            else:
                if not self.publish_to_pypi(dry_run):
                    success = False
                else:
                    # Test installation from PyPI
                    if not dry_run:
                        self.test_installation("pypi", dry_run)
        
        if success:
            print("\n🎉 Publishing completed successfully!")
            if test:
                print("   🧪 TestPyPI: https://test.pypi.org/project/adamsnrc/")
            if production:
                print("   🚀 PyPI: https://pypi.org/project/adamsnrc/")
        else:
            print("\n❌ Publishing failed!")
        
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build and publish ADAMSNRC package to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_and_publish.py --test                    # Publish to TestPyPI only
  python build_and_publish.py --production              # Publish to PyPI only
  python build_and_publish.py --test --production       # Publish to both
  python build_and_publish.py --dry-run                 # Show what would be done
  python build_and_publish.py --test --dry-run          # Test workflow without publishing
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Publish to TestPyPI"
    )

    parser.add_argument(
        "--production",
        action="store_true",
        help="Publish to PyPI (production)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.test and not args.production:
        print("❌ Error: You must specify --test and/or --production")
        print("   Use --help for usage information")
        sys.exit(1)

    # Find project root
    project_root = Path.cwd()
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found in current directory")
        print("   Please run this script from the project root directory")
        sys.exit(1)

    # Create publisher and run
    publisher = PackagePublisher(project_root)
    success = publisher.publish(
        test=args.test,
        production=args.production,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
