#!/usr/bin/env python3
"""The domain skills' own check (W2-101, I1; DEC-959 items 4 and 5). Standard library only.

    python3 check_domain_skill.py <SKILL.md>

Prints one line per finding and exits 1, or prints `PASS` and exits 0:

    REFUSED <skill>: missing <section, part or point>
    REFUSED <skill>: permission line <n>: <text>

`<skill>` is the front matter's `name`; the area's list of named points is chosen from it, so the script works on a
copy in any folder. A file it cannot read, or with no front matter `name`, is a refusal (exit 1), never a pass; a name
with no point list is `REFUSED <name>: missing point list`. A usage error exits 64 with a line on stderr.

It checks: the template's eight `## ` sections, in order, Sources last; the five parts (Conventions, Pre-commit
checklist, Unit-test focus, Common mistakes, When to escalate), each a heading (`#` to `###`) or a labelled line
`**<Part>:**`; the area's named points, each a labelled line `**<Point>:**`; and any line of the file that begins
(after a list marker, backticks or a quote) with a permission-granting key and a colon. The skill validator
(`gov.check.skill_validator`) keeps the front-matter key and size checks.
"""
import re
import sys
from pathlib import Path

SECTIONS = ("When / not when", "Inputs", "Steps", "Done when", "Output and handover", "Escalation", "Never",
            "Sources")
PARTS = ("Conventions", "Pre-commit checklist", "Unit-test focus", "Common mistakes", "When to escalate")
POINTS = {
    "frontend": ("Accessibility", "State", "Browser support"),
    "ui-ux": ("User flows as scenarios",),
    "devops": ("Hermetic builds", "Pinned versions", "Rollback"),
}
USAGE = "usage: check_domain_skill.py <SKILL.md>"

# The keys are built from pieces, so that no file of a skill spells out a permission key it would then be read as
# holding (a grep of the skill's files for the keys finds none).
KEYS = "|".join(("allowed" + "[-_]" + "tools", "permission" + "s?", "al" + "low", "de" + "ny"))
LIST_MARKER = r"(?:(?:[-*+]|\d+[.)])\s+)?"
PERMISSION = re.compile(r"^\s*" + LIST_MARKER + r"[`\"'\s]*(?:" + KEYS + r")\s*:", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
SECTION_HEADING = re.compile(r"^##(?!#)\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def body_lines(lines):
    """(line number, text) of each line outside the front matter and outside a code fence."""
    start = 0
    if lines and lines[0].strip() == "---":
        for number, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                start = number + 1
                break
    fenced, found = False, []
    for number in range(start, len(lines)):
        if FENCE.match(lines[number]):
            fenced = not fenced
            continue
        if not fenced:
            found.append((number + 1, lines[number]))
    return found


def front_name(lines):
    """The front matter's `name`, or None."""
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        found = re.match(r"^name\s*:\s*(.*?)\s*$", line)
        if found:
            return found.group(1).strip("\"'").strip() or None
    return None


def label_pattern(text):
    """A labelled line `**<text>:**` (or `**<text>**:`), optionally a list item, case-insensitive."""
    return re.compile(r"^\s*" + LIST_MARKER + r"\*\*\s*" + re.escape(text) + r"\s*(?::\*\*|\*\*\s*:)", re.I)


def has_heading(lines, text):
    wanted = text.lower()
    for _, line in lines:
        found = HEADING.match(line)
        if found and len(found.group(1)) <= 3:
            title = found.group(2).rstrip(":").strip().lower()
            if title == wanted or title.startswith(wanted + " ") or title.startswith(wanted + ":"):
                return True
    return False


def has_label(lines, text):
    pattern = label_pattern(text)
    return any(pattern.match(line) for _, line in lines)


def has_part(lines, text):
    return has_heading(lines, text) or has_label(lines, text)


def section_findings(lines):
    """The sections absent or out of order, named by their heading text. The seven before Sources are kept in
    order by dropping the fewest (the longest increasing run stays); Sources must be the last `## ` heading."""
    titles = []
    for _, line in lines:
        found = SECTION_HEADING.match(line)
        if found:
            titles.append(found.group(1).strip().lower())
    names = [s.lower() for s in SECTIONS]
    refused = []
    position = {name: titles.index(name) for name in names if name in titles}
    ordered = [name for name in names[:-1] if name in position]
    best = {}  # best[i]: the longest increasing run of `ordered` ending at i
    for i, name in enumerate(ordered):
        run = [name]
        for j in range(i):
            if position[ordered[j]] < position[name] and len(best[j]) + 1 > len(run):
                run = best[j] + [name]
        best[i] = run
    kept = max(best.values(), key=len) if best else []
    for name, shown in zip(names[:-1], SECTIONS[:-1]):
        if name not in position or name not in kept:
            refused.append(shown)
    last = names[-1]
    if not titles or titles[-1] != last:
        refused.append(SECTIONS[-1])
    return refused


def check(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        print("REFUSED %s: cannot read the file" % path)
        return 1
    raw = text.splitlines()
    name = front_name(raw)
    if not name:
        print("REFUSED %s: no front matter name" % path)
        return 1
    lines = body_lines(raw)
    refused = ["REFUSED %s: missing %s" % (name, section) for section in section_findings(lines)]
    refused += ["REFUSED %s: missing %s" % (name, part) for part in PARTS if not has_part(lines, part)]
    if name in POINTS:
        refused += ["REFUSED %s: missing %s" % (name, point) for point in POINTS[name] if not has_label(lines, point)]
    else:
        refused.append("REFUSED %s: missing point list" % name)
    for number, line in enumerate(raw, 1):
        if PERMISSION.match(line):
            refused.append("REFUSED %s: permission line %d: %s" % (name, number, line.strip()))
    print("\n".join(refused) if refused else "PASS")
    return 1 if refused else 0


def main(argv):
    if len(argv) != 1 or argv[0].startswith("--"):
        print(USAGE, file=sys.stderr)
        return 64
    return check(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
