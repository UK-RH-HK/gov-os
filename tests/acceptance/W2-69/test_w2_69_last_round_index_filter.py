"""W2-69, the last round (DEC-909, DEC-136), behaviour 2: the pre-index filter finds the same tokens and key blocks
as the check and keeps a file that holds one out of the index.

KPI (DEC-909 item 3, P-3), success: "The pre-index filter, which shares the
check's gitleaks call, finds the same tokens and key blocks at every boundary and
keeps a file that holds one out of the index." And DEC-285: the filter is
``gov.secrets.indexable(root, paths)``; it returns the sub-list of ``paths`` an
indexer may read and never lets a path through undecided.

The filter is called through its public function, in a child process of its own
with this worktree's code (DEC-732), on a temporary project whose ``docs/**`` is
a governed source folder (governance memory in its path map):

- **Short tokens** (the first batch's K1 tokens, and one of each of the project's
  rules): a github-pat shape (gitleaks' defaults), the project's digit token at
  its shortest with five dashes inside, its upper- and lower-case tokens at their
  shortest, its canary; at a word boundary, at every offset of the read-edge
  sweep (from the token's full length plus 3 bytes before a place to 3 bytes after
  it), across up to four places the filter's learning run shows (where it ends or
  begins a piece of its input, where gitleaks begins a read), in 128 KiB texts of
  three layouts: lines, paragraphs, one line.
- **Key blocks of 9 to 24 KB** (behaviour 1's blocks and placements) in a 200 KiB
  document; and blocks only the project's own rules find (DEC-347).
- **End to end:** ``gov rebuild --json`` in a temporary project whose sources hold
  such files (the code-graph tool hidden from ``PATH``, as the first batch's K3
  does, so no daemon starts): the files are in neither the code index's staged
  files nor the lexical index, no store holds a block's text, and the check is
  green on the stores.
- **Controls:** the clean text of the same shape is returned (every learning run)
  and indexed (end to end); and the chance red is not brought into the filter: a
  file whose only token-shaped strings are the first batch's word-internal
  fragments (the project's four rules) is returned, at every offset (four
  layouts) and with each string beginning exactly where the filter's learning run
  shows a piece or a read begins, and indexed end to end.

Today the filter misses the long blocks the check misses (the second review: "the
pre-index filter shares the miss") and lets the file into the index.
"""

from __future__ import annotations

import importlib.util
import shutil

import pytest

import w2_69_last_round_support as lr
import w2_69_review_support as review
import w2_69_support as support

pytestmark = [support.needs_gitleaks, support.local_only]

R = support.RUNTIME
UNCERTAIN = 3       # bytes beyond the token's length on each side of a place (the first batch's read-edge sweep)
TOKEN_CAP = 3       # places per token sweep

needs_vectors = pytest.mark.skipif(importlib.util.find_spec("sqlite_vec") is None,
                                   reason="sqlite_vec is not installed: the semantic index cannot be built")


def _tokens():
    """{name: (rule, maker, cuts)}: ``cuts`` are where a cut leaves no part of the token a finding (every cut, but for
    the canary, whose head alone is a canary again once a cut leaves a character before ``_CANARY_``)."""
    upper = lambda seed: "pk" + "_" + "A" + "b" + support.chars(f"up-{seed}", 14)          # noqa: E731
    lower = lambda seed: "tok" + "_" + "a" + "B" + support.chars(f"low-{seed}", 14)        # noqa: E731
    return {
        "github-pat": ("github-pat", support.ghp_token, None),
        "gov-token-digit": ("gov-token-digit", support.dashed_token, None),
        "gov-token-upper": ("gov-token-upper", upper, None),
        "gov-token-lower": ("gov-token-lower", lower, None),
        "gov-canary": ("gov-canary", support.canary, range(2, 11)),
    }


TOKENS = _tokens()


@pytest.fixture()
def embedder():
    stand_in = support.EmbedderStandIn()
    yield stand_in
    stand_in.close()


# --------------------------------------------------------------------------
# Premises
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(TOKENS))
def test_premise_each_short_token_is_a_finding_alone_and_no_part_of_it_once_cut(name):
    rule, make, cuts = TOKENS[name]
    token = make(f"premise-{name}")
    sets = support.rule_sets()
    for set_name, config in sets.items():
        if rule == "github-pat" and set_name == "alone":
            assert support.gitleaks_finds(f" {token} \n", config) == [], "premise: github-pat is no project rule"
            continue
        assert rule in support.gitleaks_finds(f" {token} \n", config), f"premise: the {name} token alone ({set_name})"
    positions = cuts or range(1, len(token))
    parts = "".join(f" {token[:i]} \n {token[i:]} \n" for i in positions)
    assert support.gitleaks_finds(parts, sets["extended"]) == [], f"premise: a part of the {name} token once cut"


