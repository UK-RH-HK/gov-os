"""The model and effort of every role, in one file (MR-1 to MR-3; DEC-1246 (3)(b), DEC-1242 R-4, DEC-1236 (3)).

``governance/project/role-table.yaml`` holds ``version: 1`` and ``rows: [{role, model, effort, decided}]``. ``gov launch``
reads the row of the role it starts when the file is there (``lead`` for a ticket, fix or chore lead); a project with no
file launches by the role file's ``Launch default`` line as before. A file that cannot be read, repeats a role, holds a
model that is Fable or that the launcher does not know, or an effort it does not know, refuses a launch
(``LAUNCH_REFUSED``, fail closed).

Three checks stand here and run as ``python3 -m gov.launch.role_table`` (``gov launch --table-check``):

* no argument: each role file's ``Launch default`` line equals its row (``check_roles``);
* ``--check <range>``: a commit of the range that changes a row without the trailer ``Decided-by: owner`` is reported
  with the role and its old and new value (``check_range``);
* ``--scripts <dir>``: ``start_lead.sh``, ``start_cto.sh`` and ``start_audit.sh`` each print their ``--model`` and
  ``--effort`` beside the row they must equal (``check_scripts``); a script naming the Fable substitution reader, or
  holding no ``--model`` or no ``--effort``, is reported.

Exit 0 when nothing is reported, 1 when something is, 2 for a usage error.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

from gov.cli.errors import GovError
from gov.launch import role as roles
from gov.util.parts import load_yaml_unique

REL = "governance/project/role-table.yaml"
KIT_REL = "template/governance/project/role-table.yaml"
KEYS = frozenset({"role", "model", "effort", "decided"})
KNOWN_MODEL = re.compile(r"claude-(?:opus|sonnet|haiku)(?:-[a-z0-9]+)+")
ROLE_NAME = re.compile(r"[a-z][a-z0-9-]*")
LEAD_ROW = "lead"
OWNER_TRAILER = "Decided-by: owner"
# the role file of a row, where its name differs from the row's
ROLE_FILES = {"lead": "ticket-lead"}
# the three start scripts and the row each must equal
SCRIPTS = {"start_lead.sh": "lead", "start_cto.sh": "orchestrator", "start_audit.sh": "audit-wide"}
SUBSTITUTION = re.compile(r"substitution", re.IGNORECASE)


def _refuse(reason: str) -> GovError:
    return GovError("LAUNCH_REFUSED", f"{REL}: {reason}")


def exists(root: Path) -> bool:
    """True when the file is there (a link counts), whether or not it is well formed."""
    return os.path.lexists(Path(root) / REL)


def parse(text: str) -> dict[str, dict]:
    """The table's text read and checked whole: ``{role: {"model", "effort", "decided"}}``; ``GovError`` when it is
    not of the stated form."""
    try:
        data = load_yaml_unique(text)
    except (yaml.YAMLError, ValueError):
        raise _refuse("cannot be read, is not YAML, or writes a key twice") from None
    if not isinstance(data, dict) or set(data) != {"version", "rows"}:
        raise _refuse("must be a map with exactly the keys rows, version")
    if data["version"] != 1 or isinstance(data["version"], bool):
        raise _refuse("version must be the integer 1")
    if not isinstance(data["rows"], list):
        raise _refuse("rows must be a list")
    table: dict[str, dict] = {}
    for index, row in enumerate(data["rows"]):
        where = f"row {index}"
        if not isinstance(row, dict) or set(row) != KEYS:
            raise _refuse(f"{where} must be a map with exactly the keys {', '.join(sorted(KEYS))}")
        role, model, effort, decided = (row[key] for key in ("role", "model", "effort", "decided"))
        if not isinstance(role, str) or not ROLE_NAME.fullmatch(role):
            raise _refuse(f"{where}: role is a lower-case name")
        if role in table:
            raise _refuse(f"{where}: the role {role} is repeated")
        if not isinstance(model, str) or "fable" in model.lower():
            raise _refuse(f"{where} ({role}): no role runs Fable (DEC-1225 (3)), or the model is not text")
        if not KNOWN_MODEL.fullmatch(model):
            raise _refuse(f"{where} ({role}): the model {model!r} is not one the launcher knows (claude-opus-..., "
                          f"claude-sonnet-..., claude-haiku-...)")
        if effort not in roles.EFFORTS:
            raise _refuse(f"{where} ({role}): effort is one of {', '.join(roles.EFFORTS)}")
        if not isinstance(decided, str) or not decided.strip():
            raise _refuse(f"{where} ({role}): decided names the decision that set the row")
        table[role] = {"model": model, "effort": effort, "decided": decided}
    return table


def load(root: Path) -> dict[str, dict]:
    """The project's table, read at each call: ``{role: {"model", "effort", "decided"}}``."""
    try:
        text = (Path(root) / REL).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise _refuse("cannot be read, is not YAML, or writes a key twice") from None
    return parse(text)


