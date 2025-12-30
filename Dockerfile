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
# Note: git is no longer needed now that power_switch_pro is on PyPI
RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY LICENSE ./
COPY src/ ./src/

# Install the package
# Install power_switch_pro from PyPI
RUN pip install --upgrade pip && \
    pip install power_switch_pro && \
    pip install .

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Expose port for HTTP server
EXPOSE 5000

# Default to HTTP server (can be overridden)
CMD ["python", "-m", "power_switch_pro_mcp.http_server"]
