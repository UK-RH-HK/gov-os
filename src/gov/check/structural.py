"""``gov check --structural``: one cheap, bounded pass over the declared check families and the new links (W2-158).

A notice, never a refusal (DEC-1052, DEC-1073): the pass exits 0 whatever any check finds or however it ends (S3, F1),
and 2 only when it could not run at all (L8). No commit, close, landing or launch code calls it to decide anything.

What it does (the ticket's S1-S5 and F1-F4; the lead's readings L1-L10 of its Interface line):

- **Families (S1, L3).** schema, graph, claims, mutation, authority, pathmap, audit and skills, then portability,
  then links. Each family's command is the tree's own declaration, ``template/governance/kernel/checks/<id>.yaml``,
  else ``governance/kernel/checks/<id>.yaml``; skills is every declaration whose ``family`` is ``skill regression``.
  There is no built-in command (F3): a family with no declaration reads ``skipped (no declaration)`` and nothing is
  run for it; a file that cannot be read, or has no string ``command``, makes only its own family a NOTICE.
- **How a command runs (S1, L4).** ``shlex.split``, a first word ``python3`` is this interpreter, in the tree, with
  the caller's environment less every ``GIT_*`` variable, ``PYTHONPATH=<tree>/src`` and
  ``PYTHONDONTWRITEBYTECODE=1``, stdin from /dev/null, in a session and process group of its own. All are started
  at once (one thread and one process each); at the bound the whole group is killed, so a grandchild dies with it.
- **How a result reads (S2, L5).** Exit 0 ``ok``; exit 2 with ``{"not_applicable": true}`` ``ok (not applicable:
  <reason>)``; killed at the bound ``NOTICE not measured: ...`` (never ok, never a non-zero exit); any other exit a
  NOTICE with the ``message`` of each finding, else ``<id> exit <code>: <first line>``; a command that cannot be
  started ``<id> could not run: <why>``. Findings are joined with `` | ``, three shown, then ``(+k more)``.
- **Portability and links (S4, L6, L7).** Both need a ``<base>``. Portability runs when ``<base>..HEAD`` touches the
  kernel's roles, skills or hooks or ``.rulesync/``, or when ``<base>`` does not resolve. Links runs the tree's own
  ``gov links --since <base>`` after the others, if the tree has ``src/gov/links/``.
- **Nothing else (S5, L9).** The pass writes no file; its git reads take no optional lock; the children write no
  bytecode. The only writes are those of the declared commands and of links' own mark.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import NamedTuple

CHECKS_DIRS = ("template/governance/kernel/checks", "governance/kernel/checks")  # gov.cli.checks.CHECKS_DIRS
FAMILIES = (("schema", "core-schema"), ("graph", "core-graph"), ("claims", "core-claims"),
            ("mutation", "core-mutation"), ("authority", "core-authority"), ("pathmap", "core-pathmap"),
            ("audit", "audit-reproducibility"))
SKILLS = "skills"
SKILL_FAMILY = "skill regression"  # the declarations' own `family` field
PORTABILITY_ID = "adapter-portability"
PORTABILITY_PATHS = tuple(f"template/governance/kernel/{d}/" for d in ("roles", "skills", "hooks")) + (".rulesync/",)
LINKS_DIR = "src/gov/links"
DEFAULT_TIMEOUT = 50.0
SHOWN = 3  # findings shown on a line
WIDTH = 160  # characters of each one


class CannotRun(Exception):
    """The pass cannot run at all (exit 2)."""


def _env(tree: Path) -> dict:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["PYTHONPATH"] = str(tree / "src")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _git(tree: Path, *args: str) -> subprocess.CompletedProcess:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    return subprocess.run(["git", "--no-optional-locks", "-C", str(tree), *args], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, env=env, timeout=60)


def _short(text) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= WIDTH else text[:WIDTH - 3] + "..."


def _shown(items: list[str]) -> str:
    more = f" (+{len(items) - SHOWN} more)" if len(items) > SHOWN else ""
    return " | ".join(_short(item) for item in items[:SHOWN]) + more


# ---- the declarations --------------------------------------------------------------------------------------

class Decl(NamedTuple):
    rel: str  # the file, relative to the tree
    ident: str  # its id (its file name's stem when it states none or cannot be read)
    command: str | None
    problem: str | None  # why it cannot be run: unreadable, or no string `command`
    family: str | None  # its `family` field, None when unreadable or absent


def _declarations(tree: Path) -> dict[str, Decl]:
    """{key: declaration} over both layouts, template layout first. A file is keyed by its name's stem and by its
    ``id``; the first file for a key is the declaration (the template's, else the installed layout's)."""
    import yaml
    found: dict[str, Decl] = {}
    for directory in CHECKS_DIRS:
        folder = tree / directory
        for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else ():
            rel = f"{directory}/{path.name}"
            try:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as error:  # a file that cannot be read is its own family's notice, nothing else's
                found.setdefault(path.stem, Decl(rel, path.stem, None, f"{rel} cannot be read: {_short(error)}", None))
                continue
            document = document if isinstance(document, dict) else {}
            command, ident = document.get("command"), document.get("id")
            ident = ident if isinstance(ident, str) and ident else path.stem
            problem = None if isinstance(command, str) and command.strip() else f"{rel} has no string 'command'"
            decl = Decl(rel, ident, None if problem else command, problem, document.get("family"))
            for key in {path.stem, ident}:
                found.setdefault(key, decl)
    return found


def _skills(found: dict[str, Decl]) -> list[Decl]:
    """The skills family: every declaration whose family is ``skill regression`` (an unreadable file counts when its
    name starts ``skill-regression``), one per id, in id order."""
    chosen: dict[str, Decl] = {}
    for decl in found.values():
        if decl.family == SKILL_FAMILY or (decl.family is None and decl.ident.startswith("skill-regression")):
            chosen.setdefault(decl.ident, decl)
    return [chosen[ident] for ident in sorted(chosen)]


def _plan(tree: Path, with_portability: bool) -> list[tuple[str, list[tuple[str, Decl | None]]]]:
    """[(family, [(id, declaration, or None for none)])] in print order."""
    found = _declarations(tree)
    plan = [(family, [(ident, found.get(ident))]) for family, ident in FAMILIES]
    plan.append((SKILLS, [(decl.ident, decl) for decl in _skills(found)] or [("", None)]))
    plan.append(("portability", [(PORTABILITY_ID, found.get(PORTABILITY_ID) if with_portability else None)]))
    return plan


# ---- running a command -------------------------------------------------------------------------------------

def _run(tree: Path, command: str, bound: float):
    """(exit code, stdout, stderr) of one command; exit None past the bound; exit "x" with the reason in stdout when
    it cannot be started."""
    try:
        argv = shlex.split(command)
        if not argv:
            raise ValueError("an empty command")
        if argv[0] == "python3":
            argv[0] = sys.executable
        proc = subprocess.Popen(argv, cwd=str(tree), env=_env(tree), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, errors="replace", start_new_session=True)
    except (OSError, ValueError) as error:
        return "x", str(getattr(error, "strerror", None) or error), ""
    try:
        out, err = proc.communicate(timeout=bound)
        return proc.returncode, out, err
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)  # the command and whatever it started
        except ProcessLookupError:
            pass
        proc.wait()
        for stream in (proc.stdout, proc.stderr):
            if stream:
                stream.close()
        return None, "", ""


def _judge(ident: str, result, bound: float):
    """(ok, text): ok with a reason when not applicable, or a notice's text."""
    code, out, err = result
    if code is None:
        return False, f"not measured: {ident} did not end within {bound:g} s"
    if code == "x":
        return False, f"{ident} could not run: {_short(out)}"
    try:
        parsed = json.loads(out) if out.strip() else None
    except ValueError:
        parsed = None
    if code == 0:
        return True, ""
    if code == 2 and isinstance(parsed, dict) and parsed.get("not_applicable") is True:
        return True, f"not applicable: {parsed.get('reason', '')}"
    findings = parsed if isinstance(parsed, list) else parsed.get("findings") if isinstance(parsed, dict) else None
    if isinstance(findings, list) and findings:
        return False, [item.get("message") or json.dumps(item) if isinstance(item, dict) else str(item)
                       for item in findings]
    first = next((line for line in (out.strip() or err.strip() or "no output").splitlines() if line.strip()), "")
    return False, f"{ident} exit {code}: {first}"


