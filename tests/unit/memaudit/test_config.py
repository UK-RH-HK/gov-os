"""W2-204: the repository's own memory-audit configuration (``config``), the tables that read it and the small parts
of ``brief``, ``deliver`` and ``fresh``. Planted files under ``tmp_path`` only."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from gov.memaudit import brief, config, deliver, fresh, measure, say, tables
from gov.memaudit.common import UsageError

GOOD = {
    "version": 1, "repository": "Second Harbour", "half_size": 10,
    "categories": [{"name": "decision", "count": 5, "about": "what was decided"},
                   {"name": "berth-spec", "count": 4}, {"name": "nonexistent-id", "count": 1}],
    "domains": [{"name": "records", "paths": ["records/**"]}, {"name": "code", "paths": ["app/*.py", "tool.sh"]}],
    "subsystems": [{"name": "capture-flow", "record_key": "feature", "values": ["F01"]},
                   {"name": "tide-engine", "paths": ["app/engine/**"]}],
    "spread": {"domain_min": 2, "subsystem_max": 5}, "exclude": ["archive/**", "docs/audit/memory-*/**"],
    "control": {"set": "second-control", "part": "visible", "size": 24, "baseline": "first", "spread": 2},
}


def raw(doc) -> bytes:
    return yaml.safe_dump(doc, sort_keys=False).encode()


def changed(**over):
    doc = yaml.safe_load(raw(GOOD))
    doc.update(over)
    return {k: v for k, v in doc.items() if v is not ...}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.delenv(config.ENV, raising=False)
    root = tmp_path / "repo"
    for rel, text in {"records/a.md": "---\nfeature: F01\n---\nbody\n", "records/b.md": "no front matter\n",
                      "app/main.py": "x = 1\n", config.PATH: raw(GOOD).decode()}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "one"]):
        subprocess.run(["git", "-C", str(root), *args], check=True)
    return root


def head(repo) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def test_parse_returns_the_file_s_rows_in_order():
    cfg = config.parse(raw(GOOD))
    assert (cfg.repository, cfg.half_size, cfg.min_kept) == ("Second Harbour", 10, 9)
    assert list(cfg.quotas.items()) == [("decision", 5), ("berth-spec", 4), ("nonexistent-id", 1)]
    assert cfg.domain_names == ["records", "code"] and cfg.subsystem_names == ["capture-flow", "tide-engine"]
    assert (cfg.spread.domain_min, cfg.spread.subsystem_max) == (2, 5) and cfg.control.baseline == "first"
    assert cfg.domain_min(9) == 2 and cfg.subsystem_max(9) == 4  # ceil(2 x 9 / 10), floor(5 x 9 / 10)


def test_control_none_and_an_absent_spread():
    cfg = config.parse(raw(changed(control="none", spread=..., half_size=40,
                                   categories=[{"name": "nonexistent-id", "count": 40}])))
    assert cfg.control is None and (cfg.spread.domain_min, cfg.spread.subsystem_max) == (4, 10)


@pytest.mark.parametrize("over, line", [
    ({"colour": 1}, "MA-CONFIG-KEY colour"),
    ({"control": {**GOOD["control"], "colour": 1}}, "MA-CONFIG-KEY control.colour"),
    ({"domains": [{"name": "records", "paths": ["records/**"], "colour": 1}]}, "MA-CONFIG-KEY domains[0].colour"),
    ({"control": {**GOOD["control"], "baseline": "second"}}, "MA-CONFIG-FORM control.baseline: not an integer or first"),
    ({"half_size": 11}, "MA-CONFIG-QUOTA sum 10 of 11"),
    ({"half_size": ...}, "MA-CONFIG-FORM half_size: missing"),
    ({"categories": [{"name": "decision", "count": 10}]}, "MA-CONFIG-FORM categories: nonexistent-id absent"),
    ({"domains": [{"name": "a", "paths": ["x"]}, {"name": "a", "paths": ["y"]}]},
     "MA-CONFIG-FORM domains[1].name: a duplicate name"),
    ({"subsystems": [{"name": "s", "paths": ["x"], "record_key": "k", "values": ["v"]}]},
     "MA-CONFIG-FORM subsystems[0]: paths and a record key in one row"),
])
def test_the_first_fault_is_named_by_its_key_path_only(over, line):
    with pytest.raises(config.ConfigError) as e:
        config.parse(raw(changed(**over)))
    assert e.value.line == line and e.value.code == line.split()[0]


def test_a_file_that_is_not_yaml_names_no_text_of_it():
    with pytest.raises(config.ConfigError) as e:
        config.parse(b"version: [1\nquorblat: {")
    assert e.value.code == "MA-CONFIG-FORM" and "quorblat" not in e.value.line


def test_load_takes_the_named_file_then_the_commit_s_then_the_working_tree_s(repo, tmp_path, monkeypatch):
    at = head(repo)
    (repo / config.PATH).write_text(raw(changed(repository="Working Tree")).decode())
    assert config.load(repo, at).repository == "Second Harbour" and config.load(repo).repository == "Working Tree"
    trial = tmp_path / "trial.yaml"
    trial.write_bytes(raw(changed(repository="Trial")))
    monkeypatch.setenv(config.ENV, str(trial))
    assert config.load(repo, at).repository == "Trial"
    monkeypatch.setenv(config.ENV, "")  # set and empty: not named
    assert config.load(repo, at).repository == "Second Harbour"


def test_no_file_is_refused_and_never_defaulted(repo, tmp_path):
    (repo / config.PATH).unlink()
    for call in (lambda: config.load(repo), lambda: config.load(tmp_path, None), lambda: config.load(None)):
        with pytest.raises(config.ConfigError) as e:
            call()
        assert e.value.line == "MA-CONFIG-MISSING write governance/project/memory-audit.yaml"


def test_a_domain_no_tracked_file_matches_is_named(repo, tmp_path, monkeypatch):
    trial = tmp_path / "trial.yaml"
    trial.write_bytes(raw(changed(domains=[*GOOD["domains"], {"name": "plans", "paths": ["plans/**"]}])))
    monkeypatch.setenv(config.ENV, str(trial))
    with pytest.raises(config.ConfigError) as e:
        config.load(repo, head(repo))
    assert e.value.line == "MA-CONFIG-DOMAIN-EMPTY plans"
    assert config.load(repo).domain_names[-1] == "plans"  # without a commit the tracked files are not looked at


def test_patterns_match_as_the_old_table_did_and_a_star_before_a_folder():
    assert config.matches("src/a/b.py", "src/**") and not config.matches("src", "src/**")
    assert config.matches("tools/nightly_x.sh", "tools/nightly*") and not config.matches("tools/a/nightly", "tools/*")
    assert config.matches("docs/audit/memory-1/x.md", "docs/audit/memory-*/**")
    assert not config.matches("docs/audit/other/x.md", "docs/audit/memory-*/**")
    assert config.matches("a.md", "a.md") and not config.matches("a.md.bak", "a.md")


def test_a_record_key_row_counts_by_the_first_source_s_front_matter(repo):
    cfg, at = config.load(repo), tables.reader(repo, head(repo))
    domains, subsystems = tables.spread(["records/a.md", "records/b.md", "app/engine/x.py", "app/main.py", None],
                                        cfg, at)
    assert domains == {"records": 2, "code": 1, "none": 2}  # app/engine/x.py is below app/, not a name inside it
    assert subsystems == {"capture-flow": 1, "tide-engine": 1, "none": 3}
    assert tables.spread(["records/a.md"], cfg)[1]["capture-flow"] == 0  # no reader: a record-key row holds nothing
    assert tables.thin_domains(domains, 5, cfg) == [] and tables.thin_domains({"records": 0, "code": 1}, 10, cfg) == [
        "records", "code"]
    assert tables.heavy_subsystems({"capture-flow": 6}, 10, cfg) == ["capture-flow"]


def test_front_matter_is_the_first_block_only():
    assert tables.front_matter(b"---\nfeature: F01\n---\n---\nfeature: F02\n---\n") == {"feature": "F01"}
    assert tables.front_matter(b"text\n---\nfeature: F01\n---\n") == {} and tables.front_matter(None) == {}
    assert tables.front_matter(b"---\nfeature: [\n---\n") == {} and tables.front_matter(b"---\nfeature: F01\n") == {}


def test_the_first_baseline_is_the_first_measure_s_own_figure(tmp_path):
    import json
    root = tmp_path / "sets"
    p = {"root": root, "run": root / "runs" / "memory-audit-26111902"}
    cfg = config.parse(raw(GOOD))
    assert measure.last_control(p, cfg.control) == (None, None) and measure.last_control(p, None) == (None, None)
    earlier = root / "runs" / "memory-audit-26111901"
    earlier.mkdir(parents=True)
    (earlier / "ledger.jsonl").write_text(json.dumps({"event": "control", "ok": True, "hit5": 20}) + "\n")
    assert measure.last_control(p, cfg.control) == (20, "memory-audit-26111901")
    (earlier / "FIGURES.json").write_text(json.dumps({"control": {"hit5": 21}}))
    assert measure.last_control(p, cfg.control) == (21, "memory-audit-26111901")


def test_a_brief_is_filled_from_the_configuration_and_keeps_no_field():
    cfg = config.parse(raw(GOOD))
    for kind in brief.KINDS:
        text = brief.render(kind, cfg, "a" * 40, 1)
        assert "{{" not in text and "Second Harbour" in text and "a" * 40 in text
        assert "`archive/**`" in text and "berth-spec" in text and "`capture-flow`" in text
    writer = brief.render("writer", cfg, "a" * 40, 2)
    assert "`records`, `code`, `none`" in writer and "| Count | 5 | 4 | 1 |" in writer
    assert "6 questions are drawn from `changed` and 4" in writer  # 24 of 40, scaled to a half of 10


def test_a_writer_s_result_counts_areas_in_the_configuration_s_domains():
    cfg = config.parse(raw(GOOD))
    good = {"questions": 3, "by_kind": {"fact": 3}, "by_area": {"records": 1, "code": 1, "none": 1}}
    assert deliver.result_ok(good, cfg)
    assert not deliver.result_ok({**good, "by_area": {"kernel": 3}}, cfg)  # another repository's areas
    assert not deliver.result_ok({**good, "by_area": {"records": 2}}, cfg)  # does not sum
    assert not deliver.result_ok({**good, "by_kind": {"fact": True}}, cfg) and not deliver.result_ok(None, cfg)


def test_a_set_folder_holds_plain_question_files_only(tmp_path):
    folder = tmp_path / "set"
    folder.mkdir()
    assert deliver.set_files(folder) is None  # none at all
    (folder / "q01.yaml").write_text("x")
    assert [f.name for f in deliver.set_files(folder)] == ["q01.yaml"]
    (folder / "q02.yaml").symlink_to(folder / "q01.yaml")
    assert deliver.set_files(folder) is None
    (folder / "q02.yaml").unlink()
    (folder / "notes.txt").write_text("x")
    assert deliver.set_files(folder) is None


def test_notes_need_their_three_headings_in_order():
    good = "# Cross-check notes\n## Questions\nq01 | accept | - | also: none | fine\n## The set\nset codes: none\n"
    assert deliver.notes_ok(good)
    assert not deliver.notes_ok(good.replace("## Questions\n", ""))
    assert not deliver.notes_ok(good.replace("# Cross-check notes\n", ""))
    assert not deliver.notes_ok("# Cross-check notes\n## The set\n## Questions\n")


def test_the_halves_are_named_from_the_tag():
    assert fresh.names("20261119") == ("memory-audit-26111901", "memory-audit-26111902")
    assert fresh.names("20261119b") == ("memory-audit-26111903", "memory-audit-26111904")
    for bad in ("2026111", "20261119a", "20261119bb", "", None):
        with pytest.raises(UsageError):
            fresh.names(bad)


def test_say_prints_fresh_s_two_lines_whole_and_refuses_any_other_use_of_the_word():
    assert not say.refused("FRESH plan: visible memory-audit-26111901 hidden memory-audit-26111902 at 0123456789ab")
    assert not say.refused("FRESH VERDICT hidden right 37 of 40 (92.5 %): misses")
    assert say.refused("FRESH VERDICT hidden right 37 of 40 (92.5 %): misses q01")
    assert say.refused("FRESH plan: visible memory-audit-26111901 hidden fixtures/x at 0123456789ab")
    assert say.refused("STEP hidden") and say.refused("x hidden/q01.yaml")
