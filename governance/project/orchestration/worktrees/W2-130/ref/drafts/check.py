"""W2-130 (d): the patches apply cleanly to today's register and tickets, and `gov links` falls as expected.

    python3 check.py <repo> [<work-dir>]

Touches nothing in <repo>: `git apply --check` there (read-only), then everything else on a scratch clone in
<work-dir> (default: this folder's work/clone), `git clone --shared` (the clone borrows <repo>'s objects, read-only,
and writes none into it). In the clone, each stage is applied and committed (gov links reads HEAD, and S16 reads the
commits), then the pinned `gov links --root <clone> --all` is run and its first line's counts recorded:

  0 before      HEAD as it is
  1 a1          the marks for the drifting decisions with no hint in their own entry (the "87"; 83 today)
  2 a2          the marks for the other drifting decisions
  3 b1          the sources: of open and in-progress tickets
  4 a3          (after the owner's sitting) the marks on spent, PROPOSED, SUPERSEDED and DONE entries, as they
                stand today; to be regenerated after the sitting
  5 b2          (with the owner's word on DEC-1088 (6)) the sources: of closed tickets

and W2-92-proto-drift.py --from-head before, after a2 and after a3, with the count this ticket's KPI 2 names: the
drifting decisions whose status line does not name every changer. Then the guards of the KPIs' failure lines: the
register diff changes status lines only, each by appending; every ticket's frontmatter other than sources: and its
body are byte-identical. Writes check-report.md and check-report.json beside this file; exits 1 on any failure.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FINAL = "--final" in sys.argv  # after the owner's sitting (DEC-1098 (3)): final/f1 to f5, built by final_build.py
ROOT = Path(ARGS[0]).resolve()
HERE = Path(__file__).resolve().parent
WORK = Path(ARGS[1]).resolve() if len(ARGS) > 1 else HERE / "work"
CLONE = WORK / ("final-check-clone" if FINAL else "clone")
GOV = Path.home() / ".local/bin/gov"
PATCHES = HERE / "final" if FINAL else HERE
BUILD = PATCHES / ("final-summary.json" if FINAL else "build-summary.json")
REPORT = "final-check-report" if FINAL else "check-report"
STAGES = [("a1", "a1-marks-no-hint.patch"), ("a2", "a2-marks-rest.patch"), ("a0", "a0-archive-one-per-line.patch"),
          ("b1", "b1-sources-open.patch"),
          ("a3", "a3-marks-after-sitting.patch"), ("b2", "b2-sources-closed.patch")]
if FINAL:
    STAGES = [(n, f"{n}-{rest}") for n, rest in (("f1", "statuses.patch"), ("f2", "archive.patch"),
                                                 ("f3", "ticket-kpi4.patch"), ("f4", "in-force.patch"),
                                                 ("f5", "marks.patch"))]
    STAGES = [(n, p) for n, p in STAGES if (PATCHES / p).read_text().strip()]  # f4 is empty when nothing clashes
IN_ORDER_ONLY = ("f5",) if FINAL else ("a2", "a3")  # taken against the text the earlier stages leave
REGISTER = "docs/DECISION_REGISTER.md"
failures: list[str] = []


def run(*args, cwd=None, check=True, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, check=check, env=env)


def links(root: Path) -> dict:
    """The pinned `gov links --all --json`: every finding, new and standing alike (the text form's first line
    counts the standing ones by code; the ones a stage's own commit brings are "new" and listed apart)."""
    out = run(str(GOV), "links", "--root", str(root), "--all", "--json", cwd=root, check=False)
    result = json.loads(out.stdout)["result"]
    counts, by_code = {}, {}
    for finding in result["findings"]:
        key = f"{finding['code']} {finding['role']}"
        counts[key] = counts.get(key, 0) + 1
        by_code[finding["code"]] = by_code.get(finding["code"], 0) + 1
    return {"summary": result.get("summary"), "new": result.get("new"), "by_code_role": counts,
            "by_code": by_code, "total": len(result["findings"]), "exit": out.returncode,
            "not_in_force": sorted(f["subject"] for f in result["findings"] if f["code"] == "NOT_IN_FORCE_AS_RULE"),
            "status_conflict": sorted(f["subject"] for f in result["findings"] if f["code"] == "STATUS_CONFLICT"),
            "enforces": sorted(f"{f['subject']} | {f['path']}:{f['line']}" for f in result["findings"]
                               if f["code"] == "ENFORCES_SUPERSEDED")}


def drift(root: Path) -> dict:
    out = WORK / "drift.json"
    run(sys.executable, str(root / "docs/research/W2-92-proto-drift.py"), str(root), str(out), "--from-head",
        env={"PYTHONPATH": str(root / "src"), "PATH": "/usr/bin:/bin"})
    data = json.loads(out.read_text())
    sys.path.insert(0, str(root / "src"))
    from gov.store.loader import register_entries
    entries = {e["id"]: e for e in register_entries((root / REGISTER).read_text())[0]}
    not_all = [r["id"] for r in data["rows"]
               if not all(re.search(rf"\b{c}(?![0-9])", entries[r["id"]]["first"]) for c in r["changers"])]
    return {"drifted_current": data["summary"]["drifted_current"],
            "drifted_no_hint": data["summary"]["drifted_no_hint"],
            "status_line_misses_a_changer": len(not_all), "misses": not_all}


def commit(message: str) -> None:
    run("git", "add", "-A", cwd=CLONE)
    run("git", "-c", "user.name=W2-130 check", "-c", "user.email=check@localhost", "commit", "-q", "-m", message,
        "--trailer", "Task: DAEO-q8cl", "--trailer", "Role: orchestrator", "--trailer", "Implements: DEC-1073",
        cwd=CLONE)


report = {"head": run("git", "rev-parse", "HEAD", cwd=ROOT).stdout.strip(), "apply_check_on_repo": {},
          "built_at": json.loads(BUILD.read_text())["head"], "mode": "final" if FINAL else "drafts",
          "stages": [], "drift": {}}

if report["built_at"] != report["head"]:
    failures.append(f"the patches were built at {report['built_at'][:12]}, HEAD is {report['head'][:12]}: "
                    f"rerun {'final_build.py' if FINAL else 'build_patches.py'} first")

# ---------------------------------------------------------------- 1. read-only: each patch against today's tree
for name, path in STAGES:
    if name in IN_ORDER_ONLY:
        continue  # taken against the text the earlier stages leave; checked in order on the clone
    out = run("git", "apply", "--check", "-v", str(PATCHES / path), cwd=ROOT, check=False)
    report["apply_check_on_repo"][name] = out.returncode == 0
    if out.returncode:
        failures.append(f"{path} does not apply to {ROOT} at HEAD: {out.stderr.strip()[:300]}")

# ---------------------------------------------------------------- 2. the scratch clone
if CLONE.exists():
    shutil.rmtree(CLONE)
WORK.mkdir(parents=True, exist_ok=True)
run("git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(CLONE))
run("git", "checkout", "-q", "--detach", report["head"], cwd=CLONE)
before_register = (CLONE / REGISTER).read_text()
before_tickets = {p.name: p.read_text() for p in (CLONE / ".tickets").glob("*.md")}

state = links(CLONE)
report["stages"].append({"stage": "before", **state})
report["drift"]["before"] = drift(CLONE)
for name, path in STAGES:
    out = run("git", "apply", "--check", str(PATCHES / path), cwd=CLONE, check=False)
    if out.returncode:
        failures.append(f"{path} does not apply in order on the clone: {out.stderr.strip()[:300]}")
        break
    run("git", "apply", str(PATCHES / path), cwd=CLONE)
    commit(f"W2-130 check: {path}")
    state = links(CLONE)
    report["stages"].append({"stage": name, **state})
    if name in ("a2", "a3", "f1", "f5"):
        report["drift"][f"after {name}"] = drift(CLONE)

# ---------------------------------------------------------------- 3. the expectations
build = json.loads(BUILD.read_text())
got = {s["stage"]: s["by_code"] for s in report["stages"]}
before = got.get("before", {})
roles = {s["stage"]: s["by_code_role"] for s in report["stages"]}


def expect(stage, code, value, why):
    have = got.get(stage, {}).get(code, 0)
    report.setdefault("expectations", []).append({"stage": stage, "code": code, "expected": value, "got": have,
                                                  "why": why, "ok": have == value})
    if have != value:
        failures.append(f"after {stage}: {code} {have}, expected {value} ({why})")


def expect_role(stage, key, value, why):
    have = roles.get(stage, {}).get(key, 0)
    report.setdefault("expectations", []).append({"stage": stage, "code": key, "expected": value, "got": have,
                                                  "why": why, "ok": have == value})
    if have != value:
        failures.append(f"after {stage}: {key} {have}, expected {value} ({why})")


def final_expectations():
    last = report["stages"][-1]["stage"]
    expect_role("before", "STATUS_CONFLICT orchestrator", 110, "the 110 spent-but-current ids, as the sitting found")
    expect_role("f1", "STATUS_CONFLICT orchestrator", 7,
                "after the statuses only group F's seven stay ACCEPTED while the archive still says spent")
    expect_role("f2", "STATUS_CONFLICT orchestrator", 0, "the archive agrees with the register (KPI 6)")
    expect("f2", "STATUS_CONFLICT", before.get("STATUS_CONFLICT", 0) - 110,
           "only MR-1..MR-6 left (group G: product-spec regenerates them)")
    expect(last, "UNMARKED_CHANGE", len(build["f5"]["dropped"]),
           "only the dropped wrong pairs left (the audit's 3 and the 5 older-changer misreads; the loader row)")
    for code in ("UNLINKED_ID", "CLOSED_TICKET_EDITED", "TICKET_CHANGE_UNMARKED", "UNKNOWN_ID"):
        expect(last, code, before.get(code, 0), "the final patches leave it as it was")
    # ENFORCES_SUPERSEDED rises only by places citing an id the rulings made SUPERSEDED or WITHDRAWN (D-6's to fix)
    newly = {i for i, w in build["status_changes_by_id"].items() if w in ("SUPERSEDED", "WITHDRAWN")}
    added = sorted(set(report["stages"][-1]["enforces"]) - set(report["stages"][0]["enforces"]))
    gone = sorted(set(report["stages"][0]["enforces"]) - set(report["stages"][-1]["enforces"]))
    stray = [x for x in added if re.findall(r"DEC-\d+", x.split(" | ")[0])[0] not in newly]
    report["enforces_added"] = {"count": len(added), "by_id": {i: sum(1 for x in added if f"cites {i}:" in x)
                                                               for i in sorted(newly)}, "stray": stray,
                                "gone": gone}
    ok = not stray and not gone
    report.setdefault("expectations", []).append(
        {"stage": last, "code": "ENFORCES_SUPERSEDED", "expected": f"{before.get('ENFORCES_SUPERSEDED', 0)} + new "
         "ones naming only ids the rulings superseded or withdrew", "got": got[last].get("ENFORCES_SUPERSEDED", 0),
         "why": f"{len(added)} new: " + ", ".join(f"{i} {n}" for i, n in report["enforces_added"]["by_id"].items()
                                                  if n), "ok": ok})
    if not ok:
        failures.append(f"ENFORCES_SUPERSEDED changed other than by the new supersessions: {(stray + gone)[:5]}")
    proposed = [x for x in report["stages"][-1]["not_in_force"] if "(PROPOSED)" in x and re.match(r"DEC-\d+ ", x)]
    report["proposed_still_cited"] = proposed
    if proposed:
        failures.append(f"a register decision is still PROPOSED where it is cited as a rule: {proposed[:5]}")
    sys.path.insert(0, str(CLONE / "src"))
    from gov.store.loader import register_entries
    status = {e["id"]: e["status"] for e in register_entries((CLONE / REGISTER).read_text())[0]}
    sitting = (CLONE / "governance/project/orchestration/packages/W2-130-SITTING.md").read_text()
    wrong = []
    for i, prop in re.findall(r"^\| (DEC-\d+) \| [^|]* \| [^|]* \| \*\*(.+?)\*\* \|", sitting, re.M):
        want = "ACCEPTED" if prop.startswith(("ACCEPTED", "In force", "Stays ACCEPTED")) else prop.split(" ")[0]
        if status.get(i) != want:
            wrong.append(f"{i}: {status.get(i)} (ruled {want})")
    report["rulings_read_back"] = {"checked": len(re.findall(r"^\| DEC-\d+ \|", sitting, re.M)), "wrong": wrong}
    if wrong:
        failures.append(f"statuses not as ruled: {wrong[:5]}")


if FINAL:
    final_expectations()
else:
  expect("a1", "UNMARKED_CHANGE", before.get("UNMARKED_CHANGE", 0) - build["a1"]["pairs"], "a1's pairs marked")
  expect("a2", "UNMARKED_CHANGE", build["a3"]["pairs"] + build["dropped_pairs"], "a3's pairs and the dropped left")
  AUDIT_CLEARS = 9  # the archive rewrite clears the 9 pairs only ARCHIVE §A's collective line stated (audit F4)
  expect("a0", "UNMARKED_CHANGE", build["a3"]["pairs"] + build["dropped_pairs"] - AUDIT_CLEARS,
         "the archive one decision a line: its 9 unsupported pairs gone")
  for stage, value in (("a1", 86), ("a2", 46), ("a0", 37)):  # the independent audit's figures (w2-130-marks.md)
      expect(stage, "UNMARKED_CHANGE", value, "the independent audit's figure")
  expect("b1", "UNLINKED_ID", build["b2"]["findings"], "only closed tickets' findings left")
  expect("a3", "UNMARKED_CHANGE", build["dropped_pairs"] - AUDIT_CLEARS,
         "only the dropped pairs the archive rewrite does not clear (the loader row)")
  expect("b2", "UNLINKED_ID", 0, "every ticket linked")
  expect("b2", "CLOSED_TICKET_EDITED", before.get("CLOSED_TICKET_EDITED", 0) + build["b2"]["tickets"],
         "each closed ticket b2 edits is one S16 finding (DEC-1088 (6))")
  expect("a2", "STATUS_CONFLICT", before.get("STATUS_CONFLICT", 0), "marks change no status")

# ---------------------------------------------------------------- 4. the failure lines' guards
after_register = (CLONE / REGISTER).read_text()
old, new = before_register.split("\n"), after_register.split("\n")
changed = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
def kept_whole(a: str, b: str) -> bool:
    """The old status line is in the new one whole: an append at the end, or (final) a status word inserted right
    after `**Status:** ` with the old text following it unchanged."""
    if not a.lstrip().startswith("- **Status:**"):
        return False
    if b.startswith(a.rstrip()):
        return True
    cut = a.index("**Status:**") + len("**Status:**")
    rest = a[cut:].lstrip(" ").rstrip()
    return FINAL and b.startswith(a[:cut] + " ") and re.search(r"; it was " + re.escape(rest), b) is not None


bad = [i + 1 for i in changed if not kept_whole(old[i], new[i])]
report["register"] = {"lines_changed": len(changed), "same_line_count": len(old) == len(new),
                      "not_an_append_to_a_status_line": bad[:20]}
if bad or len(old) != len(new):
    failures.append(f"the register changed other than by appending to status lines: lines {bad[:10]}")


def split(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---", 4)
    return yaml.safe_load(text[4:end]) or {}, text[end:]


ticket_bad = []
for name, text in before_tickets.items():
    now = (CLONE / ".tickets" / name).read_text()
    if now == text:
        continue
    (fa, ba), (fb, bb) = split(text), split(now)
    if FINAL:  # only W2-130's KPI 4 (H1 (b)), marked with the deciding ids
        ka, kb = fa.get("kpis", {}).get("success", []), fb.get("kpis", {}).get("success", [])
        diff_at = [n for n, (x, y) in enumerate(zip(ka, kb)) if x != y]
        added_sources = [x for x in (fb.get("sources") or []) if x not in (fa.get("sources") or [])]
        ok = (name == "DAEO-q8cl.md" and {k: v for k, v in fa.items() if k not in ("kpis", "sources")} ==
              {k: v for k, v in fb.items() if k not in ("kpis", "sources")} and ba == bb
              and (fb.get("sources") or [])[:len(fa.get("sources") or [])] == (fa.get("sources") or [])
              and set(added_sources) <= {"DEC-1098", "DEC-1088"} and len(ka) == len(kb) and diff_at == [3]
              and kb[3].endswith("[changed, DEC-1098 (3); DEC-1088 (6)]") and fa["kpis"].get("failure") ==
              fb["kpis"].get("failure"))
        if not ok:
            ticket_bad.append(name)
        continue
    others_same = {k: v for k, v in fa.items() if k != "sources"} == {k: v for k, v in fb.items() if k != "sources"}
    kept = set(map(str, fa.get("sources") or [])) <= set(map(str, fb.get("sources") or []))
    if not (others_same and ba == bb and kept):
        ticket_bad.append(name)
report["tickets"] = {"changed": sum(1 for n, t in before_tickets.items() if (CLONE / ".tickets" / n).read_text() != t),
                     "changed_other_than_sources": ticket_bad}
if ticket_bad:
    failures.append(f"tickets changed other than sources: {ticket_bad[:10]}")

report["failures"] = failures
(HERE / f"{REPORT}.json").write_text(json.dumps(report, indent=1))
codes = sorted({c for s in report["stages"] for c in s["by_code"]})
md = [f"# W2-130 check report ({report['mode']}; generated by check.py)", "",
      f"HEAD `{report['head'][:12]}`; scratch clone `{CLONE}` (`git clone --shared`, nothing written to the repo).",
      "", "## `git apply --check` against the repository's HEAD (read-only)", ""]
md += [f"- {k}: {'applies' if v else 'FAILS'}" for k, v in report["apply_check_on_repo"].items()]
md += [f"- {', '.join(IN_ORDER_ONLY)}: taken against the text the earlier stages leave; checked in order on the clone below", "",
       "## `gov links --root <clone> --all`, by code, after each stage (cumulative)", "",
       "| Code | " + " | ".join(s["stage"] for s in report["stages"]) + " |",
       "|---|" + "---|" * len(report["stages"])]
for code in codes:
    md.append(f"| {code} | " + " | ".join(str(s["by_code"].get(code, 0)) for s in report["stages"]) + " |")
md.append("| **total** | " + " | ".join(str(s["total"]) for s in report["stages"]) + " |")
md += ["", "## The drift script (`W2-92-proto-drift.py --from-head`) on the clone", "",
       "| Point | drifted, current | with no hint in their own entry | status line misses a changer |",
       "|---|---|---|---|"]
md += [f"| {k} | {v['drifted_current']} | {v['drifted_no_hint']} | {v['status_line_misses_a_changer']} |"
       for k, v in report["drift"].items()]
md += ["", "## Expectations", ""]
md += [f"- {'ok' if e['ok'] else 'FAIL'}: after {e['stage']}, {e['code']} {e['got']} (expected {e['expected']}: "
       f"{e['why']})" for e in report.get("expectations", [])]
md += ["", "## Guards", "",
       f"- Register: {report['register']['lines_changed']} lines changed, each an append to a status line; line count "
       f"unchanged: {report['register']['same_line_count']}; other changes: {report['register']['not_an_append_to_a_status_line'] or 'none'}",
       f"- Tickets: {report['tickets']['changed']} changed; changed other than "
       f"{'W2-130 KPI 4 and its two new sources' if FINAL else '`sources:`'}: {report['tickets']['changed_other_than_sources'] or 'none'}"]
if FINAL:
    rb = report.get("rulings_read_back", {})
    md += [f"- Rulings read back from the clone's register: {rb.get('checked')} checked, not as ruled: "
           f"{rb.get('wrong') or 'none'}",
           f"- PROPOSED register decisions still cited as a rule: {report.get('proposed_still_cited') or 'none'}",
           "- NOT_IN_FORCE_AS_RULE, before → after: " + str(report["stages"][0]["by_code"].get("NOT_IN_FORCE_AS_RULE", 0))
           + " → " + str(report["stages"][-1]["by_code"].get("NOT_IN_FORCE_AS_RULE", 0)) + "; new ones: "
           + "; ".join(sorted(set(report["stages"][-1]["not_in_force"]) - set(report["stages"][0]["not_in_force"])))[:900]]
md += ["",
       f"## Result: {'PASS' if not failures else 'FAIL'}", ""] + [f"- {f}" for f in failures]
(HERE / f"{REPORT}.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
sys.exit(1 if failures else 0)
