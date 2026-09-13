from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO / "bootstrap" / "openspec-brownfield.py"


def load_bootstrap():
    spec = importlib.util.spec_from_file_location("openspec_brownfield", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MODULE = load_bootstrap()
CONTRACT = MODULE.parse_contract()
SKILL_HASHES = {
    "brownfield-map": "e8dc54021787e5d9d850f41820bab42ef26a764f91a082b9c33ce5ff1ad087c5",
    "product-boundaries": "e230369e9fb0d4a65c3866948b5b895431155e56f61801a3ee6d9ac8207d686c",
    "cross-change-roadmap": "26d2ba26fa20af3b88b5d4a271d132f202a499003bfb0e0265808015562c024b",
}


def run(args, *, cwd=None, env=None, check=True):
    result = subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and result.returncode:
        raise AssertionError(f"command failed {args}:\n{result.stdout}")
    return result


def write_fake_openspec(bin_dir: Path, version: str = "1.12.0") -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    path = bin_dir / "openspec"
    path.write_text(
        "#!/bin/sh\n"
        f"if [ \"$1\" = \"--version\" ]; then echo {version}; exit 0; fi\n"
        "if [ \"$1\" = \"doctor\" ]; then echo "
        "'{\"root\":{\"healthy\":true},\"status\":[]}'; exit 0; fi\n"
        "if [ \"$1\" = \"validate\" ]; then echo "
        "'{\"items\":[],\"summary\":{\"totals\":{\"failed\":0}}}'; exit 0; fi\n"
        "if [ \"$1\" = \"list\" ]; then echo '{\"changes\":[]}'; exit 0; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def write_openspec_wrapper(bin_dir: Path, binary: Path) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    path = bin_dir / "openspec"
    escaped = str(binary).replace("'", "'\"'\"'")
    path.write_text(f"#!/bin/sh\nexec '{escaped}' \"$@\"\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def environment(bin_dir: Path, xdg_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env["XDG_CONFIG_HOME"] = str(xdg_dir)
    return env


def make_project(base: Path, config: str | None = None) -> tuple[Path, dict[str, str]]:
    root = base / "project"
    root.mkdir(parents=True)
    run(["git", "init", "-q", root])
    (root / ".agents/skills").mkdir(parents=True)
    (root / ".agents/skills/.openspec-target").write_text("codex\n")
    (root / "openspec/changes/archive").mkdir(parents=True)
    (root / "openspec/specs").mkdir(parents=True)
    (root / "openspec/config.yaml").write_text(
        config
        if config is not None
        else (
            "schema: spec-driven\n\n"
            "# Project context (optional)\n"
            "# Per-artifact rules (optional)\n"
        ),
        encoding="utf-8",
    )
    fake_bin = base / "bin"
    write_fake_openspec(fake_bin)
    return root, environment(fake_bin, base / "xdg")


def invoke(root: Path, env: dict[str, str], *args: str, check: bool = True):
    return run(
        ["python3", BOOTSTRAP, *args, "--target", root],
        cwd=REPO,
        env=env,
        check=check,
    )


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def add_project_knowledge(root: Path) -> dict[str, bytes]:
    content = {
        "openspec/system/brownfield-map.md": b"# Generic system map\n",
        "openspec/roadmap.md": b"# Generic roadmap\n",
        "docs/product/product-model.md": b"# Generic product model\n",
        "docs/product/product-boundaries.md": b"# Generic boundaries\n",
        "docs/product/access-model.md": b"# Generic access model\n",
        "PRD.canonical.md": b"# Generic requirements\n",
        "openspec/specs/example/spec.md": b"# Example Specification\n",
        "openspec/changes/archive/example/proposal.md": b"# Example archived change\n",
        "openspec/deferred-changes/example/DEFERRED.md": b"# Generic deferred work\n",
    }
    for relative, data in content.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return content


class TempProjectTest(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix="openspec-brownfield-test.", dir="/tmp"))
        self.root, self.env = make_project(self.temp)

    def tearDown(self):
        shutil.rmtree(self.temp, ignore_errors=True)
