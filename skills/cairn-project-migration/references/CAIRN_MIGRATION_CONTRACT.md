# Cairn Migration Contract

## Required Outputs

- `cairn-proposed/`: staged concept files.
- `cairn-proposed/schemas/`: copied schema concepts needed for local validation.
- `reports/CAIRN_MIGRATION_<timestamp>.md`: report as a Cairn concept.

## Candidate Detection

Scan for:

- services and modules: entrypoints, manifests, Dockerfiles, Kubernetes manifests
- APIs: OpenAPI, Swagger, route files, controller files
- data models: migrations, schema files, ORM models, warehouse table definitions
- workflows: CI/CD configs, DAGs, automation scripts
- ownership: CODEOWNERS, manifest maintainers, commit-frequency fallback
- docs: README files, `docs/`, wikis

## Relation Rules

Use `confidence: inferred` for generated relations.

Never upgrade an inferred relation to `declared`; only a human can do that.

Relation notes must cite concrete evidence, for example:

- `Inferred from import 'billing' in src/payments.ts:12.`
- `Inferred from foreign key customer_id references customers in migrations/001_orders.sql:8.`
- `Inferred from config key DATABASE_URL in docker-compose.yml:14.`

## Review Stop

After staging concepts and writing the report, stop. A human decides what to merge.