def row_for(root: Path, role: str) -> dict | None:
    """The row ``gov launch`` takes for ``role`` (a lead's is ``lead``), or ``None`` when the project has no table file
    or the table holds no row for the role (the role file's line then decides). A table that cannot be read refuses."""
    if not exists(root):
        return None
    table = load(root)
    return table.get(LEAD_ROW if role in ("lead", "ticket-lead") else role)


# --- MR-1: the role files equal their rows -------------------------------------------------------------------------


def _role_file_lines(root: Path, name: str) -> tuple[str, list[str]] | None:
    for base in (roles.ROLES_REL, roles.ADOPTED_ROLES_REL):
        path = Path(root) / base / f"{name}.md"
        if path.is_file():
            try:
                return f"{base}/{name}.md", path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                return f"{base}/{name}.md", []
    return None


def check_roles(root: Path) -> list[dict]:
    """Each role file whose ``Launch default`` line differs from its row (or has none of the form), as findings
    ``{"code": "ROLE_FILE_DIFFERS", "role", "file", "table", "found"}``; a table that cannot be read refuses."""
    findings = []
    for role, row in load(root).items():
        found = _role_file_lines(root, ROLE_FILES.get(role, role))
        if found is None:
            continue
        rel, lines = found
        lines = [line for line in lines if line.lstrip().startswith(roles.DEFAULT_HEAD)]
        match = roles.DEFAULT_LINE.fullmatch(lines[0]) if len(lines) == 1 else None
        have = (match.group(1), match.group(2)) if match else None
        want = (row["model"], row["effort"])
        if have != want:
            findings.append({"code": "ROLE_FILE_DIFFERS", "role": role, "file": rel,
                             "table": {"model": want[0], "effort": want[1]},
                             "found": None if have is None else {"model": have[0], "effort": have[1]},
                             "message": f"{rel}: its Launch default line says "
                                        f"{'nothing of the form' if have is None else 'model %s, effort %s' % have}; "
                                        f"the table's row for {role} is model {want[0]}, effort {want[1]}"})
    return findings


# --- MR-1: a row changes only on the owner's trailer -----------------------------------------------------------------


def _git(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *argv], capture_output=True, text=True)


def _table_at(root: Path, revision: str) -> dict[str, dict]:
    shown = _git(root, "show", f"{revision}:{REL}")
    if shown.returncode != 0:
        return {}
    try:
        return parse(shown.stdout)
    except GovError:
        return {}


def _owner_trailer(root: Path, commit: str) -> bool:
    message = _git(root, "show", "-s", "--format=%B", commit).stdout
    parsed = subprocess.run(["git", "-C", str(root), "interpret-trailers", "--parse"], input=message,
                            capture_output=True, text=True).stdout
    return any(line.strip() == OWNER_TRAILER for line in parsed.splitlines())


def check_range(root: Path, rng: str) -> list[dict]:
    """The commits of ``rng`` that change a row of the table without the trailer ``Decided-by: owner``, as findings
    ``{"code": "ROLE_TABLE_CHANGED", "commit", "role", "old", "new", "message"}``, one per changed role. A range that
    does not touch the file reports nothing; one git cannot read refuses."""
    listed = _git(root, "log", "--reverse", "--format=%H", rng, "--", REL)
    if listed.returncode != 0:
        raise GovError("ROLE_TABLE_RANGE", f"git cannot read the range {rng!r}: {listed.stderr.strip()}")
    findings = []
    for commit in listed.stdout.split():
        if _owner_trailer(root, commit):
            continue
        before, after = _table_at(root, f"{commit}^"), _table_at(root, commit)
        for role in sorted(set(before) | set(after)):
            old, new = before.get(role), after.get(role)
            pick = lambda row: None if row is None else {"model": row["model"], "effort": row["effort"]}  # noqa: E731
            if pick(old) == pick(new):
                continue
            show = lambda row: "no row" if row is None else f"model {row['model']}, effort {row['effort']}"  # noqa: E731
            findings.append({"code": "ROLE_TABLE_CHANGED", "commit": commit, "role": role, "old": pick(old),
                             "new": pick(new),
                             "message": f"{commit[:12]}: the row for {role} changed from {show(old)} to {show(new)} "
                                        f"with no trailer '{OWNER_TRAILER}'"})
    return findings


