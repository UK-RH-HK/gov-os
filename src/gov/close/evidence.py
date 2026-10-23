"""The evidence block of a close (W2-66; DEC-889 item 12, DEC-890 item 1, I4 F5).

The block states the scope (``scoped`` or ``full``, and why full), the base, the head and the tree, the changed
paths, every target run and why, every acceptance suite left out and why, every skip with its reason and their
count, every failing test with its failure text, and each run's JUnit XML file. A passed close states it in its
record's frontmatter and under ``result.evidence``; a refused close under ``error.details.evidence``.

The JUnit XML of a close goes under ``.gov-runtime/``, so that a refused close leaves nothing untracked but its
repair ticket.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

JUNIT_DIR = ".gov-runtime/close"
KEY = "evidence"
_SCOPE_KEYS = ("scope", "why_full", "base", "head", "tree", "changed", "selected", "left_out")


def junit_rel(ticket: str, stamp: str, number: int, run: str, form: str) -> str:
    """Where the JUnit XML of one run of a close goes, relative to the project."""
    return f"{JUNIT_DIR}/{ticket}/{stamp}/{number:02d}-{run}-{form}.xml"


def _node(root: Path, base: Path | None, case) -> str:
    """The pytest node id, relative to the project, of a JUnit ``testcase`` written with ``junit_family=xunit1``."""
    file = case.get("file") or ""
    classname, name = case.get("classname") or "", case.get("name") or ""
    rel = file
    for folder in filter(None, (base, root)):
        if file and (folder / file).is_file():
            rel = (folder / file).resolve().relative_to(root.resolve()).as_posix() \
                if (folder / file).resolve().is_relative_to(root.resolve()) else file
            break
    module = file[:-3].replace("/", ".") if file.endswith(".py") else ""
    classes = classname[len(module):].strip(".") if module and classname.startswith(module) else ""
    parts = [rel or classname] + [c for c in classes.split(".") if c] + [name]
    return "::".join(parts)


def read_junit(root: Path, xml_path: Path, base: Path | None = None) -> dict:
    """The cases, the skips and the failures a JUnit XML file states; empty where the file is missing or broken."""
    found = {"cases": [], "skips": [], "failures": []}
    try:
        tree = ET.parse(xml_path)
    except (OSError, ET.ParseError):
        return found
    for case in tree.iter("testcase"):
        node = _node(Path(root), base, case)
        found["cases"].append(node)
        for tag in ("failure", "error"):
            for element in case.findall(tag):
                text = (element.text or "").strip() or element.get("message") or tag
                found["failures"].append({"test": node, "text": text})
        for element in case.findall("skipped"):
            found["skips"].append({"test": node, "reason": element.get("message") or (element.text or "").strip()})
    return found


def block(plan: dict, runs: list[dict], junit_xml: list[str]) -> dict:
    """The evidence block from the selection's ``plan`` and what each run's JUnit XML states (``read_junit``)."""
    skips = [s for run in runs for s in run["skips"]]
    failures = [f for run in runs for f in run["failures"]]
    evidence = {key: plan[key] for key in _SCOPE_KEYS}
    evidence.update({
        "skips": skips,
        "skip_count": len(skips),
        "failures": failures,
        "junit_xml": list(junit_xml),
        "per_test_timeout": plan["per_test_timeout"],
        "distribution": plan["distribution"],
    })
    return evidence
