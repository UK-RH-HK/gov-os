p = "src/gov/adopt/refactor_plan.py"
s = open(p).read()

s = s.replace('''a repository with nothing to refactor gets ``NOTHING-TO-REFACTOR.md`` instead. It runs no ``tk``, applies nothing and''',
'''a repository with nothing to refactor gets ``NOTHING-TO-REFACTOR.md`` instead, unless the secrets scan did not run or
skipped files: then ``PLAN.md`` states ``secrets: not scanned (<reason>)`` and the unscanned paths, and no file says
there is nothing to refactor (B-1.5). It runs no ``tk``, applies nothing and''')

s = s.replace('''def plan(assessment: dict, path_map: dict | None, out: Path) -> dict:
    """The proposals for ``assessment`` under ``<out>/refactor-plan/``; ``{count, proposals, nothing, assessment_sha256}``."""''',
'''def unscanned(assessment: dict) -> dict | None:
    """``{reason, unscanned, all}`` where the secrets scan did not run or skipped files, else None. ``unscanned`` holds the
    skipped paths; where the scanner did not run, ``all`` is the count of tracked files and none is named singly."""
    skipped = [item for item in assessment.get("secrets_unscanned") or [] if isinstance(item, str)]
    if assessment.get("secrets_scanned") is False:
        return {"reason": assessment.get("secrets_unscanned_reason") or "the secrets scan did not run", "unscanned": skipped,
                "all": len(_tracked(assessment))}
    if skipped:
        return {"reason": assessment.get("secrets_unscanned_reason") or "blobs over the scan limit were not scanned",
                "unscanned": skipped, "all": None}
    return None


def plan(assessment: dict, path_map: dict | None, out: Path) -> dict:
    """The proposals for ``assessment`` under ``<out>/refactor-plan/``; ``{count, proposals, nothing, secrets_unscanned,
    assessment_sha256}`` (``nothing`` is False wherever the secrets scan did not cover the repository)."""''')

old = s[s.index("    if proposals:\n        lines ="):s.index("    return {\"count\": len(proposals)")]
new = '''    blind = unscanned(assessment)
    if blind:  # never "no secret" for a scan that did not run (B-1.5): PLAN.md says so, with the proposals found
        where = (f"all {blind['all']} tracked files" if blind["all"] is not None
                 else "\\n".join(f"- `{path}`" for path in blind["unscanned"]))
        lines = [f"- `{item['file'].rsplit('/', 1)[-1]}`: {item['kind']}: {item['title']}" for item in proposals]
        (folder / "PLAN.md").write_text(
            "# Refactoring plan\\n\\nSources: memory-assessment sha256:" + digest + "\\n\\n"
            f"secrets: not scanned ({blind['reason']})\\n\\nUnscanned paths: {where}\\n\\n"
            + ("\\n".join(lines) + "\\n" if lines else "No other blocker was found.\\n"), encoding="utf-8")
    elif proposals:
        lines = [f"- `{item['file'].rsplit('/', 1)[-1]}`: {item['kind']}: {item['title']}" for item in proposals]
        (folder / "PLAN.md").write_text("# Refactoring plan\\n\\nSources: memory-assessment sha256:" + digest + "\\n\\n"
                                        + "\\n".join(lines) + "\\n", encoding="utf-8")
    else:
        (folder / "NOTHING-TO-REFACTOR.md").write_text(
            f"# Nothing to refactor\\n\\nThe assessment (memory-assessment sha256:{digest}) found no blocker to full "
            "indexing: no vendored or generated code without a folder, no namespace policy to state, no file over "
            "the chunker's limit, no secret in a tracked file and no path in no namespace or in two.\\n",
            encoding="utf-8")
'''
s = s.replace(old, new)
s = s.replace('''    return {"count": len(proposals), "proposals": proposals, "nothing": not proposals, "assessment_sha256": digest}''',
'''    return {"count": len(proposals), "proposals": proposals, "nothing": not proposals and not blind,
            "secrets_unscanned": blind, "assessment_sha256": digest}''')
open(p, "w").write(s)

p = "src/gov/adopt/stages.py"
s = open(p).read()
s = s.replace('''    made = refactor_plan.plan(assessment, path_map if isinstance(path_map, dict) else None, out)
    return {"stage": "MA",''', '''    made = refactor_plan.plan(assessment, path_map if isinstance(path_map, dict) else None, out)
    blind = made["secrets_unscanned"]
    if blind:  # the files are written (the assessment, the proposals found, PLAN.md); the result is not ok (B-1.5)
        listed = blind["unscanned"] or sorted(assessment.get("paths") or [])
        raise GovError("SECRETS_UNSCANNED", f"the secrets scan did not cover the repository ({blind['reason']}): "
                       "the plan cannot say there is no secret in a tracked file; the assessment and the proposals found "
                       f"are written under {out}", {"reason": blind["reason"], "unscanned": listed[:SCAN_LIST_LIMIT],
                                                    "unscanned_count": blind["all"] or len(blind["unscanned"])})
    return {"stage": "MA",''')
s = s.replace('''POLICIES = (EMBEDDED, "not embedded")  # the two values of a namespace's embedding_policy (DEC-388, DEC-694)
''', '''POLICIES = (EMBEDDED, "not embedded")  # the two values of a namespace's embedding_policy (DEC-388, DEC-694)
SCAN_LIST_LIMIT = 1000  # paths named in SECRETS_UNSCANNED's details (the full list is the assessment's ``paths``)
''', 1)
open(p, "w").write(s)
