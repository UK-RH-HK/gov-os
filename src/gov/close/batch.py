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
the governance check that run's record names, where it may stand in for the close's own. ``check_red_run`` holds a
close on the code of a red batch run until a green run on that code (point F).

The commits the batch makes carry ``Role:`` (the caller's ``GOV_ROLE``, else ``orchestrator``), ``Implements:
DEC-883`` and a ``Co-Authored-By:`` only where the caller's environment gives one (``GOV_CO_AUTHORED_BY``).

The design is ``docs/research/W2-68-batched-close.md``. Each answer is the API-0002 envelope, as
``gov.close.nightly`` gives it.
"""

from __future__ import annotations

import argparse
import json
import os
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


def check_red_run(root: Path) -> None:
    """``RED_RUN_ON_CODE`` (exit 1, not counted) when the newest batch run on ``HEAD``'s code is red and no green full
    run on that code is newer (the design note, section 11, point F; DEC-883 item 2 c: an unrelated ticket waits for
    a green run).

    The batch runs are the nightly folder's records of ``kind: batch`` whose head is ``HEAD`` or an ancestor of it and
    whose stated code fingerprint is ``HEAD``'s, computed now; the newest is the deepest, ties by the record's name. A
    green full run (a night or a batch) is on that code where the fingerprint it states, else its head's computed
    now, is ``HEAD``'s. Where ``HEAD``'s code fingerprint cannot be computed, no batch is on its code: nothing is
    asked."""
    root = Path(root)
    now = _fingerprint.of_commit(root, "HEAD")
    if now is None:
        return
    batches, greens = [], []
    for path in sorted((root / _select.NIGHTLY_REL).glob("*.json")):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        head = _select.full_id(root, run.get("head")) if isinstance(run, dict) and isinstance(run.get("head"), str) \
            else None
        if not head or not _select.is_ancestor(root, head):
            continue
        at = (int(_git(root, "rev-list", "--count", head).strip() or 0), path.name)
        if run.get("kind") == KIND and run.get("code_fingerprint") == now["code"]:
            batches.append((at, path.relative_to(root).as_posix(), head, run.get("verdict")))
        if run.get("verdict") == "green" and run.get("scope") == "full":
            stated = run["code_fingerprint"] if "code_fingerprint" in run else \
                (_fingerprint.of_commit(root, head) or {}).get("code")
            if stated == now["code"]:
                greens.append(at)
    if not batches:
        return
    at, rel, head, verdict = max(batches)
    if verdict != "green" and not any(green > at for green in greens):
        raise GovError("RED_RUN_ON_CODE", f"the newest batch run on HEAD's code ({rel}, at {head[:12]}) is red and no "
                       "green run on that code is newer: the close waits for a green run",
                       {"record": rel, "head": head, "code_fingerprint": now["code"]})


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
    rel = f"{BATCH_DIR}/{stamp}/{CHECK_FILE}"
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
    night = nightly.night(root, head, rebuild=False)  # rebuilt above (today's, F4)
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
    """A commit of ``paths`` alone, with the batch's trailers, as the close commits a repair ticket
    (``gov.close.tool``: the repository's identity, else ``gov``'s); its id."""
    trailers = ([f"Task: {task}"] if task else []) + [f"Role: {os.environ.get('GOV_ROLE') or DEFAULT_ROLE}",
                                                      f"Implements: {IMPLEMENTS}"]
    if os.environ.get(CO_AUTHOR_VARIABLE):
        trailers.append(f"Co-Authored-By: {os.environ[CO_AUTHOR_VARIABLE]}")
    named = _git(root, "config", "user.email", ok=(0, 1), code=True, pinned=False) == 0
    identity = [] if named else ["-c", "user.name=gov", "-c", "user.email=gov@localhost"]
    _git(root, "add", "--all", "--", *paths, pinned=False)
    _git(root, *identity, "commit", "-q", "-m", subject, *[a for t in trailers for a in ("--trailer", t)],
         "--", *paths, pinned=False)
    return _git(root, "rev-parse", "HEAD").strip()


def _fresh(root: Path) -> dict:
    """The store made fresh at ``HEAD`` before a close: the incremental record load where the store's code
    fingerprint is ``HEAD``'s, else (one that cannot be computed, or other code) a full rebuild."""
    from gov.store import load_records

    try:
        loaded = load_records(root)
    except GovError as e:
        if e.code != "STORE_CODE_CHANGED":
            raise
        return _rebuild(root)
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
    from gov.close.command import SCOPED, close_mode
    from gov.tasks.tickets import TICKETS_REL

    root = Path(root)
    if close_mode(root) == SCOPED:  # W2-115 S6: the culprit isolated before anything lands; strict: today's (F4)
        return run_scoped(root, tickets)
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


# ---------------------------------------------------------------------------
# The scoped close's batch: the culprit isolated before anything lands (W2-115 S6, F3; DEC-979 item 3, DEC-988,
# DEC-1002)
# ---------------------------------------------------------------------------
#
# ``isolate --base <commit> <candidate> ... [--test <target> ...] [--onto <branch>]``: the merged result of every
# candidate (a branch, or ``<name>=<commit>``) built on the base in the warm clone, and its selection run. On a red,
# each red is run again alone; for each candidate in turn the merged result without it is built afresh (the others
# merged onto the base: never merged code taken out) and each red run alone there; a candidate explains a red that
# is green without it. A red no single candidate explains is ``BATCH_UNEXPLAINED``; a candidate whose build without
# it cannot be made is ``CANDIDATE_NOT_ISOLATED``: both refuse the batch and nothing lands. Otherwise the culprits go
# back and the merged result of the rest, run green again, lands on the same run (``--onto``: that branch moved to
# it, only from the base). Nothing lands before every candidate is judged.

BATCH_UNEXPLAINED, CANDIDATE_NOT_ISOLATED = "BATCH_UNEXPLAINED", "CANDIDATE_NOT_ISOLATED"
EXIT_CULPRITS = 5  # landed but for the culprits sent back
_MERGE_IDENTITY = ["-c", "user.name=gov", "-c", "user.email=gov@localhost"]
LAND_REF = "refs/gov-close/land"


def _candidate(root: Path, given: str) -> dict:
    name, sep, rev = given.partition("=")
    rev = rev if sep else name
    sha = _git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", ok=(0, 1)).strip()
    if not sha:
        raise GovError(CANDIDATE_NOT_ISOLATED, f"the candidate {given} names no commit", {"candidate": given})
    return {"name": name, "commit": sha}


def _build(clone: Path, base: str, merged: list[dict]) -> str | None:
    """The base with ``merged`` merged onto it in turn, in the clone (fresh merges); its commit, or None where a
    merge cannot be made."""
    from gov.close import attribution as _attribution

    _attribution.checkout(clone, base)
    for cand in merged:
        done = _attribution._git(clone, *_MERGE_IDENTITY, "merge", "--no-ff", "--no-edit", "-q",
                                 "-m", f"batch: merge {cand['name']}", cand["commit"])
        if done.returncode != 0:
            _attribution._git(clone, "merge", "--abort")
            return None
    return _attribution._git(clone, "rev-parse", "HEAD").stdout.strip()


def _entangled(root: Path, base: str, candidates: list[dict]) -> tuple[str, str] | None:
    """The first candidate that cannot be isolated and the candidate it shares work with: two candidates whose
    commits past the base overlap (one built on the other, or both on a common unmerged commit), since the build
    without one still holds its work through the other. Checked before anything runs (fail closed: the batch is
    refused even when the run would be green). The candidate named is the one whose work the other holds (an
    ancestor's), else the first in order."""
    own = {c["name"]: set(_git(root, "rev-list", f"{base}..{c['commit']}").split()) for c in candidates}
    for n, cand in enumerate(candidates):
        for other in candidates[n + 1:]:
            if not own[cand["name"]] & own[other["name"]]:
                continue
            if own[other["name"]] <= own[cand["name"]]:
                return other["name"], cand["name"]
            return cand["name"], other["name"]
    return None


def _targets(clone: Path, candidates: list[dict], given: list[str] | None) -> dict:
    """The run's selection: the targets given, else the union of the candidates' scoped selections (each a ticket
    of the project) at the merged result."""
    if given:
        return {"suites": sorted(dict.fromkeys(given)), "pytest_options": _select.pytest_options(
            _select.load_map(clone)[0])}
    suites, options = [], None
    for cand in candidates:
        try:
            chosen = _select.scoped(clone, cand["name"])
        except _select.SelectionRefused as refused:
            raise GovError(_select.SELECTION_REFUSED, f"{cand['name']}: {refused.reason}",
                           {"candidate": cand["name"]}, exit_code=EXIT_RED)
        suites += chosen["suites"]
        options = chosen["pytest_options"]
    return {"suites": sorted(dict.fromkeys(suites)), "pytest_options": options or list(_select.PYTEST_OPTIONS)}


def isolate(root: Path, base: str, given: list[str], targets: list[str] | None = None, onto: str | None = None,
            timeout: float = 3600) -> tuple[dict, int]:
    """The batch (S6): ``(result, exit code)``; a ``GovError`` for a refusal (nothing landed)."""
    from gov.close import attribution as _attribution
    from gov.close.command import _phases

    root = Path(root)
    base_sha = _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", ok=(0, 1)).strip()
    if not base_sha:
        raise GovError("BASE_UNKNOWN", f"--base {base} names no commit", {"base": base})
    if not given:
        raise GovError(CANDIDATE_NOT_ISOLATED, "the batch names no candidate", {"candidates": []})
    candidates = [_candidate(root, g) for g in given]
    stamp = _stamp()
    folder = root / BATCH_DIR / stamp
    try:
        clone_state = _attribution.prepare(root, base_sha)
    except _attribution.CloneError as e:
        raise GovError("CLOSE_CLONE_FAILED", f"the batch's clone cannot be made: {e}", {"base": base_sha})
    clone = root / clone_state["path"]
    result = {"base": base_sha, "candidates": [c["name"] for c in candidates], "culprits": [], "landed": [],
              "land_commit": None, "reds": [], "flaky": [], "clone": clone_state, "folder": str(folder)}

    def refuse(code: str, message: str, **more):
        raise GovError(code, message + "; nothing lands", {**result, **more}, exit_code=EXIT_RED)

    def run_on(commit: str, chosen: dict, name: str) -> dict:
        _attribution.checkout(clone, commit)
        phases = _phases(clone, chosen, folder / name, timeout, 1)
        if not phases["complete"]:
            refuse("RUN_INCOMPLETE", f"the run on {name} did not complete: {'; '.join(phases['incomplete'])}")
        return phases

    shared = _entangled(root, base_sha, candidates)
    if shared:
        name, other = shared
        refuse(CANDIDATE_NOT_ISOLATED, f"{name} cannot be isolated: its work shares commits past the base with "
               f"{other}, so the merged result without {name} still holds its work",
               candidate=name, shares_with=other)
    whole = _build(clone, base_sha, candidates)
    if whole is None:
        bad = next((c["name"] for n, c in enumerate(candidates) if _build(clone, base_sha, candidates[:n + 1]) is None),
                   candidates[-1]["name"])
        refuse(CANDIDATE_NOT_ISOLATED, f"the candidates cannot be merged together on the base: {bad} does not merge",
               candidate=bad)
    chosen = _targets(clone, candidates, targets)
    result["selection"] = chosen
    phases = run_on(whole, chosen, "batch")
    result["runs"] = phases["runs"]
    options = chosen["pytest_options"]
    reds = []
    for test in dict.fromkeys(f["test"] for f in phases["failing"]):
        alone = _attribution.run_alone(clone, test, options, folder / "alone", timeout, "batch")
        (reds if alone is not None else result["flaky"]).append(test)
    result["reds"] = reds
    land, landed = whole, candidates
    if reds:
        explains: dict[str, list[str]] = {r: [] for r in reds}
        absent: list[tuple[str, dict]] = []
        for cand in candidates:
            others = [c for c in candidates if c is not cand]
            without = _build(clone, base_sha, others)
            if without is None:
                refuse(CANDIDATE_NOT_ISOLATED, f"the merged result without {cand['name']} cannot be built (the "
                       "others do not merge without it)", candidate=cand["name"])
            for red in reds:
                seen = _attribution.run_alone(clone, red, options, folder / "alone", timeout,
                                              f"without-{cand['name']}")
                if seen is None:
                    explains[red].append(cand["name"])
                elif seen == _attribution.ABSENT:
                    absent.append((red, cand))
        # a red that cannot run without a candidate (its own new test) is that candidate's only once it is red again
        # on the base with that candidate alone (a real failure: no timeout, no unknown); else it stays unexplained
        for red, cand in absent:
            alone = _build(clone, base_sha, [cand])
            if alone is None:
                continue
            seen = _attribution.run_alone(clone, red, options, folder / "alone", timeout, f"alone-{cand['name']}")
            if seen is not None and seen not in _attribution.NEVER_MATCH:
                explains[red].append(cand["name"])
        result["explains"] = explains
        unexplained = [r for r, names in explains.items() if not names]
        if unexplained:
            refuse(BATCH_UNEXPLAINED, f"{len(unexplained)} red(s) no single candidate explains: "
                   f"{', '.join(unexplained)}", unexplained=unexplained)
        culprits = sorted({n for names in explains.values() for n in names},
                          key=[c["name"] for c in candidates].index)
        result["culprits"] = culprits
        landed = [c for c in candidates if c["name"] not in culprits]
        if landed:
            land = _build(clone, base_sha, landed)
            if land is None:
                refuse(CANDIDATE_NOT_ISOLATED, "the candidates left after the culprits cannot be merged together")
            rest = run_on(land, chosen, "rest")
            result["rest_runs"] = rest["runs"]
            if rest["failing"]:
                refuse(BATCH_UNEXPLAINED, "the merged result without the culprits is not green: "
                       + ", ".join(dict.fromkeys(f["test"] for f in rest["failing"])))
        else:
            land = None
    if land is not None:
        _attribution._git(clone, "update-ref", LAND_REF, land)
        _git(root, "fetch", "--quiet", "--no-tags", str(clone.resolve()), f"+{LAND_REF}:{LAND_REF}", pinned=False)
        if onto:
            current = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD", ok=(0, 1)).strip()
            if current == onto:
                _git(root, "merge", "--ff-only", "-q", land, pinned=False)
            else:
                _git(root, "update-ref", f"refs/heads/{onto}", land, base_sha, pinned=False)
        result["land_commit"] = land
        result["landed"] = [c["name"] for c in landed]
    _attribution.checkout(clone, base_sha)
    return result, (EXIT_CULPRITS if result["culprits"] else 0)


WORK_BRANCH = "w2/{wbs}"


def run_scoped(root: Path, tickets: list[str], timeout: float = 3600) -> tuple[dict, int]:
    """``run`` in a scoped project (S6, F3): each ticket a candidate whose work is on its unmerged ``w2/<wbs_id>``
    branch, isolated on ``HEAD`` by ``isolate`` before anything lands; the culprits are sent back (not landed, not
    closed), the rest land and are closed on the same run: each landed ticket's close record names the land commit
    and the culprits. ``BATCH_UNEXPLAINED`` and ``CANDIDATE_NOT_ISOLATED`` refuse the batch: nothing lands or
    closes. A ticket whose review is not READY (S11) refuses the batch before anything runs."""
    from gov.close import attribution as _attribution
    from gov.close import command as _command
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    root = Path(root)
    _refuse_unless_ready(root, tickets)
    base_sha = _git(root, "rev-parse", "HEAD").strip()
    branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD", ok=(0, 1)).strip() or None
    given = []
    for ticket in tickets:
        front = frontmatter(root / TICKETS_REL / f"{ticket}.md") or {}
        ref = WORK_BRANCH.format(wbs=str(front.get("wbs_id") or front.get("external-ref") or ticket))
        sha = _git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{ref}^{{commit}}", ok=(0, 1)).strip()
        if not sha:
            raise GovError(CANDIDATE_NOT_ISOLATED, f"{ticket}: its work branch {ref} names no commit, so it cannot be "
                           "isolated; nothing lands", {"candidate": ticket, "branch": ref}, exit_code=EXIT_RED)
        if _select.is_ancestor(root, sha, base_sha):
            raise GovError(CANDIDATE_NOT_ISOLATED, f"{ticket}: its work branch {ref} is already merged, so the build "
                           "without it cannot be made; nothing lands", {"candidate": ticket, "branch": ref},
                           exit_code=EXIT_RED)
        given.append({"name": ticket, "commit": sha, "branch": ref})
    reviews = _reviews(root, base_sha, given)
    result, code = isolate(root, base_sha, [f"{c['name']}={c['commit']}" for c in given], None, onto=branch,
                           timeout=timeout)
    result["closes"] = []
    land = result["land_commit"]
    if land is None:
        return result, code
    if branch is None:
        _git(root, "merge", "--ff-only", "-q", land, pinned=False)
    # every landed ticket's selection at the land commit, before any close record moves HEAD
    try:
        chosen = {t: _select.scoped(root, t) for t in result["landed"]}
    except _select.SelectionRefused as refused:
        raise GovError(_select.SELECTION_REFUSED, f"landed at {land[:12]} but nothing closed: {refused.reason}",
                       result, exit_code=EXIT_RED)
    runs = result.get("rest_runs") or result.get("runs") or []
    night = _attribution.nightly_reading(root)
    clone = result["clone"]
    for ticket in result["landed"]:
        record = {
            "close": _command.SCOPED,
            "commit": land,
            "selection": {"suites": chosen[ticket]["suites"], "pytest_options": chosen[ticket]["pytest_options"]},
            "runs": runs,
            "review": {"verdict": reviews[ticket]["verdict"], "record": reviews[ticket]["record"]},
            "reds": [],
            "culprits": list(result["culprits"]),
            "clone": {"path": clone["path"], "reused": clone["reused"], "replaced": clone["replaced"]},
            "nightly": {"read": night["read"], "record": night["record"]},
            "base": base_sha,
            "changed": chosen[ticket]["changed"],
            "batch": {"candidates": result["candidates"], "landed": result["landed"], "land_commit": land},
        }
        close_rel, checkpoint = _command._record_and_close(root, ticket, record, list(chosen[ticket]["own"]))
        outputs = [f"{TICKETS_REL}/{ticket}.md", f"docs/close/{ticket}", f"docs/checkpoints/{ticket}"]
        commit = _commit(root, f"close: {ticket} (batch landed at {land[:12]})",
                         [p for p in outputs if (root / p).exists()], task=ticket)
        result["closes"].append({"ticket": ticket, "close_record": close_rel, "checkpoint": checkpoint,
                                 "commit": commit, "closed_commit": land})
    return result, code


def _reviews(root: Path, base: str, candidates: list[dict]) -> dict:
    """Each candidate's review verdict (S11), read in the warm clone at the base with that candidate merged onto
    it: READY for each, else the batch is refused with the first refusal's code before anything runs."""
    from gov.close import attribution as _attribution
    from gov.close import command as _command
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    try:
        state = _attribution.prepare(root, base)
    except _attribution.CloneError as e:
        raise GovError("CLOSE_CLONE_FAILED", f"the batch's clone cannot be made: {e}", {"base": base})
    clone = root / state["path"]
    found = {}
    try:
        for cand in candidates:
            if _build(clone, base, [cand]) is None:
                raise GovError(CANDIDATE_NOT_ISOLATED, f"{cand['name']} does not merge onto the base; nothing lands",
                               {"candidate": cand["name"]}, exit_code=EXIT_RED)
            front = frontmatter(clone / TICKETS_REL / f"{cand['name']}.md") or {}
            review = _command.review_verdict(clone, cand["name"], front)
            if review["verdict"] != _command.READY:
                raise GovError(review["verdict"], f"{cand['name']}: " + "; ".join(review["reasons"])
                               + "; nothing lands", {"candidate": cand["name"], "review": review},
                               exit_code=EXIT_RED)
            found[cand["name"]] = review
    finally:
        _attribution.checkout(clone, base)
    return found


def refresh(root: Path) -> dict:
    """The incremental record load at ``HEAD``; ``STORE_STALE`` where the store is not fresh at ``HEAD`` after it."""
    from gov.store import load_records

    root = Path(root)
    loaded = load_records(root)
    if _store_is_of_head(root) is not True:
        raise GovError("STORE_STALE", "the record store is not of HEAD after the record load; run gov rebuild",
                       {"head": _git(root, "rev-parse", "HEAD").strip(), "load": loaded})
    return {"load": loaded, "fresh": True}


def _scoped_action(args) -> bool:
    """The scoped batch's action (``isolate``, or ``run`` in a scoped project); the strict batch prints as today."""
    from gov.close.command import SCOPED, close_mode

    if args.action == "isolate":
        return True
    try:
        return args.action == "run" and close_mode(Path(args.root)) == SCOPED
    except GovError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.close.batch", description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="action", required=True)
    batch = commands.add_parser("run", help="the batch: one run at HEAD, then each ticket's close")
    batch.add_argument("tickets", nargs="+")
    action = commands.add_parser("refresh", help="the incremental record load at HEAD")
    scoped = commands.add_parser("isolate", help="the scoped close's batch: the culprit isolated before anything "
                                 "lands (W2-115)")
    scoped.add_argument("candidates", nargs="+", help="a branch, or <name>=<commit>")
    scoped.add_argument("--base", required=True, help="the commit the candidates merge onto")
    scoped.add_argument("--test", action="append", default=None, help="a target to run (default: the candidates' "
                        "scoped selections)")
    scoped.add_argument("--onto", default=None, help="the branch the rest lands on (moved only from the base)")
    scoped.add_argument("--timeout", type=float, default=3600)
    for sub in (batch, action, scoped):
        sub.add_argument("--root", default=".")
        sub.add_argument("--json", action="store_true")
        sub.add_argument("--session", default="")
    args = parser.parse_args(argv)
    try:
        if args.action == "isolate":
            result, code = isolate(Path(args.root), args.base, args.candidates, args.test, args.onto, args.timeout)
        else:
            result, code = run(Path(args.root), args.tickets) if args.action == "run" \
                else (refresh(Path(args.root)), 0)
    except GovError as error:
        envelope = {"ok": False, "command": COMMAND, "result": {}, "session": args.session,
                    "error": {"code": error.code, "message": error.message, "details": error.details}}
        print(json.dumps(envelope) if args.json else f"{COMMAND}: {error.code}: {error.message}")
        if args.json and _scoped_action(args):  # W2-115: the code on stderr too, as the close's refusals print it
            print(f"{error.code}: {error.message}", file=sys.stderr)
        return error.exit_code
    envelope = {"ok": True, "command": COMMAND, "result": result, "session": args.session}
    print(json.dumps(envelope) if args.json else json.dumps(envelope, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
