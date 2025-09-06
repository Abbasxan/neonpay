#!/usr/bin/env python3
"""
Script to clean up Python cache files and other temporary files
"""

import os
import shutil
import sys
from pathlib import Path


def find_and_remove_patterns(root_dir, patterns):
    """Find and remove files/directories matching patterns"""
    removed_count = 0
    removed_size = 0
    
    for pattern in patterns:
        for path in Path(root_dir).rglob(pattern):
            try:
                if path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    removed_count += 1
                    removed_size += size
                    print(f"🗑️  Removed file: {path}")
                elif path.is_dir():
                    # Calculate directory size
                    size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                    shutil.rmtree(path)
                    removed_count += 1
                    removed_size += size
                    print(f"🗑️  Removed directory: {path}")
            except (OSError, PermissionError) as e:
                print(f"⚠️  Could not remove {path}: {e}")
    
    return removed_count, removed_size


def format_size(size_bytes):
    """Format size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def main():
    """Main cleanup function"""
    print("🧹 Starting cleanup of Python cache files...")
    print("=" * 50)
    
    # Patterns to clean up
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        "htmlcov",
        ".benchmarks",
        "*.egg-info",
        "dist",
        "build",
        "*.log",
        "*.tmp",
        ".DS_Store",
        "Thumbs.db",
    ]
    
    # Get current directory
    root_dir = Path.cwd()
    print(f"📁 Cleaning directory: {root_dir}")
    print()
    
    # Remove files and directories
    removed_count, removed_size = find_and_remove_patterns(root_dir, patterns)
    
    print()
    print("=" * 50)
    print(f"✅ Cleanup completed!")
    print(f"📊 Removed {removed_count} items")
    print(f"💾 Freed up {format_size(removed_size)} of space")
    
    if removed_count == 0:
        print("🎉 No cache files found - project is already clean!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
