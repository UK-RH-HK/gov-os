# Framework migrations

Declarative, versioned migration definitions executed by `gov update --apply`. Each file is validated against
`framework/schemas/migration.schema.json`. Migrations may only touch `governance/project/` (overlay),
`governance/framework.lock`, `governance/generated/` and derived runtime. They never modify `spec/` or `product/`
(hard invariant INV-013).
