"""W2-130 (a) and (b): the marks patch in tranches and the sources patch, against <repo>'s HEAD. Read-only.

    python3 build_patches.py <repo> <out-dir>

Writes, in <out-dir>:
- a1-marks-no-hint.patch    the drifting decisions with no hint in their own entry (W2-92-proto-drift.py's
                            "hint_in_own_entry" false, DEC-1073 (2)'s definitions: spent and PROPOSED left out)
- a2-marks-rest.patch       the other drifting decisions (they name some changer, not every one), on top of a1
- a3-marks-after-sitting.patch  every other UNMARKED_CHANGE: the 110 spent, the PROPOSED entries and the entries
                            already SUPERSEDED or DONE; on top of a2. Applied only after the owner's sitting, and
                            regenerated then (a decided status changes what is current and who is a changer)
- b1-sources-open.patch     UNLINKED_ID for open and in-progress tickets
- b2-sources-closed.patch   UNLINKED_ID for closed tickets: each edit is a CLOSED_TICKET_EDITED finding (S16,
                            DEC-1088 (6): "a decision id does not excuse the edit"), so it waits for the owner's word
- marks-audit.md            every mark with its tranche, form, label or free text, the changer's words, and a
                            pre-check flag; and 20 labelled marks drawn at random (seed 1302) for the auditor
- build-summary.json        the counts

The marks are gov.links.patch.marks's own (`gov links --propose-marks`), split by target; each tranche's diff is
taken against the text the earlier tranches leave, so they apply in order with `git apply`. A mark only appends to
a status line, so no line number moves. The sources are gov.links.patch.sources's own, split by ticket status.
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from gov.links import check, patch  # noqa: E402

HERE = Path(__file__).resolve().parent
DRIFT = ROOT / "docs/research/W2-92-proto-drift.py"

repo = check._Repo(ROOT)
found, _ = check.findings(repo, None)
unmarked = [f for f in found if f["code"] == "UNMARKED_CHANGE"]
statements = check._statements(repo)
unlinked = [f for f in found if f["code"] == "UNLINKED_ID"]

drift_json = OUT / "work-drift-head.json"
subprocess.run([sys.executable, str(DRIFT), str(ROOT), str(drift_json), "--from-head"], check=True,
               env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"}, stdout=subprocess.DEVNULL)
drift = json.loads(drift_json.read_text())
rows = {r["id"]: r for r in drift["rows"]}
spent = set(drift["summary"]["spent_for_status_reconciliation"]["ids"])
no_hint = {i for i, r in rows.items() if not r["hint_in_own_entry"]}


def tranche(target: str) -> str:
    if target in no_hint:
        return "a1"
    if target in rows:
        return "a2"
    return "a3"


def why_a3(target: str) -> str:
    status = repo.status.get(target)
    if target in spent:
        return "spent (sitting)"
    if status != "ACCEPTED":
        return f"{status} (sitting)" if status == "PROPOSED" else f"already {status}"
    return "ACCEPTED, superseded whole by an edge"


lines_of = {e["id"]: repo.status_line(e) for e in repo.entries}


def apply_marks(text: str, chosen: list[dict]) -> str:
    """gov.links.patch.marks's change, as text (the same rule: whole supersessions, then the parts, one line)."""
    wanted: dict[int, list[dict]] = {}
    for f in chosen:
        wanted.setdefault(lines_of[f["ids"][0]], []).append(f)
    lines = text.split("\n")
    for number, group in wanted.items():
        whole = [f["ids"][1] for f in group if f["whole"]]
        parts = [f["mark"].removeprefix("**Changed by:** ") for f in group if not f["whole"]]
        line = lines[number - 1].rstrip()
        if whole:
            line += f" · SUPERSEDED by {', '.join(whole)}"
        if parts:
            line += f" · **Changed by:** {', '.join(parts)}"
        lines[number - 1] = line
    return "\n".join(lines)


