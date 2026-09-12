"""Secret and sensitivity scanning (T0). Fails closed: any hit blocks indexing/export of the unit."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from govos.runtime.util import glob_match, is_text_file, read_text

DEFAULT_PATTERNS = [
    {"id": "aws-access-key", "regex": r"AKIA[0-9A-Z]{16}"},
    {"id": "private-key-block", "regex": r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----"},
    {"id": "github-token", "regex": r"gh[pousr]_[A-Za-z0-9]{36,}"},
    {"id": "generic-api-key", "regex": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}"},
    {"id": "password-assignment", "regex": r"(?i)password\s*[=:]\s*['\"][^'\"\s]{8,}['\"]"},
]


@dataclass
class SecretHit:
    path: str
    pattern_id: str
    line: int
    excerpt: str  # redacted


class SecretScanner:
    def __init__(self, content_patterns: Iterable[dict[str, str]] | None = None, path_patterns: Iterable[str] | None = None,
                 identifiers: Iterable[str] | None = None):
        pats = list(content_patterns) if content_patterns else DEFAULT_PATTERNS
        self.patterns = [(p["id"], re.compile(p["regex"])) for p in pats]
        self.path_patterns = list(path_patterns or [])
        self.identifiers = [i for i in (identifiers or []) if i]

    def path_is_secret(self, relpath: str) -> bool:
        return any(glob_match(p, relpath) for p in self.path_patterns)

    def scan_text(self, text: str, relpath: str = "<text>") -> list[SecretHit]:
        hits: list[SecretHit] = []
        for ln, line in enumerate(text.splitlines(), start=1):
            for pid, rx in self.patterns:
                m = rx.search(line)
                if m:
                    hits.append(SecretHit(relpath, pid, ln, _redact(line, m.start())))
        return hits

    def scan_file(self, abs_path: Path, relpath: str, max_bytes: int = 2_000_000) -> list[SecretHit]:
        if not is_text_file(abs_path):
            return []
        try:
            if abs_path.stat().st_size > max_bytes:
                return []
            return self.scan_text(read_text(abs_path), relpath)
        except OSError:
            return []

    def identifier_hits(self, text: str) -> list[str]:
        low = text.lower()
        return [i for i in self.identifiers if i.lower() in low]


def _redact(line: str, start: int) -> str:
    prefix = line[:start][-40:]
    return (prefix + "[REDACTED]").strip()


def scanner_from_policies(security_policy: dict[str, Any], data_sensitivity: dict[str, Any] | None = None) -> SecretScanner:
    return SecretScanner(security_policy.get("secret_content_patterns"), security_policy.get("secret_path_patterns"),
                         (data_sensitivity or {}).get("identifiers_to_strip"))
