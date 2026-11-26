"""PG-1: page-ready, by code. Packages with one defect each and one clean; ``page`` takes the clean one and names the
field of each other."""
from __future__ import annotations

import json
import re

import w2_211_support as S

FIELDS = ("question", "found", "sources", "blocks", "rubric", "recommendation", "touches")
NEW_FIELDS = ["touches", "reversible", "inside", "question", "found", "options", "recommendation", "sources", "blocks"]


def _planted(tmp_path, env):
    pk = {
        "DP-0001": S.package_text("DP-0001"),
        "DP-0002": S.package_text("DP-0002", drop=["found"]),
        "DP-0003": S.package_text("DP-0003", question="q" * 301),
        "DP-0004": S.package_text("DP-0004", recommendation={"option": "z", "reason": "r", "confidence": "high"}),
        "DP-0005": S.package_text("DP-0005", sources=["docs/not-there.md"]),
        "DP-0006": S.package_text("DP-0006", rubric="P1.99"),
        "DP-0007": S.package_text("DP-0007", options=[S.option("a", "Only one")]),
        "DP-0008": S.package_text("DP-0008", drop=["touches"]),
    }
    return S.init_repo(tmp_path, env, "pg1", pk)


def test_page_takes_the_clean_package_and_names_each_planted_field(tmp_path, env):
    repo = _planted(tmp_path, env)
    run = S.gov(["decisions", "page", "--batches", S.BATCH_DIR, "--root", repo], env=env, cwd=repo)
    _batch, data, cards = S.read_manifest(repo)
    assert cards == ["DP-0001"], f"only the clean package goes on the page, got {cards}; output: {run.both[-600:]}"
    planted = {"DP-0002": "found", "DP-0003": "question", "DP-0004": "recommendation", "DP-0005": "sources",
               "DP-0006": "rubric", "DP-0007": "options", "DP-0008": "touches"}
    for pid, field in planted.items():
        lines = [ln for ln in run.both.splitlines() if pid in ln]
        assert lines, f"no refusal line for {pid}: {run.both[-800:]}"
        text = " ".join(lines)
        assert re.search(rf"\b{field}\b", text), f"{pid}: the line must name `{field}`: {text}"
        others = [f for f in FIELDS if f != field and re.search(rf"\b{f}\b", text)]
        assert not others, f"{pid}: names fields that are not at fault ({others}): {text}"


def test_a_page_of_only_defective_packages_puts_none_on_a_page(tmp_path, env):
    repo = S.init_repo(tmp_path, env, "pg1b", {"DP-0002": S.package_text("DP-0002", drop=["blocks"])})
    run = S.gov(["decisions", "page", "--batches", S.BATCH_DIR, "--root", repo], env=env, cwd=repo)
    files = list((repo / S.BATCH_DIR).glob("*.manifest.json")) if (repo / S.BATCH_DIR).exists() else []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        assert not data["cards"], "a defective package must not be on a page"
    assert re.search(r"\bblocks\b", run.both) and "DP-0002" in run.both, run.both[-600:]


def test_schema_adds_the_fields_as_optional():
    schema = json.loads((S.REPO_ROOT / "template/governance/kernel/schemas/decision-package.schema.json")
                        .read_text(encoding="utf-8"))
    props = schema.get("properties", {})
    missing = [f for f in NEW_FIELDS if f not in props]
    assert not missing, f"schema lacks properties: {missing}"
    required = set(schema.get("required", []))
    assert not required & set(NEW_FIELDS), f"new fields must stay optional, required: {required & set(NEW_FIELDS)}"
    assert schema.get("additionalProperties") is not False
