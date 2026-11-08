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

ROOT = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
WORK = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else HERE / "work"
CLONE = WORK / "clone"
GOV = Path.home() / ".local/bin/gov"
STAGES = [("a1", "a1-marks-no-hint.patch"), ("a2", "a2-marks-rest.patch"), ("a0", "a0-archive-one-per-line.patch"),
          ("b1", "b1-sources-open.patch"),
          ("a3", "a3-marks-after-sitting.patch"), ("b2", "b2-sources-closed.patch")]
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
            "by_code": by_code, "total": len(result["findings"]), "exit": out.returncode}


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
          "built_at": json.loads((HERE / "build-summary.json").read_text())["head"],
          "stages": [], "drift": {}}

if report["built_at"] != report["head"]:
    failures.append(f"the patches were built at {report['built_at'][:12]}, HEAD is {report['head'][:12]}: "
                    "rerun build_patches.py first")

# ---------------------------------------------------------------- 1. read-only: each patch against today's tree
for name, path in STAGES:
    if name in ("a2", "a3"):
        continue  # a2 and a3 are taken against the text a1 (and a2) leave; checked in order on the clone
    out = run("git", "apply", "--check", "-v", str(HERE / path), cwd=ROOT, check=False)
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
    out = run("git", "apply", "--check", str(HERE / path), cwd=CLONE, check=False)
    if out.returncode:
        failures.append(f"{path} does not apply in order on the clone: {out.stderr.strip()[:300]}")
        break
    run("git", "apply", str(HERE / path), cwd=CLONE)
    commit(f"W2-130 check: {path}")
    state = links(CLONE)
    report["stages"].append({"stage": name, **state})
    if name in ("a2", "a3"):
        report["drift"][f"after {name}"] = drift(CLONE)

# ---------------------------------------------------------------- 3. the expectations
build = json.loads((HERE / "build-summary.json").read_text())
got = {s["stage"]: s["by_code"] for s in report["stages"]}
before = got.get("before", {})


def expect(stage, code, value, why):
    have = got.get(stage, {}).get(code, 0)
    report.setdefault("expectations", []).append({"stage": stage, "code": code, "expected": value, "got": have,
                                                  "why": why, "ok": have == value})
    if have != value:
        failures.append(f"after {stage}: {code} {have}, expected {value} ({why})")


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
bad = [i + 1 for i in changed if not (new[i].startswith(old[i].rstrip()) and old[i].lstrip().startswith("- **Status:**"))]
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
    others_same = {k: v for k, v in fa.items() if k != "sources"} == {k: v for k, v in fb.items() if k != "sources"}
    kept = set(map(str, fa.get("sources") or [])) <= set(map(str, fb.get("sources") or []))
    if not (others_same and ba == bb and kept):
        ticket_bad.append(name)
report["tickets"] = {"changed": sum(1 for n, t in before_tickets.items() if (CLONE / ".tickets" / n).read_text() != t),
                     "changed_other_than_sources": ticket_bad}
if ticket_bad:
    failures.append(f"tickets changed other than sources: {ticket_bad[:10]}")

report["failures"] = failures
(HERE / "check-report.json").write_text(json.dumps(report, indent=1))
codes = sorted({c for s in report["stages"] for c in s["by_code"]})
md = ["# W2-130 check report (generated by check.py)", "",
      f"HEAD `{report['head'][:12]}`; scratch clone `{CLONE}` (`git clone --shared`, nothing written to the repo).",
      "", "## `git apply --check` against the repository's HEAD (read-only)", ""]
md += [f"- {k}: {'applies' if v else 'FAILS'}" for k, v in report["apply_check_on_repo"].items()]
md += ["- a2 and a3: taken against the text a1 (and a2) leave; checked in order on the clone below", "",
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
       f"- Tickets: {report['tickets']['changed']} changed; changed other than `sources:`: "
       f"{report['tickets']['changed_other_than_sources'] or 'none'}", "",
       f"## Result: {'PASS' if not failures else 'FAIL'}", ""] + [f"- {f}" for f in failures]
(HERE / "check-report.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
sys.exit(1 if failures else 0)
