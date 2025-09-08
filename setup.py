"""
Setup script for NEONPAY - Modern Python library for Telegram Stars payments integration.
"""

import sys
from pathlib import Path

try:
    from setuptools import find_packages, setup
except ImportError:
    print("Error: setuptools is required but not installed.")
    print("Please install setuptools using: pip install setuptools")
    print("Or install the package in development mode: pip install -e .")
    print("Alternatively, use: pip install --upgrade pip setuptools wheel")
    sys.exit(1)

# Minimum Python version check
if sys.version_info < (3, 9):
    raise RuntimeError("NEONPAY requires Python 3.9 or higher")

# Read version from _version.py
version_file = Path(__file__).parent / "neonpay" / "_version.py"
version_dict = {}
if version_file.exists():
    with open(version_file, "r", encoding="utf-8") as f:
        exec(f.read(), version_dict)
    version = version_dict.get("__version__", "1.0.0")
else:
    version = "1.0.0"

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = (
    readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
)

# Core dependencies
install_requires = [
    "aiohttp>=3.8.0",
    "typing-extensions>=4.0.0; python_version<'3.10'",
    "tgcrypto>=1.2.0",
]

# Optional dependencies
extras_require = {
    "aiogram": ["aiogram>=3.0.0"],
    "pyrogram": ["pyrogram>=2.0.106", "tgcrypto>=1.2.0"],
    "ptb": ["python-telegram-bot>=20.0"],
    "telebot": ["pyTelegramBotAPI>=4.0.0"],
    "all": [
        "aiogram>=3.0.0",
        "pyrogram>=2.0.106",
        "tgcrypto>=1.2.0",
        "python-telegram-bot>=20.0",
        "pyTelegramBotAPI>=4.0.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "mypy>=1.0.0",
        "flake8>=6.0.0",
        "pre-commit>=2.20.0",
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
}

setup(
    name="neonpay",
    version=version,
    description="Modern Python library for Telegram Stars (XTR) payments integration with support for Aiogram, Pyrogram, python-telegram-bot and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Abbas Sultanov",
    author_email="sultanov.abas@outlook.com",
    url="https://github.com/Abbasxan/neonpay",
    project_urls={
        "Homepage": "https://github.com/Abbasxan/neonpay",
        "Repository": "https://github.com/Abbasxan/neonpay",
        "Issues": "https://github.com/Abbasxan/neonpay/issues",
        "Documentation": "https://github.com/Abbasxan/neonpay/tree/main/docs",
        "Changelog": "https://github.com/Abbasxan/neonpay/releases",
        "Telegram": "https://t.me/neonsahib",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*", "website*"]),
    package_data={"neonpay": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    keywords=[
        "telegram",
        "bot",
        "payments",
        "stars",
        "xtr",
        "donations",
        "aiogram",
        "pyrogram",
        "python-telegram-bot",
        "telebot",
        "telegram-payments",
        "cryptocurrency",
        "micropayments",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    license="MIT",
    license_files=["LICENSE"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "neonpay=neonpay.cli:main",
        ],
    },
)
