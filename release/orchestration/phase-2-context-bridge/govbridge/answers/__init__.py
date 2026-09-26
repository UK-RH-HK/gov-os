"""``govbridge cite`` and ``govbridge answers lint`` (REPAIR_DAG.yaml node R1-RA, REPAIR_PLAN.md section 7,
RC-11): answer-side aids that resolve a named identifier to an exact citation, and lint a demonstration agent's
own ``answers.yaml`` (``schemas/answers.yaml``) against the packet(s) it was compiled with.

Every lookup in this package is READ-ONLY against the store and against Git (BR-DAG-AMEND-R1-15): nothing here
opens a read-write store connection, builds an index, or writes a file other than the CLI's own stdout.
"""
