import re
p = "src/gov/retrieval/retrieve.py"
s = open(p).read()

s = s.replace('''def _same_store(payload: dict, commit) -> None:
    """W2-138 S3: refuses a token that names no store commit (made before W2-138) or another commit than ``commit``,
    the store's now, naming both."""
''', '''def _same_store(payload: dict, commit, folder=None) -> None:
    """W2-138 S3: refuses a token that names no store commit (made before W2-138) or another commit than ``commit``,
    the store's now, naming both. With ``folder`` (W2-116 R2-F3), the store's resolved root: a token made on another
    folder is refused even at the same commit (two halves of the integration store at one head), naming both folders,
    and a token with no mark of its folder (made before R2-F3) is refused."""
''')
s = s.replace('''                       {"token_commit": payload["s"], "store_commit": commit}) from None


def _encode''', '''                       {"token_commit": payload["s"], "store_commit": commit}) from None
    if folder is None:
        return
    if "f" not in payload:
        raise GovError("CONTINUATION_INVALID", "the continuation was made before it carried the store's folder and "
                       "names none: ask the first page again", {"store_root": str(folder)}) from None
    if payload["f"] != str(folder):
        raise GovError("CONTINUATION_INVALID",
                       f"the continuation was made on another store, the folder {payload['f']}, and this search "
                       f"answers from the folder {folder}: ask the first page again",
                       {"token_root": payload["f"], "store_root": str(folder)}) from None


def _encode''')
s = s.replace('''                         pooled=None, commit=None):''', '''                         pooled=None, commit=None, folder=None):''')
s = s.replace('''cuts its page from it without a rerank request and without writing anything (DEC-782). ``s`` (W2-138 S3) is the
    store's commit."""''', '''cuts its page from it without a rerank request and without writing anything (DEC-782). ``s`` (W2-138 S3) is the
    store's commit and ``f`` (W2-116 R2-F3) the store's folder as resolved once (``resolved``)."""''')
s = s.replace('''"c": sorted([list(item) for item in alone]), "s": commit,''', '''"c": sorted([list(item) for item in alone]), "s": commit, "f": folder,''')
s = s.replace('''                         carried=None, commit=_UNCHECKED):''', '''                         carried=None, commit=_UNCHECKED, folder=None):''')
s = s.replace('''made on another store commit is refused (W2-138 S3)."""''', '''made on another store commit is refused (W2-138 S3); with ``folder``, one made on another folder too (W2-116 R2-F3)."""''')
s = s.replace('''        _same_store(payload, commit)
    expected''', '''        _same_store(payload, commit, folder)
    expected''')
s = s.replace('''earlier, alone, carried, commit=store["commit"])''', '''earlier, alone, carried, commit=store["commit"], folder=store["root"])''')
s = s.replace('''sent_alone, pool_token, commit=store["commit"])''', '''sent_alone, pool_token, commit=store["commit"],
                                     folder=store["root"])''')
open(p, "w").write(s)
