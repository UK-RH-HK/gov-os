"""S9 and S10: the briefs are filled from the repository's own file, and a session's ``out/`` folder is delivered by
command. ``--from`` names the ``out/`` folder itself (the README's reading)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil

import pytest
import yaml

import w2_204_stages as ST
import w2_204_support as K
from w2_204_support import HIDDEN, W171

GOV_OS_AUDIT = W171.AUDIT


def token(name: str) -> re.Pattern:
    return re.compile(rf"(?<![\w-]){re.escape(name)}(?![\w-])")


def quota_stated(text: str, name: str, count: int) -> bool:
    """The category's name with its count: on one line, or in a table whose header row holds the names and whose
    next rows hold the counts."""
    number, lines = re.compile(rf"(?<![\w.-]){count}(?![\w.-])"), text.splitlines()
    if any(token(name).search(x) and number.search(token(name).sub("", x)) for x in lines):
        return True
    rows = [[c.strip(" `*") for c in x.strip().strip("|").split("|")] for x in lines if x.strip().startswith("|")]
    for at, row in enumerate(rows):
        if name in row and any(len(later) > row.index(name) and later[row.index(name)] == str(count)
                               for later in rows[at + 1:at + 3]):
            return True
    return False


class Briefs:
    """Every brief call of the module, made once: the second repository's (its own file at the commit) and Gov OS's
    (W2-171's planted repository with ``MEMAUDIT_CONFIG`` naming Gov OS's file)."""

    def __init__(self, base):
        self.world = world = K.build(base / "w")
        self.out = {name: base / "sessions" / name for name in ("writer-1", "writer-2", "checker-1", "gov-os", "gov-os-checker")}
        self.writer_1 = world.brief("writer", HIDDEN, self.out["writer-1"], "--since", world.base_commit)
        world.write_half(HIDDEN, K.clean_specs())
        world.write_notes(HIDDEN, 1, {"q05": ("revise", "R6-SPAN-MISSES")})
        self.delivered = {p.name: p.read_bytes() for p in world.hidden(HIDDEN).glob("q*.yaml")}
        self.checker_1 = world.brief("checker", HIDDEN, self.out["checker-1"])
        self.writer_2 = world.brief("writer", HIDDEN, self.out["writer-2"], round_no=2)
        W171.build(base / "g")
        self.gov_os = W171.World(base / "g")
        flags = ["--sets-root", self.gov_os.sets, "--audit", GOV_OS_AUDIT, "--commit", self.gov_os.audit_commit,
                 "--repo", self.gov_os.repo, "--round", 1]
        self.gov_os_writer = ST.gov_os_call(self.gov_os, "cli", "brief", ["--kind", "writer", *flags, "--out", self.out["gov-os"]])
        self.gov_os.write_set(W171.clean_specs())
        self.gov_os_checker = ST.gov_os_call(self.gov_os, "cli", "brief",
                                             ["--kind", "checker", *flags, "--out", self.out["gov-os-checker"]])

    def text(self, name: str) -> str:
        path = self.out[name] / "brief.md"
        assert path.is_file(), f"no brief.md in the {name} folder"
        return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def briefs(tmp_path_factory) -> Briefs:
    return Briefs(tmp_path_factory.mktemp("w2-204-briefs"))


# -- S9 ----------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("name, kind, round_no", [("writer_1", "writer", 1), ("writer_2", "writer", 2),
                                                  ("checker_1", "checker", 1)])
def test_s9_brief_prints_one_line_with_the_brief_s_sha256_and_no_path(briefs, name, kind, round_no):
    call = getattr(briefs, name)
    text = briefs.text(name.replace("_", "-"))
    brief_line = f"BRIEF {kind} round {round_no} {hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]}"
    lines = call.lines
    assert call.code == 0 and lines and lines[0] == brief_line, call
    if kind == "writer":  # FM-5: the BRIEF line, then exactly one LAUNCH writer line (it may carry the CTO's own --out folder)
        assert len(lines) == 2 and lines[1].startswith("LAUNCH writer "), call
    else:
        assert lines == [brief_line], call
    assert "/" not in brief_line and text.strip() and text[:200] not in call.text


def test_s9_the_second_repository_s_writer_brief_is_filled_from_its_file(briefs):
    text, world = briefs.text("writer-1"), briefs.world
    assert K.REPOSITORY in text and world.audit_commit[:12] in text and token("40").search(text)
    for name, count, about in K.CATEGORIES:
        assert quota_stated(text, name, count), f"the quota of {name} is not stated"
        assert about in text, f"the about text of {name} is missing"
    for name in [*K.DOMAIN_NAMES, *K.SUBSYSTEM_NAMES]:
        assert token(name).search(text), f"{name} is not named"
    assert K.EXCLUDED in text and token("4").search(text) and token("10").search(text)


def test_s9_the_second_repository_s_briefs_hold_no_name_of_gov_os_s_tables(briefs):
    for name in ("writer-1", "writer-2", "checker-1"):
        text = briefs.text(name)
        assert "Gov OS" not in text
        for other in (*K.GOV_OS_ONLY_CATEGORIES, "tickets", "kernel"):
            assert not token(other).search(text), f"the {name} brief names Gov OS's {other}"


@pytest.mark.parametrize("name, domains", [("writer-1", K.DOMAIN_NAMES),
                                           ("gov-os", ["decisions", "tickets", "plan", "contract", "code"])])
def test_s9_by_area_is_counted_in_the_file_s_domains_and_none(briefs, name, domains):
    text = briefs.text(name)
    assert "by_area" in text
    after = text[text.index("by_area"):]
    section = after[:after.index("\n## ")] if "\n## " in after else after
    for domain in [*domains, "none"]:
        assert token(domain).search(section), f"by_area does not list {domain}"
    for old in ("kernel", "operations"):   # the approved brief's own areas (F-2): never a domain of either file
        assert not re.search(rf"`{old}`", section)


def test_s9_gov_os_s_brief_is_filled_from_gov_os_s_file_and_holds_nothing_of_the_second_repository(briefs):
    assert briefs.gov_os_writer.code == 0, briefs.gov_os_writer
    text = briefs.text("gov-os")
    config = yaml.safe_load(K.GOV_OS_CONFIG.read_text(encoding="utf-8"))
    assert "Gov OS" in text and briefs.gov_os.audit_commit[:12] in text and K.REPOSITORY not in text
    for row in config["categories"]:
        assert quota_stated(text, row["name"], row["count"]) and row["about"] in text, row["name"]
    for name in ("harbour-task", "berth-spec", "tide-scenario", "pilot-report", "harbour-tasks", "berth-specs",
                 "pilot-reports", *K.SUBSYSTEM_NAMES):
        assert name not in text, f"Gov OS's brief names the second repository's {name}"
    checker = briefs.text("gov-os-checker")
    assert briefs.gov_os_checker.code == 0 and "Gov OS" in checker and "harbour" not in checker


def test_s9_the_selection_lists_the_commit_s_tracked_paths_less_the_excluded(briefs):
    world, folder = briefs.world, briefs.out["writer-1"]
    assert (folder / "input" / "selection.json").is_file(), briefs.writer_1
    selection = json.loads((folder / "input" / "selection.json").read_text(encoding="utf-8"))
    assert {"commit", "last_audit", "seed_sha256", "changed", "sample"} <= set(selection)
    tracked = set(W171.git(world.repo, "ls-tree", "-r", "--name-only", world.audit_commit, home=world.home).split())
    listed = [*selection["changed"], *selection["sample"]]
    assert selection["commit"] == world.audit_commit and selection["last_audit"] == world.base_commit
    assert set(listed) <= tracked and len(listed) == len(set(listed)) and len(selection["sample"]) <= 300
    assert not [p for p in listed if p.startswith("archive/")], "an excluded path is listed"
    assert sorted(selection["changed"]) == ["app/engine/e21.py", "records/tasks/T-07.md"]   # archive/old.md changed too
    assert sorted(listed) == sorted(p for p in tracked if not p.startswith("archive/"))    # under 300: every path


def test_s9_the_seed_is_written_beside_the_brief_and_the_selection_holds_its_sha256(briefs):
    folder = briefs.out["writer-1"]
    assert (folder / "seed.txt").is_file(), briefs.writer_1
    raw = (folder / "seed.txt").read_bytes()
    seed = int(raw.decode().strip())
    selection = json.loads((folder / "input" / "selection.json").read_text(encoding="utf-8"))
    forms = {hashlib.sha256(x).hexdigest() for x in (raw, f"{seed}\n".encode(), str(seed).encode())}
    assert selection["seed_sha256"] in forms


def test_s9_the_set_s_selection_json_in_the_sets_root_equals_the_folder_s(briefs):
    kept = briefs.world.set_dir(HIDDEN) / "selection.json"
    assert kept.is_file(), briefs.writer_1
    assert json.loads(kept.read_text(encoding="utf-8")) == json.loads(
        (briefs.out["writer-1"] / "input" / "selection.json").read_text(encoding="utf-8"))


def test_s9_a_round_2_writer_folder_holds_the_delivered_set_and_the_round_1_notes(briefs):
    folder, world = briefs.out["writer-2"] / "input", briefs.world
    assert (folder / "set").is_dir(), briefs.writer_2
    assert {p.name: p.read_bytes() for p in (folder / "set").iterdir()} == briefs.delivered
    assert (folder / "notes.md").read_bytes() == (world.set_dir(HIDDEN) / "XCHECK-r1.md").read_bytes()


def test_s9_a_checker_folder_holds_the_delivered_set(briefs):
    folder = briefs.out["checker-1"] / "input" / "set"
    assert folder.is_dir(), briefs.checker_1
    assert {p.name: p.read_bytes() for p in folder.iterdir()} == briefs.delivered


def test_s9_each_brief_is_an_event_of_the_audit_s_ledger(briefs):
    events = [e for e in briefs.world.ledger(HIDDEN) if e.get("event") == "brief"]
    assert len(events) == 3, briefs.world.ledger(HIDDEN)
    assert not any(word in json.dumps(events) for word in K.planted_words())


# -- S10 ---------------------------------------------------------------------------------------------------------------
def by_area(specs: list[dict]) -> dict:
    counts = {name: 0 for name in [*K.DOMAIN_NAMES, "none"]}
    for spec in specs:
        path = K.first_path(spec)
        counts[next((name for name, patterns in K.DOMAINS
                     if any(path == p or (p.endswith("/**") and path.startswith(p[:-2])) for p in patterns)), "none")] += 1
    return counts


def writer_out(world: K.World, folder, specs=None, **over):
    """A writer session's ``out/`` folder: ``set/q*.yaml`` and ``result.json``."""
    specs = specs if specs is not None else K.clean_specs()
    out = folder / "out"
    world.write_half(HIDDEN, specs, folder=out / "set", salt=over.pop("salt", None))
    n = len(specs)
    result = {"questions": n, "by_kind": {"fact": n - 12, "procedure": 4, "decision": 6, "location": 1, "negative": 1},
              "by_area": by_area(specs)}
    result.update(over)
    (out / "result.json").write_text(json.dumps(result), encoding="utf-8")
    return out