def test_premise_the_project_a_filter_is_given_is_one_whose_docs_are_a_governed_source_folder(sandbox):
    project = lr.filter_project(sandbox)
    support.write(project / "docs/a.md", support.prose(2000, "a"))
    support.write(project / "elsewhere/b.md", support.prose(2000, "b"))
    run = lr.run_filter(sandbox, project, ["docs/a.md", "elsewhere/b.md"])
    assert run.returncode == 0 and run.returned == ["docs/a.md"], (
        f"premise: the filter returns a clean file of docs/ and leaves out one of no namespace\n{run.describe()}")


# --------------------------------------------------------------------------
# Short tokens at every offset of the read-edge sweep
# --------------------------------------------------------------------------

TOKEN_LAYOUTS = ("lines", "blank", "oneline")
TOKEN_CASES = [(layout, name) for layout in TOKEN_LAYOUTS for name in sorted(TOKENS)]


@pytest.mark.parametrize("layout,name", TOKEN_CASES, ids=[f"{lay}-{n}" for lay, n in TOKEN_CASES])
def test_the_filter_keeps_out_a_file_with_a_short_token_across_every_place_it_cuts_or_gitleaks_reads(
        sandbox, stand_in, slots, layout, name):
    project = lr.filter_project(sandbox)
    content = support.tagged(layout, support.SWEEP_SIZE)
    clean = "docs/sweep/clean.md"
    cuts = lr.learn_filter(sandbox, project, stand_in, clean, content)
    _rule, make, _cuts = TOKENS[name]
    token = make(f"filter-{layout}-{name}").encode()
    low, high = len(token) + UNCERTAIN + 2, len(content) - len(token) - UNCERTAIN - 2
    places = lr.spread([p for p in cuts.ends + cuts.starts + cuts.reads if low <= p <= high], TOKEN_CAP)
    assert places, f"the filter's learning run showed no place where it cuts or gitleaks reads inside {layout}"
    cases, rels = [], []
    for place in places:
        for at in range(place - len(token) - UNCERTAIN, place + UNCERTAIN + 1):
            data = support.place(content, at, token)
            if data is not None:
                rel = f"docs/sweep/case-{len(rels):05d}.md"
                support.write(project / rel, bytes(data))
                cases.append((place, at))
                rels.append(rel)
    with support.slot(slots):
        run = lr.run_filter(sandbox, project, [clean] + rels)
    assert run.returncode == 0, f"the filter did not decide\n{run.describe()}"
    assert clean in run.returned, f"control: the clean text was left out\n{run.describe()}"
    let_through = {}
    for rel, (place, at) in zip(rels, cases):
        if rel in run.returned:
            let_through.setdefault(place, []).append(at - place)
    assert not let_through, (
        f"{layout}, {name}: the filter let {sum(map(len, let_through.values()))} of {len(rels)} files with a real "
        f"token at a word boundary through to the index:\n" + "\n".join(
            f"  content offset {place} ({cuts.kind(place)}): token start at {sorted(offs)} bytes from it"
            for place, offs in sorted(let_through.items())) + f"\n{run.describe(600)}")


# --------------------------------------------------------------------------
# Key blocks of 9 to 24 KB wherever they lie in a long document
# --------------------------------------------------------------------------

def _filter_sweep(sandbox, project, stand_in, slots, layout, blocks, **how):
    content = support.tagged(lr.LAYOUTS[layout], lr.TEXT)
    clean = "docs/keys/clean.md"
    cuts = lr.learn_filter(sandbox, project, stand_in, clean, content)
    cases = lr.placements(layout, content, blocks, cuts, **how)
    rels = []
    for number, case in enumerate(cases):
        rel = f"docs/keys/case-{number:05d}.md"
        support.write(project / rel, case.data(layout, content, blocks))
        rels.append(rel)
    with support.slot(slots):
        run = lr.run_filter(sandbox, project, [clean] + rels)
    assert run.returncode == 0, f"the filter did not decide\n{run.describe()}"
    assert clean in run.returned, f"control: the clean text was left out\n{run.describe()}"
    returned = set(run.returned)
    return run, cases, lr.misses(lambda rel: rel not in returned, rels, cases), cuts


FILTER_BLOCKS = [(layout, shape) for layout in lr.LAYOUTS for shape in lr.SHAPES]


