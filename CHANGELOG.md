# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-12-30

### Added
- AutoPing management tools for monitoring hosts and automatic outlet power cycling
  - `autoping_add_entry` - Add new AutoPing monitoring entries
  - `autoping_list_entries` - List all configured AutoPing entries
  - `autoping_get_entry` - Get details of specific entry
  - `autoping_update_entry` - Update existing entries
  - `autoping_delete_entry` - Delete entries
  - `autoping_enable_entry` / `autoping_disable_entry` - Enable/disable monitoring

### Changed
- Updated to power-switch-pro >=1.1.1 for improved AutoPing API support
- Default HTTP server port changed from 8000 to 5000
- Port is now configurable via PORT environment variable

### Fixed
- Fixed AutoPing field name display in list_entries output
- Corrected HTTP server integration tests for new default port
- Import ordering issues in test files

## [0.1.0] - 2025-12-22

### Added
- Initial release of Power Switch Pro MCP Server
- MCP server implementation with stdio transport for local clients
- HTTP server implementation with streamable-http transport for remote access
- Outlet control tools (on, off, cycle, bulk operations)
- Power monitoring tools (voltage, current, power, energy)
- Device information and configuration tools
- Docker support with multi-platform images (amd64, arm64)
- Docker Compose configuration for easy deployment
- GitHub Container Registry integration
- Comprehensive test suite with pytest
- Sphinx documentation
- Pre-commit hooks for code quality
- GitHub Actions CI/CD workflows
- Support for Python 3.10+

[Unreleased]: https://github.com/bryankemp/power-switch-pro-mcp/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/bryankemp/power-switch-pro-mcp/compare/v0.1.0...v1.1.0
[0.1.0]: https://github.com/bryankemp/power-switch-pro-mcp/releases/tag/v0.1.0