def landed(world: K.World) -> dict:
    hidden = world.hidden(HIDDEN)
    return {p.name: p.read_bytes() for p in hidden.iterdir()} if hidden.is_dir() else {}


@pytest.mark.parametrize("entry", ["module", "cli"])
def test_s10_a_good_writer_delivery_lands_forty_files_and_prints_counts_only(world, tmp_path, entry):
    out = writer_out(world, tmp_path)
    run = world.deliver("writer", HIDDEN, out, entry=entry)
    assert run.code == 0 and run.lines == ["DELIVER writer round 1 files 40"], run
    assert landed(world) == {p.name: p.read_bytes() for p in (out / "set").iterdir()} and len(landed(world)) == 40
    assert not any(word in run.text for word in K.planted_words())


def _other_areas(out):
    doc = json.loads((out / "result.json").read_text())
    doc["by_area"] = {"contract": 4, "decisions": 8, "kernel": 3, "code": 15, "tests": 0, "operations": 4, "docs": 6}
    (out / "result.json").write_text(json.dumps(doc))


def _no_sum(out):
    doc = json.loads((out / "result.json").read_text())
    doc["by_area"]["decisions"] += 1
    (out / "result.json").write_text(json.dumps(doc))


def _stray(out):
    (out / "set" / "notes.txt").write_text("a stray file\n")


