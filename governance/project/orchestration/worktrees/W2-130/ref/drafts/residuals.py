"""W2-130 (c): every commit trailer value that names no record, listed once (DEC-927, DEC-861, DEC-1073). Read-only.

    python3 residuals.py <repo> <out.md> [<out.json>]

History is not rewritten. Reads every commit of HEAD as `gov links` reads it (gov.links.check: the same git log
format, the same trailer pattern, the message before DEC-182's date and the trailer block after it, `Task:`'s
first token, `Implements:` split on commas and spaces) and resolves each value against the same known set.
Unlike `gov links`, it also lists an `Implements:` value that is free text (a role, a word), which `gov links`
skips; and it marks the values the path map's `accepted_history` already accepts (DEC-927's 39 and the like).

Per residual: the value, the commits that carry it (first and last, count), the ticket each names in `Task:`,
and the candidates it should have named: for `Task:`, the coordination ticket of its time or `decision-record`;
for `Implements:`, the ids the commit's ticket's `sources:` holds and any DEC id in the commit's subject.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
OUT_JSON = Path(sys.argv[3]) if len(sys.argv) > 3 else None
sys.path.insert(0, str(ROOT / "src"))
import yaml  # noqa: E402

from gov.links import check  # noqa: E402
from gov.store import loader  # noqa: E402

repo = check._Repo(ROOT)
log = loader._git(repo.root, "-c", "core.quotePath=false", "log", check._LOG, "HEAD").decode("utf-8", "replace")
tickets = {str(front["id"]): (path, front) for path, front in repo.tickets}
path_map = yaml.safe_load((ROOT / loader.PATH_MAP_REL).read_text()) or {}
HISTORY_FROM = "HEAD"
if not path_map.get("accepted_history"):  # deleted by c5e9d962 (D-4 Q-8, lifted gate): read its last version
    gone = loader._git(repo.root, "log", "-S", "accepted_history", "--format=%H", "-1", "HEAD", "--",
                       loader.PATH_MAP_REL).decode().strip()
    if gone:
        HISTORY_FROM = gone[:8] + "^"
        path_map = yaml.safe_load(loader._git(repo.root, "show", f"{gone}^:{loader.PATH_MAP_REL}").decode()) or {}
accepted = {}
for item in path_map.get("accepted_history") or []:
    if isinstance(item, dict) and item.get("commit"):
        accepted[str(item["commit"])] = item
DEC = re.compile(r"(?<![A-Za-z0-9_])DEC-[0-9]+(?![0-9])")

totals = collections.Counter()
residual = {"Task": collections.OrderedDict(), "Implements": collections.OrderedDict()}


def accepted_for(sha):
    return next((item for commit, item in accepted.items() if sha.startswith(commit) or commit.startswith(sha)), None)


for chunk in log.split("\x1e")[1:]:
    sha, date, block, message = chunk.split("\x1f", 3)
    message = message.rstrip("\n")
    subject = message.split("\n", 1)[0]
    read_from = message if date < loader.TRAILER_RULE_DATE else block
    tasks, implements = [], []
    for key, value in loader._TRAILER.findall(read_from):
        items = [item for item in re.split(r"[,\s]+", value) if item]
        (tasks if key.lower() == "task" else implements).extend(items[:1] if key.lower() == "task" else items)
    ticket = None
    for task in tasks:
        totals["Task"] += 1
        named = repo.alias.get(task, task)
        if named in tickets:
            ticket = tickets[named]
        if task in check.EXEMPT_TASKS:
            totals["Task decision-record"] += 1
        elif repo.resolves(task):
            totals["Task resolves"] += 1
        else:
            residual["Task"].setdefault(task, []).append((sha, date, subject, None))
    raw_lines = [value.strip() for key, value in loader._TRAILER.findall(read_from) if key.lower() == "implements"]
    bad = []
    for value in dict.fromkeys(implements):
        totals["Implements"] += 1
        named = repo.lead_id(value)
        if named is not None and repo.resolves(named):
            totals["Implements resolves"] += 1
            continue
        bad.append((value, "free text" if named is None else "names no record"))
    if bad:
        whole = " | ".join(raw_lines)
        alone = len(bad) == 1 and whole.strip() == bad[0][0]
        totals["Implements residual pairs"] += len(bad)
        residual["Implements"].setdefault(bad[0][0] if alone else whole, []).append(
            (sha, date, subject, (ticket, bad[0][1] if alone else "prose in the trailer: " +
                                  ", ".join(v for v, _ in bad))))


def coordination(date):
    """The coordination ticket of a date: W1-45's DAEO-6cc2 before W2-00 existed (DEC-729), W2-00 after."""
    return "W2-00 (DAEO-sdxk)" if date >= "2026-10-16" else "W1-45 (DAEO-6cc2), the Wave 1 coordination ticket"


