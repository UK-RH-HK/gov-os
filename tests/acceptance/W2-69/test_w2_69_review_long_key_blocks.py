"""W2-69, added after implementation from the review (DEC-136), behaviour 1: a long private-key block is found
wherever it lies.

KPI 1, success: "A real token is found at every offset and in every form the
derived stores hold it: ... and across every boundary where the check splits or
reads its input, at a word boundary as the rule defines it [DEC-897 item 1,
W2-M404]." Failure: "A real token at a word boundary that the check misses, at
any offset or in any stored form."

A private-key block of the size real keys have, up to 8,192 bytes (an RSA-8192
PEM key is about 6.4 KB; an armoured PGP secret key of RSA-3072 or RSA-4096 with
a subkey about 5 to 7 KB), is a finding wherever it lies in a long text:

- shapes: PEM (``RSA PRIVATE KEY``), PKCS#8 (``PRIVATE KEY``), OpenSSH, an
  armoured PGP private key block; each built at run time in the form gitleaks'
  own ``private-key`` rule matches, and checked first by the real gitleaks (whole
  it is a finding; cut anywhere inside, neither part is);
- sizes: 4,000, 4,600, 6,600 and 8,192 bytes, on both sides of 4,096;
- placements: in paragraph text (the block at every paragraph start over a
  stretch around each place where the check splits or gitleaks reads), and in
  text without blank lines at offsets across each such place (the place at 1 to
  1,000 bytes from the block's start and from its end, and at 11 points between);
- forms: a plain file under ``.gov-runtime/`` (256 KiB) and a single SQLite text
  value (256 KiB);
- rule sets: the kernel's (the key found by gitleaks' defaults, which the
  kernel's file extends), and a project whose own rules hold the key rule while
  the block is sheltered under ``extend`` (found by the project's rules alone,
  DEC-347).

The places are learned as the first batch learns them (README, "Where the check
reads"): a learning run on the clean text alone, the stand-in gitleaks keeping
each input. Today the check gives gitleaks pieces of about 16 KB that overlap by
about 4.1 KB, so a block longer than the overlap is missed wherever a piece's
start or end falls inside it and no piece holds it whole. The code before this
ticket gave gitleaks the whole text and found those placements.

Not required (residual, README): a block spread over several separate stored
values (a document's text cut into chunks of 1,200 characters) is not found from
those values.
"""

from __future__ import annotations

import pytest

import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
TEXT = 256 * 1024
CAP = 3                      # places per case: spread over the text, half where gitleaks reads, half the check's
PARAGRAPH = 433              # the paragraph text's period: six lines of 72 bytes and a blank line
LAYOUTS = {"paragraphs": "blank", "no-blank-lines": "lines"}
FORMS = {"plain-file": ".txt", "sqlite-value": ".db"}
NEAR = (1, 2, 3, 8, 24, 64, 160, 400, 1000)


def _writer(form):
    if form == "plain-file":
        return lambda path, data: support.write(path, bytes(data))
    return lambda path, data: support.long_value_store(path, bytes(data).decode("ascii"))


def _offsets(layout, place, size, starts):
    """Where the block begins for one place: in paragraph text, every paragraph start from a paragraph before the
    block's full length to a paragraph after the place; elsewhere, the place at ``NEAR`` bytes from the block's
    start and from its end (a split that misses a block by a few bytes of overlap misses it there), and at 11 points
    spread over it between."""
    if layout == "paragraphs":
        return [p for p in starts if place - size - PARAGRAPH <= p <= place + PARAGRAPH]
    near = {place - d for d in NEAR} | {place - size + d for d in NEAR}
    spread = {place - size + round(j * size / 12) for j in range(1, 12)}
    return sorted(near | spread)


def _place(layout, content, at, block):
    if layout == "paragraphs":     # the block is a paragraph of its own: a blank line after it
        return support.place(content, at, block, before=b"\n", after=b"\n\n")
    return support.place(content, at, block, before=b"\n", after=b"\n")


def _sweep(sandbox, project, stand_in, slots, form, layout, blocks):
    """One learning run, then every block at every offset across the learned places, one file or store each, judged
    by one run of the check with the real gitleaks. Returns the misses as {(size, place): [offsets from it]}."""
    ext, writer = FORMS[form], _writer(form)
    content = support.tagged(LAYOUTS[layout], TEXT)
    clean = f"{R}/keys/clean{ext}"
    edges = support.learn(sandbox, project, stand_in, clean, lambda path: writer(path, content), content)
    margin = max(blocks) + 2 * PARAGRAPH + 16
    places = edges.chosen(margin, len(content) - margin, CAP)
    assert places, f"the learning run showed no place where the check splits or gitleaks reads inside {form}"
    starts = review.paragraph_starts(content)
    cases = []
    for size, block in blocks.items():
        data_block = block.encode()
        for place in places:
            for at in _offsets(layout, place, size, starts):
                data = _place(layout, content, at, data_block)
                if data is not None:
                    cases.append((size, place, at, data))
    rels = []
    for number, (_size, _place_, _at, data) in enumerate(cases):
        rel = f"{R}/keys/case-{number:05d}{ext}"
        writer(project / rel, data)
        rels.append(rel)
    with support.slot(slots):
        run = support.run_check(sandbox, project)
    assert run.returncode is not None, f"the check did not end within its declared limit\n{run.describe()}"
    printed = run.stdout + run.stderr
    assert not any(block.splitlines()[2] in printed for block in blocks.values()), "the check printed a key block"
    assert not run.names(clean), f"the clean text of {form} was named as holding a secret\n{run.describe()}"
    missed = {}
    for rel, (size, place, at, _data) in zip(rels, cases):
        if not run.names(rel):
            missed.setdefault((size, place), []).append(at - place)
    kinds = {place: ("a read of gitleaks" if place in edges.reads else "a split of the check") for place in places}
    return run, cases, missed, kinds


