#!/usr/bin/env python3
"""Generate the Contract's derived forms from `docs/contract/contract.yaml`, the authority (DEC-971 item 2).

    python3 docs/contract/tools/gen_contract.py --check     # regenerate in memory; non-zero if a file differs
    python3 docs/contract/tools/gen_contract.py --write     # rewrite the Contract text (from "## 1. Counts") and the records
    python3 docs/contract/tools/gen_contract.py --baseline <git-ref>   # reproduce the files at a commit (the proof)

What it makes:
  * `docs/contract/capabilities/<id>.md`: one record per capability and per covers item (62 + 215 = 277);
  * `docs/contract/master-rules/MR-n.md`: one record per master rule (6);
  * the Contract text from its "## 1. Counts" heading to the end: the counts table, §2 envelope, §3 master rules,
    §4 capabilities. Everything above that heading (front matter, title, version table, precedence and fields
    paragraphs) is hand-written and is kept as it is; `--check` also compares the version table with `change_log`.

The generator was first run on the v4.4 files and reproduced the 277 records, the 6 master-rule records and the
Contract text byte for byte (`--baseline <the commit before v5>`), then used for v5. The prose of the §1 notes
paragraph lives in `docs/contract/tools/counts_notes.md`.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CON = ROOT / "docs/contract"
YAML = CON / "contract.yaml"
NOTES = CON / "tools/counts_notes.md"
WAVES = ("W1", "W2", "W3", "NONE")
CLASSES = ("KEPT", "LITE", "DROP")


def q(s: str) -> str:
    """YAML single-quoted scalar, as `yaml.safe_dump` writes the records' titles."""
    return yaml.safe_dump(s, allow_unicode=True, default_flow_style=True, width=1 << 30).splitlines()[0].rstrip()


def frontmatter_title(title: str) -> str:
    dumped = yaml.safe_dump({"title": title}, allow_unicode=True, width=1 << 30, default_flow_style=False)
    return dumped.rstrip("\n").split("\n", 1)[0] if "\n" not in dumped.rstrip("\n") else dumped.rstrip("\n")


def version_line(c: dict) -> str:
    n = c["id"].rsplit("-v", 1)[1]
    return f"Contract v{n}, version {c['version']}"


def wave_text(cap: dict) -> str:
    w = cap["wave"]
    if cap["disposition"]["class"] == "DROP":
        return "NONE (dropped)"
    return f"{w} ({cap['wave_note']})" if cap.get("wave_note") else w


def disposition_text(cap: dict) -> str:
    d = cap["disposition"]
    if d["class"] == "LITE":
        return f"LITE — lite form: {d['lite_form']}"
    if d["class"] == "DROP":
        return f"DROP — {d['non_goal']}"
    if d.get("note"):
        return f"KEPT ({d['note']})"
    return "KEPT"


# ------------------------------------------------------------------ records
def record(rid: str, typ: str, title: str, depends: str, body: str, name: str) -> tuple[str, str]:
    head = f"---\nid: {rid}\ntype: {typ}\nstatus: ACCEPTED\nstate_class: DERIVED\n"
    head += yaml.safe_dump({"title": title}, allow_unicode=True, width=1 << 30, default_flow_style=False)
    head += f"depends_on:\n- {depends}\n---\n\n# {rid}: {title}\n\n"
    return name, head + body


