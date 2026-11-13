p = "src/gov/adopt/fabric.py"
s = open(p).read()
s = s.replace('''    except Exception as exc:  # noqa: BLE001 - a route that raised was not measured: the record names the error
        return None, None, type(exc).__name__
    took = round((time.perf_counter() - start) * 1000, 1)
    if isinstance''', '''    except Exception as exc:  # noqa: BLE001 - a route that raised ran no scan: the record names the error
        return round((time.perf_counter() - start) * 1000, 1), None, type(exc).__name__
    took = round((time.perf_counter() - start) * 1000, 1)
    if isinstance''')
s = s.replace('''    said = over(found_scale)
    if said:
        proposal(out, said, found_scale)''', '''    said = over(found_scale)
    if said:
        proposal(out, said, found_scale)
    else:  # this run's record decides: a proposal an earlier run left in the folder is not this run's
        (out / "SCALE-PROPOSAL.md").unlink(missing_ok=True)''')
# the files the keyword index holds that are not in the classified set (the adoption's own records)
s = s.replace('''    vec_i = [rel for rel in lexical_i if rel in vectored]
    vec_r =''', '''    for rel in sorted(set(verdicts) - set(paths)):  # held by the store, outside the path map (the adoption's records)
        state = verdicts[rel]
        if state == 1:
            lexical_i.append(rel)
        else:
            lexical_r.append({"path": rel, "reason": "not-embedded" if state == 2 else "secrets"})
    vec_i = [rel for rel in lexical_i if rel in vectored]
    vec_r =''')
s = s.replace('''        "lexical": {**base, "judged": len(paths), "indexed"''', '''        "lexical": {**base, "judged": len(lexical_i) + len(lexical_r), "indexed"''')
open(p, "w").write(s)
