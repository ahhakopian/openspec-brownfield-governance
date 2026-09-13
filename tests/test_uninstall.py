import json
from pathlib import Path

from support import (
    CONTRACT,
    MODULE,
    SKILL_HASHES,
    TempProjectTest,
    add_project_knowledge,
    invoke,
    write_fake_openspec,
)


class UninstallTests(TempProjectTest):
    def test_uninstall_preserves_context_added_after_install(self):
        invoke(self.root, self.env, "install")
        config = self.root / "openspec/config.yaml"
        text = config.read_text()
        insertion = text.index("\n# Project context")
        text = text[:insertion] + "\n  Target project context added later.\n" + text[insertion:]
        config.write_text(text)

        invoke(self.root, self.env, "uninstall")

        remaining = config.read_text()
        self.assertIn("context: |", remaining)
        self.assertIn("Target project context added later.", remaining)
        self.assertNotIn(CONTRACT["context"], remaining)
        for name in SKILL_HASHES:
            self.assertFalse(
                (self.root / ".agents/skills" / name / "SKILL.md").exists()
            )
        self.assertFalse(
            (self.root / ".openspec-brownfield-governance/receipt.json").exists()
        )

    def test_uninstall_does_not_require_a_supported_openspec_binary(self):
        invoke(self.root, self.env, "install")
        write_fake_openspec(Path(self.env["PATH"].split(":", 1)[0]), "9.9.9")
        result = invoke(self.root, self.env, "uninstall")
        self.assertEqual(result.returncode, 0)
        self.assertFalse(
            (self.root / ".openspec-brownfield-governance/receipt.json").exists()
        )

    def test_uninstall_preserves_project_knowledge(self):
        invoke(self.root, self.env, "install")
        knowledge = add_project_knowledge(self.root)
        deferred_index = self.root / "openspec/deferred-changes/README.md"
        deferred_index.write_text(
            deferred_index.read_text() + "| generic-change | DEFERRED | reason | trigger |\n"
        )
        invoke(self.root, self.env, "uninstall")
        for name in SKILL_HASHES:
            self.assertFalse(
                (self.root / ".agents/skills" / name / "SKILL.md").exists()
            )
        for relative, expected in knowledge.items():
            self.assertEqual((self.root / relative).read_bytes(), expected)
        self.assertIn("generic-change", deferred_index.read_text())
        self.assertFalse(
            (self.root / ".openspec-brownfield-governance/receipt.json").exists()
        )
        config = (self.root / "openspec/config.yaml").read_text()
        self.assertEqual(config, (
            "schema: spec-driven\n\n"
            "# Project context (optional)\n"
            "# Per-artifact rules (optional)\n"
        ))

    def test_locally_modified_skill_blocks_uninstall(self):
        invoke(self.root, self.env, "install")
        target = self.root / ".agents/skills/product-boundaries/SKILL.md"
        target.write_text(target.read_text() + "\nlocal edit\n")
        result = invoke(self.root, self.env, "uninstall", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("will not be deleted", result.stdout)
        self.assertTrue(target.exists())
        self.assertTrue(
            (self.root / ".openspec-brownfield-governance/receipt.json").exists()
        )

    def test_uninstall_dry_run_performs_no_writes(self):
        invoke(self.root, self.env, "install")
        before = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        invoke(self.root, self.env, "uninstall", "--dry-run")
        after = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        self.assertEqual(before, after)

    def test_tampered_receipt_cannot_escape_target_root(self):
        invoke(self.root, self.env, "install")
        sentinel = self.temp / "outside-sentinel.txt"
        sentinel.write_text("must survive\n")
        receipt_path = (
            self.root / ".openspec-brownfield-governance/receipt.json"
        )
        receipt = json.loads(receipt_path.read_text())
        receipt["skills"][0]["path"] = str(sentinel)
        receipt["integrity_sha256"] = MODULE.receipt_integrity(receipt)
        receipt_path.write_text(json.dumps(receipt))
        result = invoke(self.root, self.env, "uninstall", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsafe receipt skill path", result.stdout)
        self.assertEqual(sentinel.read_text(), "must survive\n")

    def test_incomplete_config_provenance_is_rejected(self):
        invoke(self.root, self.env, "install")
        receipt_path = (
            self.root / ".openspec-brownfield-governance/receipt.json"
        )
        receipt = json.loads(receipt_path.read_text())
        receipt["config"]["rules"]["proposal"]["inserted"].pop()
        receipt["integrity_sha256"] = MODULE.receipt_integrity(receipt)
        receipt_path.write_text(json.dumps(receipt))
        result = invoke(self.root, self.env, "uninstall", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("provenance is incomplete", result.stdout)

    def test_receipt_cannot_adopt_modified_skill_or_structural_file(self):
        invoke(self.root, self.env, "install")
        skill = self.root / ".agents/skills/brownfield-map/SKILL.md"
        index = self.root / "openspec/deferred-changes/README.md"
        skill.write_text(skill.read_text() + "\nlocal edit\n")
        index.write_text(index.read_text() + "| work | DEFERRED | reason | trigger |\n")
        receipt_path = (
            self.root / ".openspec-brownfield-governance/receipt.json"
        )
        receipt = json.loads(receipt_path.read_text())
        receipt["skills"][0]["hash"] = MODULE.sha256_path(skill)
        receipt["generated_structural_files"][0]["hash"] = MODULE.sha256_path(index)
        receipt["integrity_sha256"] = MODULE.receipt_integrity(receipt)
        receipt_path.write_text(json.dumps(receipt))
        result = invoke(self.root, self.env, "uninstall", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown managed skill hash", result.stdout)
        self.assertTrue(skill.exists())
        self.assertTrue(index.exists())
