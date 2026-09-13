import json

from support import CONTRACT, TempProjectTest, invoke


class DoctorTests(TempProjectTest):
    def test_doctor_separates_health_from_readiness_notices(self):
        invoke(self.root, self.env, "install")
        result = invoke(self.root, self.env, "doctor")
        self.assertIn("Installation health: HEALTHY", result.stdout)
        self.assertIn("Workflow readiness:", result.stdout)
        self.assertIn("NOTICE:", result.stdout)
        self.assertIn("openspec doctor: pass", result.stdout)
        self.assertIn("openspec validate: pass", result.stdout)

    def test_doctor_reports_modified_skill_as_unhealthy(self):
        invoke(self.root, self.env, "install")
        skill = self.root / ".agents/skills/cross-change-roadmap/SKILL.md"
        skill.write_text(skill.read_text() + "\nlocal edit\n")
        result = invoke(self.root, self.env, "doctor", check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Installation health: UNHEALTHY", result.stdout)
        self.assertIn("locally modified installed skill", result.stdout)

    def test_doctor_reports_duplicate_owned_config_item_as_unhealthy(self):
        invoke(self.root, self.env, "install")
        config = self.root / "openspec/config.yaml"
        item_line = "    - " + json.dumps(CONTRACT["rules"]["proposal"][0])
        text = config.read_text()
        config.write_text(text.replace(item_line, item_line + "\n" + item_line, 1))

        result = invoke(self.root, self.env, "doctor", check=False)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Installation health: UNHEALTHY", result.stdout)
        self.assertIn("rules.proposal duplicates 1 required item", result.stdout)
