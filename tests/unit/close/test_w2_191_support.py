"""Planted projects for W2-191's unit tests (any project-relative test target). No test here: the helpers the
other files share.

The schema the fixture projects carry is the kernel's own with ``$defs.target`` replaced by the new target rule
(DEC-1199 (2): no leading ``/`` or ``\\``, no drive letter, no ``..`` segment, no backslash), planted at the
project's own ``governance/kernel/schemas/`` where ``select._schema`` reads it first (``SCHEMA_DIRS``). The tests are
therefore green before the kernel's new bytes land and after."""
from __future__ import annotations

import json

import yaml

from gov.close import select

from .conftest import REPO_ROOT, Repo

KERNEL_SCHEMA = REPO_ROOT / "template" / "governance" / "kernel" / "schemas" / select.SCHEMA_NAME
PLANTED_SCHEMA_REL = f"governance/kernel/schemas/{select.SCHEMA_NAME}"
TARGET_PATTERN = r"^(?![/\\])(?![A-Za-z]:)(?!(.*[/\\])?\.\.([/\\]|::|$))[^\\]+$"
TICKET_TEXT = "---\nid: P-{wbs}\nwbs_id: {wbs}\nallowed_paths:\n{paths}---\n"

OUTSIDE_SUITE = "governance/scripts/tests"
OUTSIDE_FILE = "product/tests/test_a.py"
OUTSIDE_CASE = f"{OUTSIDE_FILE}::test_a"


def new_schema(pattern: str | None = TARGET_PATTERN) -> dict:
    """The kernel's schema with the new target rule; ``pattern=None`` leaves any string a target (an edited copy
    that judges nothing about the target: the loader's own defence is then what refuses)."""
    schema = json.loads(KERNEL_SCHEMA.read_text(encoding="utf-8"))
    target = {"type": "string", "minLength": 1}
    if pattern is not None:
        target["pattern"] = pattern
    schema["$defs"]["target"] = target
    return schema


def schema_file(pattern: str | None = TARGET_PATTERN) -> dict:
    return {PLANTED_SCHEMA_REL: json.dumps(new_schema(pattern), indent=2) + "\n"}


def ticket(wbs: str, *paths: str) -> str:
    return TICKET_TEXT.format(wbs=wbs, paths="".join(f"- {p}\n" for p in paths))


def map_data(**more) -> dict:
    data = {"version": 1, "shared_core": ["src/core/**"],
            "record_only": [".tickets/**.md", "docs/**.md", "docs/close/nightly/*.json"],
            "record_reading": [OUTSIDE_CASE], "every_close": ["governance/scripts/tests/test_tool.py"],
            "couplings": [{"paths": ["governance/scripts/**"], "suites": [OUTSIDE_SUITE],
                           "why": "the scripts' suite lives beside them"}]}
    data.update(more)
    return data


def files(test_map: dict | None = None, schema: dict | None = None) -> dict:
    """An adopted project whose suites live outside ``tests/``, with its own ticket and a ``tests/`` suite."""
    out = {
        ".gitignore": ".gov-runtime/\n__pycache__/\n",
        ".tickets/P-W1-own.md": ticket("W1-own", "src/own/**"),
        "src/own/y.py": "y = 1\n", "src/core/z.py": "z = 1\n",
        "tests/unit/test_u.py": "def test_u():\n    pass\n",
        "tests/acceptance/W1-own/test_own.py": "def test_own():\n    pass\n",
        "governance/scripts/tool.py": "T = 1\n",
        "governance/scripts/tests/test_tool.py": "def test_t():\n    pass\n",
        "governance/scripts/tests/test_more.py": "def test_m():\n    pass\n",
        "product/app.py": "A = 1\n",
        "product/tests/test_a.py": "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n",
        "product/tests/test_c.py": "def test_c():\n    pass\n",
        "docs/notes.md": "# notes\n",
        **(schema if schema is not None else schema_file()),
    }
    out[select.MAP_REL] = yaml.safe_dump(test_map if test_map is not None else map_data())
    return out


def green(repo: Repo, name: str = "NR-1") -> str:
    """A green night naming the head as it is now: the base a scoped selection counts from."""
    head = repo.git("rev-parse", "HEAD").strip()
    repo.commit("night", files={f"{select.NIGHTLY_REL}/{name}.json": json.dumps({"head": head, "verdict": "green"})})
    return head


def project(repo: Repo, test_map: dict | None = None, schema: dict | None = None) -> str:
    """Commit the base project, then a green night naming it."""
    repo.commit("base", files=files(test_map, schema))
    return green(repo)


def targets(plan: dict) -> dict:
    return {entry["target"]: [why["reason"] for why in entry["why"]] for entry in plan["selected"]}
