"""Regex-based structural facts for JS/TS/Go-like sources (fallback when no language server is registered)."""
from __future__ import annotations

import re

from govos.runtime.code_intelligence.python_ast import ModuleFacts, Symbol

PATTERNS = [
    (re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\("), "function"),
    (re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)"), "class"),
    (re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"), "function"),
    (re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_][\w]*)\s*\("), "function"),
    (re.compile(r"^\s*(?:pub\s+)?fn\s+([A-Za-z_][\w]*)"), "function"),
]
IMPORT_RX = [re.compile(r"""^\s*import\s+.*?from\s+['"]([^'"]+)['"]"""), re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)"""),
             re.compile(r"""^\s*import\s+['"]([^'"]+)['"]""")]


def analyze(source: str, module_name: str) -> ModuleFacts:
    lines = source.splitlines()
    symbols = [Symbol(module_name, module_name, "module", 1, max(1, len(lines)))]
    imports: list[str] = []
    for i, line in enumerate(lines, start=1):
        for rx, kind in PATTERNS:
            m = rx.match(line)
            if m:
                symbols.append(Symbol(m.group(1), m.group(1), kind, i, i, None, line.strip()[:120]))
                break
        for rx in IMPORT_RX:
            m = rx.search(line)
            if m:
                imports.append(m.group(1))
    return ModuleFacts(symbols=symbols, imports=sorted(set(imports)))
