# Compatibility

Version 0.1.0 has been tested only with:

- OpenSpec 1.12.0;
- OpenSpec 1.13.0.

No broader semantic-version compatibility is claimed. The installer rejects
other versions unless the package is updated and tested for them.

Both tested versions use the normal `spec-driven` config and preserve the
three non-`openspec-*` skills during `openspec update`.

The package requires the Codex integration layout under `.agents/skills`.
It does not install or alter that integration.

The exact extracted `product-boundaries` skill fails strict YAML-frontmatter
validation because its description contains an unquoted colon. This is an
inherited 0.1.0 issue; correcting it would change the audited file hash.
