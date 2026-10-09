"""Support code for the DEC-548 cases of W1-02: second names, copies outside the project, refusals beyond the order.

Everything here is a stand-in in a temporary folder, as in
``w1_02_protected_support``: no file of this repository is opened, and the
held-out file's path is never spelled (it comes from the guard's own module
through ``w1_02_protected_support.HELD_REL``).

``make_world`` builds one session project with both stand-in files and, around
it, **copies** of the two files at the same project-relative paths under other
folders. A copy at ``<P>/<the file's project-relative path>`` has the *site*
``<P>``:

=============  ==========================================================  ==============
site           ``<P>``                                                     copies
=============  ==========================================================  ==============
``own``        the session's project (the rule as built)                   both files
``sibling``    another checkout: a git repository beside the project        both files
``plain``      a folder that is no repository, beside the project           both files
``worktree``   a git worktree of the session's project, beside it           both files
``nested``     ``template/`` below the session's project root               both files
``home``       the ``HOME`` of the hook's environment (a stand-in)          settings file
=============  ==========================================================  ==============

Every decision is asked of the hook, run as a process on a hook input.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

import w1_02_protected_support as protected
import w1_02_support as support

SETTINGS = "settings-file"
HELD = "held-out-file"
FILES = sorted(protected.PROTECTED)
NESTED_REL = "template"
SCRATCH_REL = support.SCRATCH_REL
# A file two folders below the folder that holds the user-level settings file (where the harness keeps transcripts).
HOME_BELOW_REL = ".claude/projects/w1-02-stand-in/notes.md"

# An engineer ticket whose allowed_paths name both stand-in files: a role that may write either file today.
WRITER_TICKET_ID = "DAEO-zz97"

# Who makes a call: the eleven actors of the revision, and three named for what they may write.
ACTORS = dict(protected.ACTORS)
ACTORS.update({
    "engineer-who-may-write-the-file": (support.ENGINEER, WRITER_TICKET_ID, None),
    "engineer-who-may-not-write-the-file": (support.ENGINEER, support.TICKET_ID, None),
})
MAY_WRITE = ("orchestrator", "engineer-who-may-write-the-file")
MAY_NOT_WRITE = ("engineer-who-may-not-write-the-file", "no-role")

RULE_RE = re.compile(r"\bDEC-(508|525|548)\b")


@dataclass(frozen=True)
class Site:
    """A folder ``<P>`` that holds a copy of one or both files at the project-relative path."""
    name: str
    root: Path
    names: tuple

    def rel(self, name):
        return protected.PROTECTED[name]

    def path(self, name):
        return self.root / protected.PROTECTED[name]

    def folder_rel(self, name):
        return os.path.dirname(protected.PROTECTED[name])

    def folder(self, name):
        return self.root / self.folder_rel(name)

    def neighbour_rel(self, name):
        """Another file in the folder that holds the copy."""
        other = "notes.md" if name == SETTINGS else "bootstrap.md"
        return f"{self.folder_rel(name)}/{other}"

    def neighbour(self, name):
        return self.root / self.neighbour_rel(name)

    def base(self, name):
        return os.path.basename(protected.PROTECTED[name])

    def ext(self, name):
        return os.path.splitext(protected.PROTECTED[name])[1]


@dataclass(frozen=True)
class World:
    base: Path
    project: Path
    sandbox: support.Sandbox
    listed: Path           # what the session project's stand-in held-out file lists
    copy_listed: Path      # what every copy's stand-in deny line and stand-in held-out file list
    sites: dict            # site name -> Site
    links: dict            # (site name, file name) -> a symbolic link to that copy, outside every site

    def site(self, name):
        return self.sites[name]

    def secrets(self, site, name):
        """What a refusal for the copy ``name`` of ``site`` must not carry: a path, a folder, a value of the file."""
        at = self.sites[site]
        listed = self.listed if site == "own" else self.copy_listed
        values = [str(at.path(name)), str(at.folder(name)), str(listed), protected.HELD_REL,
                  os.path.basename(protected.HELD_REL), protected.SETTINGS_REL]
        if site != "own":
            values.append(str(at.root))
        if name == SETTINGS:
            values.extend(protected.settings_secrets(listed))
        return tuple(values)


def _put_copies(site, listed):
    for name in site.names:
        path = site.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if name == SETTINGS:
            protected.write_settings(site.root, protected.stand_in_settings(listed))
        else:
            path.write_text(f"{protected.CONFIG_KEY}:\n- {listed}\n", encoding="utf-8")
        if not site.neighbour(name).exists():
            site.neighbour(name).write_text("VALUE = 1\n", encoding="utf-8")


def _commit(directory, message):
    support.git(directory, "add", "-A")
    support.git(directory, "commit", "-q", "-m", message)


def make_world(base):
    """Build the session project, the copies around it and the links to them."""
    base = Path(base)
    guarded = protected.make_guarded(base)
    project, sandbox = guarded.project, guarded.sandbox

    copy_listed = sandbox.elsewhere / "w1-02-stand-in-held-out-of-a-copy"
    copy_listed.mkdir()

    ticket = project / ".tickets" / f"{WRITER_TICKET_ID}.md"
    ticket.write_text(support.ticket_text(ticket_id=WRITER_TICKET_ID, wbs_id="W1-97", role=support.ENGINEER,
                                          allowed_paths=(protected.SETTINGS_REL, protected.HELD_REL)),
                      encoding="utf-8")

    sites = {"own": Site("own", project, tuple(FILES))}
    nested = Site("nested", project / NESTED_REL, tuple(FILES))
    _put_copies(nested, copy_listed)
    sites["nested"] = nested
    _commit(project, "a ticket that names both stand-in files, and copies of them below template/")

    # Another checkout of the project's commit, beside it: a git worktree.
    worktree = base / "worktree-of-the-project"
    support.git(project, "worktree", "add", "-q", str(worktree), "-b", "w1-02-stand-in-worktree", "HEAD")
    sites["worktree"] = Site("worktree", worktree, tuple(FILES))

    sibling = Site("sibling", base / "sibling-checkout", tuple(FILES))
    for rel in ("README.md", "src/app.py"):
        (sibling.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (sibling.root / rel).write_text("VALUE = 1\n", encoding="utf-8")
    _put_copies(sibling, copy_listed)
    support.git(sibling.root, "init", "-q", "-b", "main")
    _commit(sibling.root, "a sibling checkout with copies of both stand-in files")
    sites["sibling"] = sibling

    plain = Site("plain", base / "a-folder-that-is-no-repository", tuple(FILES))
    _put_copies(plain, copy_listed)
    sites["plain"] = plain

    home = Site("home", sandbox.home, (SETTINGS,))
    _put_copies(home, copy_listed)
    below = home.root / HOME_BELOW_REL
    below.parent.mkdir(parents=True)
    below.write_text("VALUE = 1\n", encoding="utf-8")
    sites["home"] = home

    links = {}
    for site in ("sibling", "home"):
        for name in sites[site].names:
            link = sandbox.elsewhere / f"link-to-the-{name}-of-the-{site}-site"
            link.symlink_to(sites[site].path(name))
            links[(site, name)] = link
    return World(base, project, sandbox, guarded.listed, copy_listed, sites, links)


# --------------------------------------------------------------------------
# One decision
# --------------------------------------------------------------------------

def ask(world, tool_name, tool_input, who, cwd=None):
    """The guard's decision on one call by ``who``; ``cwd`` is the hook input's working folder (the project if left out).

    The hook's ``HOME`` is the stand-in home of the world, so ``~`` and ``$HOME`` name it.
    """
    role, ticket, subagent = ACTORS[who] if isinstance(who, str) else who
    data = support.payload(world.project, tool_name, tool_input, world.sandbox, subagent)
    if cwd is not None:
        data["cwd"] = str(cwd)
    return support.run_hook_raw(world.project, json.dumps(data), world.sandbox, role, ticket)


def ask_bash(world, command, who, cwd=None):
    return ask(world, "Bash", support.bash_tool_input(command), who, cwd)


def fill(world, site, name, text):
    """A command or a path template for the copy ``name`` of ``site``.

    ``{rel}`` the file's project-relative path, ``{abs}`` the copy, ``{dir}`` and
    ``{absdir}`` its folder, ``{base}`` its name, ``{ext}`` its extension,
    ``{root}`` the site ``<P>``, ``{nrel}`` and ``{nabs}`` another file of the
    folder, ``{project}`` the session's project, ``{scratch}`` the project's
    scratch folder (relative), ``{tmp}`` the hook's temporary folder,
    ``{elsewhere}`` a folder outside every site, ``{link}`` a symbolic link to
    the copy (the ``sibling`` and ``home`` sites); ``{here}``, ``{heredir}`` and
    ``{nhere}`` the copy, its folder and the other file as relative paths from
    the session's project; ``{dirbase}`` the folder's own name; ``{top}`` the
    first folder below ``<P>`` on the way to the copy.
    """
    at = world.sites[site]
    return text.format(rel=at.rel(name), abs=at.path(name), dir=at.folder_rel(name), absdir=at.folder(name),
                       base=at.base(name), ext=at.ext(name), root=at.root, nrel=at.neighbour_rel(name),
                       nabs=at.neighbour(name), project=world.project, scratch=SCRATCH_REL,
                       tmp=world.sandbox.tmpdir, elsewhere=world.sandbox.elsewhere,
                       link=world.links.get((site, name), ""),
                       here=os.path.relpath(at.path(name), world.project),
                       heredir=os.path.relpath(at.folder(name), world.project),
                       nhere=os.path.relpath(at.neighbour(name), world.project),
                       dirbase=os.path.basename(at.folder_rel(name)),
                       top=at.root / at.rel(name).split("/")[0])


def assert_refused_by_the_rule(result, what):
    """The read rule's own decision: ``deny``, exit code 0, and a reason that names the rule's decision.

    A denial by the allow-list (a write the role may not make) names no decision
    of the rule and does not pass: a second name is refused as a read, for every role.
    """
    protected.assert_refused_by_rule(result, what)
    reason = protected.reason_of(result)
    assert RULE_RE.search(reason), (
        f"{what} was denied, but not as a read of the two files: the reason names none of DEC-508, DEC-525, DEC-548"
    )


def assert_says_nothing_of_the_file(result, world, site, name, what):
    """A refusal names the rule and the decision: no path, no folder, no value of the file."""
    reason = protected.reason_of(result)
    assert re.sub(r"\bDEC-\d+\b", "", reason).strip(" .:;()[]"), f"the refusal of {what} names a decision and no rule"
    said = protected.output_of(result)
    shown = [index for index, secret in enumerate(world.secrets(site, name)) if secret in said]
    # The values are not put in the message: a failure must not print what a refusal must not print.
    assert not shown, (
        f"the refusal of {what} carries {len(shown)} value(s) it must not (positions {shown} of World.secrets): "
        f"a path, a folder, or a value of the file"
    )


def assert_as_today(result, allowed, what):
    """A write is decided as it is today: allowed, or denied (by whichever rule denies it today)."""
    if allowed:
        protected.assert_allowed(result, what)
    else:
        assert result.decision == "deny", f"{what} was not denied: decision={result.decision} exit={result.returncode}"
