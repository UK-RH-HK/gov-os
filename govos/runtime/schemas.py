"""Schema validation against the installed kernel's schemas (or the bundled canonical schemas)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

from govos.runtime.kernel import canonical_framework_dir
from govos.runtime.util import GovError, read_json


class SchemaRegistry:
    def __init__(self, schema_dir: Path | None = None):
        self.schema_dir = Path(schema_dir) if schema_dir else canonical_framework_dir() / "schemas"
        self._cache: dict[str, dict] = {}

    def get(self, name: str) -> dict[str, Any]:
        if name not in self._cache:
            p = self.schema_dir / f"{name}.schema.json"
            if not p.exists():
                raise GovError(f"Schema not found: {name}", "SCHEMA_NOT_FOUND")
            self._cache[name] = read_json(p)
        return self._cache[name]

    def errors(self, name: str, data: Any) -> list[str]:
        schema = self.get(name)
        v = jsonschema.Draft202012Validator(schema)
        out = []
        for e in sorted(v.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in e.path) or "<root>"
            out.append(f"{loc}: {e.message}")
        return out

    def validate(self, name: str, data: Any, context: str = "") -> None:
        errs = self.errors(name, data)
        if errs:
            raise GovError(f"Schema validation failed for {name} {context}: " + "; ".join(errs[:6]), "SCHEMA_INVALID", {"errors": errs})

    def names(self) -> list[str]:
        return sorted(p.name[: -len(".schema.json")] for p in self.schema_dir.glob("*.schema.json"))


@lru_cache(maxsize=8)
def registry_for(schema_dir: str | None) -> SchemaRegistry:
    return SchemaRegistry(Path(schema_dir) if schema_dir else None)
