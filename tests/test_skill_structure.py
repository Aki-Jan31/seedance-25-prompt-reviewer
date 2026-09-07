import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_and_name(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertRegex(frontmatter, r"(?m)^name: seedance-25-prompt-reviewer$")
        description = re.search(r"(?m)^description: (.+)$", frontmatter)
        self.assertIsNotNone(description)
        self.assertIn("existing Seedance 2.5", description.group(1))
        self.assertIn("Not a general from-scratch", description.group(1))
        self.assertRegex(frontmatter, r"(?m)^license: MIT$")

    def test_relative_markdown_links_resolve_inside_skill(self):
        for source in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]:
            text = source.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                path_part = target.split("#", 1)[0]
                resolved = (source.parent / path_part).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT.resolve()), f"link escapes skill: {source} -> {target}")
                self.assertTrue(resolved.exists(), f"broken link: {source} -> {target}")

    def test_openai_yaml_keeps_implicit_discovery(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^policy:\n  allow_implicit_invocation: true$")
        default_prompt = re.search(r'(?m)^  default_prompt: "(.+)"$', text)
        short_description = re.search(r'(?m)^  short_description: "(.+)"$', text)
        self.assertIsNotNone(default_prompt)
        self.assertIsNotNone(short_description)
        self.assertIn("$seedance-25-prompt-reviewer", default_prompt.group(1))
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)

    def test_progressive_disclosure_and_version_rules_are_present(self):
        entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        adapter = (ROOT / "references" / "seedance-25-adapter.md").read_text(encoding="utf-8")
        self.assertIn("dialogue-staging.md", entry)
        self.assertIn("only when", entry)
        for duration in ("19-second", "22-second", "30-second"):
            self.assertIn(duration, adapter)
        self.assertIn("Never split", adapter)


if __name__ == "__main__":
    unittest.main()