def _report(what, run, cases, missed, kinds):
    return (f"{what}: the check missed {sum(map(len, missed.values()))} of {len(cases)} private-key blocks:\n"
            + "\n".join(f"  a block of {size} bytes across content offset {place} ({kinds[place]}): block start at "
                        f"{sorted(offs)} bytes from it" for (size, place), offs in sorted(missed.items()))
            + f"\n{run.describe(600)}")


# --------------------------------------------------------------------------
# Premises: each block is a finding whole, and no part of it is a finding once it is cut
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", review.SHAPES)
def test_premise_each_key_block_is_a_finding_whole_and_none_once_cut(shape):
    sets = support.rule_sets()
    for size in review.KEY_SIZES:
        block = review.key_block(shape, size, f"premise-{shape}-{size}")
        assert "private-key" in support.gitleaks_finds(f"\n{block}\n", sets["extended"]), (
            f"premise: the {shape} block of {size} bytes is no private-key finding by the kernel's rules")
        # The project's rules alone find nothing in a block's base64 (no _ or - follows a key prefix there): the parts
        # are judged by the kernel's rules. The tails together (none holds a block's beginning), each head alone (a
        # head's beginning would join the next head's header line).
        heads = [head for head, _tail in review.cut_parts(block)]
        tails = "\n\n".join(tail for _head, tail in review.cut_parts(block))
        for part in [tails, *heads]:
            assert support.gitleaks_finds(f"\n{part}\n", sets["extended"]) == [], (
                f"premise: a part of the {shape} block of {size} bytes cut inside it is a finding")
    extended, alone = review.config_with_a_private_key_rule()
    sheltered = review.key_block(shape, 4600, f"premise-sheltered-{shape}", sheltered=True)
    assert support.gitleaks_finds(f"\n{sheltered}\n", extended) == [], (
        f"premise: the sheltered {shape} block is a finding under extend")
    assert review.PRIVATE_KEY_RULE in support.gitleaks_finds(f"\n{sheltered}\n", alone), (
        f"premise: the sheltered {shape} block is no finding by the project's rules alone")


# --------------------------------------------------------------------------
# The sweeps
# --------------------------------------------------------------------------

CASES = [(form, layout, shape) for form in FORMS for layout in LAYOUTS for shape in review.SHAPES]


@pytest.mark.parametrize("form,layout,shape", CASES, ids=[f"{f}-{lay}-{s}" for f, lay, s in CASES])
def test_a_long_private_key_block_is_found_wherever_the_check_splits_or_reads_inside_it(sandbox, project, stand_in,
                                                                                        slots, form, layout, shape):
    blocks = {size: review.key_block(shape, size, f"{form}-{layout}-{shape}-{size}") for size in review.KEY_SIZES}
    run, cases, missed, kinds = _sweep(sandbox, project, stand_in, slots, form, layout, blocks)
    assert not missed, _report(f"{form}, {layout}, {shape}", run, cases, missed, kinds)
    assert run.returncode == support.FINDING_EXIT, f"every block was named but the exit code is {run.returncode}"


@pytest.mark.parametrize("form", sorted(FORMS))
def test_a_long_key_block_only_the_projects_own_rules_find_is_found_wherever_the_check_splits_inside_it(
        sandbox, stand_in, slots, form):
    """The second rule set (DEC-347): the block holds the run of the alphabet that gitleaks' global allowlist
    shelters under ``extend``, and the project's own rules hold the key rule, so only the scan with the project's
    rules alone finds it."""
    extended, _alone = review.config_with_a_private_key_rule()
    project = support.make_check_project(sandbox, name="project-own-key-rule", gitleaks_toml=extended)
    blocks = {size: review.key_block("pem-rsa", size, f"own-{form}-{size}", sheltered=True) for size in (4600, 8192)}
    run, cases, missed, kinds = _sweep(sandbox, project, stand_in, slots, form, "no-blank-lines", blocks)
    assert not missed, _report(f"{form}, the project's rules alone", run, cases, missed, kinds)
    assert run.returncode == support.FINDING_EXIT, f"every block was named but the exit code is {run.returncode}"