# --- MR-3: the start scripts equal their rows ------------------------------------------------------------------------

_ASSIGN = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=([^\s#]*)", re.MULTILINE)
_DEFAULTING = re.compile(r':\s*"?\$\{([A-Za-z_][A-Za-z0-9_]*):=([^}]*)\}"?')


def _variables(text: str) -> dict[str, str]:
    values = {m.group(1): m.group(2).strip("\"'") for m in _ASSIGN.finditer(text)}
    values.update({m.group(1): m.group(2) for m in _DEFAULTING.finditer(text)})
    return values


def _resolve(value: str, variables: dict[str, str]) -> str | None:
    """A word of a script as its value: a plain word as written; ``$x``, ``${x}`` and ``${x:-d}`` by the variable's
    assignment in the script, or ``d``; ``None`` when it cannot be told."""
    value = value.strip("\"'")
    match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?-([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)", value)
    if match is None:
        return value if value and "$" not in value else None
    name = match.group(1) or match.group(3)
    if name in variables:
        return _resolve(variables[name], {k: v for k, v in variables.items() if k != name})
    return match.group(2) if match.group(2) else None


def _option(text: str, flag: str, variables: dict[str, str]) -> tuple[bool, str | None]:
    """``(named, value)``: whether ``flag`` stands in the script's text, and its value (``None`` when told by nothing)."""
    found = re.search(rf"(?<![\w-]){re.escape(flag)}(?:\s+|=)(\"[^\"]*\"|'[^']*'|[^\s\\\"']+)", text)
    if found is None:
        return False, None
    return True, _resolve(found.group(1), variables)


def check_scripts(root: Path, directory: Path | str) -> tuple[list[str], bool]:
    """``(lines, ok)``: one line for each of the three start scripts in ``directory`` with its ``--model`` and
    ``--effort`` beside the row it must equal, then a line for each fault (a disagreement, a script with no ``--model``
    or no ``--effort``, one that is missing, one that names the Fable substitution reader). ``ok`` is True when no fault
    stands. A table that cannot be read refuses."""
    table = load(root)
    lines: list[str] = []
    faults: list[str] = []
    for name, role in SCRIPTS.items():
        row = table.get(role)
        want = "no row" if row is None else f"model {row['model']}, effort {row['effort']}"
        path = Path(directory) / name
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            lines.append(f"{name}: not readable; the table's row for {role}: {want}")
            faults.append(f"{name}: cannot be read, so it cannot be checked against the row for {role}")
            continue
        variables = _variables(text)
        (has_model, model), (has_effort, effort) = (_option(text, flag, variables) for flag in ("--model", "--effort"))
        lines.append(f"{name}: --model {model or 'none'} --effort {effort or 'none'}; the table's row for {role}: "
                     f"{want}")
        if row is None:
            faults.append(f"{name}: the table has no row for {role}")
            continue
        for flag, has, value, key in (("--model", has_model, model, "model"), ("--effort", has_effort, effort, "effort")):
            if not has:
                faults.append(f"{name}: names no {flag}; the table's {role} row says {row[key]}")
            elif value != row[key]:
                faults.append(f"{name}: {flag} is {value if value is not None else 'not readable'}; the table's {role} "
                              f"row says {row[key]}")
        if SUBSTITUTION.search(text):
            faults.append(f"{name}: names the substitution reader; no start script holds one (no session runs Fable)")
    return lines + faults, not faults


# --- the command -----------------------------------------------------------------------------------------------------


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--check", metavar="<range>", help="report the commits of a git range that change a row "
                        "without the trailer 'Decided-by: owner'")
    parser.add_argument("--scripts", metavar="<dir>", help="compare start_lead.sh, start_cto.sh and start_audit.sh "
                        "in <dir> with the table")
    parser.add_argument("--root", metavar="<dir>", default=None, help="the project (default: the working folder)")


def run(args, root: Path | None = None) -> int:
    root = Path(args.root or root or os.getcwd())
    try:
        if args.scripts:
            lines, ok = check_scripts(root, args.scripts)
            for line in lines:
                print(line)
            return 0 if ok else 1
        if args.check:
            findings = check_range(root, args.check)
        else:
            load(root)
            findings = check_roles(root)
    except GovError as error:
        print(f"{error.code}: {error.message}", file=sys.stderr)
        return 1
    for finding in findings:
        print(f"{finding['code']}: {finding['message']}")
    return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.launch.role_table", description=__doc__.splitlines()[0])
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
