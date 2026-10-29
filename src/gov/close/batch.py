"""Batched closes (W2-68; DEC-883 items 1 to 3, DEC-889 items 2 and 4, DEC-890): ``python3 -m gov.close.batch``.

- ``run <ticket> [<ticket> ...] --root <project>``: the batch (the design note, section 3, with point E). It refuses
  (exit 1, nothing run) unless the working tree is ``HEAD`` and every ticket named is an open ticket of the project;
  ``HEAD`` is then the batch's head H. One full rebuild at H, one ``gov check`` at H (its result under
  ``.gov-runtime/close/batch/<stamp>/check.json``; a blocking one ends the batch, exit 3), one full regression at H
  through the nightly's own run (``gov.close.nightly.night``): every red run again alone, a red that passes alone a
  flaky candidate never bisected, one that fails alone attributed by the bisect's first bad commit, else by the
  ticket whose acceptance folder holds the test, else ``outside``. ``BATCH_CODE_CHANGED`` (exit 1) when ``HEAD``'s
  code fingerprint is no longer H's at the end. The record is the nightly's, with ``kind: batch`` and the batch's
  keys; it is committed in a commit that names no task. Nothing closes on a red run (exit 3). On a green run each
  ticket is closed in the order given, in-process (``gov close`` with the batch's check result), the store made
  fresh at ``HEAD`` before each (the incremental record load, else a full rebuild where ``HEAD``'s fingerprints
  cannot be computed) and its outputs committed; a refused close ends the batch (exit 3).
- ``refresh --root <project>``: the incremental record load at ``HEAD`` (``gov.store.load_records``). It exits 0
  when the store is fresh at ``HEAD`` after the load (``gov.close.repo.store_is_of_head``), and 1 with the error's
  code otherwise: ``STORE_CODE_CHANGED`` where the store was built on other code (a full rebuild is needed),
  ``STORE_STALE`` where the load left it stale.

Reuse (section 4): ``reuse`` gives a close the last fully passing run on its code, or None, and ``reused_check``
the governance check that run's record names, where it may stand in for the close's own.

The commits the batch makes carry ``Role:`` (the caller's ``GOV_ROLE``, else ``orchestrator``), ``Implements:
DEC-883`` and a ``Co-Authored-By:`` only where the caller's environment gives one (``GOV_CO_AUTHORED_BY``).

The design is ``docs/research/W2-68-batched-close.md``. Each answer is the API-0002 envelope, as
``gov.close.nightly`` gives it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import evidence as _evidence, fingerprint as _fingerprint, select as _select
from gov.close.repo import (git as _git, read_commits as _read_commits, store_is_of_head as _store_is_of_head,
                            tickets_of_head as _tickets_of_head, tree_differences as _tree_differences)

COMMAND = "batch"
EXIT_RED = 3
BATCH_DIR = ".gov-runtime/close/batch"
CHECK_FILE = "check.json"
KIND = "batch"
IMPLEMENTS = "DEC-883"
DEFAULT_ROLE = "orchestrator"
CO_AUTHOR_VARIABLE = "GOV_CO_AUTHORED_BY"
OUTSIDE = "outside"
# What the commits of the batch keep of the caller's git environment: who commits, and when. Nothing else of it
# reaches git (DEC-500), as ``gov.close.repo.git`` gives none.
_IDENTITY = ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_AUTHOR_DATE",
             "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL", "GIT_COMMITTER_DATE")


# ---------------------------------------------------------------------------
# Reuse: the last fully passing run (section 4)
# ---------------------------------------------------------------------------

def _count(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _candidates(root: Path) -> list[dict]:
    """W2-66's green records, as ``select._green_heads`` reads them: the nightly folder's green full runs (nights
    and batches, newest name first), then the close records whose evidence is ``full``."""
    from gov.close.ratchet import ACCEPTED_REDS, LOAD_SENSITIVE
    from gov.tasks.tickets import frontmatter

    found = []
    for path in sorted((root / _select.NIGHTLY_REL).glob("*.json"), reverse=True):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(run, dict) or run.get("verdict") != "green" or run.get("scope") != "full":
            continue
        tests_run = run.get("tests_run") if isinstance(run.get("tests_run"), dict) else {}
        found.append({"record": path.relative_to(root).as_posix(), "head": run.get("head"),
                      "failed": bool(run.get("failures")) or bool(run.get("findings")),
                      "junit_xml": run.get("junit_xml"), "tests_run": tests_run,
                      "skip_count": run.get("skip_count") if run.get("kind") == KIND else tests_run.get("skipped"),
                      "states_fingerprint": "code_fingerprint" in run, "code_fingerprint": run.get("code_fingerprint"),
                      "check_result": run.get("check_result")})
    for path in sorted((root / "docs" / "close").glob("*/CL-*.md")):
        front = frontmatter(path) or {}
        evidence = front.get(_evidence.KEY)
        if not isinstance(evidence, dict) or evidence.get("scope") != "full":
            continue
        found.append({"record": path.relative_to(root).as_posix(), "head": evidence.get("head"),
                      # a close that needed a load-sensitive re-run or an accepted red did not pass outright
                      "failed": bool(evidence.get("failures")) or bool(front.get(ACCEPTED_REDS))
                      or bool(front.get(LOAD_SENSITIVE)),
                      "junit_xml": evidence.get("junit_xml"), "tests_run": front.get("tests_run") or {},
                      "skip_count": evidence.get("skip_count"),
                      "states_fingerprint": "code_fingerprint" in evidence,
                      "code_fingerprint": evidence.get("code_fingerprint"), "check_result": None})
    return found


def _junit(root: Path, named) -> dict | None:
    """What the run's JUnit XML files state (``cases``, ``skips``); None unless it names at least one file and every
    file it names exists, parses, holds a case and holds no failure or error (condition 4)."""
    if not isinstance(named, list) or not named or not all(isinstance(rel, str) and rel for rel in named):
        return None
    cases, skips = 0, []
    for rel in named:
        path = root / rel
        if not path.is_file():
            return None
        read = _evidence.read_junit(root, path)
        if not read["cases"] or read["failures"]:  # a placeholder of a run cut short holds no case
            return None
        cases += len(read["cases"])
        skips += read["skips"]
    return {"cases": cases, "skips": skips}


def reuse(root: Path, plan: dict, full_asked: bool = False) -> dict | None:
    """The run a close on ``HEAD`` reuses: of W2-66's green records, the newest by ancestry that meets every
    condition of section 4; None, so the close runs fresh, where none does. ``plan`` is W2-66's selection of the
    close (``select.plan``).

    The answer is the evidence's ``reused`` block (``record``, ``head``, ``code_fingerprint``, ``junit_xml``,
    ``skip_count`` and ``skips`` as its JUnit XML states them, ``tests_run``) and, under ``check_result``, the check
    result the record names (None where it names none)."""
    root = Path(root)
    if full_asked or any(str(why.get("reason", "")).startswith("TEST_MAP_") or why.get("reason") ==
                         "UNRESOLVED_TARGET" for why in plan.get("why_full") or []):
        return None  # condition 7
    now = _fingerprint.of_commit(root, "HEAD")
    if now is None:
        return None  # condition 6: nothing is reused where HEAD's code fingerprint cannot be computed
    passing = []
    for candidate in _candidates(root):
        head = _select.full_id(root, candidate["head"]) if isinstance(candidate["head"], str) else None
        if not head or not _select.is_ancestor(root, head):  # condition 1
            continue
        if candidate["failed"]:  # conditions 2 (read above) and 3
            continue
        read = _junit(root, candidate["junit_xml"])  # condition 4
        stated = _count(candidate["skip_count"])
        if read is None or stated is None or stated != len(read["skips"]):  # condition 5
            continue
        then = _fingerprint.of_commit(root, head)
        if then is None or then["code"] != now["code"] or (candidate["states_fingerprint"] and
                                                           candidate["code_fingerprint"] != now["code"]):
            continue  # condition 6: computed now, and as the record states it
        passing.append({"record": candidate["record"], "head": head, "code_fingerprint": now["code"],
                        "junit_xml": list(candidate["junit_xml"]), "skip_count": stated, "skips": read["skips"],
                        "tests_run": candidate["tests_run"], "check_result": candidate["check_result"]})
    newest = _select.newest(root, list(dict.fromkeys(p["head"] for p in passing)))
    return next((p for p in passing if p["head"] == newest), None)


def _check_of(path: Path) -> tuple[dict, bool] | None:
    """``(result, blocks)`` of a ``gov check --json`` envelope; None where it cannot be read as one."""
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        result = envelope["result"] if envelope["ok"] is True else envelope["error"]["details"]
        checks = result["checks"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return (result, envelope["ok"] is not True) if isinstance(checks, list) else None


def reused_check(root: Path, reused: dict | None) -> dict | None:
    """What a reusing close states in place of its own ``gov check`` (``governance_checks_reused``): the record, its
    commit, its code fingerprint and the check result's file; None, so the close runs its own, unless the reused
    record names a check result, the file exists, every check in it ran at the record's head and it does not
    block."""
    named = (reused or {}).get("check_result")
    if not isinstance(named, dict) or not isinstance(named.get("path"), str) or not named["path"]:
        return None
    read = _check_of(Path(root) / named["path"])
    if read is None:
        return None
    result, blocks = read
    try:
        ran_at = {check["provenance"]["commit"] for check in result["checks"]}
    except (KeyError, TypeError):
        return None
    if blocks or named.get("blocks") is not False or ran_at != {reused["head"]}:
        return None
    return {"record": reused["record"], "commit": reused["head"], "code_fingerprint": reused["code_fingerprint"],
            "check_result": named["path"]}


def reused_form(root: Path, own: str, plan: dict) -> dict:
    """The reusing close's regression run: the record-reading set alone, in the full run's form (``pytest tests``
    with ``--ignore`` and ``--deselect``). Every acceptance suite and every other folder under ``tests/`` that is no
    record-reading target is left out, ``tests/unit`` included."""
    test_map, _ = _select.load_map(root)
    targets = list((test_map or {}).get("record_reading") or [])
    tests = Path(root) / _select.FULL_TARGET
    folders = [f"{_select.FULL_TARGET}/{d.name}/" for d in sorted(tests.iterdir()) if d.is_dir()
               and not d.name.startswith((".", "__")) and d.name != Path(_select.ACCEPTANCE).name] \
        if tests.is_dir() else []
    ignore, deselect, left_out = _select._form(root, own, _select._suites(root) + folders, targets)
    return {**plan, "scope": "reused", "why_full": [],
            "selected": [{"target": t, "why": [{"reason": "RECORD_READING"}]} for t in targets],
            "ignore": ignore, "deselect": deselect, "left_out": left_out}


# ---------------------------------------------------------------------------
# The batch's run (section 3, steps 1 to 7)
# ---------------------------------------------------------------------------

def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _refuse_unless_ready(root: Path, tickets: list[str]) -> None:
    """Step 1: the working tree is ``HEAD``, and every ticket named is an open ticket of the project."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    differing = sorted({path for _, path in _tree_differences(root)})
    if differing:
        raise GovError("TREE_NOT_COMMITTED", "the working tree is not HEAD, so the batch would measure another tree "
                       f"than it records: {', '.join(differing)}", {"paths": differing})
    if not tickets:
        raise GovError("TICKET_UNKNOWN", "the batch names no ticket", {"tickets": []})
    for ticket in tickets:
        front = frontmatter(Path(root) / TICKETS_REL / f"{ticket}.md")
        if front is None:
            raise GovError("TICKET_UNKNOWN", f"{ticket} is not a ticket of this project", {"ticket": ticket})
        if str(front.get("status", "")) == "closed":
            raise GovError("TICKET_CLOSED", f"ticket {ticket} is already closed", {"ticket": ticket})


