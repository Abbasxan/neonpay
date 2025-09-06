#!/usr/bin/env python3
"""
Script to automatically update version information in README.md
"""

import re
import sys
from pathlib import Path


def get_current_version():
    """Get current version from _version.py"""
    version_file = Path("neonpay/_version.py")
    if not version_file.exists():
        print("❌ Version file not found: neonpay/_version.py")
        return None
    
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract version using regex
    match = re.search(r'__version__ = "([^"]+)"', content)
    if match:
        return match.group(1)
    
    print("❌ Could not extract version from _version.py")
    return None


def update_readme_version(version):
    """Update version information in README.md"""
    readme_file = Path("README.md")
    if not readme_file.exists():
        print("❌ README.md not found")
        return False
    
    with open(readme_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update version in the header
    old_pattern = r'\*\*Current Version: \[([^\]]+)\]\([^)]+\) - Published on PyPI\*\* 🚀'
    new_text = f'**Current Version: [{version}](https://pypi.org/project/neonpay/{version}/) - Published on PyPI** 🚀'
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_text, content)
        print(f"✅ Updated header version to {version}")
    else:
        print("⚠️  Version header pattern not found")
    
    # Update installation section
    old_install_pattern = r'pip install neonpay==[0-9.]+'
    new_install_text = f'pip install neonpay=={version}'
    
    if re.search(old_install_pattern, content):
        content = re.sub(old_install_pattern, new_install_text, content)
        print(f"✅ Updated installation version to {version}")
    else:
        print("⚠️  Installation version pattern not found")
    
    # Update PyPI link
    old_pypi_pattern = r'\[neonpay [0-9.]+\]\(https://pypi\.org/project/neonpay/[0-9.]+/\)'
    new_pypi_text = f'[neonpay {version}](https://pypi.org/project/neonpay/{version}/)'
    
    if re.search(old_pypi_pattern, content):
        content = re.sub(old_pypi_pattern, new_pypi_text, content)
        print(f"✅ Updated PyPI link to {version}")
    else:
        print("⚠️  PyPI link pattern not found")
    
    # Write updated content
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎉 README.md updated with version {version}")
    return True


def main():
    """Main function"""
    print("🔍 Updating README.md version information...")
    
    # Get current version
    version = get_current_version()
    if not version:
        return 1
    
    print(f"📦 Current version: {version}")
    
    # Update README
    if update_readme_version(version):
        print(f"✅ Successfully updated README.md with version {version}")
        print(f"🔗 PyPI URL: https://pypi.org/project/neonpay/{version}/")
        return 0
    else:
        print("❌ Failed to update README.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
