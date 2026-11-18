"""The spec check of ``gov discover --check``: the spec-writing skill's own check, read from the kernel skill, with two
additions (W2-36): an HTML comment is not content, and a part left as slots is missing; and ``## Verify`` holds one
``- K<n>: <verify>`` line per KPI. Nothing is printed here and nothing is written (the skill's P1 file included)."""

from __future__ import annotations

import re
import types
from pathlib import Path

SKILL_REL = "governance/kernel/skills/spec-writing/check_spec.py"
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_loaded: dict[str, types.ModuleType] = {}


def skill(root: Path) -> types.ModuleType:
    """The kernel skill's ``check_spec.py``: the project's copy (a Gov OS tree keeps the kernel under ``template/``),
    else the one Gov OS ships. Run from its source, so no bytecode is written beside it."""
    from gov.adopt.fabric import shipped

    for place in (Path(root) / "template" / SKILL_REL, Path(root) / SKILL_REL):
        if place.is_file():
            break
    else:
        place = shipped("template/" + SKILL_REL, root)
    if str(place) not in _loaded:
        module = types.ModuleType("check_spec")
        module.__file__ = str(place)
        exec(compile(place.read_text(encoding="utf-8"), str(place), "exec"), module.__dict__)
        _loaded[str(place)] = module
    return _loaded[str(place)]


def _sections(module, text: str) -> dict[str, list[str]]:
    return module.split_sections(COMMENT.sub("", text))


def kpis(text: str, module) -> list[tuple[str, str, str]]:
    """``(number, behaviour, Fails if: text)`` of each KPI of the spec, its lines joined by one space."""
    found, into = [], None
    for line in _sections(module, text).get("kpis", []):
        kpi, fails = module.KPI_LINE.match(line), module.FAILS_LINE.match(line)
        if kpi:
            found.append([kpi.group(2), [kpi.group(3)], []])
            into = found[-1][1]
        elif fails and found:
            found[-1][2].append(fails.group(1))
            into = found[-1][2]
        elif module.LIST_ITEM.match(line) or module.KPI_ID_LINE.match(line):
            into = None
        elif into is not None and line.strip():
            into.append(line)
    return [(n, " ".join(" ".join(b).split()), " ".join(" ".join(f).split())) for n, b, f in found]


def verifies(text: str, module) -> dict[str, str]:
    """``{K number: verify}`` of the ``## Verify`` lines, a verify's following lines joined to it."""
    found, into = {}, None
    for line in _sections(module, text).get("verify", []):
        match = module.KPI_LINE.match(line)
        if match:
            into = match.group(2)
            found[into] = found.get(into, "") + " " + match.group(3)
        elif into is not None and line.strip() and not module.LIST_ITEM.match(line):
            found[into] += " " + line
    return {n: " ".join(v.split()) for n, v in found.items()}


def bullets(text: str, part: str, module) -> list[str]:
    """The bullets under the ``##`` heading ``part``, each with its continuation lines."""
    found = []
    for line in _sections(module, text).get(part.lower(), []):
        if BULLET.match(line):
            found.append(BULLET.sub("", line).strip())
        elif found and line.strip():
            found[-1] += " " + line.strip()
    return found


def refusals(root: Path, text: str) -> list[str]:
    """The ``REFUSED`` lines of the spec (and the skill's ``P1`` lines), none when it passes."""
    module = skill(root)
    text = COMMENT.sub("", text)
    sections, out, unsecured = module.split_sections(text), [], []
    for part in module.PARTS:
        lines = sections.get(part.lower(), [])
        body = [BULLET.sub("", line) for line in lines if line.strip()]
        if not body or all(module.is_placeholder(line) for line in body):
            out.append(f"REFUSED {part}: missing")
        elif part == "KPIs":
            out += module.check_kpis(lines)
        elif part == "Test data":
            found, unsecured = module.check_data(lines)
            out += found
    out += [f"P1 Test data: {row['source']} cannot be secured" for row in unsecured]
    wanted, given = {n for n, _, _ in kpis(text, module)}, verifies(text, module)
    if wanted:
        out += [f"REFUSED Verify: K{n} has no verify" for n in sorted(wanted, key=int)
                if n not in given or module.is_placeholder(given[n])]
        out += [f"REFUSED Verify: K{n} is not a KPI" for n in sorted(given, key=int) if n not in wanted]
    return out
