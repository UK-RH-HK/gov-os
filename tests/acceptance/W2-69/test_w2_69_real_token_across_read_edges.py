"""W2-69 (K1): a real token is found across every place where the check or gitleaks begins or ends a read.

Success: "A real token is found at every offset ... and across every boundary
where the check splits or reads its input, at a word boundary as the rule defines
it [DEC-897 item 1, W2-M404]."

Failure: "A real token at a word boundary that the check misses, at any offset
or in any stored form."

How a case is made (README, "Where the check reads"):

1. A learning run: the clean content alone (128 KiB of cells that each name their
   own offset), in its form, and the stand-in gitleaks first on PATH keeping a copy
   of each input. The cells locate every stretch of the content in every input:
   where an input (or a stretch of one) begins and ends is where the check splits;
   where gitleaks begins a read inside an input follows from its measured reads
   (65,536 bytes from a pipe or 100,000 from a file, then 3,672, each with a peek
   to a blank line or 25,000 bytes more). Up to six of these places are chosen.
2. For each place, one case per offset across it: the token at every offset from
   its full length plus 3 bytes before the place to 3 bytes after it, with a
   space (a newline for the key block) before and after it. Each case is one file
   or store; one run of the check with the real gitleaks judges them all, and each
   must be named.

Tokens: a github-pat shape (40 word characters; any cut of it is no token), the
project's digit token at its shortest with five dashes inside (19 characters; a
cut at a dash falls at a byte that is not a word character), and a private-key
block over five lines (about 260 bytes, cut at every 7th offset across the place
and at each of its spaces and newlines).

Today's check gives gitleaks a plain file as one input, so a token across
gitleaks' read at 90,536 (or 119,208) of that input is missed: the plain layouts
without a blank line (``oneline``, ``lines``, ``longword``) and the UTF-16 file
are red today. The SQLite forms are not red today: today's check gives gitleaks
each value three times (the raw bytes, the rows as text, the bytes without zeros),
so a token cut in one copy is whole in another. The ``blank`` layout is not red
today either: gitleaks ends its reads at a blank line there.
"""

from __future__ import annotations

import pytest

import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
VALUE = 72          # the many-values form: one line of eight cells per value
UNCERTAIN = 3       # bytes beyond the token's length on each side of a place
CAP = 6             # places per case


def _plain(path, content):
    support.write(path, bytes(content))


def _utf16(path, content):
    support.write(path, bytes(content).decode("ascii").encode("utf-16-le"))


def _long_value(path, content):
    support.long_value_store(path, bytes(content).decode("ascii"))


def _many_values(path, content):
    data = bytes(content).decode("ascii")
    support.values_store(path, [data[i:i + VALUE] for i in range(0, len(data), VALUE)])


def _utf16_value(path, content):
    support.long_value_store(path, bytes(content).decode("ascii"), encoding="UTF-16le")


def _blob(path, content):
    support.blob_store(path, bytes(content))


# form: (layout of the content, writer, file extension)
FORMS = {
    "plain-oneline": ("oneline", _plain, ".txt"),
    "plain-lines": ("lines", _plain, ".txt"),
    "plain-blank-lines": ("blank", _plain, ".txt"),
    "plain-longword": ("longword", _plain, ".txt"),
    "plain-utf16le": ("lines", _utf16, ".txt"),
    "sqlite-long-value": ("lines", _long_value, ".db"),
    "sqlite-many-values": ("lines", _many_values, ".db"),
    "sqlite-utf16-store-value": ("lines", _utf16_value, ".db"),
    "sqlite-blob": ("lines", _blob, ".db"),
}

TOKENS = {
    "github-pat": (support.ghp_token, b" ", b" "),
    "dashed-token": (support.dashed_token, b" ", b" "),
    "private-key-block": (support.pem_key, b"\n", b"\n"),
}

CASES = [(form, kind) for form in FORMS for kind in ("github-pat", "dashed-token")]
CASES += [("plain-lines", "private-key-block"), ("sqlite-long-value", "private-key-block")]


def _offsets(kind, edge, token):
    if kind != "private-key-block":
        return range(edge - len(token) - UNCERTAIN, edge + UNCERTAIN + 1)
    inside = [i for i, ch in enumerate(token) if ch in " \n"]
    near = {edge - i + d for i in inside for d in (-1, 0, 1)}
    return sorted(near | set(range(edge - len(token) + 1, edge, 7)))


def _fits(form, at, token, before, after):
    if form != "sqlite-many-values":
        return True
    start, end = at - len(before), at + len(token) + len(after) - 1
    return start // VALUE == end // VALUE


@pytest.mark.parametrize("form,kind", CASES, ids=[f"{f}-{k}" for f, k in CASES])
def test_a_real_token_is_found_across_every_place_a_read_begins_or_ends(sandbox, project, stand_in, slots, form, kind):
    layout, writer, ext = FORMS[form]
    make, before, after = TOKENS[kind]
    content = support.tagged(layout, support.SWEEP_SIZE)
    clean = f"{R}/sweep/clean{ext}"
    edges = support.learn(sandbox, project, stand_in, clean, lambda path: writer(path, content), content)
    token = make(f"{form}-{kind}").encode()
    places = edges.chosen(len(token) + UNCERTAIN + 2, len(content) - len(token) - UNCERTAIN - 2, CAP)
    assert places, f"the learning run showed no place where a read begins or ends inside {form}"
    cases = []
    for edge in places:
        for at in _offsets(kind, edge, token.decode()):
            data = support.place(content, at, token, before, after)
            if data is not None and _fits(form, at, token, before, after):
                cases.append((edge, at, data))
    rels = []
    for number, (_edge, _at, data) in enumerate(cases):
        rel = f"{R}/sweep/case-{number:05d}{ext}"
        writer(project / rel, data)
        rels.append(rel)
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert token.decode() not in run.stdout + run.stderr, "the check printed the token"
    assert not run.names(clean), f"the clean content of {form} was named as holding a secret\n{run.describe()}"
    missed = {}
    for rel, (edge, at, _data) in zip(rels, cases):
        if not run.names(rel):
            missed.setdefault(edge, []).append(at - edge)
    kinds = {edge: ("a read of gitleaks" if edge in edges.reads else "a split of the check") for edge in places}
    assert not missed, (
        f"{form}, {kind}: the check missed {sum(map(len, missed.values()))} of {len(cases)} real tokens at a word "
        f"boundary across the places where a read begins or ends:\n" + "\n".join(
            f"  content offset {edge} ({kinds[edge]}): token start at {sorted(offs)} bytes from it"
            for edge, offs in sorted(missed.items())) + f"\n{run.describe(600)}")
    assert run.returncode == support.FINDING_EXIT, f"every case was named but the exit code is {run.returncode}"
