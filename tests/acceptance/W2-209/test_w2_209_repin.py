"""S8, S9, F4 and S10 (the push, rollback.sh): the general re-pin, ``gov.release.repin.repin(repo, version, home)``.

A planted source holds, beside 0.1.1, one release per case, each on a branch from 0.1.1 with its record (built with
``gov.release.build``, the base's code; ``kind.json``, ``gates.json`` and ``suite.json`` beside it in the cut's form)
committed with C its parent and tagged annotated: 0.1.2 green (two ``Fix:`` commits), and four releases whose own gov
fails one post-pin check in the new pin's environment (a hook that exits 1, a hook that crashes, a search that loses its
semantic facet, a doctor part newly unhealthy), and one whose ``gov --version`` names another release. The early
stops are planted on copies of 0.1.2 by moving its tag. Each re-pin runs in a scratch clone and a scratch home (the
live pin of 0.1.1 and its link) with a stand-in push command. README, "S8, S9, F4, S10".
"""

import json
import shutil
import subprocess

import pytest
import yaml

import w2_209_support as support

FAILURES = {"0.1.3": ("hook_exit:stop", "hooks"), "0.1.4": ("hook_crash:sessionstart", "hooks"),
            "0.1.5": ("facet", "search"), "0.1.6": ("doctor", "doctor")}
WRONG_VERSION = "0.1.7"


def _cut_form(repo, version, c):
    rules = {r: {"pass": True, "detail": "planted"} for r in support.RULES}
    kind = {"version": version, "kind": "patch", "from": support.N_VERSION, "commit": c, "rules": rules}
    suite = json.loads(support.suite_record(repo.parent / "records", f"NR-{version}.json", c,
                                            support.tree_of(repo, c)).read_text(encoding="utf-8"))
    gates = {"suite": {"record": f"NR-{version}.json", "head": c, "tree": suite["tree"], "optin": ["weekly"]},
             "proving": support.ready_report(), "rule": {"kind": "patch", "rules": rules}}
    return {"kind.json": json.dumps(kind, indent=2) + "\n", "gates.json": json.dumps(gates, indent=2) + "\n",
            "suite.json": json.dumps(suite, indent=2) + "\n", "NOTE.md": f"# Gov OS {version}\n"}


