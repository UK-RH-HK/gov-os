"""``gov queue <ticket>[=<branch>] ... [--onto <branch>]``: the product's deterministic landing (W2-115b), which
is the close too (W2-202; L2 section 2).

A thin queue on the close's pieces (EMERGENCY-2 4.3 step 3; audit 1 question 1 (b)):

0. **The hold.** While ``gov pause`` froze the project nothing lands (``PROJECT_PAUSED``, exit 1, before anything
   else is read or written).
1. **Settings.** The integration branch is ``--onto``, else ``governance/project/queue.yaml``'s ``integration``,
   else the branch checked out at the root (``INTEGRATION_UNKNOWN``). A ticket's work branch is ``=<branch>``,
   else ``queue.yaml``'s ``work_branch`` form with ``{wbs}`` and ``{ticket}`` (``BRANCH_UNKNOWN``). The ticket is
   read at the integration head (``TICKET_UNKNOWN``, ``TICKET_CLOSED``). All exit 1, before anything is written.
   A closed ticket's branch is a **fix landing** (W2-201 fix X6, DEC-1219 (5)) when one of its commits carries the
   ticket's ``Task:`` and a ``Fix:`` trailer (``checks.fix_line``); any other branch of a closed ticket is
   ``TICKET_CLOSED``. A fix landing is a candidate as any other, and lands with no second close (step 4).
   A branch whose tip is already on the integration branch (merged by hand) is landed alone and without a merge:
   its change is counted from the head before the merge that brought it.
2. **Checks** on ``<head>..<tip>`` (``gov.queue.checks``): G-1 refuses a ticket (``TEST_AUTHOR_REFUSED``, out of
   the batch before the run); a path outside ``allowed_paths`` is a notice, and so is a ticket file the branch adds
   that is not a feature (no ``kpis.success`` line with its verify, or no spec: ``NEW_TICKET_NOT_FEATURE``, W2-201
   fix X4, DEC-1219 (5)), said as one line on stderr and kept under ``ticket_notices``, in the answer, ``queue.json``
   and the landed ticket's close record; neither notice refuses or changes the exit code. A ticket judged on its
   tests whose acceptance folder holds no test is refused (``NO_ACCEPTANCE_TESTS``), and one whose README the runner of
   ``gov accept`` cannot judge by, with the runner's code. A ticket of a class judged on a record (research,
   audit, coordination, specification) is judged by the close's own gate of that record, in the clone, and needs
   no test folder; a record the gate refuses puts the ticket out of the batch with the gate's code.
3. **The run.** The candidates left are merged onto the head in the warm clone; the union of their
   ``select.scoped`` selections (each branch's changed paths counted in its change), less their own acceptance
   folders, is run once by ``gov.close.batch.isolate``, which also runs each ticket's acceptance folder through
   the runner of ``gov accept`` (``gov.queue.acceptance``: no test of it runs twice), re-runs a red alone, finds
   the culprit and runs the rest again. A red no candidate explains that is red at the base with the same failure
   type is a known base red: named, not blocking.
4. **The land.** One close commit per landed ticket on the tested commit, in the clone (its close record, its
   checkpoint, ``tk close``); a fix landing's commit is ``fix: <ticket> ...`` instead and only appends the fix to
   the ticket's close record (``gov.queue.fix``; ``tk close`` is not reached, the ticket stays closed), and its
   ``closes`` entry adds ``fix: true`` and ``fix_line``; then the integration branch moves from the head the run merged onto to the last
   close commit, only if it is still there (``HEAD_MOVED``); where it is checked out, its working tree follows.
5. **After** (``gov.queue.after``; never refuses): the integration store's refresh where ``rebuild.yaml`` names
   one, and the structural pass with the landing's base; both are notices under ``after``.

The answer and ``.gov-runtime/queue/<stamp>/queue.json`` hold the same result, with the seconds of each step.

The flags of W2-206 (L2 section 3, A6):

- ``--dry-run [--out <dir>]``: steps 0 to 3 and nothing else. No close commit, no close record, no branch and no
  ref moves; the warm clone is left at the base. The answer and the exit code are those the landing would have
  given (a fix landing that would land is named in ``closes`` with ``fix: true``, ``fix_line`` and a null
  ``commit`` and ``close_record``); ``<dir>`` gets ``select.json``, the run files, ``summary.txt`` and, last, ``verify.exit``
  (``gov.queue.dry``), also when the dry run is refused as a whole.
- ``--select``: the selection the run would make, as one JSON object on stdout, exit 0; nothing is run or
  recorded. ``SELECTION_REFUSED`` goes to stderr with exit 2.
- ``--full``: the run of step 3 is the whole ``tests/`` of the merged result (``gov.queue.full``), in a pool no
  wider than its slot; a selection is not computed, so no path is ``SELECTION_REFUSED``.
"""