# ---------------------------------------------------------------- the auditor's sheet
def changer_words(f: dict) -> str:
    source, target = f["ids"][1], f["ids"][0]
    if f["form"].startswith("ARCHIVE"):
        for line in repo.files[check.ARCHIVE_REL].split("\n"):
            if line.startswith("- ") and target in line.split(":")[0]:
                return line[2:].strip()
        return ""
    origins = [x["origin"] for x in statements if x["target"] == target and x["source"] == source
               and x["cls"] in check.CHANGE_CLASSES and x["origin"] not in (None, source, target)]
    tries = [(source, target, "")] + [(o, target, f"[stated by {o}] ") for o in dict.fromkeys(origins)] \
        + [(target, source, "[in its own entry] ")]
    if not origins and any(x["where"] == "preamble" and x["target"] == target and x["source"] == source
                           for x in statements):
        for line in repo.register_text.split("\n"):
            if target in line and source in line and not line.startswith("### "):
                return "[change log] " + line.replace("|", "/")[:260]
    for owner, needle, said in tries:
        span = repo.entry.get(owner, {}).get("span", "")
        at = span.find(needle, span.find("\n") + 1) if owner == target else span.find(needle)
        if at >= 0:
            start = max(0, span.rfind("\n", 0, at) + 1, at - 160)
            return said + span[start:at + 160].replace("\n", " ").replace("|", "/").strip()
    return ""


def pre_check(f: dict) -> str:
    words, flags = changer_words(f), []
    if f["form"].startswith("ARCHIVE") and re.search(r"itself|then by", words):
        flags.append("archive chain: the later id may change the middle one, not this entry")
    if f["form"].startswith("ARCHIVE"):
        head, _, tail = words.partition(":")
        if re.search(r"DEC-\d+:", tail) and tail.find(f["ids"][1]) > tail.find(re.search(r"DEC-\d+:", tail).group(0)):
            flags.append("archive line holds a second 'DEC-n:' sentence: this changer belongs to that one")
        if len(re.findall(r"DEC-\d+", head)) > 1 and len(re.findall(r"DEC-\d+", tail)) > 1:
            flags.append("archive line names several entries and several changers: which changed which is unstated")
    if f["mark"].count("(") != f["mark"].count(")"):
        flags.append("unbalanced parentheses: the part was cut mid-phrase; write it by hand")
    if re.search(r"\((items?|item|part|Q)\)$", f["mark"]):
        flags.append("part not captured")
    if f["whole"] and len([g for g in unmarked if g["ids"][0] == f["ids"][0] and g["whole"]]) > 1:
        flags.append("two whole supersessions of one entry")
    if repo.status.get(f["ids"][0]) == "SUPERSEDED" and f["whole"]:
        flags.append("already SUPERSEDED: a second successor")
    source_span = repo.entry.get(f["ids"][1], {}).get("span", "")
    if f["text"] and not re.search(rf"\b{f['ids'][0]}(?![0-9])", source_span):
        flags.append("the changer's own entry never names this entry")
    if f["text"] and not f["whole"] and re.search(r"replac|supersed|withdraw", f["form"].split(":")[-1], re.I) \
            and not f["mark"].endswith(")"):
        flags.append("a text supersession with no part: Changed by, or SUPERSEDED by? (DEC-825 item 4)")
    if words.startswith("[stated by"):
        flags.append("stated by a third entry: check it is not a chain through that entry")
    if f["text"] and not words:
        flags.append("changer's words not found")
    return "; ".join(flags)


def certainly_wrong(f: dict) -> str:
    """A pair no auditor need weigh: a changer older than its target (readiness reviewer 2, F2), or the second
    'DEC-n:' sentence of an ARCHIVE §A line read as changing the first's entry."""
    if check._num(f["ids"][1]) < check._num(f["ids"][0]):
        return "the changer is older than the entry (reviewer 2 F2): a pattern misread, not a change"
    if "second 'DEC-n:' sentence" in pre_check(f):
        return "the ARCHIVE §A line's second sentence: this changer changes the other entry"
    return ""


# The independent audit (reviews/w2-130-marks.md, F1 to F5): marks the register's text does not support are dropped,
# and the parts it found wrong or cut are written as the audit says.
AUDIT_DROP = {("DEC-1050", "DEC-1057"): "F1", ("DEC-120", "DEC-173"): "F2", ("DEC-724", "DEC-860"): "F3",
              ("DEC-454", "DEC-904"): "F4", ("DEC-455", "DEC-904"): "F4", ("DEC-480", "DEC-899"): "F4",
              ("DEC-480", "DEC-904"): "F4", ("DEC-490", "DEC-868"): "F4", ("DEC-490", "DEC-899"): "F4",
              ("DEC-490", "DEC-908"): "F4", ("DEC-492", "DEC-904"): "F4", ("DEC-492", "DEC-908"): "F4"}
