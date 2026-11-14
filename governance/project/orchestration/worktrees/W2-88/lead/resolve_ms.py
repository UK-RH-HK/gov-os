from pathlib import Path
p = Path("/home/usain/gov-os-worktrees/W2-88/src/gov/adopt/memory_sets.py")
t = p.read_text(encoding="utf-8")
a = t.index("<<<<<<< HEAD\n"); b = t.index(">>>>>>> w2/integrate\n") + len(">>>>>>> w2/integrate\n")
new = '''def _toplevel(out: Path) -> str:
    """The git top level of ``out`` (or of its nearest folder that exists), else that folder: A9 writes inside the
    repository."""
    here = Path(out).resolve()
    while not here.exists():
        here = here.parent
    try:
        done = subprocess.run(["git", "-C", str(here), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError:
        return str(here)
    return done.stdout.strip() if done.returncode == 0 and done.stdout.strip() else str(here)


def _gitleaks() -> str:
    """The scanner for step 6's line: the absolute path ``shutil.which`` finds when A9 runs (cron's PATH lacks
    ``~/.local/bin``; review round 1 R1), else the placeholder the operator fills in."""
    found = shutil.which("gitleaks")
    return os.path.abspath(found) if found else "<path to gitleaks>"


def _cron(root: Path | None) -> str:
    """The weekly wrapper for step 6's line: its path where Gov OS ships it (``fabric.shipped``, never the package's
    ``parents[3]``), else the placeholder the operator fills in. A9 never reads the script; the line is text."""
    from gov.adopt import fabric
    from gov.cli.errors import GovError

    try:
        return str(fabric.shipped(CRON, root))
    except GovError:
        return f"<path to Gov OS>/{CRON}"


def walls_act(out: Path, *, sets_root: str, audit: str, made: dict, blind: list[str], root: Path | None = None,
              repo=None) -> Path:
    """Write ``<out>/memory-audit/ACT-WALLS/``: the walls' template copy (as Gov OS ships it, found by
    ``fabric.shipped``, refused ``SHIPPED_FILE_MISSING`` where it is nowhere), the sets root's spec (mode 0700), the
    approved list with the three variant briefs, the path map's hidden globs, the refresh the operator installs and the
    repository's weekly cron line (text for its owner's operator, W2-187 I11). ``repo`` defaults to the git top level of
    ``out``. Nothing is applied: no folder is made at the sets root, no path map is changed and no cron table is read or
    written."""
    from gov.adopt import fabric

    walls = fabric.shipped(WALLS, root)
    repo = str(repo) if repo is not None else _toplevel(out)
'''
t = t[:a] + new + t[b:]
t = t.replace("{GOV_OS / CRON} ", "{_cron(root)} ")
assert "GOV_OS" not in t and "<<<<<<<" not in t and ">>>>>>>" not in t
p.write_text(t, encoding="utf-8")
print("resolved")
