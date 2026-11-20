"""F5 and S10 end to end: the plain ``gov release`` and the pushes stay as they were.

The plain form (no ``--patch``) is refused from an orchestrator session and from a session with no terminal, as
DEC-772 has it (these pin today's behaviour and pass on the base; W2-16's owner-terminal cases stay in W2-16's folder,
which the landing selects for any change under ``src/gov/release``). A full cut and re-pin (``gov.release._patch_test``
with G3 stood in and the real re-pin, in a scratch home) runs in a planted source whose ``origin`` records any contact:
nothing contacts it, the authority file is not written, and the owner gets one push. README, "F5".
"""

import pytest

import w2_209_support as support

RECORDER = """#!/bin/sh
echo "contact: $0 $*" >> {log}
exit 1
"""


def test_f5_the_plain_form_is_refused_from_an_orchestrator_session(base, tmp_path, home):
    """Pins today's behaviour (DEC-772): passes on the base."""
    repo = support.make_case(base, tmp_path / "repo", "clean")
    before = support.snapshot(repo)
    run = support.gov(repo, home.path, "release", support.X)
    assert support.refusal(run).get("reason") in ("session", "ancestry", "role")
    assert not support.difference(before, support.snapshot(repo)), "the plain form changed the repository"


def test_f5_the_plain_form_is_refused_without_a_terminal_and_without_a_role(base, tmp_path, home):
    """Pins today's behaviour (DEC-772): passes on the base."""
    repo = support.make_case(base, tmp_path / "repo", "contract")
    before = support.snapshot(repo)
    run = support.gov(repo, home.path, "release", support.X, role=None)
    assert support.refusal(run).get("reason") in ("session", "ancestry", "terminal")
    assert not support.difference(before, support.snapshot(repo)), "the plain form changed the repository"
    assert f"v{support.X}" not in support.git(repo, "tag", "--list").split()


@pytest.fixture(scope="module")
def flow(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-flow")
    repo = support.make_case(base, folder / "repo", "clean")
    contact = folder / "origin-contact.log"
    recorder = folder / "recorder"
    recorder.write_text(RECORDER.format(log=contact), encoding="utf-8")
    recorder.chmod(0o755)
    bare = folder / "origin.git"
    support.git(folder, "init", "-q", "--bare", str(bare))
    support.git(repo, "remote", "add", "origin", str(bare))
    for key in ("uploadpack", "receivepack"):
        support.git(repo, "config", f"remote.origin.{key}", str(recorder))
    support.git(repo, "config", "remote.origin.pushurl", str(bare))
    support.git(repo, "ls-remote", "origin", check=False)  # the recorder records a contact: proven, then cleared
    assert contact.exists() and "contact" in contact.read_text(), "W2-209 fixture: the recording origin records nothing"
    contact.unlink()
    authority = (repo / support.AUTHORITY_REL).read_bytes()
    c = support.rev(repo)
    record = support.good_suite(repo, folder / "records")
    home = support.make_home(folder / "home", base.n_version_commit)
    command, pushes = support.push_command(folder / "push")
    logs = folder / "logs"
    logs.mkdir()
    out = support.call(home.path, "gov.release:_patch_test", [support.path_arg(repo), support.X],
                       {"suite": support.path_arg(record),
                        "rehearse": support.standin("rehearse", log=str(logs / "rehearse.jsonl")),
                        "push": command},
                       role="orchestrator")
    return {"repo": repo, "c": c, "contact": contact, "authority": authority, "home": home, "pushes": pushes,
            "out": out}


def _done(flow):
    out = flow["out"]
    assert out.kind != "missing", support.missing_message(out, "gov.release._patch_test")
    return out.returned("the full cut and re-pin")


def test_f5_a_full_cut_and_re_pin_contacts_no_remote(flow):
    _done(flow)
    assert support.tag_type(flow["repo"], f"v{support.X}") == "tag", "the cut made no release"
    assert not flow["contact"].exists(), f"a remote was contacted:\n{flow['contact'].read_text()}"


def test_f5_the_authority_file_is_not_written_by_a_cut_or_a_re_pin(flow):
    _done(flow)
    repo = flow["repo"]
    assert (repo / support.AUTHORITY_REL).read_bytes() == flow["authority"], "the authority file changed in the run"
    later = support.git(repo, "rev-list", "--all", f"^{flow['c']}", "--", support.AUTHORITY_REL).split()
    assert not later, f"a commit made in the run touches the authority file: {later}"


def test_s10_the_full_flow_pins_the_release_and_pushes_the_owner_once(flow):
    result = _done(flow)
    home = flow["home"]
    pin = home.share / f"pin-{flow['c'][:12]}"
    assert home.target() == (pin / "bin" / "gov").resolve(), f"the link names {home.target()}: {result}"
    sent = support.pushes(flow["pushes"])
    assert len(sent) == 1, f"not one push: {sent}"
    text = sent[0][-1]
    assert len(text) <= support.PUSH_LIMIT and text.startswith(f"Gov OS {support.X} released (patch, 2 fixes).") \
        and flow["c"][:8] in text and "READY" in text and support.ROLLBACK_LINE in text, text