from __future__ import annotations

import contextlib
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
EXIT_SELECT_REFUSED = 2
CHILD_EXIT_CODE = True  # --select prints the selection itself and ends with its own code, 0 or 2
EXIT_CODES = {EXIT_RED: "a candidate did not land, or the run was refused as a whole (nothing of it landed)"}
ACT_PATHS = (".gov-runtime/**", ".tickets/**", "docs/close/**", "docs/checkpoints/**")
SETTINGS_REL = "governance/project/queue.yaml"
QUEUE_DIR = ".gov-runtime/queue"
ACCEPTANCE = "tests/acceptance/"
LAND_REF = "refs/gov-queue/land"
DEFAULT_TIMEOUT = 3600
DEFAULT_ROLE = "orchestrator"
_TICKET = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
STEPS = ("merge", "selection", "acceptance", "run", "close")


def add_arguments(parser) -> None:
    parser.add_argument("tickets", nargs="+", metavar="<ticket>[=<branch>]", help="the tickets to land")
    parser.add_argument("--onto", metavar="<branch>", help="the integration branch")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, metavar="<seconds>",
                        help="each test run's time limit")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="dry_run", action="store_true",
                      help="everything but the land: no close commit, no branch moved; the answer and exit code "
                           "the landing would give, and select.json, the run files, summary.txt and verify.exit "
                           "under --out")
    mode.add_argument("--select", action="store_true",
                      help="print the selection the run would make as one JSON object and run nothing "
                           "(SELECTION_REFUSED: stderr, exit 2)")
    parser.add_argument("--out", metavar="<dir>", default=None,
                        help="--dry-run: the folder of its files (default .gov-runtime/queue/dry/<ticket>/, the "
                             "tickets joined by +)")
    parser.add_argument("--full", action="store_true",
                        help="run the whole tests/ of the merged result instead of the selection, in a pool no "
                             "wider than the run's slot")


def run(root: Path, args, config: dict):
    given, full = list(args.tickets), bool(getattr(args, "full", False))
    try:
        if getattr(args, "select", False):
            return select(Path(root), given, args.onto, full)
        if getattr(args, "dry_run", False):
            return dry_run(Path(root), given, args.onto, args.timeout, getattr(args, "out", None), full)
        return land(Path(root), given, args.onto, args.timeout, full=full)
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


def _hold(root: Path) -> None:
    """``PROJECT_PAUSED`` while ``gov pause``'s freeze flag is frozen at the root or at the main checkout of the
    repository the root belongs to (as the launcher reads it; CAP-05, audit 7 C-1)."""
    from gov.launch import record
    from gov.util.freeze import FREEZE_FLAG, freeze_state

    places = [root]
    try:
        main = record.main_checkout(root, "the freeze flag gov pause sets")
        places += [main] if main != root else []
    except GovError:
        pass
    for place in places:
        if freeze_state(str(place)) == "frozen":
            _refuse("PROJECT_PAUSED", f"the project is paused (gov pause set {place / FREEZE_FLAG}): nothing lands "
                    "until the owner lifts it with gov pause --off", {"flag": str(place / FREEZE_FLAG)})


def _before_merge(root: Path, base: str, tip: str) -> str | None:
    """For a ``tip`` already on ``base``: the integration head before the merge that brought it (the first parent
    of the oldest first-parent commit of ``base`` that holds ``tip``); None where no such head can be told (the
    tip is the head, or it came by a fast-forward: the branch's own commits cannot be told from the base's)."""
    line = _git(root, "rev-list", "--first-parent", f"{tip}..{base}").split()
    holds = set(_git(root, "rev-list", "--ancestry-path", f"{tip}..{base}").split())
    brought = next((commit for commit in reversed(line) if commit in holds), None)
    before = _commit_of(root, f"{brought}^1") if brought else None
    if not before or _git(root, "merge-base", "--is-ancestor", tip, before, ok=True) is not None:
        return None
    return before


