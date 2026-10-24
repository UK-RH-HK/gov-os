"""W2-69, the last round (DEC-909, DEC-136), behaviour 1: a key block of 9 to 24 KB is found wherever it lies in a
long document, in every stored form.

KPI (DEC-909 items 2, 3 and 6), success: "Each BEGIN...END key block (PEM or
armoured PGP) goes to gitleaks whole, as its own piece, up to 24 KB; a block of
9 to 24 KB is found at every boundary position, in a long document and in every
stored form ..." And KPI 1, success: "A real token is found at every offset and
in every form the derived stores hold it ..."; failure: "A real token at a word
boundary that the check misses, at any offset or in any stored form."

- **Blocks:** the whole block, from the first byte of its BEGIN line to the last
  byte of its END line, built at run time as the second batch builds them, in the
  form gitleaks' own ``private-key`` rule matches, and checked first by the real
  gitleaks (whole it is a finding; cut inside, no part is): PEM (``RSA PRIVATE
  KEY``), PKCS#8 (``PRIVATE KEY``), OpenSSH, and an armoured PGP private key
  block (a blank line after its armour header, a checksum line).
- **Sizes:** 9,300, 10,650, 13,900, 18,000, 24,000 and 24,576 bytes (24 KiB, the
  stricter reading of "24 KB", the top).
- **Long documents:** 200 KiB of text, in two layouts: paragraph text (six lines
  of 72 bytes and a blank line) and text without blank lines (lines of 72 bytes).
- **Placements:** the places where the check splits its input and where gitleaks
  begins a read are learned as the first two batches learn them (a learning run on
  the clean text, the stand-in gitleaks keeping each input): one place near the
  start of the text and two well past the first 60 KB (a piece's end from 110,000
  bytes on, a piece's start from 140,000). The block lies across each so that the
  place falls at its very start, on its BEGIN line, at eight points inside its
  body, on its END line and at its very end (21 offsets; 5 near the start); and at
  52 regular steps of 307 bytes from 70,000 (past gitleaks' first read of the
  check's input), one size a step in turn; and at the text's very start and end.
- **Forms:** a plain file under ``.gov-runtime/``, a staged copy where the code
  index stages files (``.gov-runtime/codeintel/files/``), a single SQLite text
  value (full sweeps); and every other form of the first batch's K1 forms that
  holds a long text whole in one value (fewer placements, DEC-221); and a block
  whole in one value among many short values.
- **Rule sets (DEC-347, the second batch's R9):** the main sweeps' blocks are
  found by the kernel's rules (gitleaks' defaults, which the kernel's file
  extends); a project whose own rules hold the key rule is given sheltered blocks,
  which only the scan with the project's rules alone finds.

Today the check gives gitleaks pieces of at most 24,000 bytes that overlap by
about 9.2 KB, each piece read on its own past gitleaks' first read of the input
(about the first 55 KB of a text): a block longer than the overlap is missed
where no piece holds it whole. The code before this ticket missed 0 to 1 of the
second review's 53 placements.

Not required, not tested (residuals, README): a block over 24 KB (row W2-L419);
a block spread over several separate stored values (the second batch's residual).
"""

from __future__ import annotations

import pytest

import w2_69_last_round_support as lr
import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME


def _rel(form, name):
    if form == "staged-copy":
        return f"{R}/codeintel/files/docs/{name}.md"
    return f"{R}/keys/{name}{lr.FORMS[form][0]}"


def _writer(form):
    return lr.FORMS["plain-file" if form == "staged-copy" else form][1]


def _blocks(shapes, sizes, seed, sheltered=False):
    return {(shape, size): lr.block(shape, size, f"{seed}-{shape}-{size}", sheltered=sheltered)
            for shape in shapes for size in sizes}


