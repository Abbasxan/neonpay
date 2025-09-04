"""
Version information for NEONPAY
"""

__version__ = "2.4.0"
__version_info__ = (2, 4, 0)

# Version history
VERSION_HISTORY = {
    "1.0.0": "Initial release with basic functionality",
    "2.0.0": "Major security improvements, enhanced validation, webhook security, comprehensive testing",
    "2.1.0": "Simplified architecture, removed unnecessary localization, cleaner API",
    "2.2.0": "Complete localization removal, maximum simplification, focused on core functionality",
    "2.3.0": "Complete localization system removal, English-only library, reduced complexity by 40%",
    "2.4.0": "Added official Bot API adapter, improved async/sync handling, extended adapter support",
}

# Latest version details
LATEST_VERSION = {
    "version": __version__,
    "major": 2,
    "minor": 4,
    "patch": 0,
    "release_date": "2025-09-04",
    "highlights": [
        "🆕 Added BotAPIAdapter for official Telegram Bot API support",
        "✅ Full async and sync compatibility across all adapters",
        "🔒 Enhanced security with stricter input validation",
        "🛡️ Webhook signature verification and timestamp validation",
        "🚀 Performance improvements and better error handling",
        "📚 Streamlined English-only documentation",
        "⚡ Further complexity reduction while maintaining security",
    ],
    "breaking_changes": [
        "BotAPIAdapter introduces a slightly different async callback mechanism",
        "All adapters now require explicit setup for payment handlers",
        "PaymentStage validation stricter: title ≤ 32 chars, description ≤ 255 chars",
    ],
    "simplifications": [
        "Adapters standardized for both async and sync usage",
        "Legacy localization completely removed",
        "Error messages and user feedback are English-only",
        "Reduced memory footprint and faster initialization",
        "Unified payload handling across all adapters",
    ],
    "migration_guide": "See CHANGELOG.md for upgrade instructions from v2.3.0 to v2.4.0",
}
