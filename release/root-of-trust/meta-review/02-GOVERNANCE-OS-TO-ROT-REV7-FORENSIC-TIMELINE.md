# Governance OS to RoT Revision 7 forensic timeline

| Time / commit | Event | Requirement effect | Meta-review reading |
|---|---|---|---|
| 2026-09-12 `5118d40` | Original three documents committed | Establishes product baseline | Broad Governance OS, modest release integrity language |
| `f709834` | 4.1.2 candidate | Implements Rust-first core and OS capabilities | Product implementation begins |
| 4.1.2 verification `9563192` | 2 CRITICAL, 7 HIGH plus medium/low defects | Enforces original architecture and prompt amendments | Mostly legitimate baseline verification |
| `78f6853` / 4.1.3 | First repair | Fixes embedder coupling, authority, gates, sensitivity and rebuild issues | Still within product architecture |
| 4.1.3 verification `9cb05d8` | Finds CIT gate bypass, policy weakening, ungoverned plugins | Tightens trust derivation | Necessary closure of explicit authority/security promises |
| `c6b594b` / 4.1.4 | Second repair | Adds policy precedence, governed plugins, observed mutation scope | Sound security hardening |
| 4.1.4 verification `f4b3429` | Finds descriptor self-authorization, unverified installed kernel, self-attested exceptions | Generalizes lower-trust/higher-trust defect | Leads to D-0007 |
| `25dac6e` / 4.1.5 | Third repair; D-0007 ACTIVE | Trust classes, verified installed kernel, governed exceptions | General rule useful, but install-time authenticity remains circular |
| 4.1.5 review `c8a138f` | V-H3: install/update authenticates neither source nor declared release identity | Calls for artifact-independent root at every ingress | Contract A2 later adopts this class |
| `676dfce` | RoT-1 revision 1 | Introduces signed release/root architecture | Start of post-baseline architecture expansion |
| `1c6027c` | Rev 1 rejected | Currency, replay, TOCTOU, role-purpose and legacy ingress findings | Mix of necessary source-auth hardening and expanding lifecycle guarantees |
| `d37b05c` / `e5a6b8a` | Rev 2 / rejection | Adds monotonic state, snapshots, protected paths; rejected on constitutional surface, state selection, binary authenticity, legacy containment | Architecture becomes a generalized trust-state system |
| `ca77a43` / `79a09a1` | Rev 3 / rejection | Adds total floors and stronger state/binary provenance; rejected on project strengthening, stale anchoring, source-to-binary binding | Review remains internally coherent but assurance scope grows |
| `bca05a7` / `97a5545` | Rev 4 / rejection | Adds release-scoped registration and first-binary rules; rejected on threshold-1 attestations and non-circular first TCB | Build/certification and runtime authenticity converge into one protocol |
| `cdb4e14` / `d1228cb` | Rev 5 / rejection | Adds reproduction quorums and first-contact mechanisms; rejected on true first-contact root, build environment and first-hand constitutional content | Bespoke supply-chain proof system now dominates Phase 1 |
| `4106885` / `ab6b1f8` | Rev 6 / rejection | Adds first-hand content, environment logic and decision register; rejected on source composition, unbounded currency, manifest authority and input completeness | Proof obligations expand to every selector/input |
| `fbd09d5` | OWNER-DESIGN-REQUIREMENTS-0001 | Owner selects Option C and OP-1…OP-16 for Rev 7 | Expansion becomes owner-approved normative for CP-1, but still not D-0008 approval |
| `d07d200` | Rev 7 / CP-1 | One concrete profile; excludes option tree | Large design is now a specific owner-directed proposal |
| `54be694` | Rev 7 trust review | Finds unestablished restrictive-fact listing and stale-state C3 | Legitimate against CP-1 claims |
| `30542e5` | OWNER-DESIGN-REQUIREMENTS-0002 | Resolves OT-1 and OT-2 after Rev 7 was authored | Current normative clarification; temporal goalpost movement is owner-driven, not reviewer-created |
| `4fd5ab5` | Owner freezes loop | Prohibits Rev 8 and new architecture author | Correctly stops non-convergent cycle |
| `34633cc` | Rev 7 compatibility review | Confirms stale C3 and carries transaction/recovery issues | One blocker plus implementation-stage concerns |
| `4c7735b` | Synthesis rejects Rev 7 | 2 HIGH, 4 blocking MEDIUM; records correction only | Correct relative to CP-1; too broad as generic Phase-1 product acceptance |
| `d1b79c8` | Frozen evidence package | Final state: D-0007 ACTIVE, D-0008/ARCH-0002 PROPOSED | Proper forensic boundary for this review |
| 2026-09-16 owner-supplied Contract v3 | Current acceptance target supplied | Makes A2/F4, G0–G6, V and W owner-approved | Does not adopt every CP-1 implementation detail |

## Causal summary

The original product did not accidentally “become” CP-1 through reviewer fiat. The sequence was:

1. real implementation defects exposed an authentic trust-boundary gap;
2. the response chose a comprehensive custom trust protocol instead of a narrower standard release-signing boundary;
3. reviews correctly tested the claims the protocol made;
4. owner OP decisions formalized many of the expanded claims;
5. every correction increased the state space and created new proof obligations;
6. Phase-1 architecture acceptance, release certification and advanced supply-chain qualification became conflated.

That causal distinction is the foundation for the recommended rebase.
