"""RP-1 (the fix recorded in DAEO-a2h5): the re-pin writes gov's tool-registry entry after the switch and before the
post-pin checks, so ``gov doctor``'s ``tools`` part reads the new gov as pinned; a pass commits it, a failing check, a
failed commit or an error restores the file's bytes and commits nothing. README, "RP-1".

One planted release 0.1.2 on the planted source whose own ``gov doctor`` is the planted stand-in with one change: its
``tools`` part reads the ``tool-registry.yaml`` of the working directory (the repository) and fails unless the ``gov``
entry names the gov's own version and the ``other`` entry still names 1.0. (The real ``gov doctor`` cannot be run
hermetically here: the pin is built from the planted source, whose gov is the stand-in; the planted doctor does what the
real ``_check_tools`` does for the gov entry, reading the working tree's file against the pin's ``gov --version``.)
The stand-in ``check`` (``registry_check``) records the registry file and HEAD as it runs.
"""

import json

import pytest
import yaml

import w2_209_support as support
from test_w2_209_repin import _cut_form

TOOLS_DEF = '''
def _tools():
    from pathlib import Path
    try:
        import yaml
        text = (Path.cwd() / "governance/project/tool-registry.yaml").read_text(encoding="utf-8")
        entries = {e["name"]: str(e["version"]) for e in yaml.safe_load(text)["tools"]}
    except Exception:
        return "fail"
    return "pass" if entries.get("gov") == _version() and entries.get("other") == "1.0" else "fail"

'''
MAIN_GUARD = '\nif __name__ == "__main__":'


def _planted_main():
    main = support.PACKAGE_MAIN.replace('"tools": {"status": "pass"}', '"tools": {"status": _tools()}')
    assert main != support.PACKAGE_MAIN and MAIN_GUARD in main
    return main.replace(MAIN_GUARD, TOOLS_DEF + MAIN_GUARD.lstrip("\n"), 1)


