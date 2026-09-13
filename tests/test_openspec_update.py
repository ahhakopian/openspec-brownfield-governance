import os
from pathlib import Path
import shutil
import tempfile
import unittest

from support import (
    BOOTSTRAP,
    MODULE,
    REPO,
    SKILL_HASHES,
    add_project_knowledge,
    digest_tree,
    environment,
    run,
    write_openspec_wrapper,
)


class OpenSpecCompatibilityTests(unittest.TestCase):
    def test_real_openspec_versions_preserve_custom_skills_and_validate(self):
        binaries = {
            "1.12.0": os.environ.get("OPENSPEC_112_BIN"),
            "1.13.0": os.environ.get("OPENSPEC_113_BIN"),
        }
        if not all(binaries.values()):
            self.skipTest(
                "set OPENSPEC_112_BIN and OPENSPEC_113_BIN for compatibility tests"
            )
        for version, binary_value in binaries.items():
            with self.subTest(version=version):
                binary = Path(binary_value).resolve()
                self.assertTrue(binary.exists(), binary)
                temp = Path(
                    tempfile.mkdtemp(
                        prefix=f"openspec-brownfield-{version}.", dir="/tmp"
                    )
                )
                try:
                    root = temp / "project"
                    root.mkdir()
                    run(["git", "init", "-q", root])
                    xdg = temp / "xdg"
                    env = environment(temp / "bin", xdg)
                    write_openspec_wrapper(temp / "bin", binary)
                    run(
                        [
                            binary,
                            "init",
                            root,
                            "--tools",
                            "codex",
                            "--no-animation",
                            "--no-copilot-cloud",
                        ],
                        env=env,
                    )
                    result = run(
                        [
                            "python3",
                            BOOTSTRAP,
                            "install",
                            "--target",
                            root,
                        ],
                        cwd=REPO,
                        env=env,
                    )
                    self.assertIn("Installed", result.stdout)
                    installed_digest = digest_tree(root)
                    second_install = run(
                        ["python3", BOOTSTRAP, "install", "--target", root],
                        cwd=REPO,
                        env=env,
                    )
                    self.assertIn("already installed", second_install.stdout)
                    self.assertEqual(installed_digest, digest_tree(root))
                    before = {
                        name: MODULE.sha256_path(
                            root / ".agents/skills" / name / "SKILL.md"
                        )
                        for name in SKILL_HASHES
                    }
                    run([binary, "update", root], env=env)
                    after = {
                        name: MODULE.sha256_path(
                            root / ".agents/skills" / name / "SKILL.md"
                        )
                        for name in SKILL_HASHES
                    }
                    self.assertEqual(before, after)
                    self.assertEqual(after, SKILL_HASHES)
                    validation = run(
                        [
                            binary,
                            "validate",
                            "--all",
                            "--strict",
                            "--json",
                            "--no-interactive",
                        ],
                        cwd=root,
                        env=env,
                    )
                    self.assertIn('"failed": 0', validation.stdout)
                    doctor = run([binary, "doctor", "--json"], cwd=root, env=env)
                    self.assertIn('"healthy": true', doctor.stdout)
                    knowledge = add_project_knowledge(root)
                    run(
                        ["python3", BOOTSTRAP, "update", "--target", root],
                        cwd=REPO,
                        env=env,
                    )
                    for relative, expected in knowledge.items():
                        self.assertEqual((root / relative).read_bytes(), expected)
                    run(
                        ["python3", BOOTSTRAP, "uninstall", "--target", root],
                        cwd=REPO,
                        env=env,
                    )
                    for relative, expected in knowledge.items():
                        self.assertEqual((root / relative).read_bytes(), expected)
                    for name in SKILL_HASHES:
                        self.assertFalse(
                            (root / ".agents/skills" / name / "SKILL.md").exists()
                        )
                finally:
                    shutil.rmtree(temp, ignore_errors=True)
