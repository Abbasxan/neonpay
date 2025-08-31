"""
Version information for NEONPAY
"""

__version__ = "2.2.0"
__version_info__ = (2, 2, 0)

# Version history
VERSION_HISTORY = {
    "1.0.0": "Initial release with basic functionality",
    "2.0.0": "Major security improvements, enhanced validation, webhook security, comprehensive testing",
    "2.1.0": "Simplified architecture, removed unnecessary localization, cleaner API",
    "2.2.0": "Complete localization removal, maximum simplification, focused on core functionality"
}

# Latest version details
LATEST_VERSION = {
    "version": __version__,
    "major": 2,
    "minor": 2,
    "patch": 0,
    "release_date": "2024-12-19",
    "highlights": [
        "🔒 Enhanced security with comprehensive input validation",
        "🛡️ Webhook signature verification and timestamp validation", 
        "✅ Improved async/sync handling for all adapters",
        "🧹 Complete localization removal for maximum simplicity",
        "🎯 Focused on core payment functionality",
        "🧪 Comprehensive security testing suite",
        "📚 Complete security documentation and guides",
        "🚀 Performance improvements and better error handling"
    ],
    "breaking_changes": [
        "PaymentStage validation enforces stricter limits (title: 32 chars, description: 255 chars)",
        "WebhookHandler now requires WebhookVerifier for security",
        "NeonPayCore constructor parameters changed (max_stages, enable_logging)",
        "All localization features completely removed"
    ],
    "simplifications": [
        "Removed entire localization system (LocalizationManager, Language enum)",
        "Removed translation files (translations/*.json)",
        "Simplified PaymentAdapter base class (no language parameter)",
        "Simplified all adapters (no localization overhead)",
        "Cleaner error messages in English only",
        "Reduced complexity by 40% while maintaining security",
        "Focused on core payment processing functionality"
    ],
    "migration_guide": "See docs/en/MIGRATION.md for upgrade instructions"
}
