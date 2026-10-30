"""Shared tree builder and runner for W2-51's acceptance tests: the Wave 2 plan validator (DEC-744).

Every test builds a plan tree of its own, from scratch, in pytest's ``tmp_path``, and runs the validator on it as a
subprocess: ``python3 docs/plan/tools/validate_w2.py --root <tree>``. Nothing here reads this repository's live plan.

The trees imitate, in miniature, the real forms of ``docs/plan/WAVE_2_WBS.md`` (§1's ticket table and its paragraph
"The Contract's N Wave 2 items, by ticket."), ``.tickets/*.md``, ``docs/plan/WAVE_2_LIST.md``,
``docs/plan/WAVE_2_TRIAGE.md``, ``docs/contract/contract.yaml`` (with a ``CONTRACT_v4.md`` that agrees with it) and,
for a 4.2 Contract, a CIT-P under ``docs/changes/`` whose proposed text holds fenced YAML covers entries.

Contract ids in these trees are fictitious (CAP-91 to CAP-99, which the real Contract does not hold), so that no file
of this folder ever reads as an acceptance test citing a real Contract item.
"""

from __future__ import annotations

import copy
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

WORKTREE = Path(__file__).resolve().parents[3]
SCRIPT = WORKTREE / "docs" / "plan" / "tools" / "validate_w2.py"
SRC = WORKTREE / "src"

# The eight named checks the README fixes (the validator's public interface).
WAVE2_TICKETS = "wave2-tickets"
DELIVERED = "contract-items-delivered"
CITED = "contract-items-cited-by-tests"
IDS_EXIST = "ticket-contract-ids-exist"
CITP_MOVED = "cit-p-moved-items"
CITP_APPLIED = "cit-p-lines-applied"
LIST_COUNTS = "list-counts"
TRIAGE_COUNTS = "triage-counts"
CHECKS = (WAVE2_TICKETS, DELIVERED, CITED, IDS_EXIST, CITP_MOVED, CITP_APPLIED, LIST_COUNTS, TRIAGE_COUNTS)

# One line per check: "<STATUS> <name> — <reason>", STATUS one of PASS, FAIL, NOT RUN; the name one token.
STATUS_LINE = re.compile(r"^(PASS|FAIL|NOT RUN) ([A-Za-z0-9._-]+) — (\S.*)$")
STATUS_START = re.compile(r"^(PASS|FAIL|NOT RUN)\b")


# --------------------------------------------------------------------------------------------------------------------
# The plan model
# --------------------------------------------------------------------------------------------------------------------

def _cover(cid, wave, item=None, source="Contract v3 Z1"):
    return {"id": cid, "item": item or f"The behaviour of {cid}", "source": source, "wave": wave}


def _cap(cid, title, wave, covers):
    return {
        "id": cid,
        "title": title,
        "outcome": f"An agent can rely on {title.lower()}.",
        "acceptance": f"Given a case of {title.lower()}, the check holds.",
        "wave": wave,
        "provider": ["W1-07"] if wave == "W1" else [f"{wave}: later"],
        "sources": ["Contract v3 Z1", "DEC-900"],
        "disposition": {"class": "KEPT"},
        "covers": covers,
    }


def _ticket(tid, w2, title, closes=(), kpi_ids=(), sources=(), wbs=True, ext=True, cls="implementation"):
    fm = {"id": tid, "status": "open", "deps": [], "links": [], "created": "2026-10-16T16:35:11Z", "type": "task",
          "priority": 1, "assignee": "engineer"}
    if ext:
        fm["external-ref"] = w2
    fm["tags"] = ["wave-2", cls]
    if wbs:
        fm["wbs_id"] = w2
    fm.update({
        "title": title, "class": cls, "state_class": "AUTHORITATIVE", "role": "engineer", "depends_on": [],
        "allowed_paths": [f"src/gov/{tid.lower()}/**"],
        "kpis": {"success": [f"It does {title.lower()}" + (f" [{', '.join(kpi_ids)}]." if kpi_ids else ".")],
                 "failure": ["It does not."]},
        "profile": "STANDARD", "sources": list(sources) or ["DEC-900"], "est_loc": 50,
        "acceptance_tests": {"path": f"tests/acceptance/{w2}/", "author": "independent-test-designer (MR-3)"},
        "closes": list(closes), "list_rows": [],
    })
    return fm