def _candidate(root: Path, base: str, given: str, settings: dict) -> dict:
    ticket, sep, branch = given.partition("=")
    front = _front_at(root, base, ticket) if _TICKET.fullmatch(ticket) else None
    if not isinstance(front, dict):
        _refuse("TICKET_UNKNOWN", f"{ticket} is not a ticket file .tickets/{ticket}.md at the integration head",
                {"ticket": ticket})
    closed = str(front.get("status")) == "closed"

    def refuse(code: str, message: str, details: dict, exit_code: int = 1):
        """A closed ticket's branch that cannot be told a fix is refused as a closed ticket's (W2-201 X6)."""
        if closed:
            _refuse("TICKET_CLOSED", f"{ticket} is closed at the integration head (a fix lands from a branch with a "
                    f"commit carrying Task: {ticket} and Fix: <line>)", {"ticket": ticket})
        _refuse(code, message, details, exit_code)

    wbs = str(front.get("wbs_id") or front.get("external-ref") or ticket)
    if not sep:
        form = settings.get("work_branch")
        if not isinstance(form, str) or not form.strip():
            refuse("BRANCH_UNKNOWN", f"{ticket}: no branch given and {SETTINGS_REL} names no work_branch form",
                   {"ticket": ticket})
        branch = form.replace("{wbs}", wbs).replace("{ticket}", ticket)
    tip = _commit_of(root, f"refs/heads/{branch}") or _commit_of(root, branch) if branch else None
    if not tip:
        refuse("BRANCH_UNKNOWN", f"{ticket}: its work branch {branch!r} names no commit",
               {"ticket": ticket, "branch": branch})
    since, merged = base, _git(root, "merge-base", "--is-ancestor", tip, base, ok=True) is not None
    if merged:
        since = _before_merge(root, base, tip)
        if since is None:
            refuse("CANDIDATE_NOT_ISOLATED", f"{ticket}: its work branch {branch} is already merged and the head "
                   "before its merge cannot be told (a fast-forward, or the branch is the head itself), so its "
                   "change cannot be checked; nothing lands", {"ticket": ticket, "branch": branch}, EXIT_RED)
    fix = None
    if closed:  # W2-201 X6: a fix landing, or refused as today
        from gov.queue import checks
        try:
            fix = checks.fix_line(root, since, tip, ticket)
        except RuntimeError:  # commits that cannot be read are no fix: fails closed
            fix = None
        if fix is None:
            refuse("TICKET_CLOSED", "", {})
    tree = _checked_out(root, branch)
    if tree is not None:
        _refuse_dirty(tree, branch, ticket)
    at_tip = _front_at(root, tip, ticket)
    return {"ticket": ticket, "branch": branch, "tip": tip, "front": front, "merged": merged, "since": since,
            "at_tip": at_tip if isinstance(at_tip, dict) else front, "folder": None, "record": None, "fix": fix}


def _refuse_dirty(tree: Path, branch: str, ticket: str | None = None) -> None:
    """``QUEUE_WORKTREE_DIRTY`` (W2-115b fix, audit N-01) before any merge: the worktree ``tree`` that holds
    ``branch`` has uncommitted or untracked work the branch's tip does not contain, which the landing would leave
    behind. The message names the worktree and each dirty file; the candidate is refused as a ``BRANCH_UNKNOWN`` is."""
    from gov.queue import checks

    files = checks.dirty_files(tree)
    if files:
        who = f"{ticket}: " if ticket else ""
        _refuse("QUEUE_WORKTREE_DIRTY", f"{who}the worktree {tree} holds {branch} with uncommitted work the landing "
                f"would leave behind ({len(files)} file{'s' if len(files) != 1 else ''}): {', '.join(files)}; "
                "commit or discard it, then queue the entry again; nothing lands",
                {"ticket": ticket, "branch": branch, "worktree": str(tree), "files": files})


def _on_record(front: dict) -> bool:
    """A ticket of a class judged on a record (as the ticket's file at the integration head names its class)."""
    from gov.close import gates

    return gates.ticket_class(front) in (*gates.EVIDENCE_CLASSES, gates.SPECIFICATION_CLASS)


def _acceptance(front: dict) -> str | None:
    tests = front.get("acceptance_tests")
    path = tests.get("path") if isinstance(tests, dict) else None
    return path if isinstance(path, str) and path.strip("/") else None


def _changed(root: Path, base: str, tip: str) -> list[str]:
    names = _git(root, "diff", "-z", "--no-renames", "--name-only", f"{base}...{tip}")
    return sorted(set(filter(None, names.split("\0"))))


