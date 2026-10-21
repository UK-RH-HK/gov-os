#!/bin/bash
# DEC-623: the data the context check misses, each piece in its own commit.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
c() {
  git commit -q -m "$1" --trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-44.b" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 1
  git log --oneline -1
}
git add docs/contract/master-rules
c "Master rule records: one per id of the contract file, generated (DEC-623)"
git add docs/interfaces/API-0002.md
c "A record for the interface API-0002, so that the id resolves (DEC-623)"
git add .tickets/DAEO-dtv3.md .tickets/DAEO-emkd.md
c "Two ticket source lines cut to the id; the clause stays in the text (DEC-623)"
git add docs/imported governance/project/external-references.yaml
c "Outside sources imported with origin and sha256; research-catalogue ids listed as external references (DEC-560, DEC-564, DEC-623)"
git add .tickets/DAEO-o4fg.md .tickets/DAEO-jdqr.md
c "EXP-001 leaves the sources list of two tickets, which cite the decision that accepted it (DEC-623)"
git status --short
