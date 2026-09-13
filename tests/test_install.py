from pathlib import Path
from unittest import mock

from support import (
    BOOTSTRAP,
    CONTRACT,
    MODULE,
    SKILL_HASHES,
    TempProjectTest,
    digest_tree,
    invoke,
    make_project,
    run,
)


class InstallTests(TempProjectTest):
    def test_package_integrity_checks_config_contract_and_template(self):
        damaged_contract = self.temp / "damaged-contract.yaml"
        damaged_contract.write_text(MODULE.CONTRACT_PATH.read_text() + "\n# damage\n")
        with mock.patch.object(MODULE, "CONTRACT_PATH", damaged_contract):
            # A comment is semantically inert and therefore intentionally accepted.
            MODULE.verify_package()
        damaged_contract.write_text("required_schema: spec-driven\n")
        with mock.patch.object(MODULE, "CONTRACT_PATH", damaged_contract):
            with self.assertRaises(MODULE.GovernanceError):
                MODULE.verify_package()

        damaged_template = self.temp / "damaged-template.md"
        damaged_template.write_text("# damaged\n")
        with mock.patch.object(MODULE, "TEMPLATE_PATH", damaged_template):
            with self.assertRaisesRegex(
                MODULE.GovernanceError, "structural template hash mismatch"
            ):
                MODULE.verify_package()

    def test_clean_install_and_second_install_are_idempotent(self):
        self.assertEqual(MODULE.SKILLS, SKILL_HASHES)
        result = invoke(self.root, self.env, "install")
        self.assertIn("Installed openspec-brownfield-governance 0.1.0", result.stdout)
        for name, expected in SKILL_HASHES.items():
            target = self.root / ".agents/skills" / name / "SKILL.md"
            self.assertTrue(target.is_file())
            self.assertEqual(MODULE.sha256_path(target), expected)
        self.assertTrue(
            (self.root / "openspec/deferred-changes/README.md").is_file()
        )
        self.assertFalse(
            MODULE.config_complete(
                (self.root / "openspec/config.yaml").read_text(), CONTRACT
            )
        )
        first = digest_tree(self.root)
        second_result = invoke(self.root, self.env, "install")
        second = digest_tree(self.root)
        self.assertIn("already installed", second_result.stdout)
        self.assertEqual(first, second)

    def test_dry_run_performs_no_writes(self):
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", "--dry-run")
        self.assertIn("Dry run", result.stdout)
        self.assertEqual(before, digest_tree(self.root))
        self.assertFalse(
            (self.root / ".openspec-brownfield-governance/receipt.json").exists()
        )

    def test_unsupported_schema_fails_without_writes(self):
        (self.root / "openspec/config.yaml").write_text("schema: custom-schema\n")
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported schema", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_target_defaults_to_current_working_directory(self):
        result = run(
            ["python3", BOOTSTRAP, "install"],
            cwd=self.root,
            env=self.env,
        )
        self.assertEqual(result.returncode, 0)

    def test_symlink_escape_is_rejected(self):
        outside = self.temp / "outside"
        outside.mkdir()
        receipt_dir = self.root / ".openspec-brownfield-governance"
        receipt_dir.symlink_to(outside, target_is_directory=True)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("escapes the Git root through a symlink", result.stdout)
        self.assertEqual(list(outside.iterdir()), [])
