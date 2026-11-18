"""``gov discover`` as a command module (W2-36, DAEO-w19l; the convention is in ``gov.cli.main``).

- ``gov discover <words...> [--profile P] [--type T]...`` opens discovery: a draft spec in the spec-writing form,
  its proposal and readiness records, and one discovery ticket (the words are joined by one space, quoted or not).
- ``gov discover --check <change>`` runs the spec check: exit 0 with ``PASS`` and the open required readiness rows
  (``OPEN <key> <gap ticket or UNLINKED>``), exit 1 with its ``REFUSED`` lines.
- ``gov discover --generate <change>`` makes one linked gap ticket per required open row not yet linked.
- ``gov discover --ticket <change> --paths <glob>...`` makes the feature ticket of a spec that passes the check.

It writes in the working tree and commits nothing, and makes no model or network call: where judgement is needed it
names the ``gov brief`` of the session that does it. The text form prints plain lines; ``--json`` the envelope.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

HELP = "open discovery from an idea, check a spec, make gap tickets and the feature ticket"
CLASS = "act"
ACT_PATHS = ("openspec/changes/**", ".tickets/**")
CHILD_EXIT_CODE = True  # the text form prints its own lines; --json returns the result as the envelope's
NOT_READY = "DISCOVER_SPEC_NOT_READY"


def add_arguments(parser) -> None:
    from gov.readiness.checker import EXTRA, PROFILES

    parser.add_argument("words", nargs="*", metavar="<words>", help="the idea, in plain language")
    parser.add_argument("--profile", choices=PROFILES, help="the readiness profile (default LITE)")
    parser.add_argument("--type", action="append", default=[], choices=sorted(EXTRA), metavar="<type>",
                        help="a capability type of the readiness schema; repeatable; STANDARD needs one")
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--check", metavar="<change>", help="check the spec of a change")
    which.add_argument("--generate", metavar="<change>", help="make the gap tickets of a change's open rows")
    which.add_argument("--ticket", metavar="<change>", help="make the feature ticket of a change whose spec passes")
    parser.add_argument("--paths", action="append", default=[], metavar="<glob>", help="the feature ticket's paths")


def _error(code: str, message: str, details: dict | None = None):
    from gov.cli.errors import GovError

    return GovError(code, message, details or {})


def _brief(role: str, ticket: str) -> str:
    from gov.discover.tickets import BRIEF

    return BRIEF.format(role=role, ticket=ticket)


def _folder(root: Path, change: str) -> Path:
    from gov.readiness.checker import CHANGES_REL

    folder = root / CHANGES_REL / change
    if not re.fullmatch(r"[^/\\]+", change) or change in (".", "..") or not (folder / "spec.md").is_file():
        raise _error("DISCOVER_CHANGE_NOT_FOUND", f"{change}: no such change ({CHANGES_REL}/{change}/ holds no spec.md)",
                     {"change": change})
    return folder


def _record(root: Path, folder: Path) -> dict:
    from gov.util.frontmatter import of_file

    front = of_file(folder / "proposal.md") or {}
    if front.get("type") != "specification" or not isinstance(front.get("id"), str):
        raise _error("READINESS_INVALID", f"{folder.name}: proposal.md holds no specification record",
                     {"change": folder.name})
    return front


def _passing(root: Path, change: str) -> tuple[Path, dict, str]:
    """``(folder, proposal front matter, spec text)`` of a change whose spec passes the check; else
    ``DISCOVER_SPEC_NOT_READY`` with the refused lines."""
    from gov.discover import check

    folder = _folder(root, change)
    text = (folder / "spec.md").read_text(encoding="utf-8")
    refused = check.refusals(root, text)
    if refused:
        raise _error(NOT_READY, f"{change}: the spec is not ready: " + "; ".join(refused),
                     {"change": change, "refused": refused})
    return folder, _record(root, folder), text


def open_discovery(root: Path, args) -> dict:
    from gov.discover import draft, tickets
    from gov.readiness.checker import CHANGES_REL

    words = draft.words_of(args.words)
    change = draft.change_name(words)
    if not change:
        raise _error("DISCOVER_NO_WORDS", "gov discover needs the idea in words (more than stop words)")
    profile, types = args.profile or "LITE", list(dict.fromkeys(args.type))
    if profile == "STANDARD" and not types:
        raise _error("DISCOVER_NO_TYPE", "a STANDARD specification declares at least one --type")
    folder = root / CHANGES_REL / change
    if folder.exists():
        raise _error("DISCOVER_EXISTS", f"{CHANGES_REL}/{change}/ already exists: nothing is written", {"change": change})
    spec_rel = f"{CHANGES_REL}/{change}/spec.md"
    spec = draft.spec(words, profile, types, args.profile is None, draft.sources(root, change),
                      draft.memory(root, words), draft.row_names(root))
    title, fields, body = tickets.discovery(change, words, profile, spec_rel)
    ticket = tickets.create(root, title)
    try:
        tickets.write(root, ticket, fields, body)
        folder.mkdir(parents=True)
        (folder / "proposal.md").write_text(draft.proposal_text(change, words, profile, types, ticket), encoding="utf-8")
        (folder / "readiness.yaml").write_text(draft.readiness_text(root), encoding="utf-8")
        (folder / "spec.md").write_text(spec, encoding="utf-8")
    except BaseException:  # never half-written
        tickets.remove(root, [ticket])
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return {"change": change, "specification": f"SPEC-{change}", "ticket": ticket, "spec": spec_rel,
            "briefs": [_brief("product-spec", ticket)]}


def check_change(root: Path, change: str) -> dict:
    from gov.readiness import checker

    folder, front, _ = _passing(root, change)
    report = checker.judge(root, front["id"], folder / "proposal.md", front)
    return {"change": change, "specification": front["id"], "passed": True, "open": report["open"]}


def generate(root: Path, change: str) -> dict:
    import yaml

    from gov.discover import draft, tickets
    from gov.readiness import checker

    folder = _folder(root, change)
    front = _record(root, folder)
    spec_id = front["id"]
    report = checker.judge(root, spec_id, folder / "proposal.md", front)
    rows = {row["n"]: row for row in yaml.safe_load((folder / "readiness.yaml").read_text(encoding="utf-8"))["rows"]}
    todo = [row for row in report["open"] if not tickets.exists(root, row["gap_ticket"])]
    known = {row["n"]: row["gap_ticket"] for row in report["open"] if tickets.exists(root, row["gap_ticket"])}
    made = {}
    try:
        for row in todo:
            made[row["n"]] = tickets.create(root, f"Settle readiness row {row['n']} {row['key']} of {change}")
        known.update(made)
        names, keys = draft.row_names(root), {row["key"]: n for n, row in rows.items()}
        for row in todo:
            if row["key"] == "acceptance_tests":  # tests come last (DEC-103)
                wanted = {n for n in known if n != row["n"]}
            else:
                named = [keys.get(dep, dep) for dep in rows[row["n"]].get("depends_on") or []]
                wanted = {n for n in named if n in known and n != row["n"]}
            title, fields, body = tickets.gap(change, spec_id, row, names.get(row["n"], row["key"]),
                                              sorted({known[n] for n in wanted}), report["profile"])
            tickets.write(root, made[row["n"]], fields, body)
        if made:
            _link(folder / "readiness.yaml", made)
    except BaseException:
        tickets.remove(root, list(made.values()))
        raise
    done = [{"n": row["n"], "key": row["key"], "ticket": made[row["n"]], "role": draft.class_of(row["key"])[1],
             "class": draft.class_of(row["key"])[0], "brief": _brief(draft.class_of(row["key"])[1], made[row["n"]])}
            for row in todo]
    return {"change": change, "specification": spec_id, "tickets": done, "briefs": [item["brief"] for item in done]}


def _link(path: Path, links: dict[int, str]) -> None:
    """Each row's ``gap_ticket`` written in its line of ``readiness.yaml``; nothing else in the file changes. A file
    whose rows are not one flow mapping per line is written again whole."""
    import yaml

    text = path.read_text(encoding="utf-8")
    expected = yaml.safe_load(text)
    for row in expected["rows"]:
        row["gap_ticket"] = links.get(row["n"], row.get("gap_ticket"))
    lines = text.split("\n")
    for n, ticket in links.items():
        at = next((i for i, line in enumerate(lines) if re.match(rf"\s*-\s*\{{\s*n:\s*{n}\s*,", line)), None)
        if at is not None and "gap_ticket:" in lines[at]:
            lines[at] = re.sub(r"gap_ticket:\s*[^,}]*", f"gap_ticket: {ticket}", lines[at])
    edited = "\n".join(lines)
    path.write_text(edited if yaml.safe_load(edited) == expected
                    else yaml.safe_dump(expected, sort_keys=False, width=1000), encoding="utf-8")


def feature(root: Path, change: str, paths: list[str]) -> dict:
    from gov.discover import check, tickets

    if not paths:
        raise _error("DISCOVER_NO_PATHS", "--ticket needs the feature ticket's paths: --paths <glob>")
    folder, front, text = _passing(root, change)
    module = check.skill(root)
    verify = check.verifies(text, module)
    kpis = [(n, behaviour, fails, verify[n]) for n, behaviour, fails in check.kpis(text, module)]
    heading = re.search(r"^# (.+)$", (folder / "proposal.md").read_text(encoding="utf-8"), re.M)
    title, fields, body = tickets.feature(change, front["id"], heading.group(1) if heading else change,
                                          front.get("profile"), paths, kpis, check.bullets(text, "Non-goals", module))
    ticket = tickets.create(root, title)
    try:
        fields["acceptance_tests"] = {"path": f"tests/acceptance/{ticket}/", "author": "independent-test-designer"}
        tickets.write(root, ticket, fields, body)
    except BaseException:
        tickets.remove(root, [ticket])
        raise
    return {"change": change, "specification": front["id"], "ticket": ticket,
            "briefs": [_brief("independent-test-designer", ticket), _brief("engineer", ticket)]}


def act(root: Path, args) -> dict:
    if args.check:
        return check_change(root, args.check)
    if args.generate:
        return generate(root, args.generate)
    if args.ticket:
        return feature(root, args.ticket, args.paths)
    return open_discovery(root, args)


def _lines(args, result: dict) -> list[str]:
    if args.check:
        return ["PASS", *(f"OPEN {row['key']} {row['gap_ticket']}" for row in result["open"])]
    if args.generate:
        return [f"{len(result['tickets'])} gap tickets made for {result['change']}",
                *(f"{item['key']}: {item['ticket']} ({item['class']}, {item['role']})" for item in result["tickets"]),
                *result["briefs"]]
    if args.ticket:
        return [f"feature ticket {result['ticket']} made for {result['change']}", *result["briefs"]]
    return [f"discovery opened: {result['change']} ({result['specification']})", f"spec: {result['spec']}",
            f"ticket: {result['ticket']}", *result["briefs"]]


def run(root, args, config):
    from gov.cli.errors import GovError

    root = Path(root)
    try:
        result = act(root, args)
    except GovError as error:
        if args.check and error.code == NOT_READY and not args.json:
            print("\n".join(error.details["refused"]))
            return 1
        raise
    if args.json:
        return result
    print("\n".join(_lines(args, result)))
    return 0
