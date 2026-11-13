"""The reader's and graders' pinned parts (Interface item 7; S3; DEC-1097 (1)(d), DEC-1098 (1)).

Copied verbatim from the CTO's scratch ``drafts/d4b/e2_run.py`` (sha256 ``f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a``;
``e2g_run.py`` and ``e3_run.py`` hold the same strings): the reader's instruction and schema, the grader's instruction
and schema, the reader's attempt cap, the prompt form, the bundle items, the A1/A2/A3 cut (``outcome``) and the exact
McNemar test, with the grader's prompt form. ``tests/unit/memaudit/test_prompts.py`` recomputes each one against the
hash list of item 7: do not edit a string or a function here. (One departure from byte equality, on purpose: the
trailing comment of ``outcome``'s last line is left out, because item 7's hash is of the function's syntax-tree text,
which ends at its last statement, while ``inspect.getsource`` would carry the comment and hash differently.) The refine strings (``REFINE_*``, the glossary) and
``UNRANKED_NOTE`` are not copied: the glossary is a prototype, not the standard.
"""

import math

CAP = 3

READER_SYS = (
    "You answer one question about a software repository, using only the search bundles you are given. Each bundle item "
    "has a path, a line range and the text of those lines. If the bundles answer the question, give the answer and cite "
    "the items (path, start_line, end_line) you rely on. If the bundles do not answer the question, give different search "
    "words in 'search' and set verdict to search_again. If you can tell your answer may be incomplete, search again for "
    "what is missing. If you judge the answer is not in the repository (an id that exists nowhere, say), answer "
    "not_found. Never answer beyond the bundles.")
READER_SCHEMA = {"type": "object", "required": ["verdict", "answer", "citations", "search"], "properties": {
    "verdict": {"type": "string", "enum": ["answer", "search_again", "not_found"]},
    "answer": {"type": "string"},
    "citations": {"type": "array", "items": {"type": "object", "required": ["path", "start_line", "end_line"], "properties": {
        "path": {"type": "string"}, "start_line": {"type": "integer"}, "end_line": {"type": "integer"}}}},
    "search": {"type": "string"}}}
GRADER_SYS = (
    "You grade one answer to a question about a software repository against the gold answer. Return correct when the "
    "answer states the gold answer's facts and contradicts none of them; wrong when it contradicts them or misses their "
    "substance; not_found when it says the answer could not be found. For a question about an id that exists nowhere, "
    "correct means the answer says it was not found or does not exist.")
GRADER_SCHEMA = {"type": "object", "required": ["grade", "reason"], "properties": {
    "grade": {"type": "string", "enum": ["correct", "wrong", "not_found"]}, "reason": {"type": "string"}}}
GRADER_PROMPT = "Question: {question}\n\nGold answer: {gold}\n\nAnswer to grade: {said}"


def items_of(result):
    return [(e.get("path"), int(e.get("start_line")), int(e.get("end_line")), str(e.get("text", "")))
            for e in (result.get("evidence") or [])]


def prompt_of(question, bundles):
    parts = [f"Question: {question}"]
    for k, b in enumerate(bundles, 1):
        parts.append(f"\n=== Bundle {k} ===")
        for path, a, z, text in b:
            parts.append(f"--- {path} lines {a}-{z}\n{text}")
    return "\n".join(parts)


def mcnemar(a, b):
    g = sum(1 for x, y in zip(a, b) if y and not x); l = sum(1 for x, y in zip(a, b) if x and not y)
    n, k = g + l, min(g, l)
    return g, l, (min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0)


def outcome(r, cut):
    """Under condition A<cut>: right end to end, correct, wrong claim, not found."""
    grade = (r["grades"].get("grader") or {}).get("grade")
    answered = r["answered_at"] is not None and r["answered_at"] <= cut
    settled = r["final_verdict"] == "not_found" and len(r["attempts"]) <= cut
    if r["apart"]:
        nf = not answered  # cut before answering, or settled
        right = nf or (answered and grade == "correct")
        return {"right": right, "correct": right, "wrong": answered and grade != "correct", "nf": nf}
    if answered:
        return {"right": grade == "correct" and r["citation_right"], "correct": grade == "correct",
                "wrong": grade != "correct", "nf": False}
    return {"right": False, "correct": False, "wrong": False, "nf": True}
