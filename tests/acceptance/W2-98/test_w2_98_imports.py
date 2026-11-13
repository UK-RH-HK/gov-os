"""W2-98: imported parts and their licence record (I4): success-5, failure-4.

``python3 <skill>/check_spec.py --imports <folder>`` reads ``imports.yaml`` in the folder (an ``imports:`` list of
entries with ``part``, ``source``, ``version``, ``licence``, the form of ``superpowers/vendored.yaml``) and the
``<!-- imported: <part> -->`` markers in the folder's files. It refuses a marked part with no record, or with a
licence outside the allowed list, naming the part (``REFUSED import <part>: <reason>``), and prints ``PASS`` only
with every marked part recorded and allowed. Planted folders live in ``tmp_path``.
"""
from __future__ import annotations

import re

import pytest
import yaml

import w2_98_support as s

PART = "reference-notes.md"
OTHER = "checklist-ideas.md"


def _folder(tmp_path, parts, records):
    """A planted skill folder: a SKILL.md, each marked part as a file carrying its marker, and imports.yaml."""
    folder = tmp_path / "planted-skill"
    folder.mkdir()
    (folder / "SKILL.md").write_text("---\nname: planted\nversion: \"1.0.0\"\ndescription: Planted.\n---\n\n# Planted\n",
                                     encoding="utf-8")
    for part in parts:
        (folder / part).write_text(f"<!-- imported: {part} -->\n\nCopied text of the part.\n", encoding="utf-8")
    if records is not None:
        entries = [{"part": p, "source": "https://example.org/skills", "version": "v1.0.0", "licence": lic}
                   for p, lic in records]
        (folder / "imports.yaml").write_text(yaml.safe_dump({"imports": entries}), encoding="utf-8")
    return folder


def _imports(tmp_path, parts, records):
    code, output = s.run_script("--imports", _folder(tmp_path, parts, records), cwd=tmp_path)
    return code, output


def _refusals_naming(output, part):
    return [line for line in s.refused(output) if part in line]


@pytest.mark.parametrize("licence", ["MIT", "Apache-2.0", "BSD-3-Clause"])
def test_a_marked_part_recorded_with_a_permissive_licence_is_accepted(tmp_path, licence):
    code, output = _imports(tmp_path, [PART], [(PART, licence)])
    assert code == 0, f"exit {code}: {output!r}"
    assert s.passes(output) and not s.refused(output), f"{output!r}"


def test_a_folder_with_no_marked_part_passes(tmp_path):
    code, output = _imports(tmp_path, [], [])
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


def test_a_marked_part_with_no_licence_record_is_refused_naming_the_part(tmp_path):
    code, output = _imports(tmp_path, [PART], [])
    assert code == 1, f"exit {code}: {output!r}"
    assert _refusals_naming(output, PART), f"no REFUSED line names {PART}: {output!r}"
    assert not s.passes(output), f"PASS printed beside a refusal: {output!r}"


def test_a_marked_part_with_no_imports_file_at_all_is_refused_naming_the_part(tmp_path):
    code, output = _imports(tmp_path, [PART], None)
    assert code == 1, f"exit {code}: {output!r}"
    assert _refusals_naming(output, PART), f"no REFUSED line names {PART}: {output!r}"
    assert not s.passes(output)


def test_a_marked_part_whose_record_is_for_another_part_is_refused_naming_the_part(tmp_path):
    code, output = _imports(tmp_path, [PART], [(OTHER, "MIT")])
    assert code == 1, f"exit {code}: {output!r}"
    assert _refusals_naming(output, PART), f"no REFUSED line names {PART}: {output!r}"
    assert not s.passes(output)


@pytest.mark.parametrize("licence", ["Proprietary", "GPL-3.0", "CC-BY-NC-4.0"])
def test_a_marked_part_whose_licence_forbids_the_use_is_refused_naming_the_part(tmp_path, licence):
    code, output = _imports(tmp_path, [PART], [(PART, licence)])
    assert code == 1, f"exit {code}: {output!r}"
    assert _refusals_naming(output, PART), f"no REFUSED line names {PART}: {output!r}"
    assert not s.passes(output), f"PASS printed beside a refusal: {output!r}"


def test_only_the_part_that_fails_is_named(tmp_path):
    code, output = _imports(tmp_path, [PART, OTHER], [(PART, "MIT"), (OTHER, "Proprietary")])
    assert code == 1 and not s.passes(output), f"exit {code}: {output!r}"
    assert _refusals_naming(output, OTHER), f"no REFUSED line names {OTHER}: {output!r}"
    assert not _refusals_naming(output, PART), f"the recorded, allowed part {PART} was named: {output!r}"


# the real skill folder ---------------------------------------------------------------------------------------------

MARKER = re.compile(r"<!--\s*imported:\s*(.+?)\s*-->")


def _markers(folder):
    return {m.group(1): str(p.relative_to(folder)) for p in sorted(folder.rglob("*"))
            if p.is_file() and p.suffix in {".md", ".py", ".yaml", ".yml", ".sh", ".txt"}
            for m in MARKER.finditer(p.read_text(encoding="utf-8", errors="replace"))
            if not m.group(1).startswith("<")}  # '<part>' in a sentence describing the marker is no marker


def test_the_skill_folder_has_an_import_record_in_the_vendored_form():
    path = s.need(s.SKILL_DIR / "imports.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("imports"), list), (
        "imports.yaml is not a mapping with an 'imports' list (the skill itself may import nothing: 'imports: []')")
    for entry in data["imports"]:
        missing = [k for k in ("part", "source", "version", "licence") if not entry.get(k)]
        assert not missing, f"an import record lacks {missing}: {entry}"


def test_every_imported_marker_in_the_skill_folder_has_a_record():
    """Repository-state case, green on the base: with no skill folder there is no marker to leave unrecorded.
    The folder's own case above (the record exists) and the next one (the check passes it) are red there."""
    if not s.SKILL_DIR.is_dir():
        return
    marked = _markers(s.SKILL_DIR)
    record = s.SKILL_DIR / "imports.yaml"
    parts = {e.get("part") for e in (yaml.safe_load(record.read_text(encoding="utf-8")) or {}).get("imports", [])} \
        if record.is_file() else set()
    unrecorded = {part: where for part, where in marked.items() if part not in parts}
    assert not unrecorded, f"imported text with no licence record: {unrecorded}"


def test_the_check_passes_the_real_skill_folders_imports():
    code, output = s.run_script("--imports", s.need(s.SKILL_DIR / "SKILL.md").parent, cwd=s.REPO_ROOT)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"