@pytest.fixture(scope="module")
def releases(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-repin")
    builder = folder / "builder"
    (builder / "tmp").mkdir(parents=True)
    repo = support.copy_repo(base.path, folder / "source")
    commits = {}
    plan = [(support.X, None), *[(v, fail) for v, (fail, _) in FAILURES.items()], (WRONG_VERSION, "version")]
    for version, fail in plan:
        support.git(repo, "checkout", "-q", "-B", support.INTEGRATION, base.n_commit)
        if fail is None:
            c = support.fixes(repo, version)
        else:
            support.commit(repo, {"src/gov/w2209_behaviour.py": support.behaviour(fail)}, f"Plant {fail}",
                           (("Class", "C"),))
            c = support.commit(repo, {"pyproject.toml": support.PYPROJECT.format(version=version)},
                               f"Version {version}", (("Class", "C"),))
        support.git(repo, "branch", "-f", f"release/{version}", c)
        commits[version] = (c, support.record(repo, builder, version, extra=_cut_form(repo, version, c)))
    return repo, commits


def _repin(releases, base, tmp_path, version, mutate=None):
    repo_source, commits = releases
    repo = support.copy_repo(repo_source, tmp_path / "repo")
    if mutate:
        mutate(repo, commits[version])
    home = support.make_home(tmp_path / "home", base.n_version_commit)
    command, pushes = support.push_command(tmp_path / "push")
    before = {"head": support.rev(repo), "registry": (repo / support.REGISTRY_REL).read_bytes(),
              "home": home.state()}
    out = support.call(home.path, "gov.release.repin:repin",
                       [support.path_arg(repo), version, support.path_arg(home.path)], {"push": command})
    assert out.kind != "missing", support.missing_message(out, "gov.release.repin.repin")
    return {"repo": repo, "home": home, "pushes": pushes, "out": out, "before": before, "c": commits[version][0],
            "version": version, "command": command}


@pytest.fixture(scope="module")
def outcomes(releases, base, tmp_path_factory):
    """Each re-pin once per process: ``outcomes(version)``."""
    cache = {}

    def get(version):
        if version not in cache:
            cache[version] = _repin(releases, base, tmp_path_factory.mktemp(f"repin-{version}"), version)
        return cache[version]
    return get


def _pin(home, c):
    return home.share / f"pin-{c[:12]}"


# --------------------------------------------------------------------------
# S8: a green re-pin
# --------------------------------------------------------------------------

def test_s8_a_green_re_pin_switches_the_link_to_the_new_pin(outcomes):
    green = outcomes(support.X)
    result = green["out"].returned("the green re-pin")
    assert result.get("status") == "ok", f"the green re-pin did not end ok: {result}"
    home = green["home"]
    assert home.target() == (_pin(home, green["c"]) / "bin" / "gov").resolve(), \
        f"the link names {home.target()}, not pin-{green['c'][:12]}/bin/gov"
    assert home.old_pin.is_dir(), "the old pin folder was removed"
    version = subprocess.run([str(home.link), "--version"], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
    assert support.X in version.stdout, f"the machine's gov is not the release's: {version.stdout!r}"


def test_s8_a_green_re_pin_commits_the_registry_entry_with_the_orchestrator_and_the_standing_decision(outcomes):
    green = outcomes(support.X)
    green["out"].returned("the green re-pin")
    repo = green["repo"]
    head = support.rev(repo)
    assert support.rev(repo, "HEAD~1") == green["before"]["head"], "the re-pin did not add one commit on HEAD"
    assert support.changed_paths(repo, "HEAD~1", "HEAD") == [support.REGISTRY_REL], \
        f"the registry commit changes more: {support.changed_paths(repo, 'HEAD~1', 'HEAD')}"
    assert support.trailer(repo, head, "Role") == ["orchestrator"], support.git(repo, "log", "-1")
    assert support.trailer(repo, head, "Decided-by") == [support.DECIDED_BY], support.git(repo, "log", "-1")
    tools = yaml.safe_load((repo / support.REGISTRY_REL).read_text(encoding="utf-8"))["tools"]
    entry = [t for t in tools if t.get("name") == "gov"]
    assert len(entry) == 1 and str(entry[0].get("version")) == support.X, f"the gov entry is not 0.1.2's: {entry}"
    assert [t["name"] for t in tools] == ["other", "gov", "tail"], f"the other entries moved: {tools}"


def test_s8_a_green_re_pin_writes_repin_json_ok_and_rollback_sh(outcomes):
    green = outcomes(support.X)
    green["out"].returned("the green re-pin")
    home = green["home"]
    state = json.loads(home.repin_json.read_text(encoding="utf-8"))
    assert state.get("status") == "ok" and state.get("version") == support.X, f"repin.json: {state}"
    assert home.rollback.is_file(), "rollback.sh is not written"


def test_s10_rollback_sh_is_plain_shell_holding_the_line_and_the_burned_mark(outcomes):
    green = outcomes(support.X)
    green["out"].returned("the green re-pin")
    home = green["home"]
    text = home.rollback.read_text(encoding="utf-8")
    bin_ = home.path / ".local" / "bin"
    line = (f"ln -sfn {home.old_pin}/bin/gov {bin_}/gov.new && mv -Tf {bin_}/gov.new {bin_}/gov; hash -r")
    assert line in text, f"rollback.sh does not hold the line\n{line}\n---\n{text}"
    assert str(home.burned_file) in text and support.X in text, f"rollback.sh does not add 0.1.2 to burned:\n{text}"
    commands = [w for l in text.splitlines() if not l.lstrip().startswith("#") for w in l.replace(";", " ").split()]
    assert "gov" not in commands, f"rollback.sh runs gov:\n{text}"


def test_s10_a_pinned_release_makes_one_push_of_at_most_190_characters(outcomes):
    green = outcomes(support.X)
    green["out"].returned("the green re-pin")
    sent = support.pushes(green["pushes"])
    assert len(sent) == 1, f"not one push: {sent}"
    text = sent[0][-1]
    assert len(text) <= support.PUSH_LIMIT, f"the push is {len(text)} characters: {text!r}"
    assert text.startswith(f"Gov OS {support.X} released (patch, 2 fixes)."), text
    assert f"Suite green on {green['c'][:8]}" in text and "proving run READY" in text, text
    assert text.endswith(f"Roll back: {support.ROLLBACK_LINE}"), text


def test_s10_the_pasted_rollback_line_restores_the_previous_gov_and_burns_the_release(releases, base, tmp_path):
    green = _repin(releases, base, tmp_path, support.X)
    green["out"].returned("the green re-pin")
    home = green["home"]
    assert home.target() != (home.old_pin / "bin" / "gov").resolve(), "precondition: the re-pin switched the link"
    path = "/usr/bin:/bin"
    assert shutil.which("gov", path=path) is None, "precondition: no gov on the plain PATH"
    done = subprocess.run(["bash", str(home.rollback)], env={"HOME": str(home.path), "PATH": path},
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, f"rollback.sh failed: {done.stderr}"
    assert home.target() == (home.old_pin / "bin" / "gov").resolve(), f"the link names {home.target()}"
    assert support.X in home.burned_file.read_text(encoding="utf-8").split(), "rollback.sh did not burn 0.1.2"


# --------------------------------------------------------------------------
# S8: each early stop changes nothing
# --------------------------------------------------------------------------

def _retag(repo, sha, annotated=True):
    if annotated:
        support.git(repo, "tag", "-f", "-a", "-m", f"release {support.X}", f"v{support.X}", sha)
    else:
        support.git(repo, "tag", "-f", f"v{support.X}", sha)


def _amend(repo, record_commit, files):
    support.git(repo, "checkout", "-q", "--detach", record_commit)
    support.write(repo, files)
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "--amend", "--no-edit")
    sha = support.rev(repo)
    support.git(repo, "checkout", "-q", support.INTEGRATION)
    return sha


def _unannotated(repo, commits):
    _retag(repo, commits[1], annotated=False)


def _extra_file(repo, commits):
    _retag(repo, _amend(repo, commits[1], {"docs/extra.md": "not the record's\n"}))


def _manifest_hash(repo, commits):
    rel = f"{support.RELEASES_REL}/{support.X}/manifest.sha256"
    _retag(repo, _amend(repo, commits[1], {rel: f"{'1' * 64}  manifest.json\n"}))


def _wheel_hash(repo, commits):
    folder = f"{support.RELEASES_REL}/{support.X}"
    manifest = json.loads(support.show(repo, f"{commits[1]}:{folder}/manifest.json"))
    manifest["wheel"]["sha256"] = "2" * 64
    data = json.dumps(manifest, indent=2) + "\n"
    digest = support.sha256_bytes(data.encode())
    _retag(repo, _amend(repo, commits[1], {f"{folder}/manifest.json": data,
                                           f"{folder}/manifest.sha256": f"{digest}  manifest.json\n"}))


@pytest.mark.parametrize("step, version, mutate", [
    ("tag", support.X, _unannotated), ("record", support.X, _extra_file), ("manifest", support.X, _manifest_hash),
    ("wheel", support.X, _wheel_hash), ("version", WRONG_VERSION, None)])
def test_s8_each_early_stop_changes_nothing(releases, base, tmp_path, step, version, mutate):
    stopped = _repin(releases, base, tmp_path, version, mutate)
    result = stopped["out"].returned(f"the re-pin with a planted {step} fault")
    assert result.get("status") == "stopped" and result.get("step") == step, \
        f"the re-pin did not stop at {step}: {result}"
    home = stopped["home"]
    assert home.state() == stopped["before"]["home"], f"{step}: the link or the pin folders changed before the switch"
    assert support.rev(stopped["repo"]) == stopped["before"]["head"], f"{step}: a commit was made"
    assert (stopped["repo"] / support.REGISTRY_REL).read_bytes() == stopped["before"]["registry"]
    assert not home.burned_file.exists(), f"{step}: an early stop burned the release"


# --------------------------------------------------------------------------
# S9 and F4: a failed check after the switch rolls back, burns and tells the owner once
# --------------------------------------------------------------------------

@pytest.mark.parametrize("version", list(FAILURES))
def test_s9_a_failed_post_pin_check_puts_the_previous_gov_back_and_burns_the_release(outcomes, version):
    failed = outcomes(version)
    result = failed["out"].returned(f"the re-pin of {version}")
    check = FAILURES[version][1]
    assert result.get("status") == "rolled_back" and result.get("check") == check, \
        f"{version}: not rolled back naming {check}: {result}"
    home = failed["home"]
    assert home.target() == (home.old_pin / "bin" / "gov").resolve(), f"{version}: the link names {home.target()}"
    state = json.loads(home.repin_json.read_text(encoding="utf-8"))
    assert state.get("status") == "rolled_back" and state.get("check") == check and state.get("version") == version, \
        f"{version}: repin.json is {state}"
    assert home.burned_file.read_text(encoding="utf-8").splitlines() == [version], \
        f"{version}: burned is {home.burned_file.read_text(encoding='utf-8')!r}"
    listed = support.call(home.path, "gov.release.repin:burned", [support.path_arg(home.path)])
    assert listed.returned("gov.release.repin.burned") == [version], f"burned(home) is {listed.result}"
    tags = support.git(failed["repo"], "tag", "--list").split()
    assert f"v{version}" in tags, f"{version}: the burned release's tag was removed"


@pytest.mark.parametrize("version", list(FAILURES))
def test_f4_a_failed_check_leaves_the_registry_unchanged_and_pushes_the_owner_once(outcomes, version):
    failed = outcomes(version)
    failed["out"].returned(f"the re-pin of {version}")
    repo = failed["repo"]
    assert support.rev(repo) == failed["before"]["head"], f"{version}: a commit was made after a failed check"
    assert (repo / support.REGISTRY_REL).read_bytes() == failed["before"]["registry"], f"{version}: the registry changed"
    sent = support.pushes(failed["pushes"])
    assert len(sent) == 1, f"{version}: not one push: {sent}"
    text = sent[0][-1]
    assert len(text) <= support.PUSH_LIMIT, f"{version}: the push is {len(text)} characters: {text!r}"
    check = FAILURES[version][1]
    assert text.startswith(f"Gov OS {version} NOT pinned: post-pin check failed ({check})."), text
    assert "burned" in text.lower(), text


def test_s9_a_second_re_pin_of_a_burned_release_is_refused(outcomes):
    version = "0.1.3"
    failed = outcomes(version)
    failed["out"].returned(f"the re-pin of {version}")
    home = failed["home"]
    before = home.state()
    again = support.call(home.path, "gov.release.repin:repin",
                         [support.path_arg(failed["repo"]), version, support.path_arg(home.path)])
    result = again.returned("the second re-pin")
    assert result.get("status") == "stopped" and result.get("step") == "burned", f"not refused as burned: {result}"
    assert home.state() == before, "the second re-pin changed the pins or the link"


# --------------------------------------------------------------------------
# S10: the push texts' bounds
# --------------------------------------------------------------------------

def test_s10_the_release_push_fits_190_characters_for_the_longest_version_and_eight_fixes(tmp_path):
    out = support.call(tmp_path, "gov.release.repin:push_text", ["99.99.99", 8, "1b2c3d4e" + "f" * 32, "READY"])
    assert out.kind != "missing", support.missing_message(out, "gov.release.repin.push_text")
    text = out.returned("push_text")
    assert len(text) <= support.PUSH_LIMIT, f"{len(text)} characters: {text!r}"
    assert text.startswith("Gov OS 99.99.99 released (patch, 8 fixes).") and "1b2c3d4e" in text \
        and "READY" in text and text.endswith(f"Roll back: {support.ROLLBACK_LINE}"), text


def test_s10_the_failure_push_is_cut_to_190_characters_keeping_the_version_and_burned(tmp_path):
    check = "hooks: the subagentstop hook gave exit 1 through the new pin, " * 4
    out = support.call(tmp_path, "gov.release.repin:failure_text", ["99.99.99", check])
    assert out.kind != "missing", support.missing_message(out, "gov.release.repin.failure_text")
    text = out.returned("failure_text")
    assert len(text) <= support.PUSH_LIMIT, f"{len(text)} characters: {text!r}"
    assert "99.99.99" in text and "burned" in text.lower(), text
