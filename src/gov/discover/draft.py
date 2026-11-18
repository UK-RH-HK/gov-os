"""What ``gov discover <words>`` writes (W2-36): the change name, the proposal record, the readiness record, and the
draft spec in the spec-writing form with its open questions as packages, its sources read and its memory line. Pure
but for reading the project; no clock, and every list is sorted, so the same inputs give the same bytes."""

from __future__ import annotations

import re
from pathlib import Path

from gov.readiness.checker import CHANGES_REL, EXTRA, KEYS, MANDATORY, SCHEMA_REL

STOP = set("""a an the to of for in on at by and or we i you it can could should would will how what why when where which
who do does is are be please let us me my our with into this that""".split())
MAX_WORDS, MAX_SOURCES = 6, 20
ROOTS = ("docs", "openspec/specs", CHANGES_REL, ".tickets")  # where the project says what exists, beside its root *.md
PARTS = ("Problem", "Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope",
         "Open questions", "Accepted by")
GUIDE = {
    "Users and scenarios": ("Who uses it, and the situations they meet, each as a short story.",
                            "- <who uses it, and what happens to them>"),
    "Goals": ("What the change makes true.", "- <what the change makes true>"),
    "Non-goals": ("What it does not try to do, though a reader might expect it.", "- <what it leaves alone>"),
    "KPIs": ("Each outcome an observer sees or measures, with its failure line; no code names in either.",
             "- K1: <behaviour>\n  Fails if: <observable failure>"),
    "Test data": ("A table, one row per source: source | kind | owner | licence or recipe | privacy | secrets | "
                  "hidden half | secured.", "- <the table of the data the tests need>"),
    "Out of scope": ("What is left to other work, each with where it goes.", "- <what is left out, and where it goes>"),
    "Accepted by": ("Who accepts the spec, by role or name, and on what evidence.", "- <role or name, and the evidence>"),
}
VERIFY_GUIDE = "One line per KPI: how it is checked, a command and its result. A verify may name code."
CLASS = {"inputs": ("data", "product-spec"), "data_model": ("data", "product-spec"),
         "test_data": ("data", "product-spec"), "nfr": ("research", "research"),
         "integrations": ("research", "research"), "performance": ("research", "research"),
         "cost": ("research", "research"), "acceptance_tests": ("test-design", "independent-test-designer")}
DEFAULT_CLASS = ("discovery", "product-spec")
COST = {"spec": "the session writes it into the spec now", "ticket": "a ticket and a session before the spec can close",
        "na": "the owner accepts the row is out of scope here"}


def words_of(words: list[str]) -> str:
    return " ".join(" ".join(words).split())


def change_name(words: str) -> str:
    """The words lower-cased, split on anything not a letter or digit, without the stop words, the first six joined."""
    return "-".join([w for w in re.findall(r"[^\W_]+", words.lower()) if w not in STOP][:MAX_WORDS])


def required(profile: str, types: list[str]) -> list[int]:
    """The rows the readiness checker requires of a specification at ``profile`` with ``types``."""
    if profile == "FULL":
        return sorted(KEYS)
    return sorted(set(MANDATORY).union(*(EXTRA[name] for name in types if profile == "STANDARD")))


def class_of(key: str) -> tuple[str, str]:
    """``(ticket class, role)`` of the gap ticket of a row."""
    return CLASS.get(key, DEFAULT_CLASS)


def row_names(root: Path) -> dict[int, str]:
    """The schema's name of each row, by number; the key where the project's schema cannot be read."""
    import yaml

    try:
        schema = yaml.safe_load((Path(root) / SCHEMA_REL).read_text(encoding="utf-8"))
        return {row["n"]: str(row["name"]) for row in schema["dimensions"]}
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError):
        return dict(KEYS)


def readiness_text(root: Path) -> str:
    """The schema template's record, every row MISSING; written from the rows when the project holds no template."""
    template = Path(root) / "openspec/schemas/feature-readiness/templates/readiness.yaml"
    if template.is_file():
        return template.read_text(encoding="utf-8")
    rows = [f"  - {{n: {n}, key: {key}, state: MISSING, evidence: [], reason: null, gap_ticket: null}}"
            for n, key in KEYS.items()]
    return "\n".join(["rows:", *rows, ""])


def proposal_text(change: str, words: str, profile: str, types: list[str], ticket: str) -> str:
    return (f"---\nid: SPEC-{change}\ntype: specification\nstatus: DRAFT\nstate_class: AUTHORITATIVE\n"
            f"profile: {profile}\nspine: false\ncapability_types: [{', '.join(types)}]\n"
            f"discovery_ticket: {ticket}\n---\n# {words}\n")


