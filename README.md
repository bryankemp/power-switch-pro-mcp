# Power Switch Pro MCP Server

An MCP (Model Context Protocol) server that provides tools for controlling and monitoring Digital Loggers Power Switch Pro devices. This allows AI assistants and other MCP clients to interact with your power switch hardware.

## Features

- 🔌 **Outlet Control** - Turn outlets on/off/cycle individually or in bulk
- 📊 **Power Monitoring** - Read real-time voltage, current, power, and energy metrics
- 📝 **Device Management** - Get device info and configure outlet names
- 🔒 **Secure** - Uses HTTP Digest Authentication via environment variables
- 🚀 **Easy Integration** - Works with any MCP-compatible client (Warp, Claude Desktop, etc.)
- 🌐 **Multiple Transports** - Supports both stdio (local) and HTTP (remote) via MCP streamable-http transport
- 🐳 **Docker Ready** - Easy containerized deployment with docker-compose

## Installation

### Prerequisites

- Python 3.10 or higher
- A Digital Loggers Power Switch Pro device with firmware 1.7.0+
- Network access to your device

### Install from Source

```bash
git clone https://github.com/bryankemp/power-switch-pro-mcp.git
cd power-switch-pro-mcp
pip install .
```

## Configuration

The MCP server is configured via environment variables:

- `POWER_SWITCH_HOST` - IP address or hostname of your device (required)
- `POWER_SWITCH_PASSWORD` - Admin password (required)
- `POWER_SWITCH_USERNAME` - Username (default: "admin")
- `POWER_SWITCH_USE_HTTPS` - Use HTTPS instead of HTTP (default: "false")

### For Warp

Add to your Warp MCP settings configuration file:

```json
{
  "mcpServers": {
    "power-switch-pro": {
      "command": "python",
      "args": ["-m", "power_switch_pro_mcp.server"],
      "env": {
        "POWER_SWITCH_HOST": "192.168.0.100",
        "POWER_SWITCH_PASSWORD": "your-password",
        "POWER_SWITCH_USERNAME": "admin",
        "POWER_SWITCH_USE_HTTPS": "false"
      }
    }
  }
}
```

### For Claude Desktop

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "power-switch-pro": {
      "command": "python",
      "args": ["-m", "power_switch_pro_mcp.server"],
      "env": {
        "POWER_SWITCH_HOST": "192.168.0.100",
        "POWER_SWITCH_PASSWORD": "your-password",
        "POWER_SWITCH_USERNAME": "admin"
      }
    }
  }
}
```

**Note**: `POWER_SWITCH_USERNAME` is optional and defaults to "admin" if not specified.

### For Other MCP Clients

Refer to your MCP client's documentation for how to configure external MCP servers. You'll need to:

1. Set the command to run: `python -m power_switch_pro_mcp.server`
2. Configure the required environment variables

## Available Tools

The server exposes the following MCP tools:

### Outlet Control

- **`outlet_on`** - Turn on a specific outlet
  - Parameters: `outlet_id` (0-7)

- **`outlet_off`** - Turn off a specific outlet
  - Parameters: `outlet_id` (0-7)

- **`outlet_cycle`** - Power cycle an outlet (off, wait, on)
  - Parameters: `outlet_id` (0-7)

- **`bulk_outlet_operation`** - Perform operations on multiple outlets
  - Parameters: `action` ("on", "off", or "cycle"), optional `outlet_ids` array

### Status and Monitoring

- **`get_outlet_state`** - Get the power state of a specific outlet
  - Parameters: `outlet_id` (0-7)

- **`get_all_outlet_states`** - Get power states of all outlets

- **`get_outlet_info`** - Get detailed info about an outlet (name, state, lock status)
  - Parameters: `outlet_id` (0-7)

- **`get_power_metrics`** - Get real-time power measurements (voltage, current, power, energy)

- **`get_device_info`** - Get device information (serial, firmware version, etc.)

### Configuration

- **`set_outlet_name`** - Rename an outlet
  - Parameters: `outlet_id` (0-7), `name` (string, max 16 chars)

## Usage Examples

Once configured, you can use natural language with your MCP client:

```
"Turn on outlet 3"
"What's the current power consumption?"
"Cycle the server outlet"
"Show me all outlet states"
"Rename outlet 0 to 'Lab Server'"
"Turn off all outlets"
```

## Running the Server

### Stdio Transport (Local)

For local MCP clients like Claude Desktop or Warp:

```bash
# Set environment variables
export POWER_SWITCH_HOST="192.168.0.100"
export POWER_SWITCH_PASSWORD="your-password"
export POWER_SWITCH_USERNAME="admin"  # Optional, defaults to "admin"

# Run the stdio server
python -m power_switch_pro_mcp.server
```

The server will start and wait for MCP protocol messages on stdin/stdout.

### HTTP Transport (Remote)

For remote access using the MCP streamable-http transport:

```bash
# Set environment variables
export POWER_SWITCH_HOST="192.168.0.100"
export POWER_SWITCH_PASSWORD="your-password"
export POWER_SWITCH_USERNAME="admin"  # Optional, defaults to "admin"

# Run the HTTP server (default port 5000)
python -m power_switch_pro_mcp.http_server

