#!/usr/bin/env python3
"""
Version bumping script for ADAMSNRC package.

This script automatically bumps the version number across all relevant files:
- pyproject.toml
- setup.py
- adamsnrc/__init__.py

Usage:
    python bump_version.py [major|minor|patch] [--dry-run]
    
Examples:
    python bump_version.py patch          # 2.0.0 -> 2.0.1
    python bump_version.py minor          # 2.0.0 -> 2.1.0
    python bump_version.py major          # 2.0.0 -> 3.0.0
    python bump_version.py patch --dry-run # Show what would change
"""

import argparse
import re
import sys
from pathlib import Path



class VersionBumper:
    """Handles version bumping across multiple files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_toml = project_root / "pyproject.toml"
        self.setup_py = project_root / "setup.py"
        self.init_py = project_root / "adamsnrc" / "__init__.py"

    def get_current_version(self) -> str:
        """Get current version from pyproject.toml."""
        content = self.pyproject_toml.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise ValueError("Could not find version in pyproject.toml")
        return match.group(1)

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Bump version according to semantic versioning."""
        major, minor, patch = map(int, current_version.split('.'))

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}"

    def update_pyproject_toml(self, new_version: str, dry_run: bool = False) -> bool:
        """Update version in pyproject.toml."""
        content = self.pyproject_toml.read_text()
        old_content = content

        # Update version line
        content = re.sub(
            r'(version\s*=\s*["\'])[^"\']+(["\'])',
            rf'\g<1>{new_version}\g<2>',
            content
        )

        if content != old_content:
            if not dry_run:
                self.pyproject_toml.write_text(content)
            print(f"✅ Updated pyproject.toml: {new_version}")
            return True
        else:
            print("❌ No changes needed in pyproject.toml")
            return False

    def update_setup_py(self, new_version: str, dry_run: bool = False) -> bool:
        """Update version in setup.py."""
        content = self.setup_py.read_text()
        old_content = content

        # Update version line
        content = re.sub(
            r'(version\s*=\s*["\'])[^"\']+(["\'])',
            rf'\g<1>{new_version}\g<2>',
            content
        )

        if content != old_content:
            if not dry_run:
                self.setup_py.write_text(content)
            print(f"✅ Updated setup.py: {new_version}")
            return True
        else:
            print("❌ No changes needed in setup.py")
            return False

    def update_init_py(self, new_version: str, dry_run: bool = False) -> bool:
        """Update version in __init__.py."""
        if not self.init_py.exists():
            print(f"⚠️  {self.init_py} not found, skipping")
            return False

        content = self.init_py.read_text()
        old_content = content

        # Look for __version__ assignment
        version_patterns = [
            r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
            r'("version":\s*["\'])[^"\']+(["\'])',
        ]

        updated = False
        for pattern in version_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, rf'\g<1>{new_version}\g<2>', content)
                updated = True
                break

        if content != old_content and updated:
            if not dry_run:
                self.init_py.write_text(content)
            print(f"✅ Updated {self.init_py}: {new_version}")
            return True
        else:
            print(f"❌ No version found in {self.init_py}")
            return False

    def update_changelog(self, new_version: str, dry_run: bool = False, interactive: bool = False) -> bool:
        """Add version entry to CHANGELOG.md."""
        changelog_path = self.project_root / "CHANGELOG.md"
        if not changelog_path.exists():
            print(f"⚠️  {changelog_path} not found, skipping")
            return False

        content = changelog_path.read_text()

        # Check if version already exists
        if f"## [{new_version}]" in content:
            print(f"⚠️  Version {new_version} already exists in CHANGELOG.md")
            return False

        # Add new version entry after the first ## [ line
        today = self._get_today_date()
        
        if interactive and not dry_run:
            # Interactive mode: prompt for changelog content
            print(f"\n📝 Please provide changelog content for version {new_version}:")
            print("(Leave empty and press Enter to skip a section)")
            
            added = self._prompt_changelog_section("Added")
            changed = self._prompt_changelog_section("Changed") 
            fixed = self._prompt_changelog_section("Fixed")
            removed = self._prompt_changelog_section("Removed")
            
            new_entry = f"""## [{new_version}] - {today}

### Added
{added}

### Changed
{changed}

### Fixed
{fixed}

### Removed
{removed}

"""
        else:
            # Non-interactive mode: create empty template
            new_entry = f"""## [{new_version}] - {today}

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 

"""

        # Insert after the first ## [ line (usually the latest version)
        lines = content.split('\n')
        insert_index = None

        for i, line in enumerate(lines):
            if line.startswith('## [') and insert_index is None:
                insert_index = i
                break

        if insert_index is not None:
            lines.insert(insert_index, new_entry)
            new_content = '\n'.join(lines)

            if not dry_run:
                changelog_path.write_text(new_content)
            print(f"✅ Added version {new_version} to CHANGELOG.md")
            return True
        else:
            print("❌ Could not find version section in CHANGELOG.md")
            return False

    def _prompt_changelog_section(self, section_name: str) -> str:
        """Prompt user for changelog section content."""
        print(f"\n{section_name} (one item per line, empty line to finish):")
        items = []
        while True:
            try:
                line = input("  - ").strip()
                if not line:
                    break
                items.append(f"- {line}")
            except (EOFError, KeyboardInterrupt):
                break
        
        if items:
            return "\n".join(items) + "\n"
        else:
            return "- \n"

    def _get_today_date(self) -> str:
        """Get today's date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def bump(self, bump_type: str, dry_run: bool = False, auto_git: bool = False, interactive: bool = False) -> tuple[str, str]:
        """Main method to bump version across all files."""
        current_version = self.get_current_version()
        new_version = self.bump_version(current_version, bump_type)

        print(f"🔄 Bumping version from {current_version} to {new_version}")
        print(f"{'[DRY RUN] ' if dry_run else ''}Updating files...")
        print()

        changes_made = []

        # Update all files
        if self.update_pyproject_toml(new_version, dry_run):
            changes_made.append("pyproject.toml")

        if self.update_setup_py(new_version, dry_run):
            changes_made.append("setup.py")

        if self.update_init_py(new_version, dry_run):
            changes_made.append("adamsnrc/__init__.py")

        if self.update_changelog(new_version, dry_run, interactive):
            changes_made.append("CHANGELOG.md")

        print()
        if dry_run:
            print(f"🔍 DRY RUN: Would update {len(changes_made)} files")
        else:
            print(f"✅ Successfully updated {len(changes_made)} files")
            print(f"📝 Files changed: {', '.join(changes_made)}")

            # Run git commands if auto_git is enabled
            if auto_git and changes_made:
                self._run_git_commands(current_version, new_version, dry_run)

        return current_version, new_version

    def _run_git_commands(self, old_version: str, new_version: str, dry_run: bool = False):
        """Run git and GitHub CLI commands for release workflow."""
        import subprocess

        print()
        print("🚀 Running Git and GitHub CLI commands...")
        print()

        commands = [
            ("git status", "Check current git status"),
            ("git add .", "Stage all changes"),
            (f"git commit -m 'bump: version {old_version} -> {new_version}'", "Commit version changes"),
            ("git push origin main", "Push to main branch"),
            (f"git tag v{new_version}", "Create version tag"),
            (f"git push origin v{new_version}", "Push tag to remote"),
        ]

        for cmd, description in commands:
            print(f"📋 {description}...")
            if dry_run:
                print(f"   [DRY RUN] Would run: {cmd}")
            else:
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
                    print(f"   ✅ Success: {cmd}")
                    if result.stdout.strip():
                        print(f"      Output: {result.stdout.strip()}")
                except subprocess.CalledProcessError as e:
                    print(f"   ❌ Error running: {cmd}")
                    print(f"      Error: {e.stderr.strip()}")
                    print("   ⚠️  Continuing with remaining commands...")
            print()

        # Try to create GitHub release if gh CLI is available
        if not dry_run:
            self._create_github_release(new_version)

    def _create_github_release(self, version: str):
        """Create GitHub release using gh CLI."""
        import subprocess

        print("🏷️  Creating GitHub release...")

        # Check if gh CLI is available
        try:
            subprocess.run(["gh", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️  GitHub CLI (gh) not found. Skipping release creation.")
            print("   💡 Install GitHub CLI: https://cli.github.com/")
            return

        # Get release notes from CHANGELOG.md
        release_notes = self._get_release_notes(version)

        try:
            cmd = [
                "gh", "release", "create", f"v{version}",
                "--title", f"Version {version}",
                "--notes", release_notes
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ GitHub release created: v{version}")
            if result.stdout.strip():
                print(f"      {result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error creating GitHub release: {e.stderr.strip()}")
            print("   💡 You can create the release manually on GitHub")

    def _get_release_notes(self, version: str) -> str:
        """Extract release notes from CHANGELOG.md for the given version."""
        changelog_path = self.project_root / "CHANGELOG.md"
        if not changelog_path.exists():
            return f"Release version {version}"

        content = changelog_path.read_text()

        # Find the section for this version
        version_pattern = f"## [{version}]"
        lines = content.split('\n')

        start_index = None
        end_index = None

        for i, line in enumerate(lines):
            if line.startswith(version_pattern):
                start_index = i
            elif start_index is not None and line.startswith('## ['):
                end_index = i
                break

        if start_index is not None:
            if end_index is None:
                end_index = len(lines)

            # Extract the version section
            version_section = lines[start_index:end_index]

            # Remove the version header and clean up
            if len(version_section) > 1:
                version_section = version_section[1:]  # Remove header

            # Join and clean up
            notes = '\n'.join(version_section).strip()

            # Remove empty sections
            notes = re.sub(r'### \w+\n\s*\n', '', notes)
            notes = re.sub(r'\n\s*\n\s*\n', '\n\n', notes)
            
            # Clean up any remaining empty lines
            notes = re.sub(r'\n\s*\n\s*\n', '\n\n', notes)
            notes = notes.strip()
            
            # If notes are empty or only contain whitespace, provide a default message
            if not notes or notes.isspace():
                return f"Release version {version}\n\nThis release includes various improvements and bug fixes."
            
            return notes

        return f"Release version {version}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bump version across all project files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bump_version.py patch          # 2.0.0 -> 2.0.1
  python bump_version.py minor          # 2.0.0 -> 2.1.0  
  python bump_version.py major          # 2.0.0 -> 3.0.0
  python bump_version.py patch --dry-run # Show what would change
        """
    )

    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without making changes"
    )

    parser.add_argument(
        "--auto-git",
        action="store_true",
        help="Automatically run git commands and create GitHub release"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode: prompt for changelog content during version bump"
    )

    args = parser.parse_args()

    # Find project root (directory containing pyproject.toml)
    project_root = Path.cwd()
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found in current directory")
        print("   Please run this script from the project root directory")
        sys.exit(1)

    try:
        bumper = VersionBumper(project_root)
        old_version, new_version = bumper.bump(args.bump_type, args.dry_run, args.auto_git, args.interactive)

        if not args.dry_run and not args.auto_git:
            print()
            print("🎉 Version bump completed!")
            print(f"📦 Old version: {old_version}")
            print(f"📦 New version: {new_version}")
            print()
            print("Next steps:")
            print("1. Review the changes")
            print("2. Update CHANGELOG.md with actual changes")
            print("3. Commit the changes:")
            print("   git add .")
            print(f"   git commit -m 'bump: version {old_version} -> {new_version}'")
            print(f"   git tag v{new_version}")
            print("   git push origin main --tags")
        elif not args.dry_run and args.auto_git:
            print()
            print("🎉 Complete release workflow completed!")
            print(f"📦 Old version: {old_version}")
            print(f"📦 New version: {new_version}")
            print()
            print("✅ What was done:")
            print("   • Version bumped in all files")
            print("   • CHANGELOG.md updated")
            print("   • Changes committed and pushed")
            print("   • Git tag created and pushed")
            print("   • GitHub release created (if gh CLI available)")
            print()
            print("🚀 Your release is ready!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