@pytest.mark.parametrize("layout,shape", FILTER_BLOCKS, ids=[f"{lay}-{s}" for lay, s in FILTER_BLOCKS])
def test_the_filter_keeps_out_a_file_holding_a_key_block_of_9_to_24_kb_wherever_it_lies(sandbox, stand_in, slots,
                                                                                        layout, shape):
    """Every size at the boundary offsets of the learned places (21 at a piece's end well past the first read, 5 at a
    place near the start) and at the text's two ends; 52 regular steps past the first read, one size a step in turn.
    One place fewer than the check's sweeps (DEC-221): the filter shares the check's gitleaks call."""
    project = lr.filter_project(sandbox)
    blocks = {(shape, size): lr.block(shape, size, f"filter-{layout}-{shape}-{size}") for size in lr.SIZES}
    run, cases, missed, cuts = _filter_sweep(sandbox, project, stand_in, slots, layout, blocks, regular="rotating",
                                             shift=lr.SHAPES.index(shape), far_cap=1)
    assert not missed, (lr.report(f"the filter, {layout}, {shape}", missed, len(cases), cuts, judge="the filter")
                        + " (each such file was returned: let into the index)\n" + run.describe(600))


def test_the_filter_keeps_out_a_file_holding_a_key_block_only_the_projects_own_rules_find(sandbox, stand_in, slots):
    """DEC-347: the project's own rules hold the key rule; the blocks are sheltered under ``extend``."""
    extended, _alone = review.config_with_a_private_key_rule()
    project = lr.filter_project(sandbox, gitleaks_toml=extended)
    blocks = {("pem-rsa", size): lr.block("pem-rsa", size, f"filter-own-{size}", sheltered=True)
              for size in lr.SIZES}
    run, cases, missed, cuts = _filter_sweep(sandbox, project, stand_in, slots, "paragraphs", blocks,
                                             regular="rotating", near_too=False, far_cap=1)
    assert not missed, (lr.report("the filter, the project's rules alone", missed, len(cases), cuts,
                                  judge="the filter") + "\n" + run.describe(600))


# --------------------------------------------------------------------------
# Controls: the chance red is not brought into the filter
# --------------------------------------------------------------------------

@pytest.mark.parametrize("layout", ("oneline", "lines", "blank", "longword"))
def test_control_a_file_whose_only_token_shaped_strings_are_inside_words_is_returned_at_every_offset(sandbox, slots,
                                                                                                   layout):
    """The first batch's K2 cells: each of the project's four rules' word-internal strings in cells of 24 bytes, in
    24 files shifted by 0 to 23 bytes, so that every byte offset is where such a string begins inside a word in one
    of them. Every file is returned."""
    project = lr.filter_project(sandbox)
    rels, tokens = [], []
    for rule in lr.PROJECT_RULES:
        prefix, token = support.project_k2_strings()[rule]
        tokens.append(token)
        for phase in range(24):
            rel = f"docs/inside/{rule}-phase-{phase:02d}.md"
            support.write(project / rel, lr.cells(layout, prefix + token, phase, support.SWEEP_SIZE))
            rels.append(rel)
    with support.slot(slots):
        run = lr.run_filter(sandbox, project, rels)
    assert run.returncode == 0, f"the filter did not decide\n{run.describe()}"
    assert not any(token in run.stderr for token in tokens), "the filter printed a token-shaped string"
    left_out = [rel for rel in rels if rel not in run.returned]
    assert not left_out, (f"{layout}: the filter left out {len(left_out)} of {len(rels)} files whose only "
                          f"token-shaped strings stand inside words: {left_out[:12]}\n{run.describe()}")


def test_control_a_word_internal_string_at_the_filters_learned_read_edges_is_returned(sandbox, stand_in, slots):
    """Each of the project's four rules' word-internal strings placed so that its token-shaped part begins exactly
    where the filter's learning run shows a piece or a read begins (inside its word), at every such place of a
    200 KiB text, in paragraph text and in text without blank lines. Every file is returned."""
    project = lr.filter_project(sandbox)
    rels, tokens = [], []
    for layout, form in lr.LAYOUTS.items():
        content = support.tagged(form, lr.TEXT)
        cuts = lr.learn_filter(sandbox, project, stand_in, f"docs/edges/clean-{layout}.md", content)
        starts = [p for p in cuts.starts + cuts.reads if 400 <= p <= len(content) - 900]
        assert starts, f"the filter's learning run showed no place where a read begins ({layout})"
        for rule in lr.PROJECT_RULES:
            prefix, token = support.project_k2_strings()[rule]
            tokens.append(token)
            data = bytearray(content)
            for place in starts:
                data = support.place(data, place - len(prefix), (prefix + token).encode()) or data
            rel = f"docs/edges/{layout}-{rule}.md"
            support.write(project / rel, bytes(data))
            rels.append(rel)
    with support.slot(slots):
        run = lr.run_filter(sandbox, project, rels)
    assert run.returncode == 0, f"the filter did not decide\n{run.describe()}"
    assert not any(token in run.stderr for token in tokens), "the filter printed a token-shaped string"
    left_out = [rel for rel in rels if rel not in run.returned]
    assert not left_out, (f"the filter left out {len(left_out)} of {len(rels)} files whose only token-shaped strings "
                          f"stand inside words at its read edges: {left_out}\n{run.describe()}")


