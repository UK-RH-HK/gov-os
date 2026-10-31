"""The question sets of the W2-81 proving ground: their form, and their resolution against a built repository.

One YAML file per repository (``<repository>.yaml``), the same form for both halves:

- the visible (development) half is ``tests/acceptance/W2-81/questions/``, written by this ticket;
- the hidden (measurement) half is ``fixtures/evaluation/adoption-proving-ground/hidden/``, written by W2-93.

The file holds ``form: w2-81-questions/1``, ``repository`` and ``questions``. Each question holds:

- ``id``, ``category``, ``question`` and ``gold_answer``;
- ``sources``: each ``{path, holds}``, the file and the text of the line that holds the answer's evidence;
- ``forbidden``: the paths no answer may cite in its top five.

Names, places and wording are seeded, so every text is a template: ``{name}`` is a fact of the repository's manifest
(``facts``). A forbidden citation whose fact the repository lacks is dropped (the clean variant plants nothing); a
source whose fact is missing, or whose line is not in the built HEAD, makes the question malformed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

import w2_81_git as gitlib

FORM = "w2-81-questions/1"
VISIBLE = Path(__file__).resolve().parent / "questions"
HIDDEN_DEFAULT = gitlib.REPO_ROOT / "fixtures" / "evaluation" / "adoption-proving-ground" / "hidden"


class QuestionError(AssertionError):
    """A question set or question that cannot be read or resolved. Its message names ids, never a text."""


@dataclass
class Question:
    id: str
    part: str            # "visible" or "hidden"
    category: str
    question: str        # never printed or written by the scorer or the runner
    gold_answer: str     # never printed or written by the scorer or the runner
    sources: list        # [(path, line, holds)]
    forbidden: list      # [path]

    def __repr__(self):  # what a failure shows: the id, never the text
        return f"<question {self.id} ({self.part})>"


def load_set(path):
    """A question file's mapping; a QuestionError naming the file (not its content) otherwise."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise QuestionError(f"the question set {Path(path).name} cannot be read") from None
    if not isinstance(data, dict) or data.get("form") != FORM or not isinstance(data.get("questions"), list):
        raise QuestionError(f"the question set {Path(path).name} is not of the form {FORM}")
    if data.get("repository") != Path(path).stem:
        raise QuestionError(f"the question set {Path(path).name} names another repository")
    return data


def sets_in(folder):
    """Repository -> its question set's mapping, for each ``*.yaml`` of ``folder``."""
    return {path.stem: load_set(path) for path in sorted(Path(folder).glob("*.yaml"))}


def _fill(template, facts, qid):
    try:
        return str(template).format_map(facts)
    except (KeyError, IndexError, ValueError):
        raise QuestionError(f"{qid}: a template names a fact the repository does not have") from None


def resolve(question_set, manifest, root, part):
    """The set's questions with real paths and lines, read from the built HEAD (``manifest['head']``)."""
    facts = manifest.get("facts") or {}
    resolved, seen = [], set()
    for item in question_set["questions"]:
        qid = str(item.get("id")) if isinstance(item, dict) else "?"
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip()
                                                 for k in ("id", "category", "question", "gold_answer")):
            raise QuestionError(f"{qid}: id, category, question and gold_answer are required")
        if qid in seen:
            raise QuestionError(f"{qid}: the id is given twice")
        seen.add(qid)
        sources = []
        for source in item.get("sources") or []:
            if not isinstance(source, dict) or not {"path", "holds"} <= set(source):
                raise QuestionError(f"{qid}: a source is not a mapping with path and holds")
            path, holds = _fill(source["path"], facts, qid), _fill(source["holds"], facts, qid)
            text = gitlib.blob(root, manifest["head"], path)
            line = next((n for n, row in enumerate((text or "").splitlines(), 1) if holds in row), None)
            if line is None:
                raise QuestionError(f"{qid}: a gold source is not in the built repository as stated")
            sources.append((path, line, holds))
        if not sources:
            raise QuestionError(f"{qid}: a question needs at least one gold source")
        forbidden = []
        for template in item.get("forbidden") or []:
            try:
                forbidden.append(str(template).format_map(facts))
            except KeyError:
                continue  # a planted source this repository does not have
        resolved.append(Question(qid, part, item["category"], _fill(item["question"], facts, qid),
                                 _fill(item["gold_answer"], facts, qid), sources, forbidden))
    return resolved
