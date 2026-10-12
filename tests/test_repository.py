from __future__ import annotations

import re
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class RepositoryTest(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = [
            "README.md",
            "LICENSE",
            "prompts/chatgpt-prompt.md",
            "prompts/xiaohongshu-copy.txt",
            "skills/museum-archaeology-notebook/SKILL.md",
            "skills/museum-archaeology-notebook/agents/openai.yaml",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_all_example_pairs_exist(self) -> None:
        groups = (
            "ya-chang-ox-zun",
            "ya-chang-jade-knife",
            "oracle-plastron",
            "oracle-scapula-2172",
        )
        for group in groups:
            for filename in ("original.jpg", "result.jpg"):
                path = ROOT / "examples" / group / filename
                self.assertTrue(path.is_file())
                with Image.open(path) as image:
                    image.verify()

    def test_readme_local_links_resolve(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", readme)
        local = [target for target in targets if "://" not in target and not target.startswith("#")]
        for target in local:
            self.assertTrue((ROOT / target).exists(), target)

    def test_prompts_are_self_contained_and_authenticity_first(self) -> None:
        for relative in ("prompts/chatgpt-prompt.md", "prompts/xiaohongshu-copy.txt"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("直接", text)
            self.assertIn("不要编造", text)
            self.assertIn("原照片", text)
            self.assertNotIn("请阅读 GitHub", text)


if __name__ == "__main__":
    unittest.main()
