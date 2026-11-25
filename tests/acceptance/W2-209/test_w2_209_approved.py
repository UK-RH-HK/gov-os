"""RR-1 (approved content passes) and RR-2 (what still refuses): the third kind of the rule, ``approved`` (DEC-1235
(2); DEC-1251 D-01).

``gov release <X> --patch --check`` over the planted ranges (``w2_209_support._build_approvals``), the cut through
``gov.release._patch_test`` (G3 stood in; the re-pin stood in, or the real one in a scratch home) and what the cut
writes. README, "RR-1, RR-2".
"""

import json
import re

import pytest

import w2_209_support as support

CHECK_KEYS = {"version", "kind", "from", "commit", "rules", "failed", "approvals"}


def _no_patch_wording(text, what):
    low = text.lower()
    assert "approved" in low, f"{what} does not name the kind approved:\n{text}"
    assert "patch release" not in low and "(patch," not in low, f"{what} names an approved release a patch:\n{text}"


def _check(base, tmp_path, home, name, uncommitted=None):
    case = base.cases[name]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=False)
    if uncommitted:
        support.write(repo, uncommitted)
    before = support.snapshot(repo)
    run = support.release(repo, home.path, case.version, "--check")
    changed = support.difference(before, support.snapshot(repo))
    assert not changed, f"{name}: --check wrote something: {changed[:10]}"
    return case, repo, run


def _failed(rules, failed, case):
    assert {r for r in support.RULES if not rules[r]["pass"]} == set(case.failed), f"{case.name}: rules: {rules}"
    assert failed == list(case.failed), f"{case.name}: `failed` is {failed}, not {list(case.failed)}"


# --------------------------------------------------------------------------
# RR-1: the check
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", support.APPROVED)
def test_rr1_a_range_whose_every_item_names_the_owners_decision_is_checked_approved(base, tmp_path, home, name):
    case, repo, run = _check(base, tmp_path, home, name)
    envelope = run.envelope()
    assert envelope.get("ok") is True and run.returncode == 0, f"{name}: not answered approved\n{run.describe()}"
    result = envelope["result"]
    assert set(result) == CHECK_KEYS, f"{name}: the result's keys are {sorted(result)}"
    assert result["kind"] == "approved" and result["version"] == case.version, result
    assert result["from"] == support.N_VERSION and result["commit"] == support.rev(repo), result
    _failed(result["rules"], result["failed"], case)
    support.assert_approvals(result["approvals"], case)


def test_rr1_a_range_with_all_five_rules_passing_stays_a_patch_without_approvals(base, tmp_path, home):
    """Pins today's patch result (passes on the base): approving names change nothing about a patch."""
    case, repo, run = _check(base, tmp_path, home, "patch_with_approvals")
    envelope = run.envelope()
    assert envelope.get("ok") is True and run.returncode == 0, f"not a patch\n{run.describe()}"
    result = envelope["result"]
    assert result.get("kind") == "patch", result
    assert set(result) == CHECK_KEYS - {"approvals"}, f"a patch result changed its form: {sorted(result)}"


# --------------------------------------------------------------------------
# RR-1: the cut, as a patch: record, tag, merge, re-pin, push, and what is offered to an adopted repository
# --------------------------------------------------------------------------

def _cut(base, folder, name, real_repin=False, authority_on=True, suite=True, verdict="READY", plant=None):
    case = base.cases[name]
    repo = support.make_case(base, folder / "repo", case, authority_on=authority_on)
    if plant:
        plant(repo)
    c = support.rev(repo)
    record = support.good_suite(repo, folder / "records") if suite else None
    home = support.make_home(folder / "home", base.n_version_commit)
    command, pushes = support.push_command(folder / "push")
    logs = folder / "logs"
    logs.mkdir()
    kwargs = {"suite": support.path_arg(record) if record else None,
              "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl"), verdict=verdict),
              "push": command}
    if not real_repin:
        kwargs["repin"] = support.standin("repin", log=str(logs / "repin.jsonl"))
    before, home_before = support.snapshot(repo), home.state()
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), case.version], kwargs,
                       role="orchestrator")
    assert out.kind != "missing", support.missing_message(out, "gov.release._patch_test")
    return {"case": case, "repo": repo, "c": c, "home": home, "pushes": pushes, "out": out, "before": before,
            "home_before": home_before, "rehearse": support.read_jsonl(logs / "rehearse.jsonl"),
            "repin": support.read_jsonl(logs / "repin.jsonl")}


def _at_tag(flow, name):
    version = flow["case"].version
    data = support.show(flow["repo"], f"v{version}:{support.RELEASES_REL}/{version}/{name}")
    assert data is not None, f"{name} is not in the record at v{version}"
    return data.decode("utf-8")


