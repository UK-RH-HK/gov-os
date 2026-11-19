"""The writer's and the checker's brief templates (W2-204 I5, S9), filled by ``gov.memaudit.brief`` from a repository's
own configuration. They follow the sections of Gov OS's approved briefs (``governance/project/indep-briefs/memory-audit/``):
the job, the folder, what to read, what never to read, the rules, round 2, the output, the result, the stops. A template
names no repository's category, domain or subsystem: every such name is a ``{{field}}`` the configuration fills. The
text is kept in Python modules so that an installed release carries it without a package-data entry."""

from gov.memaudit.briefs import checker, writer

TEMPLATES = {"writer": writer.TEXT, "checker": checker.TEXT}
