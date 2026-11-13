"""The refactoring plan: each blocker to full indexing that the assessment finds, as a proposed ticket (W2-88 S2).

``plan(assessment, path_map, out)`` writes, under ``<out>/refactor-plan/``, one ``RP-<nn>-<kind>.md`` per kind of
blocker found (the files of that kind are its ``allowed_paths``), in the kernel's ticket form; ``PLAN.md`` lists them;
a repository with nothing to refactor gets ``NOTHING-TO-REFACTOR.md`` instead, unless the secrets scan did not run or
skipped files: then ``PLAN.md`` states ``secrets: not scanned (<reason>)`` and the unscanned paths, and no file says
there is nothing to refactor (B-1.5). It runs no ``tk``, applies nothing and
commits nothing: the proposals are files for the owner, and the A5 human gate is the only route to them. It reads the
assessment and the path map it is given, and writes nowhere else.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from gov.util.digest import sha256
from gov.util.patterns import _match_pattern

FOLDER = "refactor-plan"
KINDS = ("vendored-no-folder", "generated-no-folder", "namespace-policy", "over-limit", "secret", "no-namespace",
         "two-namespaces")
POLICIES = ("embedded", "not embedded")  # the two values of a namespace's embedding_policy (DEC-388, DEC-694)
PATH_MAP = "governance/project/path-map.yaml"
PROFILE = "STANDARD"


def _namespaces(path_map: dict | None) -> dict[str, dict]:
    spaces = path_map.get("namespaces") if isinstance(path_map, dict) else None
    return {name: space for name, space in spaces.items() if isinstance(space, dict)} if isinstance(spaces, dict) else {}


def _patterns(space: dict) -> list[str]:
    return [item for item in (space.get("paths") or []) if isinstance(item, str)]


def _tracked(assessment: dict) -> list[str]:
    paths = assessment.get("paths")
    return [item for item in paths if isinstance(item, str)] if isinstance(paths, list) else []


def _digest(assessment: dict, out: Path) -> str:
    """The sha256 of ``<out>/memory-assessment.json`` where it is the assessment given, else of its serialisation."""
    text = json.dumps(assessment, indent=2, sort_keys=True) + "\n"
    try:
        held = (Path(out) / "memory-assessment.json").read_bytes()
        if json.loads(held) == json.loads(text):
            return sha256(held)
    except (OSError, ValueError):
        pass
    return sha256(text.encode("utf-8"))


def _own_folder(rel: str, flagged: set[str], tracked: list[str]) -> bool:
    """Whether ``rel`` lies in a folder that holds nothing but flagged files: the folder is that code's own."""
    folder = rel.rpartition("/")[0]
    if not folder:
        return False
    return all(path in flagged for path in tracked if path.startswith(folder + "/"))


def _blockers(assessment: dict, path_map: dict | None, out: Path) -> dict[str, dict]:
    """Kind -> ``{paths, why}``, only the kinds that have a blocker."""
    spaces, found = _namespaces(path_map), {}
    for kind, key in (("vendored-no-folder", "vendored"), ("generated-no-folder", "generated")):
        flagged = {item["path"] for item in assessment.get(key, [])}
        tracked = _tracked(assessment)
        held = [item["path"] for item in assessment.get(key, [])
                if item.get("by") != "folder" and not _own_folder(item["path"], flagged, tracked)]
        if held:
            found[kind] = {"paths": sorted(held), "why": f"{key} code with no folder of its own"}
    faulty = {name: space.get("embedding_policy") for name, space in spaces.items()
              if space.get("embedding_policy") not in POLICIES}
    if faulty:
        found["namespace-policy"] = {"paths": [PATH_MAP], "why": "a namespace states an embedding_policy that is "
                                     "neither `embedded` nor `not embedded`: " + ", ".join(sorted(faulty))}
    over = [item["path"] for item in assessment.get("no_route", []) if item.get("reason") == "over-limit"]
    if over:
        found["over-limit"] = {"paths": sorted(over), "why": "files over the chunker's limit"}
    secret = sorted({item["path"] for item in assessment.get("secrets", [])})
    if secret:
        found["secret"] = {"paths": secret, "why": "a secret in a tracked file (by rule id, never the value)"}
    if spaces:
        none, two = [], []
        for rel in _tracked(assessment):
            held = [name for name, space in spaces.items() if any(_match_pattern(rel, p) for p in _patterns(space))]
            (none if not held else two if len(held) > 1 else []).append(rel)
        if none:
            found["no-namespace"] = {"paths": [PATH_MAP, *sorted(none)], "why": "paths that fall in no namespace"}
        if two:
            found["two-namespaces"] = {"paths": [PATH_MAP, *sorted(two)], "why": "paths that fall in two namespaces"}
    return found