def _assert_cut(flow):
    """Built, tagged and merged; the record says approved with the approvals."""
    case, repo = flow["case"], flow["repo"]
    flow["out"].returned(f"the cut of the approved range {case.name}")
    tag = f"v{case.version}"
    assert support.tag_type(repo, tag) == "tag", f"{tag} is not an annotated tag"
    tagged = support.rev(repo, f"{tag}^{{commit}}")
    parents = support.git(repo, "rev-list", "--parents", "-n", "1", tagged).split()[1:]
    assert parents == [flow["c"]], f"the record commit's parents are {parents}, not C"
    assert support.is_ancestor(repo, tagged, support.INTEGRATION), "w2/integrate does not contain the record commit"
    for name in support.RECORD_FILES:
        _at_tag(flow, name)
    kind = json.loads(_at_tag(flow, "kind.json"))
    assert kind.get("kind") == "approved" and kind.get("version") == case.version and kind.get("commit") == flow["c"] \
        and kind.get("from") == support.N_VERSION, f"kind.json: {kind}"
    support.assert_approvals(kind.get("approvals"), case)
    return tagged, kind


@pytest.mark.parametrize("name", ["ok_front", "ok_trailer"])
def test_rr1_the_cut_of_a_range_approved_by_front_matter_or_trailers_alone_builds_tags_merges_and_re_pins(
        base, tmp_path, name):
    flow = _cut(base, tmp_path, name)
    _assert_cut(flow)
    assert len(flow["rehearse"]) == 1 and len(flow["repin"]) == 1, \
        f"G3 and the re-pin did not each run once: {flow['rehearse']} {flow['repin']}"


@pytest.fixture(scope="module")
def flow(base, tmp_path_factory):
    return _cut(base, tmp_path_factory.mktemp("w2-209-approved"), "ok_mixed", real_repin=True)


def test_rr1_the_cut_of_an_approved_range_builds_tags_merges_and_writes_kind_approved_with_its_approvals(flow):
    _assert_cut(flow)
    verified = support.call(flow["home"].path, "gov.release:verify_at",
                            [support.path_arg(flow["repo"]), flow["case"].version])
    verified.returned("gov.release.verify_at of the approved release")


def test_rr1_the_record_commit_names_the_kind_approved_never_patch(flow):
    tagged, _ = _assert_cut(flow)
    message = support.git(flow["repo"], "log", "-1", "--format=%B", tagged)
    _no_patch_wording(message, "the record commit's message")
    assert support.trailer(flow["repo"], tagged, "Role") == ["orchestrator"], message
    assert support.trailer(flow["repo"], tagged, "Decided-by") == [support.DECIDED_BY], message
    assert support.trailer(flow["repo"], tagged, "Task") == ["release"], message


def test_rr1_note_md_says_approved_and_names_each_approval_with_its_decision(flow):
    _, kind = _assert_cut(flow)
    note = _at_tag(flow, support.NOTE)
    _no_patch_wording(note, "NOTE.md")
    for token, decisions in flow["case"].approved.items():
        lines = [line for line in note.splitlines() if token in line]
        assert any(all(d in line for d in decisions) for line in lines), \
            f"NOTE.md has no line naming {token} with {sorted(decisions)}:\n{note}"


def test_rr1_an_approved_release_is_re_pinned_and_pushed_once_as_approved(flow):
    _assert_cut(flow)
    case, home = flow["case"], flow["home"]
    result = flow["out"].result
    assert (result.get("repin") or {}).get("status") == "ok", f"the re-pin did not end ok: {result.get('repin')}"
    pin = home.share / f"pin-{flow['c'][:12]}"
    assert home.target() == (pin / "bin" / "gov").resolve(), f"the link names {home.target()}"
    assert json.loads(home.repin_json.read_text(encoding="utf-8")).get("status") == "ok"
    assert home.rollback.is_file(), "rollback.sh is not written"
    sent = support.pushes(flow["pushes"])
    assert len(sent) == 1, f"not one push: {sent}"
    text = sent[0][-1]
    _no_patch_wording(text, "the push")
    assert len(text) <= support.PUSH_LIMIT and case.version in text and support.ROLLBACK_LINE in text \
        and flow["c"][:8] in text and "READY" in text, text


def test_rr1_pending_offers_an_approved_release_as_bigger(flow, tmp_path):
    _assert_cut(flow)
    project = tmp_path / "project"
    support.write(project, {"governance/framework.lock": f'release:\n  version: "{support.N_VERSION}"\n',
                            ".copier-answers.yml": f"_commit: v{support.N_VERSION}\n"})
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    out = support.call(home, "gov.update.pending:pending", [support.path_arg(project)],
                       {"source": support.path_arg(flow["repo"])})
    report = out.returned("gov.update.pending.pending")
    assert report.get("pending") is True and report.get("newest") == flow["case"].version \
        and report.get("kind") == "bigger", report


