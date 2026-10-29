"""W2-58, item 2 -- (a) secrets and (b) the held-out material's contents stay refused, for every role.

KPI failure: "Each of (a) to (d) still refuses, by every read route an honest
agent takes in ordinary work (DEC-801); no write rule widens; a guard error
still fails closed." KPI success 4: "secrets stay refused [DEC-820 (a)]", "the
held-out material's contents refused [DEC-820 (b)]".

(a) Secrets and keys, by name: ``.env`` and ``.env.<anything>`` at any depth,
``*.pem``, ``*.key``, ``config/secrets*``, and any file under ``~/.ssh/``. Every
content read that names the file is refused, for every role, auditors
included. A search that starts at a folder above one is not refused for its
sake. Every such file here is a stand-in written by the fixture, in a
temporary project and a temporary HOME.

(b) Each path the held-out list names stays refused as today (DEC-162,
DEC-215): any call that names it or reaches it through a relative path,
``..``, ``~``, ``$HOME`` or a symbolic link. A broken held-out list still stops
every call (DEC-218). The list here names a stand-in folder under the
temporary HOME.
"""

from __future__ import annotations

import os

import pytest

import w2_58_support as s

LINK_REL = "docs/peek"     # a symbolic link in the project to the stand-in held-out folder


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    box = s.make_sandbox(tmp_path_factory.mktemp("refused"))
    project = s.make_project(box, base=False)
    os.symlink(box.held_out, project / LINK_REL)
    return s.World(box, project)


# --------------------------------------------------------------------------
# (a) Secrets, by name
# --------------------------------------------------------------------------

def _secret_routes(world, rel):
    copy = world.sandbox.tmpdir / "copy-of-a-secret"
    return [
        s.read(world.path(rel)),
        s.grep(path=world.path(rel), pattern="STAND_IN"),
        s.bash(f"cat {rel}"),
        s.bash(f"head -n 1 {rel}"),
        s.bash(f"sed -n 1p {rel}"),
        s.bash(f"grep STAND_IN {rel}"),
        s.bash(f"git show HEAD:{rel}"),
        s.bash(f"cp {rel} {s.q(copy)}"),
    ]


ROUTE_IDS = ("Read", "Grep-path", "cat", "head", "sed-n", "grep-file", "git-show-rev-path", "cp")


@pytest.mark.parametrize("index", range(len(ROUTE_IDS)), ids=ROUTE_IDS)
@pytest.mark.parametrize("role", s.ROLES)
def test_a_dot_env_file_is_refused_by_every_route_to_every_role(world, role, index):
    call = _secret_routes(world, ".env")[index]
    s.assert_refused(world.ask(call, role), call, f"{role}: ")


@pytest.mark.parametrize("rel", s.SECRET_FILES)
@pytest.mark.parametrize("role", (s.ENGINEER, s.AUDITOR))
@pytest.mark.parametrize("route", ("Read", "cat"))
def test_every_secret_name_is_refused(world, role, rel, route):
    """``.env``, ``.env.<anything>`` at any depth, ``*.pem``, ``*.key``, ``config/secrets*``."""
    call = s.read(world.path(rel)) if route == "Read" else s.bash(f"cat {rel}")
    s.assert_refused(world.ask(call, role), call, f"{role}: ")


def _ssh_routes(world):
    return [
        s.read(world.sandbox.ssh / "id_ed25519"),
        s.bash(f"cat {s.q(world.sandbox.ssh / 'id_ed25519')}"),
        s.bash("cat ~/.ssh/id_ed25519"),
        s.bash("cat $HOME/.ssh/config"),
        s.grep(path=world.sandbox.ssh / "config", pattern="STAND"),
    ]


SSH_IDS = ("Read-absolute", "cat-absolute", "cat-tilde", "cat-HOME", "Grep-path")


