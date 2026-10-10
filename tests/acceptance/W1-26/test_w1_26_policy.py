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


def test_every_policy_key_maps_to_a_check_or_is_informational(project, sandbox, interface):
    """A key maps to a check when a declared check states it under ``enforces`` (DEC-620); the name of a family
    or of a result maps nothing. With the kernel's thirteen keys: the nine that are not informational are each
    reported while no declaration states them, and none is once a declared check states them."""
    owed = sorted(key for key, strength in support.POLICIES.items() if strength != "informational")
    project.add_core_declarations()
    project.add_path_map({"all": ["**/*"]})
    reported, run = _uncovered(project, sandbox, interface)
    assert reported == owed, \
        f"policy keys no declaration states are not each reported: {reported}, owed {owed}\n{run.describe()}"
    project.add_check_declaration(STATES_THE_KEYS, "graph integrity")
    declared = project.root / support.CHECKS_REL / f"{STATES_THE_KEYS}.yaml"
    declared.write_text(declared.read_text(encoding="utf-8").rstrip("\n") + f"\nenforces: [{', '.join(owed)}]\n",
                        encoding="utf-8")
    reported, run = _uncovered(project, sandbox, interface)
    assert not reported, f"policy keys a declared check states under enforces are reported: {reported}\n{run.describe()}"


def test_a_new_policy_key_with_no_check_and_not_informational_is_red(project, sandbox, interface):
    """A new hard-block policy key with no associated check fails."""
    import yaml
    path_map_path = project.root / support.PATH_MAP_REL
    if path_map_path.is_file():
        data = yaml.safe_load(path_map_path.read_text(encoding="utf-8"))
    else:
        data = {"version": 1, "namespaces": [], "policies": dict(support.POLICIES)}
    data["policies"]["brand_new_policy"] = "hard-block"
    path_map_path.parent.mkdir(parents=True, exist_ok=True)
    path_map_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    project.commit()
    run = support.run_check(project, sandbox)
    support.assert_red(run, interface)


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
