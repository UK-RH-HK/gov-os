"""W2-42a reopened (DEC-1164 (18), DEC-1174 (1)): an apostrophe in a comment of a shell's heredoc body is no quote.

The defect: the product's guard, ``gov.guard.decide.decide``, refuses a Bash call whose heredoc body, read by a
shell, holds a comment with an apostrophe (``bash <<'EOF'`` / ``# it's fine`` / ``ls`` / ``EOF``) with "the command
cannot be read", although the call writes nothing; the same body without the comment is allowed. The fix to come:
comment text in a shell body (a ``#`` that starts a word, outside quotes and not part of ``${…}`` or ``$#``, to the
end of its line) is dropped before the body is read; a body still unreadable after that stays refused.

Every case asks ``decide("Bash", {"command": …}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")`` in a
project of its own (``proj``): an in-progress engineer ticket ``DAEO-03ub`` whose allowed paths are ``src/**``, so a
write under ``src/`` is allowed and any refusal of ``T`` (``tests/acceptance/X/zz.py``, which no engineer may write)
is about ``T``. No session variable is set; ``HOME`` is the case's own.

- (a) ``test_apostrophe_a_*``: a harmless body with an apostrophe comment, under each shell form of W2-42a's F1
  fixture (quoted and unquoted delimiter), is allowed; so is the same call followed by a write under ``src/``.
- (b) ``test_apostrophe_b_*``: the same forms followed, after the heredoc, by a write of ``T`` (``> T``, ``cp``,
  ``python3 -c``) are refused; ACT-GUARD-FIX-5 round 2's four reversal calls by name.
- (c) ``test_apostrophe_c_*``: a body that itself writes ``T`` after such a comment is refused; a write of ``T``
  between two apostrophe comments is refused (read as text, the two apostrophes pair into one quote that hides the
  write: the base allows it, a fail-open); and the comment drop's edges (a ``#`` inside a word, ``${#v}``,
  ``${v#a}``, ``$#``, a ``#`` inside quotes, a comment after the write), each a body line that writes ``T``, are
  refused, with and without an apostrophe comment above them.
- (d) ``test_apostrophe_d_*``: a body with a real unclosed quote outside a comment is refused, also after an
  apostrophe comment (the base pairs the two and allows it, a fail-open) and where a too-wide comment drop would hide
  the quote.
- ``test_apostrophe_control_*``: the same forms without the apostrophe comment (allowed), and the project's own
  allowed path and refused ``T`` (green on the base: they show the fixture judges what the cases say).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w2_42a_support as s  # noqa: E402

T = "tests/acceptance/X/zz.py"
OK = "src/ok.py"
UNREADABLE = "cannot be read"
TICKET = """---
id: DAEO-03ub
status: in_progress
type: task
role: engineer
wbs_id: W2-42a
allowed_paths:
- src/**
---
# A stand-in of the engineer's ticket for the apostrophe cases
"""

# The shell forms of fixtures/f1_shell_options.json named by the brief, and plain bash; ``{d}`` is the delimiter word.
FORMS = [
    ("bash-euo-pipefail", "bash -euo pipefail <<{d}"),
    ("bash-o-pipefail", "bash -o pipefail <<{d}"),
    ("bash-O-extglob", "bash -O extglob <<{d}"),
    ("bash-rcfile-f", "bash --rcfile f <<{d}"),
    ("bash-dev-stdin", "bash /dev/stdin <<{d}"),
    ("cat-pipe-bash-o-pipefail", "cat <<{d} | bash -o pipefail"),
    ("plain-bash", "bash <<{d}"),
]
DELIMITERS = [("quoted", "'EOF'"), ("unquoted", "EOF")]
HEADS = [(f"{f}-{q}", head.format(d=d)) for f, head in FORMS for q, d in DELIMITERS]
# A narrower set for the edges: quoted and unquoted plain bash, a shell with options, and a pipe from cat.
EDGE_HEADS = [h for h in HEADS if h[0] in ("plain-bash-quoted", "plain-bash-unquoted", "bash-euo-pipefail-quoted",
                                           "cat-pipe-bash-o-pipefail-quoted")]

# Harmless bodies: an apostrophe in a comment, and a command that writes nothing.
HARMLESS = [
    ("dont-overwrite", "# don't overwrite\necho hi\n"),
    ("its-fine", "# it's fine\nls\n"),
    ("trailing-comment", "echo hi # don't overwrite\n"),
    ("indented-comment", "  # it's fine\nls\n"),
]
APOSTROPHE = "# don't overwrite\n"
# What a call does after the heredoc to write T (ACT-GUARD-FIX-5 round 2's reversal writes).
AFTER = [
    ("redirect", f"echo x > {T}"),
    ("cp", f"cp x.py {T}"),
    ("python3-c", f"python3 -c \"open('{T}','w').write('x')\""),
]
# A body that writes T itself after an apostrophe comment.
BODY_WRITES = [
    ("redirect", f"{APOSTROPHE}echo x > {T}\n"),
    ("cp", f"{APOSTROPHE}cp x.py {T}\n"),
]
# A write of T between two apostrophe comments: read as text, the two apostrophes pair into one quote that hides the
# write (the base allows these: a fail-open); read by a shell, both are comments and the write is run.
PAIRED = [
    ("redirect-between-two-comments", f"# don't overwrite\necho x > {T}\n# it's done\n"),
    ("cp-between-two-comments", f"# don't overwrite\ncp x.py {T}\n# it's done\n"),
    ("redirect-before-a-trailing-comment", f"# don't overwrite\necho x > {T} # it's done\n"),
]
# The comment drop's edges: a '#' that does not start a comment, each in a body line that writes T.
EDGES = [
    ("hash-inside-a-word", f"echo a#b > {T}"),
    ("length-expansion", f"v=ab; echo ${{#v}} > {T}"),
    ("pattern-removal", f"v=ab; echo ${{v#a}} > {T}"),
    ("argument-count", f"echo $# > {T}"),
    ("hash-in-double-quotes", f'echo "a # b" > {T}'),
    ("hash-in-single-quotes", f"echo 'it # s' > {T}"),
    ("apostrophe-and-hash-in-double-quotes", f'echo "it\'s # here" > {T}'),
    ("comment-after-the-write", f"echo x > {T} # don't overwrite"),
]
EDGE_PREFIXES = [("after-an-apostrophe-comment", APOSTROPHE), ("alone", "")]
# Bodies a shell cannot read: a real unclosed quote outside a comment.
UNCLOSED = [
    ("unclosed-single", "echo 'unclosed\nls\n"),
    ("unclosed-double", 'echo "unclosed\nls\n'),
    ("unclosed-single-after-an-apostrophe-comment", "# it's fine\necho 'unclosed\nls\n"),
    ("unclosed-after-a-hash-inside-a-word", "echo a#b'c\nls\n"),
    ("unclosed-after-the-argument-count", "echo $# 'unclosed\nls\n"),
]
# ACT-GUARD-FIX-5 round 2's four F1 reversal calls (the probe's cases a, b, c, d).
BODY = "# don't overwrite\necho hi\n"
REVERSALS = [
    ("a-bash-euo-pipefail-quoted", f"bash -euo pipefail <<'EOF'\n{BODY}EOF\necho x > {T}"),
    ("b-bash-o-pipefail-unquoted", f"bash -o pipefail <<EOF\n{BODY}EOF\necho x > {T}"),
    ("c-plain-bash-unquoted", f"bash <<EOF\n{BODY}EOF\necho x > {T}"),
    ("d-bash-euo-pipefail-quoted-python3-c", f"bash -euo pipefail <<'EOF'\n{BODY}EOF\n"
                                             f"python3 -c \"open('{T}','w').write('x')\""),
]


def call(head, body, after=""):
    """The Bash command: the head line, the body, the delimiter, and what the call does after the heredoc."""
    return f"{head}\n{body}EOF" + (f"\n{after}" if after else "")


def product(*groups):
    """The cross product of (id, value) lists as pytest params: the ids joined by '/', the values as a tuple."""
    out = [((), ())]
    for group in groups:
        out = [(i + (gi,), v + (gv,)) for i, v in out for gi, gv in group]
    return [pytest.param(*v, id="/".join(i)) for i, v in out]


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """The case's project (real path): an engineer's in-progress ticket DAEO-03ub allowing ``src/**``, the files the
    commands name (``x.py``, the rcfile ``f``, an empty ``tests/acceptance/X/``); no session variable set."""
    for name in s._SESSION:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "home").mkdir()
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    root = tmp_path / "proj"
    (root / "tests" / "acceptance" / "X").mkdir(parents=True)
    (root / "src").mkdir()
    (root / ".tickets").mkdir()
    (root / ".tickets" / "DAEO-03ub.md").write_text(TICKET, encoding="utf-8")
    (root / "x.py").write_text("x = 1\n", encoding="utf-8")
    (root / "f").write_text("", encoding="utf-8")
    return os.path.realpath(str(root))


def decide(command, root):
    """The product guard's decision on the call for an engineer on DAEO-03ub: ``(decision, why)``."""
    from gov.guard.decide import decide as product_decide
    return product_decide("Bash", {"command": command}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")


def assert_allowed(command, root):
    got, why = decide(command, root)
    assert got == "allow", f"want allow, got {got}: {why}\n--- the command ---\n{command}"


def assert_refused_for_t(command, root):
    """Refused, and for T: it writes T (or a target it cannot resolve), or the command cannot be read."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny (it writes {T}), got {got}: {why}\n--- the command ---\n{command}"
    assert T in why or s.UNRESOLVABLE in why or UNREADABLE in why, \
        f"refused for another reason: {why}\n--- the command ---\n{command}"


def assert_refused_unreadable(command, root):
    """Refused because the command cannot be read, or by the unresolvable target's refusal."""
    got, why = decide(command, root)
    assert got == "deny", f"want deny (an unclosed quote), got {got}: {why}\n--- the command ---\n{command}"
    assert UNREADABLE in why or s.UNRESOLVABLE in why, \
        f"refused for another reason: {why}\n--- the command ---\n{command}"


# -- (a) a harmless body with an apostrophe comment is allowed ---------------------------------------------------------

@pytest.mark.parametrize("head,body", product(HEADS, HARMLESS))
def test_apostrophe_a_a_harmless_shell_body_with_an_apostrophe_comment_is_allowed(proj, head, body):
    assert_allowed(call(head, body), proj)


@pytest.mark.parametrize("head", product(HEADS))
def test_apostrophe_a_the_call_then_writing_an_allowed_path_is_allowed(proj, head):
    assert_allowed(call(head, BODY, f"echo x > {OK}"), proj)


# -- (b) the call writing T after such a heredoc is still refused ------------------------------------------------------

@pytest.mark.parametrize("head,after", product(HEADS, AFTER))
def test_apostrophe_b_the_call_writing_the_acceptance_folder_after_the_heredoc_is_refused(proj, head, after):
    assert_refused_for_t(call(head, BODY, after), proj)


@pytest.mark.parametrize("command", product(REVERSALS))
def test_apostrophe_b_the_four_f1_reversal_calls_of_act_guard_fix_5_stay_refused(proj, command):
    assert_refused_for_t(command, proj)


# -- (c) a body writing T after such a comment, and the comment drop's edges, are still refused -------------------------

@pytest.mark.parametrize("head,body", product(HEADS, BODY_WRITES))
def test_apostrophe_c_a_body_writing_the_acceptance_folder_after_an_apostrophe_comment_is_refused(proj, head, body):
    assert_refused_for_t(call(head, body), proj)


@pytest.mark.parametrize("head,body", product(HEADS, PAIRED))
def test_apostrophe_c_two_apostrophe_comments_do_not_pair_into_a_quote_that_hides_a_write(proj, head, body):
    assert_refused_for_t(call(head, body), proj)


@pytest.mark.parametrize("head,prefix,line", product(EDGE_HEADS, EDGE_PREFIXES, EDGES))
def test_apostrophe_c_a_hash_that_starts_no_comment_keeps_the_write_on_its_line(proj, head, prefix, line):
    assert_refused_for_t(call(head, f"{prefix}{line}\n"), proj)


# -- (d) a body with a real unclosed quote is still refused --------------------------------------------------------------

@pytest.mark.parametrize("head,body", product(EDGE_HEADS, UNCLOSED))
def test_apostrophe_d_a_body_with_an_unclosed_quote_outside_a_comment_is_refused(proj, head, body):
    assert_refused_unreadable(call(head, body), proj)


# -- controls (green on the base): the fixture judges what the cases say ----------------------------------------------

@pytest.mark.parametrize("head,body", product(HEADS, [("no-comment", "echo hi\n"),
                                                      ("comment-without-apostrophe", "# do not overwrite\necho hi\n")]))
def test_apostrophe_control_the_same_body_without_an_apostrophe_is_allowed(proj, head, body):
    assert_allowed(call(head, body), proj)


@pytest.mark.parametrize("head", product(HEADS))
def test_apostrophe_control_without_the_apostrophe_an_allowed_write_passes_and_a_write_of_t_is_refused_for_t(proj, head):
    assert_allowed(call(head, "echo hi\n", f"echo x > {OK}"), proj)
    got, why = decide(call(head, "echo hi\n", f"echo x > {T}"), proj)
    assert got == "deny" and T in why, f"want deny naming {T}, got {got}: {why}"
