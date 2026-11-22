"""S2 (what reads kind.json) and S9 (a burned release is never offered): ``gov.update.pending.pending``.

A planted source holds 0.1.1 and a release 0.1.2 whose record carries ``kind.json`` (``patch`` or ``bigger``); a
project holds 0.1.1 (its lock). ``pending(project, source=...)`` runs in a child process whose ``HOME`` is a scratch
home, whose ``~/.local/share/gov-os/burned`` lists 0.1.2 in the burned case. README, "S2, S9".
"""

import json

import pytest

import w2_209_support as support


def _kind(kind):
    rules = {r: {"pass": kind == "patch", "detail": "planted"} for r in support.RULES}
    return json.dumps({"version": support.X, "kind": kind, "from": support.N_VERSION, "commit": "0" * 40,
                       "rules": rules}, indent=2) + "\n"


@pytest.fixture(scope="module")
def sources(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-pending")
    builder = folder / "builder"
    (builder / "tmp").mkdir(parents=True)
    found = {}
    for kind in ("patch", "bigger"):
        repo = support.make_case(base, folder / f"source-{kind}", "clean", authority_on=False)
        support.record(repo, builder, support.X, extra={"kind.json": _kind(kind)})
        found[kind] = repo
    project = folder / "project"
    support.write(project, {"governance/framework.lock": f'release:\n  version: "{support.N_VERSION}"\n',
                            ".copier-answers.yml": f"_commit: v{support.N_VERSION}\n"})
    return found, project


def _pending(home, project, source):
    out = support.call(home, "gov.update.pending:pending", [support.path_arg(project)],
                       {"source": support.path_arg(source)})
    return out.returned("gov.update.pending.pending")


@pytest.mark.parametrize("kind", ["patch", "bigger"])
def test_s2_pending_reads_the_kind_of_the_release_record(sources, tmp_path, kind):
    """Pins W2-17's reading of kind.json (passes on the base): the form S2 writes is the form it reads."""
    found, project = sources
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    report = _pending(home, project, found[kind])
    assert report.get("pending") is True and report.get("newest") == support.X, report
    assert report.get("kind") == kind, f"the kind read is {report.get('kind')!r}, not {kind}: {report}"


def test_s9_a_burned_patch_release_is_never_offered(sources, tmp_path):
    found, project = sources
    home = tmp_path / "home"
    (home / "tmp").mkdir(parents=True)
    offered = _pending(home, project, found["patch"])
    assert offered.get("pending") is True, f"control: 0.1.2 is not offered before it is burned: {offered}"
    burned = home / ".local" / "share" / "gov-os" / "burned"
    burned.parent.mkdir(parents=True)
    burned.write_text(f"{support.X}\n", encoding="utf-8")
    report = _pending(home, project, found["patch"])
    assert report.get("pending") is False, f"a burned release is offered: {report}"
    assert report.get("burned") is True, f"the report does not say the release is burned: {report}"
    assert report.get("held") == support.N_VERSION, f"the report does not hold the project at 0.1.1: {report}"
    assert "burned" in str(report.get("reason")) and "burned" in str(report.get("summary")), \
        f"the reason and summary do not say burned: {report}"