def _link(out):
    target = out.parent / "elsewhere-q40.yaml"
    shutil.move(out / "set" / "q40.yaml", target)
    os.symlink(target, out / "set" / "q40.yaml")


@pytest.mark.parametrize("fault, code", [(_other_areas, "DL-RESULT"), (_no_sum, "DL-RESULT"), (_stray, "DL-SET"),
                                         (_link, "DL-SET")], ids=["other-areas", "no-sum", "stray-file", "symlink"])
def test_s10_a_delivery_that_fails_its_form_is_refused_and_nothing_is_copied(world, tmp_path, fault, code):
    out = writer_out(world, tmp_path)
    fault(out)
    before = W171.snapshot(world.sets)
    run = world.deliver("writer", HIDDEN, out)
    assert run.code == 1 and [x.split()[0] for x in run.lines] == [code], run
    assert W171.snapshot(world.sets) == before and landed(world) == {}
    assert not any(word in run.text for word in K.planted_words())


def test_s10_a_second_round_1_delivery_is_refused_dl_exists(world, tmp_path):
    assert world.deliver("writer", HIDDEN, writer_out(world, tmp_path / "a")).code == 0
    before = W171.snapshot(world.sets)
    run = world.deliver("writer", HIDDEN, writer_out(world, tmp_path / "b", salt="again"))
    assert run.code == 1 and [x.split()[0] for x in run.lines] == ["DL-EXISTS"], run
    assert W171.snapshot(world.sets) == before