def _package(question: str, options: str, recommendation: str) -> str:
    return f"- Question: {question}\n  - Options: {options}\n  - Recommendation: {recommendation}"


def questions(profile: str, types: list[str], ask_profile: bool, names: dict[int, str]) -> str:
    packages = []
    for n in required(profile, types):
        key = KEYS[n]
        name = names.get(n, key)
        options = (f"answer it in this spec (cost: {COST['spec']}); open a gap ticket (cost: {COST['ticket']}); "
                   f"N/A with a reason (cost: {COST['na']})")
        gap = class_of(key) != DEFAULT_CLASS or key == "acceptance_tests"
        packages.append(_package(
            f"Row {n}, {key} ({name}): what does this change settle for it?", options,
            "open a gap ticket: a session with the right role settles it, and the spec waits for it" if gap
            else "answer it in this spec when the idea already settles it, else open a gap ticket"))
    if ask_profile:
        packages.append(_package(
            "Which profile does this change need (LITE, STANDARD or FULL), and which capability types does it have?",
            "LITE, the ten mandatory rows only (cost: less is checked before the spec closes); STANDARD with the "
            "capability types it names (cost: more rows to settle, each with its own ticket); FULL (cost: all 26 rows)",
            "LITE, unless a capability type applies: then STANDARD with that type"))
    return "\n\n".join(packages)


def spec(words: str, profile: str, types: list[str], ask_profile: bool, sources: list[str], memory: str,
         names: dict[int, str] | None = None) -> str:
    """The draft ``spec.md``: the nine parts, then ``## Verify`` and ``## Sources read``."""
    out = []
    for part in PARTS:
        if part == "Problem":
            body = words
        elif part == "Open questions":
            body = ("<!-- Each question is a package: its options with their cost, and a recommendation. -->\n"
                    + questions(profile, types, ask_profile, names or {}))
        else:
            guide, slot = GUIDE[part]
            body = f"<!-- {guide} -->\n{slot}"
        out.append(f"## {part}\n{body}\n")
    out.append(f"## Verify\n<!-- {VERIFY_GUIDE} -->\n- K1: <how K1 is checked, and its result>\n")
    out.append("## Sources read\n" + "\n".join([*(sources or ["- none"]), memory]) + "\n")
    return "\n".join(out)


def sources(root: Path, change: str) -> list[str]:
    """``- <path>: <first matching line>`` of each file that holds a word of the change name, most words first then
    by path, at most 20. The files are those under ``docs/``, ``openspec/specs/``, ``openspec/changes/`` (other
    changes) and ``.tickets/``, and the root's ``*.md``."""
    root = Path(root)
    patterns = [re.compile(rf"\b{re.escape(word)}(?:s|es|ed|ing)?\b", re.I) for word in change.split("-")]
    files = [path for name in ROOTS for path in sorted((root / name).rglob("*")) if path.is_file()]
    files += sorted(path for path in root.glob("*.md") if path.is_file())
    found = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if rel.startswith(f"{CHANGES_REL}/{change}/") or path.stat().st_size > 1_000_000:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        text = "\n".join(lines)
        count = sum(bool(pattern.search(text)) for pattern in patterns)
        if count:
            first = next(line for line in lines if any(pattern.search(line) for pattern in patterns))
            found.append((-count, rel, " ".join(first.split())[:120]))
    return [f"- {rel}: {line}" for _, rel, line in sorted(found)[:MAX_SOURCES]]


def memory(root: Path, words: str) -> str:
    """``Memory:`` with the evidence paths of a ``gov retrieve`` on the words, or ``Memory: not available: <reason>``
    when it cannot run: never a failure of the command, and never a model or network call of this module's own."""
    import contextlib
    import io
    from types import SimpleNamespace

    try:
        from gov.retrieve.command import run

        args = SimpleNamespace(ticket=None, ids=[], radius=0, batch_size=None, bundle_budget=None, continuation=None,
                               query=words, root=str(root), role=None)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            bundle = run(Path(root), args, {})
        paths = sorted({item["path"] for item in bundle.get("evidence", []) if item.get("path")})
    except Exception as error:  # a store that is missing, a GovError, an import failure: stated, never raised
        reason = " ".join(str(getattr(error, "message", error)).split()) or type(error).__name__
        return f"Memory: not available: {getattr(error, 'code', type(error).__name__)}: {reason}"
    return "Memory: " + (", ".join(paths) if paths else "no evidence found")
