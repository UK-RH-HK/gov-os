"""``judge``: the judged reader run, the two graders, the verdict, ``misses.jsonl`` and ``FIGURES.json`` (Interface items 1, 2,
7, 8, 9, 10 and 11; S3, S5, S6, S8, F1, F2).

The run is the fresh 80's (``fresh80_reader.py``) generalised to the audit's set: each question's first bundle comes from the
counting attempt's kept outputs (``COUNTS``); the reader (pinned prompt, schema, cap 3) answers, searches again live through
``--gov`` or settles; a named grader judges the final answer and a second grader's grade is kept beside it; the citation is
checked by the measure's own matcher. A question's row ``reader/<id>.json`` is written whole, so a resumed run never asks it
again. Spend is a ledger line a call (S8) and the run stops at twice its projection before a new question starts (exit 2, to
the owner). A verdict stands: ``FIGURES.json`` present, or ``reader/`` or ``STOPPED`` present without ``--resume``, is exit 3.
Only ids, counts and digests are printed; the questions and answers go to ``reader/`` and ``misses.jsonl`` alone (F1).
"""

from __future__ import annotations

import fcntl
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.memaudit import declare, events, fault, figures, layout, ledger, matcher, prompts, runner
from gov.memaudit.claude import Caller
from gov.memaudit.common import UsageError, read_json, set_digest, toplevel, write_whole
from gov.memaudit.measure import write_text

WORKERS = 4
PER_QUESTION = 0.157  # the fresh 80's spend a question (FRESH-80-RESULT); the projection is this times n
READER, GRADER, CHECK = "claude-opus-5-5", "claude-opus-5-5", "claude-sonnet-5-5"
READER_BUDGET, GRADER_BUDGET = 1.5, 0.5


def projection_of(n: int, given) -> float:
    return float(given) if given is not None else round(PER_QUESTION * n, 4)


