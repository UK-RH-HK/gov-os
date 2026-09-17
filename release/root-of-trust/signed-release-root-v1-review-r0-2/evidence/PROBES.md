# Probe and reproduction record — AR-0025

All probes were run read-only inside the review worktree
`/…/scratchpad/wt/srr1-r0-review-2` at HEAD `2b36b440915f0052d92153748cea914846955418`,
branch `phase1/srr1-r0-review-2`. No `GOV_*` environment variable was set and no
Governance OS binary was built or executed — none was required: this is an
architecture-document review. Nothing outside this worktree was written, and the
only directory written by this run is
`release/root-of-trust/signed-release-root-v1-review-r0-2/` plus the AR-0025 report.

Probes `NR-1`…`NR-5` are **reruns** of the AR-0023 probe set against the corrected
text. Probes `NA-1`…`NA-16` are **fresh held-out attacks authored by this review**.

---

# Part 1 — Reruns of the AR-0023 probe set

## NR-1 — Mandated hash verification (STOP-condition check)

All seven digests pinned by `HO-0025` were recomputed. Full output in
`REVIEWED-CONTENT-DIGESTS.txt`.

```
70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1  …/01-FROZEN-…-BOUNDARY.md
42681978d3a7603da857029e68bd120453bd9ff373b8dea2c4247343a857cfda  spec/architecture/ARCH-0003.yaml
695aa185ab32a813cd596b12f80d235afb92d56f147f395b15f16e37d0bcd983  …/00-ARCHITECTURE.md
6922fd352219b36acb75395bc03b2a15888d3f801824acf0f878f6a7931a9044  …/04-R0-CORRECTION-1.md
4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3  Governance_OS_Capability_Acceptance_Contract_v3.md
903407729327d67c198c9bf97885a936c5601993e16ad76137a3106c5728d1db  …/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md
3831cbf51d6f663299a3a338d85bd07bed662fd33e5392502d4f270ce87e36fa  …/OWNER-DECISION-0005-R0-REVIEW-ANSWERS.md
```

**Result: all seven match `HO-0025` exactly. No STOP condition.** Contract v3 was read
only from this verified file; no contract text was reconstructed from memory.

## NR-2 — Candidate identity and correction containment

`git diff --stat 73227a1 29516f8` (pre-correction commit → correction commit):

```
 .../signed-release-root-v1/00-ARCHITECTURE.md      |  49 +++-
 .../signed-release-root-v1/04-R0-CORRECTION-1.md   | 277 +++++++++++++++++++++
 spec/architecture/ARCH-0003.yaml                   |  99 +++++++-
 3 files changed, 408 insertions(+), 17 deletions(-)
```

The correction touched exactly the two architecture documents named by CD-R0-1/CD-R0-2
plus its own new correction record. Nothing else.

## NR-3 — Time/clock declaration sweep (rerun of AR-0023 PR-3, basis for `SRR-R0-M1`)

AR-0023 ran a case-insensitive sweep of the candidate for `clock|time|wall|NTP`
excluding the compounds `timestamp|runtime|lifetime|sometimes`, and obtained
**zero matches**. Rerun against the corrected text:

```
$ grep -nEi 'clock|[^a-z]time|wall|NTP' 00-ARCHITECTURE.md ARCH-0003.yaml \
    | grep -vEi 'timestamp|runtime|lifetime|sometimes'
ARCH-0003.yaml:47,49,54,55,56,170,172,173
00-ARCHITECTURE.md:32,41,51,53,140,176
```

**Result: 14 matches, zero before.** The local time source is now named as an
assumption (`ARCH-0003.yaml:47-49`; `00-ARCHITECTURE.md:41`), placed explicitly on the
trusted OS/administrator side rather than the untrusted network side, carries a
two-directional non-guarantee (`ARCH-0003.yaml:54-58`; `00-ARCHITECTURE.md:51`), and the
currency-honesty claim is made conditional on it (`ARCH-0003.yaml:170-174`;
`00-ARCHITECTURE.md:32`, `:140`). `SRR-R0-M1` evidence is fully reversed.

