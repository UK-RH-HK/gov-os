"""S1 (success-1), F1 (failure-1, assessment half), F4 (failure-4), F5 (failure-5, secret half); I1, I2, I4.

``gov adopt --lite --stage MA --out <folder>`` on a planted repository: the memory-assessment record, outside the
project, every field I1 names, each planted item under its category, the secret by rule id only, the repository byte
identical before and after; A3 refuses without the assessment and cites its sha256 with it.
"""

from __future__ import annotations

import hashlib
import json

import pytest

import w2_88_support as W

SECRET_RULE = "aws-access-token"   # the rule id of gitleaks' default set that detects W2-81's cloud-access-key form


@pytest.fixture
def orchard(box):
    return W.plant_orchard(box.base)


def assess(orchard, box, host, *, name="out", extra=(), tools=()):
    out = box.base / name
    environment = W.env(box, host, tools=tools)
    run = W.run_adopt(orchard.root, environment, "MA", "--out", str(out), *extra)
    W.assert_offered(run, "MA")
    return run, out


@pytest.fixture
def assessed(orchard, box, host):
    """A function (called in the case, so a missing stage is the case's failure, not a fixture error)."""
    def make():
        run, out = assess(orchard, box, host)
        W.assert_ok(run, "the memory assessment (MA)")
        record = out / W.ASSESSMENT
        assert record.is_file(), f"MA wrote no {W.ASSESSMENT} under --out\n{run.describe()}"
        return orchard, run, out, W.read_json(record)
    return make


def test_the_assess_module_states_its_limit_and_its_entry_point():
    """I4: ``assess.assess(root, out)`` and ``assess.FILE_LIMIT_BYTES`` exist (red: no gov.adopt.assess on the base)."""
    from gov.adopt import assess as module
    assert callable(module.assess), "gov.adopt.assess.assess is not callable"
    assert isinstance(module.FILE_LIMIT_BYTES, int) and module.FILE_LIMIT_BYTES > 0


def test_s1_the_record_holds_every_field_i1_names(assessed):
    orchard, run, out, record = assessed()
    head = orchard.commit
    assert isinstance(record.get("commit"), str) and head.startswith(record["commit"][:12]) and len(record["commit"]) >= 12
    for key in ("tracked_files", "tracked_bytes", "commits", "peak_rss_bytes"):
        assert isinstance(record.get(key), int) and record[key] > 0, f"{key} is no positive count: {record.get(key)!r}"
    assert record["commits"] == 2, f"the planted repository has 2 commits, the record says {record['commits']}"
    assert "python" in json.dumps(record.get("languages")).lower(), f"languages names no python: {record.get('languages')}"
    for key in ("largest", "binary", "generated", "minified", "vendored", "secrets", "no_route"):
        assert isinstance(record.get(key), list), f"{key} is no list"
    estimate = record.get("estimate")
    assert isinstance(estimate, dict), "no estimate block"
    for key in ("index_seconds", "peak_rss_bytes", "disk_bytes", "free_memory_bytes", "free_disk_bytes"):
        assert isinstance(estimate.get(key), (int, float)) and estimate[key] >= 0, f"estimate.{key}: {estimate.get(key)!r}"
    assert estimate["free_memory_bytes"] > 0 and estimate["free_disk_bytes"] > 0, "the machine's free memory and disk are read"
    assert estimate.get("envelope"), "estimate.envelope (DEC-078's envelope) is empty"


def test_s1_the_counts_are_the_repositorys(assessed):
    orchard, run, out, record = assessed()
    names = W.git(orchard.root, "ls-files").splitlines()
    sizes = sum(int(W.git(orchard.root, "cat-file", "-s", f"HEAD:{n}")) for n in names)
    assert record["tracked_files"] == len(names), f"tracked_files {record['tracked_files']} != {len(names)}"
    assert record["tracked_bytes"] == sizes, f"tracked_bytes {record['tracked_bytes']} != {sizes}"
    first = record["largest"][0]
    assert W.holds([first], W.PLANT["over_limit"]), f"the largest file is {W.PLANT['over_limit']}, the record lists {first!r} first"


def test_s1_each_planted_item_is_under_its_category(assessed):
    orchard, run, out, record = assessed()
    P = W.PLANT
    assert W.holds(record["vendored"], P["vendored"], "folder"), f"vendored folder not listed by folder: {record['vendored']}"
    assert W.holds(record["generated"], P["generated"], "header"), f"generated file not listed by header: {record['generated']}"
    assert W.holds(record["minified"], P["minified"], "name"), f"minified file not listed by name: {record['minified']}"
    assert W.holds(record["binary"], P["binary"]), f"binary not listed: {record['binary']}"
    no_route = record["no_route"]
    assert W.holds(no_route, P["over_limit"], reason="over-limit"), f"file over the limit not in no_route: {no_route}"
    assert W.holds(no_route, P["wide_line"], reason="over-limit"), f"file with a line over READ_CHARS not in no_route: {no_route}"
    assert W.holds(no_route, P["unsupported"], reason="unsupported-language"), f"unsupported language not in no_route: {no_route}"
    assert not W.holds(record["vendored"] + record["generated"] + record["minified"] + record["binary"], "src/app/main.py"), \
        "a plain source file is listed as vendored, generated, minified or binary"


