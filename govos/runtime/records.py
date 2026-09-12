"""Governed records: YAML records and Markdown-with-frontmatter records under spec/ (and governance/project/)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml

from govos.runtime.util import GovError, read_text, write_text, write_yaml

FRONTMATTER_RX = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)
ID_RX = re.compile(r"^[A-Z]{1,6}-[A-Za-z0-9._-]+$")
RELATION_FIELDS = {
    "depends_on": "DEPENDS_ON", "blocks": "BLOCKS", "implements": "IMPLEMENTS", "governed_by": "GOVERNED_BY",
    "validated_by": "VALIDATED_BY", "tests": "TESTS", "derived_from": "DERIVED_FROM", "affects": "AFFECTS",
    "supersedes": "SUPERSEDES", "requirements": "GOVERNED_BY", "decisions": "GOVERNED_BY", "scenarios": "VALIDATED_BY",
    "acceptance_tests": "VALIDATED_BY", "dependencies": "DEPENDS_ON", "feature": "REALISES", "task": "PRODUCES",
    "consumers": "CONSUMES", "producers": "PRODUCES", "required_skills": "USES", "required_tools": "USES",
    "interfaces": "USES", "lessons": "LEARNED_FROM", "sources": "DERIVED_FROM", "cit": "GENERATED_FROM",
    "scenario": "TESTS", "human_gate": "BLOCKS",
}
TYPE_PREFIX = {"project": "PRJ", "feature": "F", "requirement": "REQ", "decision": "D", "task": "TASK", "scenario": "SCN",
               "test-obligation": "TST", "interface": "API", "experiment": "EXP", "release": "REL", "lesson": "L",
               "report": "RPT", "research": "RES", "human-gate": "HDG", "cit": "CIT", "checkpoint": "CKPT",
               "handoff": "HND", "audit": "AUD", "architecture": "ARCH", "workflow": "WF", "legacy": "LEG"}
TYPE_DIR = {"project": "spec/product", "feature": "spec/features", "requirement": "spec/requirements", "decision": "spec/decisions",
            "task": "spec/tasks", "scenario": "spec/scenarios", "test-obligation": "spec/tasks", "interface": "spec/interfaces",
            "experiment": "spec/experiments", "lesson": "spec/lessons", "report": "spec/reports", "research": "spec/research",
            "human-gate": "spec/decisions", "cit": "spec/decisions", "checkpoint": "spec/reports/checkpoints", "handoff": "spec/planning",
            "audit": "spec/audits", "architecture": "spec/architecture", "workflow": "spec/workflows", "legacy": "archive/governance"}


@dataclass
class Record:
    path: str
    data: dict[str, Any]
    body: str = ""
    format: str = "yaml"  # yaml | md
    problems: list[str] = field(default_factory=list)

    @property
    def id(self) -> str | None:
        return self.data.get("id")

    @property
    def type(self) -> str | None:
        return self.data.get("type")

    @property
    def status(self) -> str:
        return str(self.data.get("status", "UNKNOWN"))

    @property
    def title(self) -> str:
        return str(self.data.get("title") or self.data.get("objective") or self.data.get("name") or self.id or self.path)

    def text(self) -> str:
        """Full indexable text (structured fields + body)."""
        parts = [self.title]
        for k in ("summary", "objective", "question", "proposal", "rationale", "problem_statement", "conclusion", "statement"):
            v = self.data.get(k)
            if isinstance(v, str):
                parts.append(v)
        if isinstance(self.data.get("body"), str):
            parts.append(self.data["body"])
        if self.body:
            parts.append(self.body)
        for k in ("given", "when", "then", "acceptance_criteria", "outcomes", "options"):
            v = self.data.get(k)
            if isinstance(v, list):
                parts.extend(str(x if not isinstance(x, dict) else x.get("description", x)) for x in v)
        return "\n".join(p for p in parts if p)

    def relations(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for r in self.data.get("relations") or []:
            if isinstance(r, dict) and r.get("type") and r.get("target"):
                out.append((str(r["type"]), str(r["target"])))
        for fld, etype in RELATION_FIELDS.items():
            v = self.data.get(fld)
            if isinstance(v, str) and ID_RX.match(v):
                out.append((etype, v))
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and ID_RX.match(x):
                        out.append((etype, x))
                    elif isinstance(x, dict) and isinstance(x.get("id"), str) and ID_RX.match(x["id"]):
                        out.append((etype, x["id"]))
        return sorted(set(out))


def parse_record_text(text: str, path: str) -> Record | None:
    if path.endswith((".yaml", ".yml")):
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            return Record(path=path, data={}, problems=[f"yaml error: {e}"])
        if not isinstance(data, dict) or "id" not in data or "type" not in data:
            return None
        return Record(path=path, data=data, format="yaml")
    if path.endswith(".md"):
        m = FRONTMATTER_RX.match(text)
        if not m:
            return None
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            return Record(path=path, data={}, problems=[f"frontmatter error: {e}"])
        if not isinstance(data, dict) or "id" not in data:
            return None
        return Record(path=path, data=data, body=m.group(2), format="md")
    return None


def load_record(root: Path, relpath: str) -> Record | None:
    return parse_record_text(read_text(root / relpath), relpath)


def iter_records(root: Path, files: Iterator[tuple[Path, str]]) -> Iterator[Record]:
    for abs_path, relp in files:
        if not relp.endswith((".yaml", ".yml", ".md")):
            continue
        try:
            rec = parse_record_text(read_text(abs_path), relp)
        except OSError:
            continue
        if rec is not None:
            yield rec


def save_record(root: Path, rec: Record) -> Path:
    p = root / rec.path
    if rec.format == "md":
        fm = yaml.safe_dump(rec.data, sort_keys=False, allow_unicode=True)
        write_text(p, f"---\n{fm}---\n{rec.body}")
    else:
        write_yaml(p, rec.data)
    return p


def record_path_for(record_type: str, rid: str) -> str:
    d = TYPE_DIR.get(record_type)
    if not d:
        raise GovError(f"no canonical directory for record type {record_type}", "RECORD_TYPE_UNKNOWN")
    return f"{d}/{rid}.yaml"


def state_class_for(rec: Record, authority_policy: dict[str, Any]) -> str:
    sc = rec.data.get("state_class")
    if sc:
        return str(sc)
    return str((authority_policy.get("default_state_class_by_type") or {}).get(rec.type, "NARRATIVE"))