def _sweep(sandbox, project, stand_in, slots, form, layout, blocks, **how):
    """One learning run on the clean text, then every placement of every block, one file or store each, judged by
    one run of the check with the real gitleaks. Returns the run, the placements and the misses."""
    writer = _writer(form)
    content = support.tagged(lr.LAYOUTS[layout], lr.TEXT)
    clean = _rel(form, "clean")
    cuts = lr.learn_check(sandbox, project, stand_in, clean, lambda path: writer(path, bytes(content).decode("ascii")),
                          content)
    cases = lr.placements(layout, content, blocks, cuts, **how)
    rels = []
    for number, case in enumerate(cases):
        rel = _rel(form, f"case-{number:05d}")
        writer(project / rel, case.data(layout, content, blocks).decode("ascii"))
        rels.append(rel)
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert not lr.printed_a_block(run.stdout + run.stderr, blocks), "the check printed a key block"
    assert not run.names(clean), f"the clean text of {form} was named as holding a secret\n{run.describe()}"
    return run, cases, lr.misses(run.names, rels, cases), cuts


def _assert_all_found(what, run, cases, missed, cuts):
    assert not missed, lr.report(what, missed, len(cases), cuts) + f"\n{run.describe(600)}"
    assert run.returncode == support.FINDING_EXIT, f"{what}: every block was named but the exit code is " \
                                                   f"{run.returncode}"


# --------------------------------------------------------------------------
# Premises: each block is a finding whole, and no part of it once it is cut
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", lr.SHAPES)
def test_premise_each_block_of_9_to_24_kb_is_a_finding_whole_and_none_once_cut(shape):
    sets = support.rule_sets()
    for size in lr.SIZES:
        text = lr.block(shape, size, f"premise-{shape}-{size}")
        assert len(text) == size
        assert text.startswith("-----BEGIN ") and text.rstrip().endswith("-----"), "premise: the block's own ends"
        assert "private-key" in support.gitleaks_finds(f"\n{text}\n", sets["extended"]), (
            f"premise: the {shape} block of {size} bytes is no private-key finding by the kernel's rules")
        heads = [head for head, _tail in review.cut_parts(text)]
        tails = "\n\n".join(tail for _head, tail in review.cut_parts(text))
        for part in [tails, *heads]:
            assert support.gitleaks_finds(f"\n{part}\n", sets["extended"]) == [], (
                f"premise: a part of the {shape} block of {size} bytes cut inside it is a finding")
    extended, alone = review.config_with_a_private_key_rule()
    for size in (lr.SIZES[0], lr.SIZES[-1]):
        sheltered = lr.block(shape, size, f"premise-sheltered-{shape}-{size}", sheltered=True)
        assert support.gitleaks_finds(f"\n{sheltered}\n", extended) == [], (
            f"premise: the sheltered {shape} block of {size} bytes is a finding under extend")
        assert review.PRIVATE_KEY_RULE in support.gitleaks_finds(f"\n{sheltered}\n", alone), (
            f"premise: the sheltered {shape} block of {size} bytes is no finding by the project's rules alone")


# --------------------------------------------------------------------------
# Full sweeps: a plain file, a staged copy, a single SQLite text value
# --------------------------------------------------------------------------

MAIN = ([(form, layout, shape) for form in ("plain-file", "sqlite-value") for layout in lr.LAYOUTS
         for shape in lr.SHAPES]
        + [("staged-copy", "paragraphs", shape) for shape in lr.SHAPES])


@pytest.mark.parametrize("form,layout,shape", MAIN, ids=[f"{f}-{lay}-{s}" for f, lay, s in MAIN])
def test_a_key_block_of_9_to_24_kb_is_found_wherever_it_lies_in_a_long_document(sandbox, project, stand_in, slots,
                                                                                form, layout, shape):
    """Every size at the boundary offsets of the learned places (21 at each of two places well past the first read,
    5 at one near the start) and at the text's two ends; 52 regular steps past the first read, one size a step in
    turn, from a shape's own first size. A staged copy: ten boundary offsets at the two places well past the first
    read (DEC-221: it is a plain file the check reads as any other)."""
    blocks = _blocks([shape], lr.SIZES, f"main-{form}-{layout}")
    how = {"near_too": False, "offsets": lr.few_offsets} if form == "staged-copy" else {}
    run, cases, missed, cuts = _sweep(sandbox, project, stand_in, slots, form, layout, blocks, regular="rotating",
                                      shift=lr.SHAPES.index(shape), **how)
    _assert_all_found(f"{form}, {layout}, {shape}", run, cases, missed, cuts)