class _Judge:
    def __init__(self, p, repo, gov, caller, brake, emit):
        self.p, self.run, self.reader = p, p["run"], p["run"] / "reader"
        self.repo, self.gov, self.caller, self.brake, self.emit = repo, gov, caller, brake, emit
        self.lock, self.stopped = threading.Lock(), False

    # ---- a later search: a failure or a degraded answer is counted and gives an empty bundle

    def search(self, qid: str, words: str) -> tuple[dict, bool, str | None, str | None]:
        started = time.monotonic()
        with open(self.reader / "gov.err", "ab") as err:
            done = subprocess.run([self.gov, "retrieve", words, "--json"], stdout=subprocess.PIPE, stderr=err,
                                  stdin=subprocess.DEVNULL, cwd=str(self.repo), env=runner.environment(), check=False)
        ms = int((time.monotonic() - started) * 1000)
        text = done.stdout.decode("utf-8", "replace")
        ok, why = fault.answered(done.returncode, text)
        events.search(self.run, "later", None, None, qid, done.returncode, ms, ok)
        result = (fault.result_of(text) or {}) if ok else {}
        rerank = result.get("rerank")
        return result, ok, why, rerank.get("by") if isinstance(rerank, dict) else None

    # ---- grading

    def grade(self, q: dict, verdict, final) -> dict:
        grades = {}
        if final is not None and verdict in ("answer", "not_found"):
            said = final.get("answer") if verdict == "answer" else "Not found."
            text = prompts.GRADER_PROMPT.format(question=q["question"], gold=q["gold"], said=said)
            for name, model, call in (("grader", GRADER, "grader"), ("check", CHECK, "check")):
                meta, g = self.caller.call(model, prompts.GRADER_SYS, prompts.GRADER_SCHEMA, text, GRADER_BUDGET,
                                           call, q["id"])
                grades[name] = {**meta, "grade": (g or {}).get("grade")}
        return grades

    # ---- one question: the fresh 80's one(), kind "audit"

    def one(self, q: dict, first_result: dict) -> dict:
        bundles = [prompts.items_of(first_result)]
        attempts, final, verdict, searches = [], None, None, []
        for k in range(1, prompts.CAP + 1):
            meta, out = self.caller.call(READER, prompts.READER_SYS, prompts.READER_SCHEMA,
                                         prompts.prompt_of(q["question"], bundles), READER_BUDGET, f"reader-{k}",
                                         q["id"])
            out = out if isinstance(out, dict) else None
            attempts.append({"attempt": k, **meta, "verdict": (out or {}).get("verdict"),
                             "answer": (out or {}).get("answer"), "citations": (out or {}).get("citations")})
            if not out or out.get("verdict") not in ("answer", "search_again", "not_found"):
                verdict = "error"
                break
            final, verdict = out, out["verdict"]
            if verdict != "search_again" or k == prompts.CAP:
                break
            result, ok, why, by = self.search(q["id"], out.get("search") or q["question"])
            searches.append({"attempt": k, "ok": ok, "why": why, "rerank_by": by})
            bundles.append(prompts.items_of(result))
        if verdict == "search_again":
            verdict = "not_found"
        grades = self.grade(q, verdict, final)
        cites = []
        for c in (final or {}).get("citations") or []:
            try:
                cites.append((c.get("path"), int(c.get("start_line", 0)), int(c.get("end_line", 0))))
            except (TypeError, ValueError, AttributeError):
                continue
        got = [item for b in bundles for item in b]
        outside = [c for c in cites if not any(pth == c[0] and s <= c[2] and c[1] <= e for pth, s, e, *_ in got)]
        inside = [c for c in cites if c not in outside]
        right_cite = (not q["apart"]) and matcher.cited(self.repo, q, cites)
        right_inside = (not q["apart"]) and matcher.cited(self.repo, q, inside)
        row = {"id": q["id"], "kind": "audit", "apart": q["apart"], "final_verdict": verdict, "attempts": attempts,
               "answered_at": len(attempts) if verdict == "answer" else None,
               "gold_in_bundle": [any(matcher.hit(it, q) for it in b) for b in bundles],
               "citation_right": right_cite, "grades": grades, "searches": searches,
               "search_failures": sum(1 for s in searches if not s["ok"]), "citations": len(cites),
               "citations_outside": len(outside), "citation_right_only_outside": right_cite and not right_inside,
               "calls_retried": sum(1 for a in attempts if a.get("retried"))
                                + sum(1 for g in grades.values() if g.get("retried")),
               "first_stopping_reason": first_result.get("stopping_reason"),
               "first_gaps_name_ids": matcher.names_the_ids(first_result, q["question"]) if q["apart"] else None}
        write_whole(self.reader, f"{q['id']}.json", row)
        return row

    def work(self, q: dict, first_result: dict) -> None:
        if (self.reader / f"{q['id']}.json").exists():
            return  # a question with a row is never asked again
        with self.lock:
            if self.stopped:
                return
            if self.caller.total > self.brake:  # before the question starts: to the owner first
                self.stopped = True
                write_text(self.run / "STOPPED", "brake")
                events.append(self.run, "stopped", cause="brake")
                return
        self.one(q, first_result)


def rows_of(reader: Path) -> dict:
    out = {}
    for f in sorted(reader.glob("*.json")):
        if f.name == "plan.json":
            continue
        row = read_json(f)
        if isinstance(row, dict) and "id" in row:
            out[row["id"]] = row
    return out


def _counting(p: dict) -> Path | None:
    try:
        name = (p["run"] / "COUNTS").read_text().strip()
    except OSError:
        return None
    folder = p["run"] / name
    return folder if name in ("attempt-1", "attempt-2") and (folder / "DONE").is_file() else None


def _control_of(run, attempt_n: int) -> dict:
    """The ``control`` event of the counting attempt's control (``control-<n>``): hit@5, of, last, last_audit."""
    for e in reversed(ledger.read(run)):
        if e.get("event") == "control" and e.get("k") == attempt_n and e.get("ok") is True:
            return e
    return {}