TITLES = {
    "vendored-no-folder": "Give the vendored code a folder of its own, kept out of the embedded namespaces",
    "generated-no-folder": "Give the generated code a folder of its own, kept out of the embedded namespaces",
    "namespace-policy": "State every namespace's embedding_policy as `embedded` or `not embedded`",
    "over-limit": "Split or remove the files over the chunker's limit",
    "secret": "Remove the secrets from the tracked files and rotate them",
    "no-namespace": "Give every tracked path a namespace of the path map",
    "two-namespaces": "Give every tracked path exactly one namespace of the path map",
}


def _kpis(kind: str, paths: list[str]) -> dict:
    where = f"`{paths[0]}`" + (f" and {len(paths) - 1} more" if len(paths) > 1 else "")
    check = {
        "vendored-no-folder": ("the vendored code lies in a folder of its own, and a namespace of the path map says "
                               "`embedding_policy: not embedded` for it",
                               "`gov rebuild` records none of its files as embedded and `gov doctor` lists none as unknown"),
        "generated-no-folder": ("the generated code lies in a folder of its own, and a namespace of the path map says "
                                "`embedding_policy: not embedded` for it",
                                "`gov rebuild` records none of its files as embedded and `gov doctor` lists none as unknown"),
        "namespace-policy": ("every namespace of the path map states `embedding_policy` as `embedded` or `not embedded`",
                             "`gov adopt --lite --stage A3` accepts the path map with no EMBEDDING_POLICY refusal"),
        "over-limit": ("no tracked file is over the chunker's limit (a file over 1 MiB, or a line over 32,768 characters)",
                       "a new `memory-assessment.json` lists no `over-limit` file"),
        "secret": ("no tracked file holds a secret and each exposed secret is rotated",
                   "a new `memory-assessment.json` lists no secret and the secrets filter refuses no tracked file"),
        "no-namespace": ("every tracked path is held by one namespace of the path map",
                         "`gov doctor` lists no unknown artefact"),
        "two-namespaces": ("every tracked path is held by exactly one namespace of the path map",
                           "`gov doctor` lists no path held by two namespaces"),
    }[kind]
    return {"success": [f"{check[0][0].upper()}{check[0][1:]} for {where}. Verify: {check[1]}."],
            "failure": [f"A tracked file loses its content or its history in the change, or a secret's value is "
                        f"written into a record, a log or this ticket. Verify: `git diff --stat` of the change "
                        f"names only the proposal's paths and a grep of the change for the secret's value finds 0 hits."]}


def unscanned(assessment: dict) -> dict | None:
    """``{reason, unscanned, all}`` where the secrets scan did not run or skipped files, else None. ``unscanned`` holds the
    skipped paths; where the scanner did not run, ``all`` is the count of tracked files and none is named singly."""
    skipped = [item for item in assessment.get("secrets_unscanned") or [] if isinstance(item, str)]
    if assessment.get("secrets_scanned") is False:
        return {"reason": assessment.get("secrets_unscanned_reason") or "the secrets scan did not run", "unscanned": skipped,
                "all": len(_tracked(assessment))}
    if skipped:
        return {"reason": assessment.get("secrets_unscanned_reason") or "blobs over the scan limit were not scanned",
                "unscanned": skipped, "all": None}
    return None


