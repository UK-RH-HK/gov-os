"""KPI S2 (D-0003): every policy key maps to a check or is declared informational.

The policies section of ``governance/project/path-map.yaml`` maps each key to a
strength (hard-block, warning, informational). D-0003 requires that every key
maps to an executable check or is declared informational.
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# Every policy key maps to a check or is informational
# --------------------------------------------------------------------------

NOT_COVERED = "POLICY_NOT_COVERED"
STATES_THE_KEYS = "states-the-policy-keys"


def _uncovered(project, sandbox, interface):
    """The policy keys ``gov check`` reports as covered by no check, and the run."""
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    return sorted(finding.get("policy") for entry in support.checks_of(result) if isinstance(entry, dict)
                  for finding in entry.get("findings") or []
                  if isinstance(finding, dict) and finding.get("code") == NOT_COVERED), run


def _declarations(project):
    """Every check declaration this project holds, read from its own files: id -> mapping."""
    import yaml
    held = {}
    for path in sorted((project.root / support.CHECKS_REL).glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            held[path.stem] = data
    return held


def _stated(declarations):
    """The policy keys the declarations state under ``enforces``."""
    return {key for data in declarations.values() for key in data.get("enforces") or []}


def test_every_policy_key_maps_to_a_check_or_is_informational(project, sandbox, interface):
    """A key maps to a check when, and only when, a declared check of the project states it under ``enforces``
    (DEC-613, DEC-620); the name of a family or of a result maps nothing. A project of this suite holds the kernel
    template's declarations, some of which state keys, and the core declarations as this suite writes them, which
    state none. So, of the nine keys that are not informational: exactly those no declaration of this project
    states are reported, and none is once a declared check states the remaining ones."""
    not_informational = {key for key, strength in support.POLICIES.items() if strength != "informational"}
    project.add_core_declarations()
    project.add_path_map({"all": ["**/*"]})
    declarations = _declarations(project)
    stated = _stated(declarations)
    owed = sorted(not_informational - stated)
    # the premises, each read from the project's own files: a stated key and an unstated one both exist, and one
    # unstated key is contained in the family name of a declaration that states nothing
    assert stated & not_informational, \
        "no declaration of this project states a policy key: nothing shows a stated key is not reported"
    assert "human_gate" in owed, f"a declaration of this project states human_gate: {sorted(declarations)}"
    named = declarations.get("core-authority") or {}
    assert "authority" in str(named.get("family")) and not named.get("enforces") and "authority" in owed, \
        f"this project holds no family named after a key it does not state: {named}, stated {sorted(stated)}"
    reported, run = _uncovered(project, sandbox, interface)
    assert reported == owed, \
        (f"the policy keys reported are not exactly those no declaration of this project states: {reported}, "
         f"owed {owed}, stated {sorted(stated)}\n{run.describe()}")
    project.add_check_declaration(STATES_THE_KEYS, "graph integrity")
    declared = project.root / support.CHECKS_REL / f"{STATES_THE_KEYS}.yaml"
    declared.write_text(declared.read_text(encoding="utf-8").rstrip("\n") + f"\nenforces: [{', '.join(owed)}]\n",
                        encoding="utf-8")
    assert _stated(_declarations(project)) >= not_informational
    reported, run = _uncovered(project, sandbox, interface)
    assert not reported, f"policy keys a declared check states under enforces are reported: {reported}\n{run.describe()}"


def test_a_new_policy_key_with_no_check_and_not_informational_is_red(green_project, sandbox, interface):
    """A new hard-block policy key with no associated check fails: a check is RED with a finding that names the
    key, and it is the only key reported.

    Revised (W2-67): the base is the green project with a valid path map (its namespaces a mapping, as the kernel
    schema has them), whose policies are the keys a declared check of the project states and the informational
    ones; before, the path map's ``namespaces: []`` was refused (CONFIG_INVALID) before any check ran, on a base
    that was red anyway (I2 R1)."""
    import yaml
    project = green_project
    stated = _stated(_declarations(project))
    project.add_path_map({"all": ["**/*"]})
    path_map_path = project.root / support.PATH_MAP_REL
    data = yaml.safe_load(path_map_path.read_text(encoding="utf-8"))
    data["policies"] = {key: strength for key, strength in support.POLICIES.items()
                        if strength == "informational" or key in stated}
    data["policies"]["brand_new_policy"] = "hard-block"
    path_map_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    reported, run = _uncovered(project, sandbox, interface)
    assert reported == ["brand_new_policy"], (
        f"the policy keys reported are not exactly the new one: {reported}, stated {sorted(stated)}\n{run.describe()}"
    )
    result, envelope = support.result_and_envelope(run, interface)
    red = [entry.get("id") for entry in support.checks_of(result) if isinstance(entry, dict)
           and entry.get("status") == support.RED and support.findings_naming(entry, "brand_new_policy")]
    assert red, f"no check is RED with a finding that names brand_new_policy\n{run.describe()}"
    assert envelope["ok"] is False and run.returncode == support.EXIT_CHECK_FAILED, run.describe()


def test_an_informational_policy_key_with_no_check_passes(project, sandbox, interface):
    """An informational policy key with no associated check does not fail."""
    import yaml
    path_map_path = project.root / support.PATH_MAP_REL
    if path_map_path.is_file():
        data = yaml.safe_load(path_map_path.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "namespaces": [], "policies": dict(support.POLICIES)}
    data["policies"]["brand_new_info"] = "informational"
    path_map_path.parent.mkdir(parents=True, exist_ok=True)
    path_map_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "policy" in str(entry).lower() and "brand_new_info" in str(entry).lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"informational policy key triggers RED in {family_name}\n{run.describe()}"
