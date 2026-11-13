p = "/home/usain/gov-os-worktrees/W2-158/src/gov/check/structural.py"
s = open(p).read()
start = s.index("def _declarations")
end = s.index("# ---- running a command")
new = '''class Decl(NamedTuple):
    rel: str  # the file, relative to the tree
    ident: str  # its id (its file name's stem when it states none or cannot be read)
    command: str | None
    problem: str | None  # why it cannot be run: unreadable, or no string `command`
    family: str | None  # its `family` field, None when unreadable or absent


def _declarations(tree: Path) -> dict[str, Decl]:
    """{key: declaration} over both layouts, template layout first. A file is keyed by its name's stem and by its
    ``id``; the first file for a key is the declaration (the template's, else the installed layout's)."""
    import yaml
    found: dict[str, Decl] = {}
    for directory in CHECKS_DIRS:
        folder = tree / directory
        for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else ():
            rel = f"{directory}/{path.name}"
            try:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as error:  # a file that cannot be read is its own family's notice, nothing else's
                found.setdefault(path.stem, Decl(rel, path.stem, None, f"{rel} cannot be read: {_short(error)}", None))
                continue
            document = document if isinstance(document, dict) else {}
            command, ident = document.get("command"), document.get("id")
            ident = ident if isinstance(ident, str) and ident else path.stem
            problem = None if isinstance(command, str) and command.strip() else f"{rel} has no string 'command'"
            decl = Decl(rel, ident, None if problem else command, problem, document.get("family"))
            for key in {path.stem, ident}:
                found.setdefault(key, decl)
    return found


def _skills(found: dict[str, Decl]) -> list[Decl]:
    """The skills family: every declaration whose family is ``skill regression`` (an unreadable file counts when its
    name starts ``skill-regression``), one per id, in id order."""
    chosen: dict[str, Decl] = {}
    for decl in found.values():
        if decl.family == SKILL_FAMILY or (decl.family is None and decl.ident.startswith("skill-regression")):
            chosen.setdefault(decl.ident, decl)
    return [chosen[ident] for ident in sorted(chosen)]


def _plan(tree: Path, with_portability: bool) -> list[tuple[str, list[tuple[str, Decl | None]]]]:
    """[(family, [(id, declaration, or None for none)])] in print order."""
    found = _declarations(tree)
    plan = [(family, [(ident, found.get(ident))]) for family, ident in FAMILIES]
    plan.append((SKILLS, [(decl.ident, decl) for decl in _skills(found)] or [("", None)]))
    plan.append(("portability", [(PORTABILITY_ID, found.get(PORTABILITY_ID) if with_portability else None)]))
    return plan


'''
s = s[:start] + new + s[end:]
s = s.replace("from pathlib import Path\n", "from pathlib import Path\nfrom typing import NamedTuple\n", 1)
s = s.replace("""            if entry is not None and entry[2] is not None:
                verdicts[family].append((False, entry[2]))
            elif entry is not None:
                jobs.append((family, ident, entry[1]))""", """            if entry is not None and entry.problem is not None:
                verdicts[family].append((False, entry.problem))
            elif entry is not None:
                jobs.append((family, ident, entry.command))""")
open(p, "w").write(s)