def _rebuild(root: Path) -> dict:
    """A full ``gov rebuild`` at ``HEAD``, by its own code, never ``--no-embeddings``."""
    from gov.config.loader import load_config
    from gov.rebuild.command import run as rebuild

    done = rebuild(root, argparse.Namespace(no_embeddings=False), load_config(root))
    return {"kind": "rebuild", "head": _git(root, "rev-parse", "HEAD").strip(), "digest": done["digest"]}


def _check(root: Path, head: str, stamp: str) -> dict:
    """Step 3: one ``gov check`` at H, its ``gov check --json`` envelope written under the batch's folder; what the
    record states of it (``path``, ``commit``, ``blocks``). ``CHECKS_NOT_MEASURED`` where its checks did not run
    at H."""
    from gov.close.command import _check_governance

    stated, blocking = _check_governance(root, [], every=True)
    result = stated["governance_checks"]
    if blocking is None:
        envelope = {"ok": True, "command": "check", "result": result, "session": ""}
    else:
        envelope = {"ok": False, "command": "check", "result": {}, "session": "",
                    "error": {"code": "CHECK_FAILED", "message": "one or more hard-block checks failed",
                              "details": result}}
    rel = f"{BATCH_DIR}/{stamp}-{head[:12]}/{CHECK_FILE}"
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(json.dumps(envelope, indent=1) + "\n", encoding="utf-8")
    return {"path": rel, "commit": stated["check_commit"], "blocks": blocking is not None}


