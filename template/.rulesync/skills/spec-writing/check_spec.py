#!/usr/bin/env python3
"""The spec-writing skill's check (DEC-959 item 8; the form is in spec-form.md). Standard library only.

    python3 check_spec.py <spec.md>
    python3 check_spec.py --imports <folder>

Prints, on stdout: one `REFUSED <part>: <reason>` line per failed item (exit 1); `P1 Test data: <source> cannot
be secured` per unsecurable source, which also writes `<spec stem>.P1.md` beside the spec (exit 2 when nothing else
failed); `PASS` only when every item holds (exit 0). A usage error exits 64 with a line on stderr.
With --imports: `REFUSED import <part>: ...` for a marked part with no licence record or a licence not allowed.
"""
import re
import sys
from pathlib import Path

PARTS = ("Problem", "Users and scenarios", "Goals", "Non-goals", "KPIs", "Test data", "Out of scope",
         "Open questions", "Accepted by")
COLUMNS = ("source", "kind", "owner", "licence or recipe", "privacy", "secrets", "hidden half", "secured")
ALLOWED = ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0", "CC-BY-4.0")
EXTENSIONS = "py|js|ts|sh|yaml|yml|json|md|toml|txt|cfg|ini|html|css|sql|java|rb|php|csv|xml|cpp"
ABBREVIATIONS = {"e.g", "i.e", "a.m", "p.m", "u.s", "u.k", "ph.d", "vs"}
USAGE = "usage: check_spec.py <spec.md> | check_spec.py --imports <folder>"

CODE_SPAN = re.compile(r"`")
CALL = re.compile(r"(?<![\w.])[A-Za-z_]\w*\(")
PATH = re.compile(r"(?<!\w)[\w./-]*\w\.(?:%s)(?!\w)" % EXTENSIONS, re.I)
DOTTED = re.compile(r"(?<![\w.])[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+(?!\w)")
SNAKE = re.compile(r"(?<!\w)(?=\w*[A-Za-z])\w*_\w*(?!\w)")
KPI_LINE = re.compile(r"^\s*[-*]\s+\**K(\d+)\**:\s*(.*)$")
FAILS_LINE = re.compile(r"^\s*(?:[-*]\s+)?Fails if:\s*(.*)$", re.I)
MARKER = re.compile(r"<!--\s*imported:\s*(.*?)\s*-->")


def names_code(text):
    """The kind of code a line names (I3), or None. Plain prose (hyphens, `e.g.`, `1.5`, `a (b)`) names none."""
    if CODE_SPAN.search(text):
        return "code span"
    found = CALL.search(text)
    if found:
        return 'name( call "%s"' % found.group(0)
    found = PATH.search(text)
    if found:
        return 'path with an extension "%s"' % found.group(0)
    for found in DOTTED.finditer(text):
        parts = found.group(0).split(".")
        if found.group(0).lower() not in ABBREVIATIONS and any(len(p) >= 2 for p in parts):
            return 'dotted identifier "%s"' % found.group(0)
    found = SNAKE.search(text)
    if found:
        return 'snake_case identifier "%s"' % found.group(0)
    return None


def split_sections(text):
    sections, current = {}, None
    for line in text.splitlines():
        head = re.match(r"^##(?!#)\s+(.*?)\s*$", line)
        if head:
            current = head.group(1).strip().lower()
            sections.setdefault(current, [])
        elif current is not None:
            sections[current].append(line)
    return sections


def check_kpis(lines):
    kpis, refused = [], []
    for line in lines:
        kpi = KPI_LINE.match(line)
        if kpi:
            kpis.append([kpi.group(1), kpi.group(2), False])
            continue
        fails = FAILS_LINE.match(line)
        if fails and kpis and fails.group(1).strip():
            kpis[-1][2] = True
    if not kpis:
        return ["REFUSED KPIs: no K<n> line (- K<n>: <behaviour>)"]
    for number, behaviour, has_fails in kpis:
        kind = names_code(behaviour)
        if kind:
            refused.append("REFUSED KPIs: K%s names code (%s)" % (number, kind))
        if not has_fails:
            refused.append("REFUSED KPIs: K%s has no Fails if: line" % number)
    return refused


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_rows(lines):
    rows = [split_row(l) for l in lines if l.strip().startswith("|")]
    return [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r if c) or not any(r)]


