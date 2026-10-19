
## W1-41: `gov adopt --lite`, the legacy importer and external references in the context (DEC-518 to DEC-523, DEC-535, DEC-551, DEC-552, DEC-568; 2026-10-09)

Merged from `w1/W1-41` at `868d72b9` (182 cases in the suite; probed at `920229dc`, then one fix round of
three behaviours, DEC-552). Built: `gov adopt --lite --stage <A0..A6|A8> [--map <file>] [--verdict <path>]
--session <id>`, its records under `governance/adoption/`, its refs under
`refs/gov/adoption/{backup,rollback,archive}/` of the adopted project; the legacy importer and the
dependency proof (A8); in the context, `governance/project/external-references.yaml` (this repository's
lists `S0a-G-12` and `S0a-G-13`), the packet key `external`, and `gov.context.external_references(root)`.
Source lines: 1,011 added under `src/` against an estimate of 440. `gov adopt` has not been run on this
repository; its adoption is a later, defined step (DEC-522), and the outside sources of DEC-560 are applied
there.

**To the follow-up after W1-41 (DEC-552):** the external list is read from the working tree, so a ticket
whose paths include the file can unblock its own mandatory source without a commit, and repository-held id
forms other than a decision's (`CAP-…`) are accepted in it; `RETIRED` and `REJECTED` records satisfy a
mandatory source in the context (only `SUPERSEDED` blocks); a mandatory record whose file cannot be read
gets the hash of empty bytes and counts 0 tokens, so the packet presents it as read; any retrieval failure
in the supplementary lookup becomes "index unavailable".

**To be read again before this repository's own adoption:** a move to a target that no namespace holds is
accepted and executed and then blocks A8 with `UNKNOWN_ARTEFACT`; a project whose `.gitignore` does not
name `.gov-runtime/` refuses at A8 on a dirty tree after A6's rebuild; a project without `.gitleaks.toml`
refuses an A3 with a move.

**Residuals from the probe** (session `2020c8c7-b490-4464-8b39-64fc3030412a`; record in
`docs/probes/DAEO-cdoi/`):

- After a failed batch the earlier batches stay committed, no A6 record names what they did (a deleted file
  then has no recorded disposition, against success line 6), and the next round, which the refusal tells the
  owner to run, reuses the rollback ref names. Nothing is lost: history and the first backup ref hold it.
- An interruption at a batch's commit leaves the moves staged with the rollback ref set; at the record's
  commit it leaves the batch committed and the record staged. Every later stage refuses on a dirty tree;
  there is no resume.
- A package in a flat layout (a manifest with the package beside it, or `app/`, `pages/`, `lib/` beside a
  `package.json`) moves without the two grounds of success line 7; only `src/` beside a manifest is native.
- A Cursor rule file with unquoted globs refuses A8 before the import is tried; one such file retired while
  another is kept refuses A8, because the import tool takes both. Both fail closed.
- The dependency proof still misses: a word character or `-` directly before the path or id; backslashes,
  URL-encoding, another letter case, a path split across lines; a citation of only the store's folder or a
  glob; `../` followed by only the tail of the path. A record's prose is searched for the store's paths,
  not its ids. A record that wrongly carries `RETIRED` or `REJECTED` releases the store.
- The CIT-E text and the A8 record still say "active records" where the proof reads every record that still
  stands; the chat-database proof accepts any readable record whatever its status.
- A ticket with no `sources`, a read dependency and external dependencies is built; if the ticket file
  changes between the context's two reads the judgement falls back to every declared id.

**Residuals from the build:**

- Verdict independence rests on the `Role` trailer of the commit that brought the verdict and on the
  `auditor_session` the verdict states; both are self-declared.
- Importers come from the code graph for indexed files only: an unparsed language or a bare import with no
  use reads as "no importers"; plain-text mentions are not flagged; nothing is computed for RETIRE or
  DELETE_FROM_ACTIVE_TREE. A6 does not re-check importers, references and consumers at HEAD.
- What the proposal does not name is KEEP; an executed entry with no batch goes into one last batch.
- A batch is checked by path and blob id; file modes are not compared. A8 checks the staged tree, not the
  commit itself as A6 does.
- `gov rebuild` runs after the record's commit; if it fails the stage answers a refusal though the moves or
  the retirement stand. Only the lexical store is held to `recreated`.
- A8 retires only what the path map names; a legacy rule file the proposal did not name stays loaded. The
  proof reads a fixed list of rule places (not `.github/copilot-instructions.md`, `.clinerules`,
  `GEMINI.md`), decodes with "replace", and sees a citation only by path or id, not by folder or glob.
- A `rulesync import` target is held to "contains the source body"; frontmatter is not compared. A tools
  file without `mcpServers` is kept word for word under `.rulesync/legacy/` and retired as imported. An
  `AGENTS.md` section that is only headings is dropped. Imported `.cursorrules` and `.windsurfrules` get
  `targets: ['*']`. `rulesync` 24.0.0 refuses an `.mdc` whose `globs` is a list; the tool then imports it
  itself and the record says so.
- `governance/adoption/**` is outside the inventory and the unknown check. An existing decision package is
  not removed when its artefact is later classified.
- A rollback deletes every untracked, non-ignored file; an untracked directory would make it raise.
- Reading the record graph writes `.gov-runtime/store.db` into the project.
- The tool uses two private functions (`codeintel._graph`, doctor's `_match_pattern`).
- A3 with a move needs `/tmp/gov-cbm-<uid>` writable, so the move cases cannot run in a launched session.
- `gov adopt` without `--lite` is `NOT_IMPLEMENTED`.
- External references: a dangling symlink at the file's path reads as "no file" (the id stays blocked); the
  brief summary is cut at 2500 tokens and could cut an "external, not read" line; a key the file's shape
  does not name is accepted.
- The W1-26 README's count for its planted-defects file is stale. A killed background script leaves its
  running pytest child alive (seen in the lead's verification).
- **Latency under load (DEC-372):** one W1-05 p95 case (189 ms) failed in the fix round's full run and
  passed alone. **W1-16's runtime-folder case** failed once in run 3's long run and passed alone (DEC-563).
- **KPI disputes:** P-9 to P-14 over the runs. **Acceptance tests rewritten after implementation began:**
  two (the W1-26 planted-defect case, "planned: command implemented"; one legacy case, "stricter reading
  decided after the probe (DEC-552)"). **Added after implementation began:** 68, each red first.
