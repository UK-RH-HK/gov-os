"""The sandbox block a launched worker gets, read from its ``--settings`` (DEC-1112 (1): today's launcher sandbox,
not generated from the path map; the reranker's one socket, DEC-1035 (2); S11's one log file, the designer's choice).

S2: the write list stays today's: the session's temp folder (DEC-159) and its own run folder (DEC-728), with the
literal deny rules for .gov-runtime/ outside the session's scratch and, for every role but the test designer,
tests/acceptance/**; no entry comes from the ticket's allowed paths [changed, DEC-1112 (1)].
S3: an allowed path that is a name pattern ... no sandbox entry is made from any allowed path [changed, DEC-1112 (1)].
S8: the sandbox block allows that one Unix socket path and no other; the path comes from the same setting the service
uses, never a pattern wider than it [DEC-1035, P-W2-112-T2 (a)].
S9: nothing else in the sandbox widens: no other Unix socket, no network port, allowUnsandboxedCommands false and
strictAllowlist as today; sandbox_faults still refuses any other change [DEC-1035].
S11 (choice: one log file): the sandbox's write list widens by at most that one log file [DEC-1097 (8)].
F1: the sandbox's write list holds anything beyond today's ...; /tmp/gov-cbm-<uid> is on the write list; an allowed
path widened with nothing naming it.
F2: a launch whose sandbox cannot be built starts; a refusal the launcher makes today no longer refuses.
F4: a sandboxed session that can open any Unix socket or port beyond the reranker's one path.

Every case launches workers on a fixture project with the stand-in CLI and reads the ``--settings`` it was handed;
``sandbox_faults`` is called directly on those settings, changed one key at a time.
"""

from __future__ import annotations

import copy
import json
import os

import pytest
import yaml

import w2_56_support as s
import w2_56_sandbox_support as sb

TODAYS_SANDBOX_KEYS = {"enabled", "failIfUnavailable", "allowUnsandboxedCommands", "network", "filesystem"}
NETWORK_KEYS = {"strictAllowlist", "allowedDomains", "allowUnixSockets"}
FILESYSTEM_KEYS = {"allowWrite", "denyWrite", "denyRead"}    # the two deny keys narrow, never widen


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    sb.project(box, extra={".gov-runtime/findings.jsonl": "", ".gov-runtime/snapshots/one.json": "{}\n",
                           ".gov-runtime/scratch/notes.md": "scratch\n"})
    return box


def _launch(box, role, ticket=None):
    return s.run_launch(box, role, (ticket or s.TICKET_OF[role]).tk)


def _research_hosts():
    data = yaml.safe_load((s.REPO_ROOT / s.ALLOWLIST_REL).read_text(encoding="utf-8")) or {}
    return sorted(set(data.get("hosts") or []))


# ---------------------------------------------------------------- S2, F1: the write list stays today's

@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s2_the_write_list_is_the_temp_folder_the_run_folder_and_at_most_the_reranker_log(box, role):
    launch = _launch(box, role)
    entries = sb.write_list(sb.started(launch))
    tmpdir, log = sb.session_tmpdir(launch), sb.norm(sb.reranker_log(box.home))
    assert tmpdir in [os.path.realpath(entry) for entry in entries], (
        f"the session's temp folder {tmpdir} is not on its write list: {entries}")
    runs = sb.run_folders(box, entries)
    assert len(runs) == 1, f"the write list does not hold exactly one run folder of the session's own: {entries}"
    beyond = [entry for entry in entries if os.path.realpath(entry) != tmpdir and entry not in runs and entry != log]
    assert not beyond, f"the write list holds more than today's (and S11's one log file): {beyond}"
    cbm = f"/tmp/gov-cbm-{os.getuid()}"
    assert not [entry for entry in entries if sb.under(entry, cbm)], f"{cbm} is on the write list (DEC-799 item 2)"
    assert not [entry for entry in entries if sb.under(entry, box.project)], (
        f"the write list names the worktree or a path in it: {entries}")


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s2_the_literal_deny_rules_for_gov_runtime_and_the_acceptance_tests_stay(box, role):
    deny = sb.started(_launch(box, role)).get("permissions", {}).get("deny", [])
    root = os.path.realpath(box.project)
    for name in ("findings.jsonl", "snapshots"):
        assert f"Edit(/{root}/.gov-runtime/{name})" in deny, (
            f"no literal deny rule for .gov-runtime/{name}: {[r for r in deny if '.gov-runtime' in r]}")
    assert not [rule for rule in deny if rule in (f"Edit(/{root}/.gov-runtime/scratch)",
                                                  f"Edit(/{root}/.gov-runtime/scratch/**)")], (
        "the session's scratch is denied")
    acceptance = f"Edit(/{root}/tests/acceptance)"
    if role == s.TEST_DESIGNER:
        assert acceptance not in deny, "the test designer is denied the acceptance tests"
    else:
        assert acceptance in deny, f"no literal deny rule for tests/acceptance for {role}"


