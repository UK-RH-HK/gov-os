"""The decisions validator's register checks (W2-55; DEC-791 item 1, DEC-825 item 2, DEC-851, DEC-866 item 1).

``check_tags(root)`` gives a finding for every entry of the register whose tags line is missing or incomplete, whose
domain or scope is outside its closed list, whose "lands in" places ``HEAD`` does not hold or are not where its
scope says, and for every status that does not name what superseded or changed the entry. Findings have W2-03's
shape; an empty list passes. They are not added to ``gov.decisions.check`` (the close reads that list).

``python3 -m gov.decisions.tags``, in a project root, prints the findings and exits 1 when there are any; a
register that cannot be read exits 1 too, never 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

from gov.decisions.checker import _finding
from gov.decisions.register import DOMAINS, SCOPES, TAG_PARTS, read


def _tag_findings(entry: dict, path: str, tree: dict, out: set) -> list[dict]:
    record_id, tags = entry["id"], entry["tags"]
    if tags is None:
        return [_finding("TAG_MISSING", [record_id], [path], f"{record_id} has no tags line (`- **Tags:**`)")]
    missing = [part for part in TAG_PARTS if not tags.get(part)]
    found = [_finding("TAG_MISSING", [record_id], [path], f"{record_id}: its tags line has no {', no '.join(missing)}"
                      " part")] if missing else []
    if tags.get("domain") and tags["domain"] not in DOMAINS:
        found.append(_finding("TAG_DOMAIN_UNKNOWN", [record_id], [path], f"{record_id}: domain {tags['domain']!r} is "
                              f"not in the closed list ({', '.join(DOMAINS)})"))
    if tags.get("scope") and tags["scope"] not in SCOPES:
        found.append(_finding("TAG_SCOPE_UNKNOWN", [record_id], [path], f"{record_id}: scope {tags['scope']!r} is "
                              f"neither {' nor '.join(SCOPES)}"))
    places = tags.get("places") or []
    if not places:
        return found
    if places == ["none"]:
        if record_id not in out:
            found.append(_finding("TAG_LANDS_IN_MISPLACED", [record_id], [path], f"{record_id} is in force and lands "
                                  "in none: an entry in force lands where its scope says"))
        return found
    unknown = [place for place in places if tree.get(place, ("", ""))[1] != "blob"]
    if unknown:
        found.append(_finding("TAG_LANDS_IN_UNKNOWN", [record_id], [path], f"{record_id} lands in "
                              f"{', '.join(unknown)}, which HEAD does not hold"))
    where = SCOPES.get(tags.get("scope"))
    if where and not any(place.startswith(where) for place in places):
        found.append(_finding("TAG_LANDS_IN_MISPLACED", [record_id], [path], f"{record_id} is scoped "
                              f"{tags['scope']} and lands in no file under {where}"))
    return found


def check_tags(root: Path) -> list[dict]:
    """The register's findings, in a fixed order; an empty list passes."""
    from gov.store.loader import _tree

    root = Path(root)
    register = read(root)
    if register is None:
        return []
    path, tree, held = register["path"], _tree(root), {entry["id"]: entry for entry in register["entries"]}
    out = register["superseded"].keys() | register["done"]
    found = []
    for entry in register["entries"]:
        record_id = entry["id"]
        found += _tag_findings(entry, path, tree, out)
        if entry["status"] == "SUPERSEDED" and entry["successor"] not in held:
            found.append(_finding("STATUS_SUCCESSOR_UNNAMED", [record_id], [path], f"{record_id} is SUPERSEDED and "
                                  + (f"its successor {entry['successor']} is not in the register" if entry["successor"]
                                     else "its status names no successor (`SUPERSEDED by DEC-<n>`)")))
        for relation, olds in (("supersedes", entry["supersedes"]), ("changes", entry["changes"])):
            for old in olds:
                marked = held.get(old)
                if marked is None or old == record_id:
                    continue
                if record_id not in marked["changed_by"] and record_id not in marked["named"]:
                    found.append(_finding("STATUS_RELATION_UNMARKED", [old, record_id], [path],
                                          f"{record_id} {relation} {old}, and {old}'s status line does not name "
                                          f"{record_id} (`SUPERSEDED by {record_id}` or `**Changed by:** "
                                          f"{record_id}`)"))
    return sorted(found, key=lambda finding: (finding["code"], finding["ids"], finding["paths"]))


def main() -> int:
    from gov.cli.errors import GovError

    try:
        found = check_tags(Path.cwd())
    except GovError as exc:
        print(f"decision tags: {exc.code}: {exc.message}")
        return 1
    for finding in found:
        print(f"{finding['code']}: {finding['message']}")
    print(f"decision tags: {len(found)} finding(s)" if found else "decision tags: green")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
