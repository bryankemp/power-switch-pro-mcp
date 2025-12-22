Power Switch Pro MCP Documentation
===================================

An MCP (Model Context Protocol) server that provides tools for controlling and monitoring Digital Loggers Power Switch Pro devices.

Features
--------

* 🔌 **Outlet Control** - Turn outlets on/off/cycle individually or in bulk
* 📊 **Power Monitoring** - Read real-time voltage, current, power, and energy metrics
* 📝 **Device Management** - Get device info and configure outlet names
* 🔒 **Secure** - Uses HTTP Digest Authentication via environment variables
* 🚀 **Easy Integration** - Works with any MCP-compatible client (Warp, Claude Desktop, etc.)
* 🌐 **Multiple Transports** - Supports both stdio (local) and HTTP (remote) via MCP streamable-http transport
* 🐳 **Docker Ready** - Easy containerized deployment with docker-compose

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install power-switch-pro-mcp

Configuration
~~~~~~~~~~~~~

Set environment variables for your Power Switch Pro device:

.. code-block:: bash

   export POWER_SWITCH_HOST="192.168.0.100"
   export POWER_SWITCH_PASSWORD="your-password"

Running the Server
~~~~~~~~~~~~~~~~~~

**Stdio Transport (Local)**

.. code-block:: bash

   python -m power_switch_pro_mcp.server

**HTTP Transport (Remote)**

.. code-block:: bash

   python -m power_switch_pro_mcp.http_server

**Docker**

.. code-block:: bash

   cp .env.docker .env
   # Edit .env with your settings
   docker-compose up -d

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   usage
   docker

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/server
   api/http_server

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
