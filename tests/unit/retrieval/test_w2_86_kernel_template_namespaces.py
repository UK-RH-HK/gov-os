"""W2-86 (DEC-952, DEC-388): the kernel template is embedded, vendored code and the adapter copies are not."""
import subprocess
from pathlib import Path

import yaml

from gov.secrets import _matches

ROOT = Path(__file__).resolve().parents[3]
KERNEL = "template/governance/kernel/"


def _namespaces() -> dict:
    return yaml.safe_load((ROOT / "governance/project/path-map.yaml").read_text())["namespaces"]


def _template_paths() -> list[str]:
    out = subprocess.run(["git", "ls-files", "template"], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.split()


def _policies(namespaces: dict, rel: str) -> list:
    return [entry["embedding_policy"] for entry in namespaces.values()
            if any(_matches(rel, pattern) for pattern in entry["paths"])]


def test_every_template_path_is_in_one_namespace():
    namespaces = _namespaces()
    assert [rel for rel in _template_paths() if len(_policies(namespaces, rel)) != 1] == []


def test_only_the_two_values():
    assert {entry["embedding_policy"] for entry in _namespaces().values()} == {"embedded", "not embedded"}


def test_vendored_and_copies_are_not_embedded_and_the_rest_is():
    namespaces = _namespaces()
    for rel in _template_paths():
        vendored = rel.startswith((KERNEL + "vendor/", KERNEL + "bin/", "template/.rulesync/")) or (
            rel.startswith(KERNEL + "skills/superpowers/") and rel != KERNEL + "skills/superpowers/vendored.yaml")
        assert _policies(namespaces, rel) == ["not embedded" if vendored else "embedded"], rel
