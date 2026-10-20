---
type: probe
task: DAEO-kl5e
reviewer_session: ce198f2e-5a42-44a7-b79c-61b139c56004
implementer_session: af0e9a13-c0d8-45d5-8341-b70bf9cc2dd2
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 19a4e9fd20b9562c24b1824076c67403fb323db5
---

# Probe record: W2-50, the extra independent review (DEC-752 item 2) (DRAFT, not committed — fail; packages to the owner)

- **What was probed.** The whole change at `19a4e9fd` on `w2/W2-50` (implementation `91200c82` by session
  `bbbda207-31b9-4f4d-a58c-2fce09af7b39`, repair `86aa805c` by `0f2f9377-40c4-497c-a2ef-37d5f87d8587`, repair
  `df5f1e50` by `af0e9a13-c0d8-45d5-8341-b70bf9cc2dd2`, CIT-E §8 `d5abd786`, lead checkpoint `19a4e9fd`), with its
  focus on the DEC-751 repair. A fresh read-only reviewer (role `independent-auditor`, session
  `ce198f2e-5a42-44a7-b79c-61b139c56004`, 2026-10-17), launched in the owner's form with the reading tools only; code
  under test this worktree's `src/` (DEC-732). Eight probe scripts with a temporary HOME and a sibling TMPDIR, through
  the kernel's PreToolUse hook, `gov launch` with the stand-in CLI and the secrets check; W2-50 233 passed, W1-15 124
  passed; `git status --short` empty before and after; real `~/gov-os-runs` ABSENT.
- **What it found.**
  1. **High; fails open, loses work, changes acceptance tests.** A copy into a folder (`cp X <own>/d/`, `cp X <own>/d`,
     `install X <own>/d/`, `cp -r <own>/s/. <own>/d/`) is judged as the folder, not as the file it writes, so the file
     lands through a symbolic or hard link entry already in the own folder: it changed the project's acceptance test,
     overwrote another ticket's file, and, through a local `git clone` into the own folder (whose objects are hard
     links to the source's), corrupted the source repository's object store (`git fsck`: object corrupt or missing).
     The same write named file by file is refused (R8, the KPI's link line). Reproduced and run. The guard's parsing
     of the plain `cp`/`install` destination is older than W2-50 (the reviewer's in-repository control through a
     symbolic link was also allowed); the own folder's links and a clone's hard-linked objects are new reach.
  2. **Medium; fails open.** A project made with the file tools inside the own folder, with a `.git` file naming this
     repository's common directory, a forged `in_progress` ticket whose `external-ref` is another ticket's folder, and
     the settings file and the guard hook, passes the marker check: a guard call with that project as its root gives
     Write and `rm -rf` in the other ticket's folder, and `gov launch` from it puts that folder in its write list; a
     real `git worktree add` into the own folder with forged tickets did the same. Precondition: a session or launch
     whose root is that project (an unsandboxed role can start one; a sandboxed one not tested live). Reproduced.
  3. **Low.** The guard's refusal of the marker is bypassed by a folder destination (`mv`, `cp`, `install`,
     `ln -sf` into the folder): the marker can be replaced, handing the folder over to another repository's session.
     Contradicts CIT-E difference 15's text ("every judged Bash form"); the session hands over only its own folder.
     Reproduced. Same mechanism as finding 1.
  4. **Low; fails closed.** A FIFO in the marker's place (`mkfifo` plus the move of finding 3) makes `gov launch`
     hang with no end; the guard refuses writes outside the project at its 20-second deadline. Reproduced.
- **Found sound.** The marker's exact bytes (trailing space, no newline, two newlines, CRLF, relative path, a path
  through a link, trailing slash all refused); a link, a folder or a hard link to another repository's marker in its
  place; every direct write to the marker (Write, Edit, `rm`, `mv`/`cp` onto it, `ln -f`, `ln -sf`, `>`, `>>`,
  `sed -i`, `touch`, `tee`, relative names after `cd`, a glob); the root in every spelling; other and near-named
  folders, `..`, case changes; every session-identity case (no ticket, empty, forged, path in the id, `ticket-lead`,
  unknown or no role, a closed ticket); the earlier refusals first (freeze, `dangerouslyDisableSandbox`, unknown tool,
  acceptance tests, `.tickets/`, settings); the launcher's write list (exactly the temp folder and the marked folder,
  the same for a second worktree; nothing made or added with no `.git`, a ticket not in progress, a root that is a
  link, an own path that is a file or link); the secrets walk (chains and `..` spellings leading out of a clone under
  the root not followed, a `..` link inside it followed, a link into a clone not followed) and W1-15's B4.
- **Judgement: fail.** Findings 1 and 2 let a session write outside its own folder, and finding 1 loses work. By
  DEC-752 item 2 they come back as packages with no new round; findings 3 and 4 are residuals.