def _attribute(root: Path, night: dict) -> list[dict]:
    """Step 5: each red that failed alone, attributed with its evidence: by the bisect's first bad commit to the
    ticket its ``Task:`` names, else to the ticket whose acceptance folder holds the test, else ``outside``. A
    flaky candidate is named by the night and never bisected; it is not attributed."""
    tickets = _tickets_of_head(root)
    suites = [(tid, folder) for tid, _, _, folder, held in _select._tickets(root) if held]
    found = []
    for failure in night["failures"]:
        if failure.get("class") != "red":
            continue
        test = failure["test"]
        bisect = next((p for p in night["packages"] if p.get("kind") == "bisect" and p.get("test") == test), {})
        entry = {"test": test, "text": failure.get("text", ""), "alone": failure.get("alone"),
                 "range": bisect.get("range"), "first_bad": bisect.get("first_bad")}
        first_bad = bisect.get("first_bad")
        named = []
        if first_bad:
            commits = _read_commits(root, "-1", first_bad)
            named = [t for t in (commits[0]["trailers"].get("Task", []) if commits else []) if t in tickets]
        holder = next((tid for tid, folder in suites if test.startswith(folder)), None)
        if named:
            entry.update({"ticket": named[0], "by": "bisect"})
        elif holder:
            entry.update({"ticket": holder, "by": "folder",
                          "folder": next(folder for tid, folder in suites if tid == holder)})
        else:
            entry.update({"ticket": OUTSIDE, "by": OUTSIDE})
        found.append(entry)
    return found