## NR-4 — Floor/recovery scoping sweep (rerun of AR-0023 PR-5, basis for `SRR-R0-H1`)

Every occurrence of `high-water|floor|minimum secure` was re-enumerated across both
documents. AR-0023's finding was that **every** floor-bearing statement was lexically
scoped to the word `rollback`, and that the `recovery` row was the only backward-capable
row with no floor term.

Each of the five floor statements AR-0023 cited is now replaced:

| AR-0023 citation | Pre-correction text | Corrected text |
|---|---|---|
| `ARCH-0003.yaml:86-87` | "**Rollback** below those floors is refused." | §7 `:112-117` — "no privileged lifecycle ingress — init, adopt, update, reinstall, rollback or recovery — may place the machine on a release below its protected local high-water or below the signed minimum secure release… `rollback` is the name of one governed ingress, not the name of the rule" |
| `00-ARCHITECTURE.md:32` | "**rollback** below known signed floors is refused" | `:32` — "no lifecycle ingress places the machine on a release below its protected high-water or the signed minimum secure release, except under the explicitly authorised, recorded and marked break-glass recovery mode" |
| `00-ARCHITECTURE.md:104` | "prevents unsafe **rollback**" | `:136` — "prevents unsafe downgrade at every ingress, not only at `rollback`" |
| `00-ARCHITECTURE.md:80` (recovery row, **no floor term**) | "authenticated recovery target or installed valid recovery path … restore one complete valid state" | `:90` — "…**in both cases not below the security/high-water floor**"; authority "below floor only under break-glass"; effect "at or above floor, or a marked `DEGRADED — RECOVERY ONLY` state" |
| `ARCH-0003.yaml:91` (revoked binary may `recovery`) | "limited to inspection, export, **recovery** and uninstall" | §7.2 `:163-168` — "participation in restoring an **admissible** release… a revoked or below-floor release is not an admissible recovery object under the floor check" |

A new normative subsection `### Signed floors bind every ingress`
(`00-ARCHITECTURE.md:94-98`) states the rule over the ingress set and binds the floor
check to "the single verification policy every ingress calls".

**Result: the `SRR-R0-H1` evidence base is fully reversed.** No floor statement remains
scoped to `rollback` alone. See NA-1…NA-6 for the fresh attacks run against the
replacement text.

## NR-5 — Non-production trust-mode sweep (rerun of AR-0023 PR-4)

```
$ grep -rniE 'dev_mode|dev-mode|insecure|unsigned|test_mode|GOV_TRUST|GOV_DEV|bootstrap_mode|trust_mode|allow_untrusted|skip_verify|break.glass|breakglass' runtime/ cli/ framework/
(no matches)
```

**Result: unchanged from AR-0023.** No dev/test/bootstrap trust mode exists in the
product source, and — correctly — **no break-glass implementation exists either**: the
correction is architecture text only, and no implementation was authorised or performed.
`SRR-R0-L4` remains a non-falsified R1 obligation.

---

# Part 2 — Fresh held-out attacks authored by this review

## NA-1 — Does break-glass relax anything other than the floor check?

Attack: if "break-glass" were a general bypass, it would readmit unsigned or
unauthenticated code and defeat R0 items 2, 5 and 6.

Evidence: `ARCH-0003.yaml:138-140` — "Break-glass relaxes the floor check only; it never
relaxes the authenticity check and never admits arbitrary or unsigned code."
`00-ARCHITECTURE.md:104` — identical in bullet form. The ingress table's `recovery` row
still requires an authenticated object in both branches.

**Result: PASS, no defect.** The relaxation is confined to admissibility. Authenticity,
verified-byte binding and the transaction invariant are untouched by the mode.

## NA-2 — Can repository content, environment variables, caller fields, plugins or model output manufacture break-glass authority?