AUDIT_MARK = {("DEC-1084", "DEC-1087"): "DEC-1087 (13) (W2-33's layer lines back in Wave 2)",
              ("DEC-941", "DEC-946"): "DEC-946 (blocks A to E: their order)",
              ("DEC-988", "DEC-989"): "DEC-989 (item 3's baseline)",
              ("DEC-1032", "DEC-1033"): "DEC-1033 (items 2 and 3)",
              ("DEC-454", "DEC-868"): "DEC-868 (items 1 (b) and 3)",
              ("DEC-454", "DEC-899"): "DEC-899 (P-IS-4 (a))",
              ("DEC-455", "DEC-899"): "DEC-899 (P-IS-4 (a))",
              # not the audit's: the drafter's, from DEC-902's "**Changes:** DEC-899 item 10 (the proposal decided)"
              ("DEC-899", "DEC-902"): "DEC-902 (item 10: the proposal decided)"}


def audit_drop(f: dict) -> str:
    found = AUDIT_DROP.get((f["ids"][0], f["ids"][1]))
    return f"the independent audit's {found}: the register's text does not support it" if found else ""


dropped = [f for f in unmarked if certainly_wrong(f) or audit_drop(f)]
unmarked_all = unmarked
unmarked = []
for f in unmarked_all:
    if certainly_wrong(f) or audit_drop(f):
        continue
    key = (f["ids"][0], f["ids"][1])
    unmarked.append({**f, "mark": "**Changed by:** " + AUDIT_MARK[key], "audited_rewrite": True}
                    if key in AUDIT_MARK else f)
missing = (set(AUDIT_DROP) | set(AUDIT_MARK)) - {(f["ids"][0], f["ids"][1]) for f in unmarked_all}
if missing and not os.environ.get("W2130_AFTER_APPLY"):  # once a1/a2 are applied their audited pairs are gone
    sys.exit(f"the audit names pairs gov links no longer finds: {sorted(missing)}; re-read the audit")

summary = {"head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip(),
           "drift": {k: drift["summary"][k] for k in ("drifted_current", "drifted_no_hint",
                                                      "census_drifted_current_with_spent")},
           "unmarked_findings": len(unmarked_all), "unmarked_entries": len({f["ids"][0] for f in unmarked_all}),
           "marked_pairs": len(unmarked), "dropped_pairs": len(dropped)}
text = repo.register_text
whole_patch = patch.marks(repo.register_path, repo.register_text, [f for f in found if f not in dropped], lines_of)
names = {"a1": "a1-marks-no-hint.patch", "a2": "a2-marks-rest.patch", "a3": "a3-marks-after-sitting.patch"}
for key in ("a1", "a2", "a3"):
    chosen = [f for f in unmarked if tranche(f["ids"][0]) == key]
    after = apply_marks(text, chosen)
    (OUT / names[key]).write_text(patch._diff(repo.register_path, text, after))
    summary[key] = {"pairs": len(chosen), "entries": len({f["ids"][0] for f in chosen}),
                    "free_text_pairs": sum(1 for f in chosen if f["text"]),
                    "whole_supersessions": sum(1 for f in chosen if f["whole"])}
    text = after
summary["dropped_certainly_wrong"] = [{"entry": f["ids"][0], "changer": f["ids"][1], "mark": f["mark"],
                                       "why": certainly_wrong(f) or audit_drop(f)} for f in dropped]
summary["audited_rewrites"] = sorted(f"{a} <- {b}" for a, b in AUDIT_MARK)

# ---------------------------------------------------------------- a0: ARCHIVE §A's collective line, one decision a line
ARCHIVE_OLD = ("- DEC-454, DEC-455, DEC-480, DEC-490, DEC-492: changed by DEC-868, DEC-899, DEC-904 and DEC-908. "
               "Their close parts are now lifted (LIFTED §A).")
ARCHIVE_NEW = [  # the changers each entry's own text supports (the audit's F4)
    "- DEC-454: changed by DEC-868, DEC-899 and DEC-908. Its close parts are now lifted (LIFTED §A).",
    "- DEC-455: changed by DEC-868, DEC-899 and DEC-908. Its close parts are now lifted (LIFTED §A).",
    "- DEC-480: changed by DEC-868 and DEC-908. Its close parts are now lifted (LIFTED §A).",
    "- DEC-490: changed by DEC-904. Its close parts are now lifted (LIFTED §A).",
    "- DEC-492: changed by DEC-868 and DEC-899. Its close parts are now lifted (LIFTED §A)."]
