"""Repository contract and path map: what belongs where, what may be indexed, who may write it."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from govos.runtime.util import glob_match, read_yaml

SECRET_CLASS = "secret"
DEFAULT_RULE = {
    "class": "unknown", "semantic_index": False, "lexical_index": False, "graph_index": False, "code_index": False,
    "default_retrieval": True, "mutation": "allowed", "agent_read": "allowed", "export": "denied",
    "sensitivity": "internal", "namespace": "unknown", "owner_role": None,
}
CLASS_DEFAULTS: dict[str, dict[str, Any]] = {
    "source": {"semantic_index": True, "lexical_index": True, "graph_index": True, "code_index": True},
    "test": {"semantic_index": True, "lexical_index": True, "graph_index": True, "code_index": True},
    "authoritative": {"semantic_index": True, "lexical_index": True, "graph_index": True},
    "evidence": {"semantic_index": True, "lexical_index": True, "graph_index": True},
    "narrative": {"semantic_index": True, "lexical_index": True},
    "derived": {"semantic_index": False, "lexical_index": False, "graph_index": False},
    "generated": {"semantic_index": False, "lexical_index": False, "graph_index": False, "mutation": "generated"},
    "historical": {"semantic_index": False, "lexical_index": True, "default_retrieval": False, "mutation": "restricted"},
    "secret": {"semantic_index": False, "lexical_index": False, "graph_index": False, "code_index": False,
               "default_retrieval": False, "agent_read": "prohibited", "export": "denied", "sensitivity": "secret", "namespace": "secret"},
    "runtime-data": {"semantic_index": False, "lexical_index": False, "graph_index": False},
    "devops": {"semantic_index": True, "lexical_index": True},
    "tooling": {"semantic_index": True, "lexical_index": True, "code_index": True},
    "unknown": {},
}
ALWAYS_EXCLUDED_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".governance-runtime", ".venv", "venv"}


@dataclass
class PathDecision:
    path: str
    rule_pattern: str | None
    attrs: dict[str, Any] = field(default_factory=dict)

    @property
    def cls(self) -> str:
        return self.attrs.get("class", "unknown")

    @property
    def is_secret(self) -> bool:
        return self.cls == SECRET_CLASS or self.attrs.get("sensitivity") == "secret"

    def indexable(self, kind: str) -> bool:
        if self.is_secret:
            return False
        return bool(self.attrs.get(f"{kind}_index", False))


class RepositoryContract:
    def __init__(self, data: dict[str, Any]):
        self.data = data
        self.roots: dict[str, str] = {k: v.rstrip("/") + "/" for k, v in data.get("roots", {}).items()}
        self.rules: list[dict[str, Any]] = list(data.get("paths", []))

    @classmethod
    def load(cls, path: Path) -> "RepositoryContract":
        return cls(read_yaml(path))

    def decide(self, path: str) -> PathDecision:
        path = path.replace("\\", "/").lstrip("./")
        attrs = dict(DEFAULT_RULE)
        matched: str | None = None
        secret_locked = False
        for rule in self.rules:
            pat = rule["pattern"]
            if glob_match(pat, path):
                cls = rule.get("class", "unknown")
                merged = dict(DEFAULT_RULE)
                merged.update(CLASS_DEFAULTS.get(cls, {}))
                merged.update({k: v for k, v in rule.items() if k != "pattern"})
                if secret_locked and cls != SECRET_CLASS:
                    # A secret classification can never be downgraded by a later rule.
                    continue
                attrs = merged
                matched = pat
                if cls == SECRET_CLASS:
                    secret_locked = True
        if attrs.get("namespace") in (None, "unknown"):
            attrs["namespace"] = self.namespace_for(path)
        return PathDecision(path=path, rule_pattern=matched, attrs=attrs)

    def namespace_for(self, path: str) -> str:
        for name, root in self.roots.items():
            if path.startswith(root):
                return name
        return "root"

    def root(self, name: str) -> str:
        return self.roots.get(name, name + "/")

    def owner_role(self, path: str) -> str | None:
        return self.decide(path).attrs.get("owner_role")

    def mutation_allowed(self, path: str) -> str:
        return self.decide(path).attrs.get("mutation", "allowed")

    def to_framework_json(self, framework: str, version: str) -> dict[str, Any]:
        return {
            "framework": framework,
            "version": version,
            "generated": True,
            "source": "governance/project/REPOSITORY_CONTRACT.yaml",
            "governance_dir": "governance",
            "roots": self.roots,
            "paths": {r["pattern"]: {k: v for k, v in r.items() if k != "pattern"} for r in self.rules},
        }


def iter_repo_files(root: Path, include_runtime: bool = False, extra_excludes: set[str] | None = None):
    """Yield (abs_path, rel_posix) for every file, skipping VCS/runtime/cache directories deterministically."""
    root = Path(root)
    ex = set(ALWAYS_EXCLUDED_DIRS) | (extra_excludes or set())
    if include_runtime:
        ex.discard(".governance-runtime")
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(d.iterdir(), key=lambda p: p.name)
        except OSError:
            continue
        for p in reversed(entries):
            if p.is_symlink():
                continue
            if p.is_dir():
                if p.name in ex:
                    continue
                stack.append(p)
            elif p.is_file():
                yield p, p.relative_to(root).as_posix()
