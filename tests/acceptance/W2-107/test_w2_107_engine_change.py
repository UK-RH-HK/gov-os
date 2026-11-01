"""W2-107: any change to gitleaks or its rules forgets every remembered verdict; a scan that cannot decide still raises.

KPI success 3 (a fingerprint that differs from the cache's clears it before the first read) and success 4's last clause
(a scan that cannot decide still raises as today); failure 2 (a changed gitleaks or rule set answered from the old
results). The engine is changed as the design says a test changes it: another stand-in, with other bytes, first on PATH,
or the stand-in's own bytes rewritten in place between two processes.
"""

from __future__ import annotations

import pytest

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

FILES = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/beta.md": "W2-107: the beta page, ordinary text.\n",
}
NAME = "docs/an-ordinary-name.md"
ADDED_RULE = ("\n[[rules]]\n"
              'id = "w2-107-added"\n'
              'description = "W2-107: a rule added by the case; it matches nothing the case writes"\n'
              "regex = '''w2-107-never-written-[0-9]{12}'''\n")


def judge(root, rels):
    """One pass: the files' verdicts, then the name's."""
    return secrets.indexable(root, rels), secrets.path_holds_secret(root, NAME)


def test_a_rule_added_to_the_project_rescans_everything_and_the_old_rules_results_are_forgotten(
        project, engine, cache, per_text):
    rels = support.put(project, FILES)
    texts = len(rels) + 1
    expected = (rels, False)
    config = project / ".gitleaks.toml"
    original = config.read_text(encoding="utf-8")
    steps = [("the first rules", original, texts), ("the first rules again", original, 0),
             ("a rule added", original + ADDED_RULE, texts), ("a rule added, again", original + ADDED_RULE, 0),
             ("the first rules back", original, texts), ("the first rules back, again", original, 0)]
    for label, rules, scanned in steps:
        config.write_text(rules, encoding="utf-8")
        verdicts, calls = support.counted(engine, lambda: judge(project, rels))
        assert verdicts == expected, f"{label}: the verdicts are unchanged"
        assert calls == scanned * per_text, f"{label}: {scanned} of {texts} texts scanned"


def test_another_gitleaks_first_on_path_rescans_everything_and_switching_back_rescans_again(
        tmp_path, project, engine, cache, per_text, monkeypatch):
    other = support.make_engine(tmp_path / "engine-b", tag="b")
    rels = support.put(project, FILES)
    texts = len(rels) + 1
    steps = [("engine A", engine, texts), ("engine A again", engine, 0),
             ("engine B", other, texts), ("engine B again", other, 0),
             ("engine A back", engine, texts), ("engine A back, again", engine, 0)]
    for label, first, scanned in steps:
        monkeypatch.setenv("PATH", first.path())
        unused = other if first is engine else engine
        before = unused.calls()
        verdicts, calls = support.counted(first, lambda: judge(project, rels))
        assert verdicts == (rels, False), f"{label}: the verdicts are unchanged"
        assert unused.calls() == before, f"{label}: premise: only the gitleaks first on PATH is run"
        assert calls == scanned * per_text, \
            f"{label}: {scanned} of {texts} texts scanned (the old engine's results were forgotten, not kept beside)"


def test_a_gitleaks_whose_bytes_change_in_place_rescans_everything(project, engine, cache, per_text):
    """Each pass is a process of its own, as rebuilds are: the cache is shared between them, and the engine's identity
    is the bytes of the gitleaks PATH finds, read afresh by each process."""
    rels = support.put(project, FILES)
    texts = len(rels) + 1
    env = support.child_env(engine, cache)
    steps = [("the first bytes", None, texts), ("the first bytes again", None, 0),
             ("the bytes rewritten in place", "a, rewritten", texts), ("the rewritten bytes again", None, 0)]
    for label, retag, scanned in steps:
        if retag:
            support.write_standin(engine, retag)
        run, calls = support.counted(engine, lambda: support.run_child(project, rels, [NAME], env))
        assert run.error is None and run.indexable == rels and run.names == [False], f"{label}: the verdicts"
        assert run.gov == secrets.__file__, "the child runs the same gov as this run (DEC-732)"
        assert calls == scanned * per_text, f"{label}: {scanned} of {texts} texts scanned"


def test_a_gitleaks_that_cannot_decide_still_raises_though_the_content_was_remembered_under_another_engine(
        tmp_path, project, engine, cache, per_text, monkeypatch):
    rels = support.put(project, FILES)
    judge(project, rels)
    assert support.counted(engine, lambda: judge(project, rels))[1] == 0, "premise: remembered clean under engine A"
    failing = support.make_engine(tmp_path / "engine-f", tag="f")
    failing.fail.write_text("all", encoding="utf-8")
    monkeypatch.setenv("PATH", failing.path())
    for _ in range(2):
        with pytest.raises(RuntimeError):
            secrets.indexable(project, rels)
        with pytest.raises(RuntimeError):
            secrets.path_holds_secret(project, NAME)
    assert failing.calls() >= 4, "every call went to the gitleaks that cannot decide"
    failing.fail.unlink()  # the same engine, now deciding: nothing was remembered for the calls that could not
    verdicts, calls = support.counted(failing, lambda: judge(project, rels))
    assert verdicts == (rels, False) and calls == (len(rels) + 1) * per_text, "every text is scanned: none remembered"


def test_a_scan_whose_first_rule_set_ran_and_whose_next_could_not_decide_remembers_nothing(
        tmp_path, project, engine, cache, per_text, monkeypatch):
    """Clean means every rule set's run ended with no finding: a text one run judged and the next could not is not
    remembered, not even as half a verdict."""
    if per_text < 2:
        pytest.skip("one gitleaks call a text: no text is judged by two runs")
    rels = support.put(project, {"docs/alpha.md": FILES["docs/alpha.md"]})
    failing = support.make_engine(tmp_path / "engine-f", tag="f")
    failing.fail.write_text("after-first", encoding="utf-8")
    monkeypatch.setenv("PATH", failing.path())
    with pytest.raises(RuntimeError):
        secrets.indexable(project, rels)
    assert failing.calls() == 2, "premise: the first run went through, the second could not decide"
    failing.fail.unlink()
    kept, calls = support.counted(failing, lambda: secrets.indexable(project, rels))
    assert kept == rels and calls == per_text, "the text is scanned in full: nothing was remembered for it"


def test_no_gitleaks_on_path_still_raises_though_the_content_was_remembered(
        tmp_path, project, engine, cache, monkeypatch):
    rels = support.put(project, FILES)
    judge(project, rels)
    assert support.counted(engine, lambda: judge(project, rels))[1] == 0, "premise: remembered clean"
    empty = tmp_path / "no-gitleaks"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    with pytest.raises(OSError):
        secrets.indexable(project, rels)
    with pytest.raises(OSError):
        secrets.path_holds_secret(project, NAME)
