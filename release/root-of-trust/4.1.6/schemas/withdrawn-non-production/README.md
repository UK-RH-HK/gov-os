# Withdrawn schemas — non-production history (RoT-1 revision 7)

The schemas in this directory belonged to revision 6 (`4106885`). They are **not part of the certified production profile CP-1**
(`../../35-CERTIFIED-PROFILE.md`) and no certified verifier, admitter or checker validates, accepts or emits instances of them.

| Schema | Revision-6 role | Why withdrawn | Exclusion |
|---|---|---|---|
| `first-contact-manifest.schema.json` | a first-contact manifest composed per Trust State and bound by a first-contact code | the ordinary trust-state publisher composed first-contact values (review r6 RV6-H1); replaced by the First-Contact Authority record at root threshold (`../first-contact-authority.schema.json`, `../../32-FIRST-CONTACT-ROOT.md` §3) | EX-23 |
| `freshness-witness.schema.json` | expiring freshness witnesses under OP-7 (c) | the owner selected OP-7 (a) anchored only, with no witness service | EX-01 |

They are kept only so that the review trail of revision 6 remains readable. A certified binary refuses a root that grants the
witness purpose (`PROFILE_NONCONFORMANT`) and refuses a witness or composed manifest when offered (`PROFILE_MODE_EXCLUDED`,
`FIRST_CONTACT_AUTHORITY_UNVERIFIED`); `evidence/r7/PROF7-profile-conformance.py` checks that neither schema is present among the
certified schemas.