def test_s10_round_2_moves_round_1_aside_and_leaves_only_the_new_files(world, tmp_path):
    first = writer_out(world, tmp_path / "a")
    assert world.deliver("writer", HIDDEN, first).code == 0
    old = landed(world)
    second = writer_out(world, tmp_path / "b", [s for s in K.clean_specs() if s["id"] not in ("q39", "q21")], salt="r2")
    run = world.deliver("writer", HIDDEN, second, round_no=2)
    assert run.code == 0 and run.lines == ["DELIVER writer round 2 files 38"], run
    assert landed(world) == {p.name: p.read_bytes() for p in (second / "set").iterdir()} and len(landed(world)) == 38
    aside = world.set_dir(HIDDEN) / "r1"
    assert {p.name: p.read_bytes() for p in aside.iterdir()} == old and len(old) == 40


def checker_out(world: K.World, folder, **kw):
    out = folder / "out"
    out.mkdir(parents=True)
    (out / "notes.md").write_text(world.notes_text(HIDDEN, {"q05": ("revise", "R6-SPAN-MISSES")}, **kw), encoding="utf-8")
    (out / "result.json").write_text(json.dumps({"checked": 40, "accepted": 39, "revise": 1, "rejected": 0}))
    return out


@pytest.mark.parametrize("round_no", [1, 2])
def test_s10_a_checker_s_notes_land_as_the_round_s_xcheck_file(world, tmp_path, round_no):
    world.write_half(HIDDEN, K.clean_specs())
    out = checker_out(world, tmp_path)
    run = world.deliver("checker", HIDDEN, out, round_no=round_no)
    assert run.code == 0 and len(run.lines) == 1 and run.lines[0].startswith(f"DELIVER checker round {round_no}"), run
    assert (world.set_dir(HIDDEN) / f"XCHECK-r{round_no}.md").read_bytes() == (out / "notes.md").read_bytes()
    assert not any(word in run.text for word in K.planted_words()) and "/" not in run.out


def test_s10_notes_without_the_questions_section_are_refused_dl_notes(world, tmp_path):
    world.write_half(HIDDEN, K.clean_specs())
    out = checker_out(world, tmp_path, questions=False)
    before = W171.snapshot(world.sets)
    run = world.deliver("checker", HIDDEN, out)
    assert run.code == 1 and [x.split()[0] for x in run.lines] == ["DL-NOTES"], run
    assert W171.snapshot(world.sets) == before
