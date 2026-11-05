"""DEC-1068's index-time methods M1 and M3 (W2-32, notes within S7 and S8): the planted projects and the settings.

- **The settings** (the ticket's note "DEC-1068, the five index-time methods"): each behind a setting off by default,
  validated by the loader (``CONFIG_INVALID`` naming the key). M1 ``file_level_index`` in
  ``governance/project/rebuild.yaml``; M3 ``closure_reverse_depends_on``, in ``rebuild.yaml`` too unless the engineer
  states it is query-time (then ``governance/project/retrieval.yaml``: change ``M3_SETTINGS_REL``).
- **The settings files are kept out of the index** (a namespace of their own, ``lexical_policy: not indexed``, not
  embedded) and written uncommitted, so switching a setting changes no indexed file: an answer that changes, or a store
  that goes stale, does so by the setting alone.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import w2_32_support as s

REBUILD_REL = "governance/project/rebuild.yaml"
RETRIEVAL_REL = "governance/project/retrieval.yaml"
M1_KEY, M1_SETTINGS_REL = "file_level_index", REBUILD_REL
M3_KEY, M3_SETTINGS_REL = "closure_reverse_depends_on", REBUILD_REL
INVALID = ["yes", "1", '"true"', "files"]  # only the YAML booleans true and false are values


def plant(project, files, extra_namespaces=None):
    """A planted project whose settings files are outside the index (and ``extra_namespaces``: name -> namespace)."""
    project = s.plant(project, files)
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"]["project"]["paths"] = [s.PATH_MAP_REL, s.SECRETS_REL, s.MODELS_REL, ".gitignore"]
    document["namespaces"]["settings"] = {**s.namespace([REBUILD_REL, RETRIEVAL_REL], "not embedded"),
                                          "lexical_policy": "not indexed"}
    document["namespaces"].update(extra_namespaces or {})
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "the settings files kept out of the index")
    return project


def settle(project, rel, text):
    """Write the settings file ``rel`` (``None``: remove it), uncommitted (read as it stands in the working tree)."""
    path = Path(project) / rel
    if text is None:
        if path.exists():
            path.unlink()
    else:
        s.write(project, rel, text)


def answer_text(data):
    """A call's answer or what it raised, as text (where a code and a key are looked for)."""
    import json
    return json.dumps({key: item for key, item in data.items() if key not in ("_stderr", "stderr", "gov")})
