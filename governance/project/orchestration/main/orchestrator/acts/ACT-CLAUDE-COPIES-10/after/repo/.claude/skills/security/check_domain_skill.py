#!/usr/bin/env python3
"""The domain skills' check (DEC-959 items 4 and 5, DEC-957 Q5; W2-100). Standard library only.

    python3 check_domain_skill.py <path to a SKILL.md>

The skill (the area) is the `name` in the given file's front matter: backend, api, data or security. Prints on
stdout one line per failure, all of them, then exits 1; or `PASS` and exit 0:

    REFUSED <skill>: missing <section>            a level-2 section of the skill template is absent
    REFUSED <skill>: section order: <section>     a section out of the template's order, or any level-2 heading
                                                  after Sources
    REFUSED <skill>: missing <part>               one of the five labelled parts is absent
    REFUSED <skill>: missing <point>              one of the area's named points is absent from the body
    REFUSED <skill>: permission line <n>: <text>  a line that grants a permission (allowed-tools, permissions,
                                                  permission, allow ... as the line's first word, then a colon)
    REFUSED security: finding below P1 line <n>: <text>   (security only) a line with the word finding(s) and P2 or P3

A skill outside the four, an unreadable file or a missing argument prints one line (REFUSED or usage) and exits 64.
The skill states a method and grants nothing (CAP-24.b); this check only reads.
"""
import re
import sys
from pathlib import Path

SECTIONS = ("When / not when", "Inputs", "Steps", "Done when", "Output and handover", "Escalation", "Never", "Sources")
PARTS = ("Conventions", "Pre-commit checklist", "Unit-test focus", "Common mistakes", "When to escalate")
POINTS = {
    "backend": ("error handling", "idempotence", "migration"),
    "api": ("contract-first", "versioning", "backward compatibility"),
    "data": ("schema change", "migration", "rollback", "data quality"),
    "security": ("input check", "secrets never in code", "least privilege", "Prepare the Organization",
                 "Protect the Software", "Produce Well-Secured Software", "Respond to Vulnerabilities",
                 "any security finding is a P1"),
}
ALIASES = {"prepare the organization": ("prepare the organisation",)}  # the British spelling is accepted too
USAGE = "usage: check_domain_skill.py <path to a SKILL.md>"

HEADING = re.compile(r"^##(?!#)\s+(.*?)\s*$")
PERMISSION = re.compile(r"^\s*(?:[-*]\s+)?[*_`\"']*(allowed-tools|allowed_tools|allowedtools|permissions|permission|allow)"
                        r"[*_`\"']*:", re.I)
FINDING = re.compile(r"\bfindings?\b", re.I)
BELOW_P1 = re.compile(r"\bP[23]\b")


def split_front_matter(lines):
    """(front matter lines, body lines) of a file; no front matter gives ([], all lines)."""
    if lines and lines[0].strip() == "---":
        for number in range(1, len(lines)):
            if lines[number].strip() == "---":
                return lines[1:number], lines[number + 1:]
    return [], lines


def skill_name(front):
    for line in front:
        found = re.match(r"^name:\s*(.*?)\s*$", line)
        if found:
            return found.group(1).strip("\"'")
    return ""


def level_two_headings(lines):
    """The level-2 headings outside fenced code blocks, in order: their text, with a trailing colon dropped."""
    found, fenced = [], False
    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
        head = None if fenced else HEADING.match(line)
        if head:
            found.append(head.group(1).rstrip(":").strip())
    return found


def fold(text):
    """Lower case, a hyphen read as a space, runs of whitespace folded to one space."""
    return " ".join(text.lower().replace("-", " ").split())


def has_part(body, part):
    name = re.escape(part)
    heading = re.compile(r"^#{2,4}\s+%s\s*:?\s*$" % name, re.I)
    label = re.compile(r"^\s*(?:[-*]\s+)?[*_]*%s[*_]*:" % name, re.I)
    return any(heading.match(line) or label.match(line) for line in body)


def check(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    front, body = split_front_matter(lines)
    skill = skill_name(front)
    if skill not in POINTS:
        print("REFUSED %s: not one of backend, api, data, security" % (skill or "no name"))
        return 64
    out = []
    refuse = lambda text: out.append("REFUSED %s: %s" % (skill, text))
    headings = level_two_headings(body)
    known = {name.lower(): number for number, name in enumerate(SECTIONS)}
    for name in SECTIONS:
        if name.lower() not in [h.lower() for h in headings]:
            refuse("missing %s" % name)
    top, seen, after_sources = -1, set(), False
    for text in headings:
        number = known.get(text.lower())
        if (number is not None and number < top) or after_sources:
            if text not in seen:
                refuse("section order: %s" % text)
                seen.add(text)
        top = max(top, number if number is not None else -1)
        after_sources = after_sources or text.lower() == "sources"
    for part in PARTS:
        if not has_part(body, part):
            refuse("missing %s" % part)
    text = fold("\n".join(body))
    for point in POINTS[skill]:
        if not any(fold(form) in text for form in (point,) + ALIASES.get(point.lower(), ())):
            refuse("missing %s" % point)
    for number, line in enumerate(lines, 1):
        if PERMISSION.match(line):
            refuse("permission line %d: %s" % (number, line.strip()))
    if skill == "security":
        for number, line in enumerate(lines, 1):
            if FINDING.search(line) and BELOW_P1.search(line):
                out.append("REFUSED security: finding below P1 line %d: %s" % (number, line.strip()))
    print("\n".join(out) if out else "PASS")
    return 1 if out else 0


def main(argv):
    if len(argv) != 1 or not Path(argv[0]).is_file():
        print(USAGE)
        return 64
    try:
        return check(Path(argv[0]))
    except (OSError, UnicodeDecodeError):
        print("REFUSED: cannot read %s" % argv[0])
        return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
