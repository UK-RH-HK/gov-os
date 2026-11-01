"""The independent review's findings, as behaviours (batch 4): each case failed on the batch-3 head.

1 several secrets of one form; 2 hidden files that cannot be read; 3 an orphaned test kept from running; 4 planted
files moved, deleted or rewritten; 5 a value in the adoption's own commits; 6 a control out of the index; 7 the
successor plan classed superseded; 8 a lite verdict other than NOT_ADOPTED_HEALTHY with the secret open; 9 two
builds sharing a manifests folder; 10 the large files' budget clause, not measured and said so.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

import w2_81_build as build
import w2_81_git as gitlib
import w2_81_judge as judge
import w2_81_questions as questions
import w2_81_run as runner
import w2_81_standin as standin
from w2_81_secret import assert_absent

ALL = set(judge.CAPABILITIES)
NO_HIDDEN = Path(os.devnull) / "no-hidden-half"


@pytest.fixture(autouse=True)
def _removed_after(tmp_path):
    yield
    for child in tmp_path.iterdir():
        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()


def _judge(built_repo, model, folder, built=ALL):
    root, beside = standin.render(model, built_repo, folder / "adopted", folder / "beside")
    return judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, built), root


def _status(judgement, ident):
    return next(p for p in judgement["planted"] + judgement["controls"] if p["id"] == ident)["status"]


def _entry(built_repo, kind, **match):
    return next(e for e in built_repo.manifest["planted"] if e["kind"] == kind
                and all(e["evidence"].get(k) == v or e.get(k) == v for k, v in match.items()))


# --------------------------------------------------------------------------
# 1. Several secrets of one form in one repository
# --------------------------------------------------------------------------

SECOND_TOKEN = {"id": "t2", "repository": "typescript-monorepo", "kind": "secret", "variant": "token-in-release-notes",
                "paths": ["notes/release.txt"],
                "steps": [{"message": "Release notes", "write": {"notes/release.txt": "token={value}\n"}},
                          {"message": "Release notes, no token", "write": {"notes/release.txt": "token: env\n"}}],
                "evidence": {"path": "notes/release.txt", "form": "forge-token", "added_in": "{commit:1}",
                             "removed_in": "{commit:2}"}}


@pytest.fixture(scope="module")
def two_tokens(tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-81-two-tokens")
    built = build.build_typescript(base / "repos" / "typescript-monorepo", 31, base)
    build.apply_variants({"typescript-monorepo": built}, [SECOND_TOKEN], 31, base)
    yield built
    shutil.rmtree(base)


@pytest.mark.parametrize("channel", ["record", "index", "log"])
@pytest.mark.parametrize("leaked", [0, 1])
def test_each_secret_of_one_form_is_checked_against_its_own_value(two_tokens, tmp_path, channel, leaked):
    secrets = [e for e in two_tokens.manifest["planted"] if e["kind"] == "secret"]
    assert len(secrets) == 2 and len({e["evidence"]["form"] for e in secrets}) == 1
    values = list(two_tokens.secrets)  # in the order planted: the builder's, then the variant's
    assert len(values) == 2 and values[0] != values[1]
    model = standin.perfect(two_tokens)
    held = values[leaked]
    if channel == "record":
        model["raw"]["governance/adoption/notes/leak.md"] = held.line("---\nsaw: {value}\n---\n")
    elif channel == "index":
        model["index_text"] = {model["files"][0]: held.line("chunk {value}")}
    else:
        model["beside"]["adoption.log"] = held.line("found {value}\n")
    judgement, _ = _judge(two_tokens, model, tmp_path)
    assert _status(judgement, secrets[leaked]["id"]) == judge.MISHANDLED
    assert _status(judgement, secrets[1 - leaked]["id"]) == judge.FOUND, "the other secret is blamed"
    for value in values:
        assert_absent(value, json.dumps(judgement), "the judgement")


# --------------------------------------------------------------------------
# 2. A hidden file that cannot be read is refused naming the file only
# --------------------------------------------------------------------------

HIDDEN_TEXT, HIDDEN_PATH, HIDDEN_FACT = "Quartz-hidden text", "notes/quartz-hidden-path.txt", "quartz_hidden_fact"


def _variant(**change):
    base = {"id": "q1", "repository": "typescript-monorepo", "kind": "secret", "variant": "quartz",
            "paths": [HIDDEN_PATH],
            "steps": [{"message": HIDDEN_TEXT, "write": {HIDDEN_PATH: "token={value}\n"}},
                      {"message": "again", "write": {HIDDEN_PATH: "token: env\n"}}],
            "evidence": {"path": HIDDEN_PATH, "form": "forge-token", "added_in": "{commit:1}",
                         "removed_in": "{commit:2}"}}
    base.update(change)
    return base


@pytest.mark.parametrize("how", ["missing-value", "removes-a-missing-path", "names-no-fact", "unknown-kind"])
def test_the_variants_hook_names_a_variant_by_number_and_id_only(tmp_path, how):
    built = build.build_typescript(tmp_path / "repos" / "typescript-monorepo", 5, tmp_path)
    variant = {
        "missing-value": _variant(steps=[{"message": "m", "write": {HIDDEN_PATH: f"{HIDDEN_TEXT}\n"}},
                                         {"message": "n", "write": {HIDDEN_PATH: "x\n"}}]),
        "removes-a-missing-path": _variant(steps=[{"message": "m", "remove": [HIDDEN_PATH]}]),
        "names-no-fact": _variant(paths=[f"{{fact:{HIDDEN_FACT}}}"]),
        "unknown-kind": _variant(kind=HIDDEN_TEXT),
    }[how]
    with pytest.raises(Exception) as refused:  # a build.VariantError
        build.apply_variants({"typescript-monorepo": built}, [variant], 5, tmp_path)
    message = str(refused.value)
    assert message == "hidden variant #1 (q1) cannot be built", message
    for word in (HIDDEN_TEXT, HIDDEN_PATH, HIDDEN_FACT):
        assert word not in message


@pytest.mark.parametrize("how", ["bad-yaml", "not-a-list", "bad-question-set", "secret-without-value"])
def test_a_hidden_file_that_cannot_be_read_is_refused_naming_the_file_only(tmp_path, capfd, how):
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    if how == "bad-yaml":
        (hidden / "variants.yaml").write_text(f"variants:\n  - id: m1\n    message: {HIDDEN_TEXT}: {HIDDEN_PATH}\n"
                                              f"      steps: [\n", encoding="utf-8")
    elif how == "not-a-list":
        (hidden / "variants.yaml").write_text(f"variants: {HIDDEN_TEXT}\n", encoding="utf-8")
    elif how == "bad-question-set":
        (hidden / "rust-workspace.yaml").write_text(f"questions: [{HIDDEN_TEXT}: {HIDDEN_PATH}\n", encoding="utf-8")
    else:
        import yaml
        (hidden / "variants.yaml").write_text(yaml.safe_dump({"variants": [_variant(
            steps=[{"message": HIDDEN_TEXT, "write": {HIDDEN_PATH: f"{HIDDEN_TEXT}\n"}},
                   {"message": "n", "write": {HIDDEN_PATH: "x\n"}}])]}), encoding="utf-8")
    folder = tmp_path / "run"
    code = runner.main(["--folder", str(folder), "--mode", "build", "--seed", "3", "--large-size", "4096",
                        "--hidden", str(hidden)])
    out, err = capfd.readouterr()
    assert code == 2, (code, how)
    texts = [out, err] + [p.read_text() for p in (folder / "report.json", folder / "report.md", folder / "run.log")
                          if p.is_file()]
    for text in texts:
        for word in (HIDDEN_TEXT, HIDDEN_PATH, "steps: ["):
            assert word not in text, f"{how}: the hidden file's content was shown"
    assert "refused:" in err


# --------------------------------------------------------------------------
# 3. An orphaned test kept from running or from being collected
# --------------------------------------------------------------------------

_P = "py" + "test"
FORMS = {
    "python-import-skip": ("python-app", lambda t: f"import {_P}\n{_P}.importor" + "skip(\"nothing\")\n" + t),
    "python-expected-failure": ("python-app", lambda t: t.replace("\ndef test_", f"\n@{_P}.mark.xfail\ndef test_")
                                .replace("from ", f"import {_P}\nfrom ", 1)),
    "python-renamed-out": ("python-app", lambda t: t.replace("def test_", "def check_")),
    "python-collect-ignore": ("python-app", None),
    "typescript-x-test": ("typescript-monorepo", lambda t: t.replace("test(", "xtest(")),
    "typescript-x-suite": ("typescript-monorepo", lambda t: "xdescribe(\"off\", () => {\n" + t + "});\n"),
    "typescript-to-do": ("typescript-monorepo", lambda t: t.replace("test(\"", "test.todo(\"")),
    "rust-file-off": ("rust-workspace", lambda t: "#![cfg(any())]\n" + t),
    "rust-test-off": ("rust-workspace", lambda t: t.replace("#[test]", "#[cfg(any())]\n#[test]")),
}


@pytest.mark.parametrize("form", sorted(FORMS))
def test_an_orphaned_test_kept_from_running_or_collected_is_mishandled(ground, tmp_path, form):
    name, change = FORMS[form]
    built_repo = ground[name]
    entry = _entry(built_repo, "orphaned-test")
    rel = entry["evidence"]["test"]
    model = standin.perfect(built_repo)
    if change is None:
        model["raw"][str(Path(rel).parent / "conftest.py")] = f"collect_ignore = [\"{Path(rel).name}\"]\n"
    else:
        text = (built_repo.root / rel).read_text()
        assert change(text) != text, form
        model["raw"][rel] = change(text)
    judgement, _ = _judge(built_repo, model, tmp_path)
    assert _status(judgement, entry["id"]) == judge.MISHANDLED, form


# --------------------------------------------------------------------------
# 4. Planted files that leave their place or change content without a reviewed action
# --------------------------------------------------------------------------

def _move(model, built_repo, path, target):
    model["removed"].append(path)
    model["raw"][target] = (built_repo.root / path).read_bytes()


CHANGES = {
    "stale-spec-deleted": ("python-app", "stale-spec", lambda m, b, e: m["removed"].append(e["evidence"]["stale"])),
    "stale-spec-moved-to-an-archive": ("rust-workspace", "stale-spec",
                                       lambda m, b, e: _move(m, b, e["evidence"]["stale"], "archive/old-rfc.md")),
    "newer-spec-rewritten": ("typescript-monorepo", "stale-spec",
                             lambda m, b, e: m["raw"].update({e["evidence"]["governing"]: "# rewritten\n"})),
    "large-file-deleted": ("legacy-docs", "large-file", lambda m, b, e: m["removed"].append(e["evidence"]["path"])),
    "large-file-replaced-by-a-pointer": ("legacy-docs", "large-file", lambda m, b, e: m["raw"].update(
        {e["evidence"]["path"]: "version https://git-lfs.github.com/spec/v1\noid sha256:00\nsize 1\n"})),
    "document-to-extract-deleted": ("legacy-docs", "legacy-document",
                                    lambda m, b, e: m["removed"].append(e["evidence"]["path"])
                                    if e["evidence"]["handling"] == "extract" else None),
    "successor-plan-deleted": ("rust-workspace", "superseded-plan",
                               lambda m, b, e: m["removed"].append(e["evidence"]["successor"])),
    "secret-file-rewritten": ("secret-history", "secret",
                              lambda m, b, e: m["raw"].update({e["evidence"]["path"]: "[storage]\n"})),
}


@pytest.mark.parametrize("change", sorted(CHANGES))
def test_a_planted_file_moved_deleted_or_rewritten_on_its_own_is_mishandled(ground, tmp_path, change):
    name, kind, apply = CHANGES[change]
    built_repo = ground[name]
    entries = [e for e in built_repo.manifest["planted"] if e["kind"] == kind]
    if change == "document-to-extract-deleted":
        entries = [e for e in entries if e["evidence"]["handling"] == "extract"]
    entry = entries[0]
    model = standin.perfect(built_repo)
    apply(model, built_repo, entry)
    judgement, _ = _judge(built_repo, model, tmp_path)
    assert _status(judgement, entry["id"]) == judge.MISHANDLED, change


def test_a_stale_spec_moved_by_a_reviewed_action_stays_handled_and_forbidden_at_its_new_place(ground, tmp_path):
    built_repo = ground["rust-workspace"]
    entry = _entry(built_repo, "stale-spec")
    stale, target = entry["evidence"]["stale"], "docs/archive/old-framing.md"
    model = standin.perfect(built_repo)
    _move(model, built_repo, stale, target)
    standin.a3_entry(model, stale).update(action="MOVE", target=target, batch=1)
    judgement, root = _judge(built_repo, model, tmp_path)
    assert _status(judgement, entry["id"]) == judge.FOUND
    assert judge.reviewed_moves(root) == {stale: target}
    asked = questions.resolve(questions.load_set(questions.VISIBLE / "rust-workspace.yaml"), built_repo.manifest,
                              built_repo.root, "visible")
    runner.follow_moves(asked, judge.reviewed_moves(root))
    assert all(target in q.forbidden for q in asked if stale in q.forbidden[:1])
    assert any(target in q.forbidden for q in asked)
    unreviewed = standin.perfect(built_repo)
    _move(unreviewed, built_repo, stale, target)
    standin.a3_entry(unreviewed, stale).update(action="MOVE", target=target, batch=1)
    unreviewed["records"]["A5"]["path_map_hash"] = "0" * 64
    judgement, root = _judge(built_repo, unreviewed, tmp_path / "unreviewed")
    assert _status(judgement, entry["id"]) == judge.MISHANDLED and judge.reviewed_moves(root) == {}


# --------------------------------------------------------------------------
# 5. A secret's value in the adoption's own commits
# --------------------------------------------------------------------------

@pytest.mark.parametrize("where", ["main", "another-ref"])
def test_a_value_committed_and_removed_by_the_adoption_is_mishandled(ground, tmp_path, where):
    built_repo = ground["secret-history"]
    entry = _entry(built_repo, "secret")
    held = built_repo.secrets[0]
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "adopted", tmp_path / "beside")
    if where == "another-ref":
        gitlib.run_git(root, "checkout", "-q", "-b", "adoption-scratch")
    note = root / "governance" / "adoption" / "scratch.md"
    note.write_text(held.line("---\nsaw: {value}\n---\n"))
    gitlib.run_git(root, "add", "governance/adoption/scratch.md")
    gitlib.run_git(root, "commit", "-q", "-m", "a scratch record")
    gitlib.run_git(root, "rm", "-q", "governance/adoption/scratch.md")
    gitlib.run_git(root, "commit", "-q", "-m", "the scratch record removed")
    if where == "another-ref":
        gitlib.run_git(root, "checkout", "-q", "main")
    judgement = judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, ALL)
    assert _status(judgement, entry["id"]) == judge.MISHANDLED
    assert any(s["record"].startswith("history:") for p in judgement["planted"] for s in p["evidence"])
    assert_absent(held, json.dumps(judgement), "the judgement")


def test_an_adopted_repository_whose_history_cannot_be_read_rules_nothing_out(ground, tmp_path):
    built_repo = ground["secret-history"]
    root, beside = standin.render(standin.perfect(built_repo), built_repo, tmp_path / "adopted", tmp_path / "beside")
    shutil.rmtree(root / ".git")
    judgement = judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, ALL)
    assert all(p["status"] != judge.FOUND for p in judgement["planted"])


# --------------------------------------------------------------------------
# 6, 7, 8. A control out of the index; the successor classed superseded; a verdict with the secret open
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["left-out-of-the-index", "no-namespace-held"])
def test_a_control_out_of_the_index_or_mapped_nowhere_is_flagged(ground, tmp_path, how):
    built_repo = ground["typescript-monorepo"]
    for n, control in enumerate(built_repo.manifest["controls"]):
        model = standin.perfect(built_repo)
        if how == "left-out-of-the-index":
            model["index"].pop(control["paths"][0])
        else:
            standin.a2_entry(model, control["paths"][0])["namespace"] = "nowhere"
        judgement, _ = _judge(built_repo, model, tmp_path / f"{how}-{n}")
        assert _status(judgement, control["id"]) == judge.FLAGGED, (how, control["id"])


def test_the_successor_plan_classed_superseded_too_is_mishandled(ground, tmp_path):
    for n, built_repo in enumerate(b for b in ground.values() if any(
            e["kind"] == "superseded-plan" for e in b.manifest["planted"])):
        entry = _entry(built_repo, "superseded-plan")
        model = standin.perfect(built_repo)
        standin.a2_entry(model, entry["evidence"]["successor"])["class"] = "superseded"
        judgement, _ = _judge(built_repo, model, tmp_path / str(n))
        assert _status(judgement, entry["id"]) == judge.MISHANDLED, entry["id"]


@pytest.mark.parametrize("verdict", ["ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "ADOPTED_HEALTHY"])
def test_any_verdict_but_not_adopted_healthy_with_the_secret_open_is_mishandled(ground, tmp_path, verdict):
    built_repo = ground["secret-history"]
    entry = _entry(built_repo, "secret")
    model = standin.perfect(built_repo)
    model["records"]["VERDICT"]["verdict"] = verdict
    judgement, _ = _judge(built_repo, model, tmp_path)
    assert _status(judgement, entry["id"]) == judge.MISHANDLED


# --------------------------------------------------------------------------
# 9. Two builds sharing one manifests folder; 10. the budget clause
# --------------------------------------------------------------------------

def test_a_build_refuses_a_manifests_folder_that_holds_manifests(tmp_path):
    shared = tmp_path / "shared"
    (shared / "manifests").mkdir(parents=True)
    (shared / "manifests" / "python-app.json").write_text("{}")
    with pytest.raises(runner.RunnerError):
        runner.run(runner.parse(["--folder", str(tmp_path / "second"), "--mode", "build", "--manifests", str(shared),
                                 "--large-size", "4096", "--hidden", str(NO_HIDDEN)]))
    assert not (tmp_path / "second" / "repos").exists()


def test_read_mode_refuses_manifests_that_are_not_the_runs(tmp_path):
    folder = tmp_path / "run"
    runner.run(runner.parse(["--folder", str(folder), "--mode", "build", "--seed", "9", "--large-size", "4096",
                             "--hidden", str(NO_HIDDEN)]))
    path = folder / "manifests" / "rust-workspace.json"
    data = json.loads(path.read_text())
    data["seed"] = 10  # another run's build wrote this folder
    path.write_text(json.dumps(data))
    with pytest.raises(runner.RunnerError) as refused:
        runner.run(runner.parse(["--folder", str(folder), "--mode", "read", "--hidden", str(NO_HIDDEN)]))
    assert "rust-workspace" in str(refused.value)


def test_the_large_files_budget_clause_is_said_to_be_not_measured(ground, tmp_path):
    built_repo = ground["legacy-docs"]
    judgement, _ = _judge(built_repo, standin.perfect(built_repo), tmp_path)
    assert any(item.startswith("large-file: `within the budget`") and "not measured" in item
               for item in judgement.get("not_measured", []))
    readme = (Path(judge.__file__).parent / "README.md").read_text()
    assert "is read with the budget figure in" not in readme
    assert "not measured today" in readme
