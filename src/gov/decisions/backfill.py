"""The backfill proposer (W2-55; DEC-791 item 1, DEC-825 items 2 and 4): proposed tags for every register entry.

``python3 -m gov.decisions.backfill``, in a project root, prints a Markdown proposal for the register ``HEAD``
holds; it writes nothing. The proposal is a heuristic, and says so on every row:

- **lands in:** the files under the scope's folder (the kernel's ``template/governance/kernel/``, or the project's
  prompts and briefs) whose ``HEAD`` text cites the entry's id (DEC-825 item 1: a rule is stated with its id where
  it binds). Where none does, an entry in force is given its domain's home as a place to write it, and an entry
  superseded or done lands in ``none``.
- **scope:** ``kernel`` where only kernel files cite the id, ``repository`` where only the project's do; otherwise
  ``kernel`` where the entry names a kernel path or its title says kernel or skill, else ``repository``.
- **domain:** the closed list's domain whose keywords occur most often, the title counting five times the text.
- **status:** ``SUPERSEDED by DEC-<n>`` as the register reads it (``gov.decisions.register``), ``done`` for the
  status word DONE, ``Changed by: ...`` for every entry that changes, amends or refines it, else ``in force``.
- **amends and refines:** the ``**Amends:**`` and ``**Refines:**`` fields of the status lines (DEC-825 item 4).
- **sample:** ``random.Random(SEED).sample`` of the entries, in the register's order.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from gov.decisions.propagation import _searched
from gov.decisions.register import DOMAINS, SCOPES, ids, read

SEED, SAMPLE = 55, 40
KEYWORDS = {
    "guard": ("guard", "allowed path", "allowed_paths", "permission", "refus", "hook", "sandbox", "held-out",
              "protected"),
    "close": ("close", "closing", "acceptance", "merge"),
    "retrieval": ("retriev", "index", "embedding", "rerank", "lexical", "semantic", "search"),
    "context": ("context", "compact", "checkpoint", "resume here", "memory"),
    "adopt": ("adopt", "adoption", "migrat"),
    "launch": ("launch", "session", "model", "effort", "settings", "worktree"),
    "checks": ("check", "test", "doctor", "canary", "validator", "gate"),
    "plan": ("plan", "wave", "wbs", "slot", "schedule", "keystone", "re-plan"),
    "roles": ("role", "orchestrator", "lead", "auditor", "engineer", "test designer", "worker"),
    "records": ("register", "record", "trailer", "commit", "store"),
    "release": ("release", "version", "install", "package", "publish", "licen"),
}
HOMES = {  # where an entry in force that no file states yet is proposed to be written (DEC-851)
    "repository": "governance/project/prompts/w2-orchestrator.md",
    "guard": "template/governance/kernel/hooks/pretooluse.py", "retrieval": "template/governance/kernel/skills/"
    "retrieval/SKILL.md", "context": "template/governance/kernel/skills/checkpoint/SKILL.md",
    "adopt": "template/governance/kernel/skills/adopt/SKILL.md", "plan": "template/governance/kernel/skills/planning/"
    "SKILL.md", "roles": "template/governance/kernel/roles/orchestrator.md", "checks": "template/governance/kernel/"
    "skills/audit/SKILL.md", "records": "template/governance/kernel/skills/change/SKILL.md",
    "release": "template/governance/kernel/skills/change/SKILL.md",
}
KERNEL_HOME = "template/governance/kernel/skills/orchestration/SKILL.md"  # close and launch, and any other
_RELATION = re.compile(r"\*\*(Amends|Refines):\*\*([^·]*)")


def _domain(entry: dict) -> tuple[str, str]:
    title, text = entry["title"].lower(), entry["span"].lower()
    scores = {domain: 5 * sum(title.count(word) for word in words) + sum(text.count(word) for word in words)
              for domain, words in KEYWORDS.items()}
    if not any(scores.values()):
        return "plan", "no keyword: plan, the domain of the project's own steering"
    best = max(DOMAINS, key=lambda domain: (scores[domain], -DOMAINS.index(domain)))
    top = sorted((domain for domain in DOMAINS if scores[domain]), key=lambda domain: -scores[domain])[:2]
    return best, ", ".join(f"{domain} {scores[domain]}" for domain in top)


def propose(root: Path) -> str:
    """The proposal's Markdown for the register at ``root``'s ``HEAD``."""
    from gov.store.loader import _git

    root = Path(root)
    register = read(root)
    if register is None:
        return "# W2-55 backfill\n\nThe path map names no register: nothing to propose.\n"
    base = _git(root, "log", "-1", "--format=%H", "HEAD", "--", register["path"]).decode("ascii").strip()[:12]
    cited: dict[str, dict[str, list]] = {}
    for path, text in _searched(root, register["path"]):
        scope = next((name for name, where in SCOPES.items() if path.startswith(where)), None)
        if scope == "repository" and not path.startswith(("governance/project/prompts/", "governance/project/briefs/")):
            scope = None
        for record_id in ids(text) if scope else ():
            cited.setdefault(record_id, {}).setdefault(scope, []).append(path)
    relations = [(entry["id"], name.lower(), old) for entry in register["entries"]
                 for name, text in _RELATION.findall(entry["status_line"]) for old in ids(text)
                 if old != entry["id"]]
    changers = {old: list(new) for old, new in register["changed"].items()}
    for new, _, old in relations:
        if new not in changers.setdefault(old, []):
            changers[old].append(new)

    rows, proposed = [], {}
    for entry in register["entries"]:
        record_id = entry["id"]
        domain, why = _domain(entry)
        where = cited.get(record_id, {})
        if len(where) == 1:
            scope = next(iter(where))
            scope_why = f"only {scope} files cite it"
        else:
            kernelish = SCOPES["kernel"] in entry["span"] or re.search(r"\b(kernel|skill)", entry["title"], re.I)
            scope = "kernel" if kernelish else "repository"
            scope_why = ("files of both scopes cite it; " if where else "no file cites it; ") + \
                        ("it names a kernel path or its title says kernel or skill" if kernelish else
                         "it names no kernel path")
        if record_id in register["superseded"]:
            successor = (register["superseded"][record_id] or ["DEC-?"])[0]
            status = f"SUPERSEDED by {successor}"
        elif entry["status"] == "DONE":
            status = "done"
        elif changers.get(record_id):
            status = "Changed by: " + ", ".join(changers[record_id])
        else:
            status = "in force"
        proposed[record_id] = (domain, scope, status)
        places = where.get(scope, [])
        if places:
            lands, lands_why = ", ".join(places[:3]), "the files of its scope that cite its id"
        elif status.startswith("SUPERSEDED") or status == "done":
            lands, lands_why = "none", "not in force"
        else:
            lands = HOMES["repository"] if scope == "repository" else HOMES.get(domain, KERNEL_HOME)
            lands_why = "no file of its scope cites it yet: its domain's home, where it is to be written"
        reason = f"heuristic: domain by keywords ({why}); scope: {scope_why}; lands in: {lands_why}"
        rows.append(f"| {record_id} | {domain} | {scope} | {lands} | {status} | {reason.replace('|', '/')} |")

    drawn = sorted(random.Random(SEED).sample(range(len(register["entries"])), min(SAMPLE, len(rows))))
    lines = [
        "# W2-55 backfill: proposed tags for every register entry (a proposal; nothing is applied)",
        "",
        f"A proposal for the owner's review (DEC-791 item 1, DEC-825 items 2 and 4), for the register "
        f"`{register['path']}` as the commit `{base}` last changed it ({len(rows)} entries). Nothing here is written to the register: the "
        "orchestrator applies the accepted backfill after the owner accepts it. Every row is a heuristic proposal, "
        "and its reason says which rule gave it.",
        "",
        "## How this proposal was made",
        "",
        "By the script `src/gov/decisions/backfill.py`, run in the project root:",
        "`PYTHONPATH=src python3 -m gov.decisions.backfill > docs/research/W2-55-backfill.md`. It reads `HEAD` only, "
        "and the same commit gives the same file. Its rules (the module's docstring states them in full):",
        "",
        "- **domain:** the domain of the closed list whose keywords occur most often in the entry, its title counting "
        "five times its text (a heuristic: an entry about several domains gets the one with most words);",
        "- **scope:** `kernel` where only files under `template/governance/kernel/` cite the id, `repository` where "
        "only the project's prompts and briefs do; otherwise `kernel` where the entry names a kernel path or its "
        "title says kernel or skill, else `repository`;",
        "- **lands in:** the files of the scope that cite the id (up to three); where none does, `none` for an entry "
        "superseded or done, and its domain's home for an entry in force (a place to write it, not a place that "
        "states it yet);",
        "- **status:** `SUPERSEDED by DEC-<n>` where the register marks it superseded or another entry supersedes it "
        "by id alone; `done` for the status word DONE; `Changed by: ...` for the entries that change, correct, "
        "settle, reverse, withdraw, partly supersede, amend or refine it; else `in force`. One-offs whose action is "
        "finished and whose status word is not DONE are not detected: the owner's sample is where they show.",
        "",
        "## Proposed tags",
        "",
        "| id | domain | scope | lands in | status | reason |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
        "## Amends and refines",
        "",
        f"The {len(relations)} relations the status lines record in `**Amends:**` and `**Refines:**` fields, which "
        "DEC-825 item 4 left for this ticket, with the status note proposed for the old entry (a part is amended or "
        "refined, so no status word changes).",
        "",
        *[f"- {new} {verb} {old} — proposed status note for {old}: `Changed by: {new}`"
          for new, verb, old in relations],
        "",
        "## Sample for the owner's review",
        "",
        f"Drawn by `random.Random({SEED}).sample(range({len(rows)}), {SAMPLE})` over the entries in the register's "
        "order, then sorted: the same seed over the same register draws the same entries. For each drawn entry the "
        "owner checks: (1) the domain is what the entry is about; (2) the scope (kernel-wide, or this repository "
        "only); (3) the lands-in file states the rule, or is the right place to write it; (4) the status note "
        "(in force, done, superseded by, changed by). Proposed rule: with 36 of 40 right the backfill is accepted "
        "with the owner's corrections; with fewer, the rules are revised and the sample is drawn again.",
        "",
        "| id | domain | scope | status |",
        "|---|---|---|---|",
        *[f"| {record_id} | {' | '.join(proposed[record_id])} |"
          for record_id in (register["entries"][index]["id"] for index in drawn)],
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    sys.stdout.write(propose(Path.cwd()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
