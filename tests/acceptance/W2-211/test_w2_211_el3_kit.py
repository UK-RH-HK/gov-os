"""EL-3: through the kit. Judged by files: the kit's package template and schema carry the fields, the level table is
in the kit, and a scratch repository that carries only the kit's files judges a record below its level. (Running
``gov update`` into a scratch adopted repository is PG-9's road and too heavy here; the scratch holds the kit's files
as ``gov update`` lays them down and none of this repository's own project files.)"""
from __future__ import annotations

import json
import re

import w2_211_support as S

KIT = S.REPO_ROOT / "template/governance/kernel"
FIELDS = ["touches", "reversible", "inside", "question", "found", "options", "recommendation", "sources", "blocks"]
WORDS = ["spec", "kpi", "standing-decision", "contract", "charter", "shared-code", "cross-stream", "kernel-text",
         "secret", "paid-service", "model-effort", "release", "own-ticket"]


def test_kit_template_and_schema_carry_the_record_fields():
    template = (KIT / "templates/decision-package.md").read_text(encoding="utf-8")
    front = template.split("---")[1]
    for f in FIELDS:
        assert re.search(rf"(?m)^{f}:", front), f"the package template's frontmatter lacks `{f}:`"
    schema = json.loads((KIT / "schemas/decision-package.schema.json").read_text(encoding="utf-8"))
    for f in FIELDS:
        assert f in schema["properties"], f"the schema lacks `{f}`"


def test_level_table_and_code_are_in_the_kit():
    yaml_path = S.REPO_ROOT / "governance/project/escalation.yaml"
    assert yaml_path.is_file(), "governance/project/escalation.yaml does not exist"
    text = yaml_path.read_text(encoding="utf-8")
    for word in WORDS + ["P1", "P2", "P3", "emergency"]:
        assert word in text, f"escalation.yaml does not name `{word}`"
    assert (S.REPO_ROOT / "src/gov/decisions/level.py").is_file()


def _scratch(tmp_path, env, with_yaml: bool):
    repo = S.init_repo(tmp_path, env, "adopted-yaml" if with_yaml else "adopted")
    for rel in ("templates/decision-package.md", "schemas/decision-package.schema.json", "schemas/common.schema.json"):
        S.write(repo / "governance/kernel" / rel, (KIT / rel).read_text(encoding="utf-8"))
    if with_yaml:
        S.write(repo / "governance/project/escalation.yaml",
                (S.REPO_ROOT / "governance/project/escalation.yaml").read_text(encoding="utf-8"))
    S.commit(repo, env, "kit files")
    return repo


def _record_below_level(repo, env):
    entry = ("\n### DEC-1300 — A change to the spec\n- **Status:** ACCEPTED (CTO, 2026-11-24, in the ticket; done)\n"
             "- **Touches:** spec\n- **Reversible:** yes\n- **Inside:** repository\n- **Decision:** change it.\n"
             "- **Adds:** no rule\n- **Basis:** the message of 2026-11-24; docs/spec.md\n"
             "- **Governing sources:** docs/spec.md\n")
    reg = repo / S.REGISTER
    reg.write_text(reg.read_text(encoding="utf-8") + entry, encoding="utf-8")
    S.commit(repo, env, "DEC-1300\n\nTask: decision-record\nRole: orchestrator\nDecided-by: CTO")
    return S.gov(["decisions", "basis", "--range", "HEAD^..HEAD", "--root", repo], env=env, cwd=repo)


def test_a_repository_with_the_kits_files_refuses_a_record_below_its_level(tmp_path, env):
    repo = _scratch(tmp_path, env, with_yaml=False)
    run = _record_below_level(repo, env)
    assert run.code != 0 and "DECISION_BELOW_LEVEL" in run.both and "P1" in run.both, run.both[-500:]


def test_the_code_default_and_the_kits_table_agree(tmp_path, env):
    bare, yml = _scratch(tmp_path, env, False), _scratch(tmp_path, env, True)
    for touches, rev, inside in [("spec", "yes", "worktree"), ("shared-code", "yes", "repository"),
                                 ("own-ticket", "no", "repository"), ("own-ticket", "yes", "worktree"),
                                 ("kernel-text", "no", "worktree")]:
        outs = [S.gov(["decisions", "level", "--touches", touches, "--reversible", rev, "--inside", inside,
                       "--root", r], env=env, cwd=r) for r in (bare, yml)]
        assert outs[0].code == 0 and outs[0].out == outs[1].out, (touches, outs[0].both, outs[1].both)