def _checks(root: Path, base: str, cand: dict, result: dict) -> bool:
    """G-1, the path notice and the acceptance folder of a candidate; False where a check refuses it."""
    from gov.queue import checks

    ticket, tip, base = cand["ticket"], cand["tip"], cand["since"]
    try:  # W2-201 X4: a new ticket that is not a feature is named, never refused (DEC-1219 (5))
        for notice in checks.ticket_notices(root, base, tip):
            result["ticket_notices"].append({"ticket": ticket, **notice})
            print(notice["notice"], file=sys.stderr)
    except (RuntimeError, ValueError) as e:  # a notice only: the landing goes on
        print(f"gov queue: {ticket}: the ticket files its branch adds cannot be read: {' '.join(str(e).split())}",
              file=sys.stderr)
    places = list(dict.fromkeys(p for p in (ACCEPTANCE, _acceptance(cand["front"]), _acceptance(cand["at_tip"])) if p))
    allowed = [p for p in cand["at_tip"].get("allowed_paths") or [] if isinstance(p, str)]
    try:
        notices = checks.path_notices(root, base, tip, allowed,
                                      checks.record_places(ticket, _acceptance(cand["at_tip"])))
        result["path_notices"] += [{"ticket": ticket, **n} for n in notices]
        bad = checks.test_authors(root, base, tip, places)
        reason = "; ".join(f"{b['commit'][:12]} (Role: {', '.join(b['roles']) or 'none'}) {b['subject']}"
                           for b in bad)
    except RuntimeError as e:  # fails closed: commits that cannot be read are not landed
        bad, reason = [], f"the branch's commits cannot be read: {e}"
    if bad or reason:
        result["refused"].append({"ticket": ticket, "code": "TEST_AUTHOR_REFUSED", "commits": [b["commit"] for b in bad],
                                  "reason": f"acceptance tests changed without the test designer's or the owner's "
                                            f"role: {reason}"})
        return False
    folder = _acceptance(cand["at_tip"]) or _acceptance(cand["front"])
    try:
        why = checks.acceptance_refusal(root, [tip, base], folder)
    except RuntimeError as e:  # fails closed: a folder that cannot be read holds no test
        why = checks.NO_ACCEPTANCE_TESTS, f"its acceptance folder cannot be read: {e}"
    if why and not (why[0] == checks.NO_ACCEPTANCE_TESTS and _on_record(cand["front"])):
        result["refused"].append({"ticket": ticket, "code": why[0], "reason": why[1]})
        return False
    cand["folder"] = folder if why is None else None
    return True


def _judged_on_record(clone: Path, base: str, cand: dict, result: dict) -> bool:
    """The record of a ticket of a class judged on one, by the close's own gate (``check_specification``,
    ``check_evidence``) in the clone at the base with the branch merged; False where the gate refuses it."""
    from gov.close import attribution, batch, gates
    from gov.close.command import _Finding
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    ticket = cand["ticket"]
    try:
        if cand["merged"]:
            attribution.checkout(clone, base)
        elif batch._build(clone, base, [{"name": ticket, "commit": cand["tip"]}]) is None:
            raise GovError("CANDIDATE_NOT_ISOLATED", "its branch does not merge onto the integration head")
        if gates.ticket_class(cand["front"]) == gates.SPECIFICATION_CLASS:
            gates.check_specification(clone, ticket)
            cand["record"] = [gates.SPECIFICATION_CLASS]
        else:
            cand["record"] = gates.check_evidence(clone, ticket, frontmatter(clone / TICKETS_REL / f"{ticket}.md")
                                                  or cand["front"])
    except (GovError, _Finding) as refused:
        result["refused"].append({"ticket": ticket, "code": refused.code, "reason": refused.message})
        return False
    return True


def _run_on_head(clone: Path, cand: dict, base: str, chosen: dict, folder: Path, timeout: float, also,
                 workers: int = 1) -> dict:
    """The run of a branch already merged, on the integration head itself: ``batch.isolate``'s result keys. A red
    is run again alone (green alone: flaky), then alone at the head before the branch's merge: red there with the
    same failure type it is a known base red, else it is the ticket's, which is not closed."""
    from gov.close import attribution
    from gov.close.command import _phases

    ticket, options = cand["ticket"], chosen["pytest_options"]
    done = {"reds": [], "flaky": [], "culprits": [], "base_reds": [], "explains": {}, "landed": [],
            "land_commit": None, "runs": [], "folder": str(folder)}
    attribution.checkout(clone, base)
    phases = _phases(clone, chosen, folder, timeout, workers)
    done["runs"] = phases["runs"]
    if not phases["complete"]:
        _refuse("RUN_INCOMPLETE", f"the run on the head did not complete: {'; '.join(phases['incomplete'])}; "
                "nothing lands", done, EXIT_RED)
    more = also(base, [ticket])
    done["runs"] = phases["runs"] + more["runs"]
    kinds = {}
    for test in dict.fromkeys(f["test"] for f in phases["failing"]):
        alone = attribution.run_alone(clone, test, options, folder / "alone", timeout, "head")
        if alone is None:
            done["flaky"].append(test)
        else:
            kinds[test] = alone
    named = []  # its own acceptance run failed without naming a test: the ticket's, with no run before the merge
    for red in more["failing"]:
        if red["test"] not in kinds and red.get("culprit") == ticket:
            named.append(red["test"])
        kinds.setdefault(red["test"], red["failure_type"])
    done["reds"] = list(kinds)
    done["explains"] = {test: [ticket] for test in named}
    if len(kinds) > len(named):
        attribution.checkout(clone, cand["since"])
        for test, kind in kinds.items():
            if test in named:
                continue
            there = attribution.run_alone(clone, test, options, folder / "alone", timeout, "before")
            if there == kind and kind not in attribution.NEVER_MATCH:
                done["base_reds"].append({"test": test, "failure_type": kind, "base": cand["since"]})
            else:
                done["explains"][test] = [ticket]
        attribution.checkout(clone, base)
    if done["explains"]:
        done["culprits"] = [ticket]
    else:
        done.update(landed=[ticket], land_commit=base)
    return done


