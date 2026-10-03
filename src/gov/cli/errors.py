"""GovError: a governance error, exit code 1 with its code in the JSON envelope (API-0002)."""

from __future__ import annotations


class GovError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