Attack: the five lower-trust input classes of D-0007 (T4/T5/T6) are exactly the classes
that produced V-H1 in the 4.1.4 lineage. If any could assert break-glass entry, the mode
becomes a self-service downgrade.

Evidence: `ARCH-0003.yaml:140-143` names all five explicitly and ties the rule to "the
D-0007 trust direction of section 8 applied to this mode". `00-ARCHITECTURE.md:105`
repeats it and adds a sixth exclusion the owner did not require: "a below-floor or
revoked binary cannot authorise its own entry". `00-ARCHITECTURE.md:92` retains the
general rule that no ingress trusts a source path, repository manifest, `framework.lock`,
Git ref, environment variable or caller statement as release authority.

**Result: PASS, no defect.** All five owner-named classes are excluded, plus
self-authorisation. Cross-checked against D-0007 T4/T5/T6 (`spec/decisions/D-0007.yaml:32-35`);
the architecture's exclusion set is a superset of the owner's.

## NA-3 — Can a revoked binary re-establish itself through the recovery allowance?

Attack: AR-0023's counterexample turned on `ARCH-0003.yaml:91` permitting a known-revoked
binary to perform `recovery`. If that allowance survives, the revoked release can loop
itself back into place.

Evidence: `ARCH-0003.yaml:163-168` and `00-ARCHITECTURE.md:142`. The allowance is now
"participation in restoring an **admissible** release", and is qualified in the same
sentence: "a revoked or below-floor release is not an admissible recovery object under
the floor check, and placing the machine back onto one requires the break-glass
authorisation of section 7.1, **which a revoked binary cannot issue to itself** and which
leaves the machine marked `DEGRADED — RECOVERY ONLY` with privileged governance work
withheld."

**Result: PASS, no defect.** The loop is closed at three points: the object is
inadmissible; the authority cannot be self-issued; and the outcome is marked and
privilege-restricted. Note that break-glass **can** restore a revoked-but-authentic
release under owner authority — this is consistent with `OWNER-DECISION-0006` requirement 1,
since a revoked release is still an authentic one, and the result is marked.

## NA-4 — Is network or code-hosting reachability a precondition of recovery? (owner requirement 10)

Attack: if break-glass authority were validated against a remote service, the owner's
availability constraint fails exactly when it matters — an offline machine below floor.

Evidence: `ARCH-0003.yaml:143-144` — "Network or repository-hosting reachability is not
that authority and is not a precondition of it: recovery must remain possible with no
network or code-hosting access." `00-ARCHITECTURE.md:106` bullet **Works without network**.
The offline authenticity basis at `ARCH-0003.yaml:124-129` supplies a
no-current-metadata path, so the requirement is not merely asserted but has a stated basis.

**Result: PASS, no defect.** Owner requirement 10 is met in architecture text, with a
mechanism-level basis rather than a bare assertion.

## NA-5 — Deadlock: can a below-floor machine actually escape?

Attack — authored by this review, not raised by AR-0023. While below floor the machine
must refuse "creation or approval of Human Gates". If restoring an authenticated release
normally requires a Human Gate, the refused-activity list would make the exit condition
unreachable and the machine permanently stranded — an availability defect created by the
correction itself.

Evidence: the permitted list (`ARCH-0003.yaml:149-151`; `00-ARCHITECTURE.md:109`)
explicitly includes "uninstall/reinstall" and "restoration of an authenticated Governance
OS release". The restore path is therefore permitted *as itself*, not as a consequence of
a gate that cannot be created; the break-glass authority stands in for the ordinary local
authority for the duration of the mode.

**Result: PASS, no defect.** No deadlock. The permitted/refused lists are complementary
rather than contradictory on this point.

## NA-6 — Is the `DEGRADED — RECOVERY ONLY` token byte-identical to the owner's?

Attack: requirement 4 specifies a literal marking token. A visually similar but
byte-different token (hyphen vs em dash, double space, en dash) would make the owner's
requirement untestable at R1.

