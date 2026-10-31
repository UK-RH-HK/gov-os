<!-- For whoever writes a skill from this template. Delete this comment from a written skill.

The template's own three scenarios (DEC-959 item 5), written before its text. Each is run on a fresh session that
has only this template and the inputs named; it passes when its pass line holds.

1. A new skill from the template.
   - Situation: a fresh session is given this template and a one-page description of a method, and asked to
     write the skill.
   - Expected: it writes the skill's three scenarios first and commits them, then the skill's text in a later
     commit; the front matter has name, version and a third-person description of what it does and when; the
     sections stand in the template's order, with the sources at the end.
   - Pass line: the skill validator finds nothing; every section heading of the template is present, in order; the
     body is under about 150 lines; the scenarios' commit is older than the text's.
2. More method than fits.
   - Situation: the method described needs about 300 lines of detail.
   - Expected: the body keeps the steps and the checks; the detail goes into reference files directly in the
     skill's folder, each linked from the body; no reference file links on to another.
   - Pass line: the body is under about 150 lines; every reference file sits one level below the skill and is
     linked from it; the validator finds nothing.
3. An imported skill.
   - Situation: the session is asked to adopt a skill from another collection whose licence is not stated.
   - Expected: it does not adopt it; it records what it found of the source, version and licence in
     <the project's skill-import record>, and returns a package; with a licence that allows the use, it writes the
     skill's three scenarios and adopts it only once all three pass.
   - Pass line: no skill is marked adopted without a licence record and three passing scenarios.
-->