def check_data(lines):
    """The Test data table: (REFUSED lines, the rows that cannot be secured)."""
    rows = table_rows(lines)
    if not rows:
        return ["REFUSED Test data: no table (columns: %s)" % " | ".join(COLUMNS)], []
    header = [c.lower().replace("license", "licence") for c in rows[0]]
    refused = ["REFUSED Test data: missing column %s" % c for c in COLUMNS if c not in header]
    if len(rows) < 2:
        return refused + ["REFUSED Test data: table has no rows"], []
    unsecured = []
    for number, row in enumerate(rows[1:], 1):
        def cell(name):
            return row[header.index(name)] if name in header and header.index(name) < len(row) else ""
        source = cell("source")
        if "source" in header and not source:
            refused.append("REFUSED Test data: row %d has no source" % number)
            continue
        label = source or "row %d" % number
        kind = cell("kind").lower()
        if "owner" in header and not cell("owner"):
            refused.append("REFUSED Test data: %s has no owner" % label)
        if "kind" in header and kind not in ("imported", "synthetic"):
            refused.append("REFUSED Test data: %s has kind '%s' (imported or synthetic)" % (label, cell("kind")))
        elif "licence or recipe" in header and not cell("licence or recipe"):
            refused.append("REFUSED Test data: %s has no %s" % (label, "licence" if kind == "imported" else "recipe"))
        if "hidden half" in header and cell("hidden half").lower() not in ("yes", "no", "n/a"):
            refused.append("REFUSED Test data: %s has no hidden half (yes, no or n/a)" % label)
        secured = cell("secured").lower()
        if "secured" in header and secured not in ("yes", "no"):
            refused.append("REFUSED Test data: %s has no secured value (yes or no)" % label)
        if secured == "no":
            unsecured.append({"source": label, "privacy": cell("privacy"), "secrets": cell("secrets"),
                              "licence or recipe": cell("licence or recipe")})
    return refused, unsecured


def write_p1(spec, unsecured):
    stated = lambda row: "; ".join("%s: %s" % (k, v) for k, v in row.items() if k != "source" and v) or "none stated"
    out = ["# P1 package: test data that cannot be secured", "", "Spec: %s" % spec.name, ""]
    for row in unsecured:
        out += ["## Source: %s" % row["source"], "",
                "Why it cannot be secured, as far as its row states: %s." % stated(row), "",
                "Options:",
                "- Secure it another way (a licence, a privacy review, secrets removed, a hidden half held apart) "
                "(cost: the owner's time and a delay to every KPI that needs it).",
                "- Replace it with synthetic data built from a recipe (cost: a build and a check that it still "
                "measures what the KPI needs).",
                "- Drop the KPI that needs it, with the owner's approval (cost: that KPI is no longer measured).",
                "", "Recommendation: replace it with synthetic data, unless the owner can secure the source another "
                "way sooner.", ""]
    spec.with_suffix(".P1.md").write_text("\n".join(out), encoding="utf-8")


def check_spec(path):
    sections = split_sections(path.read_text(encoding="utf-8"))
    refused, unsecured = [], []
    for part in PARTS:
        lines = sections.get(part.lower(), [])
        body = [l for l in lines if l.strip()]
        if not body:
            refused.append("REFUSED %s: missing" % part)
        elif part == "KPIs":
            refused += check_kpis(lines)
        elif part == "Test data":
            found, unsecured = check_data(lines)
            refused += found
    out = refused + ["P1 Test data: %s cannot be secured" % row["source"] for row in unsecured]
    if unsecured:
        write_p1(path, unsecured)
    print("\n".join(out) if out else "PASS")
    return 1 if refused else 2 if unsecured else 0


def read_records(path):
    """The small YAML form of imports.yaml: `imports:` and a list of part/source/version/licence mappings."""
    records = []
    if not path.is_file():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        line = re.sub(r"(^|\s)#.*$", "", line)
        entry = re.match(r"^\s*-\s+(\w+):\s*(.*)$", line)
        more = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if entry:
            records.append({})
        match = entry or more
        if match and records:
            records[-1][match.group(1)] = match.group(2).strip().strip("\"'")
    return records


def check_imports(folder):
    records = read_records(folder / "imports.yaml")
    parts = []
    for file in sorted(folder.rglob("*")):
        try:
            found = MARKER.findall(file.read_text(encoding="utf-8")) if file.is_file() else []
        except (OSError, UnicodeDecodeError):
            continue
        parts += [p for p in found if not (p.startswith("<") and p.endswith(">")) and p not in parts]
    refused = []
    for part in parts:
        mine = [r for r in records if r.get("part") == part and r.get("licence")]
        if not mine:
            refused.append("REFUSED import %s: no licence record" % part)
        elif not any(r["licence"].lower() in [a.lower() for a in ALLOWED] for r in mine):
            refused.append("REFUSED import %s: licence %s is not in the allowed list" % (part, mine[0]["licence"]))
    print("\n".join(refused) if refused else "PASS")
    return 1 if refused else 0


def main(argv):
    if len(argv) == 2 and argv[0] == "--imports" and Path(argv[1]).is_dir():
        return check_imports(Path(argv[1]))
    if len(argv) == 1 and not argv[0].startswith("--") and Path(argv[0]).is_file():
        return check_spec(Path(argv[0]))
    print(USAGE, file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