def test_rr1_a_failed_check_after_an_approved_release_rolls_the_pin_back(base, tmp_path):
    flow = _cut(base, tmp_path, "ok_rollback", real_repin=True)
    _assert_cut(flow)
    result, home = flow["out"].result.get("repin") or {}, flow["home"]
    assert result.get("status") == "rolled_back" and result.get("check") == "search", result
    assert home.target() == (home.old_pin / "bin" / "gov").resolve(), f"the link names {home.target()}"
    assert home.burned_file.read_text(encoding="utf-8").splitlines() == [flow["case"].version]
    sent = support.pushes(flow["pushes"])
    assert len(sent) == 1, f"not one push: {sent}"
    text = sent[0][-1]
    assert "patch release" not in text.lower() and "(patch," not in text and flow["case"].version in text, text


def test_rr1_the_push_text_of_an_approved_release_fits_190_characters(tmp_path):
    out = support.call(tmp_path, "gov.release.repin:push_text", ["99.99.99", 8, "1b2c3d4e" + "f" * 32, "READY"],
                       {"kind": "approved"})
    text = out.returned("push_text with kind approved")
    _no_patch_wording(text, "the push")
    assert len(text) <= support.PUSH_LIMIT, f"{len(text)} characters: {text!r}"
    assert "99.99.99" in text and re.search(r"\b8 fixes\b", text) and "1b2c3d4e" in text and "READY" in text \
        and text.endswith(f"Roll back: {support.ROLLBACK_LINE}"), text


# --------------------------------------------------------------------------
# RR-1: an approved range passes only G1; the other gates stand as for a patch
# --------------------------------------------------------------------------

def _tag_it(repo):
    support.git(repo, "tag", "v0.2.0", "HEAD~1")


@pytest.mark.parametrize("gate, planted", [
    ("G0", {"authority_on": False}), ("G2", {"suite": False}), ("G3", {"verdict": "NOT_READY"}),
    ("G4", {"plant": _tag_it})], ids=["G0", "G2", "G3", "G4"])
def test_rr1_an_approved_range_is_still_held_by_the_other_gates(base, tmp_path, gate, planted):
    """G0 passes on the base (it is read before the rule)."""
    flow = _cut(base, tmp_path, "ok_mixed", **planted)
    support.assert_gate(flow["out"].refused(gate), gate, f"an approved range with {gate} red")
    assert not support.difference(flow["before"], support.snapshot(flow["repo"])), "a refused cut changed something"
    assert flow["home"].state() == flow["home_before"] and not flow["repin"], "the pins changed or the re-pin ran"


# --------------------------------------------------------------------------
# RR-2: what still refuses
# --------------------------------------------------------------------------

REFUSING = (*support.LACKS, *support.VERSIONS)


def _assert_bigger(case, details, message, commit):
    assert details.get("kind") == "bigger", f"{case.name}: not answered bigger: {details}"
    assert details.get("from") == support.N_VERSION and details.get("commit") == commit, details
    _failed(details["rules"], details.get("failed"), case)
    support.assert_approvals(details.get("approvals"), case)
    for token in case.lacking:
        assert token in message, f"{case.name}: the refusal's message does not name {token}: {message!r}"


@pytest.mark.parametrize("name", REFUSING)
def test_rr2_the_check_refuses_as_bigger_naming_each_item_and_what_it_lacks(base, tmp_path, home, name):
    case, repo, run = _check(base, tmp_path, home, name)
    details = support.refusal(run)
    assert run.returncode == 1, run.describe()
    _assert_bigger(case, details, run.envelope()["error"].get("message") or "", support.rev(repo))


@pytest.mark.parametrize("name", REFUSING)
def test_rr2_the_cut_refuses_at_g1_as_bigger_and_changes_nothing(base, tmp_path, name):
    flow = _cut(base, tmp_path, name)
    case, out = flow["case"], flow["out"]
    details = out.refused(name)
    support.assert_gate(details, "G1", name, rule=case.failed[0])
    _assert_bigger(case, details, out.error.get("message") or "", flow["c"])
    assert not support.difference(flow["before"], support.snapshot(flow["repo"])), f"{name}: the cut changed something"
    assert flow["home"].state() == flow["home_before"], f"{name}: the pins or the link changed"
    assert not flow["rehearse"] and not flow["repin"] and not support.pushes(flow["pushes"], wait_s=0), \
        f"{name}: something ran after a red G1"


def test_rr2_a_minor_bump_with_nothing_to_approve_is_bigger_not_approved(base, tmp_path, home):
    case = base.cases["minor"]
    repo = support.make_case(base, tmp_path / "repo", case, authority_on=False)
    run = support.release(repo, home.path, case.version, "--check")
    details = support.refusal(run)
    assert details.get("kind") == "bigger" and details.get("failed") == ["P1"], details
    assert details.get("approvals") == [], f"a range with no item has approvals {details.get('approvals')!r}"


def test_rr2_a_decision_added_to_the_register_but_not_committed_does_not_count(base, tmp_path, home):
    entry = support.register_entry(support.UNKNOWN, "ACCEPTED (owner, 2026-11-24)")
    case, repo, run = _check(base, tmp_path, home, "lack_unknown",
                             uncommitted={support.REGISTER_REL: support.REGISTER + entry})
    _assert_bigger(case, support.refusal(run), run.envelope()["error"].get("message") or "", support.rev(repo))
