# Synthetic previous release 4.1.1 (fixture)

This payload never shipped. It was derived from the immutable 4.1.2 release payload (`release/releases/4.1.2/kernel`)
with the documented 4.1.1 differences (no LEARNING/ARCHIVE policies, no PROJECT_EXCEPTIONS template/schema, old
`human_gates` overlay key, `schema_version: 0.9.0`, no bundled migrations, `supported_from_versions: []`). It is stored
immutably so the framework-update fixture upgrades a real on-disk payload instead of deriving one in-test (verifier M16).