# ---------------------------------------------------------------- S3, F1: nothing from the allowed paths

def test_s3_no_sandbox_entry_is_made_from_any_allowed_path(box):
    plain, pattern = (sb.started(s.run_launch(box, s.ENGINEER, ticket.tk)) for ticket in (s.T, sb.PATTERN))

    def shape(settings):
        data = copy.deepcopy(settings)
        files = data.get("sandbox", {}).get("filesystem", {})
        if isinstance(files, dict) and isinstance(files.get("allowWrite"), list):
            files["allowWrite"] = len(files["allowWrite"])   # the temp and run folders differ by session and ticket
        data.pop("env", None)
        return data

    assert shape(plain) == shape(pattern), (
        "the sandbox block or the deny rules change with the ticket's allowed paths:\n"
        f"{json.dumps(shape(plain))[:900]}\n{json.dumps(shape(pattern))[:900]}")
    text = json.dumps(pattern)
    named = [path for path in sb.PATTERN.allowed if path.rstrip("*/") in text]
    assert not named, f"the settings name an allowed path of the ticket: {named}"


# ---------------------------------------------------------------- S11 (choice), F1: the one log file

@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it(box, role):
    log = sb.reranker_log(box.home)
    s.set_plan(box, [sb.python_step("log", "import json, os\np = sys.argv[1]\n"
                                    "print(json.dumps({'file': os.path.isfile(p) and not os.path.islink(p)}))\n",
                                    args=[log])])
    entries = sb.write_list(sb.started(_launch(box, role)))
    assert sb.norm(log) in entries, f"the reranker's log {log} is not on the write list: {entries}"
    assert sb.step_json(box, "log")["file"], f"the reranker's log {log} is not a file when the session starts"


def test_f1_a_reranker_log_that_is_a_link_widens_nothing(box):
    target = box.elsewhere / "target.txt"
    target.write_text("kept\n", encoding="utf-8")
    link = sb.reranker_cache(box.home) / "rerank.log"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)
    launch = _launch(box, s.ENGINEER)
    if not sb.refused(launch):
        entries = sb.write_list(sb.started(launch))
        assert not [entry for entry in entries if sb.under(entry, target) or entry == sb.norm(link)], (
            f"the write list follows a link at the reranker's log to {target}: {entries}")
    assert target.read_text(encoding="utf-8") == "kept\n", "the link's target was changed"


# ---------------------------------------------------------------- S8, F4: the reranker's one socket

@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s8_the_sandbox_block_allows_the_reranker_socket_and_no_other(box, role):
    sockets = sb.unix_sockets(sb.started(_launch(box, role)))
    expected = sb.norm(sb.reranker_socket(box.home))
    assert sockets == [expected], f"the sandbox block allows {sockets!r}, not the reranker's one socket {expected}"


def test_s8_the_socket_path_follows_the_services_setting_under_another_home(tmp_path):
    base = tmp_path.resolve()
    box = s.Box(base, base / "a home", base / "systmp", base / "elsewhere", base / "pycache")
    for folder in (box.home, box.tmpdir, box.elsewhere, box.pycache, box.calls, box.results):
        folder.mkdir(parents=True, exist_ok=True)
    sb.project(box)
    sockets = sb.unix_sockets(sb.started(_launch(box, s.ENGINEER)))
    expected = sb.norm(sb.reranker_socket(box.home))
    assert sockets == [expected], f"under HOME={box.home} the block allows {sockets!r}, not {expected}"
    assert not any(c in sockets[0] for c in "*?["), f"the socket entry is a pattern: {sockets[0]}"


def test_f4_a_reranker_socket_path_that_is_a_link_is_not_allowed(box):
    other = box.elsewhere / "other.sock"
    link = sb.reranker_cache(box.home) / "rerank.sock"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(other)
    launch = _launch(box, s.ENGINEER)
    if sb.refused(launch):
        return
    sockets = sb.unix_sockets(sb.started(launch))
    assert isinstance(sockets, list), f"allowUnixSockets is not a list: {sockets!r}"
    assert sb.norm(link) not in sockets and sb.norm(other) not in sockets, (
        f"a link at the reranker's socket path, to {other}, is allowed: {sockets}")


# ---------------------------------------------------------------- S9, F4: nothing else widens

