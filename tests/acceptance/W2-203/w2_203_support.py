"""Shared helpers of the W2-203 acceptance tests (README; not a test module).

- The repository's own files and its base: ``REPO`` (the tree the tests sit in), ``BASE`` (the commit the ticket
  branched from), ``base_text`` (a file of the base, by ``git show``), ``clone_at`` (a throwaway repository in a
  temporary folder that borrows this repository's objects and holds one commit's tree: nothing is written here).
- The entry reader of the cases (``entries``, ``kept``): a heading ``### DEC-n`` to the line before the next such
  heading, a ``## `` heading or a ``---`` line, as the G4 lead's draft builder reads the register. One reader for the
  archive, the kept register and the base, so "verbatim" is the same question on each.
- The planted project (``plant``): a git repository with a path map that names a register, an archive and the archive
  namespace, a kept register, an archive, a ticket, a note, a test file and four commits. Ids are the project's own.
- The children (``child``, ``both``): ``gov`` and the checks as child processes with an empty ``HOME``.

Every id that no register holds stands in a string literal here, never in a comment.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pwd
import re
import sqlite3
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(REPO / "src"))

BASE = "05ed38219a9d013914d4efc5df8967c6ac9a5e13"
REGISTER_REL = "docs/DECISION_REGISTER.md"
ARCHIVE_REL = "docs/archive/DECISION_REGISTER-2026-11-19.md"
PATH_MAP_REL = "governance/project/path-map.yaml"
SCHEMA_REL = "template/governance/kernel/schemas/path-map.schema.json"
BUILDER_REL = "docs/emergency-2/audits/08-new-register.py"
ARCHIVE_KEY = "decision_register_archive"
ARCHIVE_TABLE = "archived_decisions"
FIRST_LATE = 1211  # every entry from this id on is in the kept register, whatever its class
STORE_REL = ".gov-runtime/store.db"

# --------------------------------------------------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------------------------------------------------

_GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
            "GIT_AUTHOR_DATE": "2026-11-11T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-11T12:00:00Z"}


def git(folder, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(folder), "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                           *args], capture_output=True, text=True, env={**_GIT_ENV, "HOME": str(folder)}, check=False)
    if done.returncode:
        raise AssertionError(f"git {' '.join(args)} failed in {folder}: {done.stderr}")
    return done.stdout


def write(root, rel: str, text: str) -> None:
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def commit(root, message: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD").strip()


def base_text(rel: str) -> str:
    """The file ``rel`` as the base commit holds it."""
    return git(REPO, "show", f"{BASE}:{rel}")


def head_of(root=REPO) -> str:
    return git(root, "rev-parse", "HEAD").strip()


def clone_at(folder: Path, commit_id: str) -> Path:
    """A repository at ``folder`` whose one branch is ``commit_id`` of this repository, checked out; its objects are
    this repository's, borrowed (``objects/info/alternates``). It holds no other ref, so a query over every ref
    reads this commit's history alone. This repository is only read."""
    folder.mkdir(parents=True)
    git(folder, "init", "-q", "-b", "main")
    common = Path(git(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
    (folder / ".git/objects/info/alternates").write_text(str(common / "objects") + "\n", encoding="utf-8")
    git(folder, "update-ref", "refs/heads/main", commit_id)
    git(folder, "checkout", "-q", "-f", "main")
    return folder


# --------------------------------------------------------------------------------------------------------------------
# The entries of a register's text
# --------------------------------------------------------------------------------------------------------------------

_HEAD = re.compile(r"### (DEC-[0-9]+)")
_CLASS = re.compile(r"\*\*Class:\*\* (\w+)")


def entries(text: str) -> list[tuple[str, str]]:
    """``(id, text)`` of each entry, in the file's order: from its heading to the line before the next entry heading,
    a ``## `` heading or a ``---`` line, without the blank lines that end it."""
    lines = text.split("\n")
    heads = [number for number, line in enumerate(lines) if _HEAD.match(line)]
    found = []
    for at, number in enumerate(heads):
        end = heads[at + 1] if at + 1 < len(heads) else len(lines)
        stop = number + 1
        while stop < end and not lines[stop].startswith("## ") and lines[stop] != "---":
            stop += 1
        found.append((_HEAD.match(lines[number]).group(1), "\n".join(lines[number:stop]).rstrip("\n")))
    return found


def number_of(record_id: str) -> int:
    return int(record_id.partition("-")[2])


def kept(record_id: str, text: str) -> bool:
    """Whether the kept register must hold the entry: an id from DEC-1211 on, or the class ``kept``."""
    if number_of(record_id) >= FIRST_LATE:
        return True
    found = _CLASS.search(text)
    return bool(found) and found.group(1) == "kept"


def cited(text: str) -> set[str]:
    return set(re.findall(r"(?<![A-Za-z0-9_])DEC-[0-9]+(?![A-Za-z0-9_])", text))


def without_entry(text: str, record_id: str) -> str:
    """``text`` less the entry ``record_id`` (its heading to the line before the next entry heading)."""
    lines, out, skipping = text.split("\n"), [], False
    for line in lines:
        head = _HEAD.match(line)
        if head:
            skipping = head.group(1) == record_id
        if not skipping:
            out.append(line)
    assert len(out) < len(lines), f"premise: the text holds no entry {record_id}"
    return "\n".join(out)


# --------------------------------------------------------------------------------------------------------------------
# The planted project
# --------------------------------------------------------------------------------------------------------------------

A_HISTORY, A_RETIRED, A_OWNER = "DEC-101", "DEC-103", "DEC-105"  # the archive alone holds them
K_FIRST, K_SECOND, K_LATE, K_LATER = "DEC-102", "DEC-104", "DEC-1211", "DEC-1212"  # both files hold them
NEITHER = "DEC-9999"  # no file holds it
ARCHIVE_ONLY = (A_HISTORY, A_RETIRED, A_OWNER)
KEPT_IDS = (K_FIRST, K_SECOND, K_LATE, K_LATER)
ARCHIVE_WORD, ARCHIVE_WORDS = "quornivex", "quornivex ballast"  # words only the archive holds
KEPT_WORD, KEPT_WORDS = "lanternfish", "lanternfish ledger"  # words of a kept entry
TICKET, NOTE = "TKT-ab12", "NOTE-001"
TICKET_REL, NOTE_REL, TEST_REL, LOG_REL = f".tickets/{TICKET}.md", "docs/note.md", "tests/test_rule.py", "docs/log.md"

ENTRY = {
    A_HISTORY: (f"### {A_HISTORY} — The {ARCHIVE_WORD} rule\n"
                "- **Status:** SUPERSEDED (owner, 2026-10-01) · **Class:** history\n"
                f"- **Decision:** the {ARCHIVE_WORDS} is weighed twice before the tide."),
    K_FIRST: (f"### {K_FIRST} — The {KEPT_WORD} rule\n"
              f"- **Status:** ACCEPTED (owner, 2026-10-02) · **Supersedes:** {A_HISTORY} · **Class:** kept\n"
              f"- **Decision:** the {KEPT_WORDS} is kept by hand.\n"
              "- **Note:** two lines, so the entry is more than its status."),
    A_RETIRED: (f"### {A_RETIRED} — The brindlewick rule\n"
                "- **Status:** ACCEPTED (owner, 2026-10-03) · **Class:** retired\n"
                "- **Decision:** the brindlewick gauge is read at noon."),
    K_SECOND: (f"### {K_SECOND} — The marrowgate rule\n"
               f"- **Status:** ACCEPTED (owner, 2026-10-04) · **Supersedes:** {NEITHER} · **Changed by:** {A_RETIRED}"
               " ·\n  **Class:** kept\n"
               "- **Decision:** the marrowgate hinge is oiled weekly."),
    A_OWNER: (f"### {A_OWNER} — The skerrywell exception\n"
              "- **Status:** ACCEPTED (owner, 2026-10-05) · **Class:** history\n"
              "- **Decision:** the skerrywell pump may run dry once."),
    K_LATE: (f"### {K_LATE} — The thistledown plan\n"
             f"- **Status:** ACCEPTED (owner, 2026-11-17) · **Under:** {A_HISTORY}\n"
             "- **Decision:** the thistledown plan is in force."),
    K_LATER: (f"### {K_LATER} — The umberfold order\n"
              "- **Status:** ACCEPTED (owner, 2026-11-18)\n"
              "- **Decision:** the umberfold order follows the plan."),
}
ARCHIVE_ORDER = (A_HISTORY, K_FIRST, A_RETIRED, K_SECOND, A_OWNER, K_LATE, K_LATER)
ARCHIVE_FIRST_LINE = "> **Archived, read-only.** The register as it stood; the decisions in force are in the register."


def archive_text(order=ARCHIVE_ORDER, entry=ENTRY) -> str:
    return (ARCHIVE_FIRST_LINE + "\n\n# Decision register\n\nThe old head.\n\n---\n\n## 1. Decisions\n\n"
            + "\n\n".join(entry[record_id] for record_id in order) + "\n")


def register_text(order=KEPT_IDS, entry=ENTRY) -> str:
    return ("# Decision register (in force)\n\nThe earlier decisions are in the archive, by id.\n\n---\n\n"
            "## Decisions\n\n" + "\n\n".join(entry[record_id] for record_id in order) + "\n")


def _namespace(patterns, embedded: bool, indexed: bool = True) -> dict:
    entry = {"paths": list(patterns), "memory_class": "governance", "sensitivity": "internal",
             "permitted_roles": ["orchestrator", "engineer", "independent-test-designer"],
             "retention": "kept in git history", "export_policy": "allowed",
             "embedding_policy": "embedded" if embedded else "not embedded",
             "provenance": "written by the W2-203 tests", "deletion_rebuild": "authoritative; restored from git only"}
    if not indexed:
        entry["lexical_policy"] = "not indexed"
    return entry


def path_map(archive_key: bool = True, **more) -> str:
    """The planted path map: the register's key, the archive's key (unless ``archive_key`` is false) and the archive
    namespace, out of both indexes as this repository's ``evaluation-sources`` is."""
    import yaml

    document = {"namespaces": {
        "root-files": _namespace(["*"], False),
        "docs": _namespace(["docs/*"], False),
        "archive": _namespace(["docs/archive/**"], False, indexed=False),
        "rest": _namespace([".tickets/**", "governance/**", "tests/**"], False),
    }, "decision_register": REGISTER_REL}
    if archive_key:
        document[ARCHIVE_KEY] = ARCHIVE_REL
    document.update(more)
    return yaml.safe_dump(document, sort_keys=False)


def record(record_id: str, kind: str, status: str, body: str, **keys) -> str:
    import yaml

    front = {"id": record_id, "type": kind, "status": status, **keys}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + body


@dataclass
class Planted:
    root: Path
    commits: dict = field(default_factory=dict)  # name -> full id


def plant(root: Path, *, archive_key: bool = True, archive_file: bool = True, index: bool = True,
          load: bool = True) -> Planted:
    """The planted project, committed (module docstring), its keyword index and record store built in place unless
    told otherwise. Four commits: ``old`` (the path map and the register alone, its message citing a kept id), ``all``
    (the archive, the ticket, the note, the test file), ``archived`` (its message and ``Implements:`` name an id the
    archive alone holds) and ``neither`` (the same for an id no file holds)."""
    root = Path(root)
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    planted = Planted(root)
    write(root, ".gitignore", ".gov-runtime/\n")
    write(root, PATH_MAP_REL, path_map(archive_key))
    write(root, REGISTER_REL, register_text())
    planted.commits["old"] = commit(root, f"The register, with {K_FIRST}")
    if archive_file:
        write(root, ARCHIVE_REL, archive_text())
    both = [A_HISTORY, NEITHER]
    write(root, TICKET_REL, record(TICKET, "task", "open", "# The ticket\n\nIts work.\n", sources=both))
    write(root, NOTE_REL, record(NOTE, "note", "ACTIVE", "# The harbour note\n\nThe harbour keeps its lanterns lit.\n",
                                 decisions=both, constrains=both))
    write(root, TEST_REL, f"# the rule of {A_HISTORY}; the rule of {NEITHER}\n\n\ndef test_rule():\n    assert True\n")
    planted.commits["all"] = commit(root, "The archive and the records")
    write(root, LOG_REL, "# Log\n\nOne line.\n")
    planted.commits["archived"] = commit(root, f"Apply {A_HISTORY}\n\nTask: {TICKET}\nImplements: {A_HISTORY}")
    write(root, LOG_REL, "# Log\n\nOne line.\nTwo lines.\n")
    planted.commits["neither"] = commit(root, f"Apply {NEITHER}\n\nTask: {TICKET}\nImplements: {NEITHER}")
    if index:
        from gov.retrieval import lexical
        lexical.refresh(root)
    if load:
        from gov import store
        store.load(root)
    return planted


# --------------------------------------------------------------------------------------------------------------------
# The store, read as a file
# --------------------------------------------------------------------------------------------------------------------

def tables(root) -> set[str]:
    with sqlite3.connect(f"file:{Path(root) / STORE_REL}?mode=ro", uri=True) as connection:
        return {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def rows(root, sql: str, *values) -> list[tuple]:
    with sqlite3.connect(f"file:{Path(root) / STORE_REL}?mode=ro", uri=True) as connection:
        return sorted(connection.execute(sql, values).fetchall())


def archived_rows(root) -> dict[str, str]:
    """``id -> heading`` of the store's archived-ids table; the case fails here where the load wrote no such table."""
    held = tables(root)
    assert ARCHIVE_TABLE in held, \
        f"the load wrote no table {ARCHIVE_TABLE} (the archive's ids and headings): the store holds {sorted(held)}"
    return dict(rows(root, f"SELECT id, heading FROM {ARCHIVE_TABLE}"))


# --------------------------------------------------------------------------------------------------------------------
# Child processes
# --------------------------------------------------------------------------------------------------------------------

def child_env(src, home) -> dict:
    """The environment of a child: ``src`` first on ``PYTHONPATH``, an empty ``HOME``, the user's own site for the
    libraries, none of the session's ``GOV_*`` settings."""
    env = {key: value for key, value in os.environ.items() if not key.startswith(("GOV_", "PYTEST_"))}
    Path(home).mkdir(parents=True, exist_ok=True)
    env.update(PYTHONPATH=str(src), HOME=str(home), PYTHONDONTWRITEBYTECODE="1",
               PYTHONUSERBASE=os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".local"))
    return env


def child(src, cwd, home, *argv: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *argv], capture_output=True, text=True, cwd=str(cwd),
                          env=child_env(src, home), timeout=timeout, stdin=subprocess.DEVNULL)


def src() -> Path:
    """The ``src`` folder of the ``gov`` under test."""
    import gov as package

    return Path(package.__file__).resolve().parents[1]


def gov(src, cwd, home, *argv: str) -> subprocess.CompletedProcess:
    return child(src, cwd, home, "-m", "gov.cli.main", *argv)


def json_of(done: subprocess.CompletedProcess):
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"no JSON on standard output (exit {done.returncode}): {done.stdout[-600:]!r} "
                             f"{done.stderr[-1200:]!r}") from None


def both(base: Path, head: Path, home: Path, *argv: str, cwd_is_root: bool = False) -> tuple:
    """The same child on the base's clone and on HEAD's, each with its own ``src``, side by side: their JSON outputs.
    ``{root}`` in an argument stands for the clone."""
    out = {}

    def run(name, root):
        args = [arg.replace("{root}", str(root)) for arg in argv]
        out[name] = child(root / "src", root if cwd_is_root else home, home / name, *args)

    threads = [threading.Thread(target=run, args=pair) for pair in (("base", base), ("head", head))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return json_of(out["base"]), json_of(out["head"])