def _family_line(family: str, verdicts: list) -> tuple[bool, str]:
    notices, notes = [], []
    for ok, text in verdicts:
        if not ok:
            notices.extend(text if isinstance(text, list) else [text])
        elif text:
            notes.append(text)
    if notices:
        return False, f"{family}: NOTICE {_shown(notices)}"
    return True, f"{family}: ok" + (f" ({_short('; '.join(notes))})" if notes else "")


# ---- portability and links ---------------------------------------------------------------------------------

def _portability_runs(tree: Path, base: str | None) -> tuple[bool, str]:
    """(runs?, why not): for the change ``base..HEAD``."""
    if base is None:
        return False, "no base given"
    resolved = _git(tree, "rev-parse", "--verify", "-q", "--end-of-options", f"{base}^{{commit}}")
    if resolved.returncode or not resolved.stdout.strip():
        return True, ""
    diff = _git(tree, "diff", "--name-only", f"{resolved.stdout.strip()}..HEAD")
    if diff.returncode or any(path.startswith(PORTABILITY_PATHS) for path in diff.stdout.splitlines()):
        return True, ""
    return False, "no such change"


def _links_line(tree: Path, base: str | None, bound: float) -> tuple[bool, str]:
    if base is None:
        return True, "links: skipped (no base given)"
    if not (tree / LINKS_DIR).is_dir():
        return True, "links: skipped (no gov links in this tree)"
    code, out, err = _run(tree, f"python3 -m gov.cli.main links --since {shlex.quote(base)}", bound)
    if code is None:
        return False, f"links: NOTICE not measured: gov links did not end within {bound:g} s"
    lines = [line for line in out.splitlines() if line.strip()]
    first = re.match(r"gov links: (\d+) new since (\S+), (\d+) standing", lines[0]) if lines else None
    if code not in (0, 1) or first is None:
        last = next((line for line in reversed((err.strip() or out.strip() or "no output").splitlines())
                     if line.strip()), "no output")
        return False, f"links: NOTICE gov links could not run (exit {code}): {_short(last)}"
    new, standing = int(first.group(1)), int(first.group(3))
    if new == 0:
        return True, f"links: ok (0 new since {base}, {standing} standing)"
    return False, f"links: NOTICE {new} new: {_shown(lines[1:])}"