@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s9_nothing_else_widens_in_the_sandbox_block(box, role):
    settings = sb.started(_launch(box, role))
    sandbox, net = sb.block(settings), sb.network(settings)
    assert set(sandbox) <= TODAYS_SANDBOX_KEYS, f"the sandbox block gains keys: {sorted(set(sandbox) - TODAYS_SANDBOX_KEYS)}"
    assert sandbox.get("allowUnsandboxedCommands") is False, "allowUnsandboxedCommands is not false"
    assert set(net) <= NETWORK_KEYS, f"the network block gains keys (a port, all sockets?): {sorted(set(net) - NETWORK_KEYS)}"
    assert net.get("strictAllowlist") is True, "network.strictAllowlist is not true"
    domains = sorted(net.get("allowedDomains") or [])
    assert domains == (_research_hosts() if role == s.RESEARCH else []), f"allowedDomains changed: {domains}"
    sockets = sb.unix_sockets(settings)
    assert isinstance(sockets, list) and len(sockets) <= 1, f"more than one Unix socket is allowed: {sockets!r}"
    files = sandbox.get("filesystem") or {}
    assert set(files) <= FILESYSTEM_KEYS, f"the filesystem block gains keys: {sorted(set(files) - FILESYSTEM_KEYS)}"


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s9_sandbox_faults_accepts_the_built_settings(box, role):
    settings = sb.started(_launch(box, role))
    assert sb.faults(box, settings) == [], "sandbox_faults refuses the settings the launcher built"


def _engineer_settings(box):
    return sb.started(_launch(box, s.ENGINEER))


def _change(settings, home, elsewhere, kind):
    data = copy.deepcopy(settings)
    sandbox = data["sandbox"]
    net = sandbox.setdefault("network", {})
    own = sb.reranker_socket(home)
    if kind == "enabled-false":
        sandbox["enabled"] = False
    elif kind == "fail-if-unavailable-false":
        sandbox["failIfUnavailable"] = False
    elif kind == "unsandboxed-commands-allowed":
        sandbox["allowUnsandboxedCommands"] = True
    elif kind == "strict-allowlist-off":
        net["strictAllowlist"] = False
    elif kind == "excluded-commands":
        sandbox["excludedCommands"] = ["git"]
    elif kind == "all-unix-sockets":
        net["allowAllUnixSockets"] = True
    elif kind == "a-second-unix-socket":
        net["allowUnixSockets"] = [own, str(elsewhere / "other.sock")]
    elif kind == "another-socket-in-its-place":
        net["allowUnixSockets"] = [str(elsewhere / "other.sock")]
    elif kind == "a-socket-pattern":
        net["allowUnixSockets"] = [str(sb.reranker_cache(home) / "*.sock")]
    elif kind == "the-socket-folder":
        net["allowUnixSockets"] = [str(sb.reranker_cache(home))]
    elif kind == "local-binding":
        net["allowLocalBinding"] = True
    elif kind == "a-proxy-port":
        net["httpProxyPort"] = 8080
    elif kind == "weaker-nested-sandbox":
        sandbox["enableWeakerNestedSandbox"] = True
    return data


TODAYS_CHANGES = ("enabled-false", "fail-if-unavailable-false", "unsandboxed-commands-allowed",
                  "strict-allowlist-off", "excluded-commands")
NEW_CHANGES = ("all-unix-sockets", "a-second-unix-socket", "another-socket-in-its-place", "a-socket-pattern",
               "the-socket-folder", "local-binding", "a-proxy-port", "weaker-nested-sandbox")


@pytest.mark.parametrize("kind", TODAYS_CHANGES + NEW_CHANGES)
def test_s9_sandbox_faults_refuses_any_other_change(box, kind):
    changed = _change(_engineer_settings(box), box.home, box.elsewhere, kind)
    assert sb.faults(box, changed), f"sandbox_faults accepts the sandbox block changed by {kind}:\n" \
                                    f"{json.dumps(changed['sandbox'])[:800]}"


# ---------------------------------------------------------------- F2: the sandbox's refusals stay

@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_f2_a_sandbox_that_cannot_be_built_stops_the_session(box, role):
    sandbox = sb.block(sb.started(_launch(box, role)))
    assert sandbox.get("enabled") is True and sandbox.get("failIfUnavailable") is True, (
        f"a session whose sandbox cannot be built would start: {json.dumps(sandbox)[:600]}")


@pytest.mark.parametrize("rel", (".claude/settings.json", ".claude/settings.local.json"))
def test_f2_a_repository_settings_file_carrying_a_sandbox_key_still_refuses(box, rel):
    path = box.project / rel
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    data["sandbox"] = {"enabled": False}
    s.write(path, json.dumps(data) + "\n")
    launch = _launch(box, s.ENGINEER)
    assert sb.refused(launch), f"a sandbox key in {rel} does not refuse the launch (DEC-233)\n{launch.describe()}"
    assert not [entry for entry in s.temp_folders(box) if entry.startswith(s.TEMP_PREFIX)], "a temp folder is left"
