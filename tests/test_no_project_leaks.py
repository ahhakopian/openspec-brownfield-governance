from pathlib import Path
import unittest

from support import REPO


FORBIDDEN = (
    "AI Response " + "Personalizer",
    "ai-response-" + "personalizer",
    "/home/art/projects/" + "personalization",
    "plumb-reliable-" + "request-context",
    "local-adaptation-" + "control",
    "local-profile-" + "adaptation",
    "privacy-minimized-" + "measurement",
    "product-administration-" + "separation",
    "settings-information-" + "architecture",
    "supported-service-" + "governance",
    "Context-aware request personalization is not required "
    + "for the current MVP",
)


class LeakTests(unittest.TestCase):
    def test_distribution_contains_no_reference_project_content(self):
        findings = []
        for path in REPO.rglob("*"):
            if (
                not path.is_file()
                or ".git" in path.parts
                or "__pycache__" in path.parts
                or path.suffix == ".pyc"
            ):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for forbidden in FORBIDDEN:
                if forbidden in text:
                    findings.append(f"{path.relative_to(REPO)}: {forbidden}")
        self.assertEqual(findings, [])

    def test_no_target_project_artifacts_are_packaged(self):
        forbidden_paths = (
            "openspec/system/brownfield-map.md",
            "openspec/roadmap.md",
            "docs/product/product-model.md",
            "docs/product/product-boundaries.md",
            "docs/product/access-model.md",
            "PRD.canonical.md",
            "openspec/specs",
            "openspec/changes",
        )
        for relative in forbidden_paths:
            self.assertFalse((REPO / relative).exists(), relative)
