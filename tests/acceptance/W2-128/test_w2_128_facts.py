"""W2-128 round 1: governance/project/facts.yaml and its schema (TPL-2 S1, S2, S4; TPL-3 S5's facts part; the
links command). TPL-2 S3 (a switch flipped in a filled brief) is round 2 (README)."""

from __future__ import annotations

import copy
import json
import re

import w2_128_support as s


# --- S6 (TPL-2 S1): the schema and the file ------------------------------------------------------------------------

def test_s6_facts_yaml_validates_against_facts_schema():
    schema = json.loads(s.read(s.FACTS_SCHEMA))
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", \
        "facts.schema.json is not JSON Schema 2020-12"
    data = s.facts()
    missing = [key for key in s.FACTS_TOP if key not in data]
    assert not missing, f"facts.yaml lacks the top-level keys {missing}"
    errors = s.schema_errors("facts.schema.json", data)
    assert not errors, f"facts.yaml does not validate against facts.schema.json: {errors[:5]}"


def test_s6_facts_schema_refuses_a_facts_file_without_commands_or_a_command_without_check():
    data = s.facts()
    without_commands = {key: value for key, value in data.items() if key != "commands"}
    assert s.schema_errors("facts.schema.json", without_commands), \
        "facts.schema.json accepts a facts file with no commands"
    no_check = copy.deepcopy(data)
    name = sorted(no_check["commands"])[0]
    no_check["commands"][name] = {k: v for k, v in no_check["commands"][name].items() if k != "check"}
    assert s.schema_errors("facts.schema.json", no_check), \
        f"facts.schema.json accepts a commands entry ({name}) with no check"


def test_s6_commands_hold_the_named_ones_each_with_run_and_check():
    commands = s.commands()
    missing = [name for name in s.REQUIRED_COMMANDS if name not in commands]
    assert not missing, f"facts.yaml commands lack {missing}"
    bad = [name for name, entry in commands.items()
           if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k].strip()
                                                     for k in ("run", "check"))]
    assert not bad, f"commands entries without a run and a check form: {bad}"


# --- S6 (TPL-2 S2): every check runs, within the limits ------------------------------------------------------------

FORBIDDEN_IN_CHECKS = re.compile(r"ollama|llama-server|nvidia-smi|\bcurl\b|\bwget\b|pip3? install|https?://"
                                 r"|huggingface|heavy_slot|rebuild_slot", re.I)


def test_s6_no_check_reaches_a_model_the_network_a_gpu_or_gov_retrieve():
    wrong = {}
    for name, entry in s.commands().items():
        check = str(entry.get("check", "")) if isinstance(entry, dict) else ""
        if FORBIDDEN_IN_CHECKS.search(check):
            wrong[name] = check
        elif re.search(r"\bgov(?:\.cli\.main)? (retrieve|context)\b", check) and not re.search(r"(--help|-h)\b", check):
            wrong[name] = check
    assert not wrong, f"check forms that may reach a model, the network, a GPU or a real retrieval: {wrong}"


def test_s6_every_check_runs_and_exits_0_in_a_temporary_repository(tmp_path):
    data = s.facts()
    tree = s.temporary_repository(tmp_path)
    failures = [why for name, entry in sorted(s.commands(data).items())
                if (why := s.run_check(name, entry, tree, tmp_path, data))]
    assert not failures, "check forms that do not run cleanly:\n" + "\n".join(failures)


# --- S6 (TPL-2 S4): dod -------------------------------------------------------------------------------------------

def test_s6_dod_has_at_most_six_items_quoted_by_id_in_t1_and_t7():
    dod = s.facts().get("dod")
    assert isinstance(dod, list) and 1 <= len(dod) <= 6, f"facts.yaml dod is not a list of one to six items: {dod!r}"
    ids = []
    for item in dod:
        assert isinstance(item, dict) and re.fullmatch(r"DOD-\d+", str(item.get("id", ""))) \
            and isinstance(item.get("line"), str) and item["line"].strip(), f"dod item not {{id: DOD-n, line}}: {item!r}"
        ids.append(item["id"])
    assert len(set(ids)) == len(ids), f"dod ids repeat: {ids}"
    for stem in ("ticket", "role-lead"):
        text = s.template(stem)
        quoted = set(re.findall(r"\bDOD-\d+\b", text))
        assert quoted, f"{stem}.md quotes no dod id"
        assert quoted <= set(ids), f"{stem}.md quotes dod ids facts.yaml lacks: {sorted(quoted - set(ids))}"
        copied = [item["id"] for item in dod if len(item["line"]) >= 30 and s.fold(item["line"]) in s.fold(text)]
        assert not copied, f"{stem}.md copies dod lines {copied} instead of quoting them by id"


# --- S8 (TPL-3 S5): the three scripts ------------------------------------------------------------------------------

SCRIPTS = {"lead_verify": "lead_verify.sh", "launch_worker": "launch_worker.sh", "wait_for": "wait_for.sh"}


def test_s8_facts_names_the_three_scripts_and_the_templates_name_each(tmp_path):
    data = s.facts()
    commands = s.commands(data)
    texts = {stem: s.template(stem) for stem in s.NINE}
    tree = s.temporary_repository(tmp_path)
    for name, script in SCRIPTS.items():
        entry = commands.get(name)
        assert isinstance(entry, dict) and script in str(entry.get("run", "")), \
            f"facts.yaml's {name} command does not run {script}: {entry!r}"
        assert any(f"{{CMD:{name}" in text for text in texts.values()), f"no template names {{CMD:{name}}}"
        why = s.run_check(name, entry, tree, tmp_path, data)
        assert why is None, why


# --- S15: the links command ----------------------------------------------------------------------------------------

def test_s15_links_command_and_its_check_and_t7_quotes_its_first_line(tmp_path):
    data = s.facts()
    entry = s.commands(data).get("links")
    assert isinstance(entry, dict) and "gov links --since {BASE}" in str(entry.get("run", "")), \
        f"facts.yaml's links command is not gov links --since {{BASE}}: {entry!r}"
    why = s.run_check("links", entry, s.temporary_repository(tmp_path), tmp_path, data)
    assert why is None, why
    hits = s.units_with("role-lead", "gov links --since {BASE}", "first line")
    assert hits, "role-lead.md does not have the return quote gov links' first line"
