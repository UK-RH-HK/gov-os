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

def test_every_policy_key_maps_to_a_check_or_is_informational(project, sandbox, interface):
    """Every policy key in path-map.yaml maps to a check or is declared informational."""
    project.add_core_declarations()
    project.add_path_map({"all": ["**/*"]})
    project.commit()
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    check_ids = set()
    for entry in support.checks_of(result):
        if isinstance(entry, dict) and "id" in entry:
            check_ids.add(entry["id"])
    for key, strength in support.POLICIES.items():
        if strength == "informational":
            continue
        assert key in families or any(key in str(fam) for fam in families), \
            f"policy key {key!r} (strength {strength}) is not covered by a check or family"


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
