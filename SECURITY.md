# Security Policy

## Reporting

Report security issues privately to the repository owner before public disclosure.

## Scope

Security-sensitive areas include:

- path traversal or writes outside requested output directories
- unsafe parsing of project files
- command execution in migration or validation tools
- incorrect hash verification
- handling of private project data in generated reports

The migration scanner is intended to be read-only unless `--write-into-target` is explicitly provided.

See [docs/security/THREAT_MODEL.md](docs/security/THREAT_MODEL.md) for the current threat model.