def _measure(root: Path, tickets: list[str]) -> dict:
    """Steps 1 to 7: the batch's run at H and its record, written to the working tree; nothing committed."""
    from gov.close import nightly

    root = Path(root)
    _refuse_unless_ready(root, tickets)
    head = _git(root, "rev-parse", "HEAD").strip()
    prints = _fingerprint.of_commit(root, head)  # None: the batch runs, and each close runs fresh
    stamp = _stamp()
    loads = [{"before": "run", **_rebuild(root)}]
    check = _check(root, head, stamp)
    if check["blocks"]:
        raise GovError("BATCH_CHECK_BLOCKED", f"the governance checks block at {head[:12]}: no regression runs and "
                       "nothing closes", {"head": head, "check_result": check, "loads": loads}, exit_code=EXIT_RED)
    night = nightly.night(root, head)
    rel = night.pop("record")
    skips = [s for named in night["junit_xml"] for s in _evidence.read_junit(root, root / named)["skips"]]
    record = {**night, "kind": KIND, "tickets": list(tickets),
              "code_fingerprint": prints["code"] if prints else None,
              "records_fingerprint": prints["records"] if prints else None,
              "skip_count": len(skips), "skips": skips, "check_result": check,
              "attribution": _attribute(root, night)}
    (root / rel).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    now = _fingerprint.of_commit(root, "HEAD")
    if _git(root, "rev-parse", "HEAD").strip() != head and (prints is None or now is None
                                                             or now["code"] != prints["code"]):
        raise GovError("BATCH_CODE_CHANGED", f"HEAD's code is no longer the batch's ({head[:12]}): its run serves "
                       "no close at other code", {"head": head, "record": rel, "loads": loads,
                                                  "code_fingerprint": record["code_fingerprint"],
                                                  "head_now_code_fingerprint": now and now["code"]})
    return {"record": rel, "loads": loads, **record}


# ---------------------------------------------------------------------------
# What the batch commits and closes (section 3, steps 8 to 10)
# ---------------------------------------------------------------------------