def _identity(root: Path) -> list[str]:
    """The committer of the close commits: the project's own git identity, else the batch's."""
    name = (_git(root, "config", "user.name", ok=True) or "").strip()
    email = (_git(root, "config", "user.email", ok=True) or "").strip()
    return ["-c", f"user.name={name or 'gov'}", "-c", f"user.email={email or 'gov@localhost'}"]


def _close_all(root: Path, clone: Path, cands: list[dict], record: dict, result: dict) -> str:
    """One close commit per landed candidate on the tested merge, in the clone; the last one. A fix landing's
    commit appends the fix to its ticket's close record and closes nothing (W2-201 X6)."""
    from gov.close import attribution, command as close
    from gov.queue import fix

    attribution.checkout(clone, result["tested"])
    who, role = _identity(root), os.environ.get("GOV_ROLE") or DEFAULT_ROLE
    for cand in cands:
        ticket = cand["ticket"]
        if cand.get("fix"):  # W2-201 X6: no second close: tk close and the first close's record are not reached
            close_rel = fix.append(clone, ticket, cand["fix"], cand["branch"], cand["tip"], result["tested"])
            _git(clone, "add", "-A", "--", close_rel)
            _git(clone, *who, "commit", "-q", "--no-verify", "--no-gpg-sign", "-m",
                 f"fix: {ticket} (gov queue landed at {result['tested'][:12]})\n\nTask: {ticket}\nRole: {role}\n")
            result["closes"].append({"ticket": ticket, "close_record": close_rel,
                                     "commit": _git(clone, "rev-parse", "HEAD").strip(), "fix": True,
                                     "fix_line": cand["fix"]})
            continue
        own = {**record, "branch": {"name": cand["branch"], "tip": cand["tip"]},
               "acceptance": cand["acceptance"],
               "path_notices": [n for n in result["path_notices"] if n["ticket"] == ticket],
               "ticket_notices": [n for n in result["ticket_notices"] if n["ticket"] == ticket]}
        close_rel, _ = close._record_and_close(clone, ticket, own, _changed(root, cand["since"], cand["tip"]))
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


def _start(root: Path, given: list[str], onto: str | None) -> tuple[str, str, list[dict], dict | None]:
    """The settings and the candidates (step 1): ``(integration branch, base, candidates, the one already
    merged)``; a refusal as a whole where one cannot be read."""
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
    alone = next((c for c in cands if c["merged"]), None)
    if alone and len(cands) > 1:  # no merged result can be built without it: it is not one of a batch
        _refuse("CANDIDATE_NOT_ISOLATED", f"{alone['ticket']}: its work branch {alone['branch']} is already merged, "
                f"so it is landed alone (gov queue {alone['ticket']}), apart from branches still to merge; nothing "
                "lands", {"ticket": alone["ticket"], "branch": alone["branch"]}, EXIT_RED)
    return onto, base, cands, alone


def _merged(clone: Path, base: str, left: list[dict], alone: dict | None) -> str:
    """The tested merge, checked out in the clone: the candidates merged onto the base (the base itself for a
    branch already merged)."""
    from gov.close import attribution, batch

    if alone:
        attribution.checkout(clone, base)
        return base
    merged = batch._build(clone, base, [{"name": c["ticket"], "commit": c["tip"]} for c in left])
    if merged is None:
        _refuse("CANDIDATE_NOT_ISOLATED", "the candidates do not merge together onto the integration head; "
                "nothing lands", {"candidates": [c["ticket"] for c in left]}, EXIT_RED)
    return merged


