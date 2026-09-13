from support import (
    MODULE,
    REPO,
    TempProjectTest,
    add_project_knowledge,
    digest_tree,
    invoke,
)


class UpdateTests(TempProjectTest):
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
        name = "brownfield-map"
        source = REPO / "skills" / name / "SKILL.md"
        target = self.root / ".agents/skills" / name / "SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_bytes(source.read_bytes())
        invoke(self.root, self.env, "install")
        invoke(self.root, self.env, "uninstall")
        self.assertTrue(target.exists())
        self.assertEqual(MODULE.sha256_path(target), MODULE.SKILLS[name])
