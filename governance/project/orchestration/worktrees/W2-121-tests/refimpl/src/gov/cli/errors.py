"""GovError: a governance error, exit code 1 with its code in the JSON envelope (API-0002).

A command that declares exit codes of its own (``EXIT_CODES``, see
``gov.cli.main``) may give one as ``exit_code``.
"""

from __future__ import annotations


class GovError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None, exit_code: int = 1):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.exit_code = exit_code


def not_implemented(name: str) -> GovError:
    return GovError("NOT_IMPLEMENTED", f"gov {name} is reserved and not built yet", {"command": name})
