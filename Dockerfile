# Multi-stage Dockerfile for Power Switch Pro MCP Server
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* || true

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src/ ./src/

# Install the package
# Install power_switch_pro v1.1.0 from PyPI
RUN pip install --upgrade pip && \
    pip install "power-switch-pro>=1.1.0" && \
    pip install .

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Expose port for HTTP server
EXPOSE 8000

# Default to HTTP server (can be overridden)
CMD ["python", "-m", "power_switch_pro_mcp.http_server"]
