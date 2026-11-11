"""Adoption safety on a real repository (W2-23): what ``gov adopt --lite`` does so that a programme loses nothing.

- **Set-up (A0):** a project without ``.gitleaks.toml`` gets the template's, and a ``.gitignore`` that does not ignore
  ``.gov-runtime/`` gets the line, both in A0's record commit; an existing ``.gitleaks.toml`` is never touched.
- **Held targets (A3, A6):** a move to a target no namespace of the path map holds is refused, naming each target,
  before anything is recorded or moved (``ADOPT_TARGET_UNHELD``).
- **A6 runs that resume:** each run has its own id and its own rollback refs
  (``refs/gov/adoption/rollback/<run-id>/batch-<n>``). Before a batch's first move the run writes its run state,
  ``<git dir>/gov-adoption/a6-run.json``: the batches done and the batch in progress with its rollback point and its
  moves. A failed batch is rolled back and the A6 record is committed with ``status: failed``; the next A6 run
  resumes at that batch. A killed batch (its moves staged, no commit) is found by the next stage from the run
  state: when what is staged is the batch's own moves and nothing else, it is unstaged to its rollback point and A6
  continues there; anything else is refused by the clean-tree check, naming the paths, and nothing is reset.
- **The A8 citation forms:** what the dependency proof reads a record or a rule for (``citations``).
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from gov.adopt import project
from gov.adopt.project import MOVING, git, refuse, resolve

REFS = "refs/gov/adoption"
GITLEAKS = ".gitleaks.toml"
IGNORED = ".gov-runtime/"
TEMPLATE_GITLEAKS = Path(__file__).resolve().parents[3] / "template" / GITLEAKS
STATE = "gov-adoption/a6-run.json"  # under the repository's git dir: never in the tree, never staged


# --------------------------------------------------------------------------
# S5: set-up at A0
# --------------------------------------------------------------------------

def setup(root: Path) -> dict[str, str]:
    """The files A0 writes with its record: path -> text. Empty when the project is already set up."""
    files = {}
    if not os.path.lexists(root / GITLEAKS):
        try:
            files[GITLEAKS] = TEMPLATE_GITLEAKS.read_text(encoding="utf-8")
        except OSError as exc:
            raise refuse("TEMPLATE_MISSING", f"the project has no {GITLEAKS} and the template's ({TEMPLATE_GITLEAKS}) "
                         f"cannot be read: {exc}; nothing is set up") from None
    if project._run(root, ("check-ignore", "-q", IGNORED + "store.db"), (0, 1))[0] == 1:
        try:
            text = (root / ".gitignore").read_text(encoding="utf-8") if (root / ".gitignore").is_file() else ""
        except (OSError, UnicodeDecodeError) as exc:
            raise refuse("GITIGNORE_UNREADABLE", f".gitignore cannot be read ({exc}): {IGNORED} is not added") from None
        files[".gitignore"] = text + ("" if not text or text.endswith("\n") else "\n") + IGNORED + "\n"
    return files


# --------------------------------------------------------------------------
# S7: every target held by a namespace
# --------------------------------------------------------------------------

def refuse_unheld(config: dict, entries) -> None:
    """Refuse ``ADOPT_TARGET_UNHELD`` when a target of a move in ``entries`` lies in no namespace of the path map."""
    targets = []
    for entry in entries:
        if entry.get("action") in MOVING:
            goals = entry.get("targets") if entry.get("action") == "SPLIT" else entry.get("target")
            targets += [goal for goal in (goals if isinstance(goals, list) else [goals]) if isinstance(goal, str)]
    unheld = [goal for goal, space in project.classify(config, targets).items() if space is None]
    if unheld:
        raise refuse("TARGET_UNHELD", "no namespace of the path map holds the target " + ", ".join(unheld) + ": a move "
                     "there would leave an unknown artefact behind; nothing is recorded or moved", targets=unheld)


# --------------------------------------------------------------------------
# S4: A6 runs, their state, and the resume
# --------------------------------------------------------------------------

def _state_path(root: Path) -> Path:
    return root / git(root, "rev-parse", "--git-path", STATE).strip()


def load(root: Path) -> dict | None:
    path = _state_path(root)
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (OSError, ValueError) as exc:
        raise refuse("RUN_STATE_UNREADABLE", f"the A6 run state {path} cannot be read ({exc}): an interrupted batch "
                     "cannot be established; nothing is moved") from None


@dataclass
class State:
    root: Path
    path_map_hash: str
    run_id: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
                        + uuid.uuid4().hex[:6])
    batches: list = field(default_factory=list)  # the batches done, as the A6 record lists them
    resumed: str | None = None                    # what this run resumes from

    @property
    def done(self) -> set:
        return {item["batch"] for item in self.batches}

    def write(self, progress: dict | None) -> None:
        path = _state_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps({"run_id": self.run_id, "path_map_hash": self.path_map_hash, "batches": self.batches,
                           "in_progress": progress}, indent=1)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)

    def remove(self) -> None:
        _state_path(self.root).unlink(missing_ok=True)


def _done_entry(batch: dict, point: str, commit: str) -> dict:
    """A batch done, as the A6 record lists it (the same shape ``stages._batch`` returns)."""
    done = [{**{key: item[key] for key in ("path", "action", "target") if key in item},
             **({} if "target" in item else {"disposition": "deleted from the active tree as the path map says",
                                             "reachable_at": point})} for item in batch["artefacts"]]
    return {"batch": batch["batch"], "status": "done", "rollback_point": point, "commit": commit, "artefacts": done}


def resume(run) -> State:
    """The state this A6 run starts from: a fresh run, or the batches an earlier run did (failed or killed)."""
    root, hashed, rel = run.root, run.hashes["A3"], project.record_path("A6")
    state, saved = State(root, hashed), load(root)
    record = project.read_record(root, run.tracked, rel)[0] if rel in run.tracked else {}
    if saved is not None and record.get("status") == "failed" and record.get("run_id") == saved.get("run_id"):
        saved = None  # killed after the failed record's commit: the record says it all
    if saved is not None and saved.get("path_map_hash") == hashed:
        state.batches, state.resumed = list(saved.get("batches") or []), f"the interrupted run {saved.get('run_id')}"
        progress = saved.get("in_progress")
        if progress:
            head = resolve(root, "HEAD")
            if head != progress["start"]:
                parent = resolve(root, "HEAD^")
                subject = git(root, "log", "-1", "--format=%s").strip()
                if parent != progress["start"] or subject != f"gov adopt --lite A6: batch {progress['batch']}":
                    raise refuse("RUN_STATE_UNEXPECTED", f"the A6 run state records batch {progress['batch']} in "
                                 f"progress from {progress['start']}, and HEAD is {head}, which is neither that commit "
                                 f"nor the batch's own commit on it: nothing is moved or reset ({_state_path(root)})",
                                 batch=progress["batch"])
                plan = next(item for item in run.records["A4"]["batches"] if item["batch"] == progress["batch"])
                state.batches.append(_done_entry(plan, progress["rollback_point"], head))  # killed after its commit
    elif record.get("status") == "failed" and record.get("path_map_hash") == hashed:
        state.batches = [item for item in record.get("batches") or [] if item.get("status") == "done"]
        state.resumed = f"the failed run {record.get('run_id')} (batch {record.get('failed_batch')})"
    for item in state.batches:
        if project._run(root, ("merge-base", "--is-ancestor", str(item.get("commit")), "HEAD"), (0, 1, 128))[0]:
            raise refuse("RUN_STATE_UNEXPECTED", f"batch {item['batch']} is recorded as done at {item.get('commit')}, "
                         "which is no ancestor of HEAD: run the stages again from A1", batch=item["batch"])
    return state


def migrate(run, plan: list, state: State, execute, data: dict) -> dict:
    """Run the batches of ``plan`` not yet done with ``execute`` (``stages._batch``), then commit the A6 record.

    The run state names the batch in progress before its first move. A failed batch is rolled back by ``execute``;
    the A6 record is then committed with ``status: failed`` and the refusal stays ``ADOPT_BATCH_FAILED``."""
    from gov.cli.errors import GovError

    head = {"run_id": state.run_id, **({"resumed_from": state.resumed} if state.resumed else {})}
    for batch in plan:
        number = batch["batch"]
        if number in state.done:
            continue
        point, start = f"{REFS}/rollback/{state.run_id}/batch-{number}", resolve(run.root, "HEAD")
        state.write({"batch": number, "rollback_point": point, "start": start,
                     "artefacts": [{key: item[key] for key in ("path", "blob", "action", "target") if key in item}
                                   for item in batch["artefacts"]]})
        try:
            state.batches.append(execute(run.root, {**batch, "rollback_point": point}, sorted(state.done)))
        except GovError as exc:
            if exc.code != "ADOPT_BATCH_FAILED":
                raise
            failed = {"batch": number, "status": "failed", "rollback_point": point, "start": start,
                      "reason": exc.message}
            run.finish({**{k: v for k, v in data.items() if k != "index_refresh"}, **head, "status": "failed",
                        "failed_batch": number,
                        "batches": [*state.batches, failed]})
            state.remove()
            raise refuse("BATCH_FAILED", f"{exc.message}; the A6 record ({project.record_path('A6')}) says "
                         f"status: failed, failed_batch: {number}; run `gov adopt --lite --stage A6` again to resume "
                         f"at batch {number}", **{**exc.details, "run_id": state.run_id, "failed_batch": number,
                                                  "record": project.record_path("A6")}) from None
        state.write(None)
    result = run.finish({**data, **head, "status": "done", "batches": state.batches})
    state.remove()
    return result


def recover(root: Path, paths: list[str]) -> bool:
    """Unstage a killed batch: True when ``paths`` (what is dirty) are the moves of the batch the run state names in
    progress and nothing else, with HEAD at its rollback point; the tree is then put back to that point."""
    saved = load(root)
    progress = (saved or {}).get("in_progress")
    if not progress or resolve(root, "HEAD") != progress.get("start"):
        return False
    at_start = project.tree(root)
    planned = {}  # path -> the blob the batch leaves there (None: removed)
    for item in progress["artefacts"]:
        planned[item["path"]] = None
        if "target" in item:
            planned[item["target"]] = item["blob"]
    staged, tokens = {}, git(root, "diff", "--cached", "--no-renames", "--no-abbrev", "--raw", "-z", "HEAD").split("\0")
    for meta, rel in zip(tokens[0::2], tokens[1::2]):  # ":<mode> <mode> <blob> <blob> <status>", then the path
        fields = meta.split()
        staged[rel] = None if fields[4] == "D" else fields[3]
    unstaged = git(root, "diff", "--name-only", "-z").split("\0")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
    if not staged or any(planned.get(rel, "absent") != blob for rel, blob in staged.items()) \
            or set(paths) - set(planned) or any(unstaged) or any(rel for rel in untracked if rel not in planned):
        return False
    if any(rel in at_start and planned[rel] is not None for rel in staged):
        return False
    git(root, "reset", "-q", "--hard", progress["start"])  # the batch's own moves, staged, and nothing else
    for rel in planned:
        for folder in PurePosixPath(rel).parents:
            if str(folder) != "." and (root / folder).is_dir() and not any((root / folder).iterdir()):
                (root / folder).rmdir()
    return True


def refuse_after_failed_a6(run) -> None:
    """A8 stands on an A6 that is done: a record that says ``status: failed`` holds the retirement back."""
    if run.records.get("A6", {}).get("status") == "failed":
        raise refuse("A6_NOT_DONE", f"{project.record_path('A6')} says status: failed (batch "
                     f"{run.records['A6'].get('failed_batch')}): run `gov adopt --lite --stage A6` again first")


# --------------------------------------------------------------------------
# S3: the citation forms of the A8 dependency proof
# --------------------------------------------------------------------------

_HEX = re.compile(r"%([0-9A-Fa-f]{2})")
_GLOB_TOKEN = re.compile(r"[^\s\"'`()<>{},;|]*[*?][^\s\"'`()<>{},;|]*")


def _normal(text: str, join: bool) -> tuple[str, list[int], list[int]]:
    """``text`` in lower case, URL-decoded, with backslashes as ``/`` (and, with ``join``, line breaks and the blanks
    around them removed); with the raw start and end of every character, so a match is printed as it was found."""
    out, starts, ends, i = [], [], [], 0
    while i < len(text):
        char, step = text[i], 1
        if char == "%" and _HEX.match(text, i):
            char, step = chr(int(text[i + 1:i + 3], 16)), 3
        if char == "\\":
            while i + step < len(text) and text[i + step] == "\\":
                step += 1
            char = "/"
        elif join and char.isspace():
            end = i
            while end < len(text) and text[end].isspace():
                end += 1
            if "\n" in text[i:end]:
                i = end
                continue
        for lower in char.lower():
            out.append(lower)
            starts.append(i)
            ends.append(i + step)
        i += step
    return "".join(out), starts, ends


def _glob(pattern: str) -> re.Pattern:
    body = "".join(".*" if part == "**" else "[^/]*" if part == "*" else "[^/]" if part == "?" else re.escape(part)
                   for part in re.split(r"(\*\*|\*|\?)", pattern))
    return re.compile(body.replace(".*/", "(?:.*/)?"))


def citations(text: str, paths: list[str], ids: list[str]) -> list[dict]:
    """Every citation of ``paths`` (the store) or ``ids`` (its records) in ``text``, each with its form and the text
    as found. The forms: the path or id with anything directly before it, backslashes, URL-encoding, another letter
    case, split across lines; the store's folder alone or a glob that holds the store; ``../`` and only the tail of
    the path. Nothing else is a citation here."""
    wanted = []  # (form, cited name, regex)
    for rel in paths:
        low, parts = rel.lower(), rel.lower().split("/")
        wanted.append(("path", rel, re.escape(low)))
        wanted += [("relative tail", rel, r"(?:\.\./)+" + re.escape("/".join(parts[k:])) + r"(?![\w.-])")
                   for k in range(1, len(parts))]
        folder = "/".join(parts[:-1])
        if folder:
            wanted.append(("folder", rel, re.escape(folder) + ("/?" if "/" in folder else "/") + r"(?![\w./*?\[-])"))
    wanted += [("id", ident, re.escape(ident.lower()) + r"(?![\w-])") for ident in ids]
    found, seen = [], set()
    for join in (True, False):  # joined first: a path split across lines is printed whole, not as its folder
        normal, starts, ends = _normal(text, join)
        hits = [(form, name, m.start(), m.end()) for form, name, rx in wanted for m in re.finditer(rx, normal)]
        for m in _GLOB_TOKEN.finditer(normal):
            token = m.group().lstrip("/").removeprefix("./")
            head = token.split("/", 1)[0]
            if "/" not in token or not head or any(c in head for c in "*?"):
                continue  # a glob with no literal folder first (``**/*``, ``*.md``) names no store
            rx = _glob(token)
            hits += [("glob", rel, m.start(), m.end()) for rel in paths
                     if rx.fullmatch(rel.lower()) or rx.fullmatch(rel.lower().rpartition("/")[0])]
        for form, name, start, end in hits:
            raw = text[starts[start]:ends[end - 1]]
            if (name, starts[start]) not in seen:
                seen.add((name, starts[start]))
                found.append({"cites": name, "form": form, "found": raw})
    return found