# ---- the pass ----------------------------------------------------------------------------------------------

def run_structural(tree: Path, base: str | None, timeout: float, out) -> int:
    """Run the pass on ``tree``, its lines to ``out``; 0 whenever it ran, 2 when it could not (named on stderr)."""
    started = time.monotonic()
    try:
        head = _prepare(Path(tree))
    except CannotRun as error:
        print(f"gov check: structural pass could not run: {error}", file=sys.stderr)
        return 2
    tree = Path(tree).resolve()
    with_portability, why = _portability_runs(tree, base)
    plan = _plan(tree, with_portability)
    jobs = []  # (family, id, command) of every command to run
    verdicts: dict = {family: [] for family, _ in plan}
    for family, checks in plan:
        for ident, entry in checks:
            if entry is not None and entry.problem is not None:
                verdicts[family].append((False, entry.problem))
            elif entry is not None:
                jobs.append((family, ident, entry.command))
    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:  # one process each, all at once
        results = [pool.submit(_run, tree, command, timeout) for _, _, command in jobs]
        for (family, ident, _), future in zip(jobs, results):
            verdicts[family].append(_judge(ident, future.result(), timeout))
    ran, notices = 0, []
    for family, checks in plan:
        if family == "portability" and not with_portability:
            line = f"portability: skipped ({why})"
        elif all(entry is None for _, entry in checks):
            line = f"{family}: skipped (no declaration)"
        else:
            ok, line = _family_line(family, verdicts[family])
            ran += 1
            if not ok:
                notices.append(family)
        print(line, file=out, flush=True)
    links_ok, links = _links_line(tree, base, timeout)
    print(links, file=out, flush=True)
    if not links.startswith("links: skipped"):
        ran += 1
        if not links_ok:
            notices.append("links")
    took = f"{time.monotonic() - started:.1f} s"
    at = f"structural pass at {head[:12]}"
    if notices:
        print(f"{at}: NOTICE in {', '.join(notices)} ({ran - len(notices)} of {ran} ran families ok), {took}; "
              "a notice, not a refusal", file=out, flush=True)
    else:
        print(f"{at}: all {ran} ran families ok, {took}", file=out, flush=True)
    return 0


def _prepare(tree: Path) -> str:
    """HEAD's sha of the git work tree whose top is ``tree``; ``CannotRun`` otherwise."""
    if not tree.is_dir():
        raise CannotRun(f"no folder {tree}")
    try:
        top = _git(tree, "rev-parse", "--show-toplevel")
        if top.returncode or Path(top.stdout.strip()).resolve() != tree.resolve():
            raise CannotRun(f"{tree} is not the top of a git work tree")
        head = _git(tree, "rev-parse", "--verify", "-q", "HEAD^{commit}").stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as error:
        raise CannotRun(f"git cannot be run in {tree}: {error}") from error
    if not head:
        raise CannotRun(f"{tree} has no HEAD commit")
    return head