@pytest.fixture(scope="module")
def release(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-rp1")
    builder = folder / "builder"
    (builder / "tmp").mkdir(parents=True)
    repo = support.copy_repo(base.path, folder / "source")
    support.git(repo, "checkout", "-q", "-B", support.INTEGRATION, base.n_commit)
    support.commit(repo, {"src/gov/cli/main.py": _planted_main()}, "Plant a doctor that reads the registry",
                   (("Class", "C"),))
    c = support.fixes(repo, support.X)
    support.git(repo, "branch", "-f", f"release/{support.X}", c)
    support.record(repo, builder, support.X, extra=_cut_form(repo, support.X, c))
    return repo, c


def _other_mismatch(repo):
    text = (repo / support.REGISTRY_REL).read_text(encoding="utf-8")
    assert 'version: "1.0"' in text
    support.commit(repo, {support.REGISTRY_REL: text.replace('version: "1.0"', 'version: "9.9"', 1)},
                   "Plant a mismatch in another tool's entry", (("Class", "C"),))


def _failing_commit(repo):
    hook = repo / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text("#!/bin/sh\necho planted refusal >&2\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)


def _repin(release, base, tmp_path, mutate=None, check=None, fail=None):
    source, c = release
    repo = support.copy_repo(source, tmp_path / "repo")
    if mutate:
        mutate(repo)
    home = support.make_home(tmp_path / "home", base.n_version_commit)
    command, pushes = support.push_command(tmp_path / "push")
    log = tmp_path / "check.jsonl"
    before = {"head": support.rev(repo), "registry": (repo / support.REGISTRY_REL).read_bytes(),
              "home": home.state()}
    kwargs = {"push": command}
    if check:
        kwargs["check"] = support.standin("registry_check", repo=str(repo), log=str(log), fail=fail)
    out = support.call(home.path, "gov.release.repin:repin",
                       [support.path_arg(repo), support.X, support.path_arg(home.path)], kwargs)
    assert out.kind != "missing", support.missing_message(out, "gov.release.repin.repin")
    result = out.returned("the re-pin")
    seen = support.read_jsonl(log) if log.exists() else []
    return {"repo": repo, "home": home, "before": before, "result": result, "seen": seen, "c": c}


def _gov(text):
    return [t for t in yaml.safe_load(text)["tools"] if t.get("name") == "gov"][0]


def _unchanged(run, what):
    repo = run["repo"]
    assert (repo / support.REGISTRY_REL).read_bytes() == run["before"]["registry"], f"{what}: the registry changed"
    assert support.rev(repo) == run["before"]["head"], f"{what}: HEAD moved"
    assert support.git(repo, "status", "--porcelain", "--untracked-files=no").strip() == "", \
        f"{what}: the working tree is dirty"


def test_rp1_the_check_sees_the_new_gov_entry_in_the_working_tree_before_anything_is_committed(release, base, tmp_path):
    run = _repin(release, base, tmp_path, check=True)
    assert run["result"].get("status") == "ok", f"the re-pin with a passing check did not end ok: {run['result']}"
    assert len(run["seen"]) == 1, f"the check ran {len(run['seen'])} times"
    seen = run["seen"][0]
    entry = _gov(seen["registry"])
    manifest = json.loads(support.show(run["repo"], f"v{support.X}:{support.RELEASES_REL}/{support.X}/manifest.json"))
    c12 = run["c"][:12]
    assert str(entry.get("version")) == support.X, f"while the check ran the gov entry names {entry.get('version')}"
    assert entry.get("sha256") == manifest["wheel"]["sha256"], f"the entry's sha256 is {entry.get('sha256')}"
    assert f"pin-{c12}" in entry.get("install", ""), f"the install line: {entry.get('install')}"
    assert run["home"].old_pin.name in entry.get("uninstall", ""), f"the uninstall line: {entry.get('uninstall')}"
    assert seen["head"] == run["before"]["head"], "the entry was already committed while the check ran"
    old = yaml.safe_load(run["before"]["registry"].decode())["tools"]
    now = yaml.safe_load(seen["registry"])["tools"]
    assert [t for t in now if t["name"] != "gov"] == [t for t in old if t["name"] != "gov"], \
        "an entry other than gov's changed"
    assert [t["name"] for t in now] == [t["name"] for t in old], "the entries moved"


def test_rp1_a_green_re_pin_through_the_planted_doctor_commits_the_entry_alone(release, base, tmp_path):
    run = _repin(release, base, tmp_path)
    assert run["result"].get("status") == "ok", f"the doctor's tools part did not pass with the entry written: {run['result']}"
    repo = run["repo"]
    assert support.rev(repo, "HEAD~1") == run["before"]["head"], "the re-pin did not add one commit on HEAD"
    assert support.changed_paths(repo, "HEAD~1", "HEAD") == [support.REGISTRY_REL]
    head = support.rev(repo)
    assert support.trailer(repo, head, "Role") == ["orchestrator"]
    assert support.trailer(repo, head, "Decided-by") == [support.DECIDED_BY]
    assert str(_gov((repo / support.REGISTRY_REL).read_text(encoding="utf-8")).get("version")) == support.X
    assert support.git(repo, "status", "--porcelain", "--untracked-files=no").strip() == ""
    assert run["home"].target() == (run["home"].share / f"pin-{run['c'][:12]}" / "bin" / "gov").resolve()


def test_rp1_a_failing_check_that_had_seen_the_new_entry_leaves_registry_head_and_link_as_they_were(release, base, tmp_path):
    run = _repin(release, base, tmp_path, check=True, fail="probe")
    result = run["result"]
    assert result.get("status") == "rolled_back" and result.get("check") == "probe", f"not rolled back: {result}"
    assert len(run["seen"]) == 1 and str(_gov(run["seen"][0]["registry"]).get("version")) == support.X, \
        "the failing check did not see the new gov entry"
    _unchanged(run, "failing check")
    home = run["home"]
    assert home.target() == (home.old_pin / "bin" / "gov").resolve(), f"the link names {home.target()}"
    assert home.burned_file.read_text(encoding="utf-8").split() == [support.X]


def test_rp1_a_genuine_mismatch_in_another_tools_entry_still_rolls_back_with_the_registry_as_it_was(release, base, tmp_path):
    run = _repin(release, base, tmp_path, mutate=_other_mismatch)
    result = run["result"]
    assert result.get("status") == "rolled_back" and result.get("check") == "doctor", f"not rolled back: {result}"
    assert "tools" in result.get("detail", ""), f"the doctor check does not name tools: {result}"
    _unchanged(run, "genuine mismatch")
    home = run["home"]
    assert home.target() == (home.old_pin / "bin" / "gov").resolve()


def test_rp1_a_failed_registry_commit_rolls_back_and_restores_the_registry_bytes(release, base, tmp_path):
    run = _repin(release, base, tmp_path, mutate=_failing_commit, check=True)
    result = run["result"]
    assert result.get("status") == "rolled_back", f"a refused commit did not roll back: {result}"
    _unchanged(run, "failed commit")
    home = run["home"]
    assert home.target() == (home.old_pin / "bin" / "gov").resolve()
    assert home.burned_file.read_text(encoding="utf-8").split() == [support.X]
