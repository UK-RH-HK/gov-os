"""``gov decisions answer``: an owner's answer sheet becomes register entries, in one commit (W2-211 PG-4 to PG-6; the spec's
"``gov decisions answer <sheet>``").

The checks run in the spec's order and the first failure refuses the whole sheet before anything is written. A pick writes
one register entry (the form of DEC-1225 to DEC-1231), sets its package ACCEPTED with its answer filled, and the sheet is
stored; one commit holds exactly these paths. A card already answered by this batch with the same option is named and left
alone; a ``skip`` writes nothing. The owner decides any level, so ``answer`` never writes a record below its level.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gov.cli.errors import GovError
from gov.decisions import package, page, sheet
from gov.util.gitrun import git

REGISTER_DEFAULT = "docs/DECISION_REGISTER.md"
_DEC = re.compile(r"^###[ \t]+DEC-(\d+)[ \t]", re.MULTILINE)


class AnswerError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def _fold(text) -> str:
    return " ".join(str(text or "").split())


def _rel(root: Path, path: str) -> str:
    given = Path(path)
    if given.is_absolute():
        try:
            return given.resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            return given.as_posix()
    return given.as_posix().removeprefix("./")


def _manifest(root: Path, batches: str, batch: str) -> dict:
    path = page.manifest_path(root, batches, batch)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise AnswerError("ANSWER_BATCH", f"no manifest for batch {batch!r} in {batches}") from None
    cards = data.get("cards") if isinstance(data, dict) else None
    if not isinstance(cards, list) or not all(isinstance(c, dict) and isinstance(c.get("id"), str) for c in cards):
        raise AnswerError("ANSWER_BATCH", f"the manifest of {batch} is not a batch manifest")
    covered = [{k: v for k, v in c.items() if k != "content_hash"} for c in cards]
    if sheet.strip_prefix(str(data.get("hash", ""))) != sheet.batch_hash(batch, covered):
        raise AnswerError("ANSWER_BATCH", f"the manifest of {batch} does not hash to its stored hash (edited by hand)")
    return data


def _parse_when(text: str) -> datetime | None:
    try:
        when = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(tzinfo=timezone.utc)


def _status_dirty(root: Path, paths: list[str]) -> list[str]:
    out = git(root, "status", "--porcelain", "--untracked-files=all", "--", *paths)
    return [line[3:] for line in out.splitlines() if line.strip()]


def _answered_here(front: dict, batch: str) -> dict | None:
    answer = front.get("answer")
    if front.get("status") == "ACCEPTED" and isinstance(answer, dict) and answer.get("batch") == batch:
        return answer
    return None


def _entry(dec: int, pkg: dict, option: dict, letter: str, note: str | None, batch: str, answered: str,
           sheet_path: str, batches: str) -> str:
    front = pkg["front"]
    day = answered[:10]
    status = (f"- **Status:** ACCEPTED (owner, {day}, on the decisions page {batch}, answer {front['id']}; recorded by code "
              f"with `Role: orchestrator`, `Decided-by: owner (page {batch})`; standing)")
    for label, value in (("Under", front.get("under")), ("Changes", option.get("changes"))):
        words = value if isinstance(value, list) else ([value] if value else [])
        if words:
            status += f" · **{label}:** {', '.join(str(w) for w in words)}"
    decision = f"- **Decision:** ({letter}) {_fold(option['label'])}: {_fold(option['consequence'])}."
    if note:
        decision += (f" The owner's note, read with the option and carried out as written: \"{note}\".")
    basis = (f"- **Basis:** the owner's answer on the decisions page {batch} (sheet `{sheet_path}`, answered {day}); "
             f"what was found: {_fold(front.get('found'))}; the page `{batches}/{batch}.html`.")
    sources = ", ".join(str(s) for s in front.get("sources") or [])
    governing = f"- **Governing sources:** {sources}; {front['id']}."
    return "\n".join([f"### DEC-{dec} — {_fold(front.get('title'))}: {_fold(option['label'])}", status, decision, basis,
                      governing])


def _answered_text(text: str, letter: str, dec: str, batch: str, day: str) -> str:
    """The package file's text with ``status: ACCEPTED``, its ``answer:`` field and its Answer section filled."""
    close = text.find("\n---", 3)
    head, rest = text[:close], text[close:]
    head = re.sub(r"(?m)^status:[^\n]*$", "status: ACCEPTED", head, count=1)
    answer = json.dumps({"option": letter, "decision": dec, "batch": batch, "date": day}, ensure_ascii=False)
    head = head.rstrip("\n") + f"\nanswer: {answer}"
    chosen = f"- Option chosen: ({letter}), on the decisions page {batch}"
    record = f"- Decision record: {dec}, appended as ACCEPTED (owner, {day})"
    if re.search(r"(?m)^- Option chosen:", rest):
        rest = re.sub(r"(?m)^- Option chosen:[^\n]*$", lambda _m: chosen, rest, count=1)
        rest = re.sub(r"(?m)^- Decision record:[^\n]*$", lambda _m: record, rest, count=1)
    else:
        rest = rest.rstrip("\n") + f"\n\n## Answer\n\n{chosen}\n{record}\n"
    return head + rest