def test_s1_the_secret_is_named_by_rule_id_only(assessed):
    orchard, run, out, record = assessed()
    secrets = record["secrets"]
    assert len(secrets) == 1, f"one tracked file holds a secret, the record lists {len(secrets)}"
    entry = secrets[0]
    assert set(entry) == {"path", "rule"}, f"a secrets item is {{path, rule}} and nothing else: {sorted(entry)}"
    assert entry["path"] == W.PLANT["secret"] and entry["rule"] == SECRET_RULE, f"found {entry}"
    W.assert_no_secret(orchard.secret, W.all_text(out), "the memory-assessment record")


def test_s1_f5_no_output_holds_the_secrets_value(orchard, box, host):
    """F5 / S1: a grep of every record, log and captured output of the run (--json and the human form) for the value."""
    run, out = assess(orchard, box, host, name="out-json")
    human = W.S124.gov(orchard.root, W.env(box, host), "adopt", "--lite", "--stage", "MA", "--out", str(box.base / "out-human"),
                       "--session", W.SESSION)
    assert run.returncode == 0 and human.returncode == 0, f"MA failed\n{run.describe()}\n{human.describe()}"
    texts = W.all_text(out, box.base / "out-human", runs=(run, human))
    assert len(texts) >= 4, "the run left nothing to grep"
    W.assert_no_secret(orchard.secret, texts, "the assessment's outputs")


def test_s1_f5_no_hidden_question_is_read_or_printed(orchard, box, host):
    """F5's second half: a planted hidden question (outside the repository, in a sets root the environment names) has a
    unique word; a grep of every output and record of the assessment for it finds 0 hits, and the guard's call log (the empty
    HOME's ``.gov-os/guard-calls``) holds no read of it."""
    word = "snorkelvantry-w288"
    sets = box.base / "sets-root"
    W.write(sets, "fixtures/evaluation/memory-verdict-9/hidden/q01.yaml", f"id: q01\nquestion: Where is the {word} rule?\n")
    environment = W.env(box, host, GOV_MEMAUDIT_SETS_ROOT=str(sets))
    out = box.base / "out-hidden"
    run = W.run_adopt(orchard.root, environment, "MA", "--out", str(out))
    W.assert_offered(run, "MA")
    assert run.returncode == 0, run.describe()
    texts = W.all_text(out, box.home / ".gov-os", runs=(run,))
    assert len(texts) >= 3, "the run left nothing to grep"
    assert not [n for n, data in texts.items() if word.encode() in data], "a hidden question's word is in an output"


def test_s1_f1_the_repository_is_byte_identical_before_and_after(orchard, box, host):
    W.settle(orchard.root)
    before = W.repo_state(orchard.root)
    run, out = assess(orchard, box, host)
    W.assert_ok(run, "MA")
    after = W.repo_state(orchard.root)
    W.assert_state_equal(before, after, "the memory assessment")
    assert after["porcelain"] == "", f"git status is not clean after MA: {after['porcelain']}"


def test_s1_out_inside_the_project_is_refused(orchard, box, host):
    W.settle(orchard.root)
    before = W.repo_state(orchard.root)
    for inside in (orchard.root / "assessment", orchard.root / "docs" / "assessment", orchard.root):
        run = W.run_adopt(orchard.root, W.env(box, host), "MA", "--out", str(inside))
        W.assert_refused(run, "OUT_INSIDE_PROJECT", f"--out {inside.relative_to(orchard.root) or '.'}", "MA")
    W.assert_state_equal(before, W.repo_state(orchard.root), "the refused MA")
    assert not (orchard.root / "assessment").exists() and not (orchard.root / "docs" / "assessment").exists()


def test_s1_the_assessment_writes_only_under_out(assessed):
    orchard, run, out, record = assessed()
    names = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert W.ASSESSMENT in names, names
    assert all(n == W.ASSESSMENT or n.startswith(W.PLAN_DIR + "/") for n in names), f"files outside I1's list under --out: {names}"


# ---- I2: A3 and the assessment -------------------------------------------------------------------------------

def to_a2(project, box, host):
    adoption = W.Adoption(project, box, host)
    for stage in ("A0", "A1", "A2"):
        run = adoption.run(stage)
        assert run.returncode == 0, f"{stage} did not run on the planted project\n{run.describe()}"
    proposal = box.base / "proposal.yaml"
    proposal.write_text("artefacts:\n- {path: docs/drop-1.txt, action: DELETE_FROM_ACTIVE_TREE, batch: 1}\n", encoding="utf-8")
    return adoption, proposal