def plan(assessment: dict, path_map: dict | None, out: Path) -> dict:
    """The proposals for ``assessment`` under ``<out>/refactor-plan/``; ``{count, proposals, nothing, secrets_unscanned,
    assessment_sha256}`` (``nothing`` is False wherever the secrets scan did not cover the repository)."""
    out = Path(out)
    folder = out / FOLDER
    folder.mkdir(parents=True, exist_ok=True)
    digest = _digest(assessment, out)
    blockers = _blockers(assessment, path_map, out)
    for old in list(folder.glob("RP-*.md")) + [folder / "PLAN.md", folder / "NOTHING-TO-REFACTOR.md"]:
        old.unlink(missing_ok=True)
    proposals = []
    for number, kind in enumerate((kind for kind in KINDS if kind in blockers), 1):
        blocker = blockers[kind]
        name = f"RP-{number:02d}-{kind}.md"
        head = {"id": f"RP-{number:02d}", "type": "task", "status": "PROPOSED", "title": TITLES[kind],
                "class": "implementation", "allowed_paths": blocker["paths"], "kpis": _kpis(kind, blocker["paths"]),
                "profile": PROFILE, "sources": [f"memory-assessment sha256:{digest}"]}
        body = (f"\n# {head['id']} {head['title']}\n\nProposed by `gov adopt --lite --stage MA`. {blocker['why'].capitalize()}. "
                f"{len(blocker.get('files', blocker['paths']))} path(s). Nothing is applied: this file is a proposal "
                "for the repository's owner, and the A5 human gate is the only route to it.\n")
        (folder / name).write_text("---\n" + yaml.safe_dump(head, sort_keys=False, allow_unicode=True, width=120)
                                   + "---\n" + body, encoding="utf-8")
        proposals.append({"file": f"{FOLDER}/{name}", "kind": kind, "title": head["title"]})
    blind = unscanned(assessment)
    if blind:  # never "no secret" for a scan that did not run (B-1.5): PLAN.md says so, with the proposals found
        where = (f" all {blind['all']} tracked files" if blind["all"] is not None  # one line (RV2-2)
                 else "\n" + "\n".join(f"- `{path}`" for path in blind["unscanned"]))  # a list from the next line
        lines = [f"- `{item['file'].rsplit('/', 1)[-1]}`: {item['kind']}: {item['title']}" for item in proposals]
        (folder / "PLAN.md").write_text(
            "# Refactoring plan\n\nSources: memory-assessment sha256:" + digest + "\n\n"
            f"secrets: not scanned ({blind['reason']})\n\nUnscanned paths:{where}\n\n"
            + ("\n".join(lines) + "\n" if lines else "No other blocker was found.\n"), encoding="utf-8")
    elif proposals:
        lines = [f"- `{item['file'].rsplit('/', 1)[-1]}`: {item['kind']}: {item['title']}" for item in proposals]
        (folder / "PLAN.md").write_text("# Refactoring plan\n\nSources: memory-assessment sha256:" + digest + "\n\n"
                                        + "\n".join(lines) + "\n", encoding="utf-8")
    else:
        (folder / "NOTHING-TO-REFACTOR.md").write_text(
            f"# Nothing to refactor\n\nThe assessment (memory-assessment sha256:{digest}) found no blocker to full "
            "indexing: no vendored or generated code without a folder, no namespace policy to state, no file over "
            "the chunker's limit, no secret in a tracked file and no path in no namespace or in two.\n",
            encoding="utf-8")
    return {"count": len(proposals), "proposals": proposals, "nothing": not proposals and not blind,
            "secrets_unscanned": blind, "assessment_sha256": digest}