Evidence: the owner's token is `DEGRADED` + SPACE + U+2014 EM DASH + SPACE + `RECOVERY ONLY`
(`xxd`: `4445 4752 4144 4544 20e2 8094 2052 4543 4f56 4552 5920 4f4e 4c59`). SHA-256 of the
token text, computed for the owner record and for all five occurrences in the two
architecture documents:

```
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   (owner, OWNER-DECISION-0006:29)
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   00-ARCHITECTURE.md:90
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   00-ARCHITECTURE.md:108
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   00-ARCHITECTURE.md:142
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   ARCH-0003.yaml:146
3807762ff421ab2bf8d692b670417f307edab68d73a10fe3f97d80c3a1345796   ARCH-0003.yaml:168
```

**Result: PASS, exact match at all five sites.** Requirement 4 is mechanically testable at R1.

## NA-7 — The intact-versus-admissible distinction: can "intact" be read as "admissible"?

Attack: AR-0023's counterexample laundered a downgrade through D-0007 self-consistency.
If the corrected text merely *adds* a floor sentence without severing the inference
"D-0007 records validate the copy ⇒ the copy may be installed", the defect survives.

Evidence: the severance is stated three times and in both directions.
`00-ARCHITECTURE.md:98` — "Local installed-integrity evidence establishes that a local copy
is *intact*, never that it is *admissible*… it is not a first-install authenticity root,
and **it is not a floor check**… Admissibility is still the floor check."
`ARCH-0003.yaml:120-129` separates three predicates explicitly: the D-0007 records
"establish only that the local copy is unmodified. They do **not** establish that it is
authentic, and they do **not** establish that it is admissible."

**Result: PASS, no defect.** Intact, authentic and admissible are now three distinct
predicates with three distinct sources. This also strengthens frozen R0 item 11
(separation of authenticity from installed integrity) beyond its pre-correction state.

## NA-8 — Is the offline authenticity basis circular?

Attack — named by `HO-0025` and pressed hard here. The corrected text says that where no
current metadata is reachable, authenticity "derives from this machine's own protected
record of the release identity it previously verified and installed". If that record were
itself derived from the copy being validated, the basis is circular and R0 item 14 fails.

