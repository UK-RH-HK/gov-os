"""S1: Gov OS's constants come from its configuration file, and the file validates against its schema.

The old tables are written out here as literals (``src/gov/memaudit/tables.py`` and ``measure.py`` at the base
``bfde928f5``); nothing is imported from the module to say what they were.
"""

from __future__ import annotations

import json
import subprocess

import pytest
import yaml

import w2_204_support as K

SCHEMA = K.TREE / "template" / "governance" / "kernel" / "schemas" / "memory-audit.schema.json"
OLD_DOMAINS = [
    ("decisions", ["docs/DECISION_REGISTER.md"]),
    ("tickets", [".tickets/**"]),
    ("plan", ["docs/plan/**"]),
    ("contract", ["docs/contract/**", "docs/charter/**"]),
    ("code", ["src/**", "template/governance/kernel/hooks/**", ".claude/hooks/**"]),
]
OLD_SUBSYSTEMS = [
    ("retrieval", ["src/gov/retrieval/**", "src/gov/retrieve/**", "src/gov/context/**", "src/gov/store/**",
                   "src/gov/codeintel/**", "governance/project/retrieval.yaml"]),
    ("guard", ["src/gov/guard/**", "src/gov/hooks/**", "template/governance/kernel/hooks/**", ".claude/hooks/**"]),
    ("close", ["src/gov/close/**", "src/gov/closure/**", "src/gov/accept/**", "src/gov/check/**",
               "src/gov/readiness/**", "src/gov/ci/**", "docs/close/**",
               "governance/project/orchestration/tools/nightly*"]),
    ("checkpoint", ["src/gov/checkpoint/**", "src/gov/pause/**", "docs/checkpoints/**"]),
    ("rebuild", ["src/gov/rebuild/**", "src/gov/secrets/**", "src/gov/doctor/**"]),
    ("launch", ["src/gov/launch/**", "src/gov/brief/**", "template/governance/kernel/launch/**",
                "governance/project/orchestration/tools/indep_launch.py", "governance/project/indep-walls/**"]),
    ("release", ["src/gov/release/**", "src/gov/adopt/**", "src/gov/adapters/**", "docs/releases/**"]),
]
OLD_QUOTAS = [("decision", 6), ("contract", 4), ("plan", 4), ("ticket", 4), ("exact-string", 4), ("callers", 4),
              ("code-paraphrase", 3), ("kernel-template", 3), ("multi-file", 3), ("failure-memory", 3), ("history", 1),
              ("nonexistent-id", 1)]
OLD_CONTROL = {"set": "memory-retrieval", "part": "visible", "size": 40, "baseline": 34, "spread": 2}
OLD_SPREAD = {"domain_min": 4, "subsystem_max": 10}
CHECK_OK = "CONFIG ok half 40 categories 12 domains 5 subsystems 7 control memory-retrieval"


def _get(row, key):
    return row[key] if isinstance(row, dict) else getattr(row, key)


def _pairs(table, key) -> list[tuple]:
    """``[(name, value of key)]`` of a table in its order: its rows are mappings or objects with the Interface's key
    names, or ``(name, value)`` pairs (a mapping by name reads as its items)."""
    out = []
    for row in (table.items() if isinstance(table, dict) else table):
        if isinstance(row, (tuple, list)) and len(row) >= 2 and isinstance(row[0], str):
            value = row[1]
            if isinstance(value, dict) or hasattr(value, key):
                value = _get(value, key)
            out.append((row[0], value))
        else:
            out.append((_get(row, "name"), _get(row, key)))
    return [(name, list(value) if isinstance(value, (list, tuple)) else value) for name, value in out]


def _gov_os_file() -> dict:
    assert K.GOV_OS_CONFIG.is_file(), "governance/project/memory-audit.yaml does not exist"
    return yaml.safe_load(K.GOV_OS_CONFIG.read_text(encoding="utf-8"))


def test_s1_the_file_holds_todays_domain_and_subsystem_tables_in_order():
    gov_os_file = _gov_os_file()
    assert _pairs(gov_os_file["domains"], "paths") == OLD_DOMAINS
    assert _pairs(gov_os_file["subsystems"], "paths") == OLD_SUBSYSTEMS


def test_s1_the_file_holds_the_twelve_categories_with_their_quotas_in_order():
    gov_os_file = _gov_os_file()
    assert _pairs(gov_os_file["categories"], "count") == OLD_QUOTAS
    assert gov_os_file["half_size"] == 40 == sum(count for _, count in OLD_QUOTAS)
    assert all(isinstance(row.get("about"), str) and row["about"].strip() for row in gov_os_file["categories"])


def test_s1_the_file_holds_the_control_set_and_the_spread_rule():
    gov_os_file = _gov_os_file()
    assert gov_os_file["control"] == OLD_CONTROL
    assert gov_os_file.get("spread", OLD_SPREAD) == OLD_SPREAD
    assert gov_os_file["repository"] == "Gov OS" and gov_os_file["version"] == 1


def test_s1_load_returns_exactly_the_old_tables_for_gov_os_s_repository():
    from gov.memaudit import config
    loaded = config.load(K.TREE)
    assert _pairs(loaded.domains, "paths") == OLD_DOMAINS
    assert _pairs(loaded.subsystems, "paths") == OLD_SUBSYSTEMS
    assert _pairs(loaded.categories, "count") == OLD_QUOTAS
    assert loaded.half_size == 40 and loaded.repository == "Gov OS"


def test_s1_load_returns_the_control_figures_and_the_spread_numbers():
    from gov.memaudit import config
    loaded = config.load(K.TREE)
    assert {key: _get(loaded.control, key) for key in OLD_CONTROL} == OLD_CONTROL
    assert {key: _get(loaded.spread, key) for key in OLD_SPREAD} == OLD_SPREAD
    assert isinstance(loaded.exclude, (list, tuple))


def test_s1_the_file_validates_against_the_schema():
    gov_os_file = _gov_os_file()
    import jsonschema
    assert SCHEMA.is_file(), "template/governance/kernel/schemas/memory-audit.schema.json does not exist"
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validators.validator_for(schema).check_schema(schema)
    jsonschema.validate(gov_os_file, schema)


def test_s1_the_schema_takes_the_second_repository_s_file_and_refuses_an_unknown_key():
    """The schema is the product's, not Gov OS's: a record-key subsystem, ``baseline: first`` and ``control: none``
    validate; a key outside the closed set does not."""
    import jsonschema
    assert SCHEMA.is_file(), "template/governance/kernel/schemas/memory-audit.schema.json does not exist"
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(K.config_doc(), schema)
    jsonschema.validate(K.config_doc(control="none"), schema)
    for bad in (K.config_doc(colour="red"),
                K.config_doc(control={"set": "x", "part": "visible", "size": 4, "baseline": 1, "spread": 1, "colour": 1}),
                K.config_doc(domains=[{"name": "decisions", "paths": ["a"], "colour": "red"}])):
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


@pytest.mark.parametrize("entry", ["module", "cli"])
def test_s1_check_reads_gov_os_s_own_file_and_prints_its_counts(entry, tmp_path):
    """Repository-state: ``check`` on this tree itself (its working tree's file, its tracked files)."""
    home = tmp_path / "home"
    home.mkdir()
    done = subprocess.run([*K.ENTRIES[entry], "check", "--repo", str(K.TREE)], cwd=tmp_path, capture_output=True,
                          text=True, timeout=120, env=K.W171.child_env(home))
    assert (done.returncode, done.stdout.splitlines()) == (0, [CHECK_OK]), (done.returncode, done.stdout, done.stderr)
