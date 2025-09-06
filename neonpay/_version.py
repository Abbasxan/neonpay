"""
Version information for NEONPAY
"""

__version__ = "2.5.0"
__version_info__ = (2, 5, 0)

# Version history
VERSION_HISTORY = {
    "1.0.0": "Initial release with basic functionality",
    "2.0.0": "Major security improvements, enhanced validation, webhook security, comprehensive testing",
    "2.1.0": "Simplified architecture, removed unnecessary localization, cleaner API",
    "2.2.0": "Complete localization removal, maximum simplification, focused on core functionality",
    "2.3.0": "Complete localization system removal, English-only library, reduced complexity by 40%",
    "2.4.0": "Added official Bot API adapter, improved async/sync handling, extended adapter support",
    "2.5.0": "Enhanced security features, improved error handling, optimized performance, updated documentation",
}

# Latest version details
LATEST_VERSION = {
    "version": __version__,
    "major": 2,
    "minor": 5,
    "patch": 0,
    "release_date": "2025-01-15",
    "highlights": [
        "🔒 Enhanced security features with improved validation",
        "🚀 Optimized performance and better error handling",
        "📚 Updated documentation and examples",
        "🛡️ Strengthened webhook security mechanisms",
        "⚡ Improved async/sync compatibility",
        "🔧 Better error messages and debugging support",
        "📦 Streamlined package structure",
    ],
    "breaking_changes": [
        "Enhanced security validation may require updates to custom implementations",
        "Improved error handling may change exception types in some cases",
        "Webhook verification now includes additional security checks",
    ],
    "simplifications": [
        "Streamlined error handling with clearer messages",
        "Optimized memory usage and faster initialization",
        "Simplified webhook processing pipeline",
        "Better separation of concerns in core modules",
        "Enhanced debugging capabilities",
    ],
    "migration_guide": "See CHANGELOG.md for upgrade instructions from v2.4.0 to v2.5.0",
}