archive_text = repo.files[check.ARCHIVE_REL]
if archive_text.count(ARCHIVE_OLD + "\n") == 1:
    (OUT / "a0-archive-one-per-line.patch").write_text(
        patch._diff(check.ARCHIVE_REL, archive_text, archive_text.replace(ARCHIVE_OLD, "\n".join(ARCHIVE_NEW))))
elif not all(line in archive_text for line in ARCHIVE_NEW):
    sys.exit("ARCHIVE-SUPERSEDED.md's collective §A line has changed; re-read the audit's F4")
else:  # a0 is applied (e12f8a30)
    (OUT / "a0-archive-one-per-line.patch").write_text("")
summary["a1"]["no_hint_entries_today"] = len(no_hint)
summary["a1"]["no_hint_entries_all_changers_proposed"] = sorted(
    no_hint - {f["ids"][0] for f in unmarked if tranche(f["ids"][0]) == "a1"})

# ---------------------------------------------------------------- (b) sources, split by the ticket's status
fronts = {path: front for path, front in repo.tickets}
openish = [f for f in unlinked if fronts.get(f["path"], {}).get("status") in check.OPEN]
closed = [f for f in unlinked if fronts.get(f["path"], {}).get("status") not in check.OPEN]
for name, chosen in (("b1-sources-open.patch", openish), ("b2-sources-closed.patch", closed)):
    (OUT / name).write_text(patch.sources({p: repo.files[p] for p in {f["path"] for f in chosen}}, chosen))
added = lambda chosen: len({(f["path"], f["ids"][0]) for f in chosen})  # noqa: E731
summary["b1"] = {"tickets": len({f["path"] for f in openish}), "ids_added": added(openish), "findings": len(openish)}
summary["b2"] = {"tickets": len({f["path"] for f in closed}), "ids_added": added(closed), "findings": len(closed)}
not_in_force = {i for f in openish for i in [f["ids"][0]] if repo.status.get(i) in check.NOT_IN_FORCE}
summary["b1"]["ids_not_in_force_added_to_open_tickets"] = sorted(not_in_force)

audit = ["# W2-130: the marks for the auditor (draft, 2026-11-08)", "",
         f"HEAD `{summary['head'][:12]}`. Every UNMARKED_CHANGE `gov links --all` finds, with the mark "
         "`--propose-marks` would add. KPI 3: an independent auditor checks every free-text mark (form not a "
         "register label: text, change log, ARCHIVE §A) and the 20 labelled marks drawn below, against both "
         "entries; a wrong mark is corrected or dropped, never committed.", "",
         "Pre-check: a mechanical flag only, by this draft, not the audit.", "",
         "| Tranche | Entry | Changer | Mark added | Form | Label/text | The changer's words (excerpt) | Pre-check |",
         "|---|---|---|---|---|---|---|---|"]
for f in sorted(unmarked, key=lambda f: (tranche(f["ids"][0]), check._num(f["ids"][0]), check._num(f["ids"][1]))):
    t = tranche(f["ids"][0])
    audit.append(f"| {t}{' (' + why_a3(f['ids'][0]) + ')' if t == 'a3' else ''} | {f['ids'][0]} | {f['ids'][1]} | "
                 f"{f['mark'].replace('|', '/')} | {f['form'].replace('|', '/')} | "
                 f"{'text' if f['text'] else 'label'} | {changer_words(f)[:260]} | {pre_check(f)} |")
labelled = [f for f in unmarked if not f["text"]]
sample = random.Random(1302).sample(labelled, min(20, len(labelled)))
audit += ["", "## The 20 labelled marks drawn at random (seed 1302)", ""]
audit += [f"- {f['ids'][0]} <- {f['ids'][1]}: `{f['mark']}` ({f['form']})" for f in sample]
flagged = [f for f in unmarked if pre_check(f)]
audit += ["", f"## Pre-check flags: {len(flagged)}", ""]
audit += [f"- {f['ids'][0]} <- {f['ids'][1]}: {pre_check(f)}" for f in flagged]
audit += ["", f"## Dropped from the patches, certainly wrong: {len(dropped)}", "",
          "These stay UNMARKED_CHANGE findings until the loader reads them right (reviewer 2's F2 row: one changer "
          "per clause, by its leading id) or the archive line is rewritten in labelled form; never an allow-list "
          "(LINK-INTEGRITY §9).", ""]