rows = []
for key in ("Task", "Implements"):
    for value, seen in residual[key].items():
        commits = [s for s, _, _, _ in seen]
        dates = sorted(d for _, d, _, _ in seen)
        acc = [s for s in commits if accepted_for(s)]
        if key == "Task":
            if value.rstrip(".") in check.EXEMPT_TASKS:
                should = "decision-record (a typing slip: the trailing full stop)"
            elif value == "owner-prompt":
                should = f"decision-record if the commit records an owner decision, else {coordination(dates[0])}"
            else:
                should = coordination(dates[0])
            ticket_names = ""
        else:
            ticket_ids = sorted({(f"{t[1].get('external-ref') or t[1].get('wbs_id')} ({t[1]['id']})"
                                  if (t[1].get('external-ref') or t[1].get('wbs_id')) else
                                  f"{t[1]['id']} (a child of {t[1].get('parent')})")
                                 for _, _, _, (t, _) in seen if t})
            ticket_names = ", ".join(ticket_ids) or "none (its Task: names no ticket)"
            cands = collections.Counter()
            for _, _, subject, (t, _) in seen:
                cands.update(DEC.findall(subject))
                if t:
                    cands.update(str(v) for v in (t[1].get("sources") or [])[:4])
            fixed = sorted({i for s in commits for i in ((accepted_for(s) or {}).get("should_implement") or [])})
            if value == "AR-9":  # Wave 1's exit-review item AR-9 (DEC-718 item 9), ruled by DEC-900
                cands = collections.Counter({"DEC-900 (the AR-9 ruling)": 2, "DEC-718 (its item 9, AR-9)": 1})
            elif seen[0][3][1].startswith("prose"):  # the ids in the line resolve; the words are a note
                ok = [t.strip("()") for t in re.split(r"[,\s]+", value) if repo.lead_id(t) and repo.resolves(repo.lead_id(t))]
                cands = collections.Counter({"nothing more: its ids resolve (" + ", ".join(ok) +
                                             "); the parenthesis is a note, not ids": 1})
            should = (("accepted as history, should_implement: " + ", ".join(fixed)) if fixed else
                      ", ".join(c for c, _ in cands.most_common(4)) or "no candidate in its ticket or subject")
        kind = "" if key == "Task" else seen[0][3][1]
        rows.append({"key": key, "value": value, "kind": kind, "count": len(seen), "first": commits[-1][:12],
                     "last": commits[0][:12], "dates": f"{dates[0]}..{dates[-1]}", "ticket": ticket_names,
                     "accepted_history": len(acc), "should_have_named": should,
                     "commits": [s[:12] for s in commits]})

lines = ["# W2-130 (c): commit-trailer residuals (draft, 2026-11-08)", "",
         "Every `Task:` and `Implements:` value in this repository's history that names no record, listed once, as "
         "DEC-927 did for its 39. History is not rewritten (W2-130 KPI 5; DEC-927, DEC-861, DEC-1073). Generated by "
         "`residuals.py` from HEAD; `gov links --all` lists the `Task:` ones and the `Implements:` ids, not the "
         "free-text `Implements:` values.", "",
         "## Totals", "",
         f"- `Task:` values: {totals['Task']}; resolve to a ticket or record: {totals['Task resolves']}; "
         f"`decision-record` (valid under DEC-861): {totals['Task decision-record']}; name no record: "
         f"{sum(len(v) for v in residual['Task'].values())} commits, {len(residual['Task'])} distinct values.",
         f"- `Implements:` values: {totals['Implements']}; resolve: {totals['Implements resolves']}; name no record: "
         f"{totals['Implements residual pairs']} (commit, value) pairs in "
         f"{sum(len(v) for v in residual['Implements'].values())} commits, {len(residual['Implements'])} distinct "
         f"values; {sum(r['accepted_history'] for r in rows if r['key'] == 'Implements')} of those commits were "
         f"accepted as history by the path map's `accepted_history` (read at `{HISTORY_FROM}`; the list was deleted "
         "by `c5e9d962`, D-4 Q-8, as a lifted gate).", "",
         "The census (m6) counted 3,561 `Task:` (3,053 resolving, 496 `decision-record`) and 4,246 `Implements:` "
         "(4,187 resolving). Today's figures differ by the commits since and by this script's reading (the trailer "
         "block after DEC-182's date, as `gov links` reads it).", ""]
for key in ("Task", "Implements"):
    lines += [f"## `{key}:` values that name no record", "",
              "| Value | Kind | Commits | Dates | Ticket (from `Task:`) | Already accepted as history | Should have named |"
              if key == "Implements" else "| Value | Commits | Dates | Should have named |",
              "|---|---|---|---|---|---|---|" if key == "Implements" else "|---|---|---|---|"]
    for r in sorted((r for r in rows if r["key"] == key), key=lambda r: (-r["count"], r["value"])):
        shas = ", ".join(f"`{s}`" for s in r["commits"][:6]) + (f" … (+{r['count'] - 6})" if r["count"] > 6 else "")
        if key == "Implements":
            lines.append(f"| `{r['value']}` | {r['kind']} | {r['count']}: {shas} | {r['dates']} | {r['ticket']} | "
                         f"{r['accepted_history']} of {r['count']} | {r['should_have_named']} |")
        else:
            lines.append(f"| `{r['value']}` | {r['count']}: {shas} | {r['dates']} | {r['should_have_named']} |")
    lines.append("")
lines += ["## What is done with them", "",
          "- Nothing is rewritten. This list goes into W2-130's record (`docs/research/W2-130-link-cleanup.md`).",
          "- The `Implements:` values in commits already in `accepted_history` need no further act.",
          "- The rest are listed only; the candidates are the commit's ticket's `sources:` and the ids its subject "
          "names, for a reader tracing the commit, not a correction of history.", ""]
OUT.write_text("\n".join(lines))
if OUT_JSON:
    OUT_JSON.write_text(json.dumps({"totals": totals, "rows": rows}, indent=1))
print(HISTORY_FROM, len(accepted), dict(totals), {k: len(v) for k, v in residual.items()},
      {k: sum(len(x) for x in v.values()) for k, v in residual.items()})
