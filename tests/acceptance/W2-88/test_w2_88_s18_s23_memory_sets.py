"""S18-S23 (success-18 .. success-23) and F9 (failure-9); I3, I4: what adoption writes for the audit that follows it.

A9 writes, under ``--out``/``memory-audit/``: ``AUDIT-RECORD.json`` (S18), ``briefs/`` with the three variants (S19),
``ACT-WALLS/`` (S22) and the cost block (S23); it starts no audit, writes no crontab line and applies no ACT (F9).
``adopt/memory_sets.py`` imports ``gov.memaudit`` and defines no pre-flight, USED marker or figures (S20); S21's ``due`` and
``baseline`` are ``gov.memaudit``'s, unchanged.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import w2_88_sets_support as T
import w2_88_support as W

HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def audit_dir(nine) -> Path:
    nine.record()
    folder = nine.out / "memory-audit"
    assert folder.is_dir(), "A9 wrote no memory-audit/ under --out"
    return folder


def audit_record(nine) -> dict:
    path = audit_dir(nine) / "AUDIT-RECORD.json"
    assert path.is_file(), "memory-audit/AUDIT-RECORD.json is not written"
    return json.loads(path.read_text(encoding="utf-8"))


def audited(worlds):
    return worlds.a9("audit", audit_tools=True)


def keys_like(data, pattern):
    """Every (key, value) of a nested JSON whose key matches ``pattern``."""
    found = []
    stack = [data]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if re.search(pattern, str(key), re.I):
                    found.append((key, value))
                stack.append(value)
        elif isinstance(item, list):
            stack.extend(item)
    return found


# ---- S18: the audit record ------------------------------------------------------------------------------------

def test_s18_the_audit_record_holds_its_sets_root_names_mode_variants_and_first_date(worlds):
    nine = audited(worlds)
    record = audit_record(nine)
    sets_root = keys_like(record, r"sets[_-]?root")
    assert sets_root and str(sets_root[0][1]).strip(), f"no sets root in the audit record: {sorted(record)}"
    assert keys_like(record, r"audit[_-]?names?|^names?$"), "no audit names in the audit record"
    assert keys_like(record, r"^mode$"), "no mode in the audit record"
    text = json.dumps(record)
    assert len(set(HEX64.findall(text))) >= 3, "the three briefs' variants are not each named with a sha256"
    assert len(keys_like(record, r"variant")) >= 1, "no variant ids in the audit record"
    assert keys_like(record, r"earliest|first[_-]?audit") or ISO_DATE.search(text), "the first audit's earliest date is not stated"


def test_s18_the_variant_hashes_of_the_record_are_the_files_hashes(worlds):
    nine = audited(worlds)
    record = audit_record(nine)
    hashes = {W.sha256_file(p) for p in T.variant_files(audit_dir(nine) / "briefs").values()}
    assert len(hashes) == 3, f"briefs/ does not hold the three variants: {sorted(T.variant_files(audit_dir(nine) / 'briefs'))}"
    assert hashes <= set(HEX64.findall(json.dumps(record))), "a variant's sha256 is not in the audit record"


def test_s18_f9_adoption_starts_no_audit_installs_no_schedule_and_changes_no_sets_root(worlds):
    nine = audited(worlds)
    nine.record()
    before, audit = nine.audit["before"], nine.audit
    calls = audit["crontab_log"].read_text(encoding="utf-8").splitlines() if audit["crontab_log"].exists() else []
    assert [c for c in calls if c.strip() not in ("-l", "-l ")] == [], f"adoption called crontab to change it: {calls}"
    assert W._tree_digest(audit["sets"], False) == before["sets"], "the sets root changed"
    assert W._tree_digest(audit["runs"], False) == before["runs"], "the audits' log folder changed: an audit started or logged"
    assert not (audit["runs"] / "indep" / "STARTS.log").exists() and not (audit["runs"] / "indep" / "AUDITS.log").exists()
    assert oct(audit["sets"].stat().st_mode & 0o777) == "0o700", "the sets root's mode changed"


# ---- S19: the variants ----------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", T.KINDS)
def test_s19_a_variant_differs_from_the_gov_os_brief_only_in_the_domain_table_and_the_blind_list(worlds, kind):
    nine = audited(worlds)
    files = T.variant_files(audit_dir(nine) / "briefs")
    assert kind in files, f"no {kind} variant under memory-audit/briefs/: {sorted(files)}"
    bad = T.diff_outside(kind, T.gov_brief(kind), files[kind].read_text(encoding="utf-8"))
    assert not bad, f"the {kind} variant differs from the Gov OS brief outside the domain table and the blind list: {bad[:3]}"


def approved_list(nine) -> Path:
    found = [p for p in (audit_dir(nine) / "ACT-WALLS").rglob("*") if p.is_file() and "approved" in p.name.lower()]
    assert found, "ACT-WALLS/ holds no approved list"
    return found[0]


def test_s19_a_launch_under_a_variant_not_on_the_approved_list_exits_10(worlds, tmp_path):
    nine = audited(worlds)
    approved = approved_list(nine)
    variant = T.variant_files(audit_dir(nine) / "briefs")["writer"]
    unlisted = tmp_path / variant.name
    unlisted.write_bytes(variant.read_bytes() + b"\nA line the owner never approved.\n")
    from gov.adopt import memory_sets
    assert memory_sets.launch_check(variant, approved) == 0, "a variant on the approved list is refused"
    assert memory_sets.launch_check(unlisted, approved) == 10, "a variant not on the approved list is not refused with 10"
    for given, code in ((variant, 0), (unlisted, 10)):
        done = subprocess.run([sys.executable, "-m", "gov.adopt.memory_sets", "launch-check", str(given), str(approved)],
                              env={**W.env(nine.box, nine.adoption.host)}, capture_output=True, text=True, timeout=120)
        assert done.returncode == code, f"launch-check exits {done.returncode}, not {code}: {done.stderr[-300:]}"


# ---- S20: one core --------------------------------------------------------------------------------------------

def test_s20_memory_sets_imports_from_gov_memaudit():
    source = (W.SRC / "gov/adopt/memory_sets.py").read_text(encoding="utf-8")     # red: no memory_sets.py on the base
    assert T.imports_from_memaudit(source), "memory_sets.py imports nothing from gov.memaudit"
    from gov.adopt import memory_sets
    for name in ("audit_record", "variants", "walls_act", "cost", "launch_check"):
        assert callable(getattr(memory_sets, name, None)), f"memory_sets.{name} is not there"


def test_s20_f9_no_file_of_src_gov_adopt_defines_a_pre_flight_a_use_once_marker_or_figures():
    """GUARD (green on the base: nothing there defines them; it must stay so once memory_sets.py exists)."""
    bad = []
    for path in sorted((W.SRC / "gov" / "adopt").glob("*.py")):
        bad += T.second_copies(path.read_text(encoding="utf-8"), path.name)
    assert not bad, f"a second copy of the pre-flight, the use-once marker or the figures: {bad}"


# ---- S21: the first audit follows the verdict set -------------------------------------------------------------

def test_s21_before_the_verdict_set_is_used_the_adoption_says_no_audit_is_due(worlds):
    nine = audited(worlds)
    text = " ".join(data.decode("utf-8", "replace") for data in W.all_text(audit_dir(nine)).values()
                    if isinstance(data, bytes))
    assert "not due: no verdict set used" in text, \
        "neither the audit record nor the memory-audit/ files say `not due: no verdict set used` (package P-5)"


def test_s21_the_baseline_line_holds_the_verdict_commit(tmp_path):
    """gov.memaudit baseline, unchanged (W2-172's code): after the verdict set's use it takes the verdict commit; green on
    the base. Judged through W2-172's planted repository (``w2_172_git.status_repo``)."""
    sys.path.insert(0, str(W.ACCEPT / "W2-172"))
    import w2_172_git as G
    repo = G.status_repo(tmp_path / "w")
    repo.audits_log.unlink(missing_ok=True)
    run = repo.baseline(repo.x2[:12])
    assert run.code == 0 and run.lines == [f"BASELINE {repo.x2[:12]}"], run
    assert json.loads(repo.audits_log.read_text().splitlines()[0])["commit"] == repo.x2, "the log does not start at the verdict commit"


# ---- S22: the walls ACT ---------------------------------------------------------------------------------------

def test_s22_the_act_package_holds_the_walls_the_sets_root_the_approved_list_and_the_hidden_globs(worlds):
    nine = audited(worlds)
    folder = audit_dir(nine) / "ACT-WALLS"
    assert folder.is_dir(), "no ACT-WALLS/ under memory-audit/"
    files = {p: p.read_bytes() for p in folder.rglob("*") if p.is_file()}
    template = {p.name: p.read_bytes() for p in (W.REPO_ROOT / "governance/project/indep-walls").iterdir() if p.is_file()}
    for name in ("wall_hook.py", "tree-exclude.txt"):
        assert any(data == template[name] for data in files.values()), f"the walls' template copy ({name}) is not in ACT-WALLS/"
    assert any(b"0700" in data or b"0o700" in data for data in files.values()), "the sets root's mode (0700) is not stated"
    approved = approved_list(nine)
    listed = set(HEX64.findall(approved.read_text(encoding="utf-8")))
    assert {W.sha256_file(p) for p in T.variant_files(audit_dir(nine) / "briefs").values()} <= listed, \
        "the approved list does not hold the three variant briefs' sha256"
    assert any(b"hidden" in data for p, data in files.items() if p != approved), "the path map's hidden globs are not stated"


def test_s22_adoption_never_applies_the_act_and_changes_nothing_of_the_sets_root_or_the_path_map(worlds):
    nine = audited(worlds)
    nine.record()
    before = nine.audit["before"]
    assert W._tree_digest(nine.audit["sets"], False) == before["sets"], "the planted sets root changed"
    now = (nine.project / "governance/project/path-map.yaml").read_bytes()
    assert now == before["path_map"], "the path map changed"
    assert oct(nine.audit["sets"].stat().st_mode & 0o777) == "0o700"


def act_step6(text: str) -> str:
    """ACT.md's step 6 as one line: its line and the lines after it up to the next numbered step."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("6.")]
    assert len(starts) == 1, f"ACT.md has no single step 6:\n{text[:1500]}"
    rest = []
    for line in lines[starts[0] + 1:]:
        if line[:1].isdigit():
            break
        rest.append(line)
    return " ".join([lines[starts[0]], *rest])


SLOT = re.compile(r"<[^<>\n]*>")
CALL_WALLS_ACT = W.REPO_ROOT / "tests" / "acceptance" / "W2-187" / "call_walls_act.py"   # W2-187's seam, used read-only


def cron_line(row: str) -> str:
    """Step 6's cron line: the code span that starts ``0 21 * * 1``."""
    found = re.search(r"`(0 21 \* \* 1[^`]*)`", row)
    assert found, f"step 6 holds no cron line (a code span starting `0 21 * * 1`): {row}"
    return found.group(1)


def test_s22_step_6_with_no_gitleaks_on_path_holds_no_slot_and_names_gitleaks_missing(tmp_path):
    """success-S22 (run 8b item 24, the CTO's condition 2, DEC-893, DEC-1156 (7)): A9's ``memory_sets.walls_act`` (this tree's, through
    W2-187's caller) run with no ``gitleaks`` on ``PATH`` (the python's folder, ``/usr/bin`` and ``/bin``). ACT.md's step 6 holds no
    ``<path to gitleaks>`` and no ``<...>`` slot in its cron line, and names ``GITLEAKS_MISSING``. (A9 itself cannot run with no gitleaks: its
    rebuild's lexical index refuses ``REBUILD_FAILED``, ``No such file or directory: 'gitleaks'``; the record half of item 24 is a package.)"""
    folders = [str(Path(sys.executable).parent), "/usr/bin", "/bin"]
    path = os.pathsep.join(folders)
    assert shutil.which("gitleaks", path=path) is None, "the plant: a gitleaks sits in a system folder"
    repo = tmp_path / "repo"
    repo.mkdir()
    W.git(repo, "init", "-q", "-b", "main")
    out, sets_root = tmp_path / "out", str(tmp_path / "never-made-sets")
    env = {"PATH": path, "HOME": str(tmp_path), "PYTHONPATH": str(W.SRC), "LANG": "C.UTF-8", "TMPDIR": str(tmp_path),
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    done = subprocess.run([sys.executable, str(CALL_WALLS_ACT), str(out), sets_root, "memory-audit-20261115", str(repo)], cwd=str(tmp_path),
                          env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, f"walls_act failed with no gitleaks on PATH: {done.stderr[-1200:]}"
    row = act_step6((out / "memory-audit" / "ACT-WALLS" / "ACT.md").read_text(encoding="utf-8"))
    assert "<path to gitleaks>" not in row, f"step 6 holds the unfilled slot <path to gitleaks> (DEC-893): {row}"
    assert "GITLEAKS_MISSING" in row, f"step 6 does not name GITLEAKS_MISSING with no gitleaks on PATH: {row}"
    line = re.search(r"`(0 21 \* \* 1[^`]*)`", row)
    assert not (line and SLOT.findall(line.group(1))), f"step 6 writes a cron line with a slot: {line.group(1) if line else ''}"


def test_s22_a9_with_gitleaks_on_path_names_its_absolute_path_in_step_6s_cron_line_and_no_slot(worlds):
    """success-S22 (run 8b items 22 and 24), GUARD (green on the base: W2-187's line must stay): A9 on a fork of the planted adoption at A8 with
    the suite's gitleaks on ``PATH``: step 6's cron line names gitleaks' absolute path (``GOV_MEMAUDIT_GITLEAKS=<that path>``), holds no
    ``<...>`` slot, and step 6 holds neither ``<path to gitleaks>`` nor ``<path to Gov OS>``; A9 is ok."""
    nine = worlds.a9("s22-gitleaks-a8", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "s22-gl-on")
    out = Path(adoption.box.base) / "s22-gl-on-out"
    run = adoption.a9(out)
    W.assert_offered(run, "A9")
    W.assert_ok(run, "A9 with gitleaks on PATH")
    row = act_step6((out / "memory-audit" / "ACT-WALLS" / "ACT.md").read_text(encoding="utf-8"))
    for slot in ("<path to gitleaks>", "<path to Gov OS>"):
        assert slot not in row, f"step 6 holds the unfilled slot {slot}: {row}"
    line = cron_line(row)
    assert not SLOT.findall(line), f"step 6's cron line holds unfilled slots {SLOT.findall(line)}: {line}"
    found = shutil.which("gitleaks", path=adoption.env()["PATH"])
    assert found, "the plant: the suite's box puts no gitleaks on PATH"
    names = {os.path.abspath(found), os.path.realpath(found)}
    assert any(f"GOV_MEMAUDIT_GITLEAKS={name} " in line for name in names), f"step 6 does not name gitleaks' absolute path {found}: {line}"


# ---- S23: the cost --------------------------------------------------------------------------------------------

def test_s23_the_record_states_the_four_figures_and_the_figure_to_replace(worlds):
    nine = audited(worlds)
    nine.record()
    texts = " ".join(data.decode("utf-8", "replace") for data in
                     list(W.all_text(audit_dir(nine)).values()) + [W.git(nine.project, "show", "HEAD:" + nine.run.result["record"]).encode()])
    for word in ("tokens", "usd", "gpu_minutes", "owner_minutes", "replace_after"):
        assert word in texts, f"the adoption record's cost block lacks {word}"
    assert "first audit" in texts, "the cost block does not name the first audit as what replaces the estimate"


def test_s23_cost_is_from_the_audit_packages_section_7_and_scales_with_the_set():
    from gov.adopt import memory_sets
    forty, eighty = memory_sets.cost(40), memory_sets.cost(80)
    assert set(forty) >= {"tokens", "usd", "gpu_minutes", "owner_minutes", "replace_after"}
    assert 15 <= forty["usd"] <= 50, f"section 7: about $20 to $30, capped at $50, for 40 questions: {forty['usd']}"
    assert eighty["usd"] > forty["usd"] and eighty["tokens"] > forty["tokens"] > 0
    assert forty["owner_minutes"] > 0 and forty["gpu_minutes"] > 0 and "first audit" in str(forty["replace_after"])
