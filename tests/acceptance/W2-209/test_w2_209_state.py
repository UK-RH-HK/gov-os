"""S6 and F1: G4, the state, and the order of the gates; no record, tag, pin or link change after any red gate.

G4 is reached only when G0 to G3 pass, and G3 passes only stood in, so the G4 cases go through
``gov.release._patch_test`` (the command line never takes a stand-in). The other gates' red inputs go through
``gov release 0.1.2 --patch``. Each case compares the repository (files, refs, HEAD, index) and the scratch home (pin
folders, the link) before and after. README, "S6, F1".
"""

import pytest

import w2_209_support as support


def _seam(repo, home, tmp_path, verdict="READY", suite=True):
    logs = tmp_path / "logs"
    logs.mkdir(exist_ok=True)
    record = support.good_suite(repo, tmp_path / "records") if suite else None
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), support.X],
                       {"suite": support.path_arg(record) if record else None,
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl"), verdict=verdict),
                        "repin": support.standin("repin", log=str(logs / "repin.jsonl"))},
                       role="orchestrator")
    assert out.kind != "missing", support.missing_message(out, "gov.release._patch_test")
    return out, support.read_jsonl(logs / "rehearse.jsonl"), support.read_jsonl(logs / "repin.jsonl")


def _plant_g4(base, tmp_path, condition):
    integrate = condition != "not_an_ancestor"
    repo = support.make_case(base, tmp_path / "repo", "previous" if condition == "previous_unreadable" else "clean",
                             integrate=integrate)
    if condition == "dirty":
        support.write(repo, {"notes.txt": "an untracked file\n"})
    elif condition == "frozen":
        support.write(repo, {support.FREEZE_REL: "FROZEN\n"})
    elif condition == "tag_exists":
        support.git(repo, "tag", f"v{support.X}", base.n_commit)
    elif condition == "record_exists":
        support.commit(repo, {f"{support.RELEASES_REL}/{support.X}/manifest.json": "{}\n"}, "A record folder",
                       (("Class", "C"),))
    elif condition == "previous_unreadable":
        support.previous_unreadable(repo)
    return repo


G4 = {"dirty": "dirty", "not_an_ancestor": "ancestor", "frozen": "frozen", "tag_exists": "exists",
      "record_exists": "exists", "previous_unreadable": "previous"}


@pytest.mark.parametrize("condition", list(G4))
def test_s6_each_state_condition_alone_is_refused_at_g4_after_g3(base, tmp_path, home, condition):
    repo = _plant_g4(base, tmp_path, condition)
    before, home_before = support.snapshot(repo), home.state()
    out, rehearsed, repinned = _seam(repo, home, tmp_path)
    support.assert_gate(out.refused(condition), "G4", condition, check=G4[condition])
    assert len(rehearsed) == 1, f"{condition}: G3 did not run once before G4 (the order G0 to G4): {rehearsed}"
    assert not repinned, f"{condition}: the re-pin ran after a red G4"
    assert not support.difference(before, support.snapshot(repo)), f"{condition}: a refused cut changed the repository"
    assert home.state() == home_before, f"{condition}: a refused cut changed the pins or the link"


def test_s6_two_reds_at_once_name_the_earlier_gate_g2_before_g4(base, tmp_path, home):
    repo = _plant_g4(base, tmp_path, "dirty")
    run = support.release(repo, home.path, support.X)  # no --suite
    support.assert_gate(support.refusal(run), "G2", "G2 and G4 red")


def test_s6_two_reds_at_once_name_the_earlier_gate_g3_before_g4_on_the_command_line(base, tmp_path, home):
    repo = _plant_g4(base, tmp_path, "tag_exists")
    record = support.good_suite(repo, tmp_path / "records")
    run = support.release(repo, home.path, support.X, "--suite", str(record), "--kept", str(tmp_path / "no-run"))
    support.assert_gate(support.refusal(run), "G3", "G3 and G4 red")


def test_s6_two_reds_at_once_name_the_earlier_gate_g3_before_g4_through_the_seam(base, tmp_path, home):
    repo = _plant_g4(base, tmp_path, "dirty")
    out, _, repinned = _seam(repo, home, tmp_path, verdict="NOT_READY")
    support.assert_gate(out.refused("G3 and G4"), "G3", "G3 and G4 red")
    assert not repinned, "the re-pin ran after a red G3"


# --------------------------------------------------------------------------
# F1: every gate red, missing or stale leaves everything as it was
# --------------------------------------------------------------------------

def _f1_case(base, tmp_path, home, gate):
    if gate == "G0_off":
        repo = support.make_case(base, tmp_path / "repo", "clean", authority_on=False)
        return repo, lambda: support.release(repo, home.path, support.X, "--suite",
                                             str(support.good_suite(repo, tmp_path / "records")))
    if gate == "G1_bigger":
        repo = support.make_case(base, tmp_path / "repo", "schema_added")
        return repo, lambda: support.release(repo, home.path, support.X, "--suite",
                                             str(support.good_suite(repo, tmp_path / "records")))
    repo = support.make_case(base, tmp_path / "repo", "clean")
    if gate == "G2_stale":
        record = support.suite_record(tmp_path / "records", "NR-parent.json", support.rev(repo, "HEAD~1"),
                                      support.tree_of(repo, "HEAD~1"))
        return repo, lambda: support.release(repo, home.path, support.X, "--suite", str(record))
    if gate == "G3_missing":
        return repo, lambda: support.release(repo, home.path, support.X, "--suite",
                                             str(support.good_suite(repo, tmp_path / "records")),
                                             "--kept", str(tmp_path / "no-such-run"))
    if gate == "G3_not_ready":
        return repo, lambda: _seam(repo, home, tmp_path, verdict="NOT_READY")[0]
    if gate == "G4_tag":
        support.git(repo, "tag", f"v{support.X}", base.n_commit)
        return repo, lambda: _seam(repo, home, tmp_path)[0]
    raise ValueError(gate)


@pytest.mark.parametrize("gate", ["G0_off", "G1_bigger", "G2_stale", "G3_missing", "G3_not_ready", "G4_tag"])
def test_f1_a_red_gate_leaves_the_record_folder_tags_branches_pins_and_link_as_they_were(base, tmp_path, home, gate):
    repo, attempt = _f1_case(base, tmp_path, home, gate)
    before, home_before = support.snapshot(repo), home.state()
    tags_before = support.git(repo, "tag", "--list")
    answer = attempt()
    details = answer.refused(gate) if isinstance(answer, support.Outcome) else support.refusal(answer)
    support.assert_gate(details, gate[:2], gate)
    assert not support.difference(before, support.snapshot(repo)), \
        f"{gate}: the repository changed after a red gate: {support.difference(before, support.snapshot(repo))[:10]}"
    assert support.git(repo, "tag", "--list") == tags_before, f"{gate}: a tag appeared after a red gate"
    assert not (repo / support.RELEASES_REL / support.X).exists(), f"{gate}: a record folder appeared"
    assert home.state() == home_before, f"{gate}: a pin folder or the link changed after a red gate"