# Or specify a custom port
PORT=3000 python -m power_switch_pro_mcp.http_server
```

The HTTP server will be available at `http://localhost:5000` and supports the MCP streamable-http protocol.

## Docker Deployment

### Using Pre-built Image from GitHub Container Registry

The easiest way to run the server is using the pre-built Docker image:

```bash
# Pull the latest image
docker pull ghcr.io/bryankemp/power-switch-pro-mcp:latest

# Run the container
docker run -d \
  -p 5000:5000 \
  -e POWER_SWITCH_HOST="192.168.0.100" \
  -e POWER_SWITCH_PASSWORD="your-password" \
  -e POWER_SWITCH_USERNAME="admin" \
  --name power-switch-pro-mcp \
  ghcr.io/bryankemp/power-switch-pro-mcp:latest
```

### Using Docker Compose (Recommended)

```bash
# Copy and configure environment variables
cp .env.docker .env
# Edit .env with your Power Switch Pro settings

# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down
```

### Using Docker Directly

```bash
# Build the image
docker build -t power-switch-pro-mcp .

# Run the container
docker run -d \
  -p 5000:5000 \
  -e POWER_SWITCH_HOST="192.168.0.100" \
  -e POWER_SWITCH_PASSWORD="your-password" \
  -e POWER_SWITCH_USERNAME="admin" \
  --name power-switch-pro-mcp \
  power-switch-pro-mcp

# View logs
docker logs -f power-switch-pro-mcp

# Stop the container
docker stop power-switch-pro-mcp
```

## CI/CD

This project uses GitHub Actions to automatically build and publish Docker images to GitHub Container Registry (ghcr.io).

### Automated Docker Builds

Docker images are automatically built and published:
- **On every push to main**: Tagged as `latest` and `main-{sha}`
- **On version tags** (e.g., `v1.0.0`): Tagged with semantic versions
- **On pull requests**: Built but not published (for testing)

The workflow builds multi-platform images for:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/Apple Silicon)

### Available Tags

- `latest` - Latest stable build from main branch
- `v1.0.0`, `v1.0`, `v1` - Semantic version tags
- `main-{sha}` - Specific commit from main branch

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/bryankemp/power-switch-pro-mcp.git
cd power-switch-pro-mcp

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Code Quality

This project uses:

- **Black** - Code formatting (line length: 100)
- **Ruff** - Fast Python linting
- **mypy** - Static type checking
- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality

Run checks:

```bash
# Format code
black src

# Lint code
ruff check src

# Type check
mypy src

# Run all checks together
black src && ruff check src && mypy src

# Run tests
pytest
```

### Git Hooks

The project includes automated git hooks for code quality and Docker testing:

#### Pre-commit Hooks

Automatically run on every commit:
- Black code formatting
- Ruff linting
- mypy type checking
- YAML/TOML validation

#### Pre-push Hook

Automatically run before every push:
- Docker image build test
- Container runtime verification
- HTTP endpoint health check

#### Installation

```bash
# Install pre-commit framework
pip install pre-commit

# Install all git hooks
pre-commit install
./hooks/install.sh

# Run hooks manually on all files
pre-commit run --all-files
```

## Project Structure

```
power-switch-pro-mcp/
├── src/
│   └── power_switch_pro_mcp/
│       ├── __init__.py
│       ├── server.py          # Stdio MCP server implementation
│       └── http_server.py     # HTTP MCP server implementation
├── docs/                       # Sphinx documentation
├── tests/                      # Test suite
├── hooks/                      # Git hooks
│   ├── pre-push               # Pre-push hook (Docker testing)
│   └── install.sh             # Hook installation script
├── Dockerfile                  # Docker container definition
├── docker-compose.yml         # Docker Compose configuration
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── LICENSE                    # BSD-3-Clause license
├── .env.example               # Example environment configuration
└── .env.docker                # Docker environment template
```

## Security Considerations

- **Never commit credentials** - Use environment variables or secure configuration
- **Use HTTPS** - Enable `POWER_SWITCH_USE_HTTPS=true` when possible
- **Network Security** - Ensure your power switch is on a secure network
- **Access Control** - Use the admin account or create restricted users on the device

## Troubleshooting

### Server won't start

- Check that environment variables are set correctly
- Verify you can reach the device at the configured host
- Ensure the password is correct

### "Authentication Error"

- Double-check your username and password
- Verify the device firmware supports REST API (1.7.0+)

### Tools not appearing in client

- Restart your MCP client after configuration changes
- Check the client's logs for MCP server errors
- Verify the server starts successfully in standalone mode

## Related Projects

- [power-switch-pro](https://github.com/bryankemp/power_switch_pro) - The underlying Python library
- [MCP Specification](https://modelcontextprotocol.io) - Model Context Protocol documentation

## License

BSD-3-Clause License - See LICENSE file for details

## Author

Bryan Kemp (bryan@kempville.com)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run code quality checks
5. Submit a pull request

## Support

- **Issues**: GitHub Issues
- **Email**: bryan@kempville.com
- **Documentation**: [power-switch-pro.readthedocs.io](https://power-switch-pro.readthedocs.io)
# Test change
