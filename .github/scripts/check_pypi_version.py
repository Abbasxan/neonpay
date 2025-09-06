#!/usr/bin/env python3
"""
Script to check PyPI version information for neonpay package
"""

import json
import sys
import requests
from typing import Optional, Dict, Any


def get_pypi_info(package_name: str) -> Optional[Dict[str, Any]]:
    """Get package information from PyPI"""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching PyPI data: {e}")
        return None


def get_latest_version(package_name: str) -> Optional[str]:
    """Get the latest version from PyPI"""
    data = get_pypi_info(package_name)
    if not data:
        return None
    
    versions = list(data['releases'].keys())
    if not versions:
        return None
    
    # Sort versions properly (handle semantic versioning)
    def version_key(version: str) -> tuple:
        try:
            # Split version into parts and convert to integers
            parts = []
            for part in version.split('.'):
                if '-' in part:
                    # Handle pre-release versions like "2.5.0-alpha"
                    main_part, pre_part = part.split('-', 1)
                    parts.append(int(main_part))
                    parts.append(pre_part)
                else:
                    parts.append(int(part))
            return tuple(parts)
        except ValueError:
            # Fallback to string comparison
            return (version,)
    
    versions.sort(key=version_key)
    return versions[-1]


def check_version_exists(package_name: str, version: str) -> bool:
    """Check if specific version exists on PyPI"""
    data = get_pypi_info(package_name)
    if not data:
        return False
    
    return version in data['releases']


def main():
    package_name = "neonpay"
    
    print(f"🔍 Checking PyPI information for '{package_name}'")
    print("=" * 50)
    
    # Get latest version
    latest_version = get_latest_version(package_name)
    if latest_version:
        print(f"📦 Latest PyPI version: {latest_version}")
        print(f"🔗 PyPI URL: https://pypi.org/project/{package_name}/{latest_version}/")
    else:
        print("❌ Could not fetch latest version")
        return 1
    
    # Check if specific version exists (if provided as argument)
    if len(sys.argv) > 1:
        check_version = sys.argv[1]
        exists = check_version_exists(package_name, check_version)
        
        print(f"\n🔍 Checking version '{check_version}':")
        if exists:
            print(f"✅ Version {check_version} exists on PyPI")
            print(f"🔗 URL: https://pypi.org/project/{package_name}/{check_version}/")
        else:
            print(f"❌ Version {check_version} does not exist on PyPI")
            print(f"🚀 Ready to publish: https://pypi.org/project/{package_name}/{check_version}/")
    
    # Show package stats
    print(f"\n📊 Package Statistics:")
    print(f"📈 Downloads: https://pypistats.org/packages/{package_name}")
    print(f"📚 Documentation: https://pypi.org/project/{package_name}/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
