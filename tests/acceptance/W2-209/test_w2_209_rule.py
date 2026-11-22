"""S1 and F2: the patch rule, read by code from the last release N to the release commit C.

``gov release <X> --patch --check`` (S1) answers ``patch`` only for a range of fixes and chores, names exactly the
planted rule otherwise, and writes nothing; it reads the rule alone (the authority file is ``off`` in these copies).
The cut itself (F2, through ``gov.release._patch_test`` with every other gate planted green and G3 stood in) is
refused at G1 naming the rule, and at G0 when the authority file is off. README, "S1, F2".
"""

import pytest

import w2_209_support as support

BIGGER = ("contract", "charter", "emergency", "ticket", "feature", "fix_open_ticket", "command", "schema_added",
          "schema_removed", "minor", "prerelease")


def _rules(rules, what):
    assert isinstance(rules, dict) and set(support.RULES) <= set(rules), f"{what}: not every rule P1 to P5: {rules}"
    for name in support.RULES:
        entry = rules[name]
        assert isinstance(entry, dict) and isinstance(entry.get("pass"), bool), f"{what}: {name} has no pass: {entry}"
        assert isinstance(entry.get("detail"), str), f"{what}: {name} has no detail: {entry}"
    return {name for name in support.RULES if not rules[name]["pass"]}


def _check(base, tmp_path, home, name):
    case = base.cases[name]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=False)
    before = support.snapshot(repo)
    run = support.release(repo, home.path, case.version, "--check")
    after = support.snapshot(repo)
    return case, repo, run, support.difference(before, after)


@pytest.mark.parametrize("name", BIGGER)
def test_s1_check_names_exactly_the_planted_rule_and_writes_nothing(base, tmp_path, home, name):
    case, repo, run, changed = _check(base, tmp_path, home, name)
    details = support.refusal(run)
    assert details.get("kind") == "bigger", f"{name}: not answered bigger\n{run.describe()}"
    failed = _rules(details.get("rules"), name)
    assert failed == {case.rule}, f"{name}: the failed rules are {sorted(failed)}, not exactly {case.rule}\n{run.describe()}"
    assert details.get("failed") == [case.rule], f"{name}: `failed` is {details.get('failed')}, not [{case.rule}]"
    detail = details["rules"][case.rule]["detail"]
    assert case.named in detail, f"{name}: {case.rule}'s detail does not name {case.named!r}: {detail!r}"
    assert run.returncode == 1, f"{name}: a bigger range is refused as other refusals are (exit 1)\n{run.describe()}"
    assert not changed, f"{name}: --check wrote something: {changed[:10]}"


def test_s1_a_range_of_fixes_and_chores_only_is_a_patch_and_writes_nothing(base, tmp_path, home):
    case, repo, run, changed = _check(base, tmp_path, home, "clean")
    envelope = run.envelope()
    assert envelope.get("ok") is True and run.returncode == 0, f"the clean range is not a patch\n{run.describe()}"
    result = envelope["result"]
    assert result.get("kind") == "patch", f"the clean range is not answered patch: {result}"
    assert _rules(result.get("rules"), "clean") == set(), f"a rule fails on the clean range: {result.get('rules')}"
    assert result.get("failed") == [], f"`failed` is not empty: {result}"
    # N is the newest tag with a record (0.1.1), not the older release nor the decoy tag v0.1.9 without one.
    assert result.get("from") == support.N_VERSION, f"N is not {support.N_VERSION}: {result.get('from')!r}"
    assert result.get("commit") == support.rev(repo), f"C is not HEAD: {result.get('commit')!r}"
    assert not changed, f"--check wrote something: {changed[:10]}"


# --------------------------------------------------------------------------
# F2: a range the rule calls bigger is never cut
# --------------------------------------------------------------------------

def _cut(base, tmp_path, home, name, authority_on=True, suite=True):
    case = base.cases[name]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=authority_on)
    record = support.good_suite(repo, tmp_path / "records") if suite else None
    logs = tmp_path / "logs"
    logs.mkdir()
    before, home_before = support.snapshot(repo), home.state()
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), case.version],
                       {"suite": support.path_arg(record) if record else None,
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl")),
                        "repin": support.standin("repin", log=str(logs / "repin.jsonl"))},
                       role="orchestrator")
    assert out.kind != "missing", support.missing_message(out, "gov.release._patch_test")
    changed = support.difference(before, support.snapshot(repo))
    return case, out, changed, home_before, home.state(), logs


@pytest.mark.parametrize("name", BIGGER)
def test_f2_a_bigger_range_is_refused_at_g1_with_every_other_gate_green(base, tmp_path, home, name):
    case, out, changed, home_before, home_after, logs = _cut(base, tmp_path, home, name)
    details = out.refused(name)
    support.assert_gate(details, "G1", name, rule=case.rule)
    assert not changed, f"{name}: a refused cut changed the repository: {changed[:10]}"
    assert home_after == home_before, f"{name}: a refused cut changed the pins or the link"
    assert not support.read_jsonl(logs / "rehearse.jsonl"), f"{name}: G3 ran after a red G1"
    assert not support.read_jsonl(logs / "repin.jsonl"), f"{name}: the re-pin ran after a red G1"


def test_f2_a_bigger_range_with_the_authority_file_off_is_refused_at_g0(base, tmp_path, home):
    case, out, changed, home_before, home_after, logs = _cut(base, tmp_path, home, "contract", authority_on=False)
    support.assert_gate(out.refused("off"), "G0", "authority off, bigger range")
    assert not changed and home_after == home_before, f"a refused cut changed something: {changed[:10]}"


def test_f2_g1_is_named_before_a_red_g2(base, tmp_path, home):
    case, out, changed, home_before, home_after, logs = _cut(base, tmp_path, home, "feature", suite=False)
    support.assert_gate(out.refused("G1 and G2 red"), "G1", "G1 and G2 red", rule="P3")
    assert not changed, f"a refused cut changed the repository: {changed[:10]}"