def run(sets_root, audit, *, repo=None, gov=None, claude=None, projection=None, resume=False, emit) -> str:
    """The exit word: ``ok``, ``refused`` (``MS-`` codes), ``stopped`` (the brake) or ``used``. A usage fault raises
    ``UsageError``."""
    p = layout.paths(sets_root, audit)
    repo = Path(repo) if repo is not None else toplevel()
    gov = os.path.abspath(os.path.expanduser(str(gov) if gov is not None else "~/.local/bin/gov"))
    claude = os.path.abspath(os.path.expanduser(str(claude) if claude is not None else "~/.local/bin/claude"))
    for flag in (repo, gov, claude):
        if layout.inside(flag, p["root"]):
            raise UsageError("flag inside the sets root")
    if projection is not None and not projection > 0:
        raise UsageError("projection")
    run_dir, reader = p["run"], p["run"] / "reader"

    # a verdict stands: never run again, never re-scored (exit 3, nothing written)
    stopped = run_dir / "STOPPED"
    if os.path.lexists(run_dir / "FIGURES.json"):
        emit("USED")
        return "used"
    if not resume and (os.path.lexists(reader) or os.path.lexists(stopped)):
        emit("USED")
        return "used"
    if resume:
        if not (stopped.is_file() and stopped.read_text().strip() == "brake" and reader.is_dir()):
            emit("USED")
            return "used"
        last = (read_json(reader / "plan.json") or {}).get("projection")
        if projection is None or not isinstance(last, (int, float)) or not projection > last:
            raise UsageError("projection")

    counting = _counting(p)
    if counting is None:
        emit("MS-NOCOUNT")
        return "refused"
    decl = read_json(p["declaration"])
    if not isinstance(decl, dict):
        emit("MS-NOCOUNT")
        return "refused"
    if set_digest(p["hidden"]) != decl.get("set_digest"):
        emit("MS-DIGEST")
        return "refused"
    if declare.gov_pin(gov) != decl.get("gov_pin"):
        emit("MS-PIN")
        return "refused"
    qs = matcher.questions(p["root"], audit, "hidden", repo)
    parsed = fault.read_parsed(counting)
    where = figures.starts(parsed)
    if any(q["id"] not in where for q in qs):
        emit("MS-FIRSTS")
        return "refused"

    n = int(decl["n"])
    proj = projection_of(n, projection)
    brake = 2 * proj
    if resume:
        k = 1
        while os.path.lexists(run_dir / f"STOPPED-{k}"):
            k += 1
        os.replace(stopped, run_dir / f"STOPPED-{k}")
    else:
        os.mkdir(reader, 0o700)
    lock = open(reader / ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        emit("USED")
        return "used"
    first = {q["id"]: (fault.kept_result(counting / "kept" / f"{where[q['id']][0]:05d}.json") or {}) for q in qs}
    write_whole(reader, "plan.json", {"ids": [q["id"] for q in qs], "apart": [q["id"] for q in qs if q["apart"]],
                                      "projection": proj, "brake": brake})
    caller = Caller(claude, run_dir, reader)
    job = _Judge(p, repo, gov, caller, brake, emit)
    before = len(rows_of(reader))
    emit(f"JUDGE questions {len(qs)}; rows already written {before}; spent so far {caller.total:.2f} USD; "
         f"projection {proj:.2f}, brake {brake:.2f}")
    with ThreadPoolExecutor(WORKERS) as pool:
        list(pool.map(lambda q: job.work(q, first[q["id"]]), qs))
    if job.stopped:
        emit("STOPPED brake")
        return "stopped"
    rows = rows_of(reader)
    attempt_n = int(counting.name.rsplit("-", 1)[1])
    spend = {"usd": round(caller.total, 6), "projection": proj, "brake": brake}
    fig, misses = figures.build(audit, decl, qs, rows, counting, parsed, _control_of(run_dir, attempt_n), spend)
    figures.write_misses(run_dir, misses)
    figures.write_figures(run_dir, fig)
    v = fig["verdict"]
    events.append(run_dir, "figures", right=v["right"], wrong=v["wrong"], n=fig["n"], passes=v["passes"])
    retried = sum(r.get("calls_retried", 0) for r in rows.values())
    for line in figures.verdict_lines(fig, retried):
        emit(line)
    failed = sorted(r["id"] for r in rows.values() if r.get("search_failures"))
    if failed:
        emit(f"SEARCH FAILED {sum(r.get('search_failures', 0) for r in rows.values())}: {', '.join(failed)}")
    return "ok"
