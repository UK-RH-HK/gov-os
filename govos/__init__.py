"""Governance OS (agentic-engineering-os) runtime and CLI.

Logical layout mapping (see docs/ARCHITECTURE.md):
  runtime/  -> govos.runtime.*
  cli/      -> govos.cli
  tools/    -> govos.tools  (code) ; tools/ (canonical registries, data)
  migrations/ -> govos.migrations (engine) ; migrations/ (declarative migration definitions, data)
"""
from __future__ import annotations

FRAMEWORK_NAME = "agentic-engineering-os"
VERSION = "4.1.2"
CLI_VERSION = "4.1.2"
RUNTIME_VERSION = "4.1.2"
INDEX_VERSION = "4.1.2-idx1"
