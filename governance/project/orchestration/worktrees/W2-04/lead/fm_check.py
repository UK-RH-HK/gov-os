"""Parses the probe record's front matter the way the close does (gov.close.command.frontmatter)."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-04/src")
from gov.tasks.tickets import frontmatter  # noqa: E402

pf = frontmatter(Path(sys.argv[1]))
print({k: pf.get(k) for k in ("type", "task", "reviewer_session", "implementer_session", "reviewer_wrote_nothing",
                               "commissioned_by", "judged_by", "judgement", "probed_commit")})
