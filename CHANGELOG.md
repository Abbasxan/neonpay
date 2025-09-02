# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2024-12-19

### Removed
- **BREAKING**: Complete removal of localization system
  - Removed `neonpay/localization.py` module
  - Removed `LocalizationManager` class
  - Removed `Language` enum
  - Removed all translation files (`translations/az.json`, `translations/en.json`, `translations/ru.json`)
  - Removed multilingual documentation (`docs/az/`, `docs/ru/`, `docs/en/`)
- Removed language parameter from all adapters
- Removed localization imports from base adapter and webhooks
- Removed localization dependencies from tests and examples

### Changed
- **BREAKING**: All error messages and user-facing text now in English only
- Simplified `PaymentAdapter` base class (no language parameter)
- Simplified all framework adapters (Aiogram, Pyrogram, PTB, Telebot)
- Reduced library complexity by ~40% while maintaining all core functionality
- Updated examples to use static English text instead of localization system

### Improved
- Faster library initialization (no translation loading)
- Reduced memory footprint
- Cleaner, more focused codebase
- Better maintainability

### Migration Guide
- Remove any `language` parameters from adapter constructors
- Replace localized error handling with English-only messages
- Update custom implementations that relied on localization features

## [2.2.0] - 2024-12-19

### Added
- 🔒 Enhanced security with comprehensive input validation
- 🛡️ Webhook signature verification and timestamp validation
- ✅ Improved async/sync handling for all adapters
- 🧪 Comprehensive security testing suite
- 📚 Complete security documentation and guides

### Changed
- **BREAKING**: PaymentStage validation enforces stricter limits (title: 32 chars, description: 255 chars)
- **BREAKING**: WebhookHandler now requires WebhookVerifier for security
- **BREAKING**: NeonPayCore constructor parameters changed (max_stages, enable_logging)

### Improved
- 🚀 Performance improvements and better error handling
- Better async/sync compatibility across all adapters

## [2.1.0] - 2024-12-18

### Added
- Simplified architecture
- Cleaner API design

### Removed
- Unnecessary complexity in core modules

## [2.0.0] - 2024-12-17

### Added
- Major security improvements
- Enhanced validation system
- Webhook security features
- Comprehensive testing suite

### Changed
- **BREAKING**: Enhanced security requirements
- Improved error handling

## [1.0.0] - 2024-12-16

### Added
- Initial release with basic functionality
- Support for Aiogram, Pyrogram, python-telegram-bot, and pyTelegramBotAPI
- Basic payment processing
- Webhook handling
- Multi-stage payment support
