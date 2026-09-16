import json
import hashlib
import copy
from pathlib import Path
import tempfile

from support import (
    CONTRACT,
    MODULE,
    REPO,
    TempProjectTest,
    digest_tree,
    invoke,
    make_project,
)


class ConfigMergeTests(TempProjectTest):
    def test_contract_matches_independently_pinned_audit_hash(self):
        canonical = json.dumps(
            CONTRACT,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            "bdbbb4d33399c0bc37b676f9b3ddf7aa359bcd762149d74e9d71e3d23dc47c33",
        )
        self.assertEqual(
            {name: len(items) for name, items in CONTRACT["rules"].items()},
            {"proposal": 8, "design": 9, "tasks": 5},
        )
        self.assertEqual(
            {name: len(items) for name, items in CONTRACT["operations"].items()},
            {"apply": 6, "archive": 7},
        )

    def test_ui_lifecycle_precedes_complexity_and_archive_map_maintenance(self):
        apply = CONTRACT["operations"]["apply"]
        archive = CONTRACT["operations"]["archive"]
        preflight = next(
            index for index, item in enumerate(apply)
            if "brownfield-ui-preflight" in item
        )
        complexity = next(
            index for index, item in enumerate(apply)
            if "brownfield-complexity-gate" in item
        )
        conformance = next(
            index for index, item in enumerate(archive)
            if "brownfield-ui-conformance" in item
        )
        final_verification = next(
            index for index, item in enumerate(archive)
            if "final OpenSpec verification" in item
        )
        map_maintenance = next(
            index for index, item in enumerate(archive)
            if "every verified Change" in item
        )
        self.assertLess(preflight, complexity)
        self.assertLess(
            archive[conformance].index("brownfield-ui-conformance"),
            archive[conformance].index("final OpenSpec verification"),
        )
        self.assertLess(final_verification, map_maintenance)
        self.assertIn("remove or replace", archive[map_maintenance])
        self.assertIn("internal architectural consistency only", archive[map_maintenance + 1])
        self.assertIn(
            "only the relevant repository code, tests, or configuration",
            archive[map_maintenance + 2],
        )
        self.assertNotIn("materially changed", "\n".join(archive))

    def test_preexisting_ui_guidance_remains_target_owned_on_uninstall(self):
        preexisting = CONTRACT["operations"]["apply"][1]
        initial = (
            "schema: spec-driven\n\noperations:\n  apply:\n    guidance:\n"
            "      - " + json.dumps(preexisting) + "\n"
        )
        self.root, self.env = make_project(self.temp / "preexisting-ui", initial)

        invoke(self.root, self.env, "install")
        receipt = json.loads(
            (self.root / ".openspec-brownfield-governance/receipt.json").read_text()
        )
        provenance = receipt["config"]["operations"]["apply"]
        self.assertIn(preexisting, provenance["pre_existing"])
        self.assertNotIn(preexisting, provenance["inserted"])

        invoke(self.root, self.env, "uninstall")
        values = [
            value
            for _, value in MODULE.YamlText(
                (self.root / "openspec/config.yaml").read_text()
            ).list_values(("operations", "apply", "guidance"))
        ]
        self.assertEqual(values, [preexisting])

    def test_complexity_contract_clauses_are_merged_once_and_reinstall_is_idempotent(self):
        invoke(self.root, self.env, "install")
        first = digest_tree(self.root)
        invoke(self.root, self.env, "install")
        self.assertEqual(first, digest_tree(self.root))

        merged = (self.root / "openspec/config.yaml").read_text()
        self.assertEqual(merged.count("Brownfield Simplicity Policy:"), 1)
        editor = MODULE.YamlText(merged)
        for path, item in (
            (("rules", "design"), CONTRACT["rules"]["design"][-2]),
            (("rules", "design"), CONTRACT["rules"]["design"][-1]),
            (("rules", "tasks"), CONTRACT["rules"]["tasks"][0]),
            (("operations", "apply", "guidance"), CONTRACT["operations"]["apply"][1]),
            (("operations", "apply", "guidance"), CONTRACT["operations"]["apply"][2]),
        ):
            values = [value for _, value in editor.list_values(path)]
            self.assertEqual(values.count(item), 1)

    def test_modified_managed_clause_refuses_versioned_removal(self):
        original = "schema: spec-driven\n"
        installed, receipt = MODULE.merge_config(original, CONTRACT)
        modified = installed.replace(CONTRACT["rules"]["design"][0], "modified", 1)
        with self.assertRaisesRegex(MODULE.GovernanceError, "inserted config item"):
            MODULE.uninstall_config(modified, receipt)

    def test_unrelated_config_and_supported_fields_survive(self):
        fixture = (REPO / "tests/fixtures/config-with-unrelated.yaml").read_text()
        self.root, self.env = make_project(self.temp / "unrelated", fixture)
        invoke(self.root, self.env, "install")
        merged = (self.root / "openspec/config.yaml").read_text()
        for exact in (
            "Existing target project context.",
            "Keep this unrelated proposal rule.",
            "Keep this unrelated apply guidance.",
            "store: existing-store",
            "references:",
            "  - shared-reference",
            "githubCopilot:",
            "  cloudAgent: false",
        ):
            self.assertIn(exact, merged)
        self.assertFalse(MODULE.config_complete(merged, CONTRACT))

    def test_preexisting_items_are_not_duplicated_or_removed(self):
        contract = CONTRACT
        preexisting_rule = contract["rules"]["proposal"][0]
        initial = (
            "schema: spec-driven\n\n"
            "context: |\n"
            + "\n".join(
                ("  " + line) if line else "  "
                for line in contract["context"].split("\n")
            )
            + "\n\nrules:\n  proposal:\n    - "
            + json.dumps(preexisting_rule)
            + "\n"
        )
        self.root, self.env = make_project(self.temp / "preexisting", initial)
        invoke(self.root, self.env, "install")
        receipt = json.loads(
            (
                self.root / ".openspec-brownfield-governance/receipt.json"
            ).read_text()
        )
        self.assertIn(
            preexisting_rule,
            receipt["config"]["rules"]["proposal"]["pre_existing"],
        )
        self.assertNotIn(
            preexisting_rule,
            receipt["config"]["rules"]["proposal"]["inserted"],
        )
        merged = (self.root / "openspec/config.yaml").read_text()
        editor = MODULE.YamlText(merged)
        values = [
            value for _, value in editor.list_values(("rules", "proposal"))
        ]
        self.assertEqual(values.count(preexisting_rule), 1)
        invoke(self.root, self.env, "uninstall")
        after = (self.root / "openspec/config.yaml").read_text()
        self.assertIn(contract["context"], "\n".join(
            MODULE.YamlText(after).literal_block("context")[2]
        ))
        values_after = [
            value
            for _, value in MODULE.YamlText(after).list_values(("rules", "proposal"))
        ]
        self.assertIn(preexisting_rule, values_after)

    def test_conflicting_partial_context_fails_without_writes(self):
        fixture = (REPO / "tests/fixtures/config-partial-context.yaml").read_text()
        self.root, self.env = make_project(self.temp / "partial", fixture)
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("conflicting partial brownfield context", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_any_exact_partial_context_line_fails_safely(self):
        final_line = CONTRACT["context"].splitlines()[-1]
        initial = f"schema: spec-driven\n\ncontext: |\n  {final_line}\n"
        self.root, self.env = make_project(self.temp / "partial-final", initial)
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("conflicting partial brownfield context", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_block_scalar_rule_fails_safely_instead_of_duplicating(self):
        required = CONTRACT["rules"]["proposal"][0]
        initial = (
            "schema: spec-driven\n\nrules:\n  proposal:\n"
            "    - >-\n"
            f"      {required}\n"
        )
        self.root, self.env = make_project(self.temp / "block-rule", initial)
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("block-scalar list item is unsafe", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_duplicate_complete_context_blocks_fail_safely(self):
        body = "\n".join(
            ("  " + line) if line else "  "
            for line in CONTRACT["context"].split("\n")
        )
        initial = f"schema: spec-driven\n\ncontext: |\n{body}\n  \n{body}\n"
        self.root, self.env = make_project(self.temp / "duplicate-context", initial)
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate brownfield context blocks", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_duplicate_required_rule_fails_safely(self):
        required = json.dumps(CONTRACT["rules"]["proposal"][0])
        initial = (
            "schema: spec-driven\n\nrules:\n  proposal:\n"
            f"    - {required}\n    - {required}\n"
        )
        self.root, self.env = make_project(self.temp / "duplicate-rule", initial)
        before = digest_tree(self.root)
        result = invoke(self.root, self.env, "install", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicate brownfield config item", result.stdout)
        self.assertEqual(before, digest_tree(self.root))

    def test_config_mode_and_final_newline_are_preserved(self):
        config = self.root / "openspec/config.yaml"
        original = b"schema: spec-driven"
        config.write_bytes(original)
        config.chmod(0o600)
        invoke(self.root, self.env, "install")
        self.assertFalse(config.read_bytes().endswith(b"\n"))
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        invoke(self.root, self.env, "uninstall")
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_versioned_contract_migration_replaces_only_owned_clauses(self):
        original = (
            "schema: spec-driven\n\ncontext: |\n  Existing target context.\n"
            "\nrules:\n  proposal:\n    - Keep this target rule.\n"
        )
        installed, old_receipt = MODULE.merge_config(original, CONTRACT)
        replacement = copy.deepcopy(CONTRACT)
        replacement["context"] += "\n\nReplacement release clause."
        replacement["rules"]["proposal"] = replacement["rules"]["proposal"][:-1]
        replacement["rules"]["proposal"].append("Replacement release rule.")
        migration_base = MODULE.uninstall_config(installed, old_receipt)
        self.assertEqual(migration_base, original)
        migrated, new_receipt = MODULE.merge_config(migration_base, replacement)
        self.assertFalse(MODULE.config_complete(migrated, replacement))
        self.assertIn("Keep this target rule.", migrated)
        self.assertNotIn(CONTRACT["rules"]["proposal"][-1], migrated)
        self.assertIn("Replacement release rule.", migrated)
