"""Builder tests for W2-153 S-ADOPTED (DEC-1192 (2)): ``gov adapters generate`` writes ``.claude/templates/<role>.md``
in an adopted repository, byte for byte from the kit's ``governance/kernel/templates/``. Regression evidence only.

The adopted repository is a ``tmp_path`` without ``copier.yml``, ``template/`` and ``src/gov/``; ``rulesync generate``
is replaced by a stand-in (``merge.generate_into``) as ``test_generate`` does. The rest is the code's own.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from gov.adapters import merge, portability
from gov.adopt import fabric
from gov.cli.errors import GovError
from gov.launch import launcher

KIT = Path(__file__).resolve().parents[3] / "template" / "governance" / "kernel" / "templates"
GENERATED = {
    "CLAUDE.md": b"# Governance\n\nGenerated line.\n",
    ".claude/settings.json": json.dumps({"permissions": {"allow": ["Read(./**)"]}}).encode(),
    ".claude/agents/engineer.md": b"generated agent\n",
}


def rel(stem):
    return f".claude/templates/{stem}.md"


@pytest.fixture()
def adopted(tmp_path, monkeypatch):
    root = tmp_path / "adopted"
    (root / ".rulesync").mkdir(parents=True)
    templates = root / "governance" / "kernel" / "templates"
    templates.mkdir(parents=True)
    for stem in portability.TEMPLATE_COPIES:
        shutil.copyfile(KIT / f"{stem}.md", templates / f"{stem}.md")
    monkeypatch.setattr(merge, "generate_into", lambda project, folder: dict(GENERATED))
    return root


def test_every_launch_template_is_a_template_copy():
    assert set(launcher.ROLE_TEMPLATES.values()) <= set(portability.TEMPLATE_COPIES)


def test_generate_writes_every_copy_byte_for_byte_and_launch_finds_each(adopted):
    assert not (adopted / ".claude" / "templates").exists()
    result = merge.generate(adopted)
    assert result["templates"] == {"written": sorted(rel(s) for s in portability.TEMPLATE_COPIES), "replaced": []}
    for stem in portability.TEMPLATE_COPIES:
        assert (adopted / rel(stem)).read_bytes() == (KIT / f"{stem}.md").read_bytes()
    for role, stem in launcher.ROLE_TEMPLATES.items():
        assert launcher.template_args(adopted, role) == [launcher.TEMPLATE_FLAG, str(adopted / rel(stem))]
    again = merge.generate(adopted)  # equal copies are left alone and named nowhere
    assert again["templates"] == {"written": [], "replaced": []}


def test_a_differing_copy_is_replaced_and_named_the_equal_ones_are_not(adopted):
    merge.generate(adopted)
    (adopted / rel("role-engineer")).write_text("a hand edit\n")
    (adopted / rel("brief")).unlink()
    result = merge.generate(adopted)
    assert result["templates"] == {"written": [rel("brief")], "replaced": [rel("role-engineer")]}
    for stem in ("brief", "role-engineer"):
        assert (adopted / rel(stem)).read_bytes() == (KIT / f"{stem}.md").read_bytes()
    assert rel("role-lead") not in json.dumps(result)


def test_a_kit_missing_one_template_refuses_and_nothing_is_written(adopted):
    (adopted / "governance/kernel/templates/role-cto.md").unlink()
    with pytest.raises(GovError) as caught:
        merge.generate(adopted)
    assert caught.value.code == "ADAPTERS_TEMPLATE_MISSING"
    assert "role-cto.md" in str(caught.value)
    assert not (adopted / "CLAUDE.md").exists() and not (adopted / ".claude").exists()


def test_gov_os_own_source_tree_gets_no_copy_and_no_templates_key(adopted):
    (adopted / "copier.yml").write_text("x: 1\n")
    (adopted / "template").mkdir()
    (adopted / "src" / "gov").mkdir(parents=True)
    assert all((adopted / marker).exists() for marker in fabric.MARKERS)
    result = merge.generate(adopted)
    assert "templates" not in result and set(result) == {"merged", "written", "kept"}
    assert not (adopted / ".claude" / "templates").exists()


def test_a_kernel_without_a_templates_folder_has_no_template_step(adopted):
    shutil.rmtree(adopted / "governance" / "kernel" / "templates")
    result = merge.generate(adopted)
    assert "templates" not in result and not (adopted / ".claude" / "templates").exists()


def test_write_templates_still_prints_and_exits_as_before(adopted, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(adopted)
    folder = tmp_path / "out" / "templates"
    assert portability.main(["--write-templates", str(folder)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == {"written": [str(folder / f"{stem}.md") for stem in portability.TEMPLATE_COPIES]}
    for stem in portability.TEMPLATE_COPIES:
        assert (folder / f"{stem}.md").read_bytes() == (KIT / f"{stem}.md").read_bytes()
    (adopted / "governance/kernel/templates/brief.md").unlink()
    other = tmp_path / "other"
    assert portability.main(["--write-templates", str(other)]) == 1
    printed = json.loads(capsys.readouterr().out)
    assert printed["written"] == [] and "missing" in printed["error"] and not other.exists()