def answer(root: Path, text: str, *, batches: str = page.BATCHES_DEFAULT, register: str = REGISTER_DEFAULT,
           role: str | None = None, dry_run: bool = False, now: datetime | None = None) -> dict:
    """The sheet's effect: ``{lines, skipped, notes, still_open, recorded, entries, commit}``; ``AnswerError`` refuses."""
    root, now = Path(root), now or datetime.now(timezone.utc)
    if role != "orchestrator":
        raise AnswerError("ANSWER_ROLE", f"the caller's role is {role or 'none'}; only the orchestrator records an answer")
    try:
        parsed = sheet.parse_sheet(text)
    except sheet.SheetError as error:
        raise AnswerError("ANSWER_FORMAT", error.message) from None
    batch = parsed["batch"]
    batches, register = _rel(root, batches), _rel(root, register)
    manifest = _manifest(root, batches, batch)
    if sheet.strip_prefix(parsed["hash"]) != sheet.strip_prefix(str(manifest["hash"])):
        raise AnswerError("ANSWER_HASH", f"the hash is not that of batch {batch}")
    cards = {c["id"]: c for c in manifest["cards"]}
    lines = parsed["lines"]
    if [x["id"] for x in lines] != [c["id"] for c in manifest["cards"]]:
        unknown = [x["id"] for x in lines if x["id"] not in cards]
        raise AnswerError("ANSWER_UNKNOWN_ID", (f"{', '.join(unknown)} not in batch {batch}" if unknown else
                                                f"the lines are not the cards of batch {batch} in its order"))
    for x in lines:
        keys = [o.get("key") for o in cards[x["id"]].get("options") or [] if isinstance(o, dict)]
        if x["letter"] != "skip" and x["letter"] not in keys:
            raise AnswerError("ANSWER_OPTION", f"{x['id']} has no option {x['letter']} (it has {', '.join(keys)})")
    packages = package.load_all(root)
    picks = [x for x in lines if x["letter"] != "skip"]
    gone = page.withdrawn(packages)
    for x in picks:
        if x["id"] in gone:
            newer = gone[x["id"]]
            held = next((m.name.split(".")[0] for m in (root / batches).glob("*.manifest.json")
                         if f'"{newer}"' in m.read_text(encoding="utf-8", errors="replace")), "no batch yet")
            raise AnswerError("ANSWER_WITHDRAWN", f"{x['id']} was re-asked as {newer} (batch {held})")
    dirty = _status_dirty(root, [register, package.PACKAGES_DIR, batches])
    if dirty:
        raise AnswerError("ANSWER_DIRTY", f"uncommitted: {', '.join(dirty[:5])}")
    for x in picks:
        pkg = packages.get(x["id"])
        if pkg is None:
            raise AnswerError("ANSWER_STALE", f"{x['id']} is not in {package.PACKAGES_DIR}")
        if _answered_here(pkg["front"], batch):
            continue
        if pkg["front"].get("status") != "PROPOSED":
            raise AnswerError("ANSWER_STALE", f"{x['id']} is {pkg['front'].get('status')}, not PROPOSED")
        if package.content_hash(pkg["text"]) != cards[x["id"]].get("content_hash"):
            raise AnswerError("ANSWER_STALE", f"{x['id']} changed after batch {batch} was published")
    for x in picks:
        done = _answered_here(packages[x["id"]]["front"], batch)
        if done and done.get("option") != x["letter"]:
            raise AnswerError("ANSWER_CONFLICT", f"{x['id']} is already answered ({done.get('option')}) by this batch")
    when, created = _parse_when(parsed["answered"]), _parse_when(str(manifest.get("created", "")))
    if when is None:
        raise AnswerError("ANSWER_DATE", f"answered: {parsed['answered']!r} is not a date")
    if (created is not None and when.date() < created.date()) or when > now + timedelta(days=1):
        raise AnswerError("ANSWER_DATE", f"answered {parsed['answered']} is before the batch was made or in the future")
    reg_path = root / register
    try:
        reg_text = reg_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        raise AnswerError("REGISTER_UNREADABLE", f"{register} cannot be read") from None
    numbers = [int(n) for n in _DEC.findall(reg_text)]
    if not numbers:
        raise AnswerError("REGISTER_UNREADABLE", f"{register} holds no `### DEC-<n> — title` entries")

    out = {"lines": [], "skipped": [x["id"] for x in lines if x["letter"] == "skip"], "notes": [], "recorded": [],
           "entries": [], "commit": None}
    new, nxt = [], max(numbers) + 1
    for x in picks:
        done = _answered_here(packages[x["id"]]["front"], batch)
        if done:
            out["lines"].append(f"{x['id']} already recorded as {done.get('decision')}")
            continue
        new.append((x, nxt))
        nxt += 1
    for x, dec in new:
        out["lines"].append(f"{x['id']} -> DEC-{dec} ({x['letter']})")
        if x["note"]:
            out["notes"].append((x["id"], x["note"]))
    answered_now = {x["id"] for x, _d in new}
    out["still_open"] = [c["id"] for c in manifest["cards"]
                         if c["id"] not in answered_now and packages[c["id"]]["front"].get("status") == "PROPOSED"]
    if not new or dry_run:
        out["entries"] = [dec for _x, dec in new]
        return out

    h8 = hashlib.sha256(parsed["text"].encode("utf-8")).hexdigest()[:8]
    sheet_rel = f"{batches}/{batch}.sheet-{h8}.txt"
    day, entries, files = parsed["answered"][:10], [], {}
    titles = []
    for x, dec in new:
        pkg = packages[x["id"]]
        option = next(o for o in cards[x["id"]]["options"] if o["key"] == x["letter"])
        source_option = next((o for o in pkg["front"].get("options") or [] if isinstance(o, dict)
                              and o.get("key") == x["letter"]), option)
        entries.append(_entry(dec, pkg, source_option, x["letter"], x["note"], batch, parsed["answered"], sheet_rel, batches))
        files[pkg["path"]] = _answered_text(pkg["text"], x["letter"], f"DEC-{dec}", batch, day)
        titles.append(_fold(pkg["front"].get("title")))
    gap = "" if reg_text.endswith("\n") else "\n"
    files[reg_path] = reg_text + gap + "\n\n".join(entries) + "\n\n"
    files[root / sheet_rel] = parsed["text"]
    first, last = new[0][1], new[-1][1]
    span = f"DEC-{first}" if first == last else f"DEC-{first} to DEC-{last}"
    message = (f"{span} (page {batch}): {'; '.join(titles)}\n\nClass: C\nTask: decision-record\nRole: orchestrator\n"
               f"Decided-by: owner (page {batch})\n")
    originals = {p: (p.read_text(encoding="utf-8") if p.exists() else None) for p in files}
    rels = [p.relative_to(root).as_posix() for p in files]
    try:
        for path, content in files.items():
            tmp = path.with_name(path.name + ".tmp-answer")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(path)
        git(root, "add", "--", *rels)
        git(root, "commit", "-q", "-m", message, "--", *rels, pinned=False)
    except (GovError, OSError) as error:
        for path, content in originals.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(content, encoding="utf-8")
        git(root, "reset", "-q", "--", *rels, ok=(0, 1, 128))
        raise AnswerError("ANSWER_COMMIT", f"the commit failed and the files were put back: {error}") from None
    out["entries"] = [dec for _x, dec in new]
    out["commit"] = git(root, "rev-parse", "HEAD").strip()
    return out
