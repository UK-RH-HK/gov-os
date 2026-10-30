"""W2-69, the last round (DEC-909 item 6, DEC-136), behaviour 3: the chance red stays away at every read edge, with
key blocks cut out whole.

KPI (DEC-909 items 2, 3 and 6): "... an embedded fragment of a longer
identifier stays unflagged at every read edge (the chance red not brought
back)." KPI 2, success: "An embedded fragment of a longer identifier is not
flagged: a token-shaped string inside a word, placed at every offset relative to
wherever the check or gitleaks begins a read, is not a finding, for every rule
with a leading word boundary"; failure: "A word-internal fragment flagged at a
read edge (the chance red of W2-62's queue, 2026-10-22)."

The fix gives gitleaks each BEGIN...END key block whole, as its own piece, so the
check now cuts its input where a block begins and ends. These cases put the first
batch's word-internal fragments (each of the project's four rules: word
characters, then a string that alone is a token by the rule) at every byte offset
around BEGIN and END lines, as the first batch's K2 cells do: one line of cells
of 24 bytes, in 24 files shifted by 0 to 23 bytes, so that wherever a read begins
near a marker, one file has a token-shaped string beginning there inside its
word. The situations:

- directly before a BEGIN line, and directly after an END line (a block whose body
  is too short for gitleaks' ``private-key`` rule);
- in the text between two blocks, and around two blocks back to back;
- after a BEGIN line with no END line (30,000 bytes of fragments after it), and
  after an END line with no BEGIN line;
- after a block longer than 24 KB (30,000 bytes);
- around a BEGIN marker in the middle of a line (``word-----BEGIN ...``) and an
  END marker followed on its line by a word;
- around a key block of 13,900 bytes (the size the fix cuts out whole).

The fragments are the only thing a rule could match (premises, by the real
gitleaks, with both rule sets): a block whose body is too short for the rule; or,
where two blocks or a block's body would make the rule match (from the first
BEGIN to a later END), blocks holding the run of the alphabet that gitleaks'
global allowlist shelters under ``extend``, which no rule of the project's holds.
Each situation lies 100,000 bytes into the text, past gitleaks' first read; a
plain file under ``.gov-runtime/`` and a single SQLite text value. Expected: no
finding. The control: a real token at a word boundary at the same places is a
finding.

Today these cases pass (the check does not cut at a key block yet): they guard
the fix.
"""

from __future__ import annotations

import pytest

import w2_69_last_round_support as lr
import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
Q = 24
ZONE = 40                   # cells of fragments on each side of a marker
LONG_ZONE = 1_250           # 30,000 bytes of cells after a BEGIN line with no END line
FILLER = 100_000            # the text before a situation: past gitleaks' first read
DASHES = "-" * 5
BEGIN = f"{DASHES}BEGIN RSA PRIV" + f"ATE KEY{DASHES}"
END = f"{DASHES}END RSA PRIV" + f"ATE KEY{DASHES}"
FORMS = {"plain-file": ".txt", "sqlite-value": ".db"}


def _short_body(seed):
    """32 base64 characters: from a BEGIN line through this body to the END line's KEY there are fewer than the 64
    characters gitleaks' ``private-key`` rule asks for."""
    return support.chars(f"short-{seed}", 32, support.B64)


def _sheltered_body(seed):
    """As short, holding the run of the alphabet gitleaks' global allowlist shelters under ``extend``: any match of
    the key rule from a BEGIN line just before it holds the run."""
    return "abcdefghijklm" + "nopqrstuvwxyz" + support.chars(f"shelter-{seed}", 6, support.B64)


def _after(word, phase, cells=ZONE):
    """Cells beginning right after a marker: ``phase`` spaces, then ``word`` at the start of each cell."""
    return " " * phase + "".join(word.ljust(Q) for _ in range(cells))


def _before(word, phase, cells=ZONE):
    """Cells ending right before a marker: ``word`` at the end of each cell, then ``phase`` spaces."""
    return "".join(word.rjust(Q) for _ in range(cells)) + " " * phase


def _block(seed, body):
    return f"{BEGIN}\n{body}\n{END}"


