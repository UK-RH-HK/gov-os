"""``gov queue <ticket>[=<branch>] ... [--onto <branch>]``: the product's deterministic landing (W2-115b).

A thin queue on the close's pieces (EMERGENCY-2 4.3 step 3; audit 1 question 1 (b)):

1. **Settings.** The integration branch is ``--onto``, else ``governance/project/queue.yaml``'s ``integration``,
   else the branch checked out at the root (``INTEGRATION_UNKNOWN``). A ticket's work branch is ``=<branch>``,
   else ``queue.yaml``'s ``work_branch`` form with ``{wbs}`` and ``{ticket}`` (``BRANCH_UNKNOWN``). The ticket is
   read at the integration head (``TICKET_UNKNOWN``, ``TICKET_CLOSED``). All exit 1, before anything is written.
2. **Checks** on ``<head>..<tip>`` (``gov.queue.checks``): G-1 refuses a ticket (``TEST_AUTHOR_REFUSED``, out of
   the batch before the run); a path outside ``allowed_paths`` is a notice.
3. **The run.** The candidates left are merged onto the head in the warm clone; the union of their
   ``select.scoped`` selections (each branch's changed paths counted in its change) is run once by
   ``gov.close.batch.isolate``, which re-runs a red alone, finds the culprit and runs the rest again.
4. **The land.** One close commit per landed ticket on the tested merge, in the clone (its close record, its
   checkpoint, ``tk close``); then the integration branch moves from the head the run merged onto to the last
   close commit, only if it is still there (``HEAD_MOVED``); where it is checked out, its working tree follows.

The answer and ``.gov-runtime/queue/<stamp>/queue.json`` hold the same result, with the seconds of each step.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from gov.cli.errors import GovError

HELP = "land tickets' branches: one run on the merged result, the close at the land"
CLASS = "act"
EXIT_RED = 3
EXIT_CODES = {EXIT_RED: "a candidate did not land, or the run was refused as a whole (nothing of it landed)"}
ACT_PATHS = (".gov-runtime/**", ".tickets/**", "docs/close/**", "docs/checkpoints/**")
SETTINGS_REL = "governance/project/queue.yaml"
QUEUE_DIR = ".gov-runtime/queue"
ACCEPTANCE = "tests/acceptance/"
LAND_REF = "refs/gov-queue/land"
DEFAULT_TIMEOUT = 3600
DEFAULT_ROLE = "orchestrator"
_TICKET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
STEPS = ("merge", "selection", "run", "close")


def add_arguments(parser) -> None:
    parser.add_argument("tickets", nargs="+", metavar="<ticket>[=<branch>]", help="the tickets to land")
    parser.add_argument("--onto", metavar="<branch>", help="the integration branch")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, metavar="<seconds>",
                        help="each test run's time limit")


def run(root: Path, args, config: dict):
    try:
        return land(Path(root), list(args.tickets), args.onto, args.timeout)
    except GovError as error:
        if getattr(args, "json", False):  # the envelope on stdout, the line on stderr too (without --json gov prints it)
            print(f"{error.code}: {error.message}", file=sys.stderr)
        raise


def _git(cwd: Path, *args: str, ok: bool = False) -> str | None:
    """git's output; None where it fails and ``ok``, else ``RuntimeError``."""
    from gov.close.attribution import _git as git

    done = git(cwd, "-c", "core.quotePath=false", *args)
    if done.returncode:
        if ok:
            return None
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {' '.join(done.stderr.split())[:300]}")
    return done.stdout


def _refuse(code: str, message: str, details: dict | None = None, exit_code: int = 1):
    raise GovError(code, message, details or {}, exit_code=exit_code)


def _settings(root: Path) -> dict:
    import yaml

    path = root / SETTINGS_REL
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
        _refuse("INTEGRATION_UNKNOWN", f"{SETTINGS_REL} cannot be read ({type(e).__name__})", {"settings": SETTINGS_REL})
    if not isinstance(data, dict):
        _refuse("INTEGRATION_UNKNOWN", f"{SETTINGS_REL} is not a mapping", {"settings": SETTINGS_REL})
    return data