def records(c: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    auth = f"Generated from `docs/contract/contract.yaml` ({version_line(c)}), which is the authority"
    for cap in c["capabilities"]:
        covers = cap.get("covers") or []
        body = (f"{auth}; this record exists so that the id resolves (DEC-614).\n\n"
                f"- **Outcome:** {cap['outcome']}\n- **Acceptance:** {cap['acceptance']}\n"
                f"- **Wave:** {cap['wave'] if cap['disposition']['class'] != 'DROP' else 'NONE'}\n"
                f"- **Disposition:** {cap['disposition']['class']}\n")
        if covers:
            body += "- **Covers:** " + ", ".join(cv["id"] for cv in covers) + "\n"
        n, t = record(cap["id"], "capability", cap["title"], c["id"], body, f"capabilities/{cap['id']}.md")
        out[n] = t
        for cv in covers:
            cbody = (f"A covers item of {cap['id']} ({cap['title']}). {auth} (DEC-614).\n\n"
                     f"- **Item:** {cv['item']}\n- **Wave:** {cv['wave']}\n")
            n, t = record(cv["id"], "capability", cv["item"], cap["id"], cbody, f"capabilities/{cv['id']}.md")
            out[n] = t
    for mr in c["master_rules"]:
        body = (f"A master rule of the Charter (v{c.get('charter', '5')}, §4). {auth}; this record exists so that the id "
                f"resolves.\n\n- **Text:** {mr['text_source']}\n- **Acceptance:** {mr['acceptance']}\n")
        n, t = record(mr["id"], "specification", mr["title"], c["id"], body, f"master-rules/{mr['id']}.md")
        out[n] = t
    return out


# ------------------------------------------------------------------ the Contract text
def counts(c: dict) -> str:
    cell = {(w, k): 0 for w in WAVES for k in CLASSES}
    for cap in c["capabilities"]:
        w = cap["wave"] if cap["disposition"]["class"] != "DROP" else "NONE"
        cell[(w, cap["disposition"]["class"])] += 1
    rows = ["| Wave | KEPT | LITE | DROP | Total |", "|---|---|---|---|---|"]
    for w in WAVES:
        vals = [cell[(w, k)] for k in CLASSES]
        rows.append(f"| {w} | " + " | ".join(map(str, vals)) + f" | {sum(vals)} |")
    tot = [sum(cell[(w, k)] for w in WAVES) for k in CLASSES]
    rows.append("| **All** | " + " | ".join(map(str, tot)) + f" | {sum(tot)} |")
    return "\n".join(rows)


def decs(d) -> str:
    return ", ".join(d) if isinstance(d, list) else str(d)


def envelope(c: dict) -> str:
    names = {"scale_envelope": "Scale envelope", "ram_budget": "RAM budget", "token_budget": "Token budget",
             "boundary": "Boundary", "loop_budget": "Loop budget", "tool_installs": "Tool installs"}
    lines = []
    for key, label in names.items():
        if key in c["envelope"]:
            e = c["envelope"][key]
            lines.append(f"- **{label}** ({decs(e['decision'])}). {e['statement']}")
    for key, e in c["envelope"].items():  # a clause the table above does not name keeps its key as label
        if key not in names:
            lines.append(f"- **{key.replace('_', ' ').capitalize()}** ({decs(e['decision'])}). {e['statement']}")
    return "\n".join(lines)


def master_rules(c: dict) -> str:
    rows = ["| Id | Rule | Acceptance | Provider | Dev scenarios | Decisions |", "|---|---|---|---|---|---|"]
    for m in c["master_rules"]:
        rows.append(f"| {m['id']} | {m['title']} | {m['acceptance']} | {', '.join(m['provider'])} | "
                    f"{', '.join(m['scenarios']['dev'])} | {', '.join(m['sources'])} |")
    return "\n".join(rows)


def scen(cap: dict) -> str:
    s = cap["scenarios"]
    dev = ", ".join(s.get("dev") or []) or "—"
    qual = ", ".join(s.get("qual") or []) or "—"
    if s.get("dev_unlisted_in_matrix"):
        dev += f" (+{s['dev_unlisted_in_matrix']} not listed in the matrix row)"
    if s.get("qual_unlisted_in_matrix"):
        qual += f" (+{s['qual_unlisted_in_matrix']} not listed in the matrix row)"
    return f"dev {dev} · qual {qual}"


def capability(cap: dict) -> str:
    drop = cap["disposition"]["class"] == "DROP"
    out = [f"### {cap['id']} — {cap['title']}", "",
           f"- **Outcome:** {cap['outcome']}", f"- **Acceptance:** {cap['acceptance']}",
           f"- **Wave:** {wave_text(cap)}",
           f"- **Provider:** {'none (non-goal)' if drop else ', '.join(cap['provider'])}",
           f"- **Disposition:** {disposition_text(cap)}", f"- **Sources:** {'; '.join(cap['sources'])}", "- **Covers:**"]
    for cv in cap.get("covers") or []:
        line = f"  - `{cv['id']}` [{cv['wave']}] {cv['item']} — {cv['source']}"
        if cv.get("provider"):
            line += " · delivered by " + ", ".join(cv["provider"])
        out.append(line)
    out.append(f"- **Scenarios:** {scen(cap)}")
    return "\n".join(out)


def body(c: dict) -> str:
    notes = NOTES.read_text(encoding="utf-8").rstrip("\n")
    parts = ["## 1. Counts", "", counts(c), "", notes, "", "## 2. Envelope and boundary", "", envelope(c), "",
             "## 3. Master-rule clauses", "", MR_INTRO(c), "", master_rules(c), "", "## 4. Capabilities", ""]
    parts.append("\n\n".join(capability(cap) for cap in c["capabilities"]))
    return "\n".join(parts) + "\n"


def MR_INTRO(c: dict) -> str:
    if "charter" not in c:  # the Contract before v5: the Charter's rules were verbatim
        return ("The rule texts are in Charter v5 §4, verbatim from architecture v0.3 §1A. Each clause below is a contract "
                "item with one acceptance check.")
    return (f"The rule texts are in Charter v{c['charter']} §4, from architecture v0.3 §1A; EMERGENCY-2 reworded the checks of "
            "MR-1 to MR-4. Each clause below is a contract item with one acceptance check.")


def contract_text(c: dict, existing: str) -> str:
    cut = existing.index("\n## 1. Counts")
    return existing[: cut + 1] + body(c)


def change_table_matches(c: dict, existing: str) -> list[str]:
    bad = []
    for e in c["change_log"]:
        row = f"| {e['version']} | {e['date']} | {e['change']} |"
        if row not in existing:
            bad.append(e["version"])
    return bad


def md_path(c: dict) -> Path:
    return CON / f"CONTRACT_v{c['id'].rsplit('-v', 1)[1]}.md"


def show(ref: str, rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def baseline(ref: str) -> int:
    """Reproduce the files at a commit from that commit's contract.yaml: the proof that the generator is faithful.

    At the v4.4 commit 275 records say "version 4.3" (CAP-44.m's leftovers: only CAP-44 and CAP-44.m say 4.4), so
    those two are the only records compared as generated; the rest are compared with 4.4 read as 4.3. The Contract
    text is compared from its "## 1. Counts" heading; the yaml carries three providers the text lacks (W1-35 on CAP-28
    and CAP-28.a, W1-26 on CAP-30.e: DEC-971 item 2), the only differences expected."""
    c = yaml.safe_load(show(ref, "docs/contract/contract.yaml"))
    ok = True
    for name, text in sorted(records(c).items()):
        if c["version"] == "4.4" and name not in ("capabilities/CAP-44.md", "capabilities/CAP-44.m.md"):
            text = text.replace("version 4.4", "version 4.3")
        if show(ref, f"docs/contract/{name}") != text:
            ok = False
            print("  differs:", name)
    old = show(ref, "docs/contract/CONTRACT_v4.md")
    new = contract_text(c, old)
    diff = [(i, a, b) for i, (a, b) in enumerate(zip(old.splitlines(), new.splitlines())) if a != b]
    print(f"records and master rules identical: {ok}; Contract text lines that differ: {len(diff)} of {len(old.splitlines())}")
    for _, a, b in diff:
        print("   ", a[-60:], "->", b[-60:])
    return 0 if ok and len(diff) <= 3 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="regenerate in memory; non-zero if a file differs")
    ap.add_argument("--write", action="store_true", help="rewrite the records and the Contract text")
    ap.add_argument("--baseline", metavar="REF", help="reproduce the files at a commit (the generator's proof)")
    a = ap.parse_args()
    if a.baseline:
        return baseline(a.baseline)
    c = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    md = md_path(c)
    existing = md.read_text(encoding="utf-8")
    want = records(c)
    want[md.name] = contract_text(c, existing)
    diff = []
    for name, text in sorted(want.items()):
        path = CON / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            diff.append(name)
    have = {p.name for p in (CON / "capabilities").glob("*.md")} | {p.name for p in (CON / "master-rules").glob("*.md")}
    stray = sorted(have - {Path(n).name for n in want})
    bad = change_table_matches(c, existing)
    if a.check:
        print(f"records {sum(1 for n in want if n.startswith('capabilities/'))}, master rules "
              f"{sum(1 for n in want if n.startswith('master-rules/'))}; differing files: {len(diff)}; "
              f"stray records: {len(stray)}; version rows missing from the text: {bad or 'none'}")
        for n in diff[:20]:
            print("  differs:", n)
        return 1 if diff or stray or bad else 0
    if a.write:
        for name, text in want.items():
            (CON / name).write_text(text, encoding="utf-8")
        for s in stray:
            for d in ("capabilities", "master-rules"):
                if (CON / d / s).exists():
                    (CON / d / s).unlink()
        print("written:", len(want), "files; removed", len(stray))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
