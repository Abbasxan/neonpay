"""
Version information for NEONPAY
"""

__version__ = "2.6.0"
__version_info__ = (2, 6, 0)

# Version history
VERSION_HISTORY = {
    "1.0.0": "Initial release with basic functionality",
    "2.0.0": "Major security improvements, enhanced validation, webhook security, comprehensive testing",
    "2.1.0": "Simplified architecture, removed unnecessary localization, cleaner API",
    "2.2.0": "Complete localization removal, maximum simplification, focused on core functionality",
    "2.3.0": "Complete localization system removal, English-only library, reduced complexity by 40%",
    "2.4.0": "Added official Bot API adapter, improved async/sync handling, extended adapter support",
    "2.5.0": "Enhanced security features, improved error handling, optimized performance, updated documentation",
    "2.5.1": "Critical security fixes: removed hardcoded tokens, fixed network binding issues, improved CLI notifications",
    "2.6.0": "NEW FEATURES: Added web interfaces, analytics system, notifications, backup system, templates, and multi-bot management",
}

# Latest version details
LATEST_VERSION = {
    "version": __version__,
    "major": 2,
    "minor": 6,
    "patch": 0,
    "release_date": "2025-09-07",
    "highlights": [
        "🌐 NEW: Web Analytics Dashboard - Real-time bot performance monitoring",
        "🔄 NEW: Web Sync Interface - Multi-bot synchronization via web API",
        "📊 NEW: Advanced Analytics System - Comprehensive payment analytics",
        "🔔 NEW: Notification System - Email, Telegram, SMS, Webhook notifications",
        "💾 NEW: Backup & Restore System - Automated data protection",
        "📋 NEW: Template System - Pre-built bot templates and generators",
        "🔗 NEW: Multi-Bot Analytics - Network-wide performance tracking",
        "📈 NEW: Event Collection System - Centralized event management",
        "🛡️ ENHANCED: Complete security overhaul with zero vulnerabilities",
        "⚡ ENHANCED: Production-ready features and scalability",
    ],
    "breaking_changes": [
        "NEW: Multiple new modules available for import",
        "ENHANCED: CLI commands now support new features",
        "SECURITY: Web servers use localhost binding by default",
        "ADMIN: Notification system requires separate admin bot setup",
    ],
    "simplifications": [
        "Unified architecture across all new modules",
        "Streamlined web interfaces for analytics and sync",
        "Integrated notification system with multiple providers",
        "Automated backup and restore workflows",
        "Template-based bot generation and management",
        "Centralized event collection and analytics",
    ],
    "migration_guide": "See CHANGELOG.md for upgrade instructions from v2.5.x to v2.6.0",
}
