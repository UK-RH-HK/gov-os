"""KPI 6 is evidence, not behaviour: the evidence file exists and states the figures the KPI names (never their
values)."""

from __future__ import annotations

import re

import w2_126_support as S

EVIDENCE_REL = "docs/changes/W2-126-evidence.md"
# What the KPI names, each as words the file must hold (case ignored).
NAMED = {
    "the texts sent to the embedder per day": r"per day|a day",
    "before and after": r"\bbefore\b[\s\S]*\bafter\b|\bafter\b[\s\S]*\bbefore\b",
    "a lead's first rebuild of a code-changing ticket": r"first rebuild",
    "a close's clone": r"\bclone\b",
    "the cache's size": r"cache'?s? size|size of the cache",
}


def test_the_evidence_file_states_the_named_figures():
    path = S.REPO_ROOT / EVIDENCE_REL
    assert path.is_file(), f"{EVIDENCE_REL} does not exist"
    text = path.read_text(encoding="utf-8")
    assert re.search(r"\d", text), "the evidence file states no figure"
    missing = [name for name, pattern in NAMED.items() if not re.search(pattern, text, re.IGNORECASE)]
    assert not missing, f"the evidence file does not state: {missing}"