# --------------------------------------------------------------------------
# The other forms that hold a long text whole in one value (fewer placements)
# --------------------------------------------------------------------------

OTHER = [form for form in lr.FORMS if form not in ("plain-file", "sqlite-value")]


@pytest.mark.parametrize("form", OTHER)
def test_a_key_block_of_9_to_24_kb_is_found_in_every_other_form_that_holds_a_long_text_whole(sandbox, project,
                                                                                            stand_in, slots, form):
    """Paragraph text (where the second review found the miss); each size in one shape, the shapes in turn; a piece's
    end well past the first read at ten boundary offsets; 26 regular steps of 601 bytes, one block a step in turn."""
    shift = OTHER.index(form)
    blocks = {(lr.SHAPES[(shift + n) % 4], size): lr.block(lr.SHAPES[(shift + n) % 4], size, f"other-{form}-{size}")
              for n, size in enumerate(lr.SIZES)}
    run, cases, missed, cuts = _sweep(sandbox, project, stand_in, slots, form, "paragraphs", blocks,
                                      regular="rotating", edges=False, near_too=False, offsets=lr.few_offsets,
                                      far_cap=1, count=26, step=601, shift=shift)
    _assert_all_found(form, run, cases, missed, cuts)


def _values_store(path, lines, at, text):
    """The text's lines as values, one each, but the block: one value of its own, in place of the lines from ``at``
    for its length."""
    values, offset, put = [], 0, False
    for line in lines:
        if offset >= at and not put:
            values.append(text)
            put = True
        if not (put and offset < at + len(text)):
            values.append(line)
        offset += len(line)
    support.values_store(path, values)


def test_a_key_block_whole_in_one_value_among_many_short_values_is_found(sandbox, project, slots):
    """A store of the text's lines, one short value each (some 3,600), one of them a whole block: at 26 regular steps
    of 601 bytes from 70,000 and one near the start, each size in one shape, the shapes in turn."""
    lines = support.tagged("blank", lr.TEXT).decode("ascii").splitlines(keepends=True)
    cases, rels, blocks = [], [], {}
    for n, size in enumerate(lr.SIZES):
        shape = lr.SHAPES[n % 4]
        text = lr.block(shape, size, f"values-{size}")
        blocks[(shape, size)] = text
        for at in [6_000] + [lr.REGULAR_START + k * 601 for k in range(26)]:
            rel = f"{R}/values/case-{len(rels):05d}.db"
            _values_store(project / rel, lines, at, text)
            assert support.held_by_a_value(project / rel, text[:200]), "premise: one value holds the block"
            cases.append(lr.Placement(shape, size, None, at))
            rels.append(rel)
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    assert not lr.printed_a_block(run.stdout + run.stderr, blocks), "the check printed a key block"
    missed = lr.misses(run.names, rels, cases)
    assert not missed, lr.report("one value among many", missed, len(cases), None) + f"\n{run.describe(600)}"
    assert run.returncode == support.FINDING_EXIT


# --------------------------------------------------------------------------
# The second rule set: blocks only the project's own rules find (DEC-347)
# --------------------------------------------------------------------------

OWN = [("plain-file", "paragraphs"), ("sqlite-value", "no-blank-lines")]


@pytest.mark.parametrize("form,layout", OWN, ids=[f"{f}-{lay}" for f, lay in OWN])
def test_a_key_block_only_the_projects_own_rules_find_is_found_wherever_it_lies(sandbox, stand_in, slots, form,
                                                                                layout):
    """A project whose own rules hold the expression of gitleaks' ``private-key`` rule; PEM blocks holding the run of
    the alphabet that gitleaks' global allowlist shelters under ``extend``, so that only the scan with the project's
    rules alone finds them."""
    extended, _alone = review.config_with_a_private_key_rule()
    project = support.make_check_project(sandbox, name="project-own-key-rule", gitleaks_toml=extended)
    blocks = _blocks(["pem-rsa"], lr.SIZES, f"own-{form}-{layout}", sheltered=True)
    run, cases, missed, cuts = _sweep(sandbox, project, stand_in, slots, form, layout, blocks, regular="rotating",
                                      near_too=False)
    _assert_all_found(f"{form}, {layout}, the project's rules alone", run, cases, missed, cuts)
