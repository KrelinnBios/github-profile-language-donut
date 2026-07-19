<<<<<<< HEAD
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from language_donut.output import write_outputs


class OutputTests(unittest.TestCase):
    def test_versioned_output_replaces_readme_and_cleans_old_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            old_image = root / "language-donut-000000000000.svg"
            readme.write_text(
                '<img src="./language-donut-000000000000.svg" alt="chart" />',
                encoding="utf-8",
            )
            old_image.write_text("old", encoding="utf-8")

            image, changed = write_outputs(
                "<svg></svg>", readme, root, "language-donut"
            )

            self.assertTrue(changed)
            self.assertTrue(image.exists())
            self.assertFalse(old_image.exists())
            self.assertIn(image.name, readme.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
=======
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from language_donut.output import write_outputs


class OutputTests(unittest.TestCase):
    def test_versioned_output_replaces_readme_and_cleans_old_images(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            old_image = root / "language-donut-000000000000.svg"
            readme.write_text(
                '<img src="./language-donut-000000000000.svg" alt="chart" />',
                encoding="utf-8",
            )
            old_image.write_text("old", encoding="utf-8")

            image, changed = write_outputs(
                "<svg></svg>", readme, root, "language-donut"
            )

            self.assertTrue(changed)
            self.assertTrue(image.exists())
            self.assertFalse(old_image.exists())
            self.assertIn(image.name, readme.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