SITUATIONS = {
    "directly-before-a-begin-line":
        lambda w, p, s: _before(w, p) + "\n" + _block(s, _short_body(s)) + "\n",
    "directly-after-an-end-line":
        lambda w, p, s: _block(s, _short_body(s)) + "\n" + _after(w, p) + "\n",
    "in-the-text-between-two-blocks":
        lambda w, p, s: (_block(s, _sheltered_body(s + "1")) + "\n" + _after(w, p, ZONE // 2) + _before(w, p, ZONE // 2)
                         + "\n" + _block(s, _sheltered_body(s + "2")) + "\n"),
    "around-two-blocks-back-to-back":
        lambda w, p, s: (_before(w, p) + "\n" + _block(s, _sheltered_body(s + "1")) + "\n"
                         + _block(s, _sheltered_body(s + "2")) + "\n" + _after(w, p) + "\n"),
    "after-a-begin-line-with-no-end-line":
        lambda w, p, s: _before(w, p) + "\n" + BEGIN + "\n" + _after(w, p, LONG_ZONE) + "\n",
    "after-an-end-line-with-no-begin-line":
        lambda w, p, s: _before(w, p) + "\n" + END + "\n" + _after(w, p) + "\n",
    "after-a-block-longer-than-24-kb":
        lambda w, p, s: (_before(w, p) + "\n" + review.key_block("pem-rsa", 30_000, f"long-{s}", sheltered=True)
                         + "\n" + _after(w, p) + "\n"),
    "around-a-begin-marker-in-the-middle-of-a-line":
        lambda w, p, s: _before(w, p) + _block(s, _short_body(s)) + _after(w, p) + "\n",
    "around-a-key-block-of-13900-bytes":
        lambda w, p, s: (_before(w, p) + "\n" + review.key_block("pgp", 13_900, f"mid-{s}", sheltered=True)
                         + "\n" + _after(w, p) + "\n"),
}


def _text(situation, word, phase, filler=FILLER):
    head = support.tagged("lines", filler).decode("ascii")
    tail = support.tagged("lines", 3_000).decode("ascii")
    return head + SITUATIONS[situation](word, phase, f"{situation}-{phase}") + tail


def _write(project, form, rel, text):
    path = project / rel
    if form == "sqlite-value":
        support.long_value_store(path, text)
    else:
        support.write(path, text)


# --------------------------------------------------------------------------
# Premises: the fragments are the only thing a rule could match; the control's tokens are findings
# --------------------------------------------------------------------------

@pytest.mark.parametrize("situation", sorted(SITUATIONS))
def test_premise_around_the_markers_only_a_fragment_could_be_matched_and_none_is(situation, tmp_path):
    """Each situation, with a short text before it (one gitleaks read), every phase and each rule's fragment: no
    finding by either rule set; and the situation without fragments holds a BEGIN or END marker."""
    texts, controls = {}, {}
    for rule in lr.PROJECT_RULES:
        prefix, token = support.project_k2_strings()[rule]
        for phase in range(Q):
            texts[f"{rule}-{phase:02d}"] = _text(situation, prefix + token, phase, filler=2_000)
        for phase in (0, 7):
            controls[f"{rule}-{phase:02d}"] = _text(situation, token, phase, filler=2_000)
    assert all(f"{DASHES}BEGIN " in t or f"{DASHES}END " in t for t in texts.values()), "premise: a marker in the text"
    for name, config in support.rule_sets().items():
        found = {key: rules for key, rules in lr.gitleaks_finds_each(texts, config, tmp_path).items() if rules}
        assert not found, f"premise: {situation}: a text holding fragments only is a finding by the rule set {name}: " \
                          f"{found}"
        for key, rules in lr.gitleaks_finds_each(controls, config, tmp_path).items():
            assert key.rsplit("-", 1)[0] in rules, (
                f"premise: {situation}: the control's real token ({key}) is no finding by the rule set {name}")


# --------------------------------------------------------------------------
# The cases
# --------------------------------------------------------------------------

@pytest.mark.parametrize("situation", sorted(SITUATIONS))
def test_a_word_internal_fragment_around_a_key_blocks_markers_is_no_finding_at_any_offset(sandbox, project, slots,
                                                                                         situation):
    rels, tokens = [], []
    for form, ext in FORMS.items():
        for rule in lr.PROJECT_RULES:
            prefix, token = support.project_k2_strings()[rule]
            tokens.append(token)
            for phase in range(Q):
                rel = f"{R}/fragments/{form}-{rule}-phase-{phase:02d}{ext}"
                _write(project, form, rel, _text(situation, prefix + token, phase))
                rels.append(rel)
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert not any(token in run.stdout + run.stderr for token in tokens), "the check printed a token-shaped string"
    named = run.named(rels)
    assert not named, (
        f"{situation}: the check flagged {len(named)} of {len(rels)} files whose only token-shaped strings stand "
        f"inside words around a key block's markers: {named[:12]}\n{run.describe(800)}")
    assert run.returncode == 0, f"{situation}: the check is not green and names no file\n{run.describe()}"


@pytest.mark.parametrize("situation", sorted(SITUATIONS))
def test_control_a_real_token_at_the_same_places_is_a_finding(sandbox, project, situation):
    rels, tokens = [], []
    for form, ext in FORMS.items():
        for rule in lr.PROJECT_RULES:
            _prefix, token = support.project_k2_strings()[rule]
            tokens.append(token)
            for phase in (0, 7):
                rel = f"{R}/control/{form}-{rule}-phase-{phase:02d}{ext}"
                _write(project, form, rel, _text(situation, token, phase))
                rels.append(rel)
    run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert not any(token in run.stdout + run.stderr for token in tokens), "the check printed a token"
    missed = [rel for rel in rels if not run.names(rel)]
    assert not missed, (f"{situation}: a real token at a word boundary around a key block's markers was not found: "
                        f"{missed}\n{run.describe(800)}")
    assert run.returncode == support.FINDING_EXIT