@pytest.mark.parametrize("index", range(len(SSH_IDS)), ids=SSH_IDS)
@pytest.mark.parametrize("role", (s.ENGINEER, s.AUDITOR, s.ORCHESTRATOR))
def test_a_file_under_the_home_ssh_folder_is_refused(world, role, index):
    call = _ssh_routes(world)[index]
    s.assert_refused(world.ask(call, role), call, f"{role}: ")


@pytest.mark.parametrize("rel", s.SECRET_NEIGHBOURS)
@pytest.mark.parametrize("role", (s.ENGINEER, s.AUDITOR))
def test_the_neighbours_of_secrets_are_readable(world, role, rel):
    """The rule is by name: an ordinary file beside a secret, or with a near name, is read as any file."""
    for call in (s.read(world.path(rel)), s.bash(f"cat {rel}")):
        s.assert_allowed(world.ask(call, role), call, f"{role}: ")


@pytest.mark.parametrize("role", (s.PRODUCT_SPEC, s.AUDITOR, s.RESEARCH))
def test_a_search_that_starts_above_a_secret_is_not_refused_for_its_sake(world, role):
    """DEC-820 (a): a search from a folder above a secret is open (the index already keeps secrets out)."""
    for call in (s.bash(f"grep -rn {s.WORD} config/"), s.grep(path=world.path("certs")),
                 s.bash(f"grep -rn {s.WORD} services/"), s.bash("ls certs/")):
        s.assert_allowed(world.ask(call, role), call, f"{role}: ")


# --------------------------------------------------------------------------
# (b) The held-out material's contents
# --------------------------------------------------------------------------

def _held_out_routes(world):
    held = world.sandbox.held_out
    rel_from_project = os.path.relpath(held, world.project)
    copy = world.sandbox.tmpdir / "copy-of-held-out"
    return [
        s.read(held / "answers.md"),
        s.grep(path=held, pattern="zqxw"),
        s.glob_call("*", path=held),
        s.bash(f"cat {s.q(held / 'answers.md')}"),
        s.bash("cat ~/held-out-material/answers.md"),
        s.bash("cat $HOME/held-out-material/answers.md"),
        s.bash(f"cat {rel_from_project}/answers.md"),
        s.read(world.path(LINK_REL) / "answers.md"),
        s.bash(f"cat {LINK_REL}/answers.md"),
        s.bash(f"ls {s.q(held)}"),
        s.bash(f"grep -rn zqxw {s.q(held)}"),
        s.bash(f"cp {s.q(held / 'answers.md')} {s.q(copy)}"),
    ]


HELD_IDS = ("Read", "Grep", "Glob", "cat-absolute", "cat-tilde", "cat-HOME", "cat-dot-dot", "Read-through-link",
            "cat-through-link", "ls", "grep-r", "cp")


@pytest.mark.parametrize("index", range(len(HELD_IDS)), ids=HELD_IDS)
@pytest.mark.parametrize("role", s.ROLES)
def test_the_held_out_material_stays_refused_by_every_route(world, role, index):
    """DEC-162, DEC-215 as today, for every role, auditors included."""
    call = _held_out_routes(world)[index]
    s.assert_refused(world.ask(call, role), call, f"{role}: ")


BROKEN_LISTS = {
    "not-yaml": f"{s.HELD_OUT_KEY}: [unclosed\n  - : :\n",
    "missing-key": "other_key:\n- /somewhere/else\n",
    "not-a-list": f"{s.HELD_OUT_KEY}: just-a-word\n",
}


@pytest.mark.parametrize("name", sorted(BROKEN_LISTS))
@pytest.mark.parametrize("role", (s.ENGINEER, s.AUDITOR))
def test_a_broken_held_out_list_still_stops_every_call(sandbox, role, name):
    """DEC-218: a missing key or a broken file makes the guard fail closed."""
    project = s.make_project(sandbox, base=False)
    s.write(project / s.HELD_OUT_LIST_REL, BROKEN_LISTS[name])
    world = s.World(sandbox, project)
    for call in (s.read(project / "README.md"), s.bash("ls src"), s.grep(path=project / "docs")):
        s.assert_refused(world.ask(call, role), call, f"{role}, held-out list {name}: ")