# --------------------------------------------------------------------------
# End to end: gov rebuild --json
# --------------------------------------------------------------------------

E2E_BLOCKS = (("pem-rsa", 13_900), ("pgp", 13_900), ("pkcs8", 18_000), ("openssh", 24_000), ("pem-rsa", 24_576),
              ("pgp", 10_650))


@needs_vectors
def test_a_rebuild_keeps_a_source_file_holding_a_key_block_out_of_every_index(sandbox, stand_in, embedder, slots):
    """``gov rebuild --json`` (full, the semantic index against the stand-in embedder; the code-graph tool hidden
    from PATH) in a project whose ``docs/`` holds six 200 KiB documents of paragraph text, each with a key block of
    10,650 to 24,576 bytes beginning 1,000 bytes before a place well past the first read where the filter's learning
    run shows a piece begins; a clean document of the same shape; and four documents whose only token-shaped strings
    are the project's rules' word-internal strings, each beginning where the filter's reads begin. Then the check."""
    content = support.tagged("blank", lr.TEXT)
    probe = lr.filter_project(sandbox, name="probe-project")
    cuts = lr.learn_filter(sandbox, probe, stand_in, "docs/clean.md", content)
    shutil.rmtree(probe, ignore_errors=True)
    _near, far = cuts.chosen(len(content), max(lr.SIZES) + 8)
    assert far, "the filter's learning run showed no place past the first read"
    files, held, blocks = {"docs/clean.md": bytes(content).decode("ascii")}, [], {}
    for n, (shape, size) in enumerate(E2E_BLOCKS):
        text = lr.block(shape, size, f"e2e-{n}")
        blocks[(shape, size)] = text
        data = lr.place_block("paragraphs", content, far[-1] - 1_000, text.encode())
        assert data is not None
        files[f"docs/keys/held-{n}.md"] = data.decode("ascii")
        held.append(f"docs/keys/held-{n}.md")
    starts = [p for p in cuts.starts + cuts.reads if 400 <= p <= len(content) - 900]
    inside = []
    for rule in lr.PROJECT_RULES:
        prefix, token = support.project_k2_strings()[rule]
        data = bytearray(content)
        for place in starts:
            data = support.place(data, place - len(prefix), (prefix + token).encode()) or data
        files[f"docs/inside/{rule}.md"] = bytes(data).decode("ascii")
        inside.append(f"docs/inside/{rule}.md")
    project = support.make_rebuild_project(sandbox, files)
    env = support.rebuild_environment(sandbox, embedder, with_code_tool=False)
    daemon = support.code_daemon_dir(project)
    try:
        with support.slot(slots):
            run = support.rebuild(project, env)
    finally:
        if daemon is not None and daemon.is_dir():
            shutil.rmtree(daemon, ignore_errors=True)
    assert support.store_status(run, "lexical") == "recreated", f"premise: the lexical index\n{run.describe()}"
    staged = project / R / "codeintel" / "files"
    assert (staged / "docs/clean.md").is_file(), (
        f"premise: the code index staged the files the filter returned (the tool hidden)\n{run.describe()}")
    judged, chunked = lr.lexical_files(project)
    assert judged.get("docs/clean.md") == 1 and "docs/clean.md" in chunked, (
        f"control: the clean document of the same shape was not indexed: {judged.get('docs/clean.md')}")
    not_indexed = [rel for rel in inside if not (staged / rel).is_file() or judged.get(rel) != 1 or rel not in chunked]
    assert not not_indexed, (f"control: documents whose only token-shaped strings stand inside words were left out "
                             f"of the index: {not_indexed}")
    let_in = {rel: [where for where, yes in (("the code index's staged files", (staged / rel).is_file()),
                                            ("the lexical index", judged.get(rel) == 1 or rel in chunked)) if yes]
              for rel in held}
    let_in = {rel: where for rel, where in let_in.items() if where}
    lines = sorted({line.encode() for text in blocks.values() for line in lr.block_lines(text)})
    holding = support.files_holding(project / R, lines)
    assert not let_in and not holding, (
        f"after gov rebuild --json, documents holding a key block were let into the index: {let_in}; files under "
        f"{R}/ holding a block's text: {holding}")
    check = support.run_check(sandbox, project, env=support.base_environment(sandbox))
    assert check.returncode == 0 and not check.stdout.strip(), (
        f"after the rebuild the check is not green on the stores\n{check.describe(800)}")
