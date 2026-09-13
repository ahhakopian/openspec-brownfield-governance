# Installation

## Prerequisites

- Git;
- Python 3.10 or newer;
- an existing OpenSpec project with `openspec/config.yaml`;
- OpenSpec 1.12.0 or 1.13.0 on `PATH`;
- Codex integration, evidenced by `.agents/skills/.openspec-target`;
- `schema: spec-driven`.

The bootstrapper has no third-party Python dependencies and does not install
anything globally.

## Commands

```bash
python3 bootstrap/openspec-brownfield.py install --target /path/to/project
python3 bootstrap/openspec-brownfield.py install --target /path/to/project --dry-run
```

`--target` defaults to the current working directory. A subdirectory is
accepted; the Git root is the installation target.

Installation creates the empty deferred-change index when it is absent because
the extracted config and roadmap skill reference it. Once edited with project
records it is project-owned knowledge and is never overwritten.

The installer refuses an existing different skill, a non-`spec-driven`
configuration, a non-Codex OpenSpec target, or an ambiguous partial brownfield
context.