def _commit_of(root: Path, rev: str) -> str | None:
    return (_git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", ok=True) or "").strip() or None


def _front_at(root: Path, rev: str, ticket: str) -> dict | None:
    from gov.util.frontmatter import parse

    text = _git(root, "show", f"{rev}:.tickets/{ticket}.md", ok=True)
    return parse(text) if text is not None else None


def _candidate(root: Path, base: str, given: str, settings: dict) -> dict:
    ticket, sep, branch = given.partition("=")
    front = _front_at(root, base, ticket) if _TICKET.fullmatch(ticket) else None
    if not isinstance(front, dict):
        _refuse("TICKET_UNKNOWN", f"{ticket} is not a ticket file .tickets/{ticket}.md at the integration head",
                {"ticket": ticket})
    if str(front.get("status")) == "closed":
        _refuse("TICKET_CLOSED", f"{ticket} is closed at the integration head", {"ticket": ticket})
    wbs = str(front.get("wbs_id") or front.get("external-ref") or ticket)
    if not sep:
        form = settings.get("work_branch")
        if not isinstance(form, str) or not form.strip():
            _refuse("BRANCH_UNKNOWN", f"{ticket}: no branch given and {SETTINGS_REL} names no work_branch form",
                    {"ticket": ticket})
        branch = form.replace("{wbs}", wbs).replace("{ticket}", ticket)
    tip = _commit_of(root, f"refs/heads/{branch}") or _commit_of(root, branch) if branch else None
    if not tip:
        _refuse("BRANCH_UNKNOWN", f"{ticket}: its work branch {branch!r} names no commit",
                {"ticket": ticket, "branch": branch})
    if _git(root, "merge-base", "--is-ancestor", tip, base, ok=True) is not None:
        _refuse("CANDIDATE_NOT_ISOLATED", f"{ticket}: its work branch {branch} is already merged; nothing lands",
                {"ticket": ticket, "branch": branch}, EXIT_RED)
    at_tip = _front_at(root, tip, ticket)
    return {"ticket": ticket, "branch": branch, "tip": tip, "front": front,
            "at_tip": at_tip if isinstance(at_tip, dict) else front}


def _acceptance(front: dict) -> str | None:
    tests = front.get("acceptance_tests")
    path = tests.get("path") if isinstance(tests, dict) else None
    return path if isinstance(path, str) and path.strip("/") else None


def _changed(root: Path, base: str, tip: str) -> list[str]:
    names = _git(root, "diff", "-z", "--no-renames", "--name-only", f"{base}...{tip}")
    return sorted(set(filter(None, names.split("\0"))))


def _checks(root: Path, base: str, cand: dict, result: dict) -> bool:
    """G-1 and the path notice of a candidate; False where G-1 refuses it."""
    from gov.queue import checks

    ticket = cand["ticket"]
    places = list(dict.fromkeys(p for p in (ACCEPTANCE, _acceptance(cand["front"]), _acceptance(cand["at_tip"])) if p))
    allowed = [p for p in cand["at_tip"].get("allowed_paths") or [] if isinstance(p, str)]
    try:
        notices = checks.path_notices(root, base, cand["tip"], allowed,
                                      checks.record_places(ticket, _acceptance(cand["at_tip"])))
        result["path_notices"] += [{"ticket": ticket, **n} for n in notices]
        bad = checks.test_authors(root, base, cand["tip"], places)
        reason = "; ".join(f"{b['commit'][:12]} (Role: {', '.join(b['roles']) or 'none'}) {b['subject']}"
                           for b in bad)
    except RuntimeError as e:  # fails closed: commits that cannot be read are not landed
        bad, reason = [], f"the branch's commits cannot be read: {e}"
    if bad or reason:
        result["refused"].append({"ticket": ticket, "code": "TEST_AUTHOR_REFUSED", "commits": [b["commit"] for b in bad],
                                  "reason": f"acceptance tests changed without the test designer's or the owner's "
                                            f"role: {reason}"})
        return False
    return True


def _identity(root: Path) -> list[str]:
    """The committer of the close commits: the project's own git identity, else the batch's."""
    name = (_git(root, "config", "user.name", ok=True) or "").strip()
    email = (_git(root, "config", "user.email", ok=True) or "").strip()
    return ["-c", f"user.name={name or 'gov'}", "-c", f"user.email={email or 'gov@localhost'}"]


def _close_all(root: Path, clone: Path, cands: list[dict], record: dict, result: dict) -> str:
    """One close commit per landed candidate on the tested merge, in the clone; the last one."""
    from gov.close import attribution, command as close

    attribution.checkout(clone, result["tested"])
    who, role = _identity(root), os.environ.get("GOV_ROLE") or DEFAULT_ROLE
    for cand in cands:
        ticket = cand["ticket"]
        own = {**record, "branch": {"name": cand["branch"], "tip": cand["tip"]},
               "path_notices": [n for n in result["path_notices"] if n["ticket"] == ticket]}
        close_rel, _ = close._record_and_close(clone, ticket, own, _changed(root, result["base"], cand["tip"]))
        places = [p for p in (f".tickets/{ticket}.md", f"docs/close/{ticket}", f"docs/checkpoints/{ticket}")
                  if (clone / p).exists()]
        _git(clone, "add", "-A", "--", *places)
        _git(clone, *who, "commit", "-q", "--no-verify", "--no-gpg-sign", "-m",
             f"close: {ticket} (gov queue landed at {result['tested'][:12]})\n\nTask: {ticket}\nRole: {role}\n")
        commit = _git(clone, "rev-parse", "HEAD").strip()
        result["closes"].append({"ticket": ticket, "close_record": close_rel, "commit": commit})
    return result["closes"][-1]["commit"]


def _checked_out(root: Path, branch: str) -> Path | None:
    """The worktree where ``branch`` is checked out, or None."""
    listed = _git(root, "worktree", "list", "--porcelain", ok=True) or ""
    path = None
    for line in listed.splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree "):])
        elif line == f"branch refs/heads/{branch}" and path is not None:
            return path
    return None


def _move(root: Path, clone: Path, onto: str, base: str, last: str, result: dict) -> None:
    """The integration branch from ``base`` to ``last``, only from ``base``; ``HEAD_MOVED`` otherwise."""
    def moved():
        _refuse("HEAD_MOVED", f"{onto} moved during the run (it is no longer at {base[:12]}); nothing lands",
                {**result, "now": _commit_of(root, f"refs/heads/{onto}")}, EXIT_RED)

    _git(clone, "update-ref", LAND_REF, last)
    _git(root, "fetch", "--quiet", "--no-tags", str(clone.resolve()), f"+{LAND_REF}:{LAND_REF}")
    tree = _checked_out(root, onto)
    if tree is None:
        if _git(root, "update-ref", f"refs/heads/{onto}", last, base, ok=True) is None:
            moved()
    else:
        if _commit_of(tree, "HEAD") != base:
            moved()
        if _git(tree, "merge", "--ff-only", "-q", last, ok=True) is None:
            if _commit_of(tree, "HEAD") != base:
                moved()
            _refuse("LAND_BLOCKED", f"{onto}'s working tree at {tree} does not take the fast-forward to "
                    f"{last[:12]} (local changes in its way); nothing lands", result, EXIT_RED)
    _git(root, "update-ref", "-d", LAND_REF, ok=True)


def _write(root: Path, result: dict, error: GovError | None = None) -> None:
    path = root / result["record"]
    path.parent.mkdir(parents=True, exist_ok=True)
    held = {"ok": error is None, "result": result}
    if error is not None:
        held["error"] = {"code": error.code, "message": error.message}
    path.write_text(json.dumps(held, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def land(root: Path, given: list[str], onto: str | None = None,
         timeout: float = DEFAULT_TIMEOUT) -> tuple[dict, int]:
    """The landing: ``(result, exit code)``, or a ``GovError`` where nothing landed."""
    from gov.close import attribution, batch, select

    start = time.monotonic()
    root = Path(root).resolve()
    settings = _settings(root)
    if not onto:
        onto = settings.get("integration") if isinstance(settings.get("integration"), str) else None
    if not onto:
        onto = (_git(root, "symbolic-ref", "--quiet", "--short", "HEAD", ok=True) or "").strip() or None
    base = _commit_of(root, f"refs/heads/{onto}") if onto else None
    if not base:
        why = f"{onto} names no branch" if onto else f"no --onto, no integration in {SETTINGS_REL}, no branch " \
            "checked out at the root"
        _refuse("INTEGRATION_UNKNOWN", f"the integration branch is unknown: {why}", {"onto": onto})
    cands = [_candidate(root, base, g, settings) for g in given]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    seconds = dict.fromkeys(STEPS, 0.0)
    result = {"onto": onto, "base": base, "candidates": [c["ticket"] for c in cands], "landed": [], "culprits": [],
              "refused": [], "reds": [], "flaky": [], "tested": None, "head": None, "closes": [],
              "selection": {"suites": [], "pytest_options": []}, "runs": [], "path_notices": [],
              "seconds": seconds, "record": f"{QUEUE_DIR}/{stamp}/queue.json"}

    def finish(code: int, error: GovError | None = None):
        seconds["total"] = round(time.monotonic() - start, 3)
        _write(root, result, error)
        if error is not None:
            error.details.update(record=result["record"], seconds=seconds)
            raise error
        return result, code

    def timed(step: str, began: float) -> None:
        seconds[step] = round(time.monotonic() - began, 3)

    try:
        left = [c for c in cands if _checks(root, base, c, result)]
        if not left:
            return finish(EXIT_RED)
        began = time.monotonic()
        try:
            clone = root / attribution.prepare(root, base)["path"]
        except attribution.CloneError as e:
            _refuse("CLOSE_CLONE_FAILED", f"the queue's clone cannot be made: {e}", {"base": base})
        merged = batch._build(clone, base, [{"name": c["ticket"], "commit": c["tip"]} for c in left])
        timed("merge", began)
        if merged is None:
            _refuse("CANDIDATE_NOT_ISOLATED", "the candidates do not merge together onto the integration head; "
                    "nothing lands", {"candidates": [c["ticket"] for c in left]}, EXIT_RED)
        began = time.monotonic()
        suites, options = [], None
        for cand in left:
            try:
                chosen = select.scoped(clone, cand["ticket"], change=_changed(root, base, cand["tip"]))
            except select.SelectionRefused as refused:
                _refuse(select.SELECTION_REFUSED, f"{cand['ticket']}: {refused.reason}; nothing lands",
                        {"candidate": cand["ticket"]}, EXIT_RED)
            suites += chosen["suites"]
            options = chosen["pytest_options"]
        result["selection"] = {"suites": sorted(dict.fromkeys(suites)), "pytest_options": options or []}
        timed("selection", began)
        began = time.monotonic()
        try:
            done, _ = batch.isolate(root, base, [f"{c['ticket']}={c['tip']}" for c in left],
                                    targets=result["selection"]["suites"], onto=None, timeout=timeout)
        finally:
            timed("run", began)
        result.update({k: done[k] for k in ("reds", "flaky", "culprits")}, tested=done["land_commit"])
        result["runs"] = done.get("runs", []) + [{**r, "name": f"rest:{r['name']}"} for r in done.get("rest_runs", [])]
        landed = [c for c in left if c["ticket"] in done["landed"]]
        if result["tested"] is None:
            return finish(EXIT_RED)
        began = time.monotonic()
        explains = done.get("explains") or {}
        record = {"close": "queue", "commit": result["tested"], "selection": result["selection"],
                  "runs": result["runs"],
                  "reds": [{"test": t, "verdict": "flaky"} for t in result["flaky"]]
                  + [{"test": t, "verdict": "culprit", "culprits": explains.get(t, [])} for t in result["reds"]],
                  "culprits": result["culprits"], "base": base, "onto": onto, "queue": result["record"]}
        last = _close_all(root, clone, landed, record, result)
        _move(root, clone, onto, base, last, result)
        timed("close", began)
        result.update(head=last, landed=[c["ticket"] for c in landed])
        return finish(EXIT_RED if len(landed) < len(cands) else 0)
    except RuntimeError as e:  # a git step that failed: nothing has moved
        return finish(1, GovError("GIT_FAILED", f"{e}; nothing lands", {"reds": result["reds"]}))
    except GovError as error:
        result["reds"] = error.details.get("reds", result["reds"])
        error.details["reds"] = result["reds"]
        return finish(EXIT_RED, error)
