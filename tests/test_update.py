import json
from pathlib import Path
from unittest import mock

from support import (
    CONTRACT,
    HISTORICAL_VERSION,
    MODULE,
    REPO,
    RELEASE_VERSION,
    SKILL_HASHES,
    TempProjectTest,
    add_project_knowledge,
    digest_tree,
    invoke,
)


class UpdateTests(TempProjectTest):
    def historical_contract(self):
        fixture = REPO / "tests/fixtures/brownfield-config-0.1.0.yaml"
        with mock.patch.object(MODULE, "CONTRACT_PATH", fixture):
            return MODULE.parse_contract()

    def install_historical_0_1_0(self, *, preexisting_context=False):
        contract = self.historical_contract()
        if preexisting_context:
            original = (
                "schema: spec-driven\n\ncontext: |\n"
                + "\n".join(
                    ("  " + line) if line else "  "
                    for line in contract["context"].split("\n")
                )
                + "\n\nrules:\n  proposal:\n    - Target-owned proposal rule.\n\n"
                "operations:\n  apply:\n    guidance:\n"
                "      - Target-owned apply guidance.\n"
            )
        else:
            original = (
                "schema: spec-driven\n\ncontext: |\n"
                "  Target-owned context survives upgrade.\n\n"
                "rules:\n  proposal:\n    - Target-owned proposal rule.\n\n"
                "operations:\n  apply:\n    guidance:\n"
                "      - Target-owned apply guidance.\n"
            )
        installed, config_receipt = MODULE.merge_config(original, contract)
        if preexisting_context:
            self.assertEqual(
                config_receipt["context"],
                {"inserted": False, "pre_existing": True, "value": contract["context"]},
            )
        (self.root / "openspec/config.yaml").write_text(installed)
        skills = []
        for name, expected in MODULE.KNOWN_SKILL_HASHES[HISTORICAL_VERSION].items():
            source = REPO / "skills" / name / "SKILL.md"
            target = self.root / ".agents/skills" / name / "SKILL.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            self.assertEqual(MODULE.sha256_path(target), expected)
            skills.append(
                {
                    "name": name,
                    "path": str(Path(".agents/skills") / name / "SKILL.md"),
                    "hash": expected,
                    "created": True,
                }
            )
        receipt = {
            "format": 1,
            "package": MODULE.PACKAGE_NAME,
            "distribution_version": HISTORICAL_VERSION,
            "openspec_version": "1.12.0",
            "installed_at": "2026-01-01T00:00:00+00:00",
            "skills": skills,
            "config": config_receipt,
            "generated_structural_files": [],
        }
        receipt["integrity_sha256"] = MODULE.receipt_integrity(receipt)
        receipt_path = self.root / ".openspec-brownfield-governance/receipt.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt))
        return contract

    def test_update_migrates_valid_0_1_0_installation_to_four_skill_0_2_0(self):
        historical_contract = self.install_historical_0_1_0()
        previous = MODULE.read_receipt(self.root, CONTRACT)
        self.assertEqual(previous["distribution_version"], HISTORICAL_VERSION)
        self.assertEqual(
            {entry["name"] for entry in previous["skills"]},
            set(MODULE.KNOWN_SKILL_HASHES[HISTORICAL_VERSION]),
        )
        knowledge = add_project_knowledge(self.root)

        invoke(self.root, self.env, "update")

        config = (self.root / "openspec/config.yaml").read_text()
        self.assertIn("Target-owned context survives upgrade.", config)
        self.assertIn("Target-owned proposal rule.", config)
        self.assertIn("Target-owned apply guidance.", config)
        self.assertNotIn(historical_contract["rules"]["tasks"][0], config)
        self.assertEqual(MODULE.config_complete(config, CONTRACT), [])
        for name, expected in SKILL_HASHES.items():
            self.assertEqual(
                MODULE.sha256_path(self.root / ".agents/skills" / name / "SKILL.md"),
                expected,
            )
        for relative, expected in knowledge.items():
            self.assertEqual((self.root / relative).read_bytes(), expected)
        receipt = json.loads(
            (self.root / ".openspec-brownfield-governance/receipt.json").read_text()
        )
        self.assertEqual(receipt["distribution_version"], RELEASE_VERSION)
        self.assertEqual({entry["name"] for entry in receipt["skills"]}, set(SKILL_HASHES))
        self.assertEqual(MODULE.read_receipt(self.root, CONTRACT), receipt)

        first = digest_tree(self.root)
        invoke(self.root, self.env, "update")
        self.assertEqual(first, digest_tree(self.root))

    def test_update_preserves_preexisting_0_1_0_context_and_uninstalls_only_suffix(self):
        historical_contract = self.install_historical_0_1_0(preexisting_context=True)
        historical_context = historical_contract["context"]

        invoke(self.root, self.env, "update")

        config = (self.root / "openspec/config.yaml").read_text()
        editor = MODULE.YamlText(config)
        self.assertEqual(
            "\n".join(editor.literal_block("context")[2]).rstrip("\n"),
            CONTRACT["context"],
        )
        self.assertTrue(CONTRACT["context"].startswith(historical_context + "\n\n"))
        self.assertEqual(config.count("Brownfield Simplicity Policy:"), 1)
        gate = self.root / ".agents/skills/brownfield-complexity-gate/SKILL.md"
        self.assertEqual(MODULE.sha256_path(gate), SKILL_HASHES["brownfield-complexity-gate"])
        receipt = json.loads(
            (self.root / ".openspec-brownfield-governance/receipt.json").read_text()
        )
        self.assertEqual(receipt["distribution_version"], RELEASE_VERSION)
        policy_suffix = "Brownfield Simplicity Policy:\n" + CONTRACT["context"].split(
            "\n\nBrownfield Simplicity Policy:\n", 1
        )[1]
        self.assertEqual(
            receipt["config"]["context"],
            {
                "inserted": True,
                "pre_existing": True,
                "value": policy_suffix,
                "pre_existing_value": historical_context,
            },
        )
        self.assertEqual(MODULE.read_receipt(self.root, CONTRACT), receipt)

        first = digest_tree(self.root)
        invoke(self.root, self.env, "update")
        self.assertEqual(first, digest_tree(self.root))

        invoke(self.root, self.env, "uninstall")
        remaining = (self.root / "openspec/config.yaml").read_text()
        remaining_context = "\n".join(
            MODULE.YamlText(remaining).literal_block("context")[2]
        )
        self.assertEqual(remaining_context.rstrip("\n"), historical_context)
        self.assertIn("Target-owned proposal rule.", remaining)
        self.assertIn("Target-owned apply guidance.", remaining)
        self.assertNotIn("Brownfield Simplicity Policy:", remaining)
        self.assertFalse(gate.exists())

    def test_structural_template_update_and_ownership_transfer(self):
        index = self.root / "openspec/deferred-changes/README.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        old_template = b"# Earlier empty structure\n"
        index.write_bytes(old_template)
        old_entry = {
            "path": "openspec/deferred-changes/README.md",
            "hash": MODULE.sha256_bytes(old_template),
            "created": True,
        }

        entries, writes = MODULE.plan_structural_file(
            self.root, {"generated_structural_files": [old_entry]}
        )
        self.assertTrue(entries[0]["created"])
        self.assertEqual(entries[0]["hash"], MODULE.sha256_path(MODULE.TEMPLATE_PATH))
        self.assertEqual(writes[0][1], MODULE.TEMPLATE_PATH.read_bytes())

        index.write_bytes(old_template + b"| target work | DEFERRED | reason | trigger |\n")
        entries, writes = MODULE.plan_structural_file(
            self.root, {"generated_structural_files": [old_entry]}
        )
        self.assertFalse(entries[0]["created"])
        self.assertEqual(entries[0]["hash"], MODULE.sha256_path(index))
        self.assertEqual(writes, [])

    def test_deleted_project_owned_structural_file_is_not_recreated(self):
        previous = {
            "generated_structural_files": [
                {
                    "path": "openspec/deferred-changes/README.md",
                    "hash": "0" * 64,
                    "created": False,
                }
            ]
        }
        entries, writes = MODULE.plan_structural_file(self.root, previous)
        self.assertEqual(entries, [])
        self.assertEqual(writes, [])

    def test_preexisting_populated_deferred_index_remains_project_owned(self):
        index = self.root / "openspec/deferred-changes/README.md"
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text("# Deferred work\n\n| generic-change | DEFERRED | reason | trigger |\n")
        expected = index.read_bytes()

        invoke(self.root, self.env, "install")
        invoke(self.root, self.env, "install")
        invoke(self.root, self.env, "update")
        self.assertEqual(index.read_bytes(), expected)
        invoke(self.root, self.env, "uninstall")
        self.assertEqual(index.read_bytes(), expected)

    def test_noop_update_and_update_dry_run_do_not_write(self):
        invoke(self.root, self.env, "install")
        before = digest_tree(self.root)
        invoke(self.root, self.env, "update", "--dry-run")
        self.assertEqual(before, digest_tree(self.root))
        invoke(self.root, self.env, "update")
        self.assertEqual(before, digest_tree(self.root))

    def test_update_preserves_all_project_owned_artifacts(self):
        invoke(self.root, self.env, "install")
        knowledge = add_project_knowledge(self.root)
        invoke(self.root, self.env, "update")
        for relative, expected in knowledge.items():
            self.assertEqual((self.root / relative).read_bytes(), expected)

    def test_update_refuses_locally_modified_skill_without_other_writes(self):
        invoke(self.root, self.env, "install")
        target = self.root / ".agents/skills/brownfield-map/SKILL.md"
        target.write_text(target.read_text() + "\nlocal edit\n")
        config_before = (self.root / "openspec/config.yaml").read_bytes()
        receipt_before = (
            self.root / ".openspec-brownfield-governance/receipt.json"
        ).read_bytes()
        result = invoke(self.root, self.env, "update", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("locally modified skill", result.stdout)
        self.assertTrue(target.read_text().endswith("local edit\n"))
        self.assertEqual(
            config_before, (self.root / "openspec/config.yaml").read_bytes()
        )
        self.assertEqual(
            receipt_before,
            (self.root / ".openspec-brownfield-governance/receipt.json").read_bytes(),
        )

    def test_package_operations_preserve_upstream_openspec_skill(self):
        upstream = self.root / ".agents/skills/openspec-propose/SKILL.md"
        upstream.parent.mkdir(parents=True)
        upstream.write_text("# upstream sentinel\n")
        expected = upstream.read_bytes()
        invoke(self.root, self.env, "install")
        invoke(self.root, self.env, "update")
        invoke(self.root, self.env, "uninstall")
        self.assertEqual(upstream.read_bytes(), expected)

    def test_preexisting_exact_skill_is_not_removed(self):
        name = "brownfield-complexity-gate"
        source = REPO / "skills" / name / "SKILL.md"
        target = self.root / ".agents/skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(source.read_bytes())
        invoke(self.root, self.env, "install")
        invoke(self.root, self.env, "uninstall")
        self.assertTrue(target.exists())
        self.assertEqual(MODULE.sha256_path(target), MODULE.SKILLS[name])