def _union(root: Path, clone: Path, left: list[dict], said: str = "; nothing lands") -> tuple[list[str], list[str], list[str]]:
    """The union of the candidates' ``select.scoped`` selections in the clone at the tested merge, each branch's
    changed paths counted in its change: ``(suites, pytest options, unplaced_base)``; ``SELECTION_REFUSED`` for a
    path the branch wrote that the test map does not map (the base's own, ``unplaced_base``, are only listed)."""
    from gov.close import select

    suites, options, unplaced = [], None, []
    for cand in left:
        try:
            chosen = select.scoped(clone, cand["ticket"], change=_changed(root, cand["since"], cand["tip"]))
        except select.SelectionRefused as refused:
            _refuse(select.SELECTION_REFUSED, f"{cand['ticket']}: {refused.reason}{said}",
                    {"candidate": cand["ticket"]}, EXIT_RED)
        suites += chosen["suites"]
        unplaced += chosen["unplaced_base"]
        options = chosen["pytest_options"]
    return sorted(dict.fromkeys(suites)), options or [], sorted(dict.fromkeys(unplaced))


def select(root: Path, given: list[str], onto: str | None = None, full: bool = False) -> int:
    """``gov queue <T>... --select`` (A6 S2): the selection the run would make, printed as one JSON object; 0.
    Nothing is run, moved or recorded: the warm clone, where the merged result is read, is left at the base. A
    selection refused is said on stderr: 2. Any other refusal is the landing's own (a ``GovError``)."""
    from gov.close import attribution
    from gov.close.select import SELECTION_REFUSED
    from gov.queue import dry, full as whole

    root = Path(root).resolve()
    onto, base, cands, alone = _start(root, given, onto)
    try:
        clone = root / attribution.prepare(root, base)["path"]
    except attribution.CloneError as e:
        _refuse("CLOSE_CLONE_FAILED", f"the queue's clone cannot be made: {e}", {"base": base})
    try:
        _merged(clone, base, cands, alone)
        if full:
            chosen = whole.selection(clone, [f for f in (_acceptance(c["at_tip"]) or _acceptance(c["front"])
                                                         for c in cands) if f])
            suites, options, unplaced = chosen["suites"], chosen["pytest_options"], None
        else:
            suites, options, unplaced = _union(root, clone, cands, "")
    except GovError as refused:
        if refused.code != SELECTION_REFUSED:
            raise
        print(f"{SELECTION_REFUSED}: {refused.message}", file=sys.stderr)
        return EXIT_SELECT_REFUSED
    finally:
        _back_to(clone, base)
    print(json.dumps(dry.selection_object([c["ticket"] for c in cands], suites, options, unplaced)))
    return 0


def _back_to(clone: Path, base: str) -> None:
    """The warm clone left at the base, where it can be."""
    from gov.close import attribution

    try:
        attribution.checkout(clone, base)
    except attribution.CloneError:
        pass


def dry_run(root: Path, given: list[str], onto: str | None = None, timeout: float = DEFAULT_TIMEOUT,
            out: str | None = None, full: bool = False) -> tuple[dict, int]:
    """``gov queue <T>... --dry-run [--out <dir>]`` (A6 S1): the landing's answer and exit code with nothing
    landed, and the out folder's files; ``verify.exit`` is written last, also where the dry run is refused as a
    whole (its exit code is then the refusal's)."""
    from gov.queue import dry

    root = Path(root).resolve()
    files = dry.Out(dry.out_dir(root, given, out))
    said = f"queue --dry-run {' '.join(g.partition('=')[0] for g in given)}"
    try:
        result, code = land(root, given, onto, timeout, full=full, dry=files)
    except GovError as error:
        code = error.exit_code if error.exit_code in EXIT_CODES else 1
        files.finish(f"{said}: exit {code}: {error.code}: {error.message}", code)
        raise
    except BaseException as error:  # the dry run itself failed: its exit file still says so, gov wait returns
        files.finish(f"{said}: exit 1: {type(error).__name__}", 1)
        raise
    runs = "; ".join(f"{r['name']} {r['passed']} passed, {r['failed']} failed, {r['errors']} errors, "
                     f"{r['skipped']} skipped" for r in result["runs"])
    told = [f"would land {', '.join(result['landed'])}"] if result["landed"] else ["nothing would land"]
    told += [f"culprits {', '.join(result['culprits'])}"] if result["culprits"] else []
    told += [f"refused {', '.join(r['ticket'] + ' (' + r['code'] + ')' for r in result['refused'])}"] \
        if result["refused"] else []
    files.finish(f"{said}: exit {code}: {'; '.join(told)}" + (f"; {runs}" if runs else ""), code)
    return result, code