audit += [f"- {f['ids'][0]} <- {f['ids'][1]} (`{f['mark']}`, {f['form']}): {certainly_wrong(f)}. Words: "
          f"{changer_words(f)[:200]}" for f in dropped]
(OUT / "marks-audit.md").write_text("\n".join(audit) + "\n")

# ---------------------------------------------------------------- (e) reviewer 2's F2: the spurious changers
VERB = re.compile(r"\b(superseded|replaced|withdrawn|reversed|overturned|ended|amended|corrected|changed|lifted|"
                  r"refined|extended|settled|marked|shown|carried|kept|confirmed|supersedes|replaces|withdraws|"
                  r"amends|corrects|changes|settles|lifts|reverses|ends)\b", re.I)
change = [x for x in statements if x["cls"] in check.CHANGE_CLASSES and x["source"] != x["target"]
          and x["source"].startswith("DEC-") and x["target"].startswith("DEC-")]
older = sorted({(x["target"], x["source"], x["where"], x["form"], x["origin"]) for x in change
                if check._num(x["source"]) < check._num(x["target"])}, key=lambda r: (check._num(r[0]), check._num(r[1])))
FIX = {"label": "the loader's next pass: a `Changed by:`/`Lifted by:` value with no verb gives one changer per clause, "
                "its leading id; the other ids in it are its object or basis",
       "text": "the loader's next pass: a free-text verb takes a changer only when the clause's subject is this "
               "entry; a version-table row or a quoted case is not the entry's text",
       "preamble": "the change log's row names another entry; the loader reads the row's subject"}
marked_ids = {(f["ids"][0], f["ids"][1]) for f in unmarked_all}
rows_e = ["# W2-130 (e): readiness reviewer 2's F2, the spurious changers (draft, 2026-11-08)", "",
          f"HEAD `{summary['head'][:12]}`. From `.gov-runtime/scratch/orchestrator/reviews/readiness-2-links.md` F2. "
          "The register's text is not edited for these (W2-130's failure line: an entry's text changes only by its "
          "status marks); the fix is the loader's reading (a D-6 row, `register_statements`), and W2-130 commits "
          "no mark built on them.", "",
          f"## A. Certainly wrong: the changer is older than the entry ({len(older)})", "",
          "| Entry | Read as changed by | Where read | Form | In which entry's text | Was a proposed mark? | Fix |",
          "|---|---|---|---|---|---|---|"]
for t, src, where, form, origin in older:
    rows_e.append(f"| {t} | {src} | {where} | {form} | {origin or 'change log'} | "
                  f"{'yes: dropped from the patch' if (t, src) in marked_ids else 'no (its status line names it)'} | "
                  f"{FIX.get(where, FIX['text'])} |")
multi = []
for e in repo.entries:
    for value in re.findall(r"\*\*Changed by:\*\*([^·]*)", e["first"]):
        ids = list(dict.fromkeys(re.findall(r"DEC-\d+", value)))
        if len(ids) > 1 and not VERB.search(value.split(ids[1])[0]):
            multi.append((e["id"], ids, value.strip()[:160]))
rows_e += ["", f"## B. `Changed by:` values with no verb before their second id ({len(multi)} values)", "",
           "Each id after the first is read as a changer too. Some are real second changers (a list), others the "
           "object or basis of the first (as DEC-880's `DEC-882: DEC-843 is superseded …`). Fix: the loader's next "
           "pass takes the leading id of each clause; a real list is written `DEC-a; DEC-b`. Until then a bundle shows "
           "the extra ids in `changed_by` (nothing current hidden, nothing superseded shown current).", "",
           "| Entry | Ids read as changers | The value (excerpt) |", "|---|---|---|"]
rows_e += [f"| {i} | {', '.join(ids)} | {v.replace('|', '/')} |" for i, ids, v in multi]
(OUT / "e-spurious-changers.md").write_text("\n".join(rows_e) + "\n")
summary["e"] = {"older_changer_links": len(older), "multi_id_no_verb_values": len(multi)}
summary["audit"] = {"free_text_marks": sum(1 for f in unmarked if f["text"]), "labelled_sample": len(sample),
                    "pre_check_flags": len(flagged)}
(OUT / "build-summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
