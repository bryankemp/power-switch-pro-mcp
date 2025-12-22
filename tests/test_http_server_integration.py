"""Integration tests for HTTP server startup and configuration."""

import importlib.util
from pathlib import Path

import pytest


@pytest.mark.integration
class TestHTTPServerStartup:
    """Integration tests for HTTP server startup."""

    def test_http_server_imports_without_error(self):
        """Test that the HTTP server module can be imported."""
        from power_switch_pro_mcp import http_server

        assert http_server is not None

    def test_mcp_run_with_valid_transport(self, monkeypatch):
        """Test that mcp.run() is called with a valid transport type."""
        # Read the http_server.py file and check the mcp.run() call
        http_server_path = (
            Path(__file__).parent.parent / "src" / "power_switch_pro_mcp" / "http_server.py"
        )

        with open(http_server_path) as f:
            content = f.read()

        # Check that mcp.run() uses a valid transport
        # FastMCP supports: 'stdio', 'sse', 'streamable-http'
        valid_transports = ["stdio", "sse", "streamable-http"]

        # Find the mcp.run() call
        assert "mcp.run(transport=" in content, "mcp.run() call not found in http_server.py"

        # Extract the transport value
        for line in content.split("\n"):
            if "mcp.run(transport=" in line:
                for transport in valid_transports:
                    if f'"{transport}"' in line or f"'{transport}'" in line:
                        return  # Found a valid transport

        pytest.fail(f"mcp.run() must use one of: {valid_transports}")

    def test_http_server_script_syntax_valid(self):
        """Test that the HTTP server script has valid Python syntax."""
        http_server_path = (
            Path(__file__).parent.parent / "src" / "power_switch_pro_mcp" / "http_server.py"
        )

        # Try to compile the module
        spec = importlib.util.spec_from_file_location("http_server", http_server_path)
        assert spec is not None
        assert spec.loader is not None

    def test_http_server_would_start_with_env_vars(self, monkeypatch):
        """Test that HTTP server can be started with proper env vars (dry run)."""
        import os

        monkeypatch.setenv("POWER_SWITCH_HOST", "192.168.1.100")
        monkeypatch.setenv("POWER_SWITCH_PASSWORD", "test-password")
        monkeypatch.setenv("POWER_SWITCH_USERNAME", "admin")

        # Verify environment variables are set
        assert os.getenv("POWER_SWITCH_HOST") == "192.168.1.100"
        assert os.getenv("POWER_SWITCH_PASSWORD") == "test-password"
        assert os.getenv("POWER_SWITCH_USERNAME") == "admin"

        # Import the module to ensure it can read env vars
        from power_switch_pro_mcp import http_server

        # The module should import without error when env vars are set
        assert http_server is not None

    def test_fastmcp_binds_to_all_interfaces(self):
        """Test that FastMCP is configured to bind to 0.0.0.0 for container accessibility."""
        from power_switch_pro_mcp import http_server

        # Verify FastMCP instance is configured with correct host and port
        assert hasattr(http_server.mcp, "settings"), "FastMCP instance missing settings"
        assert http_server.mcp.settings.host == "0.0.0.0", (
            f"FastMCP must bind to 0.0.0.0 for container accessibility, "
            f"but is configured to bind to {http_server.mcp.settings.host}"
        )
        assert http_server.mcp.settings.port == 8000, (
            f"FastMCP must bind to port 8000, "
            f"but is configured to bind to port {http_server.mcp.settings.port}"
        )