class Plan:
    """A plan tree in memory; ``write(root)`` lays it out on disk."""

    def __init__(self):
        self.version = "4.1"
        self.change_log = [
            {"version": "4.0", "date": "2026-09-30", "change": "Contract v4 as closed."},
            {"version": "4.1", "date": "2026-10-03", "change": "S2 specification change (docs/changes/S2-CIT-P.md)."},
        ]
        self.capabilities = [
            _cap("CAP-91", "Budget things", "W2", [
                _cover("CAP-91.a", "W2"), _cover("CAP-91.b", "W2"), _cover("CAP-91.c", "W1")]),
            _cap("CAP-92", "Role things", "W1", [_cover("CAP-92.a", "W1"), _cover("CAP-92.b", "W2")]),
            _cap("CAP-93", "Release things", "W1", [
                _cover("CAP-93.a", "W1"),
                _cover("CAP-93.b", "W3", "Release contents: a manifest, file hashes, versions and notes"),
                _cover("CAP-93.c", "NONE", "Non-goal: key rotation")]),
            _cap("CAP-94", "Adoption things", "W3", [_cover("CAP-94.a", "W3", "Adoption verdict")]),
            _cap("CAP-95", "Audit things", "W3", [_cover("CAP-95.a", "W3", "Audit gate")]),
        ]
        # The plan's baseline: WBS §1 "The Contract's N Wave 2 items, by ticket." (bullets of ids → ticket).
        self.baseline = [("CAP-91.a and CAP-91.b", "W2-02"), ("CAP-92.b", "W2-03a")]
        self.adds_lite = None  # the WBS §1 paragraph "Contract v4.2 adds, lite (...)" in a 4.2 tree
        # .tickets/: file name → frontmatter
        self.tickets = {
            "DAEO-t000.md": _ticket("DAEO-t000", "W2-00", "Wave 2 coordination", closes=["DEC-900"], cls="coordination"),
            "DAEO-t001.md": _ticket("DAEO-t001", "W2-01", "Close and traceability", sources=["CAP-91", "DEC-900"]),
            "DAEO-t002.md": _ticket("DAEO-t002", "W2-02", "Budget gates", closes=["CAP-91.a", "CAP-91.b"],
                                    kpi_ids=["CAP-91.a", "CAP-91.b"], sources=["CAP-91.a", "CAP-91.b"]),
            # W2-15a's form (DEC-730): the W2 number in external-ref only, no wbs_id.
            "DAEO-t03a.md": _ticket("DAEO-t03a", "W2-03a", "Role records, pass 1", closes=["CAP-92.b"],
                                    kpi_ids=["CAP-92.b"], sources=["CAP-92.b"], wbs=False),
            # W2-16's real form: a closes entry cut by YAML at its comma ("<id> (lite", "DEC-722)").
            "DAEO-t004.md": _ticket("DAEO-t004", "W2-04", "Hash-pinned releases (lite)",
                                    closes=["CAP-93.b (lite", "DEC-900)"], kpi_ids=["CAP-93.b lite"],
                                    sources=["CAP-93.b", "DEC-900"]),
            "DAEO-t005.md": _ticket("DAEO-t005", "W2-05", "Contract v4.2, lite", closes=["DEC-900"],
                                    kpi_ids=["CAP-93"], sources=["CAP-93", "CAP-93.b", "DEC-900"],
                                    cls="specification"),
            # A Wave 1 ticket: not a Wave 2 ticket, so the Contract ids it cites are not checked here.
            "DAEO-w107.md": _ticket("DAEO-w107", "W1-07", "An old Wave 1 ticket", closes=["CAP-99.z"],
                                    kpi_ids=["CAP-99.z"], sources=["CAP-99.z"]),
        }
        self.tickets["DAEO-w107.md"]["status"] = "closed"
        self.tickets["DAEO-w107.md"]["tags"] = ["wave-1"]
        # WBS §1 table rows: (W2 id, bold, title, closes column)
        self.wbs_rows = [
            ("W2-00", False, "Wave 2 coordination", "DEC-900"),
            ("W2-01", True, "Close and traceability", "AR-8"),
            ("W2-02", True, "Budget gates", "CAP-91.a, CAP-91.b"),
            ("W2-03a", True, "Role records, pass 1", "CAP-92.b"),
            ("W2-04", False, "Hash-pinned releases (lite)", "CAP-93.b (lite, DEC-900)"),
            ("W2-05", False, "Contract v4.2, lite", "DEC-900"),
        ]
        # tests/: relative path → text. Each citation sits in the delivering ticket's own acceptance folder.
        self.tests = {
            "tests/acceptance/W2-02/test_w2_02_budget.py":
                "# Success line 1 [CAP-91.a]: a ticket declares a budget\n\ndef test_budget():\n    assert True\n",
            "tests/acceptance/W2-02/README.md": "# W2-02\n\n| Test | Source |\n|---|---|\n| test_breach | CAP-91.b |\n",
            "tests/acceptance/W2-03a/test_w2_03a_roles.py":
                "# Success line 1 [CAP-92.b]\n\ndef test_roles():\n    assert True\n",
            "tests/acceptance/W2-04/test_w2_04_release.py":
                "# Success line 1 [CAP-93.b lite]: the manifest\n\ndef test_manifest():\n    assert True\n",
            "tests/unit/plan/test_nothing.py": "def test_nothing():\n    assert True\n",
        }
        # docs/plan/WAVE_2_LIST.md §3: severity → rows (id, item); stated counts default to the rows' counts.
        self.list_rows = {
            "high": [("W2-H001", "A lead keeps orchestrator rights"), ("W2-H002", "CI job red until approved")],
            "medium": [("W2-M001", "No test against the daemon"), ("W2-M002", "Canary near spellings"),
                       ("W2-M003", "Duplicate keys last-wins")],
            "low": [("W2-L001", "Cosmetic gap in a message")],
            "info": [("W2-I001", "An observation")],
        }
        self.list_stated = {}  # severity → stated count, when it must differ from the rows
        # docs/plan/WAVE_2_TRIAGE.md: (row, severity, disposition)
        self.triage_rows = [
            ("W2-H001", "high", "W2-01"), ("W2-H002", "high", "Wave 3"),
            ("W2-M001", "medium", "W2-03a"), ("W2-M002", "medium", "backlog"), ("W2-M003", "medium", "W2-02"),
            ("W2-L001", "low", "backlog"), ("W2-I001", "info", "Wave 3"),
        ]
        self.triage_stated = {}  # (severity or "all", column) → stated count, when it must differ
        self.cit_p = {}  # docs/changes file name → text
        self.extra_files = {}  # relative path → text

    # ---- views and edits ------------------------------------------------------------------------------------------

    def cover(self, cid):
        for cap in self.capabilities:
            for cv in cap["covers"]:
                if cv["id"] == cid:
                    return cv
        raise KeyError(cid)

    def cap(self, cid):
        return next(c for c in self.capabilities if c["id"] == cid)

    def ticket(self, w2):
        for fm in self.tickets.values():
            if fm.get("wbs_id", fm.get("external-ref")) == w2:
                return fm
        raise KeyError(w2)

    def ticket_file(self, w2):
        for name, fm in self.tickets.items():
            if fm.get("wbs_id", fm.get("external-ref")) == w2:
                return name
        raise KeyError(w2)

    def copy(self):
        return copy.deepcopy(self)

    # ---- writing ---------------------------------------------------------------------------------------------------

    def write(self, root):
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        _w(root / "docs/contract/contract.yaml", self._contract_yaml())
        _w(root / "docs/contract/CONTRACT_v4.md", self._contract_md())
        _w(root / "docs/plan/WAVE_2_WBS.md", self._wbs())
        _w(root / "docs/plan/WAVE_2_LIST.md", self._list())
        _w(root / "docs/plan/WAVE_2_TRIAGE.md", self._triage())
        for name, fm in self.tickets.items():
            w2 = fm.get("wbs_id", fm.get("external-ref"))
            body = f"# {w2} {fm['title']}\n\nCard: `docs/plan/WAVE_2_WBS.md` §2 ({w2}).\n"
            _w(root / ".tickets" / name, "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                                                                   width=120) + "---\n" + body)
        for rel, text in self.tests.items():
            _w(root / rel, text)
        for name, text in self.cit_p.items():
            _w(root / "docs/changes" / name, text)
        for rel, text in self.extra_files.items():
            _w(root / rel, text)
        return root

    def _contract_yaml(self):
        doc = {
            "id": "CONTRACT-v4", "status": "ACCEPTED", "version": self.version, "date": "2026-09-30",
            "revised": self.change_log[-1]["date"], "change_log": self.change_log,
            "waves": {"W1": "Integrate", "W2": "Strengthen", "W3": "Complete", "NONE": "dropped (non-goal)"},
            "master_rules": [{"id": "MR-1", "title": "Readiness", "acceptance": "A ticket is ready.",
                              "provider": ["W1-07"]}],
            "capabilities": self.capabilities,
        }
        return "# Contract v4 — machine-readable. Same content as CONTRACT_v4.md.\n" + yaml.safe_dump(
            doc, sort_keys=False, allow_unicode=True, width=120)

    def _contract_md(self):
        out = ["---", "id: CONTRACT-v4", "status: ACCEPTED", f'version: "{self.version}"', "---", "",
               f"# Contract v4 (version {self.version})", "", "| Version | Date | Change |", "|---|---|---|"]
        out += [f"| {c['version']} | {c['date']} | {c['change']} |" for c in self.change_log]
        out.append("")
        for cap in self.capabilities:
            out += [f"### {cap['id']} — {cap['title']}", "", f"- **Wave:** {cap['wave']}", "- **Covers:**"]
            out += [f"  - `{cv['id']}` [{cv['wave']}] {cv['item']} — {cv['source']}" for cv in cap["covers"]]
            out.append("")
        return "\n".join(out)

    def _wbs(self):
        n = sum(len(re.findall(r"CAP-\d\d\.[a-z]", ids)) for ids, _ in self.baseline)
        rows = []
        for w2, bold, title, closes in self.wbs_rows:
            cell = f"**{w2}**" if bold else w2
            rows.append(f"| {cell} | A | {title} | implementation | engineer | STANDARD | — | 50 | {closes} |")
        out = [
            "---", "id: WAVE-2-WBS", "type: plan", "status: ACCEPTED", "---", "",
            "# Wave 2 (Strengthen) — work breakdown (a test tree)", "",
            "**Ids.** Wave 2 tickets are `W2-00` to `W2-05`, with `W2-03a`. Rows of the Wave 2 list keep their own ids.",
            "", "## 0. Rules for every ticket", "", "1. Every Wave 2 ticket closes through a clean `gov close`.", "",
            "## 1. Tickets", "",
            "| W2 | Track | Title | Class | Role | Profile | Depends on | est. LOC | Closes |",
            "|---|---|---|---|---|---|---|---|---|",
            *rows, "", "Bold rows are on the critical path (§3).", "",
            f"**The Contract's {n} Wave 2 items, by ticket.**",
            *[f"- {ids} → {t}." for ids, t in self.baseline], "",
            f"Two of the {n} sit in Track A because the adoption-readiness block needs them.", "",
        ]
        if self.adds_lite:
            out += [self.adds_lite, ""]
        out += ["## 2. Ticket cards", "", "Each card gives the profile and the allowed paths.", "",
                "## 5. Wave 2 exit criteria", "",
                f"7. **The Contract's {n} Wave 2 items, and Contract v4.2's lite items,** are each delivered by a "
                "closed ticket and cited by an acceptance test. The plan validator checks this both ways.", ""]
        return "\n".join(out)

    def _list(self):
        sev = ("high", "medium", "low", "info")
        total = sum(len(self.list_rows[s]) for s in sev)
        out = ["---", "id: WAVE-2-LIST", "type: plan", "status: ACCEPTED", "---", "",
               "# The Wave 2 list (a test tree)", "",
               "## 1. The adoption-readiness block", "", "### AR-1: decisions as records", "",
               "- **What:** a bounded context.", "- **Sources:** A F-M5.", "",
               "## 3. The rest of the list, by severity", "",
               f"{total} open items: " + ", ".join(f"{len(self.list_rows[s])} {s}" for s in sev) + ".", ""]
        for i, s in enumerate(sev, 1):
            stated = self.list_stated.get(s, len(self.list_rows[s]))
            out += [f"### 3.{i} {s} ({stated})", "", "| ID | Item | Owner | Closes when | Sources |",
                    "|---|---|---|---|---|"]
            out += [f"| {rid} | {item} | engineer | It is fixed. | B:{100 + k} |"
                    for k, (rid, item) in enumerate(self.list_rows[s])]
            out.append("")
        out += ["## 4. Closed or superseded in the record", "", "| ID | Item | Closed by | Sources |",
                "|---|---|---|---|", "| W2-C001 | An old item | L413 | B:413 |", ""]
        return "\n".join(out)

    def _triage(self):
        sev = ("high", "medium", "low", "info")
        cols = ("Wave 2", "Wave 3", "backlog", "Total")

        def col(disp):
            if disp == "Wave 3":
                return "Wave 3"
            if disp == "backlog":
                return "backlog"
            return "Wave 2"

        counts = {(s, c): 0 for s in sev + ("all",) for c in cols}
        for _, s, d in self.triage_rows:
            for key in ((s, col(d)), (s, "Total"), ("all", col(d)), ("all", "Total")):
                counts[key] += 1
        counts.update(self.triage_stated)
        out = ["---", "id: WAVE-2-TRIAGE", "type: plan", "status: ACCEPTED", "---", "",
               "# Wave 2 triage of the open list rows (a test tree)", "",
               f"Every one of the {counts[('all', 'Total')]} open rows is placed here.", "",
               "## Counts", "", "| Severity | Wave 2 | Wave 3 | backlog | Total |", "|---|---|---|---|---|"]
        out += [f"| {s} | " + " | ".join(str(counts[(s, c)]) for c in cols) + " |" for s in sev]
        out += ["| **all** | " + " | ".join(f"**{counts[('all', c)]}**" for c in cols) + " |", "",
                "**Rows per Wave 2 ticket:** W2-01 1 · W2-02 1 · W2-03a 1.", "",
                "## Rows on the Wave 1 WBS's Wave 2 outline but not on the list", "",
                "| Item | Title | Disposition | Reason |", "|---|---|---|---|",
                "| S0b2 G-13 | Framing-tolerant client | W2-02 | A retrieval component. |", "",
                "## Every open row", "", "| Row | Item | Severity | Disposition | Reason |", "|---|---|---|---|---|"]
        items = {rid: item for rows in self.list_rows.values() for rid, item in rows}
        out += [f"| {r} | {items.get(r, 'An item')} | {s} | {d} | A reason. |" for r, s, d in self.triage_rows]
        out.append("")
        return "\n".join(out)


def _w(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------------------------------------------------
# The two Contract versions
# --------------------------------------------------------------------------------------------------------------------

CIT_P_NAME = "W2-05-CIT-P.md"


def plan_v41():
    """A tree holding a 4.1 Contract: its Wave 2 items are the plan's baseline; no Wave 2 CIT-P."""
    return Plan()


def cit_p_text(entries, extra=""):
    """A CIT-P in W2-49's form: prose, then §6.1's proposed text as fenced YAML covers entries.

    ``entries`` is a list of (id, wave or None, item); an entry with no wave is written as W2-49's
    "- id: <id>   # unchanged, W3" form.
    """
    lines = ["  covers:"]
    for cid, wave, item in entries:
        if wave is None:
            lines.append(f"  - id: {cid}            # unchanged")
            continue
        lines += [f"  - id: {cid}", f"    item: '{item}'", "    source: Contract v3 Z1; DEC-900", f"    wave: {wave}"]
    block = "\n".join(lines)
    return f"""---
id: W2-05-CIT-P
type: change-impact-proposal
status: ACCEPTED
ticket: DAEO-t005 (W2-05)
decisions_carried: [DEC-900]
---

# W2-05 — Change-impact proposal (CIT-P) for Contract v4.2, lite

This change carries DEC-900 into the Contract. Release contents come into Wave 2 in a lite form: the manifest and
the file hashes. The rest stays in Wave 3, split into a new covers item.

## 2. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now, lite** | Contract 4.1 → 4.2 | one ticket |
| Defer | Contract stays 4.1 | one owner package |
| Re-baseline | Reopen the capability | the largest |
{extra}
## 6. The proposed v4.2 text

### 6.1 `contract.yaml`

Header:

```yaml
version: '4.2'
revised: '<the apply date>'
```

CAP-93 (`wave: W1` unchanged):

```yaml
{block}
```

### 6.3 Version

The version becomes 4.2.
"""


LITE_ITEM = "Release contents, lite: the release's own manifest and file hashes"
REST_ITEM = "Release contents beyond the lite manifest and file hashes: versions and notes"


def plan_v42():
    """A tree holding a 4.2 Contract: one Wave 3 item moved to Wave 2, lite, by a CIT-P; its rest split off in W3."""
    p = Plan()
    p.version = "4.2"
    p.change_log.append({"version": "4.2", "date": "2026-10-17",
                         "change": "W2-05 specification change (docs/changes/W2-05-CIT-P.md, W2-05-CIT-E.md). "
                                   "Carries DEC-900: release contents come into Wave 2, lite."})
    cv = p.cover("CAP-93.b")
    cv.update({"item": LITE_ITEM, "source": "Contract v3 Z1; DEC-900", "wave": "W2"})
    covers = p.cap("CAP-93")["covers"]
    covers.insert(covers.index(cv) + 2, _cover("CAP-93.d", "W3", REST_ITEM, "Contract v3 Z1; DEC-900"))
    p.adds_lite = "**Contract v4.2 adds, lite (DEC-900):** CAP-93.b (W2-04, W2-05). CAP-93.d stays in Wave 3."
    p.ticket("W2-05")["sources"].append("CAP-93.d")
    p.cit_p[CIT_P_NAME] = cit_p_text([("CAP-93.b", "W2", LITE_ITEM), ("CAP-93.c", None, ""),
                                      ("CAP-93.d", "W3", REST_ITEM)])
    return p


# --------------------------------------------------------------------------------------------------------------------
# Running the validator
# --------------------------------------------------------------------------------------------------------------------

class Result:
    def __init__(self, proc):
        self.returncode = proc.returncode
        self.stdout = proc.stdout
        self.stderr = proc.stderr
        self.status_lines = [l for l in proc.stdout.splitlines() if STATUS_START.match(l)]

    def __repr__(self):
        return f"exit {self.returncode}\n--- stdout ---\n{self.stdout}\n--- stderr ---\n{self.stderr[-3000:]}"

    def lines_for(self, name):
        found = []
        for line in self.status_lines:
            m = STATUS_LINE.match(line)
            if m and m.group(2) == name:
                found.append((m.group(1), m.group(3)))
        return found

    def check(self, name):
        """(status, reason) of the one line of check ``name``; fails the test if there is not exactly one."""
        found = self.lines_for(name)
        assert len(found) == 1, f"expected exactly one line for check {name!r}, found {len(found)}\n{self!r}"
        return found[0]

    def not_run(self):
        return [(m.group(2), m.group(3)) for m in map(STATUS_LINE.match, self.status_lines)
                if m and m.group(1) == "NOT RUN"]

    def fail_lines(self):
        return [l for l in self.status_lines if l.startswith("FAIL")]


def require_script():
    if not SCRIPT.is_file():
        pytest.fail(f"{SCRIPT.relative_to(WORKTREE)} does not exist yet: the Wave 2 plan validator is not written "
                    "(W2-51 not implemented)", pytrace=False)


def run_validator(root, home, extra_env=None, cwd=None):
    """Run ``python3 docs/plan/tools/validate_w2.py --root <root>`` with ``HOME`` set to ``home``.

    PYTHONPATH is this worktree's own ``src/`` (DEC-732). ``GOV_OS_WORKBENCH`` is removed unless a test sets it.
    The working directory is a temporary folder, never the repository.
    """
    require_script()
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_OS_WORKBENCH", "PYTHONPATH", "HOME")}
    env["HOME"] = str(home)
    env["PYTHONPATH"] = str(SRC)
    env.update(extra_env or {})
    Path(home).mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], cwd=str(cwd or home), env=env,
                          capture_output=True, text=True, timeout=180)
    return Result(proc)


def build_and_run(tmp_path, plan, extra_env=None):
    root = plan.write(tmp_path / "tree")
    return run_validator(root, tmp_path / "home", extra_env=extra_env)


def assert_fails_naming(res, name, *needles):
    """Check ``name`` is FAIL, its reason names every needle, and the run exits 1."""
    status, reason = res.check(name)
    assert status == "FAIL", f"check {name} should FAIL\n{res!r}"
    for n in needles:
        assert re.search(re.escape(n) + r"(?![A-Za-z0-9])", reason), \
            f"the reason of {name} should name {n!r}: {reason!r}\n{res!r}"
    assert res.returncode == 1, f"a run with a failing check exits 1\n{res!r}"


def assert_passes(res, *names):
    for name in names:
        status, reason = res.check(name)
        assert status == "PASS", f"check {name} should PASS\n{res!r}"
        assert reason.strip(), f"check {name} passes with no named reason\n{res!r}"
