"""KPI 1 (and F1): a machine-wide cache keyed by the model, its revision and the sha256 of the exact text sent; a hit
sends nothing, a miss embeds and stores; one file, mode 0600, in the user's own folder, shared by every tree."""

from __future__ import annotations

import stat

import w2_126_support as S

QUESTION = "when does the baker score the sourdough loaves"


def test_a_second_tree_and_a_clone_send_nothing(box, stand_in, tmp_path):
    first = S.plant(tmp_path / "first")
    box.build(first)
    sent = stand_in.texts()
    assert sent, "the first tree's chunks were not sent to the embedder (the case's set-up)"

    stand_in.reset()
    box.build(S.clone(first, tmp_path / "the-clone"))
    box.build(S.plant(tmp_path / "second"))   # another tree, planted on its own, the same texts
    assert stand_in.texts() == [], "a tree whose texts are all cached sent texts to the embedder"


def test_a_changed_text_is_a_miss(box, stand_in, tmp_path):
    first = S.plant(tmp_path / "first")
    box.build(first)
    before = set(stand_in.texts())

    other = S.clone(first, tmp_path / "other")
    S.write(other, "notes/tides.md", S.CORPUS["notes/tides.md"].replace("harbour pilot", "harbour Pilot"))
    S.commit(other)
    stand_in.reset()
    box.build(other)
    sent = stand_in.texts()
    assert any("harbour Pilot" in text for text in sent), "a text changed by one letter was served from the cache"
    assert not set(sent) & before, "texts already cached were sent again"
    assert S.store_vectors(other) != S.store_vectors(first), "the changed chunk got the old text's vector"


def test_a_question_from_two_trees_is_embedded_once(box, stand_in, tmp_path):
    first = S.plant(tmp_path / "first")
    second = S.clone(first, tmp_path / "second")
    [one] = box.run(first, [S.query(QUESTION)])
    [two] = box.run(second, [S.query(QUESTION)])
    assert one["vector"] and two["vector"], f"no question vector: {one['reason']}, {two['reason']}"
    assert len(stand_in.sent_with(QUESTION)) == 1, "the question was embedded once per tree"
    assert one["vector"] == two["vector"]


def test_the_cache_is_one_file_of_mode_0600(box, tmp_path):
    first = S.plant(tmp_path / "first")
    box.build(first)
    box.run(first, [S.query(QUESTION)])
    entry = S.cache_entry(box)
    assert stat.S_IMODE(entry.stat().st_mode) == 0o600, f"{entry} has mode {oct(entry.stat().st_mode)}"


def users_files(box):
    return set(S.files_under(box.workdir / "home")) | set(S.files_under(box.workdir / "xdg-cache"))


def test_by_default_the_cache_sits_in_the_users_own_folder(box, stand_in, tmp_path):
    """The user's folder already holds what a build writes there besides the cache (the base keeps its secrets
    scan there): what the cache adds is what appears once the location setting is left out."""
    box.build(S.plant(tmp_path / "baseline", corpus={"notes/kiln.md": "# Kiln\n\nFired on Thursdays.\n"}))
    before = users_files(box)
    env = box.env(use_setting=False)
    first = S.plant(tmp_path / "first")
    box.build(first, env)
    stand_in.reset()
    box.build(S.clone(first, tmp_path / "second"), env)
    assert stand_in.texts() == [], "without the location setting, a second tree sent its texts again"
    added = sorted(users_files(box) - before)
    assert len(added) == 1 and stat.S_IMODE(added[0].stat().st_mode) == 0o600, \
        f"the user's own folder must hold the cache, one file of mode 0600: {[str(path) for path in added]}"
