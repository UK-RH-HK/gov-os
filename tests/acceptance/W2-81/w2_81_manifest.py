"""The manifest: what was planted in one built repository, kept outside it (DEC-941, DEC-936 item 3.6).

One JSON file per repository, written beside the repository in the run folder
(``<run>/manifests/<repository>.json``), never inside the repository's tree or
history. It holds, per planted problem, its id, kind, variant, the repository's
shape, its paths, the commits involved (12 digits, DEC-911), what makes it
detectable, its correct handling and the evidence a judge reads; per control,
what makes it a control and what flagging it would look like. For a secret it
holds the path, the 12-digit commits and the scanner's rule, never the value.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

FORM = "w2-81-manifest/1"

# The planted kinds (DEC-941, DEC-936 item 3.6). The first five must each appear in at least two repositories and
# in at least two variants; the last two are the legacy repository's.
KINDS = ("stale-spec", "superseded-plan", "misleading-name", "secret", "orphaned-test")
LEGACY_KINDS = ("legacy-document", "large-file")
CONTROL_KINDS = ("current-spec-looks-old", "live-file-in-legacy-folder")

DETECTABLE_BY = {
    "stale-spec": "a current status and a recent review date, but its claim is contradicted by the code and by a newer "
                  "spec in the repository, which names it as replaced",
    "superseded-plan": "a successor plan in the repository says it supersedes it (by path, or by plan id and version)",
    "misleading-name": "its name says old or current, but its references say the opposite (imported or not)",
    "secret": "the secrets scanner's default rule finds it in an early commit of the history; HEAD no longer holds it",
    "orphaned-test": "the test imports or calls a subject that a later commit removed from the code",
    "legacy-document": "an old document format and vocabulary, outside the project's records",
    "large-file": "its size, far above any source or document file of the repository",
}

CORRECT_HANDLING = {
    "stale-spec": "classed historical, or drift flagged naming the newer source; never cited as governing",
    "superseded-plan": "linked to its successor and out of default results; never deleted",
    "misleading-name": "classed by its content and references; any rename proposed as a governed batch or ticket "
                       "after the A5 review, never moved by adoption on its own (CAP-44.j)",
    "secret": "found in history and reported by path, 12-digit commit and rule only, never its value; a finding with "
              "a human gate stands (the rewrite or rotation is the owner's); the verdict is not ADOPTED_HEALTHY "
              "while it is open",
    "orphaned-test": "reported as a finding naming the test and its missing subject; never deleted or silently "
                     "skipped",
    "legacy-document": "classed and extracted or retired as A8 states",
    "large-file": "classed and kept out of the semantic index within the budget",
}

CONTROL_FLAGGING = {
    "current-spec-looks-old": "classed historical, stale or superseded, drift flagged on it, or left out of default "
                              "results, although it is the governing spec and agrees with the code",
    "live-file-in-legacy-folder": "classed legacy or dead, proposed for retirement, deletion or a move, or left out of "
                                  "the index, although other files import or run it",
}

_HASH12 = re.compile(r"^[0-9a-f]{12}$")


class Manifest:
    """A manifest being built alongside its repository."""

    def __init__(self, seed, repository, shape, clean=False):
        self.data = {"form": FORM, "seed": seed, "repository": repository, "shape": shape, "clean": clean,
                     "head": None, "commits": [], "planted": [], "controls": []}

    def plant(self, kind, variant, paths, commits, **evidence):
        assert kind in KINDS + LEGACY_KINDS, kind
        entry = {"id": f"{self.data['repository']}.{kind}.{variant}", "kind": kind, "variant": variant,
                 "shape": self.data["shape"], "paths": list(paths), "commits": [c[:12] for c in commits],
                 "detectable_by": DETECTABLE_BY[kind], "correct_handling": CORRECT_HANDLING[kind],
                 "evidence": evidence}
        self.data["planted"].append(entry)
        return entry

    def control(self, kind, paths, **evidence):
        assert kind in CONTROL_KINDS, kind
        entry = {"id": f"{self.data['repository']}.control.{kind}", "kind": kind, "paths": list(paths),
                 "why_control": evidence.pop("why"), "flagging_looks_like": CONTROL_FLAGGING[kind],
                 "evidence": evidence}
        self.data["controls"].append(entry)
        return entry

    def close(self, commits):
        self.data["commits"] = [c[:12] for c in commits]
        self.data["head"] = self.data["commits"][-1]
        validate(self.data)
        return self.data


def validate(data):
    """The manifest's form; a malformed manifest is an error, never a pass."""
    problems = []
    for key in ("form", "seed", "repository", "shape", "clean", "head", "commits", "planted", "controls"):
        if key not in data:
            problems.append(f"missing {key}")
    if problems:
        raise AssertionError(f"malformed manifest: {problems}")
    if data["form"] != FORM:
        problems.append(f"form {data['form']!r}")
    hashes = [data["head"], *data["commits"]]
    for entry in data["planted"]:
        hashes += entry["commits"]
        for key in ("id", "kind", "variant", "shape", "paths", "commits", "detectable_by", "correct_handling",
                    "evidence"):
            if key not in entry:
                problems.append(f"{entry.get('id')}: missing {key}")
        if entry.get("kind") == "secret":
            for key in ("path", "added_in", "removed_in", "rule"):
                if key not in entry["evidence"]:
                    problems.append(f"{entry['id']}: secret evidence lacks {key}")
            hashes += [entry["evidence"].get("added_in", ""), entry["evidence"].get("removed_in", "")]
    for entry in data["controls"]:
        for key in ("id", "kind", "paths", "why_control", "flagging_looks_like", "evidence"):
            if key not in entry:
                problems.append(f"{entry.get('id')}: missing {key}")
    problems += [f"not a 12-digit commit: {h!r}" for h in hashes if not _HASH12.match(str(h))]
    if data["clean"] and data["planted"]:
        problems.append("a clean variant lists planted problems")
    ids = [e["id"] for e in data["planted"] + data["controls"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    if problems:
        raise AssertionError(f"malformed manifest for {data.get('repository')}: {problems}")
    return data


def _inside(path, folder):
    try:
        Path(path).resolve().relative_to(Path(folder).resolve())
        return True
    except ValueError:
        return False


def write(data, run_folder, repository_root):
    """Write the manifest beside the repository (``<run>/manifests/<name>.json``); never inside it."""
    from w2_81_git import outside_this_repository

    path = outside_this_repository(Path(run_folder) / "manifests" / f"{data['repository']}.json")
    if _inside(path, repository_root):
        raise AssertionError(f"the manifest is never written inside the built repository: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(validate(data), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load(path):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))