def test_i2_a3_without_an_assessment_for_head_refuses(box, host):
    project = W.plant_adoption(box)
    adoption, proposal = to_a2(project, box, host)
    empty = box.base / "no-assessment"
    empty.mkdir()
    W.settle(project)
    before = W.repo_state(project)
    for label, extra in (("an empty folder", ("--assessment", str(empty))), ("no --assessment at all", ())):
        run = adoption.run("A3", "--map", str(proposal), *extra)
        W.assert_refused(run, "ASSESSMENT_MISSING", f"A3 with {label}", "A3")
    W.assert_state_equal(before, W.repo_state(project), "the refused A3")


def test_i2_an_assessment_of_an_earlier_commit_is_not_one_for_head(box, host):
    project = W.plant_adoption(box)
    adoption, proposal = to_a2(project, box, host)
    # the assessment is made at A2's HEAD, then the tree moves on by a commit (a note): it is no longer HEAD's
    out = box.base / "late"
    first = adoption.run("MA", "--out", str(out))
    W.assert_offered(first, "MA")
    assert first.returncode == 0, first.describe()
    W.write(project, "docs/late.md", "# Late\n\nAdded after the assessment.\n")
    W.commit_all(project, "a later commit")
    refused = adoption.run("A3", "--map", str(proposal), "--assessment", str(out))
    W.assert_refused(refused, "ASSESSMENT_MISSING", "A3 on an assessment of an earlier commit", "A3")


def test_i2_a3_with_the_assessment_cites_its_sha256_and_copies_no_proposal(box, host):
    project = W.plant_adoption(box)
    adoption, proposal = to_a2(project, box, host)
    out = box.base / "assessment"
    ma = adoption.run("MA", "--out", str(out))
    W.assert_offered(ma, "MA")
    assert ma.returncode == 0, ma.describe()
    digest = W.sha256_file(out / W.ASSESSMENT)
    run = adoption.run("A3", "--map", str(proposal), "--assessment", str(out))
    W.assert_ok(run, "A3 with --assessment")
    record = W.front_of(project, run.result.get("record") or "governance/adoption/A3-target-path-map.md")
    assert digest in json.dumps(record, default=str), "A3's record does not cite the assessment's sha256"
    assert not any(n.startswith("RP-") for n in W.git(project, "ls-files").replace("/", "\n").splitlines()), "A3 copied a proposal"


# ---- the proof repositories and the resource gate ------------------------------------------------------------

def test_s1_peak_rss_on_every_synthetic_proof_repository_is_under_the_per_session_figure(box, host, tmp_path):
    """The five repositories W2-81's builders make (built into tmp_path, as W2-88 may call them): the record's own
    peak RSS is recorded and stays under ``gov.resources.config``'s working size."""
    import w2_81_build as build
    built = build.build_all(box.base / "proving", seed=881)
    figure = W.per_session_figure()
    for name in build.SHAPES:
        root = built[name].root
        run = W.run_adopt(root, W.env(box, host), "MA", "--out", str(box.base / f"out-{name}"))
        W.assert_offered(run, "MA")
        assert run.returncode == 0, f"MA on {name}\n{run.describe()}"
        record = W.read_json(box.base / f"out-{name}" / W.ASSESSMENT)
        assert 0 < record["peak_rss_bytes"] < figure, f"{name}: peak RSS {record['peak_rss_bytes']} vs per-session {figure}"
        assert record["tracked_files"] > 0 and record["commit"]


# ---- F4: the memory grows with the largest file, not with the tree -------------------------------------------

MIB = 1 << 20


def _tree_of(base, name, count, each):
    root = base / name
    root.mkdir(parents=True)
    W.write(root, ".gitignore", ".gov-runtime/\n")
    W.write(root, "README.md", "# a tree\n")
    body = ("a line of the planted small file\n" * (each // 33 + 1))[:each]
    for number in range(count):
        W.write(root, f"d{number % 50:02d}/f{number:05d}.txt", f"{number}\n" + body)
    W.git(root, "init", "-q", "-b", "main")
    W.commit_all(root, name)
    return root


def test_f4_the_memory_grows_with_the_largest_file_not_with_the_tree_size(box, host):
    """Tree M: 6,000 files of 16 KiB (about 94 MiB tracked, the largest file 16 KiB). Tree S: 10 files of the same size.
    Whatever the tool loads must not be the tree: M's recorded peak RSS stays within 40 MiB of S's (the tree is 90 MiB
    larger; the margin is under half of that). Both are far under the per-session figure."""
    small = _tree_of(box.base, "few", 10, 16 * 1024)
    many = _tree_of(box.base, "many", 6000, 16 * 1024)
    rss = {}
    for name, root in (("few", small), ("many", many)):
        run = W.run_adopt(root, W.env(box, host), "MA", "--out", str(box.base / f"out-{name}"))
        W.assert_offered(run, "MA")
        assert run.returncode == 0, run.describe()
        rss[name] = W.read_json(box.base / f"out-{name}" / W.ASSESSMENT)["peak_rss_bytes"]
    assert rss["many"] - rss["few"] <= 40 * MIB, \
        f"peak RSS grows with the tree: 10 files {rss['few']} B, 6,000 files {rss['many']} B (limit +40 MiB)"
    assert rss["many"] < W.per_session_figure()
