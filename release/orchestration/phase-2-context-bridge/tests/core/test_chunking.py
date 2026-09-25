from govbridge.core import chunking


def test_empty_text_gives_no_chunks():
    assert chunking.chunk_text("") == []


def test_chunks_are_line_aligned_and_cover_the_whole_text():
    text = "".join(f"line {i}\n" for i in range(200))  # ~1400 chars
    chunks = chunking.chunk_text(text, max_chars=300, overlap_chars=50)
    assert len(chunks) > 1
    # every chunk starts and ends exactly on a line boundary
    lines = text.splitlines(keepends=True)
    for ch in chunks:
        assert ch.text == "".join(lines[ch.start_line - 1: ch.end_line])
    # the union of chunks covers every line at least once (overlap means some lines repeat)
    covered = set()
    for ch in chunks:
        covered.update(range(ch.start_line, ch.end_line + 1))
    assert covered == set(range(1, 201))


def test_consecutive_chunks_overlap():
    text = "".join(f"{'x' * 40}\n" for _ in range(30))
    chunks = chunking.chunk_text(text, max_chars=200, overlap_chars=80)
    assert len(chunks) >= 2
    for a, b in zip(chunks, chunks[1:]):
        assert b.start_line <= a.end_line  # some line range overlap
        assert b.start_line > a.start_line  # but forward progress


def test_a_single_line_longer_than_max_chars_is_still_emitted_whole():
    text = "a" * 5000 + "\n" + "short\n"
    chunks = chunking.chunk_text(text, max_chars=1200, overlap_chars=120)
    assert chunks[0].start_line == 1 and chunks[0].end_line == 1
    assert len(chunks[0].text) == 5001


def test_chunk_id_is_deterministic_and_sensitive_to_every_component():
    a = chunking.chunk_id("blob1", 1, 10)
    b = chunking.chunk_id("blob1", 1, 10)
    assert a == b
    assert a != chunking.chunk_id("blob2", 1, 10)
    assert a != chunking.chunk_id("blob1", 2, 10)
    assert a != chunking.chunk_id("blob1", 1, 11)
    assert a != chunking.chunk_id("blob1", 1, 10, chunker_version="other/2")


def test_text_sha256_matches_hashlib():
    import hashlib
    assert chunking.text_sha256("hello") == hashlib.sha256(b"hello").hexdigest()