def land(root: Path, given: list[str], onto: str | None = None,
         timeout: float = DEFAULT_TIMEOUT, *, full: bool = False, dry=None) -> tuple[dict, int]:
    """The landing: ``(result, exit code)``, or a ``GovError`` where nothing landed. ``full``: the run is the
    whole ``tests/`` of the merged result (``gov.queue.full``). ``dry`` (the out folder of a dry run,
    ``gov.queue.dry.Out``): everything but the land; ``landed`` names the tickets that would land."""
    from gov.close import attribution, batch
    from gov.queue import acceptance, after, checks, dry as _dry, full as whole

    start = time.monotonic()
    root = Path(root).resolve()
    _hold(root)
    onto, base, cands, alone = _start(root, given, onto)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    seconds = dict.fromkeys(STEPS, 0.0)
    result = {"onto": onto, "base": base, "candidates": [c["ticket"] for c in cands], "landed": [], "culprits": [],
              "refused": [], "reds": [], "base_reds": [], "flaky": [], "tested": None, "head": None, "closes": [],
              "selection": {"suites": [], "pytest_options": []}, "runs": [], "acceptance": [], "path_notices": [],
              "ticket_notices": [], "seconds": seconds, "record": f"{QUEUE_DIR}/{stamp}/queue.json"}

    def finish(code: int, error: GovError | None = None):
        seconds["total"] = round(time.monotonic() - start, 3)
        _write(root, result, error)
        if error is not None:
            error.details.update(record=result["record"], seconds=seconds)
            raise error
        return result, code

    def timed(step: str, began: float) -> None:
        seconds[step] = round(time.monotonic() - began, 3)

    accepted: dict[str, dict] = {}

    def acceptance_runs(commit: str, names: list[str]) -> dict:
        """Each named ticket's acceptance folder, run in the clone as it stands at ``commit``."""
        began, out = time.monotonic(), {"runs": [], "failing": []}
        for cand in cands:
            if cand["ticket"] in names and cand["folder"]:
                junit = root / QUEUE_DIR / stamp / f"acceptance-{cand['ticket']}-{commit[:12]}.xml"
                done = accepted[cand["ticket"]] = acceptance.run(clone, cand["ticket"], cand["folder"], timeout, junit)
                out["runs"].append(done["run"])
                out["failing"] += done["failing"]
        seconds["acceptance"] = round(seconds["acceptance"] + time.monotonic() - began, 3)
        return out

    clone, limit = None, None
    kept = _commit_of(root, batch.LAND_REF) if dry is not None else None  # the root's ref the batch's search moves

    def run_files(done: dict) -> None:
        """A dry run's run files: those of the run on the merged result."""
        if dry is not None and done.get("folder"):
            made = Path(done["folder"])
            dry.runs(made if alone else made / "batch")

    try:
        left = [c for c in cands if _checks(root, base, c, result)]
        if not left:
            return finish(EXIT_RED)
        began = time.monotonic()
        try:
            clone = root / attribution.prepare(root, base)["path"]
        except attribution.CloneError as e:
            _refuse("CLOSE_CLONE_FAILED", f"the queue's clone cannot be made: {e}", {"base": base})
        left = [c for c in left if not _on_record(c["front"]) or _judged_on_record(clone, base, c, result)]
        if not left:
            attribution.checkout(clone, base)
            return finish(EXIT_RED)
        _merged(clone, base, left, alone)
        timed("merge", began)
        began = time.monotonic()
        own = [c["folder"] for c in left if c["folder"]]  # run by the runner of gov accept: no test runs twice
        if full:  # the asked-for widening: the whole tests/, no selection computed, in a pool inside the slot
            limit = whole.cap(root)
            result["selection"] = whole.selection(clone, own)
            result["full"] = {"runs": [], **limit}
            union, unplaced = result["selection"]["suites"], None  # no selection is computed: no unplaced_base
        else:
            union, options, unplaced = _union(root, clone, left)
            result["selection"] = {"suites": [s for s in union if not checks._under(s, own)],
                                   "pytest_options": options}
        if dry is not None:
            dry.selection(_dry.selection_object([c["ticket"] for c in left], union,
                                                result["selection"]["pytest_options"], unplaced))
        timed("selection", began)
        began, before = time.monotonic(), seconds["acceptance"]
        workers = limit["workers"] if limit else 1
        try:
            with whole.capped(workers) if limit else contextlib.nullcontext():
                if alone:
                    done = _run_on_head(clone, alone, base, result["selection"], root / QUEUE_DIR / stamp / "head",
                                        timeout, acceptance_runs, workers)
                else:
                    done, _ = batch.isolate(root, base, [f"{c['ticket']}={c['tip']}" for c in left],
                                            targets=result["selection"]["suites"], onto=None, timeout=timeout,
                                            also=acceptance_runs, workers=workers,
                                            options=[f"--ignore={f.strip('/')}" for f in own] if full else None)
        except GovError as refused:
            run_files(refused.details)
            if full:
                result["full"]["runs"] = refused.details.get("runs") or []
            raise
        finally:
            seconds["run"] = round(time.monotonic() - began - (seconds["acceptance"] - before), 3)
            result["acceptance"] = [{k: a[k] for k in ("ticket", "folder", "outcome", "error_kind", "lines")}
                                    for a in accepted.values()]
        run_files(done)
        result.update({k: done[k] for k in ("reds", "flaky", "culprits")}, tested=done["land_commit"],
                      base_reds=done.get("base_reds") or [])
        result["runs"] = done.get("runs", []) + [{**r, "name": f"rest:{r['name']}"} for r in done.get("rest_runs", [])]
        if full:
            result["full"]["runs"] = result["runs"]
        landed = [c for c in left if c["ticket"] in done["landed"]]
        if result["tested"] is None:
            return finish(EXIT_RED)
        for cand in landed:  # never landed on an acceptance run that did not pass on the tested commit
            ran = accepted.get(cand["ticket"])
            if cand["folder"] and (ran is None or ran["outcome"] != "pass"):
                _refuse("ACCEPTANCE_NOT_GREEN", f"{cand['ticket']}: its acceptance run on the tested commit did not "
                        "pass; nothing lands", {"candidate": cand["ticket"]}, EXIT_RED)
            cand["acceptance"] = {"folder": cand["folder"], "lines": ran["lines"]} if cand["folder"] else \
                {"folder": None, "lines": [], "record": cand["record"]}
        code = EXIT_RED if len(landed) < len(cands) else 0
        if dry is not None:  # the answer the landing would give; nothing is closed and nothing moves
            result.update(landed=[c["ticket"] for c in landed], dry_run=True)
            # W2-201 X6: the entry a fix landing would get, with no commit and no record written
            result["closes"] = [{"ticket": c["ticket"], "close_record": None, "commit": None, "fix": True,
                                 "fix_line": c["fix"]} for c in landed if c.get("fix")]
            return finish(code)
        began = time.monotonic()
        explains = done.get("explains") or {}
        at_base = {r["test"]: r for r in result["base_reds"]}
        record = {"close": "queue", "commit": result["tested"], "selection": result["selection"],
                  "runs": result["runs"],
                  "reds": [{"test": t, "verdict": "flaky"} for t in result["flaky"]]
                  + [{**at_base[t], "verdict": "base"} if t in at_base else
                     {"test": t, "verdict": "culprit", "culprits": explains.get(t, [])} for t in result["reds"]],
                  "base_reds": list(at_base), "culprits": result["culprits"], "base": base, "onto": onto,
                  "queue": result["record"]}
        last = _close_all(root, clone, landed, record, result)
        _move(root, clone, onto, base, last, result)
        timed("close", began)
        result.update(head=last, landed=[c["ticket"] for c in landed])
        began = time.monotonic()  # the after-step: notices only, the landing stands whatever they say
        try:  # where the branch is checked out, in its tree; else the rebuild from the root, the pass in the clone
            tree = _checked_out(root, onto)
            result["after"] = after.run(tree or root, onto, base, tree or clone)
        except Exception as e:  # noqa: BLE001 - never refuses
            result["after"] = {"ok": False, "reason": f"{type(e).__name__}: {e}"[:600]}
        result["after"]["seconds"] = round(time.monotonic() - began, 3)
        return finish(code)
    except RuntimeError as e:  # a git step that failed: nothing has moved
        return finish(1, GovError("GIT_FAILED", f"{e}; nothing lands", {"reds": result["reds"]}))
    except GovError as error:
        result["reds"] = error.details.get("reds", result["reds"])
        error.details["reds"] = result["reds"]
        return finish(EXIT_RED, error)
    finally:
        if dry is not None:  # the clone at the base; the root without the ref the batch's search fetched into it
            if clone is not None:
                _back_to(clone, base)
            _git(root, "update-ref", *([batch.LAND_REF, kept] if kept else ["-d", batch.LAND_REF]), ok=True)
