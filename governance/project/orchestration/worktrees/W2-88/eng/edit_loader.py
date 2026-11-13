p = "src/gov/store/loader.py"
s = open(p).read()
s = s.replace('''    (root / STORE_REL).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / STORE_REL, isolation_level=None)
    try:
        connection.execute("BEGIN")''', '''    (root / STORE_REL).parent.mkdir(parents=True, exist_ok=True)
    current = _current_or_new(root / STORE_REL)  # judged before this load rewrites the record tables (RV1-6)
    connection = sqlite3.connect(root / STORE_REL, isolation_level=None)
    try:
        connection.execute("BEGIN")''')
s = s.replace('''        layout.stamp(connection, commit=False)  # W2-88: the layout this load wrote, with the load's own transaction
''', '''        if current:  # a load rebuilds the record tables only: it never makes a stale store (the other stores') current
            layout.stamp(connection, commit=False)  # W2-88: the layout this load wrote, with the load's own transaction
''')
s = s.replace('''def _load(root: Path, kind: str, records_fingerprint: bool = True)''', '''def _current_or_new(path: Path) -> bool:
    """Whether the store at ``path`` is new (no file) or current by ``layout.found_of``: the only stores a load stamps."""
    if not path.is_file():
        return True
    try:
        peek = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            return layout.found_of(peek) is None
        finally:
            peek.close()
    except sqlite3.Error:
        return False


def _load(root: Path, kind: str, records_fingerprint: bool = True)''', 1)
open(p, "w").write(s)

p = "tests/unit/adopt/test_w2_88_layout.py"
s = open(p).read()
s += '''

def test_a_load_does_not_make_a_stale_store_current(tmp_path):
    for found in ("unstamped", 1):
        root = repo_with_record(tmp_path / str(found))
        load(root)
        db = sqlite3.connect(root / STORE_REL)
        db.executescript("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL, path TEXT NOT NULL, "
                         "start_line INTEGER, end_line INTEGER);")  # no parent_id: the lexical store is an older form
        if found == 1:
            db.execute("UPDATE store_layout SET version = 1")
        else:
            db.execute("DROP TABLE store_layout")
        db.commit()
        db.close()
        with pytest.raises(GovError) as before:
            connect(root)
        load(root)
        with pytest.raises(GovError) as after:
            connect(root)
        assert after.value.code == "STORE_LAYOUT_STALE" and after.value.details == before.value.details
        assert after.value.details["found"] == (0 if found == "unstamped" else 1)


def test_a_load_into_a_new_or_current_store_stamps_it(tmp_path):
    root = repo_with_record(tmp_path)
    load(root)
    load(root)  # a current store stays current
    connect(root).close()
'''
open(p, "w").write(s)