def _commit(root: Path, subject: str, paths: list[str], task: str | None = None) -> str:
    """A commit of ``paths`` alone, with the batch's trailers; its id."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_") or key in _IDENTITY}
    trailers = ([f"Task: {task}"] if task else []) + [f"Role: {os.environ.get('GOV_ROLE') or DEFAULT_ROLE}",
                                                      f"Implements: {IMPLEMENTS}"]
    if os.environ.get(CO_AUTHOR_VARIABLE):
        trailers.append(f"Co-Authored-By: {os.environ[CO_AUTHOR_VARIABLE]}")
    git = ["git", "-C", str(root), "--no-replace-objects"]
    for cmd in (git + ["add", "--all", "--", *paths],
                git + ["commit", "-q", "-m", subject, *[a for t in trailers for a in ("--trailer", t)], "--", *paths]):
        done = subprocess.run(cmd, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
        if done.returncode != 0:
            raise GovError("BATCH_COMMIT_FAILED", f"git {cmd[4]} failed: {done.stderr.strip()[:200]}",
                           {"paths": paths})
    return _git(root, "rev-parse", "HEAD").strip()


def _fresh(root: Path) -> dict:
    """The store made fresh at ``HEAD`` before a close: the incremental record load where ``HEAD``'s fingerprints can
    be computed, else a full rebuild."""
    from gov.store import load_records

    if _fingerprint.of_commit(root, "HEAD") is None:
        return _rebuild(root)
    loaded = load_records(root)
    return {"kind": "records", "head": loaded["head"], "digest": loaded["digest"]}


def _close(root: Path, ticket: str, check: str) -> dict:
    """``gov close <ticket>`` in-process, by the close's own code, with the batch's check result."""
    from gov.close.command import run as close
    from gov.config.loader import load_config

    args = argparse.Namespace(ticket=ticket, disposition=None, owner_decision=None, timeout=None, ticket_session=[],
                              full=False, check_result=str(Path(root) / check))
    return close(root, args, load_config(root))


def run(root: Path, tickets: list[str]) -> tuple[dict, int]:
    """The batch: ``(result, exit code)``; a ``GovError`` where it ends before any close (step 1, the check, step 6,
    a red run)."""
    from gov.tasks.tickets import TICKETS_REL

    root = Path(root)
    measured = _measure(root, tickets)
    rel, loads = measured["record"], measured["loads"]
    green = measured["verdict"] == "green"
    commit = _commit(root, f"batch: the run record of {measured['head'][:12]} ({measured['verdict']})", [rel])
    result = {"record": rel, "record_commit": commit, "head": measured["head"], "verdict": measured["verdict"],
              "code_fingerprint": measured["code_fingerprint"], "check_result": measured["check_result"],
              "attribution": measured["attribution"], "closes": [], "loads": loads}
    if not green:
        raise GovError("BATCH_RED", f"the batch's run at {measured['head'][:12]} is red: "
                       f"{len(measured['failures'])} failing tests, {len(measured['findings'])} findings; nothing "
                       "closes on a red run", {**result, "failures": measured["failures"],
                                               "findings": measured["findings"]}, exit_code=EXIT_RED)
    for ticket in tickets:
        try:
            loads.append({"before": ticket, **_fresh(root)})
            closed = _close(root, ticket, measured["check_result"]["path"])
        except GovError as refused:
            result["closes"].append({"ticket": ticket, "refused": {
                "code": refused.code, "message": refused.message,
                "findings": refused.details.get("findings", [refused.message]),
                "repair_ticket": refused.details.get("repair_ticket")}})
            raise GovError("BATCH_CLOSE_REFUSED", f"the close of {ticket} was refused ({refused.code}): the batch "
                           "ends; the closes before it stand", result,
                           exit_code=EXIT_RED if refused.exit_code != 1 else 1)
        outputs = [f"{TICKETS_REL}/{ticket}.md", f"docs/close/{ticket}", f"docs/checkpoints/{ticket}"]
        commit = _commit(root, f"close: {ticket} (batch of {measured['head'][:12]})",
                         [p for p in outputs if (root / p).exists()], task=ticket)
        result["closes"].append({"ticket": ticket, "close_record": closed["close_record"], "commit": commit,
                                 "scope": closed[_evidence.KEY]["scope"]})
    return result, 0


def refresh(root: Path) -> dict:
    """The incremental record load at ``HEAD``; ``STORE_STALE`` where the store is not fresh at ``HEAD`` after it."""
    from gov.store import load_records

    root = Path(root)
    loaded = load_records(root)
    if _store_is_of_head(root) is not True:
        raise GovError("STORE_STALE", "the record store is not of HEAD after the record load; run gov rebuild",
                       {"head": _git(root, "rev-parse", "HEAD").strip(), "load": loaded})
    return {"load": loaded, "fresh": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.close.batch", description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="action", required=True)
    batch = commands.add_parser("run", help="the batch: one run at HEAD, then each ticket's close")
    batch.add_argument("tickets", nargs="+")
    action = commands.add_parser("refresh", help="the incremental record load at HEAD")
    for sub in (batch, action):
        sub.add_argument("--root", default=".")
        sub.add_argument("--json", action="store_true")
        sub.add_argument("--session", default="")
    args = parser.parse_args(argv)
    try:
        result, code = run(Path(args.root), args.tickets) if args.action == "run" else (refresh(Path(args.root)), 0)
    except GovError as error:
        envelope = {"ok": False, "command": COMMAND, "result": {}, "session": args.session,
                    "error": {"code": error.code, "message": error.message, "details": error.details}}
        print(json.dumps(envelope) if args.json else f"{COMMAND}: {error.code}: {error.message}")
        return error.exit_code
    envelope = {"ok": True, "command": COMMAND, "result": result, "session": args.session}
    print(json.dumps(envelope) if args.json else json.dumps(envelope, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
