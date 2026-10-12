from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "museum-archaeology-notebook" / "scripts" / "compose_notebook.py"
SAMPLE = ROOT / "examples" / "ya-chang-jade-knife" / "original.jpg"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ComposeNotebookTest(unittest.TestCase):
    def test_source_is_unchanged_and_png_is_created(self) -> None:
        before = digest(SAMPLE)
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "result.png"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(SAMPLE),
                    "--output",
                    str(output),
                    "--title",
                    "亚长玉刀",
                    "--fact",
                    "商代晚期",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("source_unchanged=true", completed.stdout)
            self.assertEqual(before, digest(SAMPLE))
            with Image.open(output) as image:
                self.assertEqual("PNG", image.format)
                self.assertEqual((1600, 1200), image.size)
                self.assertNotEqual((232, 216, 184), image.convert("RGB").getpixel((800, 320)))


if __name__ == "__main__":
    unittest.main()