Evidence: the record is protected *machine* state, written at a prior successful
verification whose authority was signed release/targets metadata
(`ARCH-0003.yaml:73-75` chain steps 6–8; `:105-107` transaction invariant "durably update
high-water/journal state"). The corrected sentence explicitly excludes the four circular
sources: "never from the manifest, the lock, the repository or mutually consistent files
delivered with the copy" (`ARCH-0003.yaml:126-127`; `00-ARCHITECTURE.md:98`).

**Result: PASS on circularity — the basis is not circular.** Authenticity flows
metadata → verification → protected local state → later offline recovery, and never from
the artifact being validated. Contract v3 A2 "A source directory cannot regenerate its own
trusted identity" and "Trusted release identity is recorded, not invented, by
`framework.lock`" are both preserved.

**One residual precision point, non-blocking:** the record is described as binding the
release *identity*, and §4 of the same document distinguishes "release version" from
"exact kernel/CLI/payload digests". Under the narrow reading (version string only), a
coherently rewritten local tree bearing the same version would satisfy both the D-0007
chain and the identity match. The architecture does not mandate that narrow reading, and
the transaction invariant already requires the committed representation to be verified and
journalled, so the safe reading is available without an architecture change. Carried as
condition `SRR2-R1-C2` — **R1, non-blocking**, not an R0 blocker.

## NA-9 — Does the floor rule actually reach `init`, `adopt`, `update` and `reinstall`?

Attack: a rule written as prose could still be read as applying only to the two
backward-capable ingresses, leaving AR-0023's defect half-closed.

Evidence: all six ingresses are enumerated by name in both documents
(`ARCH-0003.yaml:113-115`; `00-ARCHITECTURE.md:96`), and the rule is attached to the
machine rather than the operation ("The signed floors are a property of the machine, not
of one operation"). `00-ARCHITECTURE.md:136` restates it in the freshness register:
"prevents unsafe downgrade at every ingress, not only at `rollback`".

**Result: PASS, no defect.** Owner requirement 9 (ingress consistency) is met, and the
scope is stated in three independent places so it cannot be read away from any one of them.

## NA-10 — Can a wrong clock lower a signed floor?

Attack — this is the composition the correction's own non-guarantee claims is safe:
"Neither case lowers a signed floor, admits an unauthorised release or breaks the
verified-byte binding: the failure is confined to freshness" (`00-ARCHITECTURE.md:51`).
Tested rather than taken on trust.

Reasoning against the text: with the clock set behind, expired metadata evaluates as
unexpired. Could an old, validly signed metadata set carrying a *lower* minimum secure
release then reset the machine's floor? No — the floor is protected by the **version**
high-water, not by expiry: "A client never accepts an older metadata version than its
protected high-water" (`00-ARCHITECTURE.md:135`) and "Once a valid revocation/minimum is
received, protected state prevents forgetting it" (`:141`). Those rules are
clock-independent. Could a wrong clock admit an *unauthorised* release? No — expiry does
not confer authorisation; signatures do, and the signature check is unaffected. With the
clock ahead, current metadata reads as expired and trust-changing operations are refused —
an availability effect only.

**Result: PASS, no defect.** The claim survives the attack. The clock-dependent failure is
genuinely confined to freshness because both floors are anchored to monotonic version
state rather than to time.

## NA-11 — Can a wrong clock, or any time-derived condition, enable break-glass entry?

Attack: if break-glass eligibility were a function of metadata expiry ("no current
metadata reachable"), then a clock set far ahead would expire all metadata and
manufacture the precondition for a below-floor downgrade without owner involvement.

Evidence: entry authority is defined solely as "an owner-controlled local or out-of-band
recovery mechanism" (`ARCH-0003.yaml:140-141`). No clause makes expiry, staleness or
unreachable metadata sufficient for entry; the offline basis at `ARCH-0003.yaml:124-129`
governs how an object is *authenticated* once entry is authorised, not whether entry is
permitted. Below-floor recovery is "refused by default" (`:134-135`).

**Result: PASS, no defect.** Break-glass entry is not time-derived and cannot be
manufactured by clock manipulation. NA-10 and NA-11 together confirm the M1 correction
did not create a new attack surface at the H1 correction's boundary.

## NA-12 — Break-glass exit: does the marking survive until *both* floors are met?

Attack — authored by this review. "Below floor" is defined over two floors: the protected
local high-water **and** the signed minimum secure release (`00-ARCHITECTURE.md:96`). The
exit condition names only one: "resumes only once an authenticated release at or above the
signed minimum secure release is installed and verified, at which point the marking is
cleared" (`00-ARCHITECTURE.md:112`; `ARCH-0003.yaml:154-155`).

Bounded counterexample, entirely inside the declared envelope: machine `M` has protected
high-water `v6` and signed minimum secure release `v4`. Its only complete local state after
a fault is `v5` — authentic, previously verified by `M`, at or above `v4`, but below the
high-water `v6`. Installing `v5` is a below-floor ingress and requires break-glass. On
completion the exit condition is satisfied (`v5 ≥ v4`) and the marking is cleared, while
`M` remains below its protected high-water. The machine then reports itself fully trusted
and resumes privileged governance work at a release below one of its two floors — which
`00-ARCHITECTURE.md:108` ("While below floor the machine is marked") says should still be
marked.

**Result: a genuine internal ambiguity — two senses of the word "floor" in one document —
but NOT an R0 blocker.** Four reasons, stated so the orchestrator can check them:
1. The ingress itself remains compliant: it is authorised, durably recorded and marked at
   the time it occurs. The R0 guarantee at `00-ARCHITECTURE.md:32` is about which ingress
   may place the machine below a floor, and that guarantee holds. What is underspecified is
   the *lifetime* of the marking afterwards.
2. It is not reachable without break-glass authority, which is owner-controlled and
   non-manufacturable (NA-2). No unauthorised party reaches the state.
3. The safe reading is already in the text and needs no architecture change: hold the
   marking until both floors are met, per `:96` and `:108`. An R1 implementer choosing the
   stricter reading satisfies every R0 guarantee. This is the opposite of `SRR-R0-H1`, where
   the insecure reading was the *only* one the text supported.
4. The exit clause transcribes `OWNER-DECISION-0006` requirement 7 faithfully and verbatim
   in substance. Under the frozen boundary's normative hierarchy, owner decisions rank
   first; an architecture is not defective for implementing the owner's own scoping choice.

Carried as condition `SRR2-R1-C1` — **R1, non-blocking**, flagged
`NEW_OWNER_DECISION_REQUIRED` and routed to the orchestrator, because the cleanest
resolution touches the owner's requirement 7 wording rather than the architecture alone.

## NA-13 — Is the high-water durable across a normal uninstall?

Attack — authored by this review. The floor rule is scoped over the six *ingresses*.
`uninstall` is not an ingress, and only the break-glass section forbids resetting the
floor. If an ordinary uninstall cleared protected machine state, a subsequent `init` would
face no floor at all — a floor bypass that needs no break-glass authority.

Evidence for the safe reading: "The signed floors are a property of the machine, not of one
operation" (`00-ARCHITECTURE.md:96`); "Once a valid revocation/minimum is received,
protected state prevents forgetting it" (`:141`); "A persistent machine maintains its own
protected metadata/release high-water" (`:154`). Protected machine state is also
provisioned "outside each governed project repository" (`:152`), so removing a project
does not remove the floor.

**Result: PASS on the stated text — no R0 defect**, but the durability of the high-water
across uninstall/reprovision is not stated as explicitly as the break-glass case is.
Carried as condition `SRR2-R1-C3` — **R1, non-blocking, LOW**. R1 already tests
"metadata/release high-water is durable and monotonic", so the obligation has a home.

## NA-14 — Did the correction weaken any previously satisfied R0 item?

Attack: a correction that strengthens one clause may quietly relax another. The
`00-ARCHITECTURE.md:32` security objective was rewritten, which is the single highest-value
sentence to check.

Evidence: pre-correction it read "rollback below known signed floors is refused";
post-correction "no lifecycle ingress places the machine on a release below its protected
high-water or the signed minimum secure release, except under the explicitly authorised,
recorded and marked break-glass recovery mode below". The scope widens from one ingress to
six; the single exception is the owner's own decision and is itself constrained by eight
stated properties. Every other diff hunk reviewed line by line (NR-2): each is an addition
or a widening. The only deletions are the five superseded floor sentences enumerated in NR-4
and the three superseded freshness bullets, each replaced by a strictly stronger statement.

**Result: PASS, no weakening.** Net effect on R0 items 5, 8, 10, 11, 12 and 14 is a
strengthening; no item is weakened.

## NA-15 — Did the correction smuggle later-lifecycle scope into R0?

Attack: the loop's documented failure mode is lifecycle drift. If the correction imported
any of `SRR-R0-L1`…`SRR-R0-L9` or any R2/R3 control, it would expand R0 by stealth.

Evidence: `git diff --name-only 73227a1 29516f8` returns exactly three paths (NR-2). No
product source, no `release/verification/**`, no `release/root-of-trust/4.1.6*`, no prior
review evidence. Blob-identity comparison confirms unchanged: the frozen boundary,
`02-OP-1-OP-16-DISPOSITION.md`, `03-TRANSITION-MAP.md`, `D-0009`, `D-0007`, `D-0008`,
`ARCH-0002`, Contract v3, `OWNER-DIRECTIVE-0004`, and all three AR-0023 evidence files.
`D-0008` and `ARCH-0002` remain `status: PROVISIONAL`, `proposal_state: PROPOSED`,
`in_effect: false`. `D-0007` remains `status: ACTIVE`. Text sweep confirms no new
requirement for production ceremonies, DDC, supplier independence, reproduction quorum,
multi-source first contact or Gate W/G6 completion. `SRR-R0-L6` (owner-deferred to R1) and
`SRR-R0-L7` (owner-closed) were not routed in, as `OWNER-DECISION-0005` directed.

**Result: PASS, no scope smuggling.** The correction stayed inside CD-R0-1 and CD-R0-2.

## NA-16 — Are the two re-pointed traceability rows accurate? (disclosed judgement call)

Attack: AR-0024 disclosed that it did not fix `SRR-R0-L8` but re-pointed two rows whose
target sections moved. A re-point to a section that does not exist, or that does not
contain the cited material, would be a silent traceability regression.

Row for R0 item 8, `rollback/high-water` → "Lifecycle ingress invariant (Signed floors bind
every ingress; Below-floor break-glass recovery); Freshness and revocation".
Row for R0 item 12, `assumptions and non-guarantees (OS/admin/time/network)` → "Declared
Phase-1 environment, including the declared local time source and its non-guarantee;
acceptance boundary".

Heading existence check:

```
$ grep -nE '^#{2,3} (Lifecycle ingress invariant|Signed floors bind every ingress|Below-floor break-glass recovery|Freshness and revocation|Declared Phase-1 environment)$' 00-ARCHITECTURE.md
34:## Declared Phase-1 environment
79:## Lifecycle ingress invariant
94:### Signed floors bind every ingress
100:### Below-floor break-glass recovery
131:## Freshness and revocation
```

All five cited sections exist verbatim, and each contains the material the row claims:
`:94-98` carries the ingress-wide floor rule, `:100-114` the break-glass properties,
`:131-142` the revocation/high-water register, and `:34-53` the declared time source and its
non-guarantee.

**Result: PASS — both re-points are accurate.** Both are also genuine re-points rather than
additions: the row count is unchanged at eleven, so `SRR-R0-L8` (11 of 14 rows) is correctly
reported as not fixed. `SRR-R0-L8` was INFO/non-blocking at AR-0023 and is carried forward
unchanged at the same severity; frozen R0 items 13 and 14 remain covered in body text
(`00-ARCHITECTURE.md` §"Preservation of Governance OS"; `ARCH-0003.yaml` §9, §11;
`03-TRANSITION-MAP.md`) rather than in the table.

---

## Non-mutation checks required by the role prohibitions

- The only directory written by this run is
  `release/root-of-trust/signed-release-root-v1-review-r0-2/`, plus
  `release/orchestration/phase-1/AGENT_RUNS/AR-0025.report.yaml` in a separate commit.
- No file under `release/root-of-trust/signed-release-root-v1/`,
  `release/root-of-trust/signed-release-root-v1-review-r0/`, `release/verification/**`,
  `release/releases/**`, `release/root-of-trust/4.1.6*` or `release/root-of-trust/meta-review/**`
  was modified.
- No product source, runtime, kernel, CLI, capability, migration or test was modified.
- `D-0007`, `D-0008`, `ARCH-0002`, `D-0009` and the frozen boundary are untouched by this run.
- No session transcript or task-output store was read, listed or searched.
- No user auto-memory was opened or written.
- The product owner was not contacted; the one `NEW_OWNER_DECISION_REQUIRED` item (NA-12 /
  `SRR2-R1-C1`) is recorded here and in `20-LATER-LIFECYCLE-CONDITIONS.md` for the
  orchestrator to route.
- No delegation: this review was performed entirely by the single AR-0025 reviewer session.
  No helper agent, subagent or external session was spawned or consulted.
