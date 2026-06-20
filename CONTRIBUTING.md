# Contributing

Contributions should keep Cairn small, file-native, and easy to verify.

## Local Checks

Run these before opening a pull request:

```sh
python3 -m pip install -e .
python3 -m unittest discover -s tests
cairn validate .
cairn index .
cairn audit . --json-only
```

## Change Rules

- Keep core concepts readable as plain Markdown.
- Do not add databases, runtimes, memory, embeddings, workflows, or permissions to the core format.
- Add fixture tests for validator, indexer, auditor, scanner, or report changes.
- Report compliance per concept. Do not add a whole-bundle compliance score.
- Use RFCs for specification changes.
