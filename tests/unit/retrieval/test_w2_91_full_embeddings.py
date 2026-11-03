"""W2-91 (DEC-957, DEC-388, DEC-381): the root files, the governance overlay and schemas/ are embedded; the hidden
half, the generated copies, the vendored parts and the old carried cli/ stay out; nothing else moves."""
import subprocess
from pathlib import Path

import yaml

from gov.secrets import _matches

ROOT = Path(__file__).resolve().parents[3]
MAP = "governance/project/path-map.yaml"
# The merge base of w2/W2-91 and w2/integrate; its path map is the same as at f46b96537d74.
BASE = "904bb3a0e7c6"
KERNEL = "template/governance/kernel/"
NEWLY_EMBEDDED = ("governance/", "schemas/")
STAY_OUT = ("fixtures/", ".claude/", ".rulesync/", "template/.rulesync/", "cli/", KERNEL + "vendor/", KERNEL + "bin/")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _head() -> dict:
    return yaml.safe_load((ROOT / MAP).read_text())["namespaces"]


def _base() -> dict:
    return yaml.safe_load(_git("show", f"{BASE}:{MAP}"))["namespaces"]


def _tracked(*tree: str) -> list[str]:
    out = _git("ls-tree", "-r", "-z", "--name-only", *tree) if tree else _git("ls-files", "-z")
    return [rel for rel in out.split("\0") if rel]


def _owners(namespaces: dict, rel: str) -> list[str]:
    return [name for name, entry in namespaces.items() if any(_matches(rel, pattern) for pattern in entry["paths"])]


def _embedded(namespaces: dict, rel: str) -> bool:
    """The indexer's rule (semantic._wanted, DEC-381, DEC-388): embedded only when every namespace says embedded."""
    policies = [namespaces[name].get("embedding_policy") for name in _owners(namespaces, rel)]
    return bool(policies) and all(policy == "embedded" for policy in policies)


def _newly_embedded(rel: str) -> bool:
    return "/" not in rel or rel.startswith(NEWLY_EMBEDDED)


def _stays_out(rel: str) -> bool:
    return rel.startswith(STAY_OUT) or (
        rel.startswith(KERNEL + "skills/superpowers/") and rel != KERNEL + "skills/superpowers/vendored.yaml")


def test_every_tracked_path_is_in_one_namespace():
    namespaces = _head()
    assert [rel for rel in _tracked() if len(_owners(namespaces, rel)) != 1] == []


def test_only_the_two_values():
    assert {entry["embedding_policy"] for entry in _head().values()} == {"embedded", "not embedded"}


def test_the_root_files_the_overlay_and_schemas_are_embedded():
    namespaces = _head()
    newly = [rel for rel in _tracked() if _newly_embedded(rel)]
    assert any("/" not in rel for rel in newly) and any(rel.startswith("governance/") for rel in newly)
    assert [rel for rel in newly if not _embedded(namespaces, rel)] == []
    assert _embedded(namespaces, "schemas/records/planted.schema.json")


def test_what_stays_out_stays_out():
    namespaces = _head()
    assert [rel for rel in _tracked() if _stays_out(rel) and _embedded(namespaces, rel)] == []
    planted = ["fixtures/evaluation/planted.md", ".claude/planted.md", ".rulesync/planted.md",
               "template/.rulesync/planted.md", "cli/planted.py", KERNEL + "vendor/planted.py",
               KERNEL + "bin/planted", KERNEL + "skills/superpowers/planted/SKILL.md"]
    assert [rel for rel in planted if _embedded(namespaces, rel)] == []
    assert _owners(namespaces, "cli/planted.py") == ["carried-code"]


def test_the_overlay_stays_restricted():
    head, base = _head()["project-overlay"], _base()["project-overlay"]
    assert (head["sensitivity"], head["export_policy"]) == ("restricted", "denied")
    assert (head["sensitivity"], head["export_policy"]) == (base["sensitivity"], base["export_policy"])


def test_nothing_else_moves():
    head, base = _head(), _base()
    both = set(_tracked()) & set(_tracked(BASE))
    moved = sorted(rel for rel in both if _embedded(head, rel) != _embedded(base, rel))
    assert [rel for rel in moved if not _newly_embedded(rel)] == []
    assert [rel for rel in moved if not _embedded(head, rel)] == []
    assert any(rel.startswith("governance/") for rel in moved) and any("/" not in rel for rel in moved)
